# Mahy Mythic Labs — Asset License Tracker

## Purpose

This tracker records the ownership, license status, attribution requirements, and production usage of every non-original asset used by Mahy Mythic Labs.

No third-party asset may be used in a published production until its license status is documented here.

## License Status Definitions

| Status | Meaning |
| --- | --- |
| Pending | Asset received but rights have not been verified |
| Approved | Rights verified and approved for the stated use |
| Restricted | Use allowed only under documented limitations |
| Expired | License is no longer valid for new use |
| Rejected | Rights are unclear, insufficient, or unsuitable |
| Original | Created and owned by Mahy Mythic Labs |
| AI Generated | Generated with AI; prompt, tool, and review record required. See the AI-Generated Asset Requirements section for the full record required before this status can be approved for production use. |

## Common License Types Reference

| License Type | Plain-language meaning |
| --- | --- |
| CC0 | Public domain dedication. No rights reserved. Free to use, modify, and distribute commercially without attribution. |
| CC-BY | Attribution required. Free to use and modify commercially, but the original creator must be credited in the agreed format. |
| CC-BY-SA | Attribution required and any derivative work must be released under the same license. Sharing restrictions may affect commercial publishing. |
| Royalty Free | A one-time fee grants ongoing use rights. Does not mean free of charge or free of restrictions. Always check the specific terms for commercial and broadcast use. |
| Editorial Use Only | The asset may only be used to illustrate factual reporting. It cannot be used in branded, promotional, or commercial-production content. |
| AI Generated | The asset was produced by an AI tool. Rights vary by tool and terms of service. A generation record, tool terms review, and editorial review are required before production use. |

## Asset License Register

| License ID | Asset ID | Asset Name | Category | Creator / Source | License Type | Commercial Use | Attribution Required | Modification Allowed | Expiry Date | Status | Proof Location | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LIC-001 | — | — | Image / Video / Music / SFX / Font / Logo / Reference | — | — | Yes / No / Conditional | Yes / No | Yes / No / Conditional | — | Pending | — | — |

## Episode Usage Register

Record each use of an asset in a specific episode.

| Episode ID | Asset ID | License ID | Scene / Timestamp | Intended Use | Verified By | Date Verified | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EP001 | — | — | — | — | — | — | — |

## Required Proof

For every approved third-party asset, retain one or more of the following:

- License agreement or receipt
- Source page URL
- Screenshot of license terms
- Creator permission email or written release
- Subscription record, where relevant
- Attribution text required by the license
- Date the asset was downloaded or acquired

## AI-Generated Asset Requirements

For AI-generated images, video, audio, or voice assets, record:

| Field | Required Record |
| --- | --- |
| Generation tool | Name of the AI tool or model used |
| Prompt | Final approved prompt |
| Input assets | Any source images, references, or uploads used |
| Date generated | Date of creation |
| Review result | Artifact, accuracy, likeness, and rights review |
| Usage decision | Approved, restricted, or rejected |
| Episode use | Episode and scene where used |

Each AI-generated asset requires its own entry in the Asset License Register above with status `AI Generated`. The entry must be reviewed and updated before the asset is cleared for final production use.

## Approval Checklist

Before using an asset in a final export:

- [ ] Asset is listed in this tracker.
- [ ] Commercial-use rights are confirmed.
- [ ] Attribution requirements are documented.
- [ ] Modification rights are confirmed if editing is required.
- [ ] License expiry and regional limits are checked.
- [ ] Proof of license is stored and linked.
- [ ] Asset use is recorded in the episode manifest.
- [ ] Asset is approved for final production use.

## Rules

- Never assume an online asset is free to use.
- "Royalty-free" does not always mean unrestricted commercial use.
- Reference images are not automatically production assets.
- Do not use copyrighted music, stock footage, fonts, images, or sound effects without verified permission.
- If the license is unclear, mark the asset as `Pending` or `Rejected` and do not use it.
- Keep this tracker updated whenever an asset is acquired, approved, used, restricted, or archived.
