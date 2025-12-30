# Quickstart: Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-30
**Status**: Final

## Overview

This guide provides step-by-step instructions for setting up, running, and testing the todo console application. The application is a command-line interface for managing tasks in-memory.

---

## Prerequisites

- **Python 3.13+** installed ([download](https://www.python.org/downloads/))
- **uv** package manager installed ([installation guide](https://docs.astral.sh/uv/getting-started/installation))
- **Git** for version control ([installation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))

---

## Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd todo-app
git checkout 001-todo-console-app
```

### Step 2: Initialize Project with uv

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Verify Installation

```bash
python --version  # Should be Python 3.13+
uv --version      # Should show uv version
```

---

## Running the Application

### Interactive Mode (Default)

Launch the application to enter interactive loop:

```bash
python -m todo.cli.main
```

Or using uv directly:

```bash
uv run python -m todo.cli.main
```

**What to expect**:
- Prompt: `todo> `
- Enter commands one at a time
- Type `help` for available commands
- Type `exit` or `quit` to quit

**Interactive Session Example**:

```text
$ python -m todo.cli.main
Todo CLI - In-Memory Task Management

NOTE: Tasks are stored in memory only and will be lost when you exit.
For persistent storage, see Phase 2 documentation.

Type 'help' for available commands or 'exit' to quit.

todo> add "Buy groceries"
Task created with ID 1

todo> add "Write documentation" "Complete spec.md, plan.md, and tasks.md"
Task created with ID 2

todo> list
ID  Status     Title
--  --------    -----
1   Pending     Buy groceries
2   Pending     Write documentation

todo> complete 1
Task 1 marked as Complete

todo> list
ID  Status     Title
--  --------    -----
1   Complete     Buy groceries
2   Pending     Write documentation

todo> update 2 description "Complete spec.md, plan.md, tasks.md, and data-model.md"
Task 2 updated successfully

todo> delete 1
Task 1 deleted successfully

todo> list
ID  Status     Title
--  --------    -----
2   Pending     Write documentation

todo> exit
Goodbye!
```

### One-Shot Mode (Scripting)

Execute single command and exit:

```bash
# Add a task
python -m todo.cli.main add "Buy groceries"
# Output: Task created with ID 1

# List tasks
python -m todo.cli.main list
# Output: Table of tasks

# Complete task
python -m todo.cli.main complete 1
# Output: Task 1 marked as Complete
```

**Shell Script Example**:

```bash
#!/bin/bash
# Create initial tasks
python -m todo.cli.main add "Buy groceries" "Milk, eggs, bread, cheese"
python -m todo.cli.main add "Write documentation" "Complete spec.md and plan.md"
python -m todo.cli.main add "Call dentist"

# Mark first task complete
python -m todo.cli.main complete 1

# Show final list
python -m todo.cli.main list
```

---

## Command Reference

### add - Create Task

**Interactive**:
```text
todo> add "<title>" ["<description>"]
```

**One-Shot**:
```bash
python -m todo.cli.main add "<title>" ["<description>"]
```

**Examples**:
```text
# Minimal task
add "Buy groceries"

# Task with description
add "Write documentation" "Complete spec.md, plan.md, and tasks.md"
```

### list - Display All Tasks

**Interactive**:
```text
todo> list
```

**One-Shot**:
```bash
python -m todo.cli.main list
```

**Output**: Table with ID, Status, Title columns

### update - Edit Task

**Interactive**:
```text
todo> update <id> title "<new_title>"
todo> update <id> description "<new_description>"
```

**One-Shot**:
```bash
python -m todo.cli.main update <id> title "<new_title>"
python -m todo.cli.main update <id> description "<new_description>"
```

**Examples**:
```text
update 1 title "Buy organic groceries"
update 2 description "Complete all phase 1 documents"
```

### delete - Remove Task

**Interactive**:
```text
todo> delete <id>
```

**One-Shot**:
```bash
python -m todo.cli.main delete <id>
```

**Example**:
```text
delete 1
```

### complete - Toggle Status

**Interactive**:
```text
todo> complete <id>
```

**One-Shot**:
```bash
python -m todo.cli.main complete <id>
```

**Example**:
```text
complete 1  # Marks task as Complete
complete 1  # Toggles back to Pending
```

### help - Show Help

**Interactive**:
```text
todo> help
```

**One-Shot**:
```bash
python -m todo.cli.main help
```

### exit - Quit Application

**Interactive only**:
```text
todo> exit
```

**Alternative**: Type `quit` or press `Ctrl+C`

---

## Common Workflows

### Workflow 1: Daily Task Management

```text
# Start day - add tasks
add "Review email"
add "Team standup"
add "Code review"
add "Write documentation" "Complete quickstart.md"

# Complete first task
complete 1

# Check progress
list

# Add new task discovered during day
add "Fix bug in task service"

# Wrap up - complete remaining
complete 2
complete 4

exit
```

### Workflow 2: Shell Scripting

Create `setup-tasks.sh`:

```bash
#!/bin/bash
python -m todo.cli.main add "Buy groceries" "Milk, eggs, bread"
python -m todo.cli.main add "Call dentist"
python -m todo.cli.main add "Pay bills"

# Immediately set reminders
python -m todo.cli.main list
```

Run script:
```bash
chmod +x setup-tasks.sh
./setup-tasks.sh
```

### Workflow 3: Editing and Refining

```text
# Create task with minimal info
add "Write documentation"

# Realize need for more detail
list  # Shows ID 1

# Update with description
update 1 description "Complete spec.md, plan.md, tasks.md, and quickstart.md"

# Refine title
update 1 title "Complete Phase 1 documentation"

list  # Verify changes
```

---

## Testing

### Run Unit Tests

```bash
uv run pytest tests/unit/
```

### Run Integration Tests

```bash
uv run pytest tests/integration/
```

### Run All Tests with Coverage

```bash
uv run pytest --cov=src --cov-report=html tests/
```

Open coverage report:
```bash
# Linux/mac
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'todo'"

**Cause**: Not running from correct directory or virtual environment not activated

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/mac
.venv\Scripts\activate       # Windows

# Run from repository root
python -m todo.cli.main
```

### Issue: "Python version too old"

**Cause**: Python < 3.13 installed

**Solution**:
```bash
# Check version
python --version

# Install Python 3.13+ from python.org
# Then recreate virtual environment
rm -rf .venv
uv venv
```

### Issue: "Task with ID 5 not found"

**Cause**: Task ID does not exist (may have been deleted or never created)

**Solution**:
- Run `list` command to see valid task IDs
- Note: IDs are NOT reused after deletion

### Issue: "uv: command not found"

**Cause**: uv not installed or not in PATH

**Solution**:
```bash
# Install uv (Linux/mac)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install uv (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

---

## Project Structure

```
todo-app/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py           # Task dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py   # Task CRUD operations
│   └── cli/
│       ├── __init__.py
│       ├── commands.py         # CLI command implementations
│       └── main.py           # Entry point with argparse
├── tests/
│   ├── unit/
│   │   ├── test_task.py
│   │   └── test_task_service.py
│   └── integration/
│       └── test_cli_e2e.py
├── specs/
│   └── 001-todo-console-app/
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md      # This file
│       └── contracts/
│           └── cli-commands.md
├── pyproject.toml
├── README.md
├── CLAUDE.md
└── AGENTS.md
```

---

## Next Steps

1. **Complete Phase 1**: Implement tasks.md using `/sp.tasks` command
2. **Run Implementation**: Follow task breakdown to build features
3. **Test Independently**: Validate each user story works standalone
4. **Phase 2 Planning**: Add web interface and persistent storage

---

## Getting Help

- **In-Application**: Type `help` at any `todo>` prompt
- **Documentation**: See `README.md` for project overview
- **Constitution**: `.specify/memory/constitution.md` for project principles
- **Spec**: `specs/001-todo-console-app/spec.md` for detailed requirements

---

## Important Notes

- **In-Memory Only**: Tasks are lost when application exits (per Phase 1 scope)
  - Persistence is planned for Phase 2
  - See `README.md` for roadmap
- **Single User**: No authentication or multi-user support in Phase 1
- **ID Non-Reuse**: Deleted task IDs are never reassigned (monotonic counter)
- **Performance**: Handles up to 10,000 tasks with list operations under 1 second
