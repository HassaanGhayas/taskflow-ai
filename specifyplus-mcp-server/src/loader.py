"""CommandLoader - Discover and parse command files from .claude/commands/."""

import logging
from datetime import datetime
from pathlib import Path

import frontmatter
from yaml import YAMLError

from src.exceptions import CommandParseError, DirectoryNotFoundError
from src.models import CommandDefinition, CommandMetadata
from src.validators import validate_command_name, validate_yaml_frontmatter

logger = logging.getLogger(__name__)


class CommandLoader:
    """Load command definitions from markdown files in a directory.

    The loader discovers *.md files, parses YAML frontmatter and markdown content,
    and returns CommandDefinition objects for valid commands.

    Attributes:
        commands_dir: Path to directory containing .md command files.
    """

    def __init__(self, commands_dir: str) -> None:
        """Initialize the command loader with commands directory path.

        Args:
            commands_dir: Absolute path to .claude/commands/ directory.

        Raises:
            DirectoryNotFoundError: If the directory does not exist (FR-001a).
        """
        self.commands_dir = Path(commands_dir)

        # Validate directory exists (FR-001a)
        if not self.commands_dir.exists():
            raise DirectoryNotFoundError(str(self.commands_dir))

        if not self.commands_dir.is_dir():
            raise DirectoryNotFoundError(str(self.commands_dir))

        logger.info(f"CommandLoader initialized with directory: {commands_dir}")

    def discover_commands(self) -> list[Path]:
        """Discover all markdown files in the commands directory.

        Finds all files matching *.md pattern in the commands directory (FR-001).

        Returns:
            List of Path objects for discovered markdown files.
        """
        # Glob for .md files
        markdown_files = list(self.commands_dir.glob("*.md"))

        logger.debug(f"Discovered {len(markdown_files)} markdown files")
        return markdown_files

    def parse_command_file(self, file_path: Path) -> CommandDefinition | None:
        """Parse a single command file into a CommandDefinition.

        Extracts YAML frontmatter and markdown content, validates structure,
        and returns a complete CommandDefinition (FR-002).

        Args:
            file_path: Path to the .md command file.

        Returns:
            CommandDefinition if parsing succeeds, None if file is malformed.

        Raises:
            CommandParseError: If YAML frontmatter is invalid or missing fields.
        """
        try:
            # Parse frontmatter and content
            post = frontmatter.load(file_path)
            frontmatter_data = post.metadata
            content = post.content

            # Validate YAML frontmatter structure
            validated_frontmatter = validate_yaml_frontmatter(
                frontmatter_data, str(file_path)
            )

            # Create CommandMetadata from validated frontmatter
            metadata = CommandMetadata(**validated_frontmatter)

            # Derive command name from filename (remove .md extension)
            command_name = file_path.stem
            command_name = validate_command_name(command_name)

            # Check if content contains $ARGUMENTS placeholder
            has_arguments = "$ARGUMENTS" in content

            # Get file stats
            file_size = file_path.stat().st_size
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

            # Create CommandDefinition
            definition = CommandDefinition(
                name=command_name,
                file_path=str(file_path.absolute()),
                metadata=metadata,
                content=content,
                has_arguments=has_arguments,
                file_size=file_size,
                last_modified=last_modified,
            )

            logger.debug(f"Parsed command: {command_name} from {file_path}")
            return definition

        except CommandParseError:
            # Re-raise CommandParseError as-is (already has file context)
            raise

        except YAMLError as e:
            # YAML parsing errors
            error = CommandParseError(
                file_path=str(file_path), parse_error=f"YAML parsing error: {str(e)}"
            )
            logger.warning(str(error))
            raise error

        except Exception as e:
            # Unexpected errors
            error = CommandParseError(
                file_path=str(file_path), parse_error=f"Unexpected error: {str(e)}"
            )
            logger.warning(str(error))
            raise error

    def load_all_commands(self) -> dict[str, CommandDefinition]:
        """Load all commands from the commands directory.

        Discovers all markdown files and attempts to parse each one.
        Malformed files are skipped with warnings (FR-012).

        Returns:
            Dictionary mapping command names to CommandDefinition objects.
        """
        commands: dict[str, CommandDefinition] = {}

        markdown_files = self.discover_commands()

        for file_path in markdown_files:
            try:
                definition = self.parse_command_file(file_path)
                if definition is not None:
                    commands[definition.name] = definition

            except CommandParseError as e:
                # Skip malformed files with warning (FR-012)
                logger.warning(
                    f"Skipping malformed command file: {file_path}. " f"Error: {str(e)}"
                )
                continue

        logger.info(f"Loaded {len(commands)} commands from {len(markdown_files)} files")
        return commands
