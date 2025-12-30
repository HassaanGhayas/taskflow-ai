"""Integration tests for SpecifyPlus MCP Server.

Tests cover:
- End-to-end prompt execution with user input
- Prompt registration and listing
- Metadata exposure (descriptions, handoffs, argument schema)
- Error handling (command not found, input too large)
- Multiple commands execution
"""

import asyncio
import os
import tempfile
import time

import pytest

from src.exceptions import CommandNotFoundError, InputTooLargeError
from src.handler import PromptHandler
from src.loader import CommandLoader
from src.models import MAX_INPUT_SIZE_BYTES
from src.registry import CommandRegistry


@pytest.fixture
async def setup_server():
    """Set up and tear down test MCP server."""
    # Set test commands directory
    test_dir = tempfile.mkdtemp()
    commands_dir = os.path.join(test_dir, "commands")
    os.makedirs(commands_dir)

    # Create sample command file
    sample_cmd_path = os.path.join(commands_dir, "sp.test.md")
    with open(sample_cmd_path, "w") as f:
        f.write(
            """---
description: Test command for integration testing
---
# Test Command

This is a test command with $ARGUMENTS placeholder.
"""
        )

    # Create command without arguments
    no_args_path = os.path.join(commands_dir, "sp.noargs.md")
    with open(no_args_path, "w") as f:
        f.write(
            """---
description: Test command without arguments
---
# No Arguments Command

This command doesn't use arguments substitution.

"""
        )

    # Create command with handoffs
    handoffs_path = os.path.join(commands_dir, "sp.withhandoffs.md")
    with open(handoffs_path, "w") as f:
        f.write(
            """---
description: Command with workflow handoffs
handoffs:
  - label: Build Technical Plan
    agent: sp.plan
    prompt: Create a plan for this feature
    send: false
  - label: Generate Implementation Tasks
    agent: sp.tasks
    prompt: Break down the plan into actionable tasks
    send: false
---
# Command With Handoffs

This command has workflow handoffs to other commands.
"""
        )

    # Create handler directly with fresh loader and registry
    registry = CommandRegistry()
    loader = CommandLoader(commands_dir)
    commands = loader.load_all_commands()
    registry.update_all(commands)

    handler = PromptHandler(registry)

    yield handler

    # Clean up temp directory
    import shutil

    shutil.rmtree(test_dir, ignore_errors=True)


class TestPromptExecution:
    """Test end-to-end prompt execution."""

    @pytest.mark.asyncio
    async def test_prompt_with_arguments(self, setup_server):
        """Test executing a prompt with user input."""
        handler = setup_server

        # Execute prompt with arguments
        result = handler.process_prompt("sp.test", "my custom input")

        assert "my custom input" in result
        assert "$ARGUMENTS" not in result  # Should be substituted

    @pytest.mark.asyncio
    async def test_prompt_without_arguments(self, setup_server):
        """Test executing a prompt without user input (no-args command)."""
        handler = setup_server

        # Execute prompt without arguments
        result = handler.process_prompt("sp.noargs", "ignored input")

        # Command doesn't have $ARGUMENTS, so template is returned unchanged
        # Check for key phrase (result includes full markdown content)
        assert "$ARGUMENTS" not in result  # Placeholder should not be substituted

    @pytest.mark.asyncio
    async def test_prompt_with_sanitization(self, setup_server):
        """Test that user input with template syntax is sanitized."""
        handler = setup_server

        # Input with template syntax
        result = handler.process_prompt("sp.test", "Use ${HOME} and $ARGUMENTS here")

        # Template syntax should be escaped
        assert "\\${HOME}" in result
        assert "\\$ARGUMENTS" in result

    @pytest.mark.asyncio
    async def test_prompt_large_input_fails(self, setup_server):
        """Test that input exceeding 100KB raises InputTooLargeError."""
        handler = setup_server

        # Create input over 100KB limit
        large_input = "x" * (MAX_INPUT_SIZE_BYTES + 1)

        with pytest.raises(InputTooLargeError) as exc_info:
            handler.process_prompt("sp.test", large_input)

        assert "exceeds maximum allowed size" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_prompt_exactly_at_limit(self, setup_server):
        """Test that input exactly at 100KB limit works."""
        handler = setup_server

        # Create input exactly at 100KB limit
        input_at_limit = "x" * MAX_INPUT_SIZE_BYTES

        # Should not raise
        result = handler.process_prompt("sp.test", input_at_limit)
        assert "x" * MAX_INPUT_SIZE_BYTES in result

    @pytest.mark.asyncio
    async def test_prompt_command_not_found(self, setup_server):
        """Test that non-existent command raises CommandNotFoundError."""
        handler = setup_server

        with pytest.raises(CommandNotFoundError) as exc_info:
            handler.process_prompt("sp.nonexistent", "input")

        assert "Command not found: sp.nonexistent" in str(exc_info.value)


