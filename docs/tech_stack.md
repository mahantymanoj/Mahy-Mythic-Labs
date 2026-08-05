# Technology Stack

**Project:** Mahy Mythic Labs Studio OS

**Document Version:** 1.0

**Last Updated:** 05-Aug-2026

---

# Purpose

This document defines the official technology stack used by Mahy Mythic Labs.

The objective is to standardize the software, tools, platforms, and technologies used throughout the content production pipeline.

The technology stack should evolve as better tools become available, while maintaining compatibility with the established production workflow.

---

# Technology Philosophy

Mahy Mythic Labs follows these principles when selecting tools:

* Prioritize quality over popularity.
* Prefer tools with free tiers or trial credits whenever practical.
* Use local software where possible.
* Avoid unnecessary vendor lock-in.
* Keep the workflow simple and maintainable.
* Replace tools only when there is a clear improvement.

---

# Production Pipeline

```text
Research
      ↓
Story Writing
      ↓
Script Creation
      ↓
Storyboard
      ↓
Image Generation
      ↓
Video Generation
      ↓
Narration
      ↓
Music
      ↓
Editing
      ↓
Thumbnail
      ↓
SEO
      ↓
Publishing
```

---

# Core Development Tools

## Visual Studio Code

**Purpose**

Primary workspace for documentation, prompts, templates, and project management.

**Status**

Official Development Environment

---

## Git

**Purpose**

Version control for all project files.

**Status**

Required

---

## GitHub

**Purpose**

Repository hosting, backup, collaboration, and version history.

**Status**

Required

---

## Python

**Purpose**

Local helper scripts, utilities, and future automation.

Automation should support production rather than replace creativity.

**Status**

Supported

---

# AI Writing & Research

## ChatGPT

**Purpose**

Research assistance, documentation, brainstorming, prompt engineering, scripting, planning, and production guidance.

---

## Claude

**Purpose**

Long-form writing, document refinement, reasoning, and editorial review.

---

## Web Research

Primary Sources:

* Academic publications
* Museums
* Archaeological reports
* Government organizations
* Scientific journals
* Official space agencies
* Trusted historical references

Information should always be validated before publication.

---

# Image Generation

The image generation tool may change over time.

Selection Criteria:

* Photorealistic quality
* Cinematic composition
* Prompt accuracy
* Character consistency
* Lighting quality
* Camera control

Example Categories:

* General AI Image Generator
* Photorealistic Image Generator
* Character Generation
* Concept Art Generator

---

# Video Generation

Video generation technology changes rapidly.

Selection Criteria:

* Realistic motion
* Cinematic camera movement
* Character consistency
* Lighting consistency
* Natural animation
* Prompt controllability

The Studio OS is designed to remain compatible with different AI video platforms.

---

# Narration

Narration tools should provide:

* Natural speech
* Emotional control
* Multiple languages
* Voice consistency
* High audio quality

Narration style should match the video's genre.

Examples:

* Documentary
* Spiritual
* Historical
* Epic
* Suspense

---

# Background Music

Music should support the story rather than dominate it.

Preferred characteristics:

* Cinematic
* Emotional
* Royalty-free or appropriately licensed
* Genre-appropriate
* Consistent audio quality

---

# Video Editing

Primary Recommendation:

DaVinci Resolve

Responsibilities:

* Editing
* Transitions
* Color grading
* Audio mixing
* Titles
* Final rendering

Alternative editors may be evaluated as production needs evolve.

---

# Image Editing

Used for:

* Thumbnail enhancement
* Branding
* Image corrections
* Asset preparation

Preferred characteristics:

* Layer support
* Non-destructive editing
* High-resolution export

---

# Audio Editing

Used for:

* Noise reduction
* Audio balancing
* Voice enhancement
* Music mixing
* Sound effects

---

# Project Management

Primary tools:

* Git
* GitHub
* Project Board
* Documentation

The repository itself acts as the production management system.

---

# File Formats

## Documentation

* Markdown (.md)

---

## Images

* PNG
* JPG
* WEBP

---

## Video

* MP4
* MOV

---

## Audio

* WAV
* MP3

---

## Scripts

* Python (.py)

---

# Naming Standards

Documentation:

```text
mission.md
vision.md
workflow.md
```

Projects:

```text
Episode_001
Episode_002
Episode_003
```

Assets:

```text
ep001_scene01.png
ep001_scene01.mp4
ep001_voice.wav
```

Consistent naming improves organization and automation readiness.

---

# Tool Evaluation Checklist

Before adopting a new tool, evaluate:

* Does it improve quality?
* Does it simplify the workflow?
* Is it reliable?
* Does it fit the Studio OS?
* Can it be replaced easily if necessary?
* Is the learning curve reasonable?

A new tool should solve a real problem rather than add unnecessary complexity.

---

# Future Technology

Potential future additions include:

* Local AI models
* AI-assisted asset management
* Local documentation website
* Python production utilities
* Metadata generation
* Subtitle generation
* Analytics dashboards

These should integrate with the existing architecture instead of replacing it.

---

# Maintenance Policy

Review this document periodically.

Update the technology stack when:

* A significantly better tool becomes available.
* Existing tools are discontinued.
* Production requirements change.
* Workflow improvements are adopted.

---

# Revision History

| Version | Date        | Description                                              |
| ------- | ----------- | -------------------------------------------------------- |
| 1.0     | 05-Aug-2026 | Initial technology stack for Mahy Mythic Labs Studio OS. |
