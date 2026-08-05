# YouTube Tools

## Purpose

This folder contains controlled tools for uploading approved videos and retrieving channel analytics.

| File | Purpose |
| --- | --- |
| `uploader.py` | Uploads a reviewed video with approved metadata |
| `analytics.py` | Retrieves read-only channel analytics and exports CSV reports |

## Required Google Cloud Setup

1. Create a Google Cloud project.
2. Enable **YouTube Data API v3**.
3. Enable **YouTube Analytics API**.
4. Configure the OAuth consent screen.
5. Create an OAuth Desktop App client ID.
6. Download the client-secret JSON file.
7. Store it outside Git, for example: `secrets/client_secrets.json`.

## Security Rules

- Never commit `client_secrets.json` or OAuth token files.
- Add `secrets/` and `*.token.json` to `.gitignore`.
- The uploader defaults to `private`.
- Upload only after research, rights, quality, and publishing review are complete.
- Analytics is read-only and must never alter channel content.

## Examples

Upload a reviewed private video:

```powershell
python tools/youtube/uploader.py `
  projects/EP001/video/ep001-16x9-final-v01.mp4 `
  --title "The Ancient Machine That Knew the Stars" `
  --description-file projects/EP001/publishing/description.txt `
  --tags "Antikythera Mechanism,ancient Greece,astronomy" `
  --privacy private `
  --confirm-upload