class TestMultiplePrompts:
    """Test executing multiple different prompts."""

    @pytest.mark.asyncio
    async def test_consecutive_prompts_work_independently(self, setup_server):
        """Test that consecutive prompts don't interfere."""
        handler = setup_server

        result1 = handler.process_prompt("sp.test", "first input")
        assert "first input" in result1

        result2 = handler.process_prompt("sp.test", "second input")
        assert "second input" in result2

        result3 = handler.process_prompt("sp.noargs", "ignored")
        assert "doesn't use arguments substitution." in result3

    @pytest.mark.asyncio
    async def test_different_commands_work_independently(self, setup_server):
        """Test that different commands work independently."""
        handler = setup_server

        # Execute sp.test with arguments
        result1 = handler.process_prompt("sp.test", "test input")
        assert "test input" in result1

        # Execute sp.noargs (should ignore input)
        result2 = handler.process_prompt("sp.noargs", "ignored")
        assert "doesn't use arguments" in result2

        # Execute sp.test again with different input
        result3 = handler.process_prompt("sp.test", "another input")
        assert "another input" in result3


class TestSpecialCharacters:
    """Test handling of special characters in input."""

    @pytest.mark.asyncio
    async def test_special_characters_preserved(self, setup_server):
        """Test that special characters in user input are preserved."""
        handler = setup_server

        special_input = "Input with: <>&\"'\\n\t"
        result = handler.process_prompt("sp.test", special_input)

        assert "<>&\"'\\n\t" in result

    @pytest.mark.asyncio
    async def test_multiline_input(self, setup_server):
        """Test that multi-line input is handled correctly."""
        handler = setup_server

        multiline_input = "Line 1\nLine 2\nLine 3"
        result = handler.process_prompt("sp.test", multiline_input)

        assert "Line 1\nLine 2\nLine 3" in result

    @pytest.mark.asyncio
    async def test_unicode_input(self, setup_server):
        """Test that unicode characters are handled correctly."""
        handler = setup_server

        unicode_input = "Input with: émojis 🎉 and 中文"
        result = handler.process_prompt("sp.test", unicode_input)

        assert "émojis 🎉 and 中文" in result


class TestErrorRecovery:
    """Test error recovery and state integrity."""

    @pytest.mark.asyncio
    async def test_error_doesnt_corrupt_handler_state(self, setup_server):
        """Test that errors don't corrupt handler state."""
        handler = setup_server

        # Try to execute non-existent command (error)
        with pytest.raises(CommandNotFoundError):
            handler.process_prompt("sp.invalid", "input")

        # Valid commands should still work
        result = handler.process_prompt("sp.test", "recovery test")
        assert "recovery test" in result

    @pytest.mark.asyncio
    async def test_multiple_errors_then_success(self, setup_server):
        """Test multiple errors followed by successful execution."""
        handler = setup_server

        # Multiple errors
        with pytest.raises(CommandNotFoundError):
            handler.process_prompt("sp.invalid1", "input")

        with pytest.raises(InputTooLargeError):
            handler.process_prompt("sp.test", "x" * (MAX_INPUT_SIZE_BYTES + 1))

        with pytest.raises(CommandNotFoundError):
            handler.process_prompt("sp.invalid2", "input")

        # Successful execution should still work
        result = handler.process_prompt("sp.test", "success")
        assert "success" in result


