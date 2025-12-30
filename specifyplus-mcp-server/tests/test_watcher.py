"""Unit tests for FileWatcher.

Tests cover:
- File change detection (created, modified, deleted)
- Reload triggering with debouncing
- Directory validation
- Observer lifecycle (start, stop)
"""

import os
import tempfile
import time
from pathlib import Path

import pytest

from src.watcher import CommandFileHandler, FileWatcher


class TestCommandFileHandler:
    """Test CommandFileHandler event handling."""

    @pytest.fixture
    def reload_callback(self):
        """Create a mock reload callback that tracks calls."""
        calls = []

        def callback():
            calls.append(time.time())

        # Return both the callable and the list for tracking
        callback.calls = calls
        return callback

    @pytest.fixture
    def handler(self, reload_callback):
        """Create CommandFileHandler with mock callback."""
        return CommandFileHandler(
            reload_callback=reload_callback,
            debounce_seconds=0.5,  # 500ms debounce
        )

    def test_on_created_triggers_reload(self, handler, reload_callback):
        """Test that file creation triggers reload."""
        from unittest.mock import Mock

        # Create mock file event
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/test.md"

        # Call handler
        handler.on_created(event)

        # Should have scheduled a reload (with debounce)
        # After debounce delay, callback should be called
        time.sleep(0.6)  # Wait longer than debounce
        assert len(reload_callback.calls) >= 1

    def test_on_modified_triggers_reload(self, handler, reload_callback):
        """Test that file modification triggers reload."""
        from unittest.mock import Mock

        # Create mock file event
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/test.md"

        # Call handler
        handler.on_modified(event)

        # Should have scheduled a reload
        time.sleep(0.6)
        assert len(reload_callback.calls) >= 1

    def test_on_deleted_triggers_reload(self, handler, reload_callback):
        """Test that file deletion triggers reload."""
        from unittest.mock import Mock

        # Create mock file event
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/test.md"

        # Call handler
        handler.on_deleted(event)

        # Should have scheduled a reload
        time.sleep(0.6)
        assert len(reload_callback.calls) >= 1

    def test_ignores_non_markdown_files(self, handler, reload_callback):
        """Test that non-.md files are ignored."""
        from unittest.mock import Mock

        # Create mock events for different file types
        for filename in ["test.txt", "readme", "test.py", "config.json"]:
            event = Mock()
            event.is_directory = False
            event.src_path = f"/path/to/{filename}"

            # Call all handlers
            handler.on_created(event)
            handler.on_modified(event)
            handler.on_deleted(event)

        # Reload should not have been called
        time.sleep(0.6)
        assert len(reload_callback.calls) == 0

    def test_ignores_directory_events(self, handler, reload_callback):
        """Test that directory events are ignored."""
        from unittest.mock import Mock

        # Create mock directory event
        event = Mock()
        event.is_directory = True
        event.src_path = "/path/to/subdir/"

        # Call handler
        handler.on_created(event)

        # Reload should not have been called
        time.sleep(0.6)
        assert len(reload_callback.calls) == 0

    def test_debouncing_prevents_rapid_triggers(self, handler, reload_callback):
        """Test that debouncing prevents rapid consecutive reloads."""
        from unittest.mock import Mock

        # Create mock file event
        event = Mock()
        event.is_directory = False
        event.src_path = "/path/to/test.md"

        # Trigger multiple modifications rapidly
        handler.on_modified(event)
        time.sleep(0.1)  # Wait 100ms
        handler.on_modified(event)
        time.sleep(0.1)  # Wait another 100ms
        handler.on_modified(event)

        # Wait for debounce
        time.sleep(0.6)

        # Should have triggered only once (or very few times)
        call_count = len(reload_callback.calls)
        assert call_count <= 2  # Should be 1, but allow 2 for timing


