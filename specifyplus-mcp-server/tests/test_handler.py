"""Unit tests for PromptHandler.

Tests cover:
- Template sanitization (escaping $ARGUMENTS, ${...})
- Input size validation (100KB limit)
- $ARGUMENTS placeholder substitution
- Commands without $ARGUMENTS (FR-008)
- Error handling (command not found, input too large)
"""

import pytest

from src.exceptions import CommandNotFoundError, InputTooLargeError
from src.handler import PromptHandler
from src.models import MAX_INPUT_SIZE_BYTES, CommandDefinition, CommandMetadata


class TestPromptHandlerSanitization:
    """Test template sanitization functionality."""

    @pytest.fixture
    def registry(self, sample_command):
        """Create a test registry with a sample command."""
        from src.registry import CommandRegistry

        registry = CommandRegistry()
        registry.register(sample_command)
        return registry

    @pytest.fixture
    def handler(self, registry):
        """Create PromptHandler with test registry."""
        return PromptHandler(registry)

    @pytest.fixture
    def sample_command(self):
        """Create a sample CommandDefinition for testing."""
        import time

        return CommandDefinition(
            name="test-command",
            file_path="/path/to/test.md",
            metadata=CommandMetadata(description="Test command"),
            content="Here is your input: $ARGUMENTS",
            has_arguments=True,
            file_size=1024,
            last_modified=time.time(),
        )

    def test_sanitize_escapes_literal_arguments(self, handler):
        """Test that literal $ARGUMENTS is escaped."""
        result = handler.sanitize_input("Use $ARGUMENTS for input")
        assert result == "Use \\$ARGUMENTS for input"

    def test_sanitize_escapes_shell_syntax(self, handler):
        """Test that ${...} patterns are escaped."""
        result = handler.sanitize_input("Path: ${HOME}")
        assert result == "Path: \\${HOME}"

        result = handler.sanitize_input("User: ${USER}")
        assert result == "User: \\${USER}"

    def test_sanitize_multiple_patterns(self, handler):
        """Test that multiple patterns are escaped."""
        result = handler.sanitize_input("Use $ARGUMENTS in ${HOME} directory")
        assert result == "Use \\$ARGUMENTS in \\${HOME} directory"

    def test_sanitize_no_changes_needed(self, handler):
        """Test that normal text is unchanged."""
        result = handler.sanitize_input("Just regular text")
        assert result == "Just regular text"

    def test_sanitize_empty_string(self, handler):
        """Test that empty string is handled."""
        result = handler.sanitize_input("")
        assert result == ""


class TestPromptHandlerValidation:
    """Test input validation functionality."""

    @pytest.fixture
    def registry(self, sample_command):
        """Create a test registry with a sample command."""
        from src.registry import CommandRegistry

        registry = CommandRegistry()
        registry.register(sample_command)
        return registry

    @pytest.fixture
    def handler(self, registry):
        """Create PromptHandler with test registry."""
        return PromptHandler(registry)

    @pytest.fixture
    def sample_command(self):
        """Create a sample CommandDefinition for testing."""
        import time

        return CommandDefinition(
            name="test-command",
            file_path="/path/to/test.md",
            metadata=CommandMetadata(description="Test command"),
            content="Input: $ARGUMENTS",
            has_arguments=True,
            file_size=1024,
            last_modified=time.time(),
        )

    def test_valid_input_size(self, handler, sample_command):
        """Test that input under 100KB is accepted."""
        small_input = "a" * 1024  # 1KB
        result = handler.process_prompt("test-command", small_input)
        assert "a" * 1024 in result

    def test_input_at_limit(self, handler, sample_command):
        """Test that input exactly at 100KB is accepted."""
        input_at_limit = "x" * MAX_INPUT_SIZE_BYTES
        result = handler.process_prompt("test-command", input_at_limit)
        assert "x" * MAX_INPUT_SIZE_BYTES in result

    def test_input_exceeds_limit(self, handler):
        """Test that input over 100KB raises InputTooLargeError."""
        large_input = "x" * (MAX_INPUT_SIZE_BYTES + 1)

        with pytest.raises(InputTooLargeError) as exc_info:
            handler.process_prompt("test-command", large_input)

        assert "exceeds maximum allowed size" in str(exc_info.value)

    def test_none_input_accepted(self, handler, sample_command):
        """Test that None input is accepted (user didn't provide input)."""
        # Command has $ARGUMENTS but user provides None - should work
        result = handler.process_prompt("test-command", None)
        assert "Input: $ARGUMENTS" in result  # Placeholder not substituted

    def test_command_not_found(self, handler):
        """Test that non-existent command raises CommandNotFoundError."""
        with pytest.raises(CommandNotFoundError) as exc_info:
            handler.process_prompt("non-existent-command", "input")

        assert "Command not found: non-existent-command" in str(exc_info.value)


