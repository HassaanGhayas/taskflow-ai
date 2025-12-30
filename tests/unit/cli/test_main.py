"""
Unit tests for CLI main module.

Tests argparse parser, command routing, and entry points.

[Task]: T063 - Improve coverage to 80%
[Feature]: 001-todo-console-app
"""

import argparse
import pytest
from unittest.mock import patch

from todo.cli.main import (
    create_parser,
    execute_command,
    run_one_shot_mode,
)


class TestCreateParser:
    """Test create_parser() function."""

    def test_create_parser_returns_argparse_parser(self) -> None:
        """Verify create_parser returns an ArgumentParser."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_has_add_subcommand(self) -> None:
        """Verify parser has 'add' subcommand."""
        parser = create_parser()
        # Parse with a help flag to trigger subparsers
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

    def test_add_subcommand_exists(self) -> None:
        """Verify 'add' subcommand is registered."""
        parser = create_parser()
        # Get subparsers
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                assert "add" in action.choices
                break

    def test_list_subcommand_exists(self) -> None:
        """Verify 'list' subcommand is registered."""
        parser = create_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                assert "list" in action.choices
                break

    def test_update_subcommand_exists(self) -> None:
        """Verify 'update' subcommand is registered."""
        parser = create_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                assert "update" in action.choices
                break

    def test_delete_subcommand_exists(self) -> None:
        """Verify 'delete' subcommand is registered."""
        parser = create_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                assert "delete" in action.choices
                break

    def test_complete_subcommand_exists(self) -> None:
        """Verify 'complete' subcommand is registered."""
        parser = create_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                assert "complete" in action.choices
                break


class TestExecuteCommand:
    """Test execute_command() function."""

    def test_execute_add_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test routing 'add' command to add_command."""
        with patch("todo.cli.commands.add_command") as mock_add:
            execute_command("add", ["Test Task"])
            mock_add.assert_called_once_with(["Test Task"])

    def test_execute_list_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test routing 'list' command to list_command."""
        with patch("todo.cli.commands.list_command") as mock_list:
            execute_command("list", [])
            mock_list.assert_called_once_with([])

    def test_execute_update_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test routing 'update' command to update_command."""
        with patch("todo.cli.commands.update_command") as mock_update:
            execute_command("update", ["1", "title", "New Title"])
            mock_update.assert_called_once_with(["1", "title", "New Title"])

    def test_execute_delete_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test routing 'delete' command to delete_command."""
        with patch("todo.cli.commands.delete_command") as mock_delete:
            execute_command("delete", ["1"])
            mock_delete.assert_called_once_with(["1"])

    def test_execute_complete_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test routing 'complete' command to complete_command."""
        with patch("todo.cli.commands.complete_command") as mock_complete:
            execute_command("complete", ["1"])
            mock_complete.assert_called_once_with(["1"])

    def test_execute_help_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test routing 'help' command to help function."""
        with patch("todo.cli.commands.help") as mock_help:
            execute_command("help", [])
            mock_help.assert_called_once()

    def test_execute_exit_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test routing 'exit' command to exit_app function."""
        with patch("todo.cli.commands.exit_app") as mock_exit:
            execute_command("exit", [])
            mock_exit.assert_called_once()

    def test_execute_unknown_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test unknown command prints error message."""
        execute_command("unknown", [])
        captured = capsys.readouterr()
        assert "Error: Unknown command 'unknown'" in captured.out
        assert "Type 'help' for available commands" in captured.out

    def test_execute_none_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test None command does nothing."""
        # Should not raise any exceptions
        execute_command(None, [])
        captured = capsys.readouterr()
        assert captured.out == ""


class TestRunOneShotMode:
    """Test run_one_shot_mode() function."""

    def test_run_one_shot_add_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test one-shot mode with 'add' command."""
        with patch("todo.cli.commands.add_command") as mock_add:
            run_one_shot_mode(["add", "Test Task"])
            mock_add.assert_called_once_with(["Test Task"])

    def test_run_one_shot_list_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test one-shot mode with 'list' command."""
        with patch("todo.cli.commands.list_command") as mock_list:
            run_one_shot_mode(["list"])
            mock_list.assert_called_once_with([])

    def test_run_one_shot_complete_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test one-shot mode with 'complete' command."""
        with patch("todo.cli.commands.complete_command") as mock_complete:
            run_one_shot_mode(["complete", "1"])
            mock_complete.assert_called_once_with(["1"])

    def test_run_one_shot_help_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test one-shot mode with 'help' command."""
        with patch("todo.cli.commands.help") as mock_help:
            run_one_shot_mode(["help"])
            mock_help.assert_called_once()

    def test_run_one_shot_update_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test one-shot mode with 'update' command."""
        with patch("todo.cli.commands.update_command") as mock_update:
            run_one_shot_mode(["update", "1", "title", "New Title"])
            mock_update.assert_called_once_with(["1", "title", "New Title"])

    def test_run_one_shot_delete_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test one-shot mode with 'delete' command."""
        with patch("todo.cli.commands.delete_command") as mock_delete:
            run_one_shot_mode(["delete", "1"])
            mock_delete.assert_called_once_with(["1"])
