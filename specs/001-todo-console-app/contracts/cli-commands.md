# CLI Command Contracts: Todo Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-30
**Status**: Final

## Overview

This document defines the command-line interface contracts for the todo console application. Each command includes:
- Command name and invocation pattern
- Required and optional arguments
- Expected output format
- Error conditions
- Reference to user stories and functional requirements

---

## Command Execution Modes

### Mode 1: Interactive Loop (Default)

**Invocation**: `todo-cli` (no arguments)

**Behavior**:
- Application enters REPL (Read-Eval-Print Loop)
- Displays prompt: `todo> `
- Accepts commands until user types `exit` or `quit`
- Shows help on `help` or invalid command

**Exit**: `exit`, `quit`, or `Ctrl+C`

### Mode 2: One-Shot Command

**Invocation**: `todo-cli <command> [args...]`

**Behavior**:
- Executes single command with provided arguments
- Displays output to stdout
- Exits immediately after completion
- Useful for shell scripts and automation

**Example**: `todo-cli add "Buy groceries" "Milk, eggs, bread"`

---

## Commands

### Command: add

**Create a new task with a mandatory title and optional description**

**Interactive Usage**:
```text
todo> add "Buy groceries"
Task created with ID 1

todo> add "Write documentation" "Complete spec.md, plan.md, and tasks.md"
Task created with ID 2
```

**One-Shot Usage**:
```bash
todo-cli add "Buy groceries"
# Output: Task created with ID 1

todo-cli add "Write documentation" "Complete spec.md, plan.md, and tasks.md"
# Output: Task created with ID 2
```

**Arguments**:
- `title` (required, string): Task title (non-empty)
- `description` (optional, string): Additional details about task

**Success Output**:
```
Task created with ID <id>
```

**Error Conditions**:
- Empty title:
  ```
  Error: Title cannot be empty
  Usage: add "<title>" ["<description>"]
  ```
- Title exceeds 500 characters:
  ```
  Error: Title exceeds maximum length of 500 characters
  ```

**References**: FR-001, FR-002, FR-003, FR-004; User Story 1

---

### Command: list

**Display all tasks with their ID, Status, and Title**

**Interactive Usage**:
```text
todo> list
ID  Status     Title
--  --------    -----
1   Pending     Buy groceries
2   Pending     Write documentation
3   Complete     Call dentist
```

**One-Shot Usage**:
```bash
todo-cli list
# Output: Same table format as interactive mode
```

**Arguments**:
- None

**Success Output**:
- Table format with headers: `ID`, `Status`, `Title`
- Tasks sorted by ID (ascending)
- Column alignment for readability
- If no tasks exist:
  ```
  No tasks found. Add a task to get started.
  ```

**Description Display**: Description is NOT shown in list view (per US1 acceptance scenario 3: "description should be viewable but not necessarily in list view"). Future enhancement could show description via `show` command.

**References**: FR-005; User Story 1

---

### Command: update

**Edit the title or description of an existing task by its ID**

**Interactive Usage**:
```text
todo> update 1 title "Buy organic groceries"
Task 1 updated successfully

todo> update 2 description "Complete spec.md, plan.md, tasks.md, and data-model.md"
Task 2 updated successfully
```

**One-Shot Usage**:
```bash
todo-cli update 1 title "Buy organic groceries"
# Output: Task 1 updated successfully

todo-cli update 2 description "Complete spec.md, plan.md, tasks.md, and data-model.md"
# Output: Task 2 updated successfully
```

**Arguments**:
- `id` (required, int): Task ID to update
- `title` (optional, string): New title for task
- `description` (optional, string): New description for task

**Constraints**:
- At least one of `title` or `description` must be provided
- Cannot update both in single command (two separate commands required)

**Success Output**:
```
Task <id> updated successfully
```

**Error Conditions**:
- Task ID does not exist:
  ```
  Error: Task with ID 5 not found
  ```
- Neither title nor description provided:
  ```
  Error: Must provide either 'title' or 'description' to update
  Usage: update <id> title "<new_title>" | description "<new_description>"
  ```
- Empty new title:
  ```
  Error: Title cannot be empty
  ```

**References**: FR-008, FR-009, FR-012, FR-013; User Story 3

---

### Command: delete

**Remove a task from memory using its unique ID**

**Interactive Usage**:
```text
todo> delete 1
Task 1 deleted successfully
```

**One-Shot Usage**:
```bash
todo-cli delete 1
# Output: Task 1 deleted successfully
```

**Arguments**:
- `id` (required, int): Task ID to delete

