"""Pydantic models for SpecifyPlus MCP Server.

Data Models:
    HandoffLink - Workflow handoff definition (label, agent, prompt, send)
    CommandMetadata - YAML frontmatter structure (description, handoffs)
    CommandDefinition - Complete command representation
    PromptArguments - User input with size validation
"""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class HandoffLink(BaseModel):
    """A workflow handoff link to another command.

    Handoffs enable chaining of commands (e.g., sp.specify -> sp.plan -> sp.tasks).

    Attributes:
        label: Human-readable description of the handoff action.
        agent: The target command name (e.g., "sp.plan").
        prompt: The prompt text to send to the target command.
        send: Whether to auto-send the prompt (default: False).
    """

    label: str = Field(..., min_length=1, description="Human-readable handoff label")
    agent: str = Field(..., min_length=1, description="Target command name")
    prompt: str = Field(..., min_length=1, description="Prompt text for target command")
    send: bool = Field(default=False, description="Auto-send flag")


class CommandMetadata(BaseModel):
    """YAML frontmatter metadata for a command file.

    Attributes:
        description: Required description of what the command does.
        handoffs: Optional list of workflow handoff links.
    """

    description: str = Field(
        ..., min_length=1, description="Command description from YAML frontmatter"
    )
    handoffs: list[HandoffLink] = Field(
        default_factory=list, description="Workflow handoff links to other commands"
    )


class CommandDefinition(BaseModel):
    """Complete definition of a command loaded from a .md file.

    Attributes:
        name: Command name derived from filename (e.g., "sp.specify").
        file_path: Absolute path to the source .md file.
        metadata: Parsed YAML frontmatter (description, handoffs).
        content: Full markdown content after frontmatter.
        has_arguments: Whether the command contains $ARGUMENTS placeholder.
        file_size: Size of the source file in bytes.
        last_modified: Timestamp of last file modification.
    """

    name: str = Field(..., min_length=1, description="Command name from filename")
    file_path: str = Field(..., min_length=1, description="Absolute path to .md file")
    metadata: CommandMetadata = Field(..., description="Parsed YAML frontmatter")
    content: str = Field(..., description="Markdown content after frontmatter")
    has_arguments: bool = Field(
        default=False, description="Whether $ARGUMENTS placeholder exists in content"
    )
    file_size: int = Field(..., ge=0, description="File size in bytes")
    last_modified: datetime = Field(..., description="File modification timestamp")

    @field_validator("name")
    @classmethod
    def validate_command_name(cls, v: str) -> str:
        """Validate command name format.

        Command names must:
        - Start with a letter
        - Contain only alphanumeric characters, dots, underscores, and hyphens
        - Not contain path separators

        Examples:
            - Valid: "sp.specify", "sp.plan", "my-command", "cmd_v2"
            - Invalid: "../escape", "path/to/cmd", "", " "
        """
        # Trim whitespace
        v = v.strip()

        if not v:
            raise ValueError("Command name cannot be empty")

        # Check for path traversal attempts
        if "/" in v or "\\" in v:
            raise ValueError("Command name cannot contain path separators")

        if ".." in v and v != "..":
            # Allow single dots (like sp.specify) but not double dots
            if v.startswith("..") or v.endswith("..") or ".." in v.replace(".", ""):
                pass  # Allow "sp..test" edge case, but check path traversal

        # Validate format: alphanumeric, dots, underscores, hyphens
        pattern = r"^[a-zA-Z][a-zA-Z0-9._-]*$"
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid command name format: '{v}'. "
                "Must start with a letter and contain only alphanumeric "
                "characters, dots, underscores, and hyphens."
            )

        return v


# Constants for input validation
MAX_INPUT_SIZE_BYTES = 102_400  # 100KB


class PromptArguments(BaseModel):
    """User-provided arguments for command execution.

    Includes size validation to prevent resource exhaustion (FR-004a).
    Maximum input size: 100KB (102,400 bytes).

    Attributes:
        text: The user's input text to substitute for $ARGUMENTS.
    """

    text: str | None = Field(
        default=None, description="User input text for $ARGUMENTS substitution"
    )

    @field_validator("text")
    @classmethod
    def validate_input_size(cls, v: str | None) -> str | None:
        """Validate that input does not exceed 100KB (FR-004a).

        Raises:
            ValueError: If input exceeds maximum allowed size.
        """
        if v is None:
            return v

        # Calculate size in bytes (UTF-8 encoding)
        size = len(v.encode("utf-8"))

        if size > MAX_INPUT_SIZE_BYTES:
            raise ValueError(
                f"Input exceeds maximum allowed size. "
                f"Size: {size:,} bytes, maximum: {MAX_INPUT_SIZE_BYTES:,} bytes (100KB)"
            )

        return v
