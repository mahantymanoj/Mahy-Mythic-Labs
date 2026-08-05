# 📘 DECISIONS.md

> **Purpose:** Maintain a permanent record of architectural and technical decisions made throughout the Mahy Mythic Labs project.
>
> This document explains **what was decided**, **why it was decided**, **alternatives considered**, and **the expected impact**. Every major architectural decision should be documented here before implementation.

---

# Decision Record Format

Each decision should follow this structure:

| Field | Description |
|--------|-------------|
| Decision ID | Unique identifier (ADR-001, ADR-002, ...) |
| Date | Decision date |
| Status | Proposed / Accepted / Deprecated / Superseded |
| Category | Architecture, Runtime, AI, Repository, Infrastructure, etc. |
| Decision | Summary of the decision |
| Context | Why the decision was needed |
| Alternatives | Other options considered |
| Consequences | Benefits and trade-offs |

---

# ADR-001 — Documentation-First Development

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Development Process |
| Date | YYYY-MM-DD |

## Decision

Complete the documentation, architecture, prompt library, production standards, and templates before implementing production code.

## Context

The platform is expected to scale into a large AI production system with many independent modules. A strong documentation foundation reduces ambiguity and improves consistency.

## Alternatives Considered

- Code-first development
- Documentation after implementation

## Consequences

### Advantages

- Clear architecture
- Easier onboarding
- Consistent implementation
- Better AI collaboration

### Trade-offs

- Longer initial planning phase

---

# ADR-002 — Modular Repository Architecture

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Repository |
| Date | YYYY-MM-DD |

## Decision

Separate documentation, knowledge, prompts, templates, runtime code, generated projects, and assets into dedicated top-level directories.

## Context

Different concerns should remain isolated to improve maintainability and scalability.

## Consequences

### Advantages

- Cleaner repository
- Easier navigation
- Better scalability

---

# ADR-003 — Production Engine Architecture

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Architecture |
| Date | YYYY-MM-DD |

## Decision

Introduce a dedicated production engine responsible for workflow orchestration, state management, event handling, scheduling, and execution.

## Context

AI agents should focus on business logic while orchestration remains centralized.

## Components

- Director
- Workflow
- Registry
- Context
- State
- Scheduler
- Events

## Consequences

### Advantages

- Loose coupling
- Reusable workflows
- Easier testing
- Future parallel execution

---

# ADR-004 — Single Responsibility AI Agents

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | AI Architecture |
| Date | YYYY-MM-DD |

## Decision

Each AI agent must have one clearly defined responsibility.

Examples:

- Research Agent
- Script Agent
- Storyboard Agent
- Image Agent
- Video Agent
- Narration Agent
- Quality Agent
- SEO Agent
- Publishing Agent

## Context

Keeping responsibilities focused makes agents easier to maintain, test, and replace.

---

# ADR-005 — Provider Abstraction Layer

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | AI Providers |
| Date | YYYY-MM-DD |

## Decision

AI agents must never communicate directly with provider SDKs.

All interactions must go through a provider abstraction layer.

Supported providers include:

- OpenAI
- Anthropic
- Google Gemini
- xAI

## Context

This allows providers to be added or replaced without modifying agent logic.

---

# ADR-006 — Prompt-Driven AI System

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Prompt Engineering |
| Date | YYYY-MM-DD |

## Decision

Store prompts as version-controlled Markdown files instead of embedding them in Python code.

## Context

Prompt engineering is treated as a reusable project asset.

## Consequences

- Easier maintenance
- Version history
- Better collaboration
- Independent prompt improvements

---

# ADR-007 — Knowledge Base as Primary Reference

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Knowledge Management |
| Date | YYYY-MM-DD |

## Decision

The `knowledge_base/` directory serves as the project's primary factual repository.

AI agents should use this knowledge before requesting additional external information.

## Consequences

- Better consistency
- Reduced duplicate research
- Faster content generation

---

# ADR-008 — Episode-Centric Runtime

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Runtime |
| Date | YYYY-MM-DD |

## Decision

Each production run should execute within its own project directory.

Example:

```text
projects/
├── EP001/
├── EP002/
└── EP003/
```

Generated assets, scripts, logs, and metadata remain isolated per episode.

## Consequences

- Easier debugging
- Better reproducibility
- Simpler archiving

---

# ADR-009 — Generated Assets Are Not Source Assets

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Asset Management |
| Date | YYYY-MM-DD |

## Decision

Separate source-controlled assets from AI-generated outputs.

### Source Assets

- Logos
- Fonts
- Branding
- Licensed resources

### Generated Assets

- Images
- Videos
- Narration
- Temporary files

Generated outputs should be stored within the corresponding project workspace whenever practical.

---

# ADR-010 — Configuration-Driven System

| Property | Value |
|----------|-------|
| Status | Accepted |
| Category | Configuration |
| Date | YYYY-MM-DD |

## Decision

Avoid hardcoded values.

Models, providers, paths, and runtime settings should be defined in configuration files.

## Benefits

- Easier environment changes
- Better portability
- Simpler maintenance

---

# Future Decisions

Record future architectural decisions here using the same ADR format.

Examples:

- Cloud deployment strategy
- Database selection
- Vector database adoption
- Authentication
- Plugin architecture
- Distributed execution
- Cost optimization
- Caching strategy
- Model routing
- Multi-language support

---

# Decision Guidelines

A new ADR should be created whenever a change affects:

- Repository structure
- System architecture
- AI workflow
- Runtime behavior
- External integrations
- Development standards
- Security
- Deployment
- Scalability

Minor implementation details do not require an ADR.

---

# Current Status

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Documentation-First Development | ✅ Accepted |
| ADR-002 | Modular Repository Architecture | ✅ Accepted |
| ADR-003 | Production Engine Architecture | ✅ Accepted |
| ADR-004 | Single Responsibility AI Agents | ✅ Accepted |
| ADR-005 | Provider Abstraction Layer | ✅ Accepted |
| ADR-006 | Prompt-Driven AI System | ✅ Accepted |
| ADR-007 | Knowledge Base as Primary Reference | ✅ Accepted |
| ADR-008 | Episode-Centric Runtime | ✅ Accepted |
| ADR-009 | Generated Asset Strategy | ✅ Accepted |
| ADR-010 | Configuration-Driven System | ✅ Accepted |