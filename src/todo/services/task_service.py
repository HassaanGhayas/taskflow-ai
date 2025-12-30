"""
Task service module for the Todo Console Application.

This module provides in-memory storage, custom exceptions, and validation
for task management operations.

[Task]: T007, T008, T009
[From]: specs/001-todo-console-app/research.md, specs/001-todo-console-app/data-model.md
"""

from typing import Optional


# ==============================================================================
# Storage Strategy (Task T007)
# ==============================================================================

tasks: dict[int, "Task"] = {}
"""
In-memory storage for all tasks.

Uses a dictionary with integer keys (task IDs) mapping to Task objects.
Provides O(1) lookup, insert, update, and delete operations.

Note:
    Data is lost when the application exits. This is intentional per
    Phase 1 scope specification. Persistence is planned for Phase 2.

[Task]: T007
[From]: specs/001-todo-console-app/research.md (Storage Decision)
"""

next_id: int = 1
"""
Monotonically increasing counter for generating unique task IDs.

Counter starts at 1 and increments after each task creation.
IDs are never reused after task deletion, ensuring that users cannot
confuse new tasks with previously deleted ones.

[Task]: T007
[From]: specs/001-todo-console-app/research.md (Task ID Generation Strategy)
"""


# ==============================================================================
# Custom Exception (Task T008)
# ==============================================================================

class TaskNotFoundError(Exception):
    """
    Exception raised when a task with the specified ID does not exist.

    This exception is used throughout the application to provide clear,
    user-friendly error messages when attempting to access a non-existent task.

    Args:
        task_id: The ID of the task that was not found

    Example:
        >>> raise TaskNotFoundError(5)
        TaskNotFoundError: Task with ID 5 not found

    [Task]: T008
    [From]: specs/001-todo-console-app/data-model.md, specs/001-todo-console-app/contracts/cli-commands.md
    """
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


# ==============================================================================
# Input Validation (Task T009)
# ==============================================================================

def validate_title(title: str) -> None:
    """
    Validate a task title.

    Ensures the title meets all business rules:
    - Non-empty (after stripping whitespace)
    - Maximum 500 characters

    Args:
        title: The title to validate

    Raises:
        ValueError: If title is empty or exceeds 500 characters

    Example:
        >>> validate_title("Buy groceries")  # Valid, no exception
        >>> validate_title("")  # Raises ValueError
        ValueError: Title cannot be empty
        >>> validate_title("a" * 501)  # Raises ValueError
        ValueError: Title exceeds maximum length of 500 characters

    [Task]: T009
    [From]: specs/001-todo-console-app/data-model.md (Validation Rules),
            specs/001-todo-console-app/contracts/cli-commands.md (Error Conditions)
    """
    if not title or title.strip() == "":
        raise ValueError("Title cannot be empty")
    if len(title) > 500:
        raise ValueError("Title exceeds maximum length of 500 characters")


def validate_description(description: Optional[str]) -> None:
    """
    Validate a task description.

    Ensures the description (if provided) does not exceed 500 characters.
    Empty strings and None values are considered valid (description is optional).

    Args:
        description: The description to validate (may be None)

    Raises:
        ValueError: If description exceeds 500 characters

    Example:
        >>> validate_description(None)  # Valid, no exception
        >>> validate_description("")  # Valid, no exception
        >>> validate_description("Details")  # Valid, no exception
        >>> validate_description("a" * 501)  # Raises ValueError
        ValueError: Description exceeds maximum length of 500 characters

    [Task]: T009
    [From]: specs/001-todo-console-app/data-model.md (Validation Rules),
            specs/001-todo-console-app/contracts/cli-commands.md (Error Conditions)
    """
    if description is not None and len(description) > 500:
        raise ValueError("Description exceeds maximum length of 500 characters")


# ==============================================================================
# Service CRUD Functions (Tasks T010-T015)
# ==============================================================================


def create_task(title: str, description: Optional[str] = None) -> int:
    """
    Create a new task with the given title and optional description.

    Performs validation, generates a unique ID, initializes the status to PENDING,
    and stores the task in memory.

    Args:
        title: The task title (required, non-empty, max 500 characters)
        description: Optional task description (max 500 characters if provided)

    Returns:
        int: The unique ID assigned to the newly created task

    Raises:
        ValueError: If title is empty or exceeds 500 characters,
                    or if description exceeds 500 characters

    Example:
        >>> task_id = create_task("Buy groceries", "Milk, eggs, bread")
        >>> print(task_id)
        1
        >>> task_id = create_task("Call dentist")
        >>> print(task_id)
        2

    [Task]: T010
    [From]: specs/001-todo-console-app/tasks.md,
            specs/001-todo-console-app/spec.md (FR-001, FR-002, FR-003, FR-004)
    """
    # Validate input parameters
    validate_title(title)
    validate_description(description)

    # Import Task and Status here to avoid circular import
    from todo.models.task import Status, Task

    # Generate unique ID and create task
    global next_id
    task_id = next_id
    task = Task(
        id=task_id,
        title=title,
        description=description,
        status=Status.PENDING,
    )

    # Store task and increment counter
    tasks[task_id] = task
    next_id += 1

    return task_id


