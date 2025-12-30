"""
Unit tests for task_service module.

This module contains comprehensive tests for all CRUD operations in the
task_service module, following test-first TDD approach.

Tests:
    - T031: Test create_task() with various inputs
    - T032: Test get_task() retrieval behavior
    - T033: Test list_tasks() listing behavior
    - T034: Test update_task() update operations
    - T035: Test delete_task() deletion behavior
    - T036: Test toggle_task_status() status toggling

[Task]: T031, T032, T033, T034, T035, T036
[From]: specs/001-todo-console-app/tasks.md
"""

import pytest
from typing import Any

from todo.models.task import Status, Task
from todo.services.task_service import (
    TaskNotFoundError,
    create_task,
    delete_task,
    get_task,
    list_tasks,
    toggle_task_status,
    update_task,
    validate_description,
    validate_title,
)


# ==============================================================================
# Pytest Fixtures (Mock Global Storage)
# ==============================================================================


@pytest.fixture(autouse=True)
def reset_global_storage() -> Any:
    """
    Reset global storage between tests to ensure test isolation.

    This fixture automatically runs before each test to clear the in-memory
    task storage and reset the next_id counter to 1, ensuring that each
    test starts with a clean slate.

    Yields:
        None: Control is yielded to the test, then cleanup runs after

    [From]: specs/001-todo-console-app/tasks.md (Test isolation requirement)
    """
    # Import the global storage variables
    from todo.services import task_service as task_service_module

    # Save original values
    original_tasks = task_service_module.tasks.copy()
    original_next_id = task_service_module.next_id

    # Reset to initial state
    task_service_module.tasks.clear()
    task_service_module.next_id = 1

    # Yield control to the test
    yield

    # Restore original values (though this is typically not needed)
    task_service_module.tasks.clear()
    for task_id, task in original_tasks.items():
        task_service_module.tasks[task_id] = task
    task_service_module.next_id = original_next_id


# ==============================================================================
# Test Suite T031: create_task()
# ==============================================================================


