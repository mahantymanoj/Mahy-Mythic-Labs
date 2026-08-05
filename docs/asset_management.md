# Asset Management — Mahy Mythic Labs

## 1. Purpose

The **Mahy Mythic Labs Asset Management System** defines how all creative assets are created, stored, organized, versioned, tracked, and reused throughout the production lifecycle.

The objective is to build a professional media asset management system that supports:

* AI-generated images
* AI-generated videos
* Audio files
* Music
* Sound effects
* Scripts
* Prompts
* Research documents
* Thumbnails
* Branding materials

A well-structured asset system ensures:

* Faster production
* Better consistency
* Easy reuse
* Version control
* Scalable automation

---

# 2. Asset Management Philosophy

Every asset created for Mahy Mythic Labs should be:

```text id="6l1x4k"
Organized

+

Searchable

+

Reusable

+

Version Controlled

+

Production Ready
```

Assets are not temporary files; they become part of the long-term creative library.

---

# 3. Asset Categories

Mahy Mythic Labs assets are divided into:

```text id="q1sh4m"
Creative Assets

Technical Assets

Knowledge Assets

Brand Assets

Production Assets
```

---

# 4. Asset Directory Architecture

Main asset structure:

```text id="3vh7hp"
assets/

├── branding/
│
├── fonts/
│
├── logos/
│
├── music/
│
├── references/
│
├── sfx/
│
├── images/
│
├── videos/
│
├── audio/
│
└── thumbnails/
```

---

# 5. Branding Assets

Location:

```text id="p8l3yf"
assets/branding/
```

Contains:

* Brand guidelines
* Color palette
* Visual identity
* Channel graphics

Example:

```text id="x2az0u"
branding/

├── brand_guidelines.md
├── color_palette.md
└── visual_identity.md
```

---

# 6. Logo Management

Location:

```text id="0t6w0v"
assets/logos/
```

Contains:

* Channel logo
* Watermark
* Social media logos
* Project logos

Structure:

```text id="6dv2qv"
logos/

├── primary/
├── variations/
└── social/
```

---

# 7. Font Management

Location:

```text id="w8s8jg"
assets/fonts/
```

Contains:

* Title fonts
* Subtitle fonts
* Thumbnail fonts

Maintain:

```text id="4kdj0p"
Font Name

License Information

Usage Purpose
```

---

# 8. Image Asset Management

Location:

```text id="m2v6m8"
assets/images/
```

Categories:

```text id="q5h0z1"
images/

├── characters/
├── environments/
├── mythology/
├── astronomy/
├── science/
├── concepts/
└── thumbnails/
```

---

# Image Naming Convention

Format:

```text id="1n5h3c"
CATEGORY_SUBJECT_VERSION_DATE
```

Example:

```text id="h2y7kd"
SHIVA_KAILASH_SCENE01_V01_20260805.png
```

---

# Image Metadata

Every important image should maintain:

```text id="t3v4md"
Asset ID:

Episode:

Prompt Used:

AI Model:

Generation Date:

Resolution:

Usage:
```

---

# 9. Video Asset Management

Location:

```text id="6z4m0v"
assets/videos/
```

Structure:

```text id="jx8f4r"
videos/

├── raw/
├── generated/
├── edited/
└── final/
```

---

# Video Naming Convention

Format:

```text id="4h3l9v"
EPISODE_SCENE_VERSION
```

Example:

```text id="v9j5k2"
MML_EP001_SCENE05_V02.mp4
```

---

# Video Metadata

Track:

```text id="x8bq9r"
Duration:

Resolution:

Frame Rate:

AI Tool:

Prompt:

Scene Number:

Status:
```

---

# 10. Audio Asset Management

Location:

```text id="8m7z2c"
assets/audio/
```

Structure:

```text id="k0f2w1"
audio/

├── narration/
├── music/
├── effects/
└── final_mix/
```

---

# Narration Assets

Track:

```text id="d8h4r7"
Voice Model:

Language:

Emotion:

Speed:

Version:
```

---

# Music Assets

Location:

```text id="v2n9x3"
assets/music/
```

Track:

```text id="g4m7s8"
Composer:

License:

Mood:

Usage:

Copyright Status:
```

---

# Sound Effects

Location:

```text id="n5p1q8"
assets/sfx/
```

