# Implementation Plan: SpecifyPlus MCP Server

**Branch**: `001-mcp-server-prompts` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mcp-server-prompts/spec.md`

## Summary

Build a Python MCP server using FastMCP that exposes 13 SpecifyPlus commands from `.claude/commands/` as MCP prompts. The server discovers `.md` files, parses YAML frontmatter (description, handoffs), substitutes user input into `$ARGUMENTS` placeholders with sanitization, supports stdio/SSE transports, and hot-reloads on file changes.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: FastMCP 0.1+, Pydantic 2.0+, PyYAML 6.0+, Watchdog 3.0+, python-frontmatter 1.0+
**Storage**: File-based (read .md files from .claude/commands/)
**Testing**: pytest with asyncio support, coverage ≥80%
**Target Platform**: Cross-platform (Linux, macOS, Windows) - runs locally via stdio or remote via SSE
**Project Type**: Single Python package (MCP server)
**Performance Goals**: Startup <2s, prompt execution <500ms, hot reload <5s, handle 10 concurrent requests
**Constraints**: Max user input 100KB, fail if directory missing, sanitize template syntax
**Scale/Scope**: 13 commands, ~160KB total command content, stateless operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Spec Supremacy**: All functionality driven by spec.md requirements (FR-001 through FR-013)
✅ **Test-First**: Unit tests for all components before implementation
✅ **Simplicity**: Minimal dependencies, in-memory registry, no database
✅ **Security**: Input size limits (100KB), template sanitization, no secrets required, fail on HIGH/CRITICAL vulnerabilities
✅ **Performance**: Targets defined (SC-001 through SC-007) - CLI <200ms not applicable (server process)
✅ **Observability**: Structured logging with request IDs, error classification
✅ **Error Handling**: Graceful degradation for malformed files, clear error messages
✅ **Dependency Management**: Version-pinned dependencies, license compliance (MIT/Apache/BSD), lockfile required

## Project Structure

### Documentation (this feature)

```text
specs/001-mcp-server-prompts/
├── spec.md              # Feature specification
├── plan.md              # This file
├── data-model.md        # Data models and relationships (Phase 1 output)
├── quickstart.md        # Quick start guide (Phase 1 output)
├── contracts/           # API contracts (Phase 1 output)
│   └── prompts-api.md
└── tasks.md             # Implementation tasks (from /sp.tasks - NOT created by /sp.plan)
```

### Source Code (new directory: specifyplus-mcp-server/)

```text
specifyplus-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py              # FastMCP server + lifecycle hooks
│   ├── loader.py              # CommandLoader: discover & parse .md files
│   ├── registry.py            # CommandRegistry: thread-safe storage
│   ├── handler.py             # PromptHandler: argument substitution
│   ├── watcher.py             # FileWatcher: hot reload monitoring
│   ├── models.py              # Pydantic models (CommandDefinition, etc.)
│   ├── validators.py          # Input validation utilities
│   └── exceptions.py          # Custom exception classes
├── tests/
│   ├── __init__.py
│   ├── test_loader.py         # CommandLoader unit tests
│   ├── test_registry.py       # CommandRegistry unit tests
│   ├── test_handler.py        # PromptHandler unit tests
│   ├── test_watcher.py        # FileWatcher unit tests
│   ├── test_integration.py    # End-to-end integration tests
│   └── fixtures/              # Test command files
│       ├── valid/             # Well-formed samples
│       ├── malformed/         # Invalid YAML, missing sections
│       └── edge_cases/        # Special characters, large files
├── pyproject.toml             # Dependencies, build config
├── README.md                  # Installation and usage guide
└── .env.example               # Configuration template
```

**Structure Decision**: Single Python package with modular components. This aligns with "single project" pattern from Constitution and keeps MCP server separate from main TaskFlow AI codebase for independent deployment.

## Phase 0: Research

**Objective**: Understand MCP protocol, FastMCP SDK, and existing command file structure

**Activities**:
1. ✅ Reviewed MCP prompts specification (protocol draft)
2. ✅ Studied FastMCP Python SDK documentation
3. ✅ Analyzed 13 existing command files in `.claude/commands/`
4. ✅ Identified YAML frontmatter structure (description, handoffs with label/agent/prompt/send)
5. ✅ Confirmed $ARGUMENTS as single placeholder for user input substitution

**Key Findings**:
- MCP prompts are user-controlled, exposed as slash commands in IDEs
- FastMCP provides `@mcp.prompt()` decorator for registration
- Commands range from 2.5KB to 49KB, total ~160KB
- All commands use consistent YAML frontmatter + markdown body structure
- Handoffs enable workflow chaining (e.g., sp.specify → sp.plan → sp.tasks)

**Deliverables**:
- ✅ MCP protocol understanding documented
- ✅ Command file patterns analyzed
- ✅ Technical approach validated

## Phase 1: Design & Architecture

**Objective**: Create detailed technical design documents

**Research Document** (`research.md`):

### Component Architecture

**1. CommandLoader** (loader.py)
- Discovers *.md files in .claude/commands/ using `Path.glob()`
- Parses YAML frontmatter with `python-frontmatter` library
- Validates directory existence (FR-001a: fail if missing)
- Handles malformed files gracefully (FR-012: skip with warning)
- Returns Dict[str, CommandDefinition]

**2. CommandRegistry** (registry.py)
- In-memory storage: Dict[str, CommandDefinition]
- Thread-safe with threading.RLock for concurrent access (SC-003)
- Methods: register(), get(), list_commands(), update_all(), clear()
- Atomic bulk updates for hot reload

**3. PromptHandler** (handler.py)
- Validates user input size ≤100KB (FR-004a)
- Sanitizes template syntax: escapes $ARGUMENTS, ${...} patterns (FR-005a)
- Substitutes $ARGUMENTS in command content (FR-005)
- Returns processed prompt string
- Handles commands without $ARGUMENTS (FR-008: return as-is)

**4. FileWatcher** (watcher.py)
- Uses `watchdog` library for cross-platform file system monitoring
- Watches .claude/commands/ for .md file changes
- Triggers reload_commands() callback on events
- Debounces rapid changes to prevent reload storms
- Target: reload within 5 seconds (SC-007)

**5. FastMCP Server** (server.py)
- Initializes FastMCP("specifyplus-commands")
- Startup hook: initialize components, load commands, start watcher
- Shutdown hook: stop watcher, clean registry
- Dynamic prompt registration from registry
- Supports stdio (default) and SSE transports (FR-011)
- Exposes listChanged capability for hot reload notifications

### Data Models

**HandoffLink** (Pydantic BaseModel):
```python
label: str              # "Build Technical Plan"
agent: str              # "sp.plan"
prompt: str             # "Create a plan for..."
send: bool = False      # Auto-send flag
```

**CommandMetadata** (Pydantic BaseModel):
```python
description: str                    # Required: command description
handoffs: List[HandoffLink] = []    # Optional: workflow links
```

**CommandDefinition** (Pydantic BaseModel):
```python
name: str                # "sp.specify" (from filename)
file_path: str           # Absolute path to .md file
metadata: CommandMetadata
content: str             # Full markdown after frontmatter
has_arguments: bool      # Whether $ARGUMENTS exists
file_size: int           # Bytes
last_modified: datetime  # For cache invalidation
```

### Technology Choices

**Python 3.10+**: Type hints, pattern matching, performance improvements
**FastMCP**: Official MCP SDK with native prompt support
**Pydantic v2**: Data validation, type safety, clear error messages
**python-frontmatter**: Dedicated markdown + YAML parser
**Watchdog**: Cross-platform file system events (inotify/FSEvents)
**pytest + pytest-asyncio**: Async-aware testing framework

### Security Design

**Input Sanitization** (FR-005a):
```python
def sanitize_input(text: str) -> str:
    # Escape literal $ARGUMENTS to prevent re-substitution
    text = text.replace('$ARGUMENTS', '\\$ARGUMENTS')
    # Escape ${...} patterns
    text = re.sub(r'\$\{([^}]+)\}', r'\\${\1}', text)
    return text