class TestCreateTask:
    """
    Test suite for create_task() function.

    Tests task creation with various valid and invalid inputs, ID generation,
    and return values.

    [Task]: T031
    """

    def test_create_task_with_title_only(self) -> None:
        """
        Test creating a task with only a title (no description).

        Verifies that a task can be created successfully with just a title,
        and that the description defaults to None.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act
        task_id = create_task("Buy groceries")

        # Assert
        assert task_id == 1
        task = get_task(task_id)
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == Status.PENDING

    def test_create_task_with_title_and_description(self) -> None:
        """
        Test creating a task with both title and description.

        Verifies that both title and description are stored correctly.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act
        task_id = create_task("Call dentist", "Schedule annual checkup")

        # Assert
        assert task_id == 1
        task = get_task(task_id)
        assert task.title == "Call dentist"
        assert task.description == "Schedule annual checkup"
        assert task.status == Status.PENDING

    def test_create_task_empty_title_raises_value_error(self) -> None:
        """
        Test that creating a task with an empty title raises ValueError.

        Tests validation for empty string title.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            create_task("")

    def test_create_task_whitespace_title_raises_value_error(self) -> None:
        """
        Test that creating a task with whitespace-only title raises ValueError.

        Tests validation for titles that are only whitespace.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            create_task("   ")

    def test_create_task_title_exceeds_500_chars_raises_value_error(self) -> None:
        """
        Test that creating a task with title > 500 characters raises ValueError.

        Tests validation for maximum title length.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        long_title = "a" * 501

        # Act & Assert
        with pytest.raises(ValueError, match="Title exceeds maximum length of 500 characters"):
            create_task(long_title)

    def test_create_task_exactly_500_chars_succeeds(self) -> None:
        """
        Test that creating a task with exactly 500 character title succeeds.

        Tests boundary condition for maximum valid title length.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        title_500 = "a" * 500

        # Act
        task_id = create_task(title_500)

        # Assert
        assert task_id == 1
        task = get_task(task_id)
        assert task.title == title_500

    def test_create_task_unique_id_generation_monotonic(self) -> None:
        """
        Test that IDs are generated uniquely and monotonically starting at 1.

        Verifies that each new task gets an incrementing ID and IDs are
        never repeated.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act
        id1 = create_task("Task 1")
        id2 = create_task("Task 2")
        id3 = create_task("Task 3")

        # Assert
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3
        assert id1 < id2 < id3

    def test_create_task_returns_correct_task_id(self) -> None:
        """
        Test that create_task returns the correct task_id.

        Verifies the return value matches the ID of the created task.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act
        task_id = create_task("Test task")

        # Assert
        task = get_task(task_id)
        assert task.id == task_id

    def test_create_task_description_exceeds_500_chars_raises_value_error(self) -> None:
        """
        Test that creating a task with description > 500 characters raises ValueError.

        Tests validation for maximum description length.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        long_description = "a" * 501

        # Act & Assert
        with pytest.raises(ValueError, match="Description exceeds maximum length of 500 characters"):
            create_task("Valid title", long_description)

    def test_create_task_exactly_500_char_description_succeeds(self) -> None:
        """
        Test that creating a task with exactly 500 character description succeeds.

        Tests boundary condition for maximum valid description length.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        description_500 = "a" * 500

        # Act
        task_id = create_task("Valid title", description_500)

        # Assert
        task = get_task(task_id)
        assert task.description == description_500

    def test_create_task_status_initializes_to_pending(self) -> None:
        """
        Test that newly created tasks have PENDING status by default.

        Verifies the initial state of task status.

        [Task]: T031
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act
        task_id = create_task("Test task")

        # Assert
        task = get_task(task_id)
        assert task.status == Status.PENDING


# ==============================================================================
# Test Suite T032: get_task()
# ==============================================================================


class TestGetTask:
    """
    Test suite for get_task() function.

    Tests task retrieval behavior, error handling, and return values.

    [Task]: T032
    """

    def test_get_task_existing_id(self) -> None:
        """
        Test retrieving an existing task by ID.

        Verifies that get_task returns the correct task when it exists.

        [Task]: T032
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Buy groceries")

        # Act
        task = get_task(task_id)

        # Assert
        assert task.id == task_id
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == Status.PENDING

    def test_get_task_non_existent_id_raises_task_not_found_error(self) -> None:
        """
        Test that retrieving a non-existent task raises TaskNotFoundError.

        Verifies error handling when task does not exist.

        [Task]: T032
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            get_task(999)

    def test_get_task_returned_task_matches_stored_task(self) -> None:
        """
        Test that the returned task matches the stored task exactly.

        Verifies that get_task returns a faithful representation of the stored task.

        [Task]: T032
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Complete project", "Finish all tasks")

        # Act
        retrieved_task = get_task(task_id)

        # Assert - verify all attributes match
        stored_task = list_tasks()[0]
        assert retrieved_task.id == stored_task.id
        assert retrieved_task.title == stored_task.title
        assert retrieved_task.description == stored_task.description
        assert retrieved_task.status == stored_task.status

    def test_get_task_multiple_retrievals_return_same_values(self) -> None:
        """
        Test that multiple retrievals of the same task return consistent values.

        Verifies data consistency across multiple get_task calls.

        [Task]: T032
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Consistent task")

        # Act
        task1 = get_task(task_id)
        task2 = get_task(task_id)

        # Assert
        assert task1.id == task2.id
        assert task1.title == task2.title
        assert task1.description == task2.description
        assert task1.status == task2.status


# ==============================================================================
# Test Suite T033: list_tasks()
# ==============================================================================


class TestListTasks:
    """
    Test suite for list_tasks() function.

    Tests task listing behavior for various storage states and ordering.

    [Task]: T033
    """

    def test_list_tasks_returns_all_tasks_when_tasks_exist(self) -> None:
        """
        Test that list_tasks returns all tasks when tasks exist.

        Verifies that all created tasks are included in the result.

        [Task]: T033
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        create_task("Task 1", "First task")
        create_task("Task 2", "Second task")
        create_task("Task 3", "Third task")

        # Act
        tasks = list_tasks()

        # Assert
        assert len(tasks) == 3
        task_titles = [task.title for task in tasks]
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles
        assert "Task 3" in task_titles

    def test_list_tasks_returns_empty_list_when_no_tasks_exist(self) -> None:
        """
        Test that list_tasks returns an empty list when no tasks exist.

        Verifies behavior with empty storage.

        [Task]: T033
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act
        tasks = list_tasks()

        # Assert
        assert tasks == []
        assert len(tasks) == 0

    def test_list_tasks_verify_order_of_returned_tasks(self) -> None:
        """
        Test that list_tasks returns tasks in the order they were created.

        Verifies task ordering consistency.

        [Task]: T033
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        id1 = create_task("First task")
        id2 = create_task("Second task")
        id3 = create_task("Third task")

        # Act
        tasks = list_tasks()

        # Assert - tasks should be returned in creation order
        assert tasks[0].id == id1
        assert tasks[1].id == id2
        assert tasks[2].id == id3

    def test_list_tasks_after_deletion_excludes_deleted_task(self) -> None:
        """
        Test that list_tasks excludes deleted tasks from the results.

        Verifies that deletion is properly reflected in list output.

        [Task]: T033
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        id1 = create_task("Task 1")
        id2 = create_task("Task 2")
        id3 = create_task("Task 3")
        delete_task(id2)

        # Act
        tasks = list_tasks()

        # Assert
        assert len(tasks) == 2
        task_ids = [task.id for task in tasks]
        assert id1 in task_ids
        assert id2 not in task_ids
        assert id3 in task_ids

    def test_list_tasks_returns_list_of_task_objects(self) -> None:
        """
        Test that list_tasks returns a list of Task objects.

        Verifies the return type is correct.

        [Task]: T033
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        create_task("Test task")

        # Act
        tasks = list_tasks()

        # Assert
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert isinstance(tasks[0], Task)


