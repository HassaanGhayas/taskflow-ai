# Tasks: Todo In-Memory Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/cli-commands.md

**Tests**: Unit tests included for core logic per constitution 80% coverage requirement. Integration tests marked OPTIONAL.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python 3.13+ project with uv in pyproject.toml
- [ ] T003 [P] Create package initialization files: src/__init__.py, src/models/__init__.py, src/services/__init__.py, src/cli/__init__.py, tests/__init__.py, tests/unit/__init__.py, tests/integration/__init__.py
- [ ] T004 Configure uv for project development

**Checkpoint**: Project structure ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Status enum in src/models/task.py with PENDING and COMPLETE values
- [ ] T006 Create Task dataclass in src/models/task.py with frozen=True, id, title, description, status attributes in src/models/task.py (depends on T005)
- [ ] T007 [P] Implement in-memory storage (tasks: dict[int, Task], next_id: int) in src/services/task_service.py
- [ ] T008 [P] Implement TaskNotFoundError custom exception class in src/services/task_service.py
- [ ] T009 [P] Implement ValueError for invalid input (empty title, max length) in src/services/task_service.py
- [ ] T010 Implement create_task() function in src/services/task_service.py (depends on T006, T007, T008, T009)
- [ ] T011 Implement get_task() function in src/services/task_service.py (depends on T007, T008)
- [ ] T012 Implement list_tasks() function in src/services/task_service.py (depends on T007)
- [ ] T013 Implement update_task() function in src/services/task_service.py (depends on T006, T009, T011)
- [ ] T014 Implement delete_task() function in src/services/task_service.py (depends on T007, T011)
- [ ] T015 Implement toggle_task_status() function in src/services/task_service.py (depends on T006, T011)
- [ ] T016 [P] Implement command parser with argparse in src/cli/main.py with subcommands: add, list, update, delete, complete, help, exit
- [ ] T017 [P] Implement add command handler in src/cli/commands.py (depends on T010)
- [ ] T018 [P] Implement list command handler in src/cli/commands.py (depends on T012)
- [ ] T019 [P] Implement update command handler in src/cli/commands.py (depends on T013)
- [ ] T020 [P] Implement delete command handler in src/cli/commands.py (depends on T014)
- [ ] T021 [P] Implement complete command handler in src/cli/commands.py (depends on T015)
- [ ] T022 [P] Implement help command handler in src/cli/commands.py
- [ ] T023 [P] Implement exit command handler in src/cli/commands.py
- [ ] T024 [P] Implement interactive REPL loop in src/cli/main.py with prompt, command parsing, and graceful exit (depends on T016, T017, T018, T019, T020, T021, T022, T023)
- [ ] T025 Implement one-shot command mode in src/cli/main.py for shell scripting support (depends on T016)
- [ ] T026 Add entry point to pyproject.toml for `python -m todo.cli.main` (depends on T001)
- [ ] T027 Configure error logging infrastructure in src/cli/main.py per constitution observability standards

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add new tasks and see them listed so they can track what needs to be done

**Independent Test**: Launch app, add a task with title, view list to confirm task appears with ID and "Pending" status

### Unit Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T028 [P] [US1] Test Task dataclass creation in tests/unit/test_task.py
- [ ] T029 [P] [US1] Test Status enum values in tests/unit/test_task.py
- [ ] T030 [P] [US1] Test create_task() with valid title in tests/unit/test_task_service.py
- [ ] T031 [P] [US1] Test create_task() with empty title raises ValueError in tests/unit/test_task_service.py
- [ ] T032 [P] [US1] Test create_task() with title > 500 chars raises ValueError in tests/unit/test_task_service.py
- [ ] T033 [P] [US1] Test create_task() with optional description in tests/unit/test_task_service.py
- [ ] T034 [P] [US1] Test create_task() assigns unique ID in tests/unit/test_task_service.py
- [ ] T035 [P] [US1] Test create_task() initializes status to PENDING in tests/unit/test_task_service.py
- [ ] T036 [P] [US1] Test list_tasks() returns all tasks in tests/unit/test_task_service.py
- [ ] T037 [P] [US1] Test list_tasks() with empty storage returns empty list in tests/unit/test_task_service.py
- [ ] T038 [P] [US1] Test add command handler in tests/unit/test_commands.py (depends on T030, T031, T032, T033, T034, T035)

### Integration Tests for User Story 1 (OPTIONAL)

- [ ] T039 [US1] Integration test for add-and-list user journey in tests/integration/test_cli_e2e.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Mark Tasks as Complete (Priority: P2)

**Goal**: Enable users to mark tasks as complete so they can track progress and distinguish between pending and finished work

**Independent Test**: Create a task, mark it complete, verify status changes to "Complete" in task list