```

**Size Validation** (FR-004a):
```python
if len(user_input.encode('utf-8')) > 102_400:
    raise InputTooLargeError("Input exceeds maximum allowed size of 100KB")
```

**No Code Execution**: Template substitution only, no eval/exec/compile

### Performance Design

**Startup Optimization** (SC-004: <2s):
- File discovery via glob (O(n) where n=13)
- Parallel file reading if needed (ThreadPoolExecutor)
- Pre-compiled regex patterns for sanitization
- Cache file stats to avoid repeated stat() calls

**Runtime Performance** (SC-002: <500ms):
- In-memory registry lookups (O(1))
- Minimal string operations (single replace)
- No I/O in request path
- Stateless operation (no locking delays)

**Concurrency** (SC-003: 10 concurrent):
- Thread-safe registry with RLock
- Read-only operations (no state modification)
- Copy-on-write for hot reload updates

### Error Handling Design

**Startup Errors**:
- Directory missing → SystemExit with message (FR-001a)
- Malformed files → Warning logged, skipped (FR-012)
- Zero commands found → Info logged, server starts

**Runtime Errors**:
- Input too large → Return error to client (FR-004a)
- Command not found → Return error with available list
- Template substitution failure → Log error, return original

**Logging Strategy**:
```python
logger.warning(f"Failed to parse {file_path}: {error}. Skipping.")
logger.info(f"Loaded {count} commands")
logger.error(f"Error processing prompt '{name}': {error}")
```

## Phase 1 Deliverables

After completing Phase 1 design work, create these documents:

### 1. data-model.md

Document all Pydantic models with:
- Field definitions and types
- Validation rules
- Relationships between models
- Example instances

### 2. quickstart.md

Step-by-step guide:
1. Install dependencies
2. Configure .claude/commands/ directory
3. Run server (stdio mode)
4. Test with MCP Inspector
5. Connect to IDE (Claude Desktop example)

### 3. contracts/prompts-api.md

MCP protocol contracts:
- `prompts/list` request/response format
- `prompts/get` request/response format
- `notifications/prompts/list_changed` format
- Error codes and messages

## Critical Files

**Specification & Requirements**:
- `/home/hasss/todo-app/specs/001-mcp-server-prompts/spec.md` - Source of truth

**Command File Examples**:
- `/home/hasss/todo-app/.claude/commands/sp.specify.md` - Large file with handoffs (14.2 KB)
- `/home/hasss/todo-app/.claude/commands/sp.taskstoissues.md` - Minimal file (2.5 KB)
- `/home/hasss/todo-app/.claude/commands/sp.plan.md` - Mid-size, no handoffs (4.5 KB)

**Governance**:
- `/home/hasss/todo-app/.specify/memory/constitution.md` - Security, testing, quality standards

## Key Technical Decisions

**Decision 1: Python 3.10+ with FastMCP**
- **Options Considered**: TypeScript (MCP SDK), Python (FastMCP), Rust (custom)
- **Chosen**: Python 3.10+ with FastMCP
- **Rationale**:
  - Native MCP prompt support via decorators
  - Mature Python ecosystem for file parsing (frontmatter, yaml)
  - Team familiarity with Python
  - Aligns with mcp-builder skill recommendations
- **Trade-offs**: Slightly slower than TypeScript, but adequate for requirements

**Decision 2: In-Memory Registry**
- **Options Considered**: Database (SQLite), File cache, In-memory
- **Chosen**: In-memory Dict with thread safety
- **Rationale**:
  - 13 files (~160KB) easily fits in memory
  - O(1) lookups meet <500ms requirement
  - No persistence needed (commands come from files)
  - Simplicity (YAGNI principle from Constitution)
- **Trade-offs**: Lost on restart, but commands reload from disk instantly

**Decision 3: Watchdog for File Monitoring**
- **Options Considered**: Polling, Watchdog, inotify wrapper
- **Chosen**: Watchdog library
- **Rationale**:
  - Cross-platform (Linux/macOS/Windows)
  - Event-driven (efficient, no polling overhead)
  - Well-maintained, stable API
- **Trade-offs**: Additional dependency, but widely used and reliable

**Decision 4: Fail-Fast Directory Validation**
- **Options Considered**: Auto-create directory, Fail startup, Start with warnings
- **Chosen**: Fail startup if directory missing (FR-001a)
- **Rationale**: User explicitly chose this in clarification session
- **Trade-offs**: Requires manual setup, but prevents silent failures

**Decision 5: Template Sanitization over Rejection**
- **Options Considered**: Reject input with templates, Sanitize/escape, Allow raw
- **Chosen**: Escape template syntax in user input
- **Rationale**:
  - Prevents injection attacks (FR-005a)
  - Preserves user intent (literal $ARGUMENTS appears in output)
  - Better UX than rejection
- **Trade-offs**: Slightly more complex than rejection, but more robust

## Implementation Phases

### Phase 0: Research (COMPLETED)

✅ Explored MCP prompts protocol specification
✅ Studied FastMCP Python SDK documentation
✅ Analyzed existing 13 command files structure
✅ Identified YAML frontmatter patterns and $ARGUMENTS usage

### Phase 1: Project Setup

**Tasks**:
1. Create `specifyplus-mcp-server/` directory structure
2. Initialize `pyproject.toml` with dependencies
3. Create `src/__init__.py` and package metadata
4. Set up `pytest` configuration in pyproject.toml
5. Create `.env.example` with configuration variables
6. Create `.gitignore` for Python project

**Deliverables**:
- Empty package structure
- Dependency definitions
- Test framework configured

### Phase 2: Data Models & Exceptions

**Tasks**:
1. Implement `models.py`:
   - HandoffLink with Pydantic validation
   - CommandMetadata with required/optional fields
   - CommandDefinition with validators
   - PromptArguments with size validation
2. Implement `exceptions.py`:
   - DirectoryNotFoundError (FR-001a)
   - CommandParseError (FR-012)
   - InputTooLargeError (FR-004a)
   - CommandNotFoundError
3. Write unit tests for model validation

**Deliverables**:
- Validated data models
- Custom exception hierarchy
- Tests for edge cases

### Phase 3: Command Loader

**Tasks**:
1. Implement `CommandLoader` class:
   - `__init__()`: Validate directory exists (FR-001a)
   - `discover_commands()`: Glob *.md files (FR-001)
   - `parse_command_file()`: Parse YAML + content (FR-002)
   - `load_all_commands()`: Batch load with error handling (FR-012)
2. Write unit tests:
   - Test directory validation
   - Test YAML parsing
   - Test malformed file handling
   - Test command name derivation

**Deliverables**:
- Functional command loader
- 80%+ test coverage
- Graceful error handling

### Phase 4: Command Registry

**Tasks**:
1. Implement `CommandRegistry` class:
   - Thread-safe operations with RLock
   - register(), get(), list_commands(), update_all()
2. Write unit tests:
   - Test CRUD operations
   - Test thread safety (concurrent access)
   - Test atomic updates

**Deliverables**:
- Thread-safe registry
- Tested concurrent access patterns

### Phase 5: Prompt Handler

**Tasks**:
1. Implement `PromptHandler` class:
   - `sanitize_input()`: Escape $ARGUMENTS, ${...} (FR-005a)
   - `process_prompt()`: Validate, sanitize, substitute (FR-005)
2. Implement `validators.py`:
   - Input size validation (FR-004a)
   - Template syntax detection
3. Write unit tests:
   - Test $ARGUMENTS substitution
   - Test template sanitization
   - Test size limit enforcement
   - Test commands without $ARGUMENTS (FR-008)

**Deliverables**:
- Secure prompt processing
- Injection prevention validated
- Edge cases tested

### Phase 6: File Watcher

**Tasks**:
1. Implement `FileWatcher` class:
   - Watchdog observer setup
   - Event handlers (modified, created, deleted)
   - Debouncing logic
2. Write unit tests:
   - Test file change detection
   - Test reload triggering
   - Test debouncing (FR-013: within 5s)

**Deliverables**:
- Hot reload functionality
- Performance within targets (SC-007)

### Phase 7: FastMCP Server Integration

**Tasks**:
1. Implement `server.py`:
   - Initialize FastMCP instance
   - Startup hook: initialize_server()
   - Shutdown hook: cleanup
   - Dynamic prompt registration
   - Transport configuration (stdio/SSE per FR-011)
2. Write integration tests:
   - Test end-to-end prompt execution
   - Test startup performance (SC-004: <2s)
   - Test concurrent requests (SC-003: 10 concurrent)
   - Test hot reload workflow

**Deliverables**:
- Fully functional MCP server
- Multi-transport support
- Performance targets met

### Phase 8: Testing & Validation

**Tasks**:
1. Create test fixtures (valid/malformed/edge_cases command files)
2. Achieve 80% coverage minimum
3. Run performance benchmarks
4. Validate all 13 requirements (FR-001 through FR-013)
5. Validate all 7 success criteria (SC-001 through SC-007)
6. Security scan with pip-audit

**Deliverables**:
- Full test suite passing
- Coverage report ≥80%
- Performance benchmarks documented
- Security scan clean

### Phase 9: Documentation & Deployment

**Tasks**:
1. Write README.md:
   - Installation instructions
   - Configuration guide (stdio vs SSE)
   - Usage examples
   - Troubleshooting
2. Create deployment configurations:
   - Dockerfile (optional)
   - Systemd service file (optional)
3. Document API contracts in contracts/prompts-api.md

**Deliverables**:
- Complete documentation
- Deployment ready

## Architecture Details

### Core Components

**1. CommandLoader (loader.py)**
- **Purpose**: Discover and parse command files
- **Key Methods**:
  - `discover_commands()`: Find all *.md files in .claude/commands/
  - `parse_command_file()`: Extract YAML frontmatter + markdown content
  - `load_all_commands()`: Batch load all discovered files
- **Error Handling**: Skip malformed files, log warnings (FR-012)
- **Performance**: Parallel file reading if needed for startup target

**2. CommandRegistry (registry.py)**
- **Purpose**: Thread-safe in-memory storage for command definitions
- **Key Methods**:
  - `register()`: Add single command
  - `get()`: Retrieve by name
  - `update_all()`: Atomic bulk update (for hot reload)
  - `list_commands()`: Get all names
- **Concurrency**: RLock for thread safety (SC-003)

**3. PromptHandler (handler.py)**
- **Purpose**: Process user input and generate final prompts
- **Key Methods**:
  - `sanitize_input()`: Escape $ARGUMENTS and ${...} patterns (FR-005a)
  - `process_prompt()`: Validate size, sanitize, substitute $ARGUMENTS (FR-004a, FR-005)
- **Security**: Template injection prevention, size validation

**4. FileWatcher (watcher.py)**
- **Purpose**: Monitor .claude/commands/ for file changes
- **Key Methods**:
  - `start()`: Begin watching directory
  - `stop()`: Clean shutdown
  - `_trigger_reload()`: Callback to reload commands
- **Events**: on_modified, on_created, on_deleted
- **Performance**: Debouncing to prevent rapid reloads, reload within 5s (SC-007)

**5. FastMCP Server (server.py)**
- **Purpose**: MCP protocol implementation and coordination
- **Lifecycle Hooks**:
  - `on_startup()`: Initialize components, load commands, start watcher
  - `on_shutdown()`: Stop watcher, clean registry
- **Prompt Registration**: Dynamic registration of all commands as MCP prompts
- **Transport**: Configurable stdio (default) or SSE (FR-011)

### Data Flow

```
User invokes command in IDE
  ↓
