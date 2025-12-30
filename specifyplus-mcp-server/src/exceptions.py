"""Custom exception classes for SpecifyPlus MCP Server.

Exception Hierarchy:
    SpecifyPlusMCPError (base)
    ├── DirectoryNotFoundError (FR-001a)
    ├── CommandParseError (FR-012)
    ├── CommandNotFoundError
    └── InputTooLargeError (FR-004a)
"""


class SpecifyPlusMCPError(Exception):
    """Base exception for all SpecifyPlus MCP Server errors.

    All custom exceptions inherit from this class to enable
    catch-all handling when needed.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class DirectoryNotFoundError(SpecifyPlusMCPError):
    """Raised when the commands directory does not exist (FR-001a).

    The server should fail to start if the configured commands
    directory is missing, as this indicates a configuration error.

    Attributes:
        path: The path that was expected to exist.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(
            message="Commands directory not found",
            details=f"Expected directory at: {path}",
        )


class CommandParseError(SpecifyPlusMCPError):
    """Raised when a command file cannot be parsed (FR-012).

    This occurs when YAML frontmatter is malformed or when
    required fields are missing. Malformed files should be
    skipped with a warning, not cause server failure.

    Attributes:
        file_path: The path to the file that failed to parse.
        parse_error: The underlying parsing error message.
    """

    def __init__(self, file_path: str, parse_error: str) -> None:
        self.file_path = file_path
        self.parse_error = parse_error
        super().__init__(
            message=f"Failed to parse command file: {file_path}", details=parse_error
        )


class CommandNotFoundError(SpecifyPlusMCPError):
    """Raised when a requested command does not exist in the registry.

    This occurs when a user attempts to invoke a command that
    is not loaded or has been removed.

    Attributes:
        command_name: The name of the command that was not found.
        available_commands: Optional list of available command names.
    """

    def __init__(
        self, command_name: str, available_commands: list[str] | None = None
    ) -> None:
        self.command_name = command_name
        self.available_commands = available_commands or []

        details = None
        if self.available_commands:
            commands_list = ", ".join(sorted(self.available_commands))
            details = f"Available commands: {commands_list}"

        super().__init__(message=f"Command not found: {command_name}", details=details)


class InputTooLargeError(SpecifyPlusMCPError):
    """Raised when user input exceeds the maximum allowed size (FR-004a).

    The maximum input size is 100KB (102,400 bytes) to prevent
    resource exhaustion and ensure reasonable response times.

    Attributes:
        size: The actual size of the input in bytes.
        max_size: The maximum allowed size in bytes.
    """

    MAX_SIZE_BYTES = 102_400  # 100KB

    def __init__(self, size: int, max_size: int = MAX_SIZE_BYTES) -> None:
        self.size = size
        self.max_size = max_size
        super().__init__(
            message="Input exceeds maximum allowed size",
            details=f"Input size: {size:,} bytes, maximum: {max_size:,} bytes (100KB)",
        )
