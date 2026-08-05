# Mahy Mythic Labs Naming Conventions

**Document Version:** 1.0

**Category:** Studio Documentation

**Status:** Active

**Last Updated:** 05-Aug-2026

---

# Preface

A creative studio generates thousands of assets during production.

Without consistent naming conventions, finding, managing, and reusing assets becomes difficult.

Mahy Mythic Labs follows engineering-style naming practices to maintain:

* Organization.
* Searchability.
* Version control.
* Scalability.
* Collaboration readiness.

The objective:

> Every file should explain what it is without opening it.

---

# Naming Philosophy

All names should be:

* Clear.
* Consistent.
* Descriptive.
* Machine-friendly.
* Easy to search.

Avoid:

* Spaces.
* Random names.
* Personal naming styles.
* Unclear abbreviations.

---

# General Naming Rules

## Rule 1 — Use Lowercase

Preferred:

```
ancient_india_research.md
```

Avoid:

```
AncientIndiaResearch.md
```

---

## Rule 2 — Use Underscore Separator

Preferred:

```
character_profile_shiva.md
```

Avoid:

```
character-profile-shiva.md
```

---

## Rule 3 — Avoid Special Characters

Avoid:

```
@ # $ % & *
```

Allowed:

```
_
-
.
```

---

## Rule 4 — Use Version Numbers

When files evolve:

```
script_v01.md

script_v02.md

script_final.md
```

Preferred:

```
script_v03.md
```

Avoid:

```
script_final_final_latest.md
```

---

# Episode Naming Convention

Every video project follows:

```
EP###_topic_name
```

Example:

```
EP001_shiva_cosmic_dancer
```

---

# Episode Folder Structure

Example:

```
projects/

└── EP001_shiva_cosmic_dancer/

    ├── research/

    ├── script/

    ├── storyboard/

    ├── prompts/

    ├── assets/

    ├── audio/

    ├── editing/

    └── publishing/

```

---

# Research File Naming

Format:

```
EP###_topic_research_type_v##
```

Examples:

```
EP001_shiva_research_notes_v01.md

EP001_shiva_reference_list_v01.md

EP001_shiva_timeline_v01.md
```

---

# Script Naming

Format:

```
EP###_topic_script_stage_v##
```

Examples:

```
EP001_shiva_script_outline_v01.md

EP001_shiva_script_draft_v02.md

EP001_shiva_script_final_v01.md
```

---

# Storyboard Naming

Format:

```
EP###_scene_##_storyboard_v##
```

Examples:

```
EP001_scene_01_storyboard_v01.md

EP001_scene_02_storyboard_v01.md
```

---

# Image Asset Naming

Format:

```
EP###_scene_##_image_description_version
```

Example:

```
EP001_scene_03_shiva_meditation_v01.png
```

---

# Image Prompt Naming

Format:

```
EP###_scene_##_image_prompt_v##
```

Examples:

```
EP001_scene_01_image_prompt_v01.md

EP001_scene_05_environment_prompt_v02.md
```

---

# Video Asset Naming

Format:

```
EP###_scene_##_shot_type_v##
```

Examples:

```
EP001_scene_01_cosmic_animation_v01.mp4

EP001_scene_03_temple_camera_move_v02.mp4
```

---

# Audio Naming

## Narration

Format:

```
EP###_narration_language_version
```

Examples:

```
EP001_narration_english_v01.wav

EP001_narration_hindi_v01.wav
```

---

## Music

Format:

```
EP###_music_emotion_version
```

Examples:

```
EP001_music_mystery_v01.mp3

EP001_music_epic_final_v02.mp3
```

---

## Sound Effects

Format:

```
EP###_sfx_description_version
```

Examples:

```
EP001_sfx_temple_bell_v01.wav

EP001_sfx_space_ambient_v01.wav
```

---

# Thumbnail Naming

Format:

```
EP###_thumbnail_concept_version
```

Examples:

```
EP001_thumbnail_lost_city_v01.png

EP001_thumbnail_cosmic_secret_v02.png
```

---

# Prompt Naming Convention

All reusable prompts:

Format:

```
category_subject_purpose_version
```

Examples:

```
image_cinematic_character_v01.md

video_camera_motion_v01.md

voice_documentary_style_v01.md
```

---

# Documentation Naming

Documentation files:

Format:

```
topic_name.md
```

Examples:

```
architecture.md

workflow.md

quality_control.md

production_process.md
```

---

# Folder Naming Convention

Folders should describe purpose.

Preferred:

```
knowledge_base/

production_bible/

templates/

projects/
```

Avoid:

```
misc/

random/

new_folder/
```

---

# AI Generation Naming Rules

Every AI-generated asset should maintain:

```
Source

+

Prompt Version

+

Generation Version

+

Selection Status

```

Example:

```
EP001_scene01_shiva_cosmic_v03_selected.png
```

---

# Status Naming

Use standard status labels:

```
draft

review

approved

final

archive
```

Examples:

```
script_v01_draft.md

script_v02_review.md

script_v03_final.md
```

---

# Git Commit Naming

Commits should describe changes.

Format:

```
type: description
```

---

Examples:

## Documentation

```
docs: add storytelling guidelines
```

---

## New Episode

```
episode: create EP001 structure
```

---

## Prompt Updates

```
prompt: improve cinematic image prompts
```

---

## Workflow Changes

```
workflow: update production pipeline
```

---

# Asset Lifecycle

Every asset follows:

```
Created

↓

Reviewed

↓

Approved

↓

Used

↓

Archived

```

---

# File Organization Principle

When creating a new file ask:

1. What category does this belong to?

2. Will I find this easily after 100 videos?

3. Does the name explain the purpose?

4. Can another creator understand it?

---

# Future Scalability

These naming conventions are designed to support:

* Multiple creators.
* Hundreds of episodes.
* Automated tools.
* AI asset generation pipelines.
* Future production teams.

---

# Closing Statement

Good naming is invisible when done correctly.

It reduces confusion.

It saves time.

It allows creativity to scale.

Mahy Mythic Labs combines creative storytelling with engineering discipline.

A clear name is the first step toward a professional studio.

---

*End of Naming Conventions Document — Version 1.0*
