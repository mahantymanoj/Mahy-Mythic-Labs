# AI_CONTEXT.md

> **Purpose:** Persistent AI project context for Mahy Mythic Labs.
>
> This document provides every AI assistant with the minimum required context to understand the project's vision, architecture, standards, and current implementation state before making any changes.

---

# Project Information

| Property | Value |
|----------|-------|
| Project Name | Mahy Mythic Labs |
| Repository Type | AI-First Video Production Platform |
| Primary Language | Python |
| Documentation | Markdown |
| Configuration | YAML |
| Repository Status | Active Development |
| License | MIT |

---

# Project Vision

Mahy Mythic Labs is an AI-powered production platform designed to automatically create high-quality educational and cinematic YouTube content.

The platform combines:

- Artificial Intelligence
- Mythology
- Astronomy
- Science
- History
- Storytelling
- Automation

into a modular production pipeline capable of generating complete videos from a single topic.

---

# Primary Objectives

The platform should be capable of:

- Researching a topic
- Verifying information
- Writing scripts
- Generating storyboards
- Creating image prompts
- Creating video prompts
- Generating narration
- Running quality checks
- Optimizing SEO
- Preparing publishing assets

---

# Supported Content Domains

Current domains include:

- Astronomy
- Mythology
- Ancient History
- Archaeology
- Science
- Artificial Intelligence
- Future Technology

The architecture must support adding new domains without changing the production engine.

---

# Repository Architecture

```
assets/
automation/
docs/
knowledge_base/
production_bible/
prompts/
templates/
projects/
src/
tests/
config/
cache/
logs/
```

---

# Architecture Principles

Every implementation must follow these principles:

1. Modular
2. Scalable
3. Reusable
4. Provider-independent
5. Configuration-driven
6. Event-oriented
7. Maintainable
8. Well documented

---

# Production Workflow

```
Topic
    │
    ▼
Research
    ▼
Script
    ▼
Storyboard
    ▼
Image Prompt
    ▼
Image Generation
    ▼
Video Prompt
    ▼
Video Generation
    ▼
Narration
    ▼
Editing
    ▼
Quality Review
    ▼
SEO
    ▼
Publishing
```

---

# AI Agent Architecture

The production platform consists of specialized agents.

| Agent | Responsibility |
|--------|----------------|
| Master Director | Controls production workflow |
| Research Agent | Research and fact verification |
| Script Agent | Script generation |
| Storyboard Agent | Scene planning |
| Image Agent | Image prompt generation |
| Video Agent | Video prompt generation |
| Narration Agent | Narration generation |
| Quality Agent | Production review |
| SEO Agent | Metadata optimization |
| Publishing Agent | Upload package generation |

Each agent must have a single responsibility and communicate through the production engine.

---

# Production Engine

The production engine is responsible for:

- Workflow execution
- Agent orchestration
- State management
- Context sharing
- Event handling
- Scheduling
- Retry management

The engine should never contain business logic.

Business logic belongs inside the individual AI agents.

---

# AI Provider Strategy

The platform must support multiple AI providers through a common abstraction layer.

Planned providers include:

- OpenAI
- Anthropic
- Google Gemini
- xAI

Agents must never call provider SDKs directly.

All provider interactions should go through the provider layer.

---

# Prompt Strategy

Prompt files are reusable production assets.

Rules:

- Never hardcode prompts inside Python code.
- Keep prompts version-controlled.
- Store prompts in the `prompts/` directory.
- Use templates and variables instead of duplication.

---

# Knowledge Strategy

The `knowledge_base/` directory is the project's long-term factual repository.

Agents should use it as background context before requesting external information.

Knowledge must be:

- Structured
- Reusable
- Referenced
- Easy to expand

---

# Documentation Strategy

Documentation is considered part of the product.

Before implementing new functionality:

1. Review existing documentation.
2. Avoid duplicate documents.
3. Update documentation when architecture changes.
4. Keep cross-references accurate.

---

# Coding Standards

- Python 3.12+
- Type hints
- Dataclasses where appropriate
- Clear docstrings
- Small, focused modules
- No duplicated logic
- Configuration over hardcoded values

---

# Repository Rules

Do not:

- Duplicate files
- Duplicate prompts
- Duplicate templates
- Mix generated assets with source assets
- Commit secrets
- Commit API keys
- Commit generated runtime data

---

# Runtime Rules

Generated episode outputs must remain inside the corresponding project directory.

Example:

```
projects/
    EP001/
    EP002/
```

Shared assets belong in `assets/`.

Generated assets belong in `projects/<episode>/`.

---

# Current Development Phase

Current milestone:

**Phase 2 — Production Engine**

Current focus:

- Engine architecture
- Workflow execution
- Agent framework
- Provider abstraction
- Runtime implementation

Documentation is largely complete.

Implementation is the current priority.

---

# AI Instructions

Before modifying the repository:

1. Read this document.
2. Review the relevant documentation.
3. Follow the Production Bible.
4. Preserve architectural consistency.
5. Avoid unnecessary file creation.
6. Prefer extending existing components over introducing duplicates.
7. Keep changes modular and maintainable.

---

# Long-Term Goal

Create a modular, maintainable, AI-driven production platform capable of transforming a single topic into a fully researched, scripted, generated, reviewed, and publish-ready video with minimal human intervention.