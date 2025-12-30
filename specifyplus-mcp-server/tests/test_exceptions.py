"""Unit tests for custom exception classes."""

import pytest

from src.exceptions import (
    CommandNotFoundError,
    CommandParseError,
    DirectoryNotFoundError,
    InputTooLargeError,
    SpecifyPlusMCPError,
)


class TestSpecifyPlusMCPError:
    """Tests for the base exception class."""

    def test_message_only(self):
        """Test exception with message only."""
        error = SpecifyPlusMCPError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details is None

    def test_message_with_details(self):
        """Test exception with message and details."""
        error = SpecifyPlusMCPError("Error occurred", details="Additional info")
        assert str(error) == "Error occurred: Additional info"
        assert error.message == "Error occurred"
        assert error.details == "Additional info"

    def test_inheritance(self):
        """Test that it inherits from Exception."""
        error = SpecifyPlusMCPError("Test")
        assert isinstance(error, Exception)


class TestDirectoryNotFoundError:
    """Tests for DirectoryNotFoundError (FR-001a)."""

    def test_basic_creation(self):
        """Test basic error creation with path."""
        error = DirectoryNotFoundError("/path/to/commands")
        assert error.path == "/path/to/commands"
        assert "Commands directory not found" in str(error)
        assert "/path/to/commands" in str(error)

    def test_inheritance(self):
        """Test that it inherits from base error."""
        error = DirectoryNotFoundError("/test")
        assert isinstance(error, SpecifyPlusMCPError)
        assert isinstance(error, Exception)

    def test_message_format(self):
        """Test the message format includes expected information."""
        error = DirectoryNotFoundError("/my/custom/path")
        assert error.message == "Commands directory not found"
        assert "Expected directory at: /my/custom/path" in error.details


class TestCommandParseError:
    """Tests for CommandParseError (FR-012)."""

    def test_basic_creation(self):
        """Test basic error creation with file path and parse error."""
        error = CommandParseError(
            file_path="/commands/broken.md", parse_error="Invalid YAML syntax"
        )
        assert error.file_path == "/commands/broken.md"
        assert error.parse_error == "Invalid YAML syntax"

    def test_message_format(self):
        """Test the message format."""
        error = CommandParseError(
            file_path="test.md", parse_error="Missing field: description"
        )
        assert "Failed to parse command file: test.md" in str(error)
        assert "Missing field: description" in str(error)

    def test_inheritance(self):
        """Test inheritance chain."""
        error = CommandParseError("file.md", "error")
        assert isinstance(error, SpecifyPlusMCPError)


class TestCommandNotFoundError:
    """Tests for CommandNotFoundError."""

    def test_basic_creation(self):
        """Test basic error creation with command name."""
        error = CommandNotFoundError("sp.unknown")
        assert error.command_name == "sp.unknown"
        assert "Command not found: sp.unknown" in str(error)

    def test_with_available_commands(self):
        """Test error with list of available commands."""
        error = CommandNotFoundError(
            command_name="sp.typo",
            available_commands=["sp.specify", "sp.plan", "sp.tasks"],
        )
        assert error.command_name == "sp.typo"
        assert error.available_commands == ["sp.specify", "sp.plan", "sp.tasks"]
        assert "Available commands:" in str(error)
        assert "sp.specify" in str(error)

    def test_empty_available_commands(self):
        """Test with empty available commands list."""
        error = CommandNotFoundError("sp.test", available_commands=[])
        assert error.available_commands == []
        assert "Available commands:" not in str(error)

    def test_none_available_commands(self):
        """Test with None available commands."""
        error = CommandNotFoundError("sp.test")
        assert error.available_commands == []

    def test_inheritance(self):
        """Test inheritance chain."""
        error = CommandNotFoundError("test")
        assert isinstance(error, SpecifyPlusMCPError)


class TestInputTooLargeError:
    """Tests for InputTooLargeError (FR-004a)."""

    def test_basic_creation(self):
        """Test basic error creation with size."""
        error = InputTooLargeError(size=150_000)
        assert error.size == 150_000
        assert error.max_size == 102_400  # 100KB default
        assert "Input exceeds maximum allowed size" in str(error)

    def test_custom_max_size(self):
        """Test error with custom max size."""
        error = InputTooLargeError(size=60_000, max_size=50_000)
        assert error.size == 60_000
        assert error.max_size == 50_000
        assert "60,000 bytes" in str(error)
        assert "50,000 bytes" in str(error)

    def test_message_format(self):
        """Test the detailed message format."""
        error = InputTooLargeError(size=200_000)
        message = str(error)
        assert "Input size: 200,000 bytes" in message
        assert "maximum: 102,400 bytes" in message
        assert "100KB" in message

    def test_max_size_constant(self):
        """Test that MAX_SIZE_BYTES is correctly defined."""
        assert InputTooLargeError.MAX_SIZE_BYTES == 102_400

    def test_inheritance(self):
        """Test inheritance chain."""
        error = InputTooLargeError(size=200_000)
        assert isinstance(error, SpecifyPlusMCPError)


class TestExceptionRaising:
    """Tests for raising and catching exceptions."""

    def test_catch_specific_exception(self):
        """Test catching a specific exception type."""
        with pytest.raises(DirectoryNotFoundError) as exc_info:
            raise DirectoryNotFoundError("/missing")
        assert exc_info.value.path == "/missing"

    def test_catch_base_exception(self):
        """Test catching all custom exceptions via base class."""
        errors = [
            DirectoryNotFoundError("/path"),
            CommandParseError("file.md", "error"),
            CommandNotFoundError("cmd"),
            InputTooLargeError(200_000),
        ]

        for error in errors:
            with pytest.raises(SpecifyPlusMCPError):
                raise error

    def test_exception_attributes_accessible(self):
        """Test that custom attributes are accessible after catching."""
        try:
            raise CommandParseError("test.md", "bad yaml")
        except CommandParseError as e:
            assert e.file_path == "test.md"
            assert e.parse_error == "bad yaml"