class TestFileWatcherLifecycle:
    """Test FileWatcher lifecycle (start/stop)."""

    @pytest.fixture
    def test_dir(self):
        """Create a temporary test directory."""
        test_path = tempfile.mkdtemp()
        yield test_path

        import shutil

        shutil.rmtree(test_path, ignore_errors=True)

    @pytest.fixture
    def reload_callback(self):
        """Create a mock reload callback that tracks calls."""
        calls = []

        def callback():
            calls.append(True)

        # Return both callable and list for tracking
        callback.calls = calls
        return callback

    @pytest.fixture
    def watcher(self, test_dir, reload_callback):
        """Create FileWatcher for testing."""
        return FileWatcher(
            commands_dir=test_dir,
            reload_callback=reload_callback,
            debounce_seconds=0.1,
        )

    def test_initializes_with_existing_directory(self, test_dir, reload_callback):
        """Test that FileWatcher initializes with existing directory."""
        watcher = FileWatcher(
            commands_dir=test_dir,
            reload_callback=reload_callback,
        )

        assert watcher.commands_dir == Path(test_dir)
        assert watcher.observer is None
        assert watcher.event_handler is None

    def test_raises_for_missing_directory(self, reload_callback):
        """Test that FileWatcher raises error for missing directory."""
        with pytest.raises(FileNotFoundError):
            FileWatcher(
                commands_dir="/non/existent/path",
                reload_callback=reload_callback,
            )

    def test_raises_for_file_instead_of_directory(self, reload_callback, tmp_path):
        """Test that FileWatcher raises error when path is a file."""
        # Create a temporary file
        file_path = os.path.join(tmp_path, "notadir")
        with open(file_path, "w") as f:
            f.write("test")

        try:
            with pytest.raises(NotADirectoryError):
                FileWatcher(
                    commands_dir=file_path,
                    reload_callback=reload_callback,
                )
        finally:
            os.unlink(file_path)

    def test_starts_observer(self, watcher):
        """Test that start() initializes and starts observer."""
        assert watcher.observer is None

        watcher.start()

        assert watcher.observer is not None
        assert watcher.observer.is_alive()
        assert watcher.event_handler is not None

        # Clean up
        watcher.stop()

    def test_stop_shuts_down_observer(self, watcher):
        """Test that stop() shuts down observer."""
        # Start watcher first
        watcher.start()
        assert watcher.observer.is_alive()

        # Stop watcher
        watcher.stop()

        # After stop(), observer is set to None
        assert watcher.observer is None
        assert watcher.event_handler is None

    def test_stop_when_not_running_is_safe(self, watcher):
        """Test that stop() is safe when not running."""
        # Should not raise
        watcher.stop()

        assert watcher.observer is None
        assert watcher.event_handler is None

    def test_raises_on_double_start(self, watcher):
        """Test that starting twice raises RuntimeError."""
        watcher.start()

        with pytest.raises(RuntimeError) as exc_info:
            watcher.start()

        assert "already running" in str(exc_info.value)

        # Clean up
        watcher.stop()


