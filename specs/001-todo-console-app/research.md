# Research: Todo In-Memory Console Application

**Feature**: 001-todo-console-app
**Date**: 2025-12-30
**Status**: Complete

## CLI Framework Decision

**Decision**: Use Python's built-in `argparse` module for command-line argument parsing and `sys.stdin` for interactive mode

**Rationale**:
- Zero external dependencies required (simplifies setup and reduces attack surface)
- `argparse` is stable, well-documented, and part of Python standard library
- Supports subcommands (add, list, update, delete, complete) naturally
- Automatic help generation (`--help`) out of the box
- Constitution requires simplicity - `argparse` is the simplest valid solution

**Alternatives Considered**:
1. **click**: Popular third-party CLI library
   - Rejected: Introduces external dependency without clear benefit
   - Constitution Principle VII (Simplicity) violated
2. **cmd**: Python standard library command framework
   - Rejected: Overkill for simple CLI; designed for REPL interfaces not command-based CLIs
   - Verbose and less intuitive for subcommand patterns
3. **typer**: Modern type-based CLI library
   - Rejected: Third-party dependency, experimental (<1.0)
   - Constitution explicitly forbids experimental libraries (<1.0 or <100 stars)

**References**:
- Python argparse documentation: https://docs.python.org/3/library/argparse.html
- Constitution Principle VII: "Simplest valid solution is always preferred"

---

## Data Model Decision

**Decision**: Use Python `dataclasses` for Task entity

**Rationale**:
- Built-in since Python 3.7 (well-stable in 3.13+)
- Automatic `__init__`, `__repr__`, `__eq__` generation
- Type hints supported natively
- Immutability can be enforced with `frozen=True` if needed
- Cleaner than namedtuple for mutable entities with optional fields
- Zero dependencies

**Alternatives Considered**:
1. **namedtuple**: Built-in immutable data structure
   - Rejected: Not mutable; requires cumbersome replacement pattern for updates
   - Type hints less natural with optional fields
2. **Pydantic**: Validation library with BaseModel
   - Rejected: Third-party dependency, unnecessary for MVP
   - Validation can be handled in service layer
3. **Plain class with __init__**
   - Rejected: Verbose; manual implementation of __repr__, __eq__ etc.
   - More boilerplate code to maintain

**References**:
- Python dataclasses documentation: https://docs.python.org/3/library/dataclasses.html
- FR-001, FR-002 (task with mandatory title, optional description)

---

## Storage Decision

**Decision**: In-memory storage using Python `dict` with integer keys mapping to `Task` objects

**Rationale**:
- Simplest valid solution (Constitution Principle VII)
- O(1) lookup by ID (fast)
- Natural mapping: `tasks: dict[int, Task]`
- No persistence required per Phase 1 scope
- Easy to test (no file system or database interactions)

**Implementation**:
```python
tasks: dict[int, Task] = {}
next_id: int = 1
```

**Alternatives Considered**:
1. **List with index-based access**
   - Rejected: O(n) lookup by ID; poor user experience with 1000+ tasks
   - Violates SC-004 (list 1000 tasks in under 1 second)
2. **File-based persistence (JSON)**
   - Rejected: Out of scope for Phase 1 (explicit in spec.md §Out of Scope)
   - Persistence planned for Phase 2
3. **SQLite database**
   - Rejected: Overkill for MVP; violates simplicity principle
   - Adds complexity without business value in Phase 1

**References**:
- Spec.md §Out of Scope: "Persistent storage (saving tasks to file or database)"
- Constitution Performance Standards: p95 < 200ms for CLI operations

---

## Task ID Generation Strategy

**Decision**: Monotonically increasing integer counter starting at 1, never reused after deletion

**Rationale**:
- Matches spec requirement FR-003: "unique numeric ID... starting from 1, incrementing sequentially"
- User Story 4 acceptance scenario: "new task receives a fresh ID (IDs should not be reused)"
- Simple implementation: `next_id += 1` after each create
- Avoids confusion (user can't mistake new task for deleted one)

**Implementation**:
```python
def create_task(title: str, description: Optional[str]) -> Task:
    task_id = next_id
    next_id += 1
    tasks[task_id] = Task(id=task_id, title=title, description=description, status="Pending")
    return task_id
```

**Alternatives Considered**:
1. **UUIDs**: Universally unique identifiers
   - Rejected: Verbose to type in CLI (user experience pain point)
   - Spec explicitly requires "numeric ID"
2. **Reuse gaps**: Fill deleted IDs from available pool
   - Rejected: Spec acceptance scenario explicitly forbids reuse
   - Additional complexity without benefit

**References**:
- FR-003: System MUST assign a unique numeric ID to each task automatically
- FR-012: System MUST validate that task IDs exist before performing operations
- User Story 4, Acceptance Scenario 3

---

## CLI Interface Pattern

**Decision**: Support both interactive loop and one-shot commands for maximum flexibility

**Rationale**:
- Interactive mode: Better for beginners and multi-step workflows
- One-shot mode: Enables shell scripting and power user workflows
- Spec FR-015: "provide a command-line interface that runs in a loop OR accepts commands via CLI arguments"
- "OR" interpreted as "both" to support both usage patterns
- Minimal complexity to implement both modes

**Implementation Approach**:
- Default: Interactive loop that prompts for commands
- Command-line arguments: Execute single command and exit (e.g., `todo-cli add "Buy groceries"`)
- Shared command parsing logic between modes

**Alternatives Considered**:
1. **Interactive loop only**
   - Rejected: Limits automation and scripting use cases
   - Risk 2 mitigation requires considering both patterns
2. **One-shot commands only**
   - Rejected: Poor user experience for beginners
   - Violates SC-005 (95% of users succeed on first attempt)

**References**:
- FR-015: System MUST provide CLI via loop OR CLI arguments
- Risk 2 mitigation: "Consider implementing both interactive loop AND CLI arguments"

---

## Status Representation

**Decision**: Enum-based status using Python `Enum` class

**Rationale**:
- Type-safe (compilation-time checking of valid values)
- Readable in code (e.g., `Status.PENDING`, `Status.COMPLETE`)
- Easy to extend (e.g., `Status.IN_PROGRESS` in future phases)
- Matches spec: "either 'Pending' or 'Complete'"

**Implementation**:
```python
from enum import Enum

class Status(Enum):
    PENDING = "Pending"
    COMPLETE = "Complete"
```

**Alternatives Considered**:
1. **String literals**: "Pending", "Complete"
   - Rejected: Prone to typos ("pending" vs "Pending")
   - No compile-time safety
2. **Integer constants**: STATUS_PENDING = 0, STATUS_COMPLETE = 1
   - Rejected: Less readable; requires mapping to display strings

**References**:
- FR-004, FR-006, FR-007: Status must be "Pending" or "Complete"

---

## Summary of Decisions

| Decision | Technology | Rationale |
|----------|-------------|------------|
| CLI Framework | argparse | Zero dependencies, standard library, constitutional simplicity |
| Data Model | dataclasses | Type-safe, auto-generated methods, zero dependencies |
| Storage | In-memory dict | O(1) lookup, simple, meets spec scope |
| ID Strategy | Monotonic counter | Matches spec, no reuse, simple implementation |
| CLI Pattern | Interactive + one-shot | Maximum flexibility, addresses both user personas |
| Status Type | Enum | Type-safe, readable, extensible |

**Constitution Compliance**: ✅ All decisions align with Constitution Principle VII (Simplicity) and Technology Constraints (Python 3.13+, standard library preferred)

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts/, quickstart.md)
