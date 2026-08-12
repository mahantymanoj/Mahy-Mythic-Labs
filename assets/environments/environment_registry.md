# Mahy Mythic Labs — Environment Registry

## Purpose

This registry tracks every reusable location, world, landscape, interior, archaeological site, cosmic setting, and symbolic environment used in Mahy Mythic Labs productions.

It maintains visual continuity, historical accuracy, and efficient asset reuse across episodes.

## Environment Categories

| Category | Definition | Example |
| --- | --- | --- |
| Historical | A documented real-world location from a known era | Ancient Alexandria, Pompeii |
| Reconstructed | An evidence-led recreation of a historical setting | Greek workshop, Bronze Age harbor |
| Natural | A real or plausible natural landscape | Aegean Sea, desert, mountain range |
| Cosmic | A scientifically grounded space environment | Nebula, exoplanet surface, early universe |
| Mythological | A symbolic or tradition-based mythic setting | Mount Olympus, Duat, Yggdrasil |
| Symbolic | A non-literal setting representing an idea | Memory archive, passage of time |
| Futuristic | A plausible future environment | Lunar settlement, AI research facility |

## Environment Registry

| Environment ID | Name / Working Name | Category | Time / Setting | First Episode | Status | Reference File |
| --- | --- | --- | --- | --- | --- | --- |
| ENV-001 | — | — | — | — | Draft / Approved / Archived | — |

## Environment Rules

- Every recurring environment must have a completed metadata file.
- Historical environments must be based on credible research and documented references.
- Reconstructed locations must be labeled internally as artistic visualizations.
- Mythological environments must respect their original cultural context.
- Do not mix unrelated historical periods, architectural styles, or technologies.
- Record approved generation prompts for reusable environments.
- Maintain consistent geography, lighting, materials, atmosphere, and scale across scenes.
- Reuse an existing environment entry when the same location appears in a new episode. Create a new entry only when a distinctly different version of a location is required—for example, the same site in a different era, season, or state of ruin.

## Status Definitions

| Status | Meaning |
| --- | --- |
| Draft | Concept exists but is not yet approved |
| Approved | Research and visual direction are approved |
| Active | Currently in use for a production |
| Archived | Retained for record; not intended for new use |
| Restricted | Requires further research, cultural, or editorial review |

## Naming Convention

Use:

`ENV-[number]-[short-name]`

Examples:

- `ENV-001-antikythera-shipwreck`
- `ENV-002-ancient-greek-workshop`
- `ENV-003-cosmic-starfield`
- `ENV-004-bronze-age-harbor`

## Reuse Guidelines

To reuse an existing environment in a new episode:

1. Check this registry to confirm the environment is in `Approved` or `Active` status.
2. Open the environment's metadata file (listed in the Reference File column).
3. Use the approved visual-generation prompt from the metadata file exactly as recorded.
4. Do not alter materials, lighting direction, or architectural features without submitting a new metadata version.
5. Record the new episode use in the metadata file's Related Episodes field.
6. Update this registry's status to `Active` if the environment is being used in a new production.
