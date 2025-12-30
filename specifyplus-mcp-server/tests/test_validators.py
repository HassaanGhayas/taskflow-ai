"""Tests for validators.py - Validation utilities."""

import pytest

from src.exceptions import CommandParseError, InputTooLargeError
from src.validators import (
    MAX_INPUT_SIZE_BYTES,
    validate_command_name,
    validate_file_size,
    validate_input_text,
    validate_yaml_frontmatter,
)


class TestValidateCommandName:
    """Tests for validate_command_name function."""

    def test_valid_simple_name(self):
        """Test valid simple command name."""
        assert validate_command_name("test") == "test"

    def test_valid_name_with_dots(self):
        """Test valid name with dots."""
        assert validate_command_name("sp.specify") == "sp.specify"

    def test_valid_name_with_hyphens(self):
        """Test valid name with hyphens."""
        assert validate_command_name("my-command") == "my-command"

    def test_valid_name_with_underscores(self):
        """Test valid name with underscores."""
        assert validate_command_name("my_command") == "my_command"

    def test_valid_name_with_numbers(self):
        """Test valid name with numbers."""
        assert validate_command_name("cmd123") == "cmd123"

    def test_valid_complex_name(self):
        """Test valid complex name with multiple allowed characters."""
        assert validate_command_name("sp.my-cmd_v2.0") == "sp.my-cmd_v2.0"

    def test_strips_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_command_name("  sp.plan  ") == "sp.plan"
        assert validate_command_name("\tcommand\n") == "command"

    def test_empty_name_raises(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Command name cannot be empty"):
            validate_command_name("")

    def test_whitespace_only_raises(self):
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="Command name cannot be empty"):
            validate_command_name("   ")

    def test_forward_slash_raises(self):
        """Test that forward slash raises ValueError."""
        with pytest.raises(ValueError, match="cannot contain path separators"):
            validate_command_name("../escape")

    def test_backslash_raises(self):
        """Test that backslash raises ValueError."""
        with pytest.raises(ValueError, match="cannot contain path separators"):
            validate_command_name("..\\escape")

    def test_path_traversal_raises(self):
        """Test that path traversal attempts raise ValueError."""
        with pytest.raises(ValueError, match="cannot contain path separators"):
            validate_command_name("foo/bar")

    def test_name_starting_with_number_raises(self):
        """Test that name starting with number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid command name format"):
            validate_command_name("123command")

    def test_name_starting_with_dot_raises(self):
        """Test that name starting with dot raises ValueError."""
        with pytest.raises(ValueError, match="Invalid command name format"):
            validate_command_name(".hidden")

    def test_name_starting_with_hyphen_raises(self):
        """Test that name starting with hyphen raises ValueError."""
        with pytest.raises(ValueError, match="Invalid command name format"):
            validate_command_name("-invalid")

    def test_name_starting_with_underscore_raises(self):
        """Test that name starting with underscore raises ValueError."""
        with pytest.raises(ValueError, match="Invalid command name format"):
            validate_command_name("_private")

    def test_name_with_spaces_raises(self):
        """Test that name with internal spaces raises ValueError."""
        with pytest.raises(ValueError, match="Invalid command name format"):
            validate_command_name("my command")

    def test_name_with_special_chars_raises(self):
        """Test that name with special characters raises ValueError."""
        invalid_names = ["cmd@home", "cmd#1", "cmd$var", "cmd%val", "cmd&other"]
        for name in invalid_names:
            with pytest.raises(ValueError, match="Invalid command name format"):
                validate_command_name(name)


class TestValidateYamlFrontmatter:
    """Tests for validate_yaml_frontmatter function."""

    def test_valid_minimal_frontmatter(self):
        """Test valid frontmatter with only description."""
        result = validate_yaml_frontmatter({"description": "Test"}, "test.md")
        assert result == {"description": "Test"}

    def test_valid_frontmatter_with_handoffs(self):
        """Test valid frontmatter with handoffs."""
        frontmatter = {
            "description": "Test command",
            "handoffs": [{"label": "Next", "agent": "agent1", "prompt": "Continue"}],
        }
        result = validate_yaml_frontmatter(frontmatter, "test.md")
        assert result == frontmatter

    def test_valid_handoff_with_send_true(self):
        """Test valid handoff with send=true."""
        frontmatter = {
            "description": "Test",
            "handoffs": [
                {"label": "Next", "agent": "agent1", "prompt": "Go", "send": True}
            ],
        }
        result = validate_yaml_frontmatter(frontmatter, "test.md")
        assert result["handoffs"][0]["send"] is True

    def test_valid_handoff_with_send_false(self):
        """Test valid handoff with send=false."""
        frontmatter = {
            "description": "Test",
            "handoffs": [
                {"label": "Next", "agent": "agent1", "prompt": "Go", "send": False}
            ],
        }
        result = validate_yaml_frontmatter(frontmatter, "test.md")
        assert result["handoffs"][0]["send"] is False

    def test_missing_description_raises(self):
        """Test that missing description raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter({}, "test.md")
        assert "Missing required field: 'description'" in str(exc_info.value)

    def test_description_not_string_raises(self):
        """Test that non-string description raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter({"description": 123}, "test.md")
        assert "'description' must be a string, got int" in str(exc_info.value)

    def test_description_list_raises(self):
        """Test that list description raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter({"description": ["a", "b"]}, "test.md")
        assert "'description' must be a string, got list" in str(exc_info.value)

    def test_empty_description_raises(self):
        """Test that empty description raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter({"description": ""}, "test.md")
        assert "'description' cannot be empty" in str(exc_info.value)

    def test_whitespace_description_raises(self):
        """Test that whitespace-only description raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter({"description": "   "}, "test.md")
        assert "'description' cannot be empty" in str(exc_info.value)

    def test_handoffs_not_list_raises(self):
        """Test that non-list handoffs raises CommandParseError."""
        frontmatter = {"description": "Test", "handoffs": "not a list"}
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "'handoffs' must be a list, got str" in str(exc_info.value)

    def test_handoffs_dict_raises(self):
        """Test that dict handoffs raises CommandParseError."""
        frontmatter = {"description": "Test", "handoffs": {"label": "test"}}
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "'handoffs' must be a list, got dict" in str(exc_info.value)

    def test_handoff_not_dict_raises(self):
        """Test that non-dict handoff item raises CommandParseError."""
        frontmatter = {"description": "Test", "handoffs": ["not a dict"]}
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff at index 0 must be an object, got str" in str(exc_info.value)

    def test_handoff_missing_label_raises(self):
        """Test that handoff missing label raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"agent": "a", "prompt": "p"}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 0 missing required field: 'label'" in str(exc_info.value)

    def test_handoff_missing_agent_raises(self):
        """Test that handoff missing agent raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"label": "L", "prompt": "p"}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 0 missing required field: 'agent'" in str(exc_info.value)

    def test_handoff_missing_prompt_raises(self):
        """Test that handoff missing prompt raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"label": "L", "agent": "a"}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 0 missing required field: 'prompt'" in str(exc_info.value)

    def test_handoff_empty_label_raises(self):
        """Test that empty handoff label raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"label": "", "agent": "a", "prompt": "p"}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 'label' at 0 must be a non-empty string" in str(exc_info.value)

    def test_handoff_whitespace_agent_raises(self):
        """Test that whitespace-only agent raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"label": "L", "agent": "   ", "prompt": "p"}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 'agent' at 0 must be a non-empty string" in str(exc_info.value)

    def test_handoff_non_string_label_raises(self):
        """Test that non-string handoff label raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"label": 123, "agent": "a", "prompt": "p"}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 'label' at 0 must be a non-empty string" in str(exc_info.value)

    def test_handoff_send_not_boolean_raises(self):
        """Test that non-boolean send raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"label": "L", "agent": "a", "prompt": "p", "send": "yes"}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 'send' at index 0 must be a boolean" in str(exc_info.value)

    def test_handoff_send_int_raises(self):
        """Test that integer send raises CommandParseError."""
        frontmatter = {
            "description": "Test",
            "handoffs": [{"label": "L", "agent": "a", "prompt": "p", "send": 1}],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 'send' at index 0 must be a boolean" in str(exc_info.value)

    def test_multiple_handoffs_validates_all(self):
        """Test that validation checks all handoffs."""
        frontmatter = {
            "description": "Test",
            "handoffs": [
                {"label": "First", "agent": "a1", "prompt": "p1"},
                {"label": "Second", "agent": "a2"},  # Missing prompt
            ],
        }
        with pytest.raises(CommandParseError) as exc_info:
            validate_yaml_frontmatter(frontmatter, "test.md")
        assert "Handoff 1 missing required field: 'prompt'" in str(exc_info.value)

    def test_empty_handoffs_list_valid(self):
        """Test that empty handoffs list is valid."""
        frontmatter = {"description": "Test", "handoffs": []}
        result = validate_yaml_frontmatter(frontmatter, "test.md")
        assert result["handoffs"] == []


class TestValidateFileSize:
    """Tests for validate_file_size function."""

    def test_valid_size_within_limit(self):
        """Test valid size within limit."""
        assert validate_file_size(1000) == 1000

    def test_valid_size_at_limit(self):
        """Test size exactly at limit."""
        assert validate_file_size(MAX_INPUT_SIZE_BYTES) == MAX_INPUT_SIZE_BYTES

    def test_valid_size_zero(self):
        """Test zero size is valid."""
        assert validate_file_size(0) == 0

    def test_exceeds_default_limit_raises(self):
        """Test that exceeding default limit raises InputTooLargeError."""
        with pytest.raises(InputTooLargeError):
            validate_file_size(MAX_INPUT_SIZE_BYTES + 1)

    def test_custom_max_size(self):
        """Test with custom max_size parameter."""
        assert validate_file_size(500, max_size=1000) == 500

    def test_exceeds_custom_limit_raises(self):
        """Test that exceeding custom limit raises InputTooLargeError."""
        with pytest.raises(InputTooLargeError):
            validate_file_size(1001, max_size=1000)

    def test_large_size_exceeds_raises(self):
        """Test that very large size raises InputTooLargeError."""
        with pytest.raises(InputTooLargeError):
            validate_file_size(1_000_000)  # 1MB


class TestValidateInputText:
    """Tests for validate_input_text function."""

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        assert validate_input_text(None) is None

    def test_valid_text(self):
        """Test valid text passes through."""
        assert validate_input_text("Hello world") == "Hello world"

    def test_empty_string_valid(self):
        """Test empty string is valid."""
        assert validate_input_text("") == ""

    def test_unicode_text(self):
        """Test unicode text is handled correctly."""
        text = "Hello 世界 🌍"
        assert validate_input_text(text) == text

    def test_exceeds_limit_raises(self):
        """Test that text exceeding limit raises InputTooLargeError."""
        large_text = "x" * (MAX_INPUT_SIZE_BYTES + 1)
        with pytest.raises(InputTooLargeError):
            validate_input_text(large_text)

    def test_at_limit_valid(self):
        """Test text exactly at limit is valid."""
        text = "x" * MAX_INPUT_SIZE_BYTES
        assert validate_input_text(text) == text

    def test_unicode_size_calculation(self):
        """Test that size is calculated based on UTF-8 encoding."""
        # Each emoji is 4 bytes in UTF-8
        # 25600 emojis = 102400 bytes = exactly at limit
        emoji_count = MAX_INPUT_SIZE_BYTES // 4
        text = "🌍" * emoji_count
        assert validate_input_text(text) == text

        # One more emoji exceeds limit
        text_over = "🌍" * (emoji_count + 1)
        with pytest.raises(InputTooLargeError):
            validate_input_text(text_over)

    def test_multiline_text(self):
        """Test multiline text is valid."""
        text = "Line 1\nLine 2\nLine 3"
        assert validate_input_text(text) == text

    def test_whitespace_only_valid(self):
        """Test whitespace-only text is valid (size-wise)."""
        text = "   \t\n   "
        assert validate_input_text(text) == text
