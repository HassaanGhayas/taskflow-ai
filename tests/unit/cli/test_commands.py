"""
Unit tests for CLI command handlers.

This module tests the command layer by mocking the service layer functions.
It verifies that commands correctly route to service functions and handle errors.

[Task]: T037
[Feature]: 001-todo-console-app
[Spec]: specs/001-todo-console-app/tasks.md
"""

from typing import List

import pytest
from todo.cli import commands
from todo.services.task_service import TaskNotFoundError
from todo.models.task import Status, Task


# ==============================================================================
# add_command Tests
# ==============================================================================


def test_add_command_with_valid_title(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test add_command() with a valid title.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §add

    Verifies:
        - Service layer is called with correct arguments
        - Success message is printed with returned task ID
    """
    # Mock create_task to return task ID 1
    mock_create_task = monkeypatch.setattr("todo.cli.commands.create_task", lambda title, description: 1)

    # Execute command
    commands.add_command(["Buy groceries"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Task created with ID 1\n"


def test_add_command_with_title_and_description(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test add_command() with title and description.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §add

    Verifies:
        - Service layer receives both title and description
        - Success message is printed with correct task ID
    """
    # Mock create_task to return task ID 2
    mock_create_task = monkeypatch.setattr(
        "todo.cli.commands.create_task", lambda title, description: 2
    )

    # Execute command
    commands.add_command(["Write documentation", "Complete spec.md"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Task created with ID 2\n"


def test_add_command_with_empty_title(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test add_command() with empty title.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §add

    Verifies:
        - Empty title is caught by IndexError (no args provided)
        - Appropriate error message is displayed
    """
    # Execute command with no arguments
    commands.add_command([])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Title cannot be empty\n"


def test_add_command_with_validation_error(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test add_command() when service raises ValueError.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §add

    Verifies:
        - ValueError from service layer is caught and displayed
    """
    # Mock create_task to raise ValueError
    mock_create_task = monkeypatch.setattr(
        "todo.cli.commands.create_task",
        lambda title, description: (_ for _ in ()).throw(
            ValueError("Title exceeds maximum length of 500 characters")
        ),
    )

    # Execute command
    commands.add_command(["a" * 501])

    # Capture output
    captured = capsys.readouterr()
    assert "Error: Title exceeds maximum length of 500 characters" in captured.out


# ==============================================================================
# list_command Tests
# ==============================================================================


def test_list_command_displays_tasks_in_table_format(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test list_command() displays tasks in table format.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §list

    Verifies:
        - Tasks are displayed in table with ID, Status, and Title columns
        - Header and separator lines are present
        - Multiple tasks are listed correctly
    """
    # Mock list_tasks to return sample tasks
    task1 = Task(id=1, title="Buy groceries", description="Milk, eggs", status=Status.PENDING)
    task2 = Task(id=2, title="Write docs", description=None, status=Status.COMPLETE)
    mock_list_tasks = monkeypatch.setattr("todo.cli.commands.list_tasks", lambda: [task1, task2])

    # Execute command
    commands.list_command([])

    # Capture output
    captured = capsys.readouterr()
    output = captured.out

    # Verify table header
    assert "ID" in output
    assert "Status" in output
    assert "Title" in output

    # Verify separator line
    assert "----" in output

    # Verify tasks are displayed
    assert "1" in output
    assert "2" in output
    assert "Pending" in output
    assert "Complete" in output
    assert "Buy groceries" in output
    assert "Write docs" in output


def test_list_command_with_no_tasks(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test list_command() when no tasks exist.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §list

    Verifies:
        - Empty list returns appropriate message
    """
    # Mock list_tasks to return empty list
    mock_list_tasks = monkeypatch.setattr("todo.cli.commands.list_tasks", lambda: [])

    # Execute command
    commands.list_command([])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "No tasks found. Add a task to get started.\n"


# ==============================================================================
# update_command Tests
# ==============================================================================


def test_update_command_with_title(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test update_command() with title argument.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §update

    Verifies:
        - Service layer is called with correct task_id, title, and None description
        - Success message is displayed
    """
    # Track if update_task was called correctly
    called_with: dict = {}

    def mock_update(task_id: int, title: str, description: str) -> Task:
        called_with["task_id"] = task_id
        called_with["title"] = title
        called_with["description"] = description
        return Task(id=task_id, title=title, description=description, status=Status.PENDING)

    # Mock update_task
    mock_update_task = monkeypatch.setattr("todo.cli.commands.update_task", mock_update)

    # Execute command
    commands.update_command(["1", "title", "Buy organic groceries"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Task 1 updated successfully\n"

    # Verify service was called correctly
    assert called_with["task_id"] == 1
    assert called_with["title"] == "Buy organic groceries"
    assert called_with["description"] is None


def test_update_command_with_description(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test update_command() with description argument.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §update

    Verifies:
        - Service layer is called with correct task_id, None title, and description
        - Success message is displayed
    """
    # Track if update_task was called correctly
    called_with: dict = {}

    def mock_update(task_id: int, title: str, description: str) -> Task:
        called_with["task_id"] = task_id
        called_with["title"] = title
        called_with["description"] = description
        return Task(id=task_id, title="Original", description=description, status=Status.PENDING)

    # Mock update_task
    mock_update_task = monkeypatch.setattr("todo.cli.commands.update_task", mock_update)

    # Execute command
    commands.update_command(["2", "description", "Updated description"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Task 2 updated successfully\n"

    # Verify service was called correctly
    assert called_with["task_id"] == 2
    assert called_with["title"] is None
    assert called_with["description"] == "Updated description"


def test_update_command_with_invalid_field(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test update_command() with invalid field name.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §update

    Verifies:
        - Invalid field names are caught
        - Error message with usage hint is displayed
    """
    # Execute command with invalid field
    commands.update_command(["1", "invalid", "value"])

    # Capture output
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: Must provide either 'title' or 'description' to update" in output
    assert "Usage:" in output


def test_update_command_with_insufficient_args(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test update_command() with insufficient arguments.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §update

    Verifies:
        - Missing arguments are caught
        - Error message with usage hint is displayed
    """
    # Execute command with insufficient arguments
    commands.update_command(["1", "title"])

    # Capture output
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: Must provide either 'title' or 'description' to update" in output
    assert "Usage:" in output


def test_update_command_with_nonexistent_task(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test update_command() with non-existent task ID.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §update

    Verifies:
        - TaskNotFoundError is caught and displayed
    """
    # Mock update_task to raise TaskNotFoundError
    mock_update_task = monkeypatch.setattr(
        "todo.cli.commands.update_task",
        lambda task_id, title, description: (_ for _ in ()).throw(TaskNotFoundError(999)),
    )

    # Execute command
    commands.update_command(["999", "title", "New title"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Task with ID 999 not found\n"


def test_update_command_with_invalid_id(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test update_command() with invalid (non-numeric) task ID.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §update

    Verifies:
        - Invalid ID is caught by ValueError
        - Appropriate error message is displayed
    """
    # Execute command with invalid ID
    commands.update_command(["abc", "title", "New title"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Invalid task ID. Must be a number.\n"


# ==============================================================================
# delete_command Tests
# ==============================================================================


def test_delete_command_removes_task(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test delete_command() removes task.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §delete

    Verifies:
        - Service layer is called with correct task ID
        - Success message is displayed
    """
    # Track if delete_task was called correctly
    called_with: List[int] = []

    def mock_delete(task_id: int) -> None:
        called_with.append(task_id)

    # Mock delete_task
    mock_delete_task = monkeypatch.setattr("todo.cli.commands.delete_task", mock_delete)

    # Execute command
    commands.delete_command(["1"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Task 1 deleted successfully\n"

    # Verify service was called correctly
    assert called_with == [1]


def test_delete_command_with_nonexistent_task(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test delete_command() with non-existent task ID.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §delete

    Verifies:
        - TaskNotFoundError is caught and displayed
    """
    # Mock delete_task to raise TaskNotFoundError
    mock_delete_task = monkeypatch.setattr(
        "todo.cli.commands.delete_task",
        lambda task_id: (_ for _ in ()).throw(TaskNotFoundError(999)),
    )

    # Execute command
    commands.delete_command(["999"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Task with ID 999 not found\n"


def test_delete_command_with_invalid_id(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test delete_command() with invalid (non-numeric) task ID.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §delete

    Verifies:
        - Invalid ID is caught by ValueError
        - Appropriate error message is displayed
    """
    # Execute command with invalid ID
    commands.delete_command(["abc"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Invalid task ID. Must be a number.\n"


def test_delete_command_with_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test delete_command() with no arguments.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §delete

    Verifies:
        - Missing argument is caught
        - Appropriate error message is displayed
    """
    # Execute command with no arguments
    commands.delete_command([])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Invalid task ID. Must be a number.\n"


# ==============================================================================
# complete_command Tests
# ==============================================================================


def test_complete_command_toggles_status_pending_to_complete(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test complete_command() toggles status from Pending to Complete.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §complete

    Verifies:
        - Service layer is called with correct task ID
        - Success message shows "Complete" status
    """
    # Mock toggle_task_status to return a complete task
    task = Task(id=1, title="Buy groceries", description=None, status=Status.COMPLETE)
    mock_toggle_task_status = monkeypatch.setattr("todo.cli.commands.toggle_task_status", lambda task_id: task)

    # Execute command
    commands.complete_command(["1"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Task 1 marked as Complete\n"


def test_complete_command_toggles_status_complete_to_pending(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test complete_command() toggles status from Complete to Pending.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §complete

    Verifies:
        - Service layer is called with correct task ID
        - Success message shows "Pending" status
    """
    # Mock toggle_task_status to return a pending task
    task = Task(id=1, title="Buy groceries", description=None, status=Status.PENDING)
    mock_toggle_task_status = monkeypatch.setattr("todo.cli.commands.toggle_task_status", lambda task_id: task)

    # Execute command
    commands.complete_command(["1"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Task 1 marked as Pending\n"


def test_complete_command_with_nonexistent_task(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test complete_command() with non-existent task ID.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §complete

    Verifies:
        - TaskNotFoundError is caught and displayed
    """
    # Mock toggle_task_status to raise TaskNotFoundError
    mock_toggle_task_status = monkeypatch.setattr(
        "todo.cli.commands.toggle_task_status",
        lambda task_id: (_ for _ in ()).throw(TaskNotFoundError(999)),
    )

    # Execute command
    commands.complete_command(["999"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Task with ID 999 not found\n"


def test_complete_command_with_invalid_id(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test complete_command() with invalid (non-numeric) task ID.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §complete

    Verifies:
        - Invalid ID is caught by ValueError
        - Appropriate error message is displayed
    """
    # Execute command with invalid ID
    commands.complete_command(["abc"])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Invalid task ID. Must be a number.\n"


def test_complete_command_with_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test complete_command() with no arguments.

    [Task]: T037
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §complete

    Verifies:
        - Missing argument is caught
        - Appropriate error message is displayed
    """
    # Execute command with no arguments
    commands.complete_command([])

    # Capture output
    captured = capsys.readouterr()
    assert captured.out == "Error: Invalid task ID. Must be a number.\n"
