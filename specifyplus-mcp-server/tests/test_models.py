"""Unit tests for Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models import (
    MAX_INPUT_SIZE_BYTES,
    CommandDefinition,
    CommandMetadata,
    HandoffLink,
    PromptArguments,
)


class TestHandoffLink:
    """Tests for HandoffLink model."""

    def test_valid_handoff(self):
        """Test creating a valid handoff link."""
        handoff = HandoffLink(
            label="Build Technical Plan",
            agent="sp.plan",
            prompt="Create a plan for the feature",
            send=False,
        )
        assert handoff.label == "Build Technical Plan"
        assert handoff.agent == "sp.plan"
        assert handoff.prompt == "Create a plan for the feature"
        assert handoff.send is False

    def test_default_send_value(self):
        """Test that send defaults to False."""
        handoff = HandoffLink(label="Test", agent="sp.test", prompt="Test prompt")
        assert handoff.send is False

    def test_send_true(self):
        """Test handoff with send=True."""
        handoff = HandoffLink(
            label="Auto-run", agent="sp.auto", prompt="Auto execute", send=True
        )
        assert handoff.send is True

    def test_empty_label_fails(self):
        """Test that empty label fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            HandoffLink(label="", agent="sp.test", prompt="test")
        assert "label" in str(exc_info.value)

    def test_empty_agent_fails(self):
        """Test that empty agent fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            HandoffLink(label="Test", agent="", prompt="test")
        assert "agent" in str(exc_info.value)

    def test_empty_prompt_fails(self):
        """Test that empty prompt fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            HandoffLink(label="Test", agent="sp.test", prompt="")
        assert "prompt" in str(exc_info.value)

    def test_missing_required_field(self):
        """Test that missing required field fails."""
        with pytest.raises(ValidationError):
            HandoffLink(label="Test", agent="sp.test")  # Missing prompt


class TestCommandMetadata:
    """Tests for CommandMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid command metadata."""
        metadata = CommandMetadata(
            description="Execute the specification workflow",
            handoffs=[HandoffLink(label="Next", agent="sp.plan", prompt="Plan it")],
        )
        assert metadata.description == "Execute the specification workflow"
        assert len(metadata.handoffs) == 1

    def test_empty_handoffs_default(self):
        """Test that handoffs defaults to empty list."""
        metadata = CommandMetadata(description="Simple command")
        assert metadata.handoffs == []

    def test_multiple_handoffs(self):
        """Test metadata with multiple handoffs."""
        metadata = CommandMetadata(
            description="Multi-handoff command",
            handoffs=[
                HandoffLink(label="Step 1", agent="sp.one", prompt="First"),
                HandoffLink(label="Step 2", agent="sp.two", prompt="Second"),
                HandoffLink(label="Step 3", agent="sp.three", prompt="Third"),
            ],
        )
        assert len(metadata.handoffs) == 3

    def test_empty_description_fails(self):
        """Test that empty description fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            CommandMetadata(description="")
        assert "description" in str(exc_info.value)

    def test_missing_description_fails(self):
        """Test that missing description fails validation."""
        with pytest.raises(ValidationError):
            CommandMetadata()  # type: ignore


class TestCommandDefinition:
    """Tests for CommandDefinition model."""

    @pytest.fixture
    def valid_metadata(self):
        """Fixture for valid command metadata."""
        return CommandMetadata(description="Test command")

    @pytest.fixture
    def valid_command(self, valid_metadata):
        """Fixture for a valid command definition."""
        return CommandDefinition(
            name="sp.test",
            file_path="/home/user/.claude/commands/sp.test.md",
            metadata=valid_metadata,
            content="# Test\n\n$ARGUMENTS",
            has_arguments=True,
            file_size=1024,
            last_modified=datetime.now(),
        )

    def test_valid_command(self, valid_command):
        """Test creating a valid command definition."""
        assert valid_command.name == "sp.test"
        assert valid_command.has_arguments is True
        assert valid_command.file_size == 1024

    def test_command_name_validation_valid_names(self, valid_metadata):
        """Test various valid command names."""
        valid_names = [
            "sp.specify",
            "sp.plan",
            "sp.tasks",
            "my-command",
            "cmd_v2",
            "A1",
            "test.foo.bar",
            "a",
        ]
        for name in valid_names:
            cmd = CommandDefinition(
                name=name,
                file_path=f"/path/{name}.md",
                metadata=valid_metadata,
                content="test",
                file_size=100,
                last_modified=datetime.now(),
            )
            assert cmd.name == name

    def test_command_name_validation_invalid_names(self, valid_metadata):
        """Test that invalid command names are rejected."""
        invalid_names = [
            "",
            " ",
            "../escape",
            "path/to/cmd",
            "cmd\\path",
            "1starts_with_number",
            "-starts-with-dash",
            ".starts-with-dot",
        ]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                CommandDefinition(
                    name=name,
                    file_path="/path/test.md",
                    metadata=valid_metadata,
                    content="test",
                    file_size=100,
                    last_modified=datetime.now(),
                )

    def test_command_name_trimmed(self, valid_metadata):
        """Test that command names are trimmed."""
        cmd = CommandDefinition(
            name="  sp.test  ",
            file_path="/path/sp.test.md",
            metadata=valid_metadata,
            content="test",
            file_size=100,
            last_modified=datetime.now(),
        )
        assert cmd.name == "sp.test"

    def test_file_size_negative_fails(self, valid_metadata):
        """Test that negative file size fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            CommandDefinition(
                name="sp.test",
                file_path="/path/test.md",
                metadata=valid_metadata,
                content="test",
                file_size=-1,
                last_modified=datetime.now(),
            )
        assert "file_size" in str(exc_info.value)

    def test_has_arguments_default_false(self, valid_metadata):
        """Test that has_arguments defaults to False."""
        cmd = CommandDefinition(
            name="sp.test",
            file_path="/path/test.md",
            metadata=valid_metadata,
            content="test",
            file_size=100,
            last_modified=datetime.now(),
        )
        assert cmd.has_arguments is False


