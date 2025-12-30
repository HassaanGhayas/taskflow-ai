"""
Unit tests for Task model and Status enum.

[Task]: T028, T029, T030
[From]: specs/001-todo-console-app/tasks.md
"""

import pytest
from dataclasses import FrozenInstanceError

from src.todo.models.task import Status, Task


class TestStatusEnum:
    """Test cases for Status enum.

    [Task]: T028
    """

    def test_status_enum_values(self: "TestStatusEnum") -> None:
        """
        Test that Status enum has correct values.

        Verifies that the enum has exactly PENDING and COMPLETE members.

        [Task]: T028
        """
        assert hasattr(Status, "PENDING")
        assert hasattr(Status, "COMPLETE")

    def test_status_pending_value(self: "TestStatusEnum") -> None:
        """
        Test that Status.PENDING has correct string representation.

        Verifies that Status.PENDING equals "Pending".

        [Task]: T028
        """
        assert Status.PENDING.value == "Pending"

    def test_status_complete_value(self: "TestStatusEnum") -> None:
        """
        Test that Status.COMPLETE has correct string representation.

        Verifies that Status.COMPLETE equals "Complete".

        [Task]: T028
        """
        assert Status.COMPLETE.value == "Complete"

    def test_status_enum_iteration(self: "TestStatusEnum") -> None:
        """
        Test that all Status enum members are accessible.

        Verifies that both PENDING and COMPLETE can be iterated.

        [Task]: T028
        """
        status_list = list(Status)
        assert len(status_list) == 2
        assert Status.PENDING in status_list
        assert Status.COMPLETE in status_list

    def test_status_enum_string_representation(self: "TestStatusEnum") -> None:
        """
        Test that Status enum members have correct string representations.

        Verifies that str(Status.PENDING) returns "Status.PENDING"
        and str(Status.COMPLETE) returns "Status.COMPLETE".

        [Task]: T028
        """
        assert str(Status.PENDING) == "Status.PENDING"
        assert str(Status.COMPLETE) == "Status.COMPLETE"


class TestTaskDataclass:
    """Test cases for Task dataclass.

    [Task]: T029, T030
    """

    def test_task_creation_with_all_fields(self: "TestTaskDataclass") -> None:
        """
        Test Task creation with all fields provided.

        Verifies that a Task can be created with id, title, description, and status.

        [Task]: T029
        """
        task = Task(
            id=1,
            title="Buy groceries",
            description="Milk, eggs, bread",
            status=Status.PENDING,
        )

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.status == Status.PENDING

    def test_task_creation_with_none_description(self: "TestTaskDataclass") -> None:
        """
        Test Task creation with description as None.

        Verifies that description can be None (default behavior).

        [Task]: T029
        """
        task = Task(
            id=1,
            title="Buy groceries",
            description=None,
            status=Status.PENDING,
        )

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == Status.PENDING

    def test_task_id_attribute(self: "TestTaskDataclass") -> None:
        """
        Test Task id attribute.

        Verifies that the id field is correctly stored and accessible.

        [Task]: T029
        """
        task = Task(id=42, title="Test task", description=None, status=Status.PENDING)

        assert task.id == 42

    def test_task_title_attribute(self: "TestTaskDataclass") -> None:
        """
        Test Task title attribute.

        Verifies that the title field is correctly stored and accessible.

        [Task]: T029
        """
        task = Task(id=1, title="Sample task title", description=None, status=Status.PENDING)

        assert task.title == "Sample task title"

    def test_task_description_attribute(self: "TestTaskDataclass") -> None:
        """
        Test Task description attribute.

        Verifies that the description field is correctly stored and accessible.

        [Task]: T029
        """
        description = "This is a detailed description of the task"
        task = Task(id=1, title="Task", description=description, status=Status.PENDING)

        assert task.description == description

    def test_task_status_attribute(self: "TestTaskDataclass") -> None:
        """
        Test Task status attribute.

        Verifies that the status field is correctly stored and accessible.

        [Task]: T029
        """
        task = Task(id=1, title="Task", description=None, status=Status.PENDING)

        assert task.status == Status.PENDING

    def test_task_immutability_cannot_modify_id(self: "TestTaskDataclass") -> None:
        """
        Test that Task is immutable - cannot modify id.

        Verifies that frozen=True prevents attribute modification.

        [Task]: T029
        """
        task = Task(id=1, title="Task", description=None, status=Status.PENDING)

        with pytest.raises(FrozenInstanceError):
            task.id = 2

    def test_task_immutability_cannot_modify_title(self: "TestTaskDataclass") -> None:
        """
        Test that Task is immutable - cannot modify title.

        Verifies that frozen=True prevents attribute modification.

        [Task]: T029
        """
        task = Task(id=1, title="Task", description=None, status=Status.PENDING)

        with pytest.raises(FrozenInstanceError):
            task.title = "New title"

    def test_task_immutability_cannot_modify_description(self: "TestTaskDataclass") -> None:
        """
        Test that Task is immutable - cannot modify description.

        Verifies that frozen=True prevents attribute modification.

        [Task]: T029
        """
        task = Task(id=1, title="Task", description=None, status=Status.PENDING)

        with pytest.raises(FrozenInstanceError):
            task.description = "New description"

    def test_task_immutability_cannot_modify_status(self: "TestTaskDataclass") -> None:
        """
        Test that Task is immutable - cannot modify status.

        Verifies that frozen=True prevents attribute modification.

        [Task]: T029
        """
        task = Task(id=1, title="Task", description=None, status=Status.PENDING)

        with pytest.raises(FrozenInstanceError):
            task.status = Status.COMPLETE

    def test_task_equality(self: "TestTaskDataclass") -> None:
        """
        Test Task equality comparison.

        Verifies that two Tasks with identical fields are equal.

        [Task]: T029
        """
        task1 = Task(id=1, title="Task", description="Desc", status=Status.PENDING)
        task2 = Task(id=1, title="Task", description="Desc", status=Status.PENDING)

        assert task1 == task2

    def test_task_inequality(self: "TestTaskDataclass") -> None:
        """
        Test Task inequality comparison.

        Verifies that Tasks with different fields are not equal.

        [Task]: T029
        """
        task1 = Task(id=1, title="Task", description="Desc", status=Status.PENDING)
        task2 = Task(id=2, title="Task", description="Desc", status=Status.PENDING)

        assert task1 != task2


