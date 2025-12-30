---
description: "A test command for unit testing purposes"
handoffs:
  - label: "Run next step"
    agent: "sp.next"
    prompt: "Continue with the next step"
    send: false
  - label: "Auto-run final"
    agent: "sp.final"
    prompt: "Finalize the process"
    send: true
---

# Test Command

This is a test command for unit testing the SpecifyPlus MCP Server.

## Purpose

Validate that the command loader correctly:
1. Parses YAML frontmatter
2. Extracts the description
3. Processes handoff links
4. Detects $ARGUMENTS placeholder

## User Input

$ARGUMENTS

## Expected Behavior

When invoked, the $ARGUMENTS placeholder above should be replaced with the user's input text.
