#!/bin/bash
export COMMANDS_DIR="/home/hasss/todo-app/.claude/commands"
cd /home/hasss/todo-app/specifyplus-mcp-server
exec /home/hasss/.local/bin/uv run python -m src.server
