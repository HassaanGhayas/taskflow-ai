"""FastMCP Server - SpecifyPlus MCP Server for IDE integration."""

import logging
import os
import sys

from fastmcp import FastMCP

from src.handler import PromptHandler
from src.loader import CommandLoader
from src.registry import CommandRegistry
from src.watcher import FileWatcher

# Initialize logging to stderr (required for MCP stdio transport)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    stream=sys.stderr,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger(__name__)

# MCP Server instance
mcp = FastMCP("specifyplus-commands")

# Global components
_loader: CommandLoader | None = None
_registry: CommandRegistry = CommandRegistry()
_handler: PromptHandler | None = None
_watcher: FileWatcher | None = None


async def on_startup() -> None:
    """Initialize server components and load commands."""
    global _loader, _registry, _handler, _watcher

    # Get commands directory from environment variable
    commands_dir = os.getenv("COMMANDS_DIR", ".claude/commands")

    # Initialize CommandLoader
    logger.info(f"Initializing CommandLoader with directory: {commands_dir}")
    _loader = CommandLoader(commands_dir)

    # Load all commands into registry
    logger.info("Loading commands...")
    commands = _loader.load_all_commands()
    _registry.update_all(commands)

    logger.info(f"Server started with {_registry.count()} commands loaded")

    # Initialize PromptHandler with registry
    _handler = PromptHandler(_registry)

    # Initialize FileWatcher for hot reload (FR-013)
    _watcher = FileWatcher(
        commands_dir=commands_dir,
        reload_callback=reload_commands,
        debounce_seconds=1.0,  # Target: reload <5s per SC-007
    )

    # Start file watcher
    _watcher.start()

    # Register all commands as MCP prompts
    register_prompts()


async def on_shutdown() -> None:
    """Clean up on server shutdown."""
    global _loader, _registry, _watcher

    logger.info("Shutting down server...")

    # Stop file watcher if running
    if _watcher is not None:
        _watcher.stop()
        _watcher = None

    _registry.clear()
    _loader = None
    logger.info("Server shutdown complete")


def reload_commands() -> None:
    """Reload all commands from disk (triggered by FileWatcher)."""
    global _loader, _registry

    if _loader is None:
        logger.warning("CommandLoader not initialized, skipping reload")
        return

    try:
        logger.info("Reloading commands...")

        # Reload all commands from disk
        commands = _loader.load_all_commands()

        # Update registry atomically
        _registry.update_all(commands)

        logger.info(f"Reload complete: {_registry.count()} commands loaded")
    except Exception as e:
        logger.error(f"Failed to reload commands: {e}")


def register_prompts() -> None:
    """Register all commands from registry as MCP prompts."""
    command_names = _registry.list_commands()

    logger.info(f"Registering {len(command_names)} prompts...")

    for name in command_names:
        command = _registry.get(name)
        if command:
            # Extract values for closure capture
            cmd_description = command.metadata.description

            # Create handler function with default arg to capture name in closure
            async def get_prompt_handler(
                arguments: str | None = None,
                _cmd_name: str = name,
                _cmd_description: str = cmd_description,
            ) -> list[dict[str, str]]:
                """Get prompt for a command with optional arguments.

                Args:
                    arguments: Optional user input text for $ARGUMENTS substitution.

                Returns:
                    List of message dictionaries with role="user" and prompt content.

                Raises:
                    CommandNotFoundError: If command name is not in registry.
                    InputTooLargeError: If input exceeds 100KB limit.
                """
                # Process prompt (handles validation, sanitization, substitution)
                if _handler is None:
                    raise RuntimeError("PromptHandler not initialized")

                # Process with captured command name
                content = _handler.process_prompt(_cmd_name, arguments)

                # Return as message with role="user"
                return [{"role": "user", "content": content}]

            # Build prompt metadata (FR-009: expose handoff links)

            if command.has_arguments:
                # Add argument schema for commands with $ARGUMENTS
                pass

            # Register with FastMCP decorator
            # Include description from CommandMetadata (already set)
            # Note: FastMCP may not support additional metadata in current version,
            # but we pass it if available
            mcp.prompt(name=name, description=command.metadata.description)(
                get_prompt_handler
            )

            # Log handoff information if present (FR-009)
            if command.metadata.handoffs:
                handoff_count = len(command.metadata.handoffs)
                handoff_labels = ", ".join(h.label for h in command.metadata.handoffs)
                logger.debug(
                    f"Registered prompt: {name} with {handoff_count} handoffs: "
                    f"{handoff_labels}"
                )
            else:
                logger.debug(f"Registered prompt: {name}")


def main() -> None:
    """Run MCP server.

    Uses stdio transport by default (FR-011).
    FastMCP.run() manages its own event loop, so this must be synchronous.
    """
    import asyncio

    logger.info("Starting SpecifyPlus MCP Server...")

    # Initialize components synchronously
    asyncio.run(on_startup())

    # Check for SSE transport configuration (FR-011)
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    port = int(os.getenv("MCP_PORT", "8080"))

    logger.info(f"Transport: {transport}")
    if port != 8080:
        logger.info(f"Port: {port}")

    try:
        # Run server with configured transport
        # mcp.run() creates its own event loop
        if transport == "stdio":
            mcp.run()
        elif transport in ("http", "sse", "streamable-http"):
            # Type-safe transport selection for FastMCP
            from typing import Literal, cast

            transport_type = cast(Literal["http", "sse", "streamable-http"], transport)
            mcp.run(transport=transport_type, port=port)
        else:
            logger.warning(f"Unknown transport: {transport}, using stdio")
            mcp.run()
    finally:
        # Clean up on shutdown
        asyncio.run(on_shutdown())


if __name__ == "__main__":
    main()
