"""
CLI command implementations for Todo Console Application.

[Task]: T017-T023
[Feature]: 001-todo-console-app
[Spec]: specs/001-todo-console-app/contracts/cli-commands.md
"""

from typing import List

from todo.services.task_service import (
    TaskNotFoundError,
    create_task,
    delete_task,
    get_task,
    list_tasks,
    toggle_task_status,
    update_task,
)


def help() -> None:
    """
    Display usage information and available commands.

    [Task]: T022 - Implement help command handler
    [Feature]: 001-todo-console-app
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §help
    [Requirements]: FR-013 - System MUST display clear error messages

    Output format:
        Table or clear list of all available commands with descriptions
        and usage examples per quickstart.md
    """
    help_text = """
Todo CLI - Task Management

Available commands:
  add <title> ["<description>"]      Create a new task
  list                                  List all tasks
  update <id> title "<title>"            Update task title
  update <id> description "<desc>"        Update task description
  delete <id>                           Delete a task
  complete <id>                          Mark task as complete/incomplete
  help                                   Show this help message
  exit                                   Exit the application

Examples:
  add "Buy groceries"
  add "Write documentation" "Complete spec.md and plan.md"
  list
  complete 1
  update 2 title "New title"
  update 2 description "New description"
  delete 3

For more information, see README.md
"""
    print(help_text.strip())


def exit_app() -> None:
    """
    Gracefully exit the application.

    [Task]: T023 - Implement exit command handler
    [Feature]: 001-todo-console-app
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §exit
    [Requirements]: FR-013 - System MUST display clear error messages

    Behavior:
        Prints "Goodbye!" message and signals application to terminate.
        This function does not actually exit; the caller handles termination.
    """
    print("Goodbye!")


def add_command(args: List[str]) -> None:
    """
    Create a new task with the given title and optional description.

    [Task]: T017 - Implement add command handler
    [Feature]: 001-todo-console-app
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §add

    Args:
        args: Command arguments as a list of strings.
            args[0]: Task title (required)
            args[1]: Task description (optional)

    Output:
        Success: "Task created with ID {task_id}"
        Error: "Error: Title cannot be empty"
               "Error: Title exceeds maximum length of 500 characters"

    Examples:
        >>> add_command(["Buy groceries"])
        Task created with ID 1

        >>> add_command(["Write documentation", "Complete spec.md"])
        Task created with ID 2

        >>> add_command([""])
        Error: Title cannot be empty
    """
    try:
        # Parse arguments
        title = args[0] if len(args) > 0 else ""
        description = args[1] if len(args) > 1 else None

        # Call service layer to create task
        task_id = create_task(title, description)

        # Print success message
        print(f"Task created with ID {task_id}")

    except ValueError as e:
        print(f"Error: {e}")
    except IndexError:
        print("Error: Title cannot be empty")


def list_command(args: List[str]) -> None:
    """
    Display all tasks with ID, Status, and Title in a formatted table.

    [Task]: T018 - Implement list command handler
    [Feature]: 001-todo-console-app
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §list

    Args:
        args: Command arguments (unused for list command)

    Output:
        Table format with columns: ID, Status, Title
        If empty: "No tasks found. Add a task to get started."

    Examples:
        >>> list_command([])
          ID  Status     Title
        ----  --------    -----
          1  Pending     Buy groceries
          2  Complete     Write documentation
    """
    # Get all tasks from service layer
    tasks = list_tasks()

    # Check if no tasks exist
    if not tasks:
        print("No tasks found. Add a task to get started.")
        return

    # Print table header
    print(f"  ID  Status     Title")
    print(f"----  --------    -----")

    # Print each task
    for task in tasks:
        status_value = task.status.value
        print(f"  {task.id}  {status_value:10} {task.title}")


