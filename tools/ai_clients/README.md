# AI Clients

## Purpose

This folder contains small, reusable clients for the Mahy Mythic Labs AI production pipeline.

| File | Purpose |
| --- | --- |
| `llm_client.py` | Research, outlining, scripting, metadata, and quality-review text generation |
| `image_client.py` | AI image generation and local image-file output |
| `video_client.py` | Video-generation job creation, status checks, and downloads |
| `voice_client.py` | Text-to-speech narration generation |

## Setup

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install openai requests