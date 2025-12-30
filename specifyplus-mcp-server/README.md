# SpecifyPlus MCP Server

An MCP (Model Context Protocol) server that exposes SpecifyPlus commands as prompts for IDE integration.

## Overview

This server discovers and serves SpecifyPlus command files from `.claude/commands/` as MCP prompts, enabling seamless integration with MCP-compatible IDEs like Claude Desktop, VS Code, and others.

## Features

- **Command Discovery**: Automatically discovers all `.md` command files
- **YAML Frontmatter Parsing**: Extracts description and handoff metadata
- **Argument Substitution**: Replaces `$ARGUMENTS` with user input
- **Hot Reload**: Monitors for file changes and reloads automatically
- **Dual Transport**: Supports both stdio (default) and SSE protocols

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install package with dependencies
pip install -e .

# Install dev dependencies for testing
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file or set environment variables:

```bash
# Directory containing command files (required)
COMMANDS_DIR=/path/to/.claude/commands

# Logging level (optional, default: INFO)
LOG_LEVEL=INFO

# Transport protocol (optional, default: stdio)
MCP_TRANSPORT=stdio  # or "sse"

# Port for SSE transport (optional, default: 8080)
MCP_PORT=8080
```

## Usage

### Running the Server

```bash
# stdio mode (default)
python -m src.server

# SSE mode
MCP_TRANSPORT=sse MCP_PORT=8080 python -m src.server
```

### Connecting from Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "specifyplus": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/specifyplus-mcp-server"
    }
  }
}
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Format code
black src tests

# Lint code
ruff check src tests

# Type check
mypy src
```

## License

MIT
