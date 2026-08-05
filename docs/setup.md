# 🛠 Setup Guide

> **Mahy Mythic Labs Development Setup**
>
> Version: 1.0
>
> This document explains how to install, configure, and verify a local development environment for Mahy Mythic Labs.

---

# 1. Purpose

This guide enables developers to:

- Clone the repository
- Install dependencies
- Configure AI providers
- Verify the installation
- Run the project locally

It applies only to local development.

Production deployment is documented separately in `docs/deployment.md`.

---

# 2. Prerequisites

Required software:

| Software | Version |
|-----------|----------|
| Git | Latest Stable |
| Python | 3.12+ |
| FFmpeg | Latest Stable |
| VS Code / Cursor | Latest |
| Docker (Optional) | Latest |
| Git LFS (Optional) | Latest |

---

# 3. Recommended Hardware

Minimum:

- 4 CPU cores
- 8 GB RAM
- 20 GB free disk space

Recommended:

- 8+ CPU cores
- 16 GB RAM
- SSD Storage

---

# 4. Clone Repository

```bash
git clone https://github.com/<username>/Mahy-Mythic-Labs.git

cd Mahy-Mythic-Labs
```

---

# 5. Create Virtual Environment

Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

# 6. Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

Developer dependencies

```bash
pip install -r requirements-dev.txt
```

---

# 7. Verify Python

```bash
python --version
```

Expected:

```
Python 3.12+
```

---

# 8. Repository Structure

Important directories:

```
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
```

Do not modify the repository structure without updating the documentation.

---

# 9. Environment Variables

Create:

```
.env
```

Example:

```text
OPENAI_API_KEY=

ANTHROPIC_API_KEY=

GOOGLE_API_KEY=

XAI_API_KEY=

YOUTUBE_CLIENT_ID=

YOUTUBE_CLIENT_SECRET=

YOUTUBE_REFRESH_TOKEN=
```

Never commit `.env`.

---

# 10. Configuration Files

Configuration directory:

```
config/
```

Example:

```
application.yaml

providers.yaml

workflow.yaml

logging.yaml

models.yaml
```

Configuration should remain outside application code.

---

# 11. Install FFmpeg

Verify installation:

```bash
ffmpeg -version
```

If FFmpeg is unavailable, video generation and processing may fail.

---

# 12. Verify Installation

Run:

```bash
python --version

pip --version

ffmpeg -version

git --version
```

All commands should complete successfully.

---

# 13. Run the Project

Current example:

```bash
python main.py
```

Future CLI:

```bash
python -m src.cli

or

mml run
```

---

# 14. Verify AI Providers

Check configuration:

```bash
python scripts/check_providers.py
```

Expected:

```
OpenAI

✓ Connected

Anthropic

✓ Connected

Gemini

✓ Connected
```

(Provider validation script to be implemented.)

---

# 15. Verify Repository

Recommended checks:

```bash
ruff check .

black --check .

pytest
```

All validation checks should pass before committing code.

---

# 16. Recommended VS Code Extensions

- Python
- Pylance
- Ruff
- Black Formatter
- GitLens
- Markdown All in One
- Error Lens
- YAML
- Docker

---

# 17. Troubleshooting

## Virtual Environment Not Activated

Verify:

```bash
python --version

where python
```

---

## Missing API Key

Check:

```
.env
```

Ensure required variables are defined.

---

## FFmpeg Not Found

Verify:

```bash
ffmpeg -version
```

Add FFmpeg to your system PATH if necessary.

---

## Dependency Errors

Upgrade pip:

```bash
pip install --upgrade pip
```

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

---

## Import Errors

Confirm:

- Virtual environment is active.
- Dependencies are installed.
- Working directory is the repository root.

---

# 18. Development Checklist

Before starting development:

- Repository cloned
- Virtual environment created
- Dependencies installed
- Environment variables configured
- FFmpeg installed
- Tests passing
- Linting successful

---

# 19. Related Documents

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `docs/development_workflow.md` | Development process |
| `docs/coding_standards.md` | Coding conventions |
| `docs/testing_strategy.md` | Testing approach |
| `docs/deployment.md` | Production deployment |
| `docs/repository_guidelines.md` | Repository organization |

---

# 20. Summary

This setup guide provides a standardized process for preparing a local Mahy Mythic Labs development environment. By following these steps, contributors can install dependencies, configure AI providers, verify their environment, and begin development with a consistent and reproducible setup.