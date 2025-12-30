# Feature Specification: SpecifyPlus MCP Server

**Feature Branch**: `001-mcp-server-prompts`
**Created**: 2025-12-21
**Status**: Draft
**Input**: User description: "We have specifyplus commands on @.claude/commands/** Each command takes user input and updates its prompt variable before sending it to the agent. Now you will use your mcp builder skill and create an mcp server where these commands are available as prompts. Goal: Now we can run this MCP server and connect with any agent and IDE."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Connect MCP Server to IDE (Priority: P1)

A developer wants to use SpecifyPlus commands from any IDE or AI agent that supports the Model Context Protocol. They install and configure the MCP server, then connect their IDE to it. Once connected, they can execute SpecifyPlus commands like /sp.specify, /sp.plan, and /sp.tasks through their IDE's AI interface without needing the original command files.

**Why this priority**: This is the foundational capability that enables all other use cases. Without the ability to connect and discover commands, no other functionality is possible.

**Independent Test**: Can be fully tested by configuring the MCP server in an IDE's settings, verifying connection status, and listing available prompts. Delivers immediate value by making commands accessible outside the original environment.

**Acceptance Scenarios**:

1. **Given** an IDE with MCP support, **When** user adds the SpecifyPlus MCP server configuration, **Then** the IDE successfully connects and lists available commands
2. **Given** a connected MCP server, **When** user requests list of available prompts, **Then** all 13 SpecifyPlus commands are displayed with their descriptions
3. **Given** a connected IDE, **When** user disconnects and reconnects, **Then** the MCP server re-establishes connection without data loss

---

### User Story 2 - Execute Commands with User Input (Priority: P2)

A developer wants to execute a SpecifyPlus command (e.g., /sp.specify) with custom input through their IDE. They select the command, provide their feature description as input, and the MCP server processes this input by substituting it into the command's prompt template before returning the complete prompt to the agent.

**Why this priority**: This enables the core workflow - transforming user input into properly formatted command prompts. Without this, commands would be static and unusable.

**Independent Test**: Can be tested independently by executing any single command (e.g., /sp.specify "Add user authentication") and verifying the prompt includes the user's input text. Delivers value by enabling actual command usage.

**Acceptance Scenarios**:

1. **Given** a connected MCP server and user input "Add payment processing", **When** user executes /sp.specify command, **Then** the returned prompt includes "Add payment processing" in the $ARGUMENTS section
2. **Given** a command execution in progress, **When** user provides multi-line input with special characters, **Then** the prompt correctly preserves formatting and escapes characters
3. **Given** a command requiring no arguments (like /sp.constitution), **When** user executes it without input, **Then** the command executes successfully with the default prompt template

---

### User Story 3 - Browse Command Documentation (Priority: P3)

A developer new to SpecifyPlus wants to understand what each command does before using it. They browse the available commands in their IDE and view detailed documentation including command purpose, expected inputs, and example usage patterns.

**Why this priority**: This improves discoverability and reduces learning curve, but the commands can be used without this if the user already knows what they want to do.

**Independent Test**: Can be tested by requesting command metadata through the IDE and verifying descriptions, parameter definitions, and usage examples are displayed. Delivers value by making the system self-documenting.

**Acceptance Scenarios**:

1. **Given** a connected MCP server, **When** user views /sp.specify command details, **Then** description includes "Create or update the feature specification from a natural language feature description"
2. **Given** browsing command list, **When** user views any command, **Then** handoff links to related commands are visible (e.g., /sp.specify shows link to /sp.plan)
3. **Given** viewing command documentation, **When** user checks input requirements, **Then** parameter types and whether they're required/optional are clearly indicated

---

### Edge Cases

- When a command file has malformed YAML frontmatter: skip the file, log warning with filename and parsing error, continue loading other commands
- User input exceeding 100KB (102,400 bytes) is rejected with error message: "Input exceeds maximum allowed size of 100KB"
- When command directory doesn't exist: fail startup with error "Command directory .claude/commands/ not found. Please create it and add command files."
- When command directory is empty: server starts successfully with zero available commands (logged as info)
- Circular handoff references are allowed and exposed as-is in metadata; client/IDE handles navigation and cycle detection
- User input containing template syntax like `$ARGUMENTS` or `${...}` is escaped/sanitized to appear as literal text (prevents injection)
- How does system behave when multiple clients connect to the same MCP server simultaneously?
- What occurs when command files are modified while the MCP server is running?

## Clarifications

### Session 2025-12-23

