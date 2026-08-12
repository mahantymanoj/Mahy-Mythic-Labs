# Mahy Mythic Labs — Asset Database

## Purpose

This database is the central index for all Mahy Mythic Labs assets. It exists to make reusable assets easy to find, track their production status, confirm rights, and record where each asset has been used across episodes.

Detailed license information belongs in:

`assets/licenses/asset_license_tracker.md`

## Folder Structure

| Category | Primary Folder |
| --- | --- |
| Branding | `assets/branding/` |
| Logos | `assets/logos/` |
| Characters | `assets/characters/` |
| Environments | `assets/environments/` |
| Images | `assets/images/` (subfolders: `generated/`, `approved/`, `archive/`, `rejected/`) |
| Videos | `assets/videos/` (subfolders: `generated/`, `edited/`, `export/`, `published/`) |
| Music | `assets/audio/music/` |
| Narration | `assets/audio/narration/` |
| SFX | `assets/audio/sfx/` |
| Fonts | `assets/fonts/` |
| References | `assets/references_media/` |
| Licenses | `assets/licenses/` |

## Asset Categories

| Category | Examples |
| --- | --- |
| Branding | Logos, banners, lower thirds, title cards |
| Character | Historical figures, mythological figures, recurring visual characters |
| Environment | Cities, temples, landscapes, cosmic locations, interiors |
| Image | Generated stills, approved keyframes, illustrations |
| Video | Generated clips, edited sequences, final exports |
| Narration | Voice recordings, AI narration, final voice masters |
| Music | Tracks, stems, loops, score cues |
| SFX | Foley, ambience, transitions, mechanical sounds |
| Font | Licensed typography files and font packages |
| Reference | Research images, visual references, source material |

## Asset Status Definitions

| Status | Meaning |
| --- | --- |
| Draft | Created or identified but not ready for use |
| Generated | AI-generated or newly created; awaiting review |
| Pending Review | Awaiting quality, factual, ethical, or license review |
| Approved | Cleared for production use |
| Active | Currently used in an active episode or campaign |
| Restricted | Use allowed only under stated conditions |
| Archived | Retained for history; not for current use |
| Rejected | Not approved for production use |

## Asset Register

| Asset ID | Asset Name | Category | Subcategory | Status | Source / Creator | License ID | Location | First Used In | Last Updated | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AST-001 | — | — | — | Draft | — | — | — | — | — | — |

## Asset ID Format

Use:

`AST-[number]`

Examples:

- `AST-001`
- `AST-002`
- `AST-003`

Use the asset ID consistently in:

- Character registry
- Environment registry
- Episode asset manifests
- License tracker
- Prompt records
- Editing projects
- Publishing records

## Recommended Subcategories

| Category | Suggested Subcategories |
| --- | --- |
| Branding | Logo, wordmark, banner, end card, lower third, thumbnail template |
| Character | Historical, reconstructed, mythological, symbolic, original |
| Environment | Historical, natural, cosmic, mythological, symbolic, futuristic |
| Image | Generated, approved, archive, reference |
| Video | Generated, edited, final |
| Narration | Raw, cleaned, final, alternate take |
| Music | Score, stem, loop, ambient, transition |
| SFX | Atmosphere, foley, impact, transition, mechanical, nature |
| Font | Display, body, subtitle, caption |
| Reference | Historical, scientific, visual, cultural |

## Episode Usage Log

Use this section to track where an approved asset appears.

| Asset ID | Episode ID | Scene / Timestamp | Usage Type | Version Used | Approved By | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| AST-001 | — | — | Background \| Hero Asset \| Audio \| Overlay \| Watermark | — | — | — |

## Asset Intake Checklist

Before adding a new asset:

- [ ] Assign an Asset ID.
- [ ] Add the asset to the Asset Register.
- [ ] Save it in the correct folder.
- [ ] Record source, creator, and date acquired.
- [ ] Add license details to the license tracker if required.
- [ ] Add generation prompt and settings for AI-created assets.
- [ ] Assign a status.
- [ ] Link the asset to the relevant episode if applicable.

## Asset Approval Checklist

Before changing an asset status to `Approved`:

- [ ] Visual or audio quality has been reviewed.
- [ ] The asset supports Mahy Mythic Labs brand direction.
- [ ] Historical, scientific, and cultural details are appropriate.
- [ ] Rights and licensing are verified.
- [ ] Required metadata is complete.
- [ ] The correct version is stored in the approved location.
- [ ] Episode use is recorded where applicable.

## Naming Convention

Use lowercase kebab case for filenames:

`[project-or-episode]-[subject]-[asset-type]-v##.[extension]`

Examples:

```text
ep001-antikythera-gear-image-v01.png
ep001-aegean-storm-video-v02.mp4
brand-mahy-wordmark-light-v01.svg
sfx-bronze-gear-turn-v01.wav
```

## Rules

- Never overwrite an approved or final asset.
- Create a new version for every meaningful revision.
- Do not use assets with unclear licensing.
- Preserve original source files, prompts, and metadata.
- Keep archive assets for traceability.
- Update this database whenever an asset is created, approved, used, restricted, or archived.
