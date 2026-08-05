# 🏛 System Architecture

> **Mahy Mythic Labs Architecture Documentation**
>
> Version: 1.0
>
> This document describes the overall software architecture, runtime design, component interactions, and design principles of the Mahy Mythic Labs AI Video Production Platform.

---

# 1. System Overview

Mahy Mythic Labs is an AI-powered production platform that automatically transforms a single content idea into a complete, publish-ready YouTube video.

The platform is designed around independent AI agents coordinated by a central Production Engine.

Core characteristics:

- Modular
- Event-driven
- Provider-independent
- Configuration-driven
- Scalable
- Extensible

---

# 2. High-Level Architecture

```

┌─────────────────────────────────────────────┐
│ User │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ Master Director │
└─────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ Production Engine │
│ │
│ • Workflow │
│ • Context │
│ • Registry │
│ • Scheduler │
│ • Events │
│ • State │
└─────────────────────────────────────────────┘
│
├───────────────┬─────────────────┬─────────────────┐
▼ ▼ ▼
Research Script Storyboard
Agent Agent Agent

│ │ │

▼ ▼ ▼
Image Video Narration
Agent Agent Agent

│
▼

Quality Agent

│
▼

SEO Agent

│
▼

Publishing Agent

```

---

# 3. Repository Architecture

```

Mahy-Mythic-Labs/

assets/
automation/
cache/
config/
docs/
knowledge_base/
logs/
production_bible/
projects/
prompts/
src/
templates/
tests/

```

Each directory has a single responsibility.

---

# 4. Runtime Architecture

```

User
│
▼

Master Director

│
▼

Workflow Engine

│
▼

Context Manager

│
▼

AI Agents

│
▼

Provider Layer

│
▼

External AI APIs

```

---

# 5. Production Pipeline

```

Topic

↓

Research

↓

Script

↓

Storyboard

↓

Image Prompt

↓

Image Generation

↓

Video Prompt

↓

Video Generation

↓

Narration

↓

Editing

↓

Quality

↓

SEO

↓

Publishing

```

---

# 6. AI Agent Architecture

Each AI capability is implemented as an independent agent.

| Agent | Responsibility |
|----------|-------------------------------------|
| Master Director | Controls production |
| Research Agent | Research |
| Script Agent | Script generation |
| Storyboard Agent | Scene planning |
| Image Agent | Image prompts |
| Video Agent | Video prompts |
| Narration Agent | Narration |
| Quality Agent | Validation |
| SEO Agent | Optimization |
| Publishing Agent | Publishing package |

Agents never communicate directly with each other.

All communication passes through the Production Engine.

---

# 7. Production Engine

The Production Engine coordinates the entire system.

Components:

- Director
- Workflow
- Context
- Registry
- State
- Events
- Scheduler

Responsibilities:

- execute workflow
- share context
- retry failures
- maintain state
- schedule agents
- emit events

---

# 8. Provider Layer

The Provider Layer isolates AI providers from business logic.

Supported providers:

- OpenAI
- Anthropic
- Google Gemini
- xAI

```

Agent

↓

Provider Interface

↓

Specific Provider

↓

LLM API

```

Changing providers should never require changing agent code.

---

# 9. Knowledge Architecture

```

knowledge_base/

astronomy/

history/

mythology/

science/

references/

```

Knowledge is reusable.

Agents consume knowledge before external searches.

---

# 10. Prompt Architecture

```

prompts/

research/

script/

storyboard/

image/

video/

quality/

seo/

system/

```

Prompts are treated as production assets.

No prompts should be embedded in Python source code.

---

# 11. Asset Architecture

Assets are divided into:

## Source Assets

- logos
- fonts
- branding
- licensed music

## Generated Assets

Episode-specific outputs:

```

projects/

EP001/

assets/

audio/

video/

```

Generated assets should not pollute shared asset directories.

---

# 12. Episode Architecture

Each episode is completely isolated.

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

This enables:

- reproducibility
- archiving
- debugging
- independent rendering

---

# 13. Configuration Architecture

Configuration is stored under:

```

config/

```

Configuration includes:

- models
- providers
- paths
- logging
- runtime settings

No hardcoded configuration is allowed.

---

# 14. Event Flow

```

Research Completed

↓

Script Started

↓

Script Completed

↓

Storyboard Started

↓

Image Started

↓

Video Started

↓

Narration Started

↓

Quality Review

↓

Publishing

```

---

# 15. State Management

The engine maintains:

- workflow state
- episode state
- execution history
- retry information
- metadata

State is stored independently of business logic.

---

# 16. Error Handling

Every agent should return:

- Success
- Warning
- Retry
- Failure

The Production Engine determines recovery behavior.

---

# 17. Scalability

Future architecture supports:

- parallel agents
- distributed execution
- cloud deployment
- multiple providers
- plugin architecture
- additional content domains

No architectural redesign should be required.

---

# 18. Design Principles

The project follows these principles:

- Single Responsibility
- Separation of Concerns
- Dependency Inversion
- Provider Abstraction
- Modular Design
- Configuration over Code
- Reusable Components
- Documentation First

---

# 19. Future Architecture

Planned additions include:

- Web dashboard
- REST API
- Plugin SDK
- Distributed workers
- Cost optimization
- Vector database
- RAG pipeline
- Multi-language support
- Cloud deployment

---

# 20. Summary

Mahy Mythic Labs is designed as a modular AI production platform where a central Production Engine orchestrates specialized AI agents through a provider abstraction layer.

The architecture separates documentation, knowledge, prompts, configuration, runtime code, and generated assets into distinct layers, ensuring maintainability, scalability, and long-term extensibility.