### Unit Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T040 [P] [US2] Test toggle_task_status() from Pending to Complete in tests/unit/test_task_service.py
- [ ] T041 [P] [US2] Test toggle_task_status() from Complete to Pending in tests/unit/test_task_service.py
- [ ] T042 [P] [US2] Test toggle_task_status() with non-existent ID raises TaskNotFoundError in tests/unit/test_task_service.py
- [ ] T043 [P] [US2] Test complete command handler in tests/unit/test_commands.py (depends on T040, T041, T042)

### Integration Tests for User Story 2 (OPTIONAL)

- [ ] T044 [US2] Integration test for complete-and-verify user journey in tests/integration/test_cli_e2e.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Enable users to edit task titles and descriptions so they can correct mistakes or add more information

**Independent Test**: Create a task, update its title or description, verify changes are reflected in task list

### Unit Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T045 [P] [US3] Test update_task() with title change in tests/unit/test_task_service.py
- [ ] T046 [P] [US3] Test update_task() with description change in tests/unit/test_task_service.py
- [ ] T047 [P] [US3] Test update_task() with both title and description in tests/unit/test_task_service.py
- [ ] T048 [P] [US3] Test update_task() with non-existent ID raises TaskNotFoundError in tests/unit/test_task_service.py
- [ ] T049 [P] [US3] Test update_task() with empty new title raises ValueError in tests/unit/test_task_service.py
- [ ] T050 [P] [US3] Test update_task() with title > 500 chars raises ValueError in tests/unit/test_task_service.py
- [ ] T051 [P] [US3] Test update command handler with title argument in tests/unit/test_commands.py (depends on T045, T048, T049, T050)
- [ ] T052 [P] [US3] Test update command handler with description argument in tests/unit/test_commands.py (depends on T046, T048)

### Integration Tests for User Story 3 (OPTIONAL)

- [ ] T053 [US3] Integration test for update-and-verify user journey in tests/integration/test_cli_e2e.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Enable users to remove tasks from their list so they can keep their task list clean and focused

**Independent Test**: Create a task, delete it, verify it no longer appears in task list

### Unit Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T054 [P] [US4] Test delete_task() removes task from storage in tests/unit/test_task_service.py
- [ ] T055 [P] [US4] Test delete_task() does NOT reuse deleted IDs in tests/unit/test_task_service.py
- [ ] T056 [P] [US4] Test delete_task() with non-existent ID raises TaskNotFoundError in tests/unit/test_task_service.py
- [ ] T057 [P] [US4] Test delete command handler in tests/unit/test_commands.py (depends on T054, T056)
- [ ] T058 [P] [US4] Test delete command handler with invalid ID type raises ValueError in tests/unit/test_commands.py

### Integration Tests for User Story 4 (OPTIONAL)

- [ ] T059 [US4] Integration test for delete-and-verify user journey in tests/integration/test_cli_e2e.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T060 [P] Update README.md with setup instructions and usage examples
- [ ] T061 [P] Add in-memory warning on application startup per Risk 3 mitigation
- [ ] T062 [P] Add help text with examples to help command in src/cli/commands.py
- [ ] T063 Run pytest with coverage report to validate 80% coverage target
- [ ] T064 Performance test: Verify list operation completes in under 1 second for 1000 tasks in tests/integration/test_performance.py (OPTIONAL)
- [ ] T065 Code review: Verify all type hints and docstrings are present per constitution
- [ ] T066 Run quickstart.md validation: Follow setup guide and verify application runs correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in priority order: US1 (P1) → US2 (P2) → US3 (P3) → US4 (P4)
  - User stories can also proceed in parallel (if staffed) after Foundational phase complete
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for list command but can implement complete logic independently
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 for task service
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1 for task service

### Within Each User Story

- Unit tests MUST be written and FAIL before implementation (per Constitution Principle IV)
- Models (T005, T006) before services (T007-T015)
- Services (T007-T015) before CLI handlers (T017-T025)
- CLI handlers before integration (T024, T025, integration tests)
- Story complete before moving to next priority

### Parallel Opportunities

**Within Foundational Phase (Phase 2)**:
- T007, T008, T009 can run in parallel (storage setup)
- T016, T022, T023 can run in parallel (command parsing setup)
- T017, T018, T019, T020, T021 can run in parallel (command handlers)

**Within User Story 1 (Phase 3)**:
- All unit tests T028-T037 can run in parallel (different test files)
- T028, T029 (model tests) can run in parallel with T030-T037 (service tests)

**Within User Story 2 (Phase 4)**:
- T040, T041, T042 (service tests) can run in parallel

**Within User Story 3 (Phase 5)**:
- T045-T050 (service tests) can run in parallel
- T051, T052 (command tests) can run in parallel

**Within User Story 4 (Phase 6)**:
- T054, T055, T056 (service tests) can run in parallel
- T057, T058 (command tests) can run in parallel

