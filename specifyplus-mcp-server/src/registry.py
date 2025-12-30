"""CommandRegistry - Thread-safe storage for command definitions."""

import logging
import threading

from src.models import CommandDefinition

logger = logging.getLogger(__name__)


class CommandRegistry:
    """Thread-safe in-memory storage for command definitions.

    Provides CRUD operations with atomic bulk updates for hot reload.
    Uses RLock for thread safety to support concurrent access (SC-003).

    Attributes:
        _registry: Internal dictionary mapping command names to definitions.
        _lock: Reentrant lock for thread-safe operations.
    """

    def __init__(self) -> None:
        """Initialize empty command registry with lock."""
        self._registry: dict[str, CommandDefinition] = {}
        self._lock = threading.RLock()
        logger.debug("CommandRegistry initialized")

    def register(self, command: CommandDefinition) -> None:
        """Register a single command in the registry.

        Args:
            command: The CommandDefinition to register.
        """
        with self._lock:
            self._registry[command.name] = command
            logger.debug(f"Registered command: {command.name}")

    def get(self, name: str) -> CommandDefinition | None:
        """Retrieve a command by name.

        Args:
            name: The command name to retrieve.

        Returns:
            CommandDefinition if found, None otherwise.
        """
        with self._lock:
            return self._registry.get(name)

    def list_commands(self) -> list[str]:
        """Get list of all registered command names.

        Returns:
            List of command names sorted alphabetically.
        """
        with self._lock:
            return sorted(self._registry.keys())

    def update_all(self, commands: dict[str, CommandDefinition]) -> None:
        """Atomically update all commands in the registry.

        Replaces the entire registry contents with the provided dictionary.
        This is used for hot reload to ensure consistency (SC-003).

        Args:
            commands: Dictionary mapping command names to CommandDefinitions.
        """
        with self._lock:
            # Atomic replacement
            old_count = len(self._registry)
            self._registry = dict(commands)  # Make a copy
            new_count = len(self._registry)
            logger.info(f"Registry updated: {old_count} -> {new_count} commands")

    def clear(self) -> None:
        """Remove all commands from the registry."""
        with self._lock:
            old_count = len(self._registry)
            self._registry.clear()
            logger.info(f"Registry cleared: removed {old_count} commands")

    def count(self) -> int:
        """Get the number of registered commands.

        Returns:
            Number of commands in the registry.
        """
        with self._lock:
            return len(self._registry)
