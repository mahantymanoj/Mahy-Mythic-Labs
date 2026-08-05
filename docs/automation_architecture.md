# ⚙️ Automation Architecture

> **Mahy Mythic Labs Automation Architecture**
>
> Version: 1.0
>
> This document describes how Mahy Mythic Labs automates the complete AI video production pipeline, from topic selection to publish-ready assets.

---

# 1. Overview

The automation system orchestrates multiple independent AI agents through a centralized Production Engine.

The automation layer is responsible for:

- Workflow execution
- Agent orchestration
- Context sharing
- State management
- Error recovery
- Retry handling
- Progress tracking
- Cost monitoring
- Logging
- Publishing preparation

Automation is configuration-driven and provider-independent.

---

# 2. Automation Goals

The automation platform should:

- Require minimal human intervention
- Support reusable workflows
- Recover from failures
- Track execution state
- Allow manual checkpoints
- Scale to multiple episodes
- Support multiple AI providers
- Produce reproducible outputs

---

# 3. High-Level Automation Flow

```
User
 │
 ▼
Master Director
 │
 ▼
Production Engine
 │
 ├──────── Workflow
 ├──────── Context
 ├──────── Registry
 ├──────── Scheduler
 ├──────── Events
 └──────── State
 │
 ▼
AI Agents
 │
 ▼
Provider Layer
 │
 ▼
External AI Services
 │
 ▼
Episode Workspace
```

---

# 4. Automation Layers

## Layer 1 — User Layer

Responsible for:

- Topic selection
- Workflow selection
- Manual approvals (optional)

---

## Layer 2 — Orchestration Layer

Responsible for:

- Agent execution
- Workflow control
- Event dispatching
- Scheduling
- State transitions

Primary component:

```
Master Director
```

---

## Layer 3 — Production Engine

The Production Engine coordinates every automation task.

Core modules:

```
Director
Workflow
Registry
Context
Scheduler
Events
State
```

Responsibilities:

- Load workflow
- Load configuration
- Execute agents
- Manage dependencies
- Handle retries
- Persist execution state

---

## Layer 4 — AI Agent Layer

Each task is performed by an independent AI agent.

Current agents:

```
Research Agent
Script Agent
Storyboard Agent
Image Agent
Video Agent
Narration Agent
Quality Agent
SEO Agent
Publishing Agent
```

Each agent has a single responsibility.

Agents never communicate directly.

---

## Layer 5 — Provider Layer

Responsible for communicating with external AI services.

Supported providers:

- OpenAI
- Anthropic
- Google Gemini
- xAI

Future providers can be added without modifying the agents.

---

## Layer 6 — Output Layer

Responsible for writing generated artifacts.

Outputs include:

- research
- script
- storyboard
- prompts
- images
- videos
- narration
- metadata
- reports

Everything is stored inside the episode workspace.

---

# 5. Workflow Execution

Automation follows a predefined workflow.

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
Quality
 ↓
SEO
 ↓
Publishing
```

Every stage waits for the previous stage to complete successfully.

---

# 6. Agent Execution Model

Each agent follows the same lifecycle.

```
Initialize

↓

Load Context

↓

Read Prompt

↓

Read Knowledge

↓

Execute

↓

Validate Output

↓

Save Result

↓

Emit Event

↓

Return Status
```

Possible return states:

- Success
- Warning
- Retry
- Failure

---

# 7. Context Management

A shared execution context is maintained throughout the workflow.

Context includes:

- Topic
- Episode metadata
- Research
- Script
- Storyboard
- Asset references
- Runtime configuration
- Previous outputs

Agents receive only the context relevant to their task.

---

# 8. State Management

The engine maintains runtime state.

Example:

```
Episode Created

↓

Research Running

↓

Research Complete

↓

Script Running

↓

Storyboard Running

↓

Generation Running

↓

Quality Running

↓

Publishing Ready

↓

Completed
```

State is persisted to allow workflow resumption after interruptions.

---

# 9. Event System

The event system enables loose coupling between components.

Example events:

```
EpisodeStarted

ResearchCompleted

ScriptCompleted

StoryboardCompleted

ImageGenerationCompleted

VideoGenerationCompleted

NarrationCompleted

QualityPassed

PublishingReady

EpisodeCompleted

EpisodeFailed
```

Future modules can subscribe to these events without modifying existing code.

---

# 10. Scheduler

The scheduler controls execution order.

Responsibilities:

- Resolve dependencies
- Queue tasks
- Schedule retries
- Manage concurrency
- Track progress

Future enhancements:

- Parallel execution
- Priority queues
- Distributed workers

---

# 11. Retry Strategy

Every task defines:

- Maximum retries
- Retry interval
- Retry conditions

Example:

```
LLM Timeout

↓

Retry

↓

Still Failed

↓

Switch Provider

↓

Still Failed

↓

Abort Workflow
```

---

# 12. Error Handling

Errors are categorized as:

## Recoverable

- API timeout
- Temporary rate limit
- Network interruption

Action:

Retry

---

## Non-Recoverable

- Invalid prompt
- Missing configuration
- Missing workflow
- Corrupted knowledge

Action:

Stop execution and report.

---

# 13. Provider Routing

The provider layer determines which AI service executes each task.

Example:

| Task | Provider |
|------|----------|
| Research | Gemini |
| Script | Claude |
| Storyboard | GPT |
| Image Prompt | GPT |
| Video Prompt | GPT |
| SEO | GPT |

Routing is configurable through YAML.

---

# 14. Workflow Configuration

Automation is driven by workflow definitions.

Example:

```
automation/workflows/

default.yaml

shorts.yaml

documentary.yaml
```

Each workflow specifies:

- stages
- dependencies
- providers
- prompts
- retry policies

---

# 15. Episode Workspace

Each execution has an isolated workspace.

```
projects/

EP001/

research/

script/

storyboard/

assets/

audio/

video/

publishing/
```

No generated content is shared between episodes.

---

# 16. Logging

Every workflow produces:

- execution log
- agent log
- provider log
- error log
- performance metrics

Logs are stored separately from generated assets.

---

# 17. Monitoring

The automation engine tracks:

- execution time
- provider usage
- API cost
- retry count
- failures
- completion rate

Future dashboards can visualize these metrics.

---

# 18. Security

Automation must never expose:

- API keys
- Secrets
- Provider credentials
- Private prompts

Secrets should be loaded from environment variables or secure configuration files.

---

# 19. Future Automation

Planned capabilities include:

- Parallel agent execution
- Human approval checkpoints
- Cloud deployment
- Distributed rendering
- Multi-language production
- Cost optimization
- Automatic model selection
- Plugin architecture
- External knowledge retrieval (RAG)

---

# 20. Summary

The automation architecture transforms Mahy Mythic Labs into an autonomous AI production platform by coordinating specialized agents through a centralized Production Engine.

The system emphasizes modularity, configurability, fault tolerance, and provider independence, enabling scalable production workflows that can evolve without requiring major architectural changes.