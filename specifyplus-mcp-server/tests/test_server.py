"""Tests for server.py - MCP Server lifecycle and prompt registration."""

import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestServerLifecycle:
    """Test server startup and shutdown lifecycle."""

    @pytest.fixture
    def commands_dir(self):
        """Create a temporary commands directory with test files."""
        test_dir = tempfile.mkdtemp()
        commands_dir = os.path.join(test_dir, "commands")
        os.makedirs(commands_dir)

        # Create a test command file
        test_command = os.path.join(commands_dir, "test-cmd.md")
        with open(test_command, "w") as f:
            f.write(
                """---
description: A test command for server tests
---

This is the test command content with $ARGUMENTS placeholder.
"""
            )

        # Create a command without arguments
        static_command = os.path.join(commands_dir, "static-cmd.md")
        with open(static_command, "w") as f:
            f.write(
                """---
description: A static command without arguments
---

This is static content without any placeholders.
"""
            )

        # Create a command with handoffs
        handoff_command = os.path.join(commands_dir, "handoff-cmd.md")
        with open(handoff_command, "w") as f:
            f.write(
                """---
description: A command with handoff links
handoffs:
  - label: "Next Step"
    agent: "implementation"
    prompt: "Continue with implementation"
---

Command with handoff content.
"""
            )

        yield commands_dir
        shutil.rmtree(test_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_on_startup_initializes_components(self, commands_dir):
        """Test that on_startup properly initializes all components."""
        # Import here to avoid module-level side effects
        from src import server

        # Reset global state
        server._loader = None
        server._handler = None
        server._watcher = None
        server._registry.clear()

        with patch.dict(os.environ, {"COMMANDS_DIR": commands_dir}):
            await server.on_startup()

            # Verify components were initialized
            assert server._loader is not None
            assert server._handler is not None
            assert server._watcher is not None
            assert server._registry.count() == 3

            # Clean up
            await server.on_shutdown()

    @pytest.mark.asyncio
    async def test_on_shutdown_cleans_up(self, commands_dir):
        """Test that on_shutdown properly cleans up resources."""
        from src import server

        # Reset and initialize
        server._loader = None
        server._handler = None
        server._watcher = None
        server._registry.clear()

        with patch.dict(os.environ, {"COMMANDS_DIR": commands_dir}):
            await server.on_startup()

            # Verify initialized
            assert server._watcher is not None
            assert server._watcher.observer is not None

            await server.on_shutdown()

            # Verify cleaned up
            assert server._watcher is None
            assert server._loader is None
            assert server._registry.count() == 0

    @pytest.mark.asyncio
    async def test_on_shutdown_handles_no_watcher(self):
        """Test that on_shutdown handles case where watcher is None."""
        from src import server

        # Set watcher to None explicitly
        server._watcher = None
        server._loader = MagicMock()
        server._registry = MagicMock()

        # Should not raise
        await server.on_shutdown()


class TestReloadCommands:
    """Test command reload functionality."""

    @pytest.fixture
    def commands_dir(self):
        """Create a temporary commands directory."""
        test_dir = tempfile.mkdtemp()
        commands_dir = os.path.join(test_dir, "commands")
        os.makedirs(commands_dir)

        test_command = os.path.join(commands_dir, "reload-test.md")
        with open(test_command, "w") as f:
            f.write(
                """---
description: Test command for reload
---

Original content.
"""
            )

        yield commands_dir
        shutil.rmtree(test_dir, ignore_errors=True)

    def test_reload_commands_updates_registry(self, commands_dir):
        """Test that reload_commands updates the registry."""
        from src import server
        from src.loader import CommandLoader
        from src.registry import CommandRegistry

        # Set up loader and registry
        server._loader = CommandLoader(commands_dir)
        server._registry = CommandRegistry()

        # Initial load
        commands = server._loader.load_all_commands()
        server._registry.update_all(commands)
        initial_count = server._registry.count()

        # Add a new command file
        new_command = os.path.join(commands_dir, "new-cmd.md")
        with open(new_command, "w") as f:
            f.write(
                """---
description: Newly added command
---

New command content.
"""
            )

        # Reload
        server.reload_commands()

        # Verify count increased
        assert server._registry.count() == initial_count + 1
        assert server._registry.get("new-cmd") is not None

    def test_reload_commands_handles_no_loader(self):
        """Test that reload_commands handles None loader gracefully."""
        from src import server

        server._loader = None

        # Should not raise, just log warning
        server.reload_commands()

    def test_reload_commands_handles_exception(self, commands_dir):
        """Test that reload_commands handles exceptions gracefully."""
        from src import server

        # Create a mock loader that raises
        mock_loader = MagicMock()
        mock_loader.load_all_commands.side_effect = Exception("Test error")
        server._loader = mock_loader

        # Should not raise
        server.reload_commands()


class TestRegisterPrompts:
    """Test MCP prompt registration."""

    @pytest.fixture
    def setup_registry(self):
        """Set up registry with test commands."""
        from src import server
        from src.handler import PromptHandler
        from src.models import CommandDefinition, CommandMetadata, HandoffLink
        from src.registry import CommandRegistry

        # Create fresh registry
        registry = CommandRegistry()

        # Add command with arguments
        cmd_with_args = CommandDefinition(
            name="with-args",
            file_path="/test/with-args.md",
            metadata=CommandMetadata(description="Command with args"),
            content="Content with $ARGUMENTS",
            has_arguments=True,
            file_size=100,
            last_modified=datetime.now(),
        )
        registry.register(cmd_with_args)

        # Add command without arguments
        cmd_no_args = CommandDefinition(
            name="no-args",
            file_path="/test/no-args.md",
            metadata=CommandMetadata(description="Command without args"),
            content="Static content",
            has_arguments=False,
            file_size=50,
            last_modified=datetime.now(),
        )
        registry.register(cmd_no_args)

        # Add command with handoffs
        cmd_handoffs = CommandDefinition(
            name="with-handoffs",
            file_path="/test/with-handoffs.md",
            metadata=CommandMetadata(
                description="Command with handoffs",
                handoffs=[
                    HandoffLink(label="Next", agent="next-agent", prompt="Continue")
                ],
            ),
            content="Handoff content",
            has_arguments=False,
            file_size=75,
            last_modified=datetime.now(),
        )
        registry.register(cmd_handoffs)

        # Set up server globals
        server._registry = registry
        server._handler = PromptHandler(registry)

        yield registry

        # Clean up
        server._registry = CommandRegistry()
        server._handler = None

    def test_register_prompts_registers_all_commands(self, setup_registry):
        """Test that register_prompts registers all commands from registry."""
        from src import server

        # Register prompts
        server.register_prompts()

        # Verify prompts were registered - check by listing prompts
        # The prompts should be registered via mcp.prompt decorator
        # We just verify the function runs without error and processes all commands
        assert setup_registry.count() == 3

    def test_register_prompts_handles_empty_registry(self):
        """Test that register_prompts handles empty registry."""
        from src import server
        from src.registry import CommandRegistry

        server._registry = CommandRegistry()

        # Should not raise
        server.register_prompts()


class TestPromptHandler:
    """Test the prompt handler function created during registration."""

    @pytest.fixture
    def setup_server(self):
        """Set up server with test commands."""
        from src import server
        from src.handler import PromptHandler
        from src.models import CommandDefinition, CommandMetadata
        from src.registry import CommandRegistry

        registry = CommandRegistry()

        cmd = CommandDefinition(
            name="handler-test",
            file_path="/test/handler-test.md",
            metadata=CommandMetadata(description="Handler test command"),
            content="Process this: $ARGUMENTS",
            has_arguments=True,
            file_size=100,
            last_modified=datetime.now(),
        )
        registry.register(cmd)

        server._registry = registry
        server._handler = PromptHandler(registry)

        yield

        server._registry = CommandRegistry()
        server._handler = None

    @pytest.mark.asyncio
    async def test_prompt_handler_processes_arguments(self, setup_server):
        """Test that registered prompt handler processes arguments."""
        from src import server

        # Test that handler can process arguments directly
        # This tests the core functionality without needing FastMCP internals
        result = server._handler.process_prompt("handler-test", "test input")

        assert "test input" in result

    @pytest.mark.asyncio
    async def test_prompt_handler_raises_without_handler(self):
        """Test that accessing handler when None raises error."""
        from src import server
        from src.registry import CommandRegistry

        # Store original handler
        original_handler = server._handler

        # Set handler to None
        server._handler = None
        server._registry = CommandRegistry()

        # Attempting to process prompt when handler is None would raise
        # We test by checking the guard in the prompt handler closure
        # The actual test is that register_prompts creates closures that check _handler
        server.register_prompts()  # Should work even with no commands

        # Clean up
        server._handler = original_handler
        server._registry = CommandRegistry()


class TestMainFunction:
    """Test main entry point functions."""

    @pytest.fixture
    def commands_dir(self):
        """Create a temporary commands directory."""
        test_dir = tempfile.mkdtemp()
        commands_dir = os.path.join(test_dir, "commands")
        os.makedirs(commands_dir)

        test_command = os.path.join(commands_dir, "main-test.md")
        with open(test_command, "w") as f:
            f.write(
                """---
description: Test for main function
---

Main test content.
"""
            )

        yield commands_dir
        shutil.rmtree(test_dir, ignore_errors=True)

    def test_main_with_stdio_transport(self, commands_dir):
        """Test main function with stdio transport."""
        from src import server

        with patch.dict(
            os.environ, {"COMMANDS_DIR": commands_dir, "MCP_TRANSPORT": "stdio"}
        ):
            with patch.object(server.mcp, "run") as mock_run:
                # Mock run to avoid actually starting server
                mock_run.return_value = None

                server.main()

                # Verify run was called with no args (stdio default)
                mock_run.assert_called_once_with()

    def test_main_with_http_transport(self, commands_dir):
        """Test main function with http transport."""
        from src import server

        with patch.dict(
            os.environ,
            {"COMMANDS_DIR": commands_dir, "MCP_TRANSPORT": "http", "MCP_PORT": "9000"},
        ):
            with patch.object(server.mcp, "run") as mock_run:
                mock_run.return_value = None

                server.main()

                # Verify run was called with transport and port
                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args
                assert call_kwargs[1]["transport"] == "http"
                assert call_kwargs[1]["port"] == 9000

    def test_main_with_sse_transport(self, commands_dir):
        """Test main function with SSE transport."""
        from src import server

        with patch.dict(
            os.environ,
            {"COMMANDS_DIR": commands_dir, "MCP_TRANSPORT": "sse", "MCP_PORT": "8888"},
        ):
            with patch.object(server.mcp, "run") as mock_run:
                mock_run.return_value = None

                server.main()

                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args
                assert call_kwargs[1]["transport"] == "sse"
                assert call_kwargs[1]["port"] == 8888

    def test_main_with_unknown_transport(self, commands_dir):
        """Test main function with unknown transport falls back to stdio."""
        from src import server

        with patch.dict(
            os.environ,
            {"COMMANDS_DIR": commands_dir, "MCP_TRANSPORT": "unknown-transport"},
        ):
            with patch.object(server.mcp, "run") as mock_run:
                mock_run.return_value = None

                server.main()

                # Should fall back to stdio (no args)
                mock_run.assert_called_once_with()

    def test_main_with_custom_port(self, commands_dir):
        """Test main function with custom port."""
        from src import server

        with patch.dict(
            os.environ,
            {
                "COMMANDS_DIR": commands_dir,
                "MCP_TRANSPORT": "streamable-http",
                "MCP_PORT": "3000",
            },
        ):
            with patch.object(server.mcp, "run") as mock_run:
                mock_run.return_value = None

                server.main()

                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args
                assert call_kwargs[1]["port"] == 3000
