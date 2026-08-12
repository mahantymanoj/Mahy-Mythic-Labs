# Rejected Images

## Purpose

This folder stores images that have been reviewed and formally rejected for production use.

A rejected image failed one or more of the required checks—visual quality, factual accuracy, ethical appropriateness, cultural sensitivity, or rights clearance—and must not be used in any final edit or published video.

## What Belongs Here

- Images that failed quality review and will not be revised.
- Images containing factual errors, anachronisms, or misleading visual claims that cannot be corrected.
- Images with ethical, cultural, or rights issues that prevent production use.
- Images rejected after a re-review that originally came from `../archive/`.

## What Does Not Belong Here

- Images that are simply superseded by a newer version — those belong in `../archive/`.
- Unreviewed raw outputs — those belong in `../generated/` until reviewed.
- Reference-only images — those belong in `assets/references_media/`.

## File Naming

Retain the original filename and add a rejected suffix:

`[original-file-name]-rejected-[reason]-v##.[extension]`

Example:

`ep001-antikythera-figure-rejected-anachronism-v01.png`

## Rejection Reasons

| Reason | Meaning |
| --- | --- |
| Quality | Artifacts, poor anatomy, distorted composition, or low resolution |
| Factual | Anachronism, incorrect materials, unsupported historical detail |
| Ethical | Harmful stereotype, cultural misrepresentation, or sacred misuse |
| Rights | Unlicensed likeness, protected content, or unclear copyright |
| Continuity | Inconsistent with the approved visual identity of a character or environment |
| Out of scope | Does not fit the episode, story, or brand direction |

## Rules

- Do not use rejected images in any production context.
- Retain rejected images for audit and prompt improvement reference.
- Record the rejection reason in the asset register Notes field.
- Do not permanently delete rejected assets without confirming they are no longer needed for review history or prompt analysis.
- A rejected image may only be reconsidered if the underlying issue is resolved and it is submitted for formal re-review from the beginning.

## Approval Checklist for Re-review

If a rejected image is submitted for re-consideration:

- [ ] The rejection reason has been addressed.
- [ ] A new review has been completed.
- [ ] If approved, the image is moved to `../approved/` with a new version number.
- [ ] The asset register is updated with the new status and review notes.
