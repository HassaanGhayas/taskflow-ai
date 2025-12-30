"""
Data models for todo application.

This package contains dataclass definitions for core domain entities.
"""

from __future__ import annotations

from .task import Status, Task

__all__ = ["Status", "Task"]