MCP client sends prompts/get request (name + arguments)
  ↓
FastMCP routes to get_prompt()
  ↓
PromptHandler validates input size (FR-004a)
  ↓
PromptHandler sanitizes template syntax (FR-005a)
  ↓
PromptHandler substitutes $ARGUMENTS (FR-005)
  ↓
Returns processed prompt as message with role="user"
  ↓
IDE receives complete prompt and sends to LLM
```

**Hot Reload Flow**:
```
File modified in .claude/commands/
  ↓
Watchdog detects change event
  ↓
FileWatcher triggers reload_commands()
  ↓
CommandLoader re-parses all files
  ↓
Registry atomically updates command definitions
  ↓
FastMCP sends listChanged notification to clients
```

## Risk Analysis & Mitigation

**Risk 1: FastMCP API Compatibility**
- **Impact**: Breaking changes could require refactoring
- **Likelihood**: Low (stable SDK)
- **Mitigation**: Pin exact version in pyproject.toml, monitor releases
- **Contingency**: Fallback to direct MCP protocol implementation

**Risk 2: File System Performance**
- **Impact**: Slow startup with large command files
- **Likelihood**: Very Low (13 files, 160KB total)
- **Mitigation**: Monitor startup time, optimize if needed
- **Contingency**: Implement lazy loading if >100 commands

**Risk 3: Hot Reload Race Conditions**
- **Impact**: Registry update during active prompt request
- **Likelihood**: Low (rare simultaneous modification + request)
- **Mitigation**: Atomic update_all() with RLock
- **Contingency**: Disable hot reload via environment variable

## Dependencies & Execution Order

**Phase Dependencies**:
- Phase 1-2: Can start immediately (no dependencies)
- Phase 3-5: Depend on Phase 2 (models must exist)
- Phase 6: Depends on Phases 3-4 (loader and registry needed)
- Phase 7: Depends on all prior phases (integration)
- Phase 8-9: Depend on Phase 7 (testing complete system)

**Parallel Opportunities**:
- Phase 2: Models and exceptions (independent modules)
- Phase 3-4: Loader and registry (both use models)
- Phase 5-6: Handler and watcher (independent)
- Testing: Unit tests for each component in parallel

**Execution Strategy**: Bottom-up implementation with continuous testing. Each phase produces testable artifacts before moving to next phase.

## Complexity Tracking

> No Constitution violations requiring justification. All design decisions align with simplicity and spec supremacy principles.

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown with file paths
2. Begin Phase 1 implementation (project setup)
3. Follow red-green-refactor cycle per Constitution Principle IV
4. Consider documenting FastMCP technology choice: `/sp.adr "Python FastMCP for MCP Server Implementation"`
