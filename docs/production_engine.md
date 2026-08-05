# ⚙️ Production Engine Specification

> **Mahy Mythic Labs Production Engine**
>
> Version: 1.0
>
> This document defines the architecture, responsibilities, lifecycle, interfaces, and implementation plan for the Production Engine—the runtime core that orchestrates the complete AI video production pipeline.

---

# 1. Purpose

The Production Engine is responsible for coordinating every workflow execution.

It acts as the operating system of Mahy Mythic Labs.

The engine:

- Executes workflows
- Manages AI agents
- Shares context
- Maintains execution state
- Handles retries
- Routes events
- Loads providers
- Tracks progress
- Produces execution reports

Agents should never coordinate themselves.

---

# 2. Design Goals

The engine must be:

- Modular
- Event-driven
- Provider-independent
- Fault tolerant
- Resumable
- Configurable
- Testable
- Extensible

---

# 3. High-Level Architecture

```
User
 │
 ▼
Master Director
 │
 ▼
Production Engine
 │
 ├── Workflow Manager
 ├── Context Manager
 ├── State Manager
 ├── Agent Registry
 ├── Scheduler
 ├── Event Bus
 ├── Provider Manager
 └── Execution Monitor
 │
 ▼
AI Agents
 │
 ▼
AI Providers
 │
 ▼
Episode Workspace
```

---

# 4. Core Responsibilities

The Production Engine owns:

- Workflow execution
- Agent orchestration
- Dependency resolution
- Runtime state
- Shared context
- Event routing
- Scheduling
- Retry policies
- Progress tracking
- Logging
- Metrics
- Error recovery

It does **not** generate content.

---

# 5. Engine Components

## 5.1 Master Director

Responsibilities:

- Load workflow
- Start execution
- Stop execution
- Pause execution
- Resume execution

---

## 5.2 Workflow Manager

Responsible for:

- Reading workflow definitions
- Building execution graph
- Validating dependencies
- Executing stages

---

## 5.3 Agent Registry

Maintains:

- Available agents
- Agent capabilities
- Agent versions
- Agent metadata

Provides:

- Registration
- Discovery
- Lookup

---

## 5.4 Context Manager

Maintains shared runtime context.

Examples:

- Topic
- Research
- Script
- Storyboard
- Metadata
- Prompts
- Asset references
- Configuration

Agents receive only the context they require.

---

## 5.5 State Manager

Tracks:

- Current stage
- Agent status
- Progress
- Retry count
- Outputs
- Errors
- Completion state

State should be serializable for workflow recovery.

---

## 5.6 Event Bus

Publishes runtime events.

Examples:

```
WorkflowStarted
ResearchCompleted
ScriptCompleted
ImageGenerated
VideoGenerated
NarrationCompleted
QualityPassed
WorkflowCompleted
WorkflowFailed
```

Subscribers should remain loosely coupled.

---

## 5.7 Scheduler

Schedules agent execution.

Responsibilities:

- Dependency ordering
- Parallel execution (future)
- Retry scheduling
- Queue management

---

## 5.8 Provider Manager

Loads AI providers.

Responsibilities:

- Provider selection
- Model routing
- Authentication
- Cost tracking
- Failover

---

## 5.9 Execution Monitor

Tracks:

- Runtime duration
- API usage
- Token usage
- Cost
- Performance
- Errors

---

# 6. Execution Lifecycle

```
Initialize
      │
      ▼
Load Configuration
      │
      ▼
Load Workflow
      │
      ▼
Build Context
      │
      ▼
Register Agents
      │
      ▼
Execute Workflow
      │
      ▼
Validate Outputs
      │
      ▼
Generate Reports
      │
      ▼
Complete
```

---

# 7. Workflow Execution

Example pipeline:

```
Research
     │
     ▼
Script
     │
     ▼
Storyboard
     │
     ▼
Image Prompt
     │
     ▼
Image Generation
     │
     ▼
Video Prompt
     │
     ▼
Video Generation
     │
     ▼
Narration
     │
     ▼
Quality
     │
     ▼
SEO
     │
     ▼
Publishing
```

Dependencies must be validated before execution.

---

# 8. Execution State

Each workflow stage may have one of the following states:

```
Pending

Queued

Running

Succeeded

Warning

Retrying

Failed

Cancelled

Completed
```

State transitions must be deterministic and logged.

---

# 9. Context Model

The engine maintains a shared execution context.

Example:

```python
EpisodeContext

topic

research

script

storyboard

assets

metadata

configuration

execution
```

The context evolves as each stage completes.

---

# 10. Error Handling

Recoverable errors:

- Timeout
- Temporary API failure
- Rate limit
- Network interruption

Action:

Retry according to policy.

---

Non-recoverable errors:

- Invalid workflow
- Missing configuration
- Corrupted prompt
- Invalid output schema

Action:

Abort execution and generate a report.

---

# 11. Retry Policy

Each task defines:

- Maximum retries
- Retry interval
- Exponential backoff (optional)
- Fallback provider

Example:

```
Attempt 1

↓

Attempt 2

↓

Switch Provider

↓

Final Failure
```

---

# 12. Logging

The engine produces:

- Engine log
- Workflow log
- Agent log
- Provider log
- Error log
- Metrics log

Logs should be structured for future dashboard integration.

---

# 13. Metrics

Track:

- Execution time
- API requests
- Token usage
- Cost
- Retry count
- Success rate
- Failure rate

Metrics support optimization and monitoring.

---

# 14. Configuration

The engine loads configuration from the `config/` directory.

Configuration includes:

- Providers
- Models
- Workflows
- Logging
- Retry policies
- Output paths

No hardcoded runtime values are permitted.

---

# 15. Episode Workspace

Every execution writes to an isolated workspace.

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

logs/
```

This ensures reproducibility and simplifies debugging.

---

# 16. Extensibility

The engine should support:

- New AI agents
- Additional providers
- Custom workflows
- Plugins
- Parallel execution
- Distributed workers
- Human approval checkpoints

No architectural redesign should be required.

---

# 17. Implementation Roadmap

Implementation order:

1. Engine Core
2. Context Manager
3. State Manager
4. Agent Registry
5. Event Bus
6. Scheduler
7. Workflow Manager
8. Provider Manager
9. Execution Monitor
10. Reporting

Each component should be independently testable.

---

# 18. Related Components

| Component | Responsibility |
|----------|----------------|
| Master Director | Starts and controls workflows |
| Workflow Manager | Defines execution order |
| Context Manager | Shares runtime data |
| State Manager | Tracks execution state |
| Agent Registry | Discovers and manages agents |
| Scheduler | Coordinates execution timing |
| Event Bus | Publishes runtime events |
| Provider Manager | Routes AI requests |
| Execution Monitor | Collects metrics and logs |

---

# 19. Future Enhancements

Planned capabilities:

- Distributed execution
- Parallel agent scheduling
- Human-in-the-loop approvals
- Cost-aware model routing
- Automatic provider failover
- Persistent execution checkpoints
- Real-time monitoring dashboard
- Plugin SDK
- Cloud-native deployment

---

# 20. Summary

The Production Engine is the runtime foundation of Mahy Mythic Labs. It orchestrates workflows, manages state and context, coordinates AI agents, integrates with multiple providers, and ensures reliable, repeatable execution. By centralizing orchestration and separating it from content generation, the engine provides a scalable platform that can evolve as new AI capabilities and workflows are added.