def update_command(args: List[str]) -> None:
    """
    Update an existing task's title or description by its ID.

    [Task]: T019 - Implement update command handler
    [Feature]: 001-todo-console-app
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §update

    Args:
        args: Command arguments as a list of strings.
            args[0]: Task ID (integer)
            args[1]: Field to update ("title" or "description")
            args[2]: New value for the field

    Output:
        Success: "Task {task_id} updated successfully"
        Error: "Error: Task with ID {task_id} not found"
               "Error: At least one of title or description must be provided"
               "Error: Title cannot be empty"

    Examples:
        >>> update_command(["1", "title", "Buy organic groceries"])
        Task 1 updated successfully

        >>> update_command(["2", "description", "Updated description"])
        Task 2 updated successfully

        >>> update_command(["999", "title", "New"])
        Error: Task with ID 999 not found
    """
    try:
        # Validate that we have enough arguments
        if len(args) < 3:
            print("Error: Must provide either 'title' or 'description' to update")
            print("Usage: update <id> title \"<new_title>\" | description \"<new_description>\"")
            return

        # Parse arguments
        task_id = int(args[0])
        field = args[1]
        value = args[2] if len(args) > 2 else None

        # Determine which field to update
        title = None
        description = None

        if field == "title":
            title = value
        elif field == "description":
            description = value
        else:
            print("Error: Must provide either 'title' or 'description' to update")
            print("Usage: update <id> title \"<new_title>\" | description \"<new_description>\"")
            return

        # Call service layer to update task
        update_task(task_id, title, description)

        # Print success message
        print(f"Task {task_id} updated successfully")

    except TaskNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            print("Error: Invalid task ID. Must be a number.")
        else:
            print(f"Error: {e}")


def delete_command(args: List[str]) -> None:
    """
    Delete a task from memory by its unique ID.

    [Task]: T020 - Implement delete command handler
    [Feature]: 001-todo-console-app
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §delete

    Args:
        args: Command arguments as a list of strings.
            args[0]: Task ID (integer)

    Output:
        Success: "Task {task_id} deleted successfully"
        Error: "Error: Task with ID {task_id} not found"
               "Error: Invalid task ID. Must be a number."

    Examples:
        >>> delete_command(["1"])
        Task 1 deleted successfully

        >>> delete_command(["999"])
        Error: Task with ID 999 not found

        >>> delete_command(["abc"])
        Error: Invalid task ID. Must be a number.
    """
    try:
        # Validate that we have an argument
        if len(args) < 1:
            print("Error: Invalid task ID. Must be a number.")
            return

        # Parse task ID
        task_id = int(args[0])

        # Call service layer to delete task
        delete_task(task_id)

        # Print success message
        print(f"Task {task_id} deleted successfully")

    except TaskNotFoundError as e:
        print(f"Error: {e}")
    except ValueError:
        print("Error: Invalid task ID. Must be a number.")


def complete_command(args: List[str]) -> None:
    """
    Toggle a task's status between "Pending" and "Complete".

    [Task]: T021 - Implement complete command handler
    [Feature]: 001-todo-console-app
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §complete

    Args:
        args: Command arguments as a list of strings.
            args[0]: Task ID (integer)

    Output:
        Success: "Task {task_id} marked as Complete"
                "Task {task_id} marked as Pending"
        Error: "Error: Task with ID {task_id} not found"
               "Error: Invalid task ID. Must be a number."

    Examples:
        >>> complete_command(["1"])
        Task 1 marked as Complete

        >>> complete_command(["1"])
        Task 1 marked as Pending

        >>> complete_command(["999"])
        Error: Task with ID 999 not found
    """
    from todo.models.task import Status

    try:
        # Validate that we have an argument
        if len(args) < 1:
            print("Error: Invalid task ID. Must be a number.")
            return

        # Parse task ID
        task_id = int(args[0])

        # Call service layer to toggle task status
        updated_task = toggle_task_status(task_id)

        # Determine the new status message
        new_status = updated_task.status
        status_text = "Complete" if new_status == Status.COMPLETE else "Pending"

        # Print success message
        print(f"Task {task_id} marked as {status_text}")

    except TaskNotFoundError as e:
        print(f"Error: {e}")
    except ValueError:
        print("Error: Invalid task ID. Must be a number.")
