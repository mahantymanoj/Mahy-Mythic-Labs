# 💻 Coding Standards

> **Mahy Mythic Labs Coding Standards**
>
> Version: 1.0
>
> This document defines the official coding conventions, software engineering principles, architectural guidelines, documentation standards, and best practices for all source code within Mahy Mythic Labs.

---

# 1. Purpose

The coding standards ensure that the codebase remains:

- Readable
- Consistent
- Maintainable
- Testable
- Scalable
- Reviewable

These standards apply equally to human-written and AI-generated code.

---

# 2. Guiding Principles

Every implementation should prioritize:

- Simplicity
- Clarity
- Reusability
- Maintainability
- Extensibility
- Testability

Code should be written for future contributors, not just current requirements.

---

# 3. Language Standards

Primary language:

```
Python 3.12+
```

Supporting formats:

- YAML
- JSON
- Markdown

Avoid introducing additional languages unless there is a clear technical justification.

---

# 4. Project Structure

Application code belongs under:

```
src/

agents/
engine/
providers/
models/
services/
utils/
cli/
```

Business logic should not exist outside `src/`.

---

# 5. Naming Conventions

## Variables

Use descriptive `snake_case`.

Good:

```python
episode_context
provider_manager
workflow_state
```

Avoid:

```python
x
tmp
data1
```

---

## Functions

Use verbs that describe behavior.

Examples:

```python
load_context()

generate_script()

execute_workflow()

validate_output()
```

---

## Classes

Use `PascalCase`.

Examples:

```python
ProductionEngine

WorkflowManager

ContextManager

ResearchAgent
```

---

## Constants

Use uppercase.

```python
MAX_RETRIES = 3

DEFAULT_TIMEOUT = 60
```

---

## Modules

Use lowercase with snake_case.

```
workflow_manager.py

provider_registry.py

context_manager.py
```

---

# 6. File Organization

Each file should have one primary responsibility.

Typical order:

1. Imports
2. Constants
3. Exceptions
4. Data models
5. Classes
6. Helper functions

Avoid excessively large modules. Consider splitting files that exceed several hundred lines or combine unrelated responsibilities.

---

# 7. Type Hints

Public functions should include type hints.

Example:

```python
def load_workflow(path: Path) -> Workflow:
    ...
```

Prefer explicit types over `Any` unless flexibility is genuinely required.

---

# 8. Docstrings

Use Google-style docstrings.

Example:

```python
def generate_script(topic: str) -> str:
    """Generate a script for the given topic.

    Args:
        topic: Episode topic.

    Returns:
        Generated script.
    """
```

Public modules, classes, and functions should be documented.

---

# 9. Error Handling

Raise meaningful exceptions.

Good:

```python
raise WorkflowValidationError(message)
```

Avoid:

```python
except:
    pass
```

Catch only exceptions you can handle meaningfully.

---

# 10. Logging

Use the standard logging framework.

Log:

- Workflow progress
- Errors
- Warnings
- Provider requests
- Retry attempts

Do not log:

- API keys
- Secrets
- Tokens
- Sensitive credentials

---

# 11. Configuration

Configuration belongs in:

```
config/
```

Never hardcode:

- API keys
- Model names
- File paths
- Environment-specific values

Access configuration through centralized configuration services.

---

# 12. Dependency Management

Every dependency should be:

- Necessary
- Maintained
- Version controlled
- Documented

Avoid duplicate libraries providing the same functionality.

---

# 13. Code Formatting

Use automated formatting tools.

Recommended:

- Black
- Ruff
- isort

Formatting should be enforced consistently across the project.

---

# 14. Architecture Principles

Follow:

- Single Responsibility Principle
- Separation of Concerns
- Composition over inheritance
- Dependency Injection where appropriate
- Interface-driven design

Avoid tightly coupled components.

---

# 15. Reusability

Before creating new code, check whether similar functionality already exists.

Prefer extending existing modules over duplicating logic.

Shared functionality belongs in reusable services or utilities.

---

# 16. Testing Requirements

New code should include appropriate tests.

Test:

- Expected behavior
- Edge cases
- Failure scenarios
- Error handling

Code should remain testable without requiring external services whenever practical.

---

# 17. AI-Generated Code

AI-generated code must:

- Follow these standards
- Include type hints
- Use descriptive names
- Avoid duplication
- Be reviewed before merging

Generated code is subject to the same quality expectations as manually written code.

---

# 18. Performance

Optimize only after measuring.

Prioritize:

- Readability
- Correctness
- Maintainability

Document performance-sensitive optimizations where they exist.

---

# 19. Security

Never:

- Commit secrets
- Trust unvalidated input
- Disable security checks without justification

Validate external inputs and keep dependencies up to date.

---

# 20. Code Review Checklist

Before merging:

- Naming is clear.
- Type hints are present.
- Documentation is updated.
- Tests pass.
- No duplicated logic.
- Logging is appropriate.
- Configuration is externalized.
- Error handling is meaningful.

---

# 21. Future Improvements

As the project grows, consider adopting:

- Static type checking
- Complexity analysis
- Security scanning
- Dependency auditing
- Automated code metrics
- Architecture validation

---

# 22. Related Documents

| Document | Purpose |
|----------|---------|
| `docs/development_workflow.md` | Development lifecycle |
| `docs/testing_strategy.md` | Testing and quality assurance |
| `docs/repository_guidelines.md` | Repository organization |
| `docs/architecture.md` | System architecture |
| `DECISIONS.md` | Architecture decisions |

---

# 23. Summary

The Mahy Mythic Labs coding standards establish a consistent approach to writing high-quality software. By following common conventions, emphasizing readability, enforcing architectural principles, and applying the same standards to both human-written and AI-generated code, the project remains maintainable and scalable as it evolves.