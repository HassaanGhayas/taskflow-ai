"""
Integration tests for CLI workflow end-to-end.

This module tests complete user journeys by integrating CLI commands
with the real service layer. It verifies state persistence across commands
and error handling.

Note: For Phase 1 (in-memory storage), these tests run within a single
process to verify state persistence. Subprocess-based tests would not
share memory state, so they are not appropriate for Phase 1.

[Task]: T038
[Feature]: 001-todo-console-app
[Spec]: specs/001-todo-console-app/tasks.md
"""

import pytest
from todo.cli import commands
from todo.services.task_service import tasks


def reset_task_storage() -> None:
    """
    Reset in-memory task storage to empty state.

    Helper function to ensure clean state between tests.
    """
    tasks.clear()
    # Reset next_id by importing and modifying the module-level variable
    import todo.services.task_service

    todo.services.task_service.next_id = 1


# ==============================================================================
# Helper Functions for Testing CLI Commands
# ==============================================================================


def run_command_and_capture(command: str, args: list[str], capsys: pytest.CaptureFixture[str]) -> str:
    """
    Run a CLI command and capture its output.

    Args:
        command: Command name (e.g., "add", "list")
        args: List of command arguments
        capsys: Pytest capsys fixture

    Returns:
        str: Captured stdout output
    """
    from todo.cli.main import execute_command

    execute_command(command, args)
    captured = capsys.readouterr()
    return captured.out


# ==============================================================================
# Complete User Journey Integration Test
# ==============================================================================