# ==============================================================================
# Test Suite T034: update_task()
# ==============================================================================


class TestUpdateTask:
    """
    Test suite for update_task() function.

    Tests task update operations including partial updates, validation,
    error handling, and immutability.

    [Task]: T034
    """

    def test_update_task_title_only(self) -> None:
        """
        Test updating only the title of a task.

        Verifies that title can be updated independently while description
        remains unchanged.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title", "Original description")

        # Act
        updated_task = update_task(task_id, title="Updated title")

        # Assert
        assert updated_task.title == "Updated title"
        assert updated_task.description == "Original description"
        assert updated_task.id == task_id
        assert updated_task.status == Status.PENDING

    def test_update_task_description_only(self) -> None:
        """
        Test updating only the description of a task.

        Verifies that description can be updated independently while title
        remains unchanged.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title", "Original description")

        # Act
        updated_task = update_task(task_id, description="Updated description")

        # Assert
        assert updated_task.title == "Original title"
        assert updated_task.description == "Updated description"
        assert updated_task.id == task_id
        assert updated_task.status == Status.PENDING

    def test_update_task_both_title_and_description(self) -> None:
        """
        Test updating both title and description of a task.

        Verifies that both fields can be updated simultaneously.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title", "Original description")

        # Act
        updated_task = update_task(
            task_id, title="New title", description="New description"
        )

        # Assert
        assert updated_task.title == "New title"
        assert updated_task.description == "New description"
        assert updated_task.id == task_id
        assert updated_task.status == Status.PENDING

    def test_update_task_non_existent_id_raises_task_not_found_error(self) -> None:
        """
        Test that updating a non-existent task raises TaskNotFoundError.

        Verifies error handling when task does not exist.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            update_task(999, title="New title")

    def test_update_task_immutability_new_instance(self) -> None:
        """
        Test that update_task creates a new Task instance (immutability).

        Verifies that the updated task is a different object from the original.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title", "Original description")
        original_task = get_task(task_id)

        # Act
        updated_task = update_task(task_id, title="Updated title")

        # Assert - different object
        assert id(updated_task) != id(original_task)

        # Assert - original task has been replaced in storage
        retrieved_task = get_task(task_id)
        assert retrieved_task.title == "Updated title"
        assert id(retrieved_task) == id(updated_task)

    def test_update_task_without_title_or_description_raises_value_error(self) -> None:
        """
        Test that updating without providing title or description raises ValueError.

        Verifies that at least one field must be provided for update.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title", "Original description")

        # Act & Assert
        with pytest.raises(ValueError, match="At least one of title or description must be provided"):
            update_task(task_id)

    def test_update_task_with_empty_title_raises_value_error(self) -> None:
        """
        Test that updating with an empty title raises ValueError.

        Validates that empty titles are not allowed during updates.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title")

        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            update_task(task_id, title="")

    def test_update_task_with_whitespace_title_raises_value_error(self) -> None:
        """
        Test that updating with whitespace-only title raises ValueError.

        Validates that whitespace-only titles are not allowed.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title")

        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            update_task(task_id, title="   ")

    def test_update_task_title_exceeds_500_chars_raises_value_error(self) -> None:
        """
        Test that updating with title > 500 characters raises ValueError.

        Validates that title length limit applies during updates.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title")
        long_title = "a" * 501

        # Act & Assert
        with pytest.raises(ValueError, match="Title exceeds maximum length of 500 characters"):
            update_task(task_id, title=long_title)

    def test_update_task_description_exceeds_500_chars_raises_value_error(self) -> None:
        """
        Test that updating with description > 500 characters raises ValueError.

        Validates that description length limit applies during updates.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title")
        long_description = "a" * 501

        # Act & Assert
        with pytest.raises(ValueError, match="Description exceeds maximum length of 500 characters"):
            update_task(task_id, description=long_description)

    def test_update_task_to_empty_description_succeeds(self) -> None:
        """
        Test that updating description to empty string succeeds.

        Verifies that descriptions can be cleared (set to empty string).

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Title", "Original description")

        # Act
        updated_task = update_task(task_id, description="")

        # Assert
        assert updated_task.description == ""

    def test_update_task_status_preserves_current_status(self) -> None:
        """
        Test that update_task preserves the current status of the task.

        Verifies that updates do not affect task status.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Title", "Description")
        toggle_task_status(task_id)  # Set to COMPLETE

        # Act
        updated_task = update_task(task_id, title="New title")

        # Assert
        assert updated_task.status == Status.COMPLETE

    def test_update_task_id_remains_unchanged(self) -> None:
        """
        Test that update_task does not change the task ID.

        Verifies that task IDs are immutable and cannot be updated.

        [Task]: T034
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Original title", "Original description")

        # Act
        updated_task = update_task(task_id, title="Updated title")

        # Assert
        assert updated_task.id == task_id


# ==============================================================================
# Test Suite T035: delete_task()
# ==============================================================================


class TestDeleteTask:
    """
    Test suite for delete_task() function.

    Tests task deletion behavior, error handling, and ID reuse prevention.

    [Task]: T035
    """

    def test_delete_task_existing_id(self) -> None:
        """
        Test deleting an existing task by ID.

        Verifies that a task can be successfully deleted from storage.

        [Task]: T035
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Task to delete")

        # Act
        delete_task(task_id)

        # Assert
        with pytest.raises(TaskNotFoundError, match="Task with ID 1 not found"):
            get_task(task_id)

    def test_delete_task_non_existent_id_raises_task_not_found_error(self) -> None:
        """
        Test that deleting a non-existent task raises TaskNotFoundError.

        Verifies error handling when task does not exist.

        [Task]: T035
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            delete_task(999)

    def test_delete_task_id_reuse_prevention(self) -> None:
        """
        Test that deleted IDs are never reused.

        Verifies that after deleting a task, its ID is not reused for new tasks.

        [Task]: T035
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        id1 = create_task("Task 1")
        id2 = create_task("Task 2")
        id3 = create_task("Task 3")

        # Act - delete task 2
        delete_task(id2)

        # Act - create new task
        id4 = create_task("Task 4")

        # Assert - new task gets ID 4, not reused ID 2
        assert id4 == 4
        tasks = list_tasks()
        task_ids = [task.id for task in tasks]
        assert id2 not in task_ids
        assert id4 in task_ids

    def test_delete_task_verify_task_removed_from_storage(self) -> None:
        """
        Test that deleted task is completely removed from storage.

        Verifies that the task no longer appears in any retrieval operations.

        [Task]: T035
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        id1 = create_task("Task 1")
        id2 = create_task("Task 2")
        id3 = create_task("Task 3")

        # Act
        delete_task(id2)

        # Assert
        tasks = list_tasks()
        assert len(tasks) == 2
        task_ids = [task.id for task in tasks]
        assert id1 in task_ids
        assert id2 not in task_ids
        assert id3 in task_ids

    def test_delete_task_can_delete_multiple_tasks(self) -> None:
        """
        Test that multiple tasks can be deleted sequentially.

        Verifies that deletion works correctly across multiple operations.

        [Task]: T035
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        id1 = create_task("Task 1")
        id2 = create_task("Task 2")
        id3 = create_task("Task 3")

        # Act
        delete_task(id1)
        delete_task(id3)

        # Assert
        tasks = list_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == id2

    def test_delete_task_delete_all_tasks(self) -> None:
        """
        Test that all tasks can be deleted.

        Verifies that storage can be completely emptied.

        [Task]: T035
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        create_task("Task 1")
        create_task("Task 2")
        create_task("Task 3")

        # Act
        delete_task(1)
        delete_task(2)
        delete_task(3)

        # Assert
        tasks = list_tasks()
        assert tasks == []

    def test_delete_task_same_id_twice_raises_task_not_found_error(self) -> None:
        """
        Test that attempting to delete the same task twice raises error on second attempt.

        Verifies error handling when trying to delete already-deleted task.

        [Task]: T035
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Task to delete")

        # Act - first deletion succeeds
        delete_task(task_id)

        # Assert - second deletion raises error
        with pytest.raises(TaskNotFoundError, match="Task with ID 1 not found"):
            delete_task(task_id)


