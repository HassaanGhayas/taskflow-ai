"""Prompt Handler - User input processing and template substitution.

This module handles:
- Input validation (size limits per FR-004a)
- Template sanitization (escaping $ARGUMENTS, ${...} per FR-005a)
- $ARGUMENTS placeholder substitution (FR-005)
- Commands without $ARGUMENTS (FR-008)
"""

import logging
import re

from src.exceptions import InputTooLargeError
from src.models import MAX_INPUT_SIZE_BYTES
from src.registry import CommandRegistry

logger = logging.getLogger(__name__)


class PromptHandler:
    """Process user input and generate prompts for command execution.

    Handles secure substitution of user input into command templates,
    with validation and sanitization to prevent injection attacks.

    Attributes:
        registry: CommandRegistry for accessing command definitions.
    """

    def __init__(self, registry: CommandRegistry) -> None:
        """Initialize PromptHandler with a CommandRegistry.

        Args:
            registry: Thread-safe registry containing command definitions.
        """
        self.registry = registry

    def sanitize_input(self, text: str) -> str:
        """Escape template syntax patterns in user input (FR-005a).

        Prevents template injection by escaping:
        - Literal $ARGUMENTS to prevent re-substitution
        - ${...} patterns to prevent shell/environment variable access

        Args:
            text: User-provided input text.

        Returns:
            Sanitized text with escaped template patterns.

        Example:
            >>> handler.sanitize_input("Use $ARGUMENTS for input")
            'Use \\$ARGUMENTS for input'
            >>> handler.sanitize_input("Path: ${HOME}")
            'Path: \\${HOME}'
        """
        # Escape literal $ARGUMENTS to prevent re-substitution
        # We escape the dollar sign with a backslash
        sanitized = text.replace("$ARGUMENTS", "\\$ARGUMENTS")

        # Escape ${...} patterns (shell/environment variable syntax)
        # This prevents access to environment variables or shell expansion
        sanitized = re.sub(r"\$\{([^}]+)\}", r"\\${\1}", sanitized)

        return sanitized

    def process_prompt(self, command_name: str, user_input: str | None = None) -> str:
        """Process a command with optional user input.

        Validates input size, sanitizes template syntax, and substitutes
        user input into $ARGUMENTS placeholder.

        Args:
            command_name: Name of the command to process.
            user_input: Optional user input for $ARGUMENTS substitution.

        Returns:
            Processed prompt content ready for LLM consumption.

        Raises:
            InputTooLargeError: If input exceeds 100KB limit (FR-004a).
            CommandNotFoundError: If command name not found in registry.

        Note:
            - Commands without $ARGUMENTS return template unchanged (FR-008).
            - Input sanitization prevents template injection (FR-005a).
            - Size validation prevents resource exhaustion (FR-004a).
        """
        # Get command definition from registry
        cmd = self.registry.get(command_name)
        if not cmd:
            available = self.registry.list_commands()
            from src.exceptions import CommandNotFoundError

            raise CommandNotFoundError(command_name, available)

        # Validate input size if provided (FR-004a)
        if user_input is not None:
            size = len(user_input.encode("utf-8"))
            if size > MAX_INPUT_SIZE_BYTES:
                raise InputTooLargeError(size, MAX_INPUT_SIZE_BYTES)

        # Start with original template content
        content = cmd.content

        # Only process if command has $ARGUMENTS placeholder
        if cmd.has_arguments and user_input is not None:
            # Sanitize user input to prevent template injection (FR-005a)
            sanitized_input = self.sanitize_input(user_input)

            # Substitute $ARGUMENTS with sanitized user input (FR-005)
            content = content.replace("$ARGUMENTS", sanitized_input)

            logger.debug(
                f"Substituted {len(user_input)} bytes of input for: {command_name}"
            )
        elif not cmd.has_arguments:
            # Command doesn't use $ARGUMENTS - return as-is (FR-008)
            logger.debug(
                f"Command {command_name} has no $ARGUMENTS, returning template"
            )
        else:
            # Command has $ARGUMENTS but no input provided
            logger.debug(f"Command {command_name} expects arguments but none provided")

        return content
