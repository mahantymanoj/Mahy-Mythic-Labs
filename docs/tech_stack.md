# 🛠 Technology Stack

> **Mahy Mythic Labs Technology Stack**
>
> Version: 1.0
>
> This document defines the official technology stack used throughout the Mahy Mythic Labs platform. It serves as the single source of truth for programming languages, frameworks, AI providers, infrastructure, development tools, and third-party services.

---

# 1. Purpose

The technology stack is designed to provide:

- Scalability
- Maintainability
- Modularity
- Provider independence
- Long-term stability
- AI-first development

Technology choices should prioritize simplicity, community support, and extensibility.

---

# 2. Technology Principles

The stack should:

- Minimize dependencies
- Prefer mature technologies
- Support multiple AI providers
- Be platform independent
- Remain open for future expansion

---

# 3. Programming Languages

| Technology | Purpose |
|------------|---------|
| Python 3.12+ | Primary application language |
| Markdown | Documentation |
| YAML | Configuration |
| JSON | Data exchange |
| Bash / PowerShell | Automation scripts |

Python is the only language used for application logic.

---

# 4. Python Ecosystem

## Runtime

- Python 3.12+

---

## Package Manager

- pip

Future consideration:

- uv

---

## Virtual Environment

- venv

---

## Dependency Management

Primary:

```
requirements.txt
```

Development:

```
requirements-dev.txt
```

---

# 5. AI Providers

The platform is provider-independent.

Supported providers:

| Provider | Purpose |
|----------|---------|
| OpenAI | GPT models |
| Anthropic | Claude models |
| Google Gemini | Gemini models |
| xAI | Grok models |

Future providers:

- DeepSeek
- Mistral
- Local LLMs
- Ollama
- Hugging Face Inference

---

# 6. AI Models

Examples:

### Text

- GPT-5.x
- Claude Opus
- Claude Sonnet
- Gemini Pro
- Grok

---

### Image

- GPT Image
- Flux
- Imagen
- Stable Diffusion

---

### Video

- Veo
- Runway
- Kling
- Pika
- Luma

---

### Narration

- ElevenLabs
- OpenAI TTS
- Azure Speech

The specific model should be configurable rather than hardcoded.

---

# 7. Core Python Libraries

## HTTP

- httpx

---

## Validation

- pydantic

---

## CLI

- typer

---

## Configuration

- pyyaml
- python-dotenv

---

## Logging

- logging (standard library)

---

## Testing

- pytest
- pytest-cov

---

## Linting

- Ruff

---

## Formatting

- Black

---

## Type Checking

- mypy (future)

---

## Progress Display

- rich
- tqdm

---

# 8. Multimedia Libraries

Required:

- FFmpeg

Optional:

- Pillow
- MoviePy
- OpenCV

These support image, audio, and video processing.

---

# 9. Data Storage

Current:

- File system

Future:

- SQLite
- PostgreSQL
- Vector Database (if semantic search is added)

Structured data should remain portable.

---

# 10. Configuration

Configuration formats:

- YAML
- Environment Variables

Never hardcode:

- API keys
- Model names
- Paths
- Provider settings

---

# 11. Development Tools

Recommended:

- VS Code
- Cursor
- Git
- GitHub

Optional:

- Docker Desktop
- Postman / Bruno
- Obsidian

---

# 12. Documentation Tools

Documentation is written in:

- Markdown

Future options:

- MkDocs
- Material for MkDocs

---

# 13. Version Control

Repository:

Git

Hosting:

GitHub

Branch strategy:

- main
- develop
- feature/*
- release/*
- hotfix/*

---

# 14. Automation

Automation technologies:

- Python
- GitHub Actions
- MCP integrations

Future:

- Celery
- Redis
- Message queues

---

# 15. Testing Stack

Testing framework:

- pytest

Coverage:

- pytest-cov

Mocking:

- unittest.mock

Future:

- Playwright (web automation)
- Benchmark tooling

---

# 16. Security

Security tools:

- python-dotenv
- GitHub Secret Scanning
- Dependabot

Future:

- Trivy
- Bandit

---

# 17. Deployment

Current:

- Local development

Future:

- Docker
- Docker Compose
- AWS
- Azure
- Google Cloud

Deployment should remain cloud agnostic.

---

# 18. Monitoring

Future tools:

- Prometheus
- Grafana
- OpenTelemetry

Initially:

- Structured logging
- Execution reports

---

# 19. YouTube Production Stack

Research

↓

Prompt Engineering

↓

Image Generation

↓

Video Generation

↓

Narration

↓

Editing

↓

SEO

↓

Publishing

Every stage should support multiple providers through a common abstraction.

---

# 20. Future Technology Roadmap

Planned additions:

- Plugin SDK
- Agent marketplace
- MCP Server
- Local AI execution
- GPU acceleration
- Distributed workers
- Web dashboard
- Asset database
- Semantic search
- RAG-powered knowledge retrieval

---

# 21. Technology Selection Criteria

New technologies should satisfy:

- Active maintenance
- Strong documentation
- Community adoption
- Cross-platform compatibility
- Clear licensing
- Long-term viability

Avoid adopting tools solely because they are new or popular.

---

# 22. Related Documents

| Document | Purpose |
|----------|---------|
| `docs/architecture.md` | Overall system architecture |
| `docs/production_engine.md` | Runtime engine |
| `docs/deployment.md` | Deployment strategy |
| `docs/setup.md` | Local development setup |
| `docs/coding_standards.md` | Coding conventions |
| `docs/testing_strategy.md` | Testing strategy |

---

# 23. Summary

Mahy Mythic Labs is built on a Python-first, AI-provider-independent technology stack designed for long-term maintainability and scalability. By standardizing languages, libraries, tools, and infrastructure while keeping providers configurable, the platform remains adaptable to future advances in AI and software engineering.