# ==============================================================================
# Test Suite T036: toggle_task_status()
# ==============================================================================


class TestToggleTaskStatus:
    """
    Test suite for toggle_task_status() function.

    Tests task status toggling between PENDING and COMPLETE states.

    [Task]: T036
    """

    def test_toggle_task_status_from_pending_to_complete(self) -> None:
        """
        Test toggling task status from PENDING to COMPLETE.

        Verifies that a pending task can be marked as complete.

        [Task]: T036
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Task to complete")

        # Act
        updated_task = toggle_task_status(task_id)

        # Assert
        assert updated_task.status == Status.COMPLETE

    def test_toggle_task_status_from_complete_to_pending(self) -> None:
        """
        Test toggling task status from COMPLETE to PENDING.

        Verifies that a complete task can be toggled back to pending.

        [Task]: T036
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Task to complete")
        toggle_task_status(task_id)  # Set to COMPLETE

        # Act
        updated_task = toggle_task_status(task_id)  # Toggle back to PENDING

        # Assert
        assert updated_task.status == Status.PENDING

    def test_toggle_task_status_non_existent_id_raises_task_not_found_error(self) -> None:
        """
        Test that toggling a non-existent task raises TaskNotFoundError.

        Verifies error handling when task does not exist.

        [Task]: T036
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Act & Assert
        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            toggle_task_status(999)

    def test_toggle_task_status_returns_updated_task_with_new_status(self) -> None:
        """
        Test that toggle_task_status returns the updated task with new status.

        Verifies that the returned task reflects the status change.

        [Task]: T036
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Task to complete")

        # Act
        updated_task = toggle_task_status(task_id)

        # Assert
        assert updated_task.status == Status.COMPLETE
        assert updated_task.id == task_id
        assert updated_task.title == "Task to complete"

    def test_toggle_task_status_multiple_toggles(self) -> None:
        """
        Test that status can be toggled multiple times.

        Verifies consistent behavior across multiple toggle operations.

        [Task]: T036
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Task to toggle")

        # Act - toggle multiple times
        task1 = toggle_task_status(task_id)  # PENDING -> COMPLETE
        task2 = toggle_task_status(task_id)  # COMPLETE -> PENDING
        task3 = toggle_task_status(task_id)  # PENDING -> COMPLETE

        # Assert
        assert task1.status == Status.COMPLETE
        assert task2.status == Status.PENDING
        assert task3.status == Status.COMPLETE

    def test_toggle_task_status_preserves_task_attributes(self) -> None:
        """
        Test that toggle_task_status preserves all other task attributes.

        Verifies that only status changes, not id, title, or description.

        [Task]: T036
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Title", "Description")
        original_task = get_task(task_id)

        # Act
        updated_task = toggle_task_status(task_id)

        # Assert
        assert updated_task.id == original_task.id
        assert updated_task.title == original_task.title
        assert updated_task.description == original_task.description
        assert updated_task.status != original_task.status

    def test_toggle_task_status_immutability_new_instance(self) -> None:
        """
        Test that toggle_task_status creates a new Task instance (immutability).

        Verifies that the updated task is a different object from the original.

        [Task]: T036
        [From]: specs/001-todo-console-app/tasks.md
        """
        # Arrange
        task_id = create_task("Task to toggle")
        original_task = get_task(task_id)

        # Act
        updated_task = toggle_task_status(task_id)

        # Assert - different object
        assert id(updated_task) != id(original_task)

        # Assert - storage updated
        retrieved_task = get_task(task_id)
        assert retrieved_task.status == Status.COMPLETE
        assert id(retrieved_task) == id(updated_task)


