"""Unit tests for CommandRegistry class."""

import logging
from datetime import datetime

import pytest

from src.models import CommandDefinition, CommandMetadata
from src.registry import CommandRegistry

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


class TestCommandRegistryInit:
    """Tests for CommandRegistry initialization."""

    def test_init_creates_empty_registry(self):
        """Test that initialization creates empty registry."""
        registry = CommandRegistry()
        assert registry.count() == 0
        assert registry.list_commands() == []

    def test_registry_has_lock(self):
        """Test that registry has lock for thread safety."""
        registry = CommandRegistry()
        assert hasattr(registry, "_lock")
        assert registry._lock is not None


class TestRegister:
    """Tests for register() method."""

    @pytest.fixture
    def sample_command(self):
        """Fixture for a sample command."""
        metadata = CommandMetadata(description="Test command")
        return CommandDefinition(
            name="sp.test",
            file_path="/path/to/test.md",
            metadata=metadata,
            content="# Test\n\n$ARGUMENTS",
            has_arguments=True,
            file_size=100,
            last_modified=datetime.now(),
        )

    def test_register_command(self, sample_command):
        """Test registering a single command."""
        registry = CommandRegistry()
        registry.register(sample_command)

        assert registry.count() == 1
        assert "sp.test" in registry.list_commands()

    def test_register_multiple_commands(self):
        """Test registering multiple commands."""
        registry = CommandRegistry()

        commands = []
        for i in range(3):
            metadata = CommandMetadata(description=f"Command {i}")
            cmd = CommandDefinition(
                name=f"cmd{i}",
                file_path=f"/path/cmd{i}.md",
                metadata=metadata,
                content=f"# Command {i}",
                has_arguments=False,
                file_size=100,
                last_modified=datetime.now(),
            )
            commands.append(cmd)
            registry.register(cmd)

        assert registry.count() == 3
        assert len(registry.list_commands()) == 3

    def test_register_overwrites_existing(self, sample_command):
        """Test that registering existing command overwrites it."""
        registry = CommandRegistry()
        registry.register(sample_command)

        # Create new version with different content
        new_metadata = CommandMetadata(description="Updated command")
        new_cmd = CommandDefinition(
            name="sp.test",
            file_path="/path/to/test.md",
            metadata=new_metadata,
            content="# Updated\n\n$ARGUMENTS",
            has_arguments=True,
            file_size=150,
            last_modified=datetime.now(),
        )
        registry.register(new_cmd)

        assert registry.count() == 1
        retrieved = registry.get("sp.test")
        assert retrieved.metadata.description == "Updated command"
        assert retrieved.file_size == 150


class TestGet:
    """Tests for get() method."""

    @pytest.fixture
    def sample_registry(self):
        """Fixture for a registry with sample commands."""
        registry = CommandRegistry()

        commands = [
            ("sp.specify", "Create specification"),
            ("sp.plan", "Create plan"),
            ("sp.tasks", "Create tasks"),
        ]

        for name, desc in commands:
            metadata = CommandMetadata(description=desc)
            cmd = CommandDefinition(
                name=name,
                file_path=f"/path/{name}.md",
                metadata=metadata,
                content=f"# {desc}",
                has_arguments=True,
                file_size=100,
                last_modified=datetime.now(),
            )
            registry.register(cmd)

        return registry

    def test_get_existing_command(self, sample_registry):
        """Test retrieving an existing command."""
        cmd = sample_registry.get("sp.specify")
        assert cmd is not None
        assert cmd.name == "sp.specify"
        assert cmd.metadata.description == "Create specification"

    def test_get_nonexistent_command(self, sample_registry):
        """Test retrieving a nonexistent command."""
        cmd = sample_registry.get("sp.nonexistent")
        assert cmd is None

    def test_get_from_empty_registry(self):
        """Test getting from empty registry."""
        registry = CommandRegistry()
        cmd = registry.get("any")
        assert cmd is None


class TestListCommands:
    """Tests for list_commands() method."""

    def test_list_empty_registry(self):
        """Test listing from empty registry."""
        registry = CommandRegistry()
        commands = registry.list_commands()
        assert commands == []

    def test_list_single_command(self):
        """Test listing single command."""
        registry = CommandRegistry()
        metadata = CommandMetadata(description="Test")
        cmd = CommandDefinition(
            name="sp.test",
            file_path="/path/test.md",
            metadata=metadata,
            content="# Test",
            has_arguments=False,
            file_size=100,
            last_modified=datetime.now(),
        )
        registry.register(cmd)

        commands = registry.list_commands()
        assert commands == ["sp.test"]

    def test_list_multiple_commands_sorted(self):
        """Test listing multiple commands returns sorted list."""
        registry = CommandRegistry()

        # Register in random order
        for name in ["sp.tasks", "sp.specify", "sp.plan"]:
            metadata = CommandMetadata(description=f"Test {name}")
            cmd = CommandDefinition(
                name=name,
                file_path=f"/path/{name}.md",
                metadata=metadata,
                content=f"# {name}",
                has_arguments=False,
                file_size=100,
                last_modified=datetime.now(),
            )
            registry.register(cmd)

        commands = registry.list_commands()
        assert commands == ["sp.plan", "sp.specify", "sp.tasks"]