class TestPromptArguments:
    """Tests for PromptArguments model."""

    def test_valid_text(self):
        """Test creating valid prompt arguments."""
        args = PromptArguments(text="Add user authentication feature")
        assert args.text == "Add user authentication feature"

    def test_none_text(self):
        """Test that None text is allowed."""
        args = PromptArguments(text=None)
        assert args.text is None

    def test_empty_text(self):
        """Test that empty text is allowed."""
        args = PromptArguments(text="")
        assert args.text == ""

    def test_default_text_none(self):
        """Test that text defaults to None."""
        args = PromptArguments()
        assert args.text is None

    def test_size_limit_under(self):
        """Test text under the size limit."""
        text = "a" * 50_000  # 50KB
        args = PromptArguments(text=text)
        assert args.text == text

    def test_size_limit_exact(self):
        """Test text at exactly the size limit."""
        text = "a" * 102_400  # Exactly 100KB
        args = PromptArguments(text=text)
        assert args.text == text

    def test_size_limit_exceeded(self):
        """Test that text over size limit fails validation (FR-004a)."""
        text = "a" * 102_401  # Just over 100KB
        with pytest.raises(ValidationError) as exc_info:
            PromptArguments(text=text)
        assert "maximum allowed size" in str(exc_info.value).lower()

    def test_size_limit_unicode(self):
        """Test size validation with multi-byte unicode characters."""
        # Use a known 4-byte emoji
        emoji = "\U0001f600"  # Grinning face, 4 bytes in UTF-8
        assert len(emoji.encode("utf-8")) == 4

        # 25,600 emojis = 102,400 bytes = exactly 100KB
        text = emoji * 25_600
        args = PromptArguments(text=text)
        assert args.text == text

        # 25,601 emojis = 102,404 bytes = over 100KB
        text_over = emoji * 25_601
        with pytest.raises(ValidationError):
            PromptArguments(text=text_over)

    def test_max_size_constant(self):
        """Test that MAX_INPUT_SIZE_BYTES is correctly defined."""
        assert MAX_INPUT_SIZE_BYTES == 102_400


class TestModelSerialization:
    """Tests for model serialization/deserialization."""

    def test_handoff_to_dict(self):
        """Test HandoffLink serialization to dict."""
        handoff = HandoffLink(
            label="Test", agent="sp.test", prompt="Do something", send=True
        )
        data = handoff.model_dump()
        assert data == {
            "label": "Test",
            "agent": "sp.test",
            "prompt": "Do something",
            "send": True,
        }

    def test_command_metadata_to_dict(self):
        """Test CommandMetadata serialization."""
        metadata = CommandMetadata(
            description="Test command",
            handoffs=[HandoffLink(label="Next", agent="sp.next", prompt="Continue")],
        )
        data = metadata.model_dump()
        assert data["description"] == "Test command"
        assert len(data["handoffs"]) == 1

    def test_from_dict(self):
        """Test model creation from dictionary."""
        data = {"label": "Test", "agent": "sp.test", "prompt": "Do it"}
        handoff = HandoffLink.model_validate(data)
        assert handoff.label == "Test"
        assert handoff.send is False  # Default