# ==============================================================================
# Additional Tests for Validation Functions (Coverage)
# ==============================================================================


class TestValidationFunctions:
    """
    Test suite for validation functions (validate_title, validate_description).

    These tests provide additional coverage for the validation logic used
    by create_task and update_task.

    [From]: specs/001-todo-console-app/tasks.md
    """

    def test_validate_title_valid_inputs(self) -> None:
        """
        Test validate_title with various valid inputs.

        Verifies that valid titles pass validation.

        [From]: specs/001-todo-console-app/tasks.md
        """
        # These should not raise exceptions
        validate_title("Normal title")
        validate_title("Title with numbers 123")
        validate_title("Title with special chars!@#$%")
        validate_title("  Valid title with surrounding whitespace  ")

    def test_validate_title_invalid_empty_string(self) -> None:
        """Test that validate_title raises ValueError for empty string."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_title("")

    def test_validate_title_invalid_whitespace_only(self) -> None:
        """Test that validate_title raises ValueError for whitespace-only string."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            validate_title("   ")

    def test_validate_title_invalid_too_long(self) -> None:
        """Test that validate_title raises ValueError for too-long string."""
        with pytest.raises(ValueError, match="Title exceeds maximum length of 500 characters"):
            validate_title("a" * 501)

    def test_validate_description_valid_inputs(self) -> None:
        """
        Test validate_description with various valid inputs.

        Verifies that valid descriptions pass validation.

        [From]: specs/001-todo-console-app/tasks.md
        """
        # These should not raise exceptions
        validate_description(None)
        validate_description("")
        validate_description("Normal description")
        validate_description("  Description with whitespace  ")

    def test_validate_description_invalid_too_long(self) -> None:
        """Test that validate_description raises ValueError for too-long string."""
        with pytest.raises(ValueError, match="Description exceeds maximum length of 500 characters"):
            validate_description("a" * 501)

    def test_validate_description_exactly_500_chars(self) -> None:
        """Test that validate_description accepts exactly 500 characters."""
        # Should not raise exception
        validate_description("a" * 500)