**Within Polish Phase (Phase 7)**:
- T060, T061, T062 can run in parallel (documentation)
- T063, T065, T066 can run in parallel (quality gates)

**Across User Stories**:
- Once Foundational (Phase 2) completes, all user stories can start in parallel (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for User Story 1 together:
Task: "Test Task dataclass creation in tests/unit/test_task.py"
Task: "Test Status enum values in tests/unit/test_task.py"
Task: "Test create_task() with valid title in tests/unit/test_task_service.py"
Task: "Test create_task() with empty title raises ValueError in tests/unit/test_task_service.py"
Task: "Test create_task() with title > 500 chars raises ValueError in tests/unit/test_task_service.py"
Task: "Test create_task() with optional description in tests/unit/test_task_service.py"
Task: "Test create_task() assigns unique ID in tests/unit/test_task_service.py"
Task: "Test create_task() initializes status to PENDING in tests/unit/test_task_service.py"
Task: "Test list_tasks() returns all tasks in tests/unit/test_task_service.py"
Task: "Test list_tasks() with empty storage returns empty list in tests/unit/test_task_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T027) - CRITICAL
3. Complete Phase 3: User Story 1 (T028-T038)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**Result**: Working add and list commands - minimum viable product

### Incremental Delivery

1. Complete Setup (T001-T004) + Foundational (T005-T027) → Foundation ready
2. Add User Story 1 (T028-T038) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (T040-T043) → Test independently → Deploy/Demo
4. Add User Story 3 (T045-T052) → Test independently → Deploy/Demo
5. Add User Story 4 (T054-T058) → Test independently → Deploy/Demo
6. Complete Polish (T060-T066) → Final release
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (T001-T004) + Foundational (T005-T027) together
2. Once Foundational is done:
   - Developer A: User Story 1 (T028-T038)
   - Developer B: User Story 2 (T040-T043)
   - Developer C: User Story 3 (T045-T052)
   - Developer D: User Story 4 (T054-T058)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US4)
- Each user story should be independently completable and testable
- Verify tests fail before implementing (per Constitution Principle IV)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

| Phase | Task Count | Description |
|--------|-------------|-------------|
| Phase 1: Setup | 4 | Project initialization |
| Phase 2: Foundational | 23 | Core infrastructure (blocks all stories) |
| Phase 3: User Story 1 (P1) | 12 | Add and list functionality |
| Phase 4: User Story 2 (P2) | 5 | Mark complete functionality |
| Phase 5: User Story 3 (P3) | 9 | Update task functionality |
| Phase 6: User Story 4 (P4) | 6 | Delete task functionality |
| Phase 7: Polish | 7 | Documentation, quality gates |
| **TOTAL** | **66** | **All tasks** |

---

## Suggested MVP Scope

**MVP = User Story 1 only** (T001-T038, 32 tasks)

This provides:
- Add tasks with mandatory title and optional description
- List all tasks with ID, Status, Title
- Unique numeric IDs starting from 1
- Default "Pending" status for new tasks
- Basic error handling

**Value**: Users can create and track tasks - core value proposition delivered

**Next**: After validating MVP, add US2 (complete), US3 (update), US4 (delete) incrementally

---

## Independent Test Criteria

### User Story 1
Launch app, run:
```bash
todo> add "Buy groceries"
todo> add "Write documentation"
todo> list
```
**Success**: Both tasks appear with IDs 1, 2, status "Pending", and titles match

### User Story 2
After US1 works, run:
```bash
todo> complete 1
todo> list
```
**Success**: Task 1 status changed to "Complete"

### User Story 3
After US1 works, run:
```bash
todo> update 2 title "Complete Phase 1 documentation"
todo> list
```
**Success**: Task 2 title updated

### User Story 4
After US1 works, run:
```bash
todo> delete 1
todo> add "New task"
todo> list
```
**Success**: Task 1 removed, new task has ID 3 (not reused)

---

## Parallel Opportunities Summary

| Phase | Parallel Tasks | Notes |
|-------|----------------|-------|
| Phase 2 (Foundational) | T007, T008, T009 (storage init) | Independent files |
| Phase 2 (Foundational) | T017, T018, T019, T020, T021 (handlers) | Independent commands |
| Phase 3 (US1) | T028, T029 (model tests) | Test different aspects |
| Phase 3 (US1) | T030-T037 (service tests) | 8 parallel tests |
| Phase 4 (US2) | T040, T041, T042 | Service layer tests |
| Phase 5 (US3) | T045-T050 | 6 service tests |
| Phase 5 (US3) | T051, T052 | 2 command tests |
| Phase 6 (US4) | T054, T055, T056 | 3 service tests |
| Phase 6 (US4) | T057, T058 | 2 command tests |
| Phase 7 (Polish) | T060, T061, T062 | Documentation tasks |

**Maximum Parallelization**: After Foundational phase, 4 developers can work on 4 user stories simultaneously.
