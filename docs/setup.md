# Development Environment Setup

**Project:** Mahy Mythic Labs Studio OS

**Document Version:** 1.0

**Last Updated:** 05-Aug-2026

---

# Purpose

This document explains how to set up the complete Mahy Mythic Labs Studio development environment on a new computer.

Following this guide should allow anyone to recreate the production workspace with minimal effort.

This document should be updated whenever new tools become part of the standard workflow.

---

# Minimum System Requirements

Recommended hardware for AI-assisted content creation.

## Operating System

* Windows 11 (Primary)
* Ubuntu Linux (Supported)
* macOS (Supported)

---

## Processor

* Intel Core i5 (12th Generation or newer)
* AMD Ryzen 5 (5000 Series or newer)

Recommended:

* Intel Core i7
* AMD Ryzen 7

---

## Memory

Minimum

* 16 GB RAM

Recommended

* 32 GB RAM

---

## Storage

Minimum

* 512 GB SSD

Recommended

* 1 TB NVMe SSD

Suggested folder organization:

```
D:\Mahy-Mythic-Labs
```

---

## Internet

Reliable broadband connection for:

* AI tools
* Research
* Software updates
* GitHub synchronization

---

# Required Software

## Git

Purpose

Version control.

Installation

https://git-scm.com/

Verify

```
git --version
```

---

## Visual Studio Code

Purpose

Primary development environment.

Installation

https://code.visualstudio.com/

Recommended Extensions

* Markdown All in One
* GitLens
* Error Lens
* Material Icon Theme
* Markdown Preview Enhanced
* Python
* YAML
* GitHub Pull Requests
* Better Comments

---

## Python

Purpose

Local helper scripts and automation.

Recommended Version

Python 3.12+

Verify

```
python --version
```

---

## GitHub Desktop (Optional)

Purpose

Visual Git management.

Useful for beginners.

---

## Video Editing Software

Primary Recommendation

DaVinci Resolve

Alternative

CapCut Desktop

---

## Image Editing

Recommended

GIMP

Alternative

Photopea (Browser)

---

## Audio Editing

Recommended

Audacity

---

# Repository Setup

Clone the repository.

```
git clone <repository-url>
```

Enter the project.

```
cd Mahy-Mythic-Labs
```

Open VS Code.

```
code .
```

---

# Repository Verification

Verify the following folders exist.

```
docs/

production_bible/

knowledge_base/

templates/

prompts/

projects/

assets/

automation/

tools/

archive/
```

---

# Git Configuration

Configure Git identity.

```
git config --global user.name "Your Name"

git config --global user.email "your-email@example.com"
```

Verify configuration.

```
git config --global --list
```

---

# Standard Workflow

Every development session should follow this sequence.

```
Pull Latest Changes

↓

Open Project Board

↓

Select Current Task

↓

Complete Documentation

↓

Commit Changes

↓

Push to GitHub
```

---

# Commit Guidelines

Every commit should describe one logical change.

Examples

```
Add mission document v1.0

Complete roadmap document

Update production workflow

Improve storyboard template

Add Episode 001 research
```

Avoid vague commit messages such as:

* Update
* Fix
* Changes
* Miscellaneous

---

# Recommended Workspace

Example directory structure.

```
Mahy-Mythic-Labs/

VS Code

GitHub Desktop

DaVinci Resolve Projects

Assets

Downloads
```

Keep project assets organized and avoid storing production files randomly across the system.

---

# Backup Strategy

Protect project data by maintaining multiple copies.

Recommended approach:

* Local Git repository
* GitHub repository
* Periodic backup of assets to an external drive

Documentation should always remain synchronized with GitHub.

---

# Troubleshooting

## Git Authentication Issues

Verify Git configuration.

Sign in to GitHub.

Confirm remote repository URL.

---

## Repository Not Updating

Run

```
git pull
```

before starting work.

---

## Merge Conflicts

Review changes carefully.

Resolve conflicts before committing.

---

## Missing Files

Restore the latest version from Git history.

Avoid deleting tracked files directly.

---

# Setup Checklist

Before beginning work, verify:

* Git is installed.
* VS Code is installed.
* Python is installed.
* Repository is cloned.
* GitHub connection works.
* Required folders exist.
* Project Board is available.
* Documentation opens correctly.

---

# Future Improvements

Future setup enhancements may include:

* Local documentation website
* Python virtual environment
* Helper scripts
* Automated project scaffolding
* Local asset indexing
* Documentation search

These additions should simplify the workflow without increasing unnecessary complexity.

---

# Revision History

| Version | Date        | Description                                  |
| ------- | ----------- | -------------------------------------------- |
| 1.0     | 05-Aug-2026 | Initial development environment setup guide. |
