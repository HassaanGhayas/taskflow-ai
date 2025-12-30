# **Project Specification: Todo In-Memory Python Console App**

## **1. Objective**

Build a professional command-line interface (CLI) todo application that manages tasks in-memory. The primary goal is to demonstrate a strict **Spec-Driven Development (SDD)** workflow using **Claude Code** and **Spec-Kit Plus**.

## **2. Technology Stack**

* **Package Manager:** [uv](https://github.com/astral-sh/uv)
* **Language:** Python 3.13+
* **Agentic Orchestration:** Claude Code
* **Specification Framework:** Spec-Kit Plus
* **Storage:** In-memory (no persistent database required for MVP)

## **3. Functional Requirements (Basic Level)**

The application must support the following core features:

| Feature | Description |
| --- | --- |
| **Add Task** | Create a new task with a mandatory `title` and optional `description`. |
| **List Tasks** | Display all tasks with their `ID`, `Status`, and `Title`. |
| **Update Task** | Edit the title or description of an existing task by its `ID`. |
| **Delete Task** | Remove a task from memory using its unique `ID`. |
| **Mark Complete** | Toggle a task's status between `Pending` and `Complete`. |

## **4. Technical Constraints & Standards**

* **Project Structure:** Must follow a modern Python layout (e.g., `src/` directory).
* **Clean Code:** Use type hints, docstrings, and modular design.
* **Execution Loop:** The app should run in a loop or accept CLI arguments via a library like `argparse` or `click`.
* **Error Handling:** Gracefully handle non-existent IDs and invalid inputs.

## **5. Spec-Driven Workflow (The Pipeline)**

All development must follow the **AGENTS.md** lifecycle:

1. **Specify:** Define user journeys in `speckit.specify`.
2. **Plan:** Design modules and logic in `speckit.plan`.
3. **Tasks:** Break down the work into atomic units in `speckit.tasks`.
4. **Implement:** Code the solution only after tasks are validated.

## **6. Deliverables**

The final GitHub repository must contain:

### **Documentation & Config**

* `speckit.constitution`: Project principles (e.g., "Always use type hints").
* `specs/`: A history folder containing all versions of your `.specify`, `.plan`, and `.tasks`.
* `README.md`: Setup instructions using `uv`.
* `CLAUDE.md`: The agent "shim" (containing `@AGENTS.md`).
* `AGENTS.md`: The rules for agent behavior.

### **Source Code**

* `/src`: Python source code.
* `tests/`: (Optional but recommended) Basic unit tests for the task logic.