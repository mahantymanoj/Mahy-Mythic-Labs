# Video Exports

## Purpose

This folder contains platform-specific delivery exports prepared for upload to YouTube, YouTube Shorts, or other distribution channels.

An export is a delivery-ready version derived from the final approved master in `../published/`. It is optimized for the target platform's codec, resolution, and file-size requirements.

## Difference from Published

| Folder | Contents |
| --- | --- |
| `../published/` | The approved final master. Highest quality. Read-only after approval. |
| `../export/` | Platform-specific delivery versions. Compressed and formatted for upload. |

Never use an export file as the source for future edits. Always work from the master in `../published/`.

## File Naming

Use:

`[episode-or-project]-[platform]-[format]-v##.[extension]`

Examples:

`ep001-youtube-16x9-v01.mp4`

`ep001-shorts-9x16-v01.mp4`

`ep001-youtube-16x9-preview-v01.mp4`

## Approved Export Specifications

| Platform | Codec | Resolution | Frame Rate | Video Bitrate | Audio Codec | Audio Bitrate |
| --- | --- | --- | --- | --- | --- | --- |
| YouTube (16:9) | H.264 | 1920 × 1080 minimum | Match source (24 or 25 fps) | 8–12 Mbps | AAC | 320 kbps |
| YouTube Shorts (9:16) | H.264 | 1080 × 1920 | Match source (24 or 25 fps) | 8–12 Mbps | AAC | 320 kbps |
| Preview / compressed | H.264 | 1280 × 720 | Match source | 4–6 Mbps | AAC | 192 kbps |

## Rules

- Never overwrite an existing export; create a new version.
- Version all exports using the `v##` suffix.
- Link each export to its source master in `../published/` in the episode asset manifest.
- Do not use export files as source material for editing.
- Record the upload date, platform, and YouTube video ID in the episode manifest once an export is published.

## Approval Checklist

- [ ] Export was generated from the approved final master in `../published/`.
- [ ] Codec, resolution, and bitrate match the approved export specifications.
- [ ] Audio is present, balanced, and clear.
- [ ] File plays correctly from start to finish.
- [ ] Export is versioned and named according to the file naming convention.
- [ ] Source master path is recorded in the episode asset manifest.
