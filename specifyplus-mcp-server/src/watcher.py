"""File Watcher - Hot reload monitoring for command files.

This module monitors the .claude/commands/ directory for file changes
and triggers automatic reload of commands.

Features:
- Watchdog-based cross-platform file monitoring
- Debouncing to prevent rapid consecutive reloads (SC-007: <5s)
- Event-driven (no polling overhead)
"""

import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from watchdog.events import (
    DirCreatedEvent,
    DirDeletedEvent,
    DirModifiedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver

logger = logging.getLogger(__name__)


class CommandFileHandler(FileSystemEventHandler):
    """Event handler for command file changes.

    Listens for .md file modifications, creations, and deletions
    and triggers reload callback with debouncing.

    Attributes:
        reload_callback: Function to call when command files change.
        debounce_seconds: Minimum time between reload triggers.
    """

    def __init__(
        self,
        reload_callback: Callable[[], None],
        debounce_seconds: float = 1.0,
    ) -> None:
        """Initialize CommandFileHandler.

        Args:
            reload_callback: Function to call when reload is triggered.
            debounce_seconds: Minimum time between consecutive reloads (default: 1s).
        """
        self.reload_callback = reload_callback
        self.debounce_seconds = debounce_seconds

        self._last_reload_time = 0.0
        self._pending_reload = False
        self._timer: threading.Timer | None = None

    def _schedule_reload(self) -> None:
        """Schedule a reload after debounce delay."""
        if self._timer and self._timer.is_alive():
            # Timer already running, update to extend debounce window
            self._timer.cancel()

        def trigger_and_clear() -> None:
            try:
                self.reload_callback()
            except Exception as e:
                logger.error(f"Error in reload callback: {e}")
            self._timer = None
            self._last_reload_time = time.time()

        self._timer = threading.Timer(self.debounce_seconds, trigger_and_clear)
        self._timer.start()
        self._pending_reload = True

    def _trigger_immediate_reload(self) -> None:
        """Trigger immediate reload if debounce window has passed."""
        current_time = time.time()
        time_since_last_reload = current_time - self._last_reload_time

        if time_since_last_reload >= self.debounce_seconds:
            # Debounce window passed, trigger reload immediately
            try:
                self.reload_callback()
            except Exception as e:
                logger.error(f"Error in reload callback: {e}")
            self._last_reload_time = current_time

            # Cancel any pending timer
            if self._timer and self._timer.is_alive():
                self._timer.cancel()
                self._timer = None
            self._pending_reload = False
        else:
            # Within debounce window, schedule reload
            self._schedule_reload()

    def _get_src_path(self, event: Any) -> str:
        """Extract source path from event, handling bytes or str.

        Args:
            event: Watchdog event.

        Returns:
            Source path as string.
        """
        src_path = event.src_path
        if isinstance(src_path, bytes):
            return src_path.decode("utf-8", errors="replace")
        return str(src_path)

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        """Handle file creation events.

        Args:
            event: FileCreatedEvent or DirCreatedEvent from watchdog.
        """
        # Only process .md files
        src_path = self._get_src_path(event)
        if not event.is_directory and src_path.endswith(".md"):
            logger.debug(f"File created: {src_path}")
            self._trigger_immediate_reload()

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
        """Handle file modification events.

        Args:
            event: FileModifiedEvent or DirModifiedEvent from watchdog.
        """
        # Only process .md files
        src_path = self._get_src_path(event)
        if not event.is_directory and src_path.endswith(".md"):
            logger.debug(f"File modified: {src_path}")
            self._trigger_immediate_reload()

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent) -> None:
        """Handle file deletion events.

        Args:
            event: FileDeletedEvent or DirDeletedEvent from watchdog.
        """
        # Only process .md files
        src_path = self._get_src_path(event)
        if not event.is_directory and src_path.endswith(".md"):
            logger.debug(f"File deleted: {src_path}")
            self._trigger_immediate_reload()


class FileWatcher:
    """Monitor commands directory for file changes and trigger hot reload.

    Uses watchdog for cross-platform file system monitoring (Linux/macOS/Windows).
    Implements debouncing to prevent rapid consecutive reloads.

    Attributes:
        commands_dir: Path to .claude/commands/ directory.
        reload_callback: Function to call when commands change.
        debounce_seconds: Minimum time between reload triggers.
    """

    def __init__(
        self,
        commands_dir: str,
        reload_callback: Callable[[], None],
        debounce_seconds: float = 1.0,
    ) -> None:
        """Initialize FileWatcher.

        Args:
            commands_dir: Path to .claude/commands/ directory.
            reload_callback: Function to call when commands change.
            debounce_seconds: Minimum time between consecutive reloads (default: 1s).
                             Target: reload completes within 5s per SC-007.
        """
        self.commands_dir = Path(commands_dir)
        self.reload_callback = reload_callback
        self.debounce_seconds = debounce_seconds

        self.observer: BaseObserver | None = None
        self.event_handler: CommandFileHandler | None = None

        if not self.commands_dir.exists():
            raise FileNotFoundError(f"Commands directory not found: {commands_dir}")

        if not self.commands_dir.is_dir():
            raise NotADirectoryError(
                f"Commands path is not a directory: {commands_dir}"
            )

    def start(self) -> None:
        """Start watching the commands directory.

        Raises:
            RuntimeError: If watcher is already running.
        """
        if self.observer is not None:
            raise RuntimeError("FileWatcher is already running")

        logger.info(f"Starting file watcher on: {self.commands_dir}")

        # Create event handler
        self.event_handler = CommandFileHandler(
            reload_callback=self.reload_callback,
            debounce_seconds=self.debounce_seconds,
        )

        # Create and start observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.commands_dir),
            recursive=False,  # Only watch top-level .md files
        )
        self.observer.start()

        logger.info("File watcher started successfully")

    def stop(self) -> None:
        """Stop watching the commands directory.

        Waits for observer to stop completely.
        """
        if self.observer is None:
            logger.warning("FileWatcher is not running")
            return

        logger.info("Stopping file watcher...")
        self.observer.stop()
        self.observer.join(timeout=5.0)  # Wait up to 5s for shutdown

        if self.observer.is_alive():
            logger.warning("FileWatcher did not stop gracefully, forcing stop")
        else:
            logger.info("File watcher stopped successfully")

        self.observer = None
        self.event_handler = None
