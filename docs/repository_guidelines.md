# 📁 Repository Guidelines

> **Mahy Mythic Labs Repository Guidelines**
>
> Version: 1.0
>
> This document defines the standards for organizing, naming, maintaining, and evolving the Mahy Mythic Labs repository. Its goal is to keep the repository consistent, scalable, and easy to navigate for both human contributors and AI assistants.

---

# 1. Purpose

The repository should be:

- Well organized
- Predictable
- Modular
- Easy to navigate
- Scalable
- Self-documenting

Every file and directory should have a clear purpose.

---

# 2. Repository Principles

The repository follows these principles:

- One responsibility per directory
- One responsibility per document
- Consistent naming
- Documentation-first
- Configuration over hardcoding
- Reusable components
- Minimal duplication

---

# 3. Top-Level Repository Structure

```
Mahy-Mythic-Labs/

archive/
assets/
automation/
config/
docs/
knowledge_base/
production_bible/
projects/
prompts/
src/
templates/
tests/
tools/

README.md
AI_CONTEXT.md
PROJECT_BOARD.md
PROJECT_STATUS.md
DECISIONS.md
CHANGELOG.md
LICENSE
```

Top-level folders should remain stable. New top-level directories should only be introduced when they represent a distinct concern.

---

# 4. Directory Responsibilities

| Directory | Responsibility |
|-----------|----------------|
| `archive/` | Archived projects, assets, and deprecated content |
| `assets/` | Shared reusable assets |
| `automation/` | Automation specifications and workflow definitions |
| `config/` | Runtime configuration |
| `docs/` | Technical documentation |
| `knowledge_base/` | Reusable domain knowledge |
| `production_bible/` | Creative standards and brand identity |
| `projects/` | Episode workspaces |
| `prompts/` | AI prompt library |
| `src/` | Application source code |
| `templates/` | Reusable Markdown and project templates |
| `tests/` | Automated tests |
| `tools/` | Development and utility scripts |

Directories should not overlap in responsibility.

---

# 5. File Naming Convention

Use:

- lowercase
- snake_case
- descriptive names

Examples:

```
production_engine.md

storyboard_generator.md

workflow_manager.py

image_generator.py
```

Avoid:

```
NewFile.py

final2.py

temp.md

abc.py
```

---

# 6. Documentation Rules

Documentation belongs in:

```
docs/
```

Documentation should:

- Explain purpose
- Be version controlled
- Remain implementation independent when appropriate
- Link to related documents
- Stay synchronized with code

---

# 7. Source Code Organization

Application code belongs under:

```
src/
```

Suggested layout:

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

Business logic should not live outside `src/`.

---

# 8. Configuration Management

Configuration belongs under:

```
config/
```

Examples:

```
application.yaml

providers.yaml

models.yaml

logging.yaml

workflow.yaml
```

Do not hardcode:

- API keys
- Paths
- Model names
- Environment-specific values

---

# 9. Asset Organization

Shared assets belong in:

```
assets/
```

Episode-specific assets belong in:

```
projects/<episode_id>/
```

Generated outputs should not be committed unless intentionally preserved.

---

# 10. Knowledge Base

Domain knowledge belongs in:

```
knowledge_base/
```

Knowledge should:

- Be factual
- Be reusable
- Cite reliable sources where applicable
- Avoid duplication across files

---

# 11. Prompt Library

All prompts belong under:

```
prompts/
```

Prompt categories include:

- research
- script
- storyboard
- image
- video
- narration
- quality
- seo
- thumbnail
- system

Prompts should be version controlled and documented.

---

# 12. Templates

Reusable document templates belong in:

```
templates/
```

Templates should avoid project-specific content and serve as starting points for new work.

---

# 13. Episode Workspaces

Each episode is isolated.

Example:

```
projects/

EP001/

episode.md

research/

script/

storyboard/

assets/

audio/

video/

publishing/
```

Episode directories should not reference outputs from other episodes.

---

# 14. Archive Policy

Obsolete or completed materials should be moved to:

```
archive/
```

Do not permanently delete files without a documented reason.

Archived content should remain readable and recoverable.

---

# 15. Dependency Management

Dependencies should be:

- Documented
- Versioned
- Minimized
- Reviewed regularly

Unused dependencies should be removed.

---

# 16. Git Rules

Do not commit:

- Secrets
- API keys
- Generated caches
- Temporary files
- Virtual environments
- Build artifacts

Use `.gitignore` to enforce repository hygiene.

---

# 17. Documentation Maintenance

Whenever the repository structure changes:

Update:

- `README.md`
- `PROJECT_STATUS.md`
- `PROJECT_BOARD.md`
- `docs/architecture.md`
- This document (if applicable)

Documentation should accurately reflect the repository.

---

# 18. Quality Checklist

Before creating a new file or directory, ask:

- Does this already exist?
- Does it fit an existing directory?
- Is the name descriptive?
- Does it duplicate another file?
- Will future contributors understand its purpose?

If the answer is "no" to any question, reconsider the change.

---

# 19. Future Growth

The repository should accommodate:

- New AI providers
- Additional AI agents
- More knowledge domains
- New automation workflows
- Additional deployment targets
- Plugin architecture
- Multi-language support

Growth should occur by extending existing structures rather than creating unnecessary top-level directories.

---

# 20. Related Documents

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `PROJECT_STATUS.md` | Current implementation status |
| `PROJECT_BOARD.md` | Sprint planning and tasks |
| `DECISIONS.md` | Architecture Decision Records |
| `docs/architecture.md` | System architecture |
| `docs/development_workflow.md` | Development process |
| `docs/asset_management.md` | Asset lifecycle and governance |

---

# 21. Summary

The Mahy Mythic Labs repository is organized around clear separation of concerns, reusable components, and long-term maintainability. By following these guidelines, contributors can add new functionality without introducing structural inconsistency or unnecessary complexity, ensuring the repository remains scalable as the platform evolves.