def test_complete_user_journey_add_list_complete_list_delete_list(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test complete user journey: add task -> list -> complete -> list -> delete -> list.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/tasks.md §Integration Tests

    Journey:
        1. Create a new task
        2. List tasks to verify it exists
        3. Mark task as complete
        4. List tasks to verify status change
        5. Delete the task
        6. List tasks to verify removal

    Verifies:
        - State persists across commands
        - Each operation produces correct output
        - Task lifecycle works end-to-end
    """
    # Reset storage
    reset_task_storage()

    # Step 1: Add a task
    commands.add_command(["Buy groceries"])
    captured = capsys.readouterr()
    assert "Task created with ID 1" in captured.out

    # Step 2: List tasks
    commands.list_command([])
    captured = capsys.readouterr()
    output = captured.out
    assert "1" in output
    assert "Pending" in output
    assert "Buy groceries" in output

    # Step 3: Complete the task
    commands.complete_command(["1"])
    captured = capsys.readouterr()
    assert "Task 1 marked as Complete" in captured.out

    # Step 4: List tasks to verify status change
    commands.list_command([])
    captured = capsys.readouterr()
    output = captured.out
    assert "1" in output
    assert "Complete" in output
    assert "Buy groceries" in output

    # Step 5: Delete the task
    commands.delete_command(["1"])
    captured = capsys.readouterr()
    assert "Task 1 deleted successfully" in captured.out

    # Step 6: List tasks to verify removal
    commands.list_command([])
    captured = capsys.readouterr()
    assert "No tasks found" in captured.out


def test_complete_user_journey_with_multiple_tasks(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test complete user journey with multiple tasks.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/tasks.md §Integration Tests

    Journey:
        1. Create three tasks
        2. List all tasks
        3. Complete the second task
        4. Update the first task's title
        5. Delete the third task
        6. List tasks to verify final state

    Verifies:
        - Multiple tasks can coexist
        - IDs are unique and sequential
        - Operations affect only intended tasks
    """
    # Reset storage
    reset_task_storage()

    # Step 1: Create three tasks
    commands.add_command(["Task 1"])
    captured = capsys.readouterr()
    assert "Task created with ID 1" in captured.out

    commands.add_command(["Task 2", "Second task"])
    captured = capsys.readouterr()
    assert "Task created with ID 2" in captured.out

    commands.add_command(["Task 3"])
    captured = capsys.readouterr()
    assert "Task created with ID 3" in captured.out

    # Step 2: List all tasks
    commands.list_command([])
    captured = capsys.readouterr()
    output = captured.out
    assert "1" in output
    assert "2" in output
    assert "3" in output
    assert "Task 1" in output
    assert "Task 2" in output
    assert "Task 3" in output
    assert output.count("Pending") == 3

    # Step 3: Complete the second task
    commands.complete_command(["2"])
    captured = capsys.readouterr()
    assert "Task 2 marked as Complete" in captured.out

    # Step 4: Update the first task's title
    commands.update_command(["1", "title", "Updated Task 1"])
    captured = capsys.readouterr()
    assert "Task 1 updated successfully" in captured.out

    # Step 5: Delete the third task
    commands.delete_command(["3"])
    captured = capsys.readouterr()
    assert "Task 3 deleted successfully" in captured.out

    # Step 6: List tasks to verify final state
    commands.list_command([])
    captured = capsys.readouterr()
    output = captured.out
    # Task 1 should be present with updated title
    assert "1" in output
    assert "Updated Task 1" in output
    assert "Pending" in output
    # Task 2 should be present with Complete status
    assert "2" in output
    assert "Task 2" in output
    assert "Complete" in output
    # Task 3 should be absent
    assert "Task 3" not in output
    assert "3" not in output or "Task 3" not in output  # Allow 3 to appear in ID column


# ==============================================================================
# One-Shot Mode Tests (In-Process for Phase 1 In-Memory Storage)
# ==============================================================================


def test_one_shot_mode_add_command(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test one-shot mode: add command.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §One-Shot Command

    Verifies:
        - Command executes correctly
        - Output matches expected format
    """
    reset_task_storage()
    output = run_command_and_capture("add", ["Test Task"], capsys)
    assert "Task created with ID 1" in output


def test_one_shot_mode_add_with_description(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test one-shot mode: add command with description.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §One-Shot Command

    Verifies:
        - Command with description executes correctly
    """
    reset_task_storage()
    output = run_command_and_capture("add", ["Test Task", "Test Description"], capsys)
    assert "Task created with ID 1" in output


def test_one_shot_mode_list_command(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test one-shot mode: list command.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §One-Shot Command

    Verifies:
        - List command executes and displays tasks
    """
    reset_task_storage()
    # Add a task first
    run_command_and_capture("add", ["List Test Task"], capsys)
    # Then list tasks
    output = run_command_and_capture("list", [], capsys)
    assert "List Test Task" in output


def test_one_shot_mode_complete_command(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test one-shot mode: complete command.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §One-Shot Command

    Verifies:
        - Complete command executes and updates status
    """
    reset_task_storage()
    # Add a task first
    run_command_and_capture("add", ["Complete Test Task"], capsys)
    # Then complete it
    output = run_command_and_capture("complete", ["1"], capsys)
    assert "Task 1 marked as Complete" in output


def test_one_shot_mode_update_command(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test one-shot mode: update command.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §One-Shot Command

    Verifies:
        - Update command executes and modifies task
    """
    reset_task_storage()
    # Add a task first
    run_command_and_capture("add", ["Update Test Task"], capsys)
    # Then update it
    output = run_command_and_capture("update", ["1", "title", "Updated Title"], capsys)
    assert "Task 1 updated successfully" in output


def test_one_shot_mode_delete_command(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test one-shot mode: delete command.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §One-Shot Command

    Verifies:
        - Delete command executes and removes task
    """
    reset_task_storage()
    # Add a task first
    run_command_and_capture("add", ["Delete Test Task"], capsys)
    # Then delete it
    output = run_command_and_capture("delete", ["1"], capsys)
    assert "Task 1 deleted successfully" in output


# ==============================================================================
# Interactive Mode Commands End-to-End Tests
# ==============================================================================


def test_interactive_mode_commands_work_end_to_end(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test interactive mode commands work end-to-end.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §Interactive Loop

    Verifies:
        - All commands can be executed via interactive mode routing
        - State persists across multiple command executions
    """
    # Reset storage
    reset_task_storage()

    # Test add command
    from todo.cli.main import execute_command

    execute_command("add", ["Interactive Test"])
    captured = capsys.readouterr()
    assert "Task created with ID 1" in captured.out

    # Test list command
    execute_command("list", [])
    captured = capsys.readouterr()
    output = captured.out
    assert "1" in output
    assert "Interactive Test" in output

    # Test update command
    execute_command("update", ["1", "title", "Updated Interactive"])
    captured = capsys.readouterr()
    assert "Task 1 updated successfully" in captured.out

    # Test complete command
    execute_command("complete", ["1"])
    captured = capsys.readouterr()
    assert "Task 1 marked as Complete" in captured.out

    # Test delete command
    execute_command("delete", ["1"])
    captured = capsys.readouterr()
    assert "Task 1 deleted successfully" in captured.out


# ==============================================================================
# Error Messages Display Tests
# ==============================================================================


def test_error_messages_display_correctly(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Test error messages display correctly for various error scenarios.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §Error Conditions

    Verifies:
        - Empty title error is displayed
        - Non-existent task error is displayed
        - Invalid ID error is displayed
    """
    # Reset storage
    reset_task_storage()

    # Test empty title error
    commands.add_command([""])
    captured = capsys.readouterr()
    assert "Error: Title cannot be empty" in captured.out

    # Test non-existent task error
    commands.delete_command(["999"])
    captured = capsys.readouterr()
    assert "Error: Task with ID 999 not found" in captured.out

    # Test invalid ID error
    commands.delete_command(["abc"])
    captured = capsys.readouterr()
    assert "Error: Invalid task ID. Must be a number." in captured.out

    # Test unknown command error
    from todo.cli.main import execute_command

    execute_command("unknown", ["args"])
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: Unknown command 'unknown'" in output
    assert "Type 'help' for available commands" in output


# ==============================================================================
# State Persistence Tests
# ==============================================================================


def test_state_persistence_across_commands(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Verify state persists correctly across multiple commands.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/tasks.md §Integration Tests

    Verifies:
        - Tasks created remain available for later commands
        - Task IDs remain consistent across operations
        - Status changes persist across command executions
    """
    # Reset storage
    reset_task_storage()

    # Create initial task
    commands.add_command(["Persistent Task", "Initial description"])
    captured = capsys.readouterr()
    assert "Task created with ID 1" in captured.out

    # Verify task exists
    commands.list_command([])
    captured = capsys.readouterr()
    assert "Persistent Task" in captured.out

    # Update task
    commands.update_command(["1", "description", "Updated description"])
    captured = capsys.readouterr()
    assert "Task 1 updated successfully" in captured.out

    # Verify update persisted
    from todo.services.task_service import get_task

    task = get_task(1)
    assert task.description == "Updated description"

    # Complete task
    commands.complete_command(["1"])
    captured = capsys.readouterr()
    assert "Task 1 marked as Complete" in captured.out

    # Verify status persisted
    task = get_task(1)
    assert task.status.value == "Complete"


def test_task_ids_not_reused_after_deletion(capsys: pytest.CaptureFixture[str]) -> None:
    """
    Verify that task IDs are not reused after deletion.

    [Task]: T038
    [Spec]: specs/001-todo-console-app/tasks.md §Integration Tests

    Verifies:
        - Deleted task IDs are not reassigned
        - next_id counter continues to increment
    """
    # Reset storage
    reset_task_storage()

    # Create three tasks
    commands.add_command(["Task 1"])
    commands.add_command(["Task 2"])
    commands.add_command(["Task 3"])

    # Delete task 2
    commands.delete_command(["2"])
    capsys.readouterr()

    # Add a new task - should get ID 4, not 2
    commands.add_command(["Task 4"])
    captured = capsys.readouterr()
    assert "Task created with ID 4" in captured.out

    # List tasks - should show IDs 1, 3, 4 (not 2)
    commands.list_command([])
    captured = capsys.readouterr()
    output = captured.out
    assert "1" in output
    assert "3" in output
    assert "4" in output
    # Task 2 should not appear in the list (ID might appear for Task 4 but not with "Task 2")
    lines = output.split("\n")
    task_2_present = any("Task 2" in line for line in lines)
    assert not task_2_present
