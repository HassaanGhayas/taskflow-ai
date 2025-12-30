"""
Task service module for Todo Console Application.

This module provides business logic for managing tasks, including
storage, validation, and CRUD operations.
"""

from .task_service import (
    TaskNotFoundError,
    create_task,
    delete_task,
    get_task,
    list_tasks,
    next_id,
    tasks,
    toggle_task_status,
    update_task,
)

__all__ = [
    "TaskNotFoundError",
    "create_task",
    "delete_task",
    "get_task",
    "list_tasks",
    "next_id",
    "tasks",
    "toggle_task_status",
    "update_task",
]
