"""
Main entry point for Todo Console Application using argparse.

[Task]: T016 - Implement argparse parser with subcommands
[Task]: T027 - Configure error logging infrastructure
[Feature]: 001-todo-console-app
[Spec]: specs/001-todo-console-app/research.md, contracts/cli-commands.md
[Requirements]: FR-015 - System MUST provide CLI via loop OR CLI arguments

Usage:
    Interactive mode: python -m todo.cli.main
    One-shot mode:  python -m todo.cli.main <command> [args...]
"""

import argparse
import logging
import shlex
import sys
from typing import List, Optional

from todo.cli import commands

# Configure logging per Constitution Principle VII (Observability)
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure ArgumentParser for Todo CLI.

    [Task]: T016
    [Spec]: specs/001-todo-console-app/research.md §CLI Framework Decision

    Returns:
        Configured ArgumentParser with all subcommands defined.

    Subcommands:
        add, list, update, delete, complete, help, exit
    """
    parser = argparse.ArgumentParser(
        prog="todo-cli",
        description="Todo CLI - In-Memory Task Management",
        allow_abbrev=False,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Available commands",
        metavar="<command>",
        help="Use 'help' for command descriptions",
    )

    # add subcommand
    add_parser = subparsers.add_parser(
        "add",
        help="Create a new task",
        description="Create a new task with mandatory title and optional description",
    )
    add_parser.add_argument(
        "title",
        type=str,
        help="Task title (required)",
    )
    add_parser.add_argument(
        "description",
        type=str,
        nargs="?",
        default=None,
        help="Optional task description",
    )

    # list subcommand
    subparsers.add_parser(
        "list",
        help="List all tasks",
        description="Display all tasks with ID, Status, and Title",
    )

    # update subcommand
    update_parser = subparsers.add_parser(
        "update",
        help="Update task title or description",
        description="Edit the title or description of an existing task by ID",
    )
    update_parser.add_argument(
        "id",
        type=int,
        help="Task ID to update",
    )
    update_parser.add_argument(
        "field",
        choices=["title", "description"],
        help="Field to update: 'title' or 'description'",
    )
    update_parser.add_argument(
        "value",
        type=str,
        help="New value for the field",
    )

    # delete subcommand
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task",
        description="Remove a task from memory using its unique ID",
    )
    delete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to delete",
    )

    # complete subcommand
    complete_parser = subparsers.add_parser(
        "complete",
        help="Mark task as complete/incomplete",
        description="Toggle a task's status between 'Pending' and 'Complete'",
    )
    complete_parser.add_argument(
        "id",
        type=int,
        help="Task ID to mark complete/incomplete",
    )

    # help subcommand
    subparsers.add_parser(
        "help",
        help="Show help message",
        description="Display usage information and available commands",
    )

    # exit subcommand (only used in interactive mode)
    subparsers.add_parser(
        "exit",
        help="Exit application",
        description="Gracefully quit the Todo CLI application",
    )

    return parser


def execute_command(command: Optional[str], args: List[str]) -> None:
    """
    Route command string to appropriate handler function.

    [Task]: T016
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md

    Args:
        command: Command name (e.g., 'add', 'list', 'help')
        args: List of command arguments

    Raises:
        SystemExit: For 'exit' command in interactive mode
    """
    if command is None:
        # No command provided
        return

    command_handlers = {
        "add": lambda: commands.add_command(args),
        "list": lambda: commands.list_command(args),
        "update": lambda: commands.update_command(args),
        "delete": lambda: commands.delete_command(args),
        "complete": lambda: commands.complete_command(args),
        "help": lambda: commands.help(),
        "exit": lambda: commands.exit_app(),
    }

    handler = command_handlers.get(command)
    if handler:
        handler()
    else:
        # Unknown command
        print(f"Error: Unknown command '{command}'")
        print("Type 'help' for available commands")


def run_interactive_mode() -> None:
    """
    Run CLI in interactive REPL mode.

    [Task]: T016 (interactive mode routing)
    [Task]: T027 - Configure error logging infrastructure
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §Interactive Loop

    Behavior:
        - Displays welcome message and prompt
        - Accepts commands until user types 'exit'
        - Shows help on 'help' or invalid command
    """
    print("Todo CLI - In-Memory Task Management")
    print()
    print("NOTE: Tasks are stored in memory only and will be lost when you exit.")
    print("For persistent storage, see Phase 2 documentation.")
    print()
    print("Type 'help' for available commands or 'exit' to quit.")

    while True:
        try:
            user_input = input("todo> ").strip()
            if not user_input:
                continue

            # Parse interactive input (use shlex to handle quoted arguments)
            parts = shlex.split(user_input)
            if not parts:
                continue

            command = parts[0]
            args = parts[1:]

            # Handle exit specially to break loop
            if command in ("exit", "quit"):
                commands.exit_app()
                break

            # Handle help
            if command == "help":
                commands.help()
                continue

            # Route to command handler
            execute_command(command, args)

        except KeyboardInterrupt:
            print()
            commands.exit_app()
            break
        except EOFError:
            print()
            commands.exit_app()
            break
        except Exception as e:
            logger.error(f"Unexpected error in interactive mode: {e}")
            print(f"Error: An unexpected error occurred. Please try again.")


def run_one_shot_mode(args: List[str]) -> None:
    """
    Run CLI in one-shot command mode.

    [Task]: T016 (one-shot mode routing)
    [Task]: T025 - One-shot command mode
    [Spec]: specs/001-todo-console-app/contracts/cli-commands.md §One-Shot Command

    Args:
        args: Command-line arguments to parse and execute

    Behavior:
        - Executes single command with provided arguments
        - Displays output to stdout
        - Exits immediately after completion
    """
    parser = create_parser()

    try:
        parsed_args = parser.parse_args(args)

        # Route to appropriate handler
        if parsed_args.command == "add":
            commands.add_command([parsed_args.title] + ([parsed_args.description] if parsed_args.description else []))
        elif parsed_args.command == "list":
            commands.list_command([])
        elif parsed_args.command == "update":
            commands.update_command([str(parsed_args.id), parsed_args.field, parsed_args.value])
        elif parsed_args.command == "delete":
            commands.delete_command([str(parsed_args.id)])
        elif parsed_args.command == "complete":
            commands.complete_command([str(parsed_args.id)])
        elif parsed_args.command == "help":
            commands.help()
        elif parsed_args.command is None:
            # No command provided in one-shot mode - show help
            parser.print_help()

    except SystemExit as e:
        # argparse exits with 0 on --help, 2 on errors
        if e.code != 0:
            raise


def main() -> None:
    """
    Main entry point for Todo CLI application.

    [Task]: T016
    [Spec]: specs/001-todo-console-app/research.md §CLI Interface Pattern

    Usage:
        python -m todo.cli.main              # Interactive mode (default)
        python -m todo.cli.main add "Task"  # One-shot mode

    Behavior:
        - If no arguments: Enter interactive REPL loop
        - If arguments provided: Execute single command and exit
    """
    if len(sys.argv) > 1:
        # One-shot mode: arguments provided
        run_one_shot_mode(sys.argv[1:])
    else:
        # Interactive mode: no arguments
        run_interactive_mode()


if __name__ == "__main__":
    main()