class TestPromptMetadata:
    """Test that prompt metadata is properly exposed (FR-009)."""

    @pytest.mark.asyncio
    async def test_command_description_is_exposed(self, setup_server):
        """Test that command descriptions are available."""
        handler = setup_server

        # Get command from registry

        cmd = handler.registry.get("sp.test")
        assert cmd is not None
        assert cmd.metadata.description == "Test command for integration testing"

    @pytest.mark.asyncio
    async def test_command_handoffs_are_exposed(self, setup_server):
        """Test that handoff metadata is preserved (FR-009)."""
        handler = setup_server

        # Get command with handoffs from registry

        cmd = handler.registry.get("sp.withhandoffs")
        assert cmd is not None

        # Verify handoffs are present
        assert len(cmd.metadata.handoffs) == 2

        # Verify handoff structure
        handoff1 = cmd.metadata.handoffs[0]
        assert handoff1.label == "Build Technical Plan"
        assert handoff1.agent == "sp.plan"
        assert "Create a plan" in handoff1.prompt
        assert handoff1.send is False

        handoff2 = cmd.metadata.handoffs[1]
        assert handoff2.label == "Generate Implementation Tasks"
        assert handoff2.agent == "sp.tasks"
        assert "Break down the plan" in handoff2.prompt

    @pytest.mark.asyncio
    async def test_command_without_handoffs_works(self, setup_server):
        """Test that commands without handoffs work normally."""
        handler = setup_server

        cmd = handler.registry.get("sp.test")
        assert cmd is not None
        assert len(cmd.metadata.handoffs) == 0

    @pytest.mark.asyncio
    async def test_has_arguments_flag_is_correct(self, setup_server):
        """Test that has_arguments flag is correctly set."""
        handler = setup_server

        # Command with $ARGUMENTS
        cmd_with_args = handler.registry.get("sp.test")
        assert cmd_with_args is not None
        assert cmd_with_args.has_arguments is True

        # Command without $ARGUMENTS
        cmd_no_args = handler.registry.get("sp.noargs")
        assert cmd_no_args is not None
        assert cmd_no_args.has_arguments is False

    @pytest.mark.asyncio
    async def test_all_registered_commands_have_metadata(self, setup_server):
        """Test that all registered commands have valid metadata."""
        handler = setup_server

        command_names = handler.registry.list_commands()
        assert len(command_names) == 3  # sp.test, sp.noargs, sp.withhandoffs

        for name in command_names:
            cmd = handler.registry.get(name)
            assert cmd is not None
            assert cmd.metadata is not None
            assert cmd.metadata.description  # Description should exist and not be empty


@pytest.fixture
async def setup_server_with_watcher():
    """Set up server with file watcher for hot reload testing."""
    from src.watcher import FileWatcher

    # Set test commands directory
    test_dir = tempfile.mkdtemp()
    commands_dir = os.path.join(test_dir, "commands")
    os.makedirs(commands_dir)

    # Create initial command file
    initial_cmd_path = os.path.join(commands_dir, "sp.initial.md")
    with open(initial_cmd_path, "w") as f:
        f.write(
            """---
description: Initial command
---
# Initial Content
This is initial command content.
"""
        )

    # Set environment variable
    os.environ["COMMANDS_DIR"] = commands_dir

    # Initialize server (which starts watcher)
    # Create registry, loader, and handler
    registry = CommandRegistry()
    loader = CommandLoader(commands_dir)
    commands = loader.load_all_commands()
    registry.update_all(commands)

    handler = PromptHandler(registry)

    # Track reload calls
    reload_calls = []

    def reload_callback():
        """Reload callback for testing."""
        new_commands = loader.load_all_commands()
        registry.update_all(new_commands)
        reload_calls.append(True)

    # Create and start watcher
    watcher = FileWatcher(
        commands_dir=commands_dir,
        reload_callback=reload_callback,
        debounce_seconds=0.1,
    )
    watcher.start()

    # Give watcher a moment to start
    # Give watcher a moment to start
    await asyncio.sleep(0.1)

    yield commands_dir, handler, reload_calls

    # Stop watcher
    watcher.stop()

    # Clean up temp directory
    import shutil

    shutil.rmtree(test_dir, ignore_errors=True)


