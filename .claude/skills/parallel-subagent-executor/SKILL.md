---
name: parallel-subagent-executor
description: Launch independent subagents in parallel using RISEN framework. Use when parsing tasks.md for parallelizable work units ([P] markers) or implementing multiple features simultaneously.
---

# Parallel Subagent Executor

Launch independent subagents concurrently using structured prompting patterns.

## Quick Start

1. Parse `tasks.md` for `[P]` parallel markers or independent user stories
2. Group by dependency (only launch when deps satisfied)
3. Launch with Task tool using correct parameters

## Launch Pattern

```python
Task(
  subagent_type="general-purpose",
  description="Brief task description (REQUIRED)",
  prompt="""Role: You are a...
Instructions:
1...
2...
Steps:
1...
2...
End Goal: Specific measurable outcome
Narrowing:
- Constraints
- What's NOT in scope"""
)
```

## Common Errors

| Error | Fix |
|-------|-----|
| "required parameter 'description' is missing" | Add `description` field |
| "InputValidationError" | Check all required fields present |
| Token limit | Resume with `resume: agent-id` |

## Workflow

### Parse Tasks
Extract `[P]` marked tasks or identify independent user stories from `tasks.md`.

### Group by Dependency
- Group 1: No deps → Launch in parallel
- Group 2: Depends on G1 → Launch after G1 complete
- Group 3: Depends on G2 → Sequential

### Launch & Track
```python
# Parallel launch (single message)
TaskOutput(task_id="agent-1", block=True)
TaskOutput(task_id="agent-2", block=True)

# Background
TaskOutput(task_id="agent-id", block=False)
```

## Example

Launch 4 setup subagents concurrently:

```
Task 1: {"subagent_type": "general-purpose", "description": "Setup Phase 1 structure", "prompt": "Role: Python project specialist..."}
Task 2: {"subagent_type": "general-purpose", "description": "Implement Status enum and Task dataclass", "prompt": "Role: Python data modeling expert..."}
Task 3: {"subagent_type": "general-purpose", "description": "Implement task_service CRUD", "prompt": "Role: Python service layer expert..."}
Task 4: {"subagent_type": "general-purpose", "description": "Implement CLI commands", "prompt": "Role: Python CLI expert..."}
```

## Quality Checklist

Before launch:
- [ ] Tasks are truly independent
- [ ] Clear success criteria for each
- [ ] RISEN framework applied
- [ ] All Task parameters included

After completion:
- [ ] Verify all succeeded
- [ ] Aggregate results
- [ ] Run integration tests
- [ ] Document issues
