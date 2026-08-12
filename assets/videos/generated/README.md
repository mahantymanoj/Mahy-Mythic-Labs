# Generated Videos

## Purpose

This folder contains raw AI-generated video clips, motion tests, animated keyframes, and unapproved scene renders.

## Allowed Content

- Raw video-generation outputs
- Camera-motion tests
- Image-to-video clips
- Prompt variations
- Draft scene renders
- Visual-effects experiments

## File Naming

Use:

`[episode-or-project]-[scene]-[shot]-[version].[extension]`

Example:

`ep001-antikythera-scene03-gears-v01.mp4`

## Required Metadata

Each generated video must have a linked record containing:

- Episode or project ID
- Scene and shot number
- Generation prompt
- Negative prompt
- Generation tool or model
- Input image or reference asset
- Camera-motion instruction
- Generation date
- Creator or operator
- Review status

## Review Checklist

Before moving a generated clip out of this folder:

- [ ] Prompt accuracy: the clip represents what the approved prompt described.
- [ ] Visual artifacts: no distortion, melting, unintended duplication, or broken geometry.
- [ ] Subject consistency: characters, environments, and objects are consistent with approved metadata.
- [ ] Motion quality: camera motion and subject movement are smooth and intentional.

## Rules

- Generated clips are not approved for final use.
- Do not place raw clips directly into a final edit.
- Do not overwrite an existing render; create a new version.
- Move approved clips to `../edited/` only after review.
- Delete rejected or obsolete clips after confirming they are not needed for prompt reference or production record.