class TestPromptHandlerSubstitution:
    """Test $ARGUMENTS placeholder substitution."""

    @pytest.fixture
    def handler(self, registry_with_command):
        """Create PromptHandler with test registry."""
        return PromptHandler(registry_with_command)

    @pytest.fixture
    def registry_with_command(self):
        """Create a test registry with a command that uses $ARGUMENTS."""
        import time

        from src.registry import CommandRegistry

        registry = CommandRegistry()
        registry.register(
            CommandDefinition(
                name="has-arguments",
                file_path="/path/to/has-args.md",
                metadata=CommandMetadata(description="Command with arguments"),
                content="Template: $ARGUMENTS",
                has_arguments=True,
                file_size=1024,
                last_modified=time.time(),
            )
        )
        return registry

    def test_substitutes_user_input(self, handler):
        """Test that $ARGUMENTS is replaced with user input."""
        result = handler.process_prompt("has-arguments", "my custom input")
        assert result == "Template: my custom input"

    def test_substitutes_sanitized_input(self, handler):
        """Test that user input is sanitized before substitution."""
        # User input contains template syntax - should be escaped
        result = handler.process_prompt("has-arguments", "Use ${HOME} and $ARGUMENTS")
        assert "\\${HOME}" in result
        assert "\\$ARGUMENTS" in result

    def test_multiline_substitution(self, handler):
        """Test that multi-line input is substituted correctly."""
        multiline_input = "Line 1\nLine 2\nLine 3"
        result = handler.process_prompt("has-arguments", multiline_input)
        assert "Line 1\nLine 2\nLine 3" in result

    def test_special_characters_in_input(self, handler):
        """Test that special characters in input are preserved."""
        special_input = "Input with: <>&\"'\\"
        result = handler.process_prompt("has-arguments", special_input)
        # Check that all special characters from input appear in result
        assert all(c in result for c in ["<", ">", "&", '"', "'", "\\"])
        assert "Input with:" in result


class TestPromptHandlerNoArguments:
    """Test commands without $ARGUMENTS placeholder (FR-008)."""

    @pytest.fixture
    def handler(self, registry_no_args):
        """Create PromptHandler with test registry."""
        return PromptHandler(registry_no_args)

    @pytest.fixture
    def registry_no_args(self):
        """Create a test registry with a command without $ARGUMENTS."""
        import time

        from src.registry import CommandRegistry

        registry = CommandRegistry()
        registry.register(
            CommandDefinition(
                name="no-arguments",
                file_path="/path/to/no-args.md",
                metadata=CommandMetadata(description="Command without arguments"),
                content="Static template without placeholders",
                has_arguments=False,
                file_size=512,
                last_modified=time.time(),
            )
        )
        return registry

    def test_returns_template_unchanged(self, handler):
        """Test that command without $ARGUMENTS returns template as-is."""
        result = handler.process_prompt("no-arguments", "ignored input")
        assert result == "Static template without placeholders"

    def test_ignores_none_input(self, handler):
        """Test that None input is ignored for no-args command."""
        result = handler.process_prompt("no-arguments", None)
        assert result == "Static template without placeholders"

    def test_ignores_any_input(self, handler):
        """Test that any input is ignored for no-args command."""
        result = handler.process_prompt("no-arguments", "this should be ignored")
        assert result == "Static template without placeholders"


class TestPromptHandlerComplexScenarios:
    """Test complex real-world scenarios."""

    @pytest.fixture
    def registry(self, sample_commands):
        """Create a test registry with multiple commands."""
        from src.registry import CommandRegistry

        registry = CommandRegistry()
        for cmd in sample_commands:
            registry.register(cmd)
        return registry

    @pytest.fixture
    def handler(self, registry):
        """Create PromptHandler with test registry."""
        return PromptHandler(registry)

    @pytest.fixture
    def sample_commands(self):
        """Create sample commands for complex scenarios."""
        import time

        ts = time.time()
        return [
            CommandDefinition(
                name="simple-substitution",
                file_path="/simple.md",
                metadata=CommandMetadata(description="Simple substitution"),
                content="Create a feature: $ARGUMENTS",
                has_arguments=True,
                file_size=512,
                last_modified=ts,
            ),
            CommandDefinition(
                name="no-substitution",
                file_path="/no-sub.md",
                metadata=CommandMetadata(description="No substitution needed"),
                content="List all available features",
                has_arguments=False,
                file_size=256,
                last_modified=ts,
            ),
            CommandDefinition(
                name="large-template",
                file_path="/large.md",
                metadata=CommandMetadata(description="Large template"),
                content="Header\n\n$ARGUMENTS\n\nFooter\n",
                has_arguments=True,
                file_size=2048,
                last_modified=ts,
            ),
        ]

    def test_multiple_commands_work_correctly(self, handler):
        """Test that multiple commands work independently."""
        # Simple substitution
        result = handler.process_prompt("simple-substitution", "user auth")
        assert "Create a feature: user auth" in result

        # No substitution
        result = handler.process_prompt("no-substitution", "ignored")
        assert "List all available features" == result

        # Large template
        result = handler.process_prompt("large-template", "middle content")
        assert "Header\n\nmiddle content\n\nFooter\n" == result

    def test_error_recovery_for_invalid_command(self, handler):
        """Test that errors don't corrupt state."""
        # Try invalid command
        with pytest.raises(CommandNotFoundError):
            handler.process_prompt("invalid-command", "input")

        # Valid commands still work
        result = handler.process_prompt("simple-substitution", "test")
        assert "Create a feature: test" in result

    def test_consecutive_substitutions(self, handler):
        """Test that consecutive calls don't interfere."""
        result1 = handler.process_prompt("simple-substitution", "first")
        assert "Create a feature: first" in result1

        result2 = handler.process_prompt("simple-substitution", "second")
        assert "Create a feature: second" in result2

        result3 = handler.process_prompt("simple-substitution", "third")
        assert "Create a feature: third" in result3