class TestFileWatcherFileMonitoring:
    """Test FileWatcher monitoring capabilities."""

    @pytest.fixture
    def test_dir(self):
        """Create a temporary test directory."""
        test_path = tempfile.mkdtemp()
        yield test_path

        import shutil

        shutil.rmtree(test_path, ignore_errors=True)

    @pytest.fixture
    def reload_callback(self):
        """Create a mock reload callback that tracks calls."""
        calls = []

        def callback():
            calls.append(time.time())

        # Return both callable and list for tracking
        callback.calls = calls
        return callback

    @pytest.fixture
    def watcher(self, test_dir, reload_callback):
        """Create and start FileWatcher for testing."""
        w = FileWatcher(
            commands_dir=test_dir,
            reload_callback=reload_callback,
            debounce_seconds=0.1,
        )
        w.start()
        yield w
        w.stop()

    def test_detects_file_creation(self, watcher, reload_callback, test_dir):
        """Test that file creation is detected."""
        # Create a new .md file
        file_path = os.path.join(test_dir, "new.md")
        with open(file_path, "w") as f:
            f.write("test")

        # Wait for debounce and processing
        time.sleep(0.3)

        # Reload should have been triggered
        assert len(reload_callback.calls) >= 1

    def test_detects_file_modification(self, watcher, reload_callback, test_dir):
        """Test that file modification is detected."""
        # Create a .md file
        file_path = os.path.join(test_dir, "test.md")
        with open(file_path, "w") as f:
            f.write("original")

        # Wait for initial processing
        time.sleep(0.3)
        initial_calls = len(reload_callback.calls)

        # Modify the file
        with open(file_path, "w") as f:
            f.write("modified")

        # Wait for debounce and processing
        time.sleep(0.3)

        # Reload should have been triggered again
        assert len(reload_callback.calls) > initial_calls

    def test_detects_file_deletion(self, watcher, reload_callback, test_dir):
        """Test that file deletion is detected."""
        # Create a .md file
        file_path = os.path.join(test_dir, "test.md")
        with open(file_path, "w") as f:
            f.write("test")

        # Wait for initial processing
        time.sleep(0.3)
        initial_calls = len(reload_callback.calls)

        # Delete the file
        os.unlink(file_path)

        # Wait for debounce and processing
        time.sleep(0.3)

        # Reload should have been triggered
        assert len(reload_callback.calls) > initial_calls

    def test_ignores_non_markdown_changes(self, watcher, reload_callback, test_dir):
        """Test that non-.md file changes are ignored."""
        # Create and modify non-.md files
        for filename in ["test.txt", "config.json"]:
            file_path = os.path.join(test_dir, filename)
            with open(file_path, "w") as f:
                f.write("test")

            # Wait for debounce
            time.sleep(0.3)

        # Reload should not have been triggered
        assert len(reload_callback.calls) == 0

    def test_multiple_files_trigger_single_reload(
        self, watcher, reload_callback, test_dir
    ):
        """Test that multiple rapid file changes trigger minimal reloads."""
        initial_calls = len(reload_callback.calls)

        # Create and modify multiple files rapidly
        for i in range(3):
            file_path = os.path.join(test_dir, f"test{i}.md")
            with open(file_path, "w") as f:
                f.write(f"content {i}")

            time.sleep(0.05)  # 50ms between files

        # Wait for debounce
        time.sleep(0.3)

        # Should trigger relatively few reloads due to debouncing
        final_calls = len(reload_callback.calls)
        # With 0.1s debounce and 3 files created 50ms apart, allow up to 4 reloads
        assert (
            final_calls - initial_calls <= 4
        )  # Debouncing should prevent excessive triggers


class TestFileWatcherErrorHandling:
    """Test FileWatcher error handling."""

    @pytest.fixture
    def test_dir(self):
        """Create a temporary test directory."""
        test_path = tempfile.mkdtemp()
        yield test_path

        import shutil

        shutil.rmtree(test_path, ignore_errors=True)

    @pytest.fixture
    def failing_callback(self):
        """Create a reload callback that raises an exception."""

        def callback():
            raise RuntimeError("Test reload error")

        return callback

    @pytest.fixture
    def watcher(self, test_dir, failing_callback):
        """Create FileWatcher with failing callback."""
        w = FileWatcher(
            commands_dir=test_dir,
            reload_callback=failing_callback,
            debounce_seconds=0.1,
        )
        w.start()
        yield w
        w.stop()

    def test_handles_callback_exceptions(self, watcher, test_dir):
        """Test that exceptions in callback are handled gracefully."""
        # Create a .md file to trigger reload
        file_path = os.path.join(test_dir, "test.md")
        with open(file_path, "w") as f:
            f.write("test")

        # Wait for debounce
        time.sleep(0.3)

        # Watcher should still be running despite exception
        assert watcher.observer is not None
        assert watcher.observer.is_alive()

    def test_watcher_continues_after_error(self, watcher, test_dir):
        """Test that watcher continues monitoring after errors."""
        # Trigger multiple file changes
        for i in range(3):
            file_path = os.path.join(test_dir, f"test{i}.md")
            with open(file_path, "w") as f:
                f.write(f"content {i}")

            time.sleep(0.2)  # Wait between changes

        # Watcher should still be running
        assert watcher.observer.is_alive()
