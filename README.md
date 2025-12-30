# Todo Console Application

A command-line todo application built with Python 3.13+ using argparse and in-memory storage.

## Features

- Add tasks with title and optional description
- List tasks with status (Pending/Complete)
- Update task title or description
- Delete tasks
- Toggle task status (complete/incomplete)
- Interactive REPL mode and one-shot command mode

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd todo-app
uv venv
source .venv/bin/activate

# Run interactive mode
python -m todo.cli.main

# Or one-shot commands
python -m todo.cli.main add "Buy groceries"
python -m todo.cli.main list
python -m todo.cli.main complete 1
```

## Commands

| Command | Description |
|---------|-------------|
| `add "<title>" ["<description>"]` | Create a new task |
| `list` | Display all tasks |
| `update <id> title "<title>"` | Update task title |
| `update <id> description "<desc>"` | Update task description |
| `delete <id>` | Delete a task |
| `complete <id>` | Toggle task status |
| `help` | Show help message |
| `exit` | Quit application |

## Installation

```bash
# Install dependencies
uv pip install -e .

# Or with dev dependencies
uv pip install -e ".[dev]"
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Architecture

```
src/
├── models/task.py          # Status enum, Task dataclass
├── services/task_service.py # CRUD operations
└── cli/
    ├── commands.py         # Command handlers
    └── main.py             # argparse entry point
```

## Important Notes

- Tasks are stored in-memory only (lost on exit)
- Deleted task IDs are never reused
- Python 3.13+ required