class TestUpdateAll:
    """Tests for update_all() method."""

    @pytest.fixture
    def sample_commands_dict(self):
        """Fixture for a dictionary of commands."""
        commands = {}
        for i in range(3):
            metadata = CommandMetadata(description=f"Command {i}")
            commands[f"cmd{i}"] = CommandDefinition(
                name=f"cmd{i}",
                file_path=f"/path/cmd{i}.md",
                metadata=metadata,
                content=f"# Command {i}",
                has_arguments=False,
                file_size=100,
                last_modified=datetime.now(),
            )
        return commands

    def test_update_all_replaces_registry(self, sample_commands_dict):
        """Test that update_all replaces entire registry."""
        registry = CommandRegistry()

        # Add initial command
        metadata = CommandMetadata(description="Old")
        old_cmd = CommandDefinition(
            name="old",
            file_path="/path/old.md",
            metadata=metadata,
            content="# Old",
            has_arguments=False,
            file_size=100,
            last_modified=datetime.now(),
        )
        registry.register(old_cmd)

        assert registry.count() == 1

        # Update with new commands
        registry.update_all(sample_commands_dict)

        assert registry.count() == 3
        assert "old" not in registry.list_commands()
        assert "cmd0" in registry.list_commands()

    def test_update_all_empty_dict(self):
        """Test updating with empty dictionary."""
        registry = CommandRegistry()

        # Add commands
        for i in range(2):
            metadata = CommandMetadata(description=f"Cmd {i}")
            cmd = CommandDefinition(
                name=f"cmd{i}",
                file_path=f"/path/cmd{i}.md",
                metadata=metadata,
                content=f"# Cmd {i}",
                has_arguments=False,
                file_size=100,
                last_modified=datetime.now(),
            )
            registry.register(cmd)

        assert registry.count() == 2

        # Clear with empty dict
        registry.update_all({})
        assert registry.count() == 0


class TestClear:
    """Tests for clear() method."""

    def test_clear_removes_all_commands(self):
        """Test that clear removes all commands."""
        registry = CommandRegistry()

        # Add commands
        for i in range(5):
            metadata = CommandMetadata(description=f"Cmd {i}")
            cmd = CommandDefinition(
                name=f"cmd{i}",
                file_path=f"/path/cmd{i}.md",
                metadata=metadata,
                content=f"# Cmd {i}",
                has_arguments=False,
                file_size=100,
                last_modified=datetime.now(),
            )
            registry.register(cmd)

        assert registry.count() == 5

        # Clear registry
        registry.clear()
        assert registry.count() == 0
        assert registry.list_commands() == []

    def test_clear_empty_registry(self):
        """Test clearing already empty registry."""
        registry = CommandRegistry()
        assert registry.count() == 0

        registry.clear()
        assert registry.count() == 0


class TestCount:
    """Tests for count() method."""

    def test_count_empty_registry(self):
        """Test count on empty registry."""
        registry = CommandRegistry()
        assert registry.count() == 0

    def test_count_single_command(self):
        """Test count with single command."""
        registry = CommandRegistry()
        metadata = CommandMetadata(description="Test")
        cmd = CommandDefinition(
            name="test",
            file_path="/path/test.md",
            metadata=metadata,
            content="# Test",
            has_arguments=False,
            file_size=100,
            last_modified=datetime.now(),
        )
        registry.register(cmd)

        assert registry.count() == 1

    def test_count_multiple_commands(self):
        """Test count with multiple commands."""
        registry = CommandRegistry()

        for i in range(10):
            metadata = CommandMetadata(description=f"Cmd {i}")
            cmd = CommandDefinition(
                name=f"cmd{i}",
                file_path=f"/path/cmd{i}.md",
                metadata=metadata,
                content=f"# Cmd {i}",
                has_arguments=False,
                file_size=100,
                last_modified=datetime.now(),
            )
            registry.register(cmd)

        assert registry.count() == 10


class TestThreadSafety:
    """Tests for thread safety (SC-003)."""

    def test_concurrent_register(self):
        """Test that concurrent registration is thread-safe."""
        import threading

        registry = CommandRegistry()
        num_threads = 10
        num_commands = 5

        def register_commands(thread_id):
            for i in range(num_commands):
                metadata = CommandMetadata(description=f"T{thread_id}-C{i}")
                cmd = CommandDefinition(
                    name=f"t{thread_id}_c{i}",
                    file_path=f"/path/t{thread_id}_c{i}.md",
                    metadata=metadata,
                    content=f"# T{thread_id}-C{i}",
                    has_arguments=False,
                    file_size=100,
                    last_modified=datetime.now(),
                )
                registry.register(cmd)

        # Create and start threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=register_commands, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify all commands were registered
        expected_count = num_threads * num_commands
        assert registry.count() == expected_count

    def test_concurrent_read_write(self):
        """Test concurrent reads and writes."""
        import threading
        import time

        registry = CommandRegistry()

        # Pre-populate with some commands
        for i in range(5):
            metadata = CommandMetadata(description=f"Init {i}")
            cmd = CommandDefinition(
                name=f"init{i}",
                file_path=f"/path/init{i}.md",
                metadata=metadata,
                content=f"# Init {i}",
                has_arguments=False,
                file_size=100,
                last_modified=datetime.now(),
            )
            registry.register(cmd)

        def reader_thread(thread_id):
            for _ in range(100):
                registry.list_commands()
                registry.count()
                time.sleep(0.001)

        def writer_thread(thread_id):
            for i in range(20):
                metadata = CommandMetadata(description=f"Write {thread_id}-{i}")
                cmd = CommandDefinition(
                    name=f"w{thread_id}_{i}",
                    file_path=f"/path/w{thread_id}_{i}.md",
                    metadata=metadata,
                    content=f"# Write {thread_id}-{i}",
                    has_arguments=False,
                    file_size=100,
                    last_modified=datetime.now(),
                )
                registry.register(cmd)
                time.sleep(0.001)

        # Start threads
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=reader_thread, args=(i,)))
        for i in range(2):
            threads.append(threading.Thread(target=writer_thread, args=(i,)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Verify registry integrity
        assert registry.count() == 5 + (2 * 20)