def get_task(task_id: int) -> "Task":
    """
    Retrieve a task by its ID.

    Args:
        task_id: The unique identifier of the task to retrieve

    Returns:
        Task: The task object with the specified ID

    Raises:
        TaskNotFoundError: If no task exists with the given ID

    Example:
        >>> task_id = create_task("Buy groceries")
        >>> task = get_task(task_id)
        >>> print(task.title)
        Buy groceries
        >>> print(task.status)
        Status.PENDING

    [Task]: T011
    [From]: specs/001-todo-console-app/tasks.md,
            specs/001-todo-console-app/data-model.md (Storage Schema)
    """
    # Import Task here to avoid circular import
    from todo.models.task import Task

    task = tasks.get(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return task


def list_tasks() -> list["Task"]:
    """
    Retrieve all tasks from storage.

    Args:
        None

    Returns:
        List[Task]: A list containing all tasks. Returns an empty list if no tasks exist.

    Example:
        >>> create_task("Buy groceries")
        >>> create_task("Call dentist")
        >>> all_tasks = list_tasks()
        >>> len(all_tasks)
        2

    [Task]: T012
    [From]: specs/001-todo-console-app/tasks.md,
            specs/001-todo-console-app/data-model.md (Storage Schema)
    """
    return list(tasks.values())


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> "Task":
    """
    Update an existing task's title and/or description.

    At least one of title or description must be provided. The task ID
    and status cannot be modified.

    Args:
        task_id: The unique identifier of the task to update
        title: New title for the task (optional, must be valid if provided)
        description: New description for the task (optional, must be valid if provided)

    Returns:
        Task: The updated task object

    Raises:
        TaskNotFoundError: If no task exists with the given ID
        ValueError: If neither title nor description is provided,
                    or if provided values are invalid

    Example:
        >>> task_id = create_task("Buy groceries", "Milk, eggs")
        >>> updated = update_task(task_id, title="Buy weekly groceries")
        >>> print(updated.title)
        Buy weekly groceries

    [Task]: T013
    [From]: specs/001-todo-console-app/tasks.md,
            specs/001-todo-console-app/data-model.md (Immutable Updates)
    """
    # Import Task here to avoid circular import
    import dataclasses
    from todo.models.task import Task

    # Verify task exists
    existing_task = get_task(task_id)

    # Validate at least one field is being updated
    if title is None and description is None:
        raise ValueError("At least one of title or description must be provided")

    # Validate title if provided
    if title is not None:
        validate_title(title)

    # Validate description if provided
    if description is not None:
        validate_description(description)

    # Create new frozen Task instance with updated fields
    updated_task = dataclasses.replace(
        existing_task,
        title=title if title is not None else existing_task.title,
        description=description if description is not None else existing_task.description,
    )

    # Update in storage
    tasks[task_id] = updated_task

    return updated_task


def delete_task(task_id: int) -> None:
    """
    Delete a task from storage.

    The task ID is not reused after deletion. The next_id counter
    continues to increment monotonically.

    Args:
        task_id: The unique identifier of the task to delete

    Returns:
        None

    Raises:
        TaskNotFoundError: If no task exists with the given ID

    Example:
        >>> task_id = create_task("Buy groceries")
        >>> delete_task(task_id)
        >>> get_task(task_id)
        TaskNotFoundError: Task with ID 1 not found

    [Task]: T014
    [From]: specs/001-todo-console-app/tasks.md,
            specs/001-todo-console-app/data-model.md (Storage Schema),
            specs/001-todo-console-app/spec.md (Task ID Management)
    """
    # Verify task exists (will raise TaskNotFoundError if not)
    get_task(task_id)

    # Delete from storage
    del tasks[task_id]


def toggle_task_status(task_id: int) -> "Task":
    """
    Toggle a task's status between PENDING and COMPLETE.

    Toggles the status of the specified task:
    - PENDING -> COMPLETE
    - COMPLETE -> PENDING

    Args:
        task_id: The unique identifier of the task to toggle

    Returns:
        Task: The updated task object with toggled status

    Raises:
        TaskNotFoundError: If no task exists with the given ID

    Example:
        >>> task_id = create_task("Buy groceries")
        >>> task = toggle_task_status(task_id)
        >>> print(task.status)
        Status.COMPLETE
        >>> task = toggle_task_status(task_id)
        >>> print(task.status)
        Status.PENDING

    [Task]: T015
    [From]: specs/001-todo-console-app/tasks.md,
            specs/001-todo-console-app/data-model.md (State Transitions),
            specs/001-todo-console-app/spec.md (FR-007)
    """
    # Import Task, Status here to avoid circular import
    import dataclasses
    from todo.models.task import Status, Task

    # Get existing task
    existing_task = get_task(task_id)

    # Determine new status (toggle)
    new_status = (
        Status.COMPLETE
        if existing_task.status == Status.PENDING
        else Status.PENDING
    )

    # Create new frozen Task instance with updated status
    updated_task = dataclasses.replace(existing_task, status=new_status)

    # Update in storage
    tasks[task_id] = updated_task

    return updated_task
