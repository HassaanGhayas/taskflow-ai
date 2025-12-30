---
description: "Command with special characters: <>&\"' and unicode "
handoffs:
  - label: "Test with 'quotes' and \"double\""
    agent: "sp.special"
    prompt: "Handle <html> & entities"
    send: false
---

# Special Characters Command

This command tests handling of special characters in:

1. Description field with HTML entities: <>&"'
2. Handoff labels with quotes
3. Unicode characters:  emoji
4. Template syntax that should NOT be processed: ${NOT_A_VAR}

## User Input

$ARGUMENTS

The above should be the only substitution made.
