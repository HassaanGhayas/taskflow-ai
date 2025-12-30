---
description: "Task list for SpecifyPlus MCP Server implementation"
---

# Tasks: SpecifyPlus MCP Server

**Input**: Design documents from `/specs/001-mcp-server-prompts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are OPTIONAL - not explicitly requested in the feature specification, so test tasks are included but marked as optional.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **MCP Server**: `specifyplus-mcp-server/src/`, `specifyplus-mcp-server/tests/`
- Paths are relative to repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create specifyplus-mcp-server/ directory structure with src/ and tests/ subdirectories
- [X] T002 Initialize pyproject.toml with project metadata, Python 3.10+ requirement, and build system (hatchling)
- [X] T003 [P] Add core dependencies to pyproject.toml: fastmcp>=0.1.0, pydantic>=2.0, pyyaml>=6.0, watchdog>=3.0, python-frontmatter>=1.0
- [X] T004 [P] Add dev dependencies to pyproject.toml: pytest>=7.0, pytest-asyncio>=0.21, pytest-cov>=4.0, black>=23.0, ruff>=0.1.0, mypy>=1.0
- [X] T005 [P] Configure pytest settings in pyproject.toml (testpaths, asyncio_mode=auto)
- [X] T006 [P] Configure coverage settings in pyproject.toml (source=src, fail_under=80)
- [X] T007 [P] Configure black and ruff formatters in pyproject.toml
- [X] T008 [P] Create .env.example with COMMANDS_DIR, LOG_LEVEL, MCP_TRANSPORT, MCP_PORT
- [X] T009 [P] Create .gitignore for Python project (__pycache__, *.pyc, .env, .coverage, dist/, build/)
- [X] T010 [P] Create specifyplus-mcp-server/src/__init__.py with package metadata
- [X] T011 [P] Create specifyplus-mcp-server/tests/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T012 [P] Create exceptions.py with SpecifyPlusMCPError base class in specifyplus-mcp-server/src/exceptions.py
- [X] T013 [P] Add DirectoryNotFoundError exception for FR-001a in specifyplus-mcp-server/src/exceptions.py
- [X] T014 [P] Add CommandParseError exception for FR-012 in specifyplus-mcp-server/src/exceptions.py
- [X] T015 [P] Add InputTooLargeError exception for FR-004a in specifyplus-mcp-server/src/exceptions.py
- [X] T016 [P] Add CommandNotFoundError exception in specifyplus-mcp-server/src/exceptions.py
- [X] T017 [P] Create models.py with HandoffLink Pydantic model (label, agent, prompt, send fields) in specifyplus-mcp-server/src/models.py
- [X] T018 [P] Add CommandMetadata Pydantic model (description, handoffs list) in specifyplus-mcp-server/src/models.py
- [X] T019 [P] Add CommandDefinition Pydantic model (name, file_path, metadata, content, has_arguments, file_size, last_modified) with name validator in specifyplus-mcp-server/src/models.py
- [X] T020 [P] Add PromptArguments Pydantic model with 100KB size validator in specifyplus-mcp-server/src/models.py
- [X] T021 [P] Create validators.py with validate_command_name, validate_yaml_frontmatter, validate_file_size functions in specifyplus-mcp-server/src/validators.py
- [X] T022 [P] Write unit tests for all Pydantic models in specifyplus-mcp-server/tests/test_models.py
- [X] T023 [P] Write unit tests for all custom exceptions in specifyplus-mcp-server/tests/test_exceptions.py
- [X] T024 [P] Create test fixtures directory structure: tests/fixtures/valid/, tests/fixtures/malformed/, tests/fixtures/edge_cases/
- [X] T025 [P] Create sample valid command file in tests/fixtures/valid/sp.test.md with YAML frontmatter and $ARGUMENTS
- [X] T026 [P] Create malformed YAML sample in tests/fixtures/malformed/invalid_yaml.md
- [X] T027 [P] Create edge case samples (no frontmatter, no $ARGUMENTS, large file) in tests/fixtures/edge_cases/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Connect MCP Server to IDE (Priority: P1) 🎯 MVP

**Goal**: Enable IDE connection, command discovery, and listing of all 13 SpecifyPlus commands

**Independent Test**: Configure MCP server in IDE settings, verify connection, list available prompts

### Implementation for User Story 1

- [X] T028 [P] [US1] Create CommandLoader class with __init__ method that validates .claude/commands/ directory exists (raises DirectoryNotFoundError per FR-001a) in specifyplus-mcp-server/src/loader.py
- [X] T029 [P] [US1] Implement discover_commands() method to glob *.md files (FR-001) in specifyplus-mcp-server/src/loader.py
- [X] T030 [US1] Implement parse_command_file() method to parse YAML frontmatter and markdown content (FR-002) in specifyplus-mcp-server/src/loader.py
- [X] T031 [US1] Add error handling to parse_command_file() to skip malformed files with warnings (FR-012) in specifyplus-mcp-server/src/loader.py
- [X] T032 [US1] Implement load_all_commands() method to batch load and return Dict[str, CommandDefinition] in specifyplus-mcp-server/src/loader.py
- [X] T033 [P] [US1] Create CommandRegistry class with thread-safe RLock in specifyplus-mcp-server/src/registry.py
- [X] T034 [P] [US1] Implement register(), get(), list_commands(), update_all(), clear(), count() methods in specifyplus-mcp-server/src/registry.py
- [X] T035 [US1] Create FastMCP server instance with name "specifyplus-commands" in specifyplus-mcp-server/src/server.py
- [X] T036 [US1] Implement on_startup() hook to initialize CommandLoader, load commands into registry in specifyplus-mcp-server/src/server.py
- [X] T037 [US1] Implement dynamic prompt registration that reads from registry and creates MCP prompts with name, description, arguments metadata (FR-003, FR-009) in specifyplus-mcp-server/src/server.py
- [X] T038 [US1] Configure FastMCP to declare prompts capability with listChanged=true in specifyplus-mcp-server/src/server.py
- [X] T039 [US1] Implement stdio transport support (default) with mcp.run() in specifyplus-mcp-server/src/server.py (FR-011)
- [X] T040 [P] [US1] Write unit tests for CommandLoader (directory validation, file discovery, YAML parsing, malformed handling) in specifyplus-mcp-server/tests/test_loader.py
- [X] T041 [P] [US1] Write unit tests for CommandRegistry (CRUD operations, thread safety, atomic updates) in specifyplus-mcp-server/tests/test_registry.py

**Checkpoint**: At this point, User Story 1 should be fully functional - MCP server starts, loads commands, and can be listed in an IDE

---

## Phase 4: User Story 2 - Execute Commands with User Input (Priority: P2)

**Goal**: Enable command execution with user input, template substitution, and security validation

**Independent Test**: Execute /sp.specify with input "Add auth", verify prompt includes "Add auth" in $ARGUMENTS section

### Implementation for User Story 2

- [X] T042 [P] [US2] Create PromptHandler class with __init__ accepting CommandRegistry in specifyplus-mcp-server/src/handler.py
- [X] T043 [P] [US2] Implement sanitize_input() method to escape $ARGUMENTS and ${...} patterns using regex (FR-005a) in specifyplus-mcp-server/src/handler.py
- [X] T044 [US2] Implement process_prompt() method with input size validation (FR-004a: 100KB limit) in specifyplus-mcp-server/src/handler.py
- [X] T045 [US2] Add template sanitization call in process_prompt() before substitution (FR-005a) in specifyplus-mcp-server/src/handler.py
- [X] T046 [US2] Implement $ARGUMENTS placeholder substitution in process_prompt() (FR-005) in specifyplus-mcp-server/src/handler.py
- [X] T047 [US2] Handle commands without $ARGUMENTS (return template as-is per FR-008) in specifyplus-mcp-server/src/handler.py
- [X] T048 [US2] Integrate PromptHandler into server.py on_startup() hook in specifyplus-mcp-server/src/server.py
- [X] T049 [US2] Implement get_prompt() function that calls PromptHandler.process_prompt() and returns message list with role="user" in specifyplus-mcp-server/src/server.py
- [X] T050 [US2] Connect get_prompt() to FastMCP prompt invocation handler in specifyplus-mcp-server/src/server.py
- [X] T051 [P] [US2] Write unit tests for PromptHandler ($ARGUMENTS substitution, sanitization, size limits, no-arguments case) in specifyplus-mcp-server/tests/test_handler.py
- [X] T052 [P] [US2] Write integration test for end-to-end prompt execution with user input in specifyplus-mcp-server/tests/test_integration.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - commands can be listed and executed with custom input

---

## Phase 5: User Story 3 - Browse Command Documentation (Priority: P3)

**Goal**: Expose comprehensive command metadata including descriptions, handoffs, and parameter requirements

**Independent Test**: Request /sp.specify metadata, verify description and handoff links are displayed

### Implementation for User Story 2

- [X] T053 [US3] Enhance prompt registration to include handoff metadata from CommandMetadata.handoffs (FR-009) in specifyplus-mcp-server/src/server.py
- [X] T054 [US3] Add argument schema details to prompt registration (name="text", description, required=False/True based on has_arguments) in specifyplus-mcp-server/src/server.py
- [X] T055 [US3] Ensure prompt descriptions from CommandMetadata.description are exposed in prompts/list response in specifyplus-mcp-server/src/server.py
- [X] T056 [P] [US3] Write integration test verifying prompts/list returns all command metadata (name, description, arguments, handoffs) in specifyplus-mcp-server/tests/test_integration.py
- [X] T057 [P] [US3] Write integration test verifying handoff links include label, agent, prompt fields in specifyplus-mcp-server/tests/test_integration.py

**Checkpoint**: All user stories should now be independently functional - full MCP server capabilities operational

---

## Phase 6: Hot Reload & File Watching (Cross-Cutting Enhancement)

**Purpose**: Enable live updates without server restart (FR-013, SC-007)

- [X] T058 [P] Create FileWatcher class with __init__ accepting commands_dir and reload_callback in specifyplus-mcp-server/src/watcher.py
- [X] T059 [P] Create CommandFileHandler class extending FileSystemEventHandler in specifyplus-mcp-server/src/watcher.py
- [X] T060 Implement on_modified(), on_created(), on_deleted() event handlers that trigger reload for *.md files in specifyplus-mcp-server/src/watcher.py
- [X] T061 Add debouncing logic to _trigger_reload() to prevent rapid consecutive reloads in specifyplus-mcp-server/src/watcher.py
- [X] T062 Implement start() and stop() methods to manage Watchdog Observer lifecycle in specifyplus-mcp-server/src/watcher.py
- [X] T063 Create reload_commands() function in server.py that calls CommandLoader.load_all_commands() and CommandRegistry.update_all() in specifyplus-mcp-server/src/server.py
- [X] T064 Initialize FileWatcher in on_startup() hook and call start() in specifyplus-mcp-server/src/server.py
- [X] T065 Stop FileWatcher in on_shutdown() hook in specifyplus-mcp-server/src/server.py
- [X] T066 [P] Write unit tests for FileWatcher (change detection, reload triggering, debouncing) in specifyplus-mcp-server/tests/test_watcher.py
- [X] T067 [P] Write integration test for hot reload workflow (modify file, verify reload <5s per SC-007) in specifyplus-mcp-server/tests/test_integration.py

---

## Phase 7: SSE Transport Support (Cross-Cutting Enhancement)

**Purpose**: Enable remote MCP server connections via SSE protocol (FR-011)

- [X] T068 [P] Add SSE transport configuration option to server.py with environment variable MCP_TRANSPORT in specifyplus-mcp-server/src/server.py
- [X] T069 [P] Add port configuration for SSE transport with environment variable MCP_PORT (default 8080) in specifyplus-mcp-server/src/server.py
- [X] T070 Update mcp.run() call to support transport parameter (stdio or sse) based on configuration in specifyplus-mcp-server/src/server.py
- [X] T071 [P] Write integration test for SSE transport (start server, connect via HTTP, execute prompt) in specifyplus-mcp-server/tests/test_integration.py

---

## Phase 8: Testing & Quality Assurance

**Purpose**: Validate all requirements, success criteria, and Constitution compliance

- [ ] T072 [P] Run pytest with coverage to verify ≥80% coverage threshold in specifyplus-mcp-server/
- [ ] T073 [P] Run black formatter on all Python files in specifyplus-mcp-server/src/ and specifyplus-mcp-server/tests/
- [ ] T074 [P] Run ruff linter and fix any issues in specifyplus-mcp-server/
- [ ] T075 [P] Run mypy type checker and resolve type errors in specifyplus-mcp-server/
- [ ] T076 Write performance benchmark test for startup time (SC-004: <2s) in specifyplus-mcp-server/tests/test_integration.py
- [ ] T077 Write performance benchmark test for prompt execution latency (SC-002: <500ms) in specifyplus-mcp-server/tests/test_integration.py
- [ ] T078 Write concurrency test for 10 simultaneous prompt requests (SC-003) in specifyplus-mcp-server/tests/test_integration.py
- [ ] T079 Create validation script to verify all 13 functional requirements (FR-001 through FR-013) with checklist
- [ ] T080 Create validation script to verify all 7 success criteria (SC-001 through SC-007) with measurements
- [ ] T081 Run pip-audit security scan and verify no HIGH/CRITICAL findings in specifyplus-mcp-server/
- [ ] T082 Generate coverage report and ensure core logic (loader, handler, registry) has ≥80% coverage

---

## Phase 9: Documentation & Deployment

**Purpose**: Production-ready documentation and deployment artifacts

- [ ] T083 [P] Create README.md with installation instructions (pip install, directory setup) in specifyplus-mcp-server/README.md
- [ ] T084 [P] Add configuration guide to README.md (stdio vs SSE, environment variables) in specifyplus-mcp-server/README.md
- [ ] T085 [P] Add usage examples to README.md (running server, connecting from IDE, invoking prompts) in specifyplus-mcp-server/README.md
- [ ] T086 [P] Add troubleshooting section to README.md (directory not found, malformed files, connection issues) in specifyplus-mcp-server/README.md
- [ ] T087 [P] Create data-model.md documenting all Pydantic models with field descriptions and examples in specs/001-mcp-server-prompts/data-model.md
- [ ] T088 [P] Create quickstart.md with step-by-step guide (install, configure, run, test) in specs/001-mcp-server-prompts/quickstart.md
- [ ] T089 [P] Create contracts/ directory and prompts-api.md with MCP protocol contracts (prompts/list, prompts/get, notifications) in specs/001-mcp-server-prompts/contracts/prompts-api.md
- [ ] T090 [P] Create Dockerfile for containerized deployment (optional) in specifyplus-mcp-server/Dockerfile
- [ ] T091 [P] Create systemd service file for production deployment (optional) in specifyplus-mcp-server/specifyplus-mcp.service

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - no dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - depends on US1 (needs CommandLoader, CommandRegistry)
  - User Story 3 (P3): Can start after Foundational - depends on US1 (needs prompt registration)
- **Hot Reload (Phase 6)**: Depends on US1 (needs CommandLoader, CommandRegistry)
- **SSE Transport (Phase 7)**: Depends on US1-2 (needs core server functionality)
- **Testing (Phase 8)**: Depends on all prior phases
- **Documentation (Phase 9)**: Depends on Phase 8 (all features complete)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (foundational MCP server capability)
- **User Story 2 (P2)**: Depends on US1 completion (needs CommandLoader and CommandRegistry from US1)
- **User Story 3 (P3)**: Depends on US1 completion (needs prompt registration mechanism from US1)

### Within Each User Story

- Models and exceptions first (Phase 2 Foundational)
- Loader before registry operations (US1)
- Registry before handler (US1 before US2)
- Handler before full prompt execution (US2)
- Metadata enrichment after basic registration (US3 after US1)

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- Tasks T003-T011 can all run in parallel (different files, no dependencies)

**Foundational Phase (Phase 2)**:
- Tasks T012-T021 can run in parallel (different modules: exceptions, models, validators)
- Tasks T022-T027 can run in parallel after T012-T021 (test files)

**User Story 1 (Phase 3)**:
- Tasks T028-T029 can run in parallel (independent methods in loader.py)
- Tasks T033-T034 can run in parallel with T028-T032 (registry.py independent of loader.py implementation)
- Tasks T040-T041 can run in parallel (independent test files)

**User Story 2 (Phase 4)**:
- Tasks T042-T043 can run in parallel (independent methods in handler.py)
- Tasks T051-T052 can run in parallel (independent test files)

**Hot Reload & SSE (Phases 6-7)**:
- Tasks T058-T062 can run in parallel with T068-T070 (watcher.py independent of transport config)

**Testing Phase (Phase 8)**:
- Tasks T072-T075 can all run in parallel (independent quality checks)
- Tasks T076-T078 can run in parallel (independent performance tests)

**Documentation Phase (Phase 9)**:
- Tasks T083-T091 can all run in parallel (different documentation files)

---

## Parallel Example: User Story 1

```bash
# Launch loader and registry implementation together:
Task T028-T032: "Implement CommandLoader class methods"
Task T033-T034: "Implement CommandRegistry class methods"

