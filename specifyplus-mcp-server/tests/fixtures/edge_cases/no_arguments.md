---
description: "Command without $ARGUMENTS placeholder"
---

# No Arguments Command

This command has valid frontmatter but does not contain the $ARGUMENTS placeholder.

Per FR-008, it should be returned as-is without any substitution.

Users can still execute this command, but any input they provide will be ignored.