- Q: What should happen when a command file has malformed YAML frontmatter that cannot be parsed? → A: Skip the malformed command, log a warning, and continue loading other commands
- Q: What is the maximum allowed size for user input to prevent resource exhaustion attacks? → A: 100KB (102,400 bytes)
- Q: What should happen when the `.claude/commands/` directory doesn't exist at server startup? → A: Fail server startup with error message instructing user to create the directory
- Q: How should the system handle user input containing `$ARGUMENTS` or other potential template syntax to prevent injection issues? → A: Escape/sanitize template syntax in user input so it appears literally in the final prompt
- Q: How should circular handoff references be handled (e.g., command A links to B, B links back to A)? → A: Allow circular references; expose handoffs as-is without traversal (client handles navigation)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST discover all command files matching the pattern `*.md` in the `.claude/commands/` directory
- **FR-001a**: System MUST fail startup if `.claude/commands/` directory does not exist, with error message: "Command directory .claude/commands/ not found. Please create it and add command files."
- **FR-002**: System MUST parse YAML frontmatter from each command file to extract description and handoffs metadata
- **FR-003**: System MUST expose each discovered command as an MCP prompt with a name derived from the filename (e.g., `sp.specify.md` → `sp.specify`)
- **FR-004**: System MUST accept user input as prompt arguments when a command is invoked
- **FR-004a**: System MUST reject user input exceeding 100KB (102,400 bytes) with a clear error message
- **FR-005**: System MUST substitute user input into the `$ARGUMENTS` placeholder in the command template
- **FR-005a**: System MUST escape/sanitize template syntax (e.g., `$ARGUMENTS`, `${...}`) in user input to prevent injection and ensure it appears as literal text in the final prompt
- **FR-006**: System MUST return the complete, processed prompt content to the requesting agent
- **FR-007**: System MUST preserve markdown formatting, code blocks, and special characters in command templates
- **FR-008**: System MUST handle commands with no `$ARGUMENTS` placeholder by returning the template as-is
- **FR-009**: System MUST expose handoff information as prompt metadata to enable command chaining, including circular references (client/IDE responsible for navigation logic)
- **FR-010**: System MUST start successfully and serve prompts on standard MCP protocol channels
- **FR-011**: System MUST support both stdio and SSE transport protocols for MCP communication
- **FR-012**: System MUST gracefully handle missing, inaccessible, or malformed command files by logging warnings and skipping the problematic file while continuing to load other commands
- **FR-013**: System MUST reload command definitions when files change without requiring server restart

### Key Entities

- **Command Definition**: Represents a SpecifyPlus command with metadata (name, description, handoffs) and prompt template content
- **Prompt Template**: The markdown content of a command file that includes placeholders for user input
- **Handoff Link**: A connection between commands that suggests next steps in the workflow (e.g., specify → plan → tasks)
- **User Input**: Text provided by the user when invoking a command, to be substituted into template placeholders

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 13 existing SpecifyPlus commands are discoverable and executable through any MCP-compatible IDE within 30 seconds of connection
- **SC-002**: Developers can execute a command with custom input and receive the processed prompt in under 500 milliseconds
- **SC-003**: The MCP server successfully handles at least 10 concurrent command executions without errors
- **SC-004**: Command discovery and metadata parsing completes in under 2 seconds on server startup
- **SC-005**: System operates correctly with command files ranging from 100 bytes to 50KB in size
- **SC-006**: 100% of command handoff links are exposed as navigable metadata in supporting IDEs
- **SC-007**: File watching detects command changes and reloads definitions within 5 seconds

## Assumptions

- Commands are stored in `.claude/commands/` directory relative to the MCP server's working directory
- All command files follow the established markdown format with YAML frontmatter
- The `$ARGUMENTS` variable is the only dynamic placeholder requiring substitution
- Agents and IDEs using the MCP server support the standard MCP prompt protocol
- Command files are encoded in UTF-8
- The operating system supports file watching capabilities (inotify on Linux, FSEvents on macOS, etc.)
- Multiple simultaneous connections will be read-only operations (no state modification conflicts)

## Out of Scope

- Executing command logic or implementing the actual SpecifyPlus workflow (server only provides prompts)
- Authentication or authorization for MCP connections
- Command history or usage analytics
- Custom command creation UI or command editor
- Validation of command syntax beyond basic YAML parsing
- Version control integration for command files
- Migration of commands from other formats
- Command aliases or shortcuts
- Internationalization of command descriptions