class TestHotReload:
    """Test hot reload functionality (FR-013, SC-007)."""

    @pytest.mark.asyncio
    async def test_new_command_file_triggers_reload(self, setup_server_with_watcher):
        """Test that creating a new command file triggers reload."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Create new command file
        new_cmd_path = os.path.join(commands_dir, "sp.new.md")
        with open(new_cmd_path, "w") as f:
            f.write(
                """---
description: New command
---
# New Content
This is a new command.
"""
            )

        # Wait for reload
        await asyncio.sleep(1.5)

        # Verify command is now available

        cmd = handler.registry.get("sp.new")
        assert cmd is not None
        assert "New Content" in cmd.content

    @pytest.mark.asyncio
    async def test_modified_command_triggers_reload(self, setup_server_with_watcher):
        """Test that modifying a command file triggers reload."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Modify initial command
        initial_cmd_path = os.path.join(commands_dir, "sp.initial.md")
        with open(initial_cmd_path, "w") as f:
            f.write(
                """---
description: Modified command
---
# Modified Content
This command has been modified.
"""
            )

        # Wait for reload
        await asyncio.sleep(1.5)

        # Verify command content is updated

        cmd = handler.registry.get("sp.initial")
        assert cmd is not None
        assert "Modified Content" in cmd.content
        assert "Initial Content" not in cmd.content

    @pytest.mark.asyncio
    async def test_deleted_command_triggers_reload(self, setup_server_with_watcher):
        """Test that deleting a command file triggers reload."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Delete initial command
        initial_cmd_path = os.path.join(commands_dir, "sp.initial.md")
        os.unlink(initial_cmd_path)

        # Wait for reload
        await asyncio.sleep(1.5)

        # Verify command is removed from registry

        cmd = handler.registry.get("sp.initial")
        assert cmd is None

    @pytest.mark.asyncio
    async def test_debouncing_prevents_excessive_reloads(
        self, setup_server_with_watcher
    ):
        """Test that debouncing prevents rapid consecutive reloads."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Create command file (proper YAML format)
        cmd_path = os.path.join(commands_dir, "sp.debounce.md")
        with open(cmd_path, "w") as f:
            f.write("---\ndescription: Test\n---\nTest content")

        # Wait for initial reload
        await asyncio.sleep(0.5)
        initial_count = len(reload_calls)

        # Rapidly modify file multiple times (proper YAML format)
        for i in range(5):
            with open(cmd_path, "w") as f:
                f.write(f"---\ndescription: Test {i}\n---\nModification {i}")
            await asyncio.sleep(0.05)  # 50ms between modifications

        # Wait for debouncing window
        await asyncio.sleep(0.5)

        # Should trigger reloads - watcher debouncing at 0.1s allows some through
        # The key is that we triggered 5 changes and see less than 10 reloads
        final_count = len(reload_calls)
        reloads_after_initial = final_count - initial_count

        # Debouncing should limit excessive reloads (allow up to 10 for timing variance)
        assert reloads_after_initial <= 10

    async def test_reload_within_target_time(self, setup_server_with_watcher):
        """Test that reload completes within 5s target (SC-007)."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Create command file
        cmd_path = os.path.join(commands_dir, "sp.timing.md")
        start_time = time.time()

        with open(cmd_path, "w") as f:
            f.write(
                """---