**Success Output**:
```
Task <id> deleted successfully
```

**Error Conditions**:
- Task ID does not exist:
  ```
  Error: Task with ID 5 not found
  ```
- Invalid ID format (non-integer):
  ```
  Error: Invalid task ID. Must be a number.
  ```

**Behavior**:
- Task is permanently removed from memory
- Task IDs are NOT reused (monotonic counter continues incrementing)

**References**: FR-010, FR-011, FR-012, FR-013; User Story 4

---

### Command: complete

**Toggle a task's status between "Pending" and "Complete"**

**Interactive Usage**:
```text
todo> complete 1
Task 1 marked as Complete

todo> complete 2
Task 2 marked as Complete

todo> complete 1
Task 1 marked as Pending
```

**One-Shot Usage**:
```bash
todo-cli complete 1
# Output: Task 1 marked as Complete

todo-cli complete 2
# Output: Task 2 marked as Complete
```

**Arguments**:
- `id` (required, int): Task ID to mark complete

**Success Output**:
- When marking pending task as complete:
  ```
  Task <id> marked as Complete
  ```
- When toggling back from complete:
  ```
  Task <id> marked as Pending
  ```

**Error Conditions**:
- Task ID does not exist:
  ```
  Error: Task with ID 5 not found
  ```
- Invalid ID format (non-integer):
  ```
  Error: Invalid task ID. Must be a number.
  ```

**Behavior**:
- Toggle logic: Pending → Complete → Pending → ...
- No separate "uncomplete" command needed

**References**: FR-006, FR-007, FR-012, FR-013; User Story 2

---

### Command: help

**Display usage information and available commands**

**Interactive Usage**:
```text
todo> help
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
  list
  complete 1
  delete 2

For more information, see README.md
```

**One-Shot Usage**:
```bash
todo-cli help
# Output: Same help text as interactive mode
```

**Arguments**:
- None

**Success Output**: Command listing with descriptions and examples

---

## Error Taxonomy

### Error Classification

| Error Type | Example | User Message |
|------------|-----------|---------------|
| Task Not Found | `complete 999` | `Error: Task with ID 999 not found` |
| Invalid Input | `delete abc` | `Error: Invalid task ID. Must be a number.` |
| Validation | `add ""` | `Error: Title cannot be empty` |
| Constraint | `update 3` | `Error: Must provide either 'title' or 'description' to update` |

**Requirements Coverage**:
- **FR-012**: System MUST validate that task IDs exist before performing operations ✅
- **FR-013**: System MUST display clear error messages for invalid operations ✅
- **User Story 2, Acceptance Scenario 3**: Clear error for non-existent IDs ✅
- **Edge Cases**: Empty title, invalid ID types ✅

---

## Output Formatting Standards

### Table Format (list command)

**Alignment Rules**:
- ID column: Right-aligned, width 3
- Status column: Left-aligned, width 10
- Title column: Left-aligned, remaining width

**Example**:
```text
  ID  Status     Title
----  --------    ------------------------------------
    1  Pending     Buy groceries
    2  Complete     Write documentation
    3  Pending     Call dentist about appointment
```

### Success Messages

- **Consistent format**: `<Entity> <id> <action> successfully`
- **Examples**:
  - `Task 1 created with ID 1` (add)
  - `Task 1 updated successfully` (update)
  - `Task 1 deleted successfully` (delete)
  - `Task 1 marked as Complete` (complete)

### Error Messages

- **Prefix**: `Error: `
- **Actionable**: Tell user what went wrong and how to fix
- **No stack traces** to user (logged internally per constitution)

---

## Performance Requirements

Per constitution performance standards and SC-004:

| Command | Target (p95) | Expected (typical) |
|---------|----------------|---------------------|
| `add` | < 200ms | < 1ms |
| `list` (1000 tasks) | < 1000ms | < 50ms |
| `update` | < 200ms | < 1ms |
| `delete` | < 200ms | < 1ms |
| `complete` | < 200ms | < 1ms |

**Validation**: Performance tests in `tests/integration/test_performance.py` (optional)

---

## References

- **Constitution**: `.specify/memory/constitution.md`
  - Error Handling & Observability
  - Performance Standards
- **Feature Spec**: `specs/001-todo-console-app/spec.md`
  - All functional requirements (FR-001 through FR-016)
  - User Stories 1-4 with acceptance scenarios
  - Edge Cases
- **Data Model**: `specs/001-todo-console-app/data-model.md`
  - Task entity definition
  - Status enum
  - Validation rules
