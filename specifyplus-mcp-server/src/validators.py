"""Validation utilities for SpecifyPlus MCP Server.

Provides standalone validation functions for:
- Command name format validation
- YAML frontmatter validation
- File size validation
"""

import re
from typing import Any

from .exceptions import CommandParseError, InputTooLargeError

# Constants
MAX_INPUT_SIZE_BYTES = 102_400  # 100KB
COMMAND_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9._-]*$")


def validate_command_name(name: str) -> str:
    """Validate and normalize a command name.

    Command names must:
    - Start with a letter
    - Contain only alphanumeric characters, dots, underscores, and hyphens
    - Not contain path separators or traversal sequences

    Args:
        name: The command name to validate.

    Returns:
        The validated and trimmed command name.

    Raises:
        ValueError: If the command name is invalid.

    Examples:
        >>> validate_command_name("sp.specify")
        'sp.specify'
        >>> validate_command_name("  sp.plan  ")
        'sp.plan'
        >>> validate_command_name("../escape")
        Traceback (most recent call last):
            ...
        ValueError: Command name cannot contain path separators
    """
    # Trim whitespace
    name = name.strip()

    if not name:
        raise ValueError("Command name cannot be empty")

    # Check for path traversal attempts
    if "/" in name or "\\" in name:
        raise ValueError("Command name cannot contain path separators")

    # Validate format
    if not COMMAND_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid command name format: '{name}'. "
            "Must start with a letter and contain only alphanumeric "
            "characters, dots, underscores, and hyphens."
        )

    return name


def validate_yaml_frontmatter(
    frontmatter: dict[str, Any], file_path: str
) -> dict[str, Any]:
    """Validate YAML frontmatter structure and required fields.

    Required fields:
    - description: Non-empty string

    Optional fields:
    - handoffs: List of handoff link objects

    Args:
        frontmatter: Parsed YAML frontmatter dictionary.
        file_path: Path to the source file (for error messages).

    Returns:
        The validated frontmatter dictionary.

    Raises:
        CommandParseError: If required fields are missing or invalid.

    Examples:
        >>> validate_yaml_frontmatter({"description": "Test"}, "test.md")
        {'description': 'Test'}
        >>> validate_yaml_frontmatter({}, "test.md")
        Traceback (most recent call last):
            ...
        CommandParseError: Failed to parse command file: test.md
    """
    # Check for description (required)
    description = frontmatter.get("description")

    if description is None:
        raise CommandParseError(
            file_path=file_path, parse_error="Missing required field: 'description'"
        )

    if not isinstance(description, str):
        desc_type = type(description).__name__
        raise CommandParseError(
            file_path=file_path,
            parse_error=f"'description' must be a string, got {desc_type}",
        )

    if not description.strip():
        raise CommandParseError(
            file_path=file_path, parse_error="'description' cannot be empty"
        )

    # Validate handoffs if present
    handoffs = frontmatter.get("handoffs", [])

    if handoffs and not isinstance(handoffs, list):
        raise CommandParseError(
            file_path=file_path,
            parse_error=f"'handoffs' must be a list, got {type(handoffs).__name__}",
        )

    for i, handoff in enumerate(handoffs):
        if not isinstance(handoff, dict):
            h_type = type(handoff).__name__
            raise CommandParseError(
                file_path=file_path,
                parse_error=f"Handoff at index {i} must be an object, got {h_type}",
            )

        # Check required handoff fields
        for field in ("label", "agent", "prompt"):
            if field not in handoff:
                raise CommandParseError(
                    file_path=file_path,
                    parse_error=f"Handoff {i} missing required field: '{field}'",
                )

            if not isinstance(handoff[field], str) or not handoff[field].strip():
                raise CommandParseError(
                    file_path=file_path,
                    parse_error=f"Handoff '{field}' at {i} must be a non-empty string",
                )

        # Validate send field if present
        if "send" in handoff and not isinstance(handoff["send"], bool):
            raise CommandParseError(
                file_path=file_path,
                parse_error=f"Handoff 'send' at index {i} must be a boolean",
            )

    return frontmatter


def validate_file_size(size: int, max_size: int = MAX_INPUT_SIZE_BYTES) -> int:
    """Validate that a file or input size is within limits.

    Args:
        size: The size in bytes to validate.
        max_size: Maximum allowed size in bytes (default: 100KB).

    Returns:
        The validated size.

    Raises:
        InputTooLargeError: If size exceeds the maximum.

    Examples:
        >>> validate_file_size(1000)
        1000
        >>> validate_file_size(200000)
        Traceback (most recent call last):
            ...
        InputTooLargeError: Input exceeds maximum allowed size
    """
    if size > max_size:
        raise InputTooLargeError(size=size, max_size=max_size)

    return size


def validate_input_text(text: str | None) -> str | None:
    """Validate user input text for size constraints (FR-004a).

    Args:
        text: The user input text to validate.

    Returns:
        The validated text, or None if input was None.

    Raises:
        InputTooLargeError: If text exceeds 100KB when encoded as UTF-8.
    """
    if text is None:
        return None

    size = len(text.encode("utf-8"))
    validate_file_size(size)

    return text