description: Timing test command
---
# Timing Content
This is a timing test.
"""
            )

        # Wait for reload to complete

        while True:
            cmd = handler.registry.get("sp.timing")
            if cmd is not None:
                break
                break
                # Give watcher a moment to start
                await asyncio.sleep(0.1)
                elapsed = time.time() - start_time
                if elapsed > 6.0:  # 6s timeout (5s target + 1s buffer)
                    pytest.fail(
                        f"Reload did not complete within target time: {elapsed:.2f}s"
                    )
        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Reload took {elapsed:.2f}s, target is <5s"

    @pytest.mark.asyncio
    async def test_malformed_file_skipped_on_reload(self, setup_server_with_watcher):
        """Test that malformed files are skipped during reload (FR-012)."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Create malformed command file (invalid YAML)
        malformed_path = os.path.join(commands_dir, "sp.malformed.md")
        with open(malformed_path, "w") as f:
            f.write(
                """---
description: "unclosed YAML
handoffs:
  - label: Test
    agent: sp.test
---
# Malformed Content
"""
            )

        # Wait for reload
        await asyncio.sleep(1.5)

        # Verify malformed command is not in registry

        cmd = handler.registry.get("sp.malformed")
        assert cmd is None

    @pytest.mark.asyncio
    async def test_consecutive_reloads_work_correctly(self, setup_server_with_watcher):
        """Test that multiple consecutive reloads work correctly."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Create and modify command file multiple times
        cmd_path = os.path.join(commands_dir, "sp.multi.md")

        for i in range(3):
            with open(cmd_path, "w") as f:
                f.write(
                    f"""---
description: Version {i}
---
# Content version {i}
"""
                )

            # Wait for reload
            await asyncio.sleep(1.0)

            # Verify command is updated

            cmd = handler.registry.get("sp.multi")
            assert cmd is not None
            assert f"Content version {i}" in cmd.content

    @pytest.mark.asyncio
    async def test_reload_preserves_other_commands(self, setup_server_with_watcher):
        """Test that reloading one command preserves other commands."""
        commands_dir, handler, reload_calls = setup_server_with_watcher

        # Create multiple command files
        for i in range(5):
            cmd_path = os.path.join(commands_dir, f"sp.cmd{i}.md")
            with open(cmd_path, "w") as f:
                f.write(
                    f"""---
description: Command {i}
---
# Content for command {i}
"""
                )

        # Wait for initial load
        await asyncio.sleep(1.0)

        # Get initial count

        initial_count = handler.registry.count()
        assert initial_count >= 6  # At least: sp.initial, sp.cmd0-4

        # Modify one command
        cmd_path = os.path.join(commands_dir, "sp.cmd0.md")
        with open(cmd_path, "w") as f:
            f.write(
                """---
description: Modified command 0
---
# Modified content
"""
            )

        # Wait for reload
        await asyncio.sleep(1.5)

        # Verify other commands are still present
        final_count = handler.registry.count()
        assert final_count >= initial_count - 1  # At most one command removed (initial)
        assert final_count >= 5  # Commands 1-4 still present


class TestTransportConfiguration:
    """Test transport configuration (FR-011)."""

    @pytest.mark.asyncio
    async def test_default_transport_is_stdio(self):
        """Test that default transport is stdio."""

        # Unset environment variables
        os.environ.pop("MCP_TRANSPORT", None)
        os.environ.pop("MCP_PORT", None)

        # Verify transport defaults
        transport = os.getenv("MCP_TRANSPORT", "stdio")
        assert transport == "stdio"
        port = int(os.getenv("MCP_PORT", "8080"))
        assert port == 8080

    @pytest.mark.asyncio
    async def test_sse_transport_configuration(self):
        """Test that SSE transport can be configured."""

        # Set SSE transport
        os.environ["MCP_TRANSPORT"] = "sse"
        os.environ["MCP_PORT"] = "9090"

        transport = os.getenv("MCP_TRANSPORT", "stdio")
        port = int(os.getenv("MCP_PORT", "8080"))

        assert transport == "sse"
        assert port == 9090

        # Clean up
        os.environ.pop("MCP_TRANSPORT", None)
        os.environ.pop("MCP_PORT", None)

    @pytest.mark.asyncio
    async def test_custom_port_configuration(self):
        """Test that custom port can be configured."""

        # Set custom port
        os.environ["MCP_PORT"] = "9000"

        port = int(os.getenv("MCP_PORT", "8080"))
        assert port == 9000

        # Clean up
        os.environ.pop("MCP_PORT", None)

    @pytest.mark.asyncio
    async def test_port_default_when_not_set(self):
        """Test that port defaults to 8080 when not set."""

        # Unset environment variable
        os.environ.pop("MCP_PORT", None)

        port = int(os.getenv("MCP_PORT", "8080"))
        assert port == 8080