Categories:

```text id="3q7x1b"
Nature

Cosmic

Atmosphere

Action

Fantasy
```

---

# 11. Prompt Asset Management

Prompts are valuable creative assets.

Location:

```text id="j8f3n6"
prompts/
```

Structure:

```text id="p3x9m4"
prompts/

├── image/
├── video/
├── narration/
├── thumbnail/
├── system/
└── agents/
```

---

# Prompt Versioning

Example:

```text id="r7k2d9"
SHIVA_COSMIC_PROMPT

V01

↓

V02

↓

V03
```

Track:

* Changes
* Improvements
* Results

---

# 12. Episode Asset Structure

Each episode maintains its own assets.

Example:

```text id="s5w8q0"
projects/

└── MML_EP001/

    ├── research/

    ├── script/

    ├── storyboard/

    ├── assets/

    │   ├── images/
    │   ├── videos/
    │   ├── audio/
    │   └── thumbnails/

    ├── editing/

    └── upload/
```

---

# 13. Asset Tracking System

Every major asset should be registered.

Template:

```text id="z2m5q7"
Asset ID:

Asset Type:

File Location:

Episode:

Creator:

AI Tool:

Creation Date:

Version:

Approval Status:

Usage:
```

---

# 14. Asset Lifecycle

Every asset follows:

```text id="n9x4k6"
Created

↓

Reviewed

↓

Approved

↓

Used

↓

Archived

↓

Reusable Library
```

---

# 15. Version Control Strategy

Version format:

```text id="b3k8p1"
V01
V02
V03
FINAL
FINAL_APPROVED
```

Example:

```text id="y7m2r5"
EP001_SCRIPT_V03.md

EP001_SCRIPT_FINAL.md
```

---

# 16. Archive Management

Location:

```text id="4p8s0z"
archive/
```

Used for:

* Old versions
* Rejected assets
* Previous episodes
* Experiments

Structure:

```text id="q6m1t8"
archive/

├── old_projects/
├── old_assets/
└── experiments/
```

---

# 17. Backup Strategy

Assets should exist in multiple locations.

Recommended:

```text id="k8v2m4"
Primary Storage

↓

Local Backup

↓

Cloud Backup
```

Possible cloud storage:

* AWS S3
* Google Cloud Storage
* Azure Blob Storage

---

# 18. Copyright Management

Every external asset must track:

```text id="c5h9z3"
Source:

License:

Permission:

Usage Rights:

Attribution Required:
```

Never use assets without verifying rights.

---

# 19. AI Generated Asset Tracking

For AI-generated assets record:

```text id="u4x8n7"
AI Model:

Prompt:

Parameters:

Generation Date:

Reference Images:

Modifications:
```

Purpose:

* Reproduce assets
* Improve future generations
* Maintain consistency

---

# 20. Asset Search Strategy

Assets should be searchable by:

## Episode

Example:

```text
MML_EP001
```

## Category

Example:

```text
Shiva
Galaxy
Temple
```

## Usage

Example:

```text
Thumbnail
Background
Character
```

---

# 21. Future AI Asset Manager

Future AI Agent:

```text id="w3q9s5"
Asset Management Agent

Responsibilities:

- Organize files
- Rename assets
- Detect duplicates
- Track versions
- Search assets
- Recommend reuse
```

Architecture:

```text id="m7k2v8"
AI Agent

↓

Asset Database

↓

Storage System

↓

Production Pipeline
```

---

# 22. Asset Database Future

Future implementation:

```text id="h5r8p2"
Asset Database

Fields:

Asset ID

Type

Location

Episode

Tags

Prompt

AI Model

License

Version

Status
```

---

# 23. Asset Quality Standards

Every production asset must satisfy:

## Visual

✓ High resolution
✓ Consistent style
✓ No artifacts

## Audio

✓ Clear quality
✓ Balanced levels

## Documentation

✓ Proper naming
✓ Metadata stored

---

# Conclusion

The Mahy Mythic Labs Asset Management System creates a professional foundation for scaling AI-powered content production.

A strong asset system enables:

```text id="x1z6m9"
Faster Production

+

Creative Consistency

+

Automation

+

Long-Term Knowledge Building
```

The goal is to transform every generated asset into a reusable building block of the Mahy Mythic Labs creative universe.