class TestTaskWithStatusEnum:
    """Test cases for Task dataclass behavior with Status enum.

    [Task]: T030
    """

    def test_task_creation_with_pending_status(self: "TestTaskWithStatusEnum") -> None:
        """
        Test Task creation with Status.PENDING.

        Verifies that a Task can be created with PENDING status.

        [Task]: T030
        """
        task = Task(
            id=1,
            title="Pending task",
            description=None,
            status=Status.PENDING,
        )

        assert task.status == Status.PENDING
        assert task.status.value == "Pending"

    def test_task_creation_with_complete_status(self: "TestTaskWithStatusEnum") -> None:
        """
        Test Task creation with Status.COMPLETE.

        Verifies that a Task can be created with COMPLETE status.

        [Task]: T030
        """
        task = Task(
            id=1,
            title="Completed task",
            description=None,
            status=Status.COMPLETE,
        )

        assert task.status == Status.COMPLETE
        assert task.status.value == "Complete"

    def test_task_status_accepts_enum_value(self: "TestTaskWithStatusEnum") -> None:
        """
        Test that status field accepts Status enum values correctly.

        Verifies that both Status.PENDING and Status.COMPLETE
        can be assigned to the status field.

        [Task]: T030
        """
        pending_task = Task(
            id=1,
            title="Task",
            description=None,
            status=Status.PENDING,
        )

        complete_task = Task(
            id=2,
            title="Task",
            description=None,
            status=Status.COMPLETE,
        )

        assert pending_task.status == Status.PENDING
        assert complete_task.status == Status.COMPLETE

    def test_task_status_type_check(self: "TestTaskWithStatusEnum") -> None:
        """
        Test that status field is of type Status.

        Verifies that the status field contains a Status enum member.

        [Task]: T030
        """
        task = Task(id=1, title="Task", description=None, status=Status.PENDING)

        assert isinstance(task.status, Status)
        assert isinstance(task.status, type(Status.PENDING))

    def test_multiple_tasks_with_different_statuses(self: "TestTaskWithStatusEnum") -> None:
        """
        Test creating multiple tasks with different statuses.

        Verifies that multiple Tasks can have different status values.

        [Task]: T030
        """
        tasks = [
            Task(id=1, title="Task 1", description=None, status=Status.PENDING),
            Task(id=2, title="Task 2", description=None, status=Status.COMPLETE),
            Task(id=3, title="Task 3", description=None, status=Status.PENDING),
        ]

        assert tasks[0].status == Status.PENDING
        assert tasks[1].status == Status.COMPLETE
        assert tasks[2].status == Status.PENDING

    def test_task_status_string_value_access(self: "TestTaskWithStatusEnum") -> None:
        """
        Test accessing the string value of Task status.

        Verifies that task.status.value returns the correct string representation.

        [Task]: T030
        """
        pending_task = Task(
            id=1,
            title="Task",
            description=None,
            status=Status.PENDING,
        )

        complete_task = Task(
            id=2,
            title="Task",
            description=None,
            status=Status.COMPLETE,
        )

        assert pending_task.status.value == "Pending"
        assert complete_task.status.value == "Complete"

    def test_task_status_comparison(self: "TestTaskWithStatusEnum") -> None:
        """
        Test comparing Task statuses.

        Verifies that Task statuses can be compared using == operator.

        [Task]: T030
        """
        task1 = Task(id=1, title="Task", description=None, status=Status.PENDING)
        task2 = Task(id=2, title="Task", description=None, status=Status.PENDING)
        task3 = Task(id=3, title="Task", description=None, status=Status.COMPLETE)

        assert task1.status == task2.status
        assert task1.status != task3.status
        assert task2.status == Status.PENDING
        assert task3.status == Status.COMPLETE