# Then server integration:
Task T035-T039: "FastMCP server setup and prompt registration"

# Finally tests:
Task T040: "Write CommandLoader unit tests"
Task T041: "Write CommandRegistry unit tests"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test connection to IDE, verify 13 commands listed
5. This delivers immediate value: SpecifyPlus commands accessible from any MCP-compatible IDE

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP achieved (commands discoverable and listable)
3. Add User Story 2 → Test independently → Core functionality (command execution with input)
4. Add User Story 3 → Test independently → Full documentation browsing
5. Add Hot Reload (Phase 6) → Live updates without restart
6. Add SSE Transport (Phase 7) → Remote server capability
7. Each increment adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T028-T041)
   - Developer B: Start on PromptHandler (T042-T047) once US1 models available
   - Developer C: Create test fixtures and documentation (T024-T027, T083-T089)
3. After US1 complete:
   - Developer A: Hot reload (T058-T067)
   - Developer B: User Story 2 completion (T048-T052)
   - Developer C: User Story 3 (T053-T057)
4. Final: All converge on testing and validation (Phase 8)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Tests are optional (not explicitly requested) but included for Constitution compliance (80% coverage)
- Verify functional requirements after each phase completion
- Commit after each completed user story phase
- Stop at checkpoints to validate story independently
- Performance targets: startup <2s, execution <500ms, reload <5s
- Security: input sanitization and size limits enforced
