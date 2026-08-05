# Automation Scripts

## Purpose

These scripts automate repeatable Mahy Mythic Labs production tasks while preserving human creative, factual, cultural, rights, and quality review.

| File | Purpose |
| --- | --- |
| `episode_creator.py` | Creates a standard episode project structure |
| `asset_manager.py` | Validates asset filenames and adds asset records |
| `markdown_generator.py` | Creates consistent Markdown documents and templates |

## Safety Principles

- Scripts must never publish content automatically.
- Scripts must not overwrite existing files.
- AI-generated content remains subject to human review.
- Every asset requires a rights and license record before final use.
- Run scripts from the repository root.

## Examples

Create an episode structure:

```powershell
python tools/automation_scripts/episode_creator.py EP001 "The Ancient Machine That Knew the Stars"