# ==============================================================================
# Integration Tests (Cross-function verification)
# ==============================================================================


class TestServiceIntegration:
    """
    Integration tests that verify correct behavior across multiple service functions.

    These tests ensure that the service layer functions work together correctly.

    [From]: specs/001-todo-console-app/tasks.md
    """

    def test_full_crud_workflow(self) -> None:
        """
        Test a complete CRUD workflow (Create, Read, Update, Delete).

        Verifies that all CRUD operations work together seamlessly.

        [From]: specs/001-todo-console-app/tasks.md
        """
        # Create
        task_id = create_task("Initial title", "Initial description")

        # Read
        task = get_task(task_id)
        assert task.title == "Initial title"

        # Update
        updated = update_task(task_id, title="Updated title")
        assert updated.title == "Updated title"

        # Delete
        delete_task(task_id)

        # Verify deletion
        with pytest.raises(TaskNotFoundError):
            get_task(task_id)

    def test_multiple_tasks_with_status_changes(self) -> None:
        """
        Test managing multiple tasks with various status changes.

        Verifies that status toggling works correctly across multiple tasks.

        [From]: specs/001-todo-console-app/tasks.md
        """
        # Create multiple tasks
        id1 = create_task("Task 1")
        id2 = create_task("Task 2")
        id3 = create_task("Task 3")

        # Toggle some tasks
        toggle_task_status(id1)  # COMPLETE
        toggle_task_status(id3)  # COMPLETE

        # Verify states
        tasks = list_tasks()
        task_dict = {task.id: task.status for task in tasks}

        assert task_dict[id1] == Status.COMPLETE
        assert task_dict[id2] == Status.PENDING
        assert task_dict[id3] == Status.COMPLETE

    def test_update_and_toggle_workflow(self) -> None:
        """
        Test a workflow combining updates and status toggles.

        Verifies that updates and status changes can be performed together.

        [From]: specs/001-todo-console-app/tasks.md
        """
        # Create task
        task_id = create_task("Original title", "Original description")

        # Update title
        update_task(task_id, title="Updated title")

        # Toggle status
        toggle_task_status(task_id)

        # Update description
        update_task(task_id, description="Updated description")

        # Verify final state
        task = get_task(task_id)
        assert task.title == "Updated title"
        assert task.description == "Updated description"
        assert task.status == Status.COMPLETE
