"""Unit tests for CommandLoader class."""

import logging
import tempfile
from pathlib import Path

import pytest

from src.exceptions import CommandParseError, DirectoryNotFoundError
from src.loader import CommandLoader
from src.models import CommandDefinition

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


class TestCommandLoaderInit:
    """Tests for CommandLoader initialization."""

    def test_init_with_valid_directory(self):
        """Test initialization with valid commands directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            loader = CommandLoader(str(commands_dir))
            assert loader.commands_dir == commands_dir

    def test_init_with_missing_directory(self):
        """Test that initialization fails with missing directory (FR-001a)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "nonexistent"

            with pytest.raises(DirectoryNotFoundError) as exc_info:
                CommandLoader(str(commands_dir))
            assert "Commands directory not found" in str(exc_info.value)
            assert str(commands_dir) in str(exc_info.value)

    def test_init_with_file_instead_of_directory(self):
        """Test that initialization fails with file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "not_a_dir.md"
            file_path.write_text("# test")

            with pytest.raises(DirectoryNotFoundError):
                CommandLoader(str(file_path))


class TestDiscoverCommands:
    """Tests for discover_commands() method."""

    def test_discover_no_files(self):
        """Test discovering when no .md files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            loader = CommandLoader(str(commands_dir))
            files = loader.discover_commands()
            assert files == []

    def test_discover_single_file(self):
        """Test discovering a single .md file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()
            (commands_dir / "test.md").write_text("# test")

            loader = CommandLoader(str(commands_dir))
            files = loader.discover_commands()
            assert len(files) == 1
            assert files[0].name == "test.md"

    def test_discover_multiple_files(self):
        """Test discovering multiple .md files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()
            (commands_dir / "sp.specify.md").write_text("# specify")
            (commands_dir / "sp.plan.md").write_text("# plan")
            (commands_dir / "sp.tasks.md").write_text("# tasks")

            loader = CommandLoader(str(commands_dir))
            files = loader.discover_commands()
            assert len(files) == 3
            file_names = {f.name for f in files}
            assert "sp.specify.md" in file_names
            assert "sp.plan.md" in file_names
            assert "sp.tasks.md" in file_names

    def test_discover_ignores_non_md_files(self):
        """Test that non-.md files are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()
            (commands_dir / "test.md").write_text("# markdown")
            (commands_dir / "readme.txt").write_text("text")
            (commands_dir / "script.py").write_text("python")

            loader = CommandLoader(str(commands_dir))
            files = loader.discover_commands()
            assert len(files) == 1
            assert files[0].name == "test.md"


class TestParseCommandFile:
    """Tests for parse_command_file() method."""

    @pytest.fixture
    def valid_command_file(self):
        """Fixture for a valid command file."""
        content = """---
description: "Test command for parsing"
---

# Test Command

This is a test.

## Arguments

$ARGUMENTS
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        yield file_path

        # Cleanup
        if file_path.exists():
            file_path.unlink()

    def test_parse_valid_command(self, valid_command_file):
        """Test parsing a valid command file."""
        loader = CommandLoader(str(valid_command_file.parent))
        definition = loader.parse_command_file(valid_command_file)

        assert isinstance(definition, CommandDefinition)
        assert definition.name == valid_command_file.stem
        assert definition.has_arguments is True
        assert "$ARGUMENTS" in definition.content
        assert definition.metadata.description == "Test command for parsing"

    def test_parse_command_without_arguments(self):
        """Test parsing command without $ARGUMENTS."""
        content = """---
description: "Command without arguments"
---

# Simple Command

No arguments here.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        loader = CommandLoader(str(file_path.parent))
        definition = loader.parse_command_file(file_path)

        assert definition.has_arguments is False
        assert "$ARGUMENTS" not in definition.content

        file_path.unlink()

    def test_parse_invalid_yaml(self):
        """Test that invalid YAML raises CommandParseError."""
        content = """---
description: "Invalid YAML
unclosed quote:
---

# Test
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        loader = CommandLoader(str(file_path.parent))
        with pytest.raises(CommandParseError) as exc_info:
            loader.parse_command_file(file_path)
        assert "YAML parsing error" in str(exc_info.value)

        file_path.unlink()

    def test_parse_missing_description(self):
        """Test that missing description raises CommandParseError."""
        content = """---
---

# Test
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        loader = CommandLoader(str(file_path.parent))
        with pytest.raises(CommandParseError) as exc_info:
            loader.parse_command_file(file_path)
        assert "description" in str(exc_info.value).lower()

        file_path.unlink()

    def test_parse_empty_description(self):
        """Test that empty description raises CommandParseError."""
        content = """---
description: ""
---

# Test
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        loader = CommandLoader(str(file_path.parent))
        with pytest.raises(CommandParseError) as exc_info:
            loader.parse_command_file(file_path)
        assert "cannot be empty" in str(exc_info.value)

        file_path.unlink()

    def test_parse_with_handoffs(self):
        """Test parsing command with handoffs."""
        content = """---
description: "Command with handoffs"
handoffs:
  - label: "Plan it"
    agent: "sp.plan"
    prompt: "Create a plan"
    send: false
---

# Test
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            file_path = Path(f.name)

        loader = CommandLoader(str(file_path.parent))
        definition = loader.parse_command_file(file_path)

        assert len(definition.metadata.handoffs) == 1
        handoff = definition.metadata.handoffs[0]
        assert handoff.label == "Plan it"
        assert handoff.agent == "sp.plan"

        file_path.unlink()


class TestLoadAllCommands:
    """Tests for load_all_commands() method."""

    def test_load_all_valid_commands(self):
        """Test loading all valid commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Create multiple valid command files
            for name in ["sp.specify", "sp.plan", "sp.tasks"]:
                content = f"""---
description: "Test {name}"
---

# {name}

## Arguments

$ARGUMENTS
"""
                (commands_dir / f"{name}.md").write_text(content)

            loader = CommandLoader(str(commands_dir))
            commands = loader.load_all_commands()

            assert len(commands) == 3
            assert "sp.specify" in commands
            assert "sp.plan" in commands
            assert "sp.tasks" in commands

    def test_load_skips_malformed_file(self):
        """Test that malformed files are skipped (FR-012)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Valid file
            (commands_dir / "valid.md").write_text(
                """---
description: "Valid"
---

# Valid

$ARGUMENTS
"""
            )

            # Malformed file (invalid YAML)
            (commands_dir / "broken.md").write_text(
                """---
description: "Unclosed "quote

---

# Broken
"""
            )

            loader = CommandLoader(str(commands_dir))
            commands = loader.load_all_commands()

            # Should only load the valid file
            assert len(commands) == 1
            assert "valid" in commands
            assert "broken" not in commands

    def test_load_returns_empty_dict_when_no_files(self):
        """Test loading when no command files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            loader = CommandLoader(str(commands_dir))
            commands = loader.load_all_commands()

            assert commands == {}

    def test_load_all_skips_files_without_frontmatter(self):
        """Test that files without frontmatter are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            commands_dir.mkdir()

            # Valid file
            (commands_dir / "valid.md").write_text(
                """---
description: "Valid"
---

# Valid
"""
            )

            # File without frontmatter
            (commands_dir / "no_frontmatter.md").write_text(
                """# No frontmatter

Just markdown.
"""
            )

            loader = CommandLoader(str(commands_dir))
            commands = loader.load_all_commands()

            assert len(commands) == 1
            assert "valid" in commands
            assert "no_frontmatter" not in commands
