# 🎬 Production Workflow

> **Mahy Mythic Labs Production Workflow**
>
> Version: 1.0
>
> This document defines the complete creative production lifecycle for every Mahy Mythic Labs project. It describes how an idea evolves into a published video, establishes responsibilities for each production stage, and provides the quality checkpoints required before moving to the next phase.

---

# 1. Purpose

The production workflow ensures that every video:

- Follows a consistent process
- Meets quality standards
- Maintains brand identity
- Preserves factual accuracy
- Produces reusable assets
- Can be automated over time

This workflow applies to both manual and AI-assisted production.

---

# 2. Production Philosophy

Every production follows five principles:

- Research before creation
- Story before visuals
- Quality before speed
- Consistency before experimentation
- Automation where it improves quality

---

# 3. Production Lifecycle

```
Idea

↓

Topic Selection

↓

Research

↓

Fact Verification

↓

Episode Planning

↓

Script Writing

↓

Script Review

↓

Storyboard

↓

Visual Planning

↓

Asset Generation

↓

Narration

↓

Video Assembly

↓

Quality Review

↓

Publishing Package

↓

YouTube Upload

↓

Analytics & Improvement
```

Every stage must be completed before the next begins.

---

# 4. Stage 1 — Topic Selection

Objective:

Choose a topic that aligns with the Mahy Mythic Labs mission.

Selection criteria:

- Educational value
- Viewer interest
- Research availability
- Visual storytelling potential
- Long-term relevance

Deliverable:

`episode.md`

---

# 5. Stage 2 — Research

Objective:

Collect accurate and trustworthy information.

Activities:

- Literature review
- Scientific sources
- Historical references
- Multiple source comparison
- Source documentation

Deliverable:

`research/research.md`

Quality Gate:

- Reliable sources
- Evidence documented
- Major claims verified

---

# 6. Stage 3 — Episode Planning

Objective:

Transform research into a production plan.

Activities:

- Define audience
- Episode length
- Learning objectives
- Key scenes
- Emotional arc

Deliverable:

Updated `episode.md`

---

# 7. Stage 4 — Script Writing

Objective:

Create a cinematic educational narrative.

Activities:

- Hook
- Narrative flow
- Scientific accuracy
- Storytelling
- Conclusion

Deliverable:

`script/script.md`

Quality Gate:

- Voice identity followed
- Storytelling framework followed
- AI generation rules satisfied

---

# 8. Stage 5 — Storyboarding

Objective:

Convert the script into visual scenes.

Activities:

- Scene breakdown
- Camera planning
- Visual references
- Timing
- Scene transitions

Deliverable:

`storyboard/storyboard.md`

---

# 9. Stage 6 — Prompt Engineering

Objective:

Prepare AI-ready prompts.

Artifacts:

- Image prompts
- Video prompts
- Narration prompts

Deliverables:

```
prompts/

image_prompts.md

video_prompts.md

narration_prompt.md
```

Quality Gate:

- Style Guide compliance
- Character consistency
- Visual continuity

---

# 10. Stage 7 — Asset Generation

Objective:

Generate production assets.

Assets include:

- Images
- Videos
- Narration
- Music
- Sound Effects

Output directories:

```
assets/

audio/

video/
```

Generated assets should pass quality review before approval.

---

# 11. Stage 8 — Video Production

Objective:

Assemble the final video.

Activities:

- Scene sequencing
- Audio synchronization
- Music
- Effects
- Titles
- Subtitles
- Branding

Deliverable:

Draft video

---

# 12. Stage 9 — Quality Review

Objective:

Validate every production component.

Review checklist:

✓ Research accuracy

✓ Script quality

✓ Narration quality

✓ Visual consistency

✓ Copyright compliance

✓ Thumbnail quality

✓ SEO metadata

Deliverable:

`quality/quality_report.md`

---

# 13. Stage 10 — Publishing

Objective:

Prepare publication assets.

Deliverables:

- Thumbnail
- Title
- Description
- Tags
- Chapters
- End screen
- Cards

Output:

`publishing/upload_metadata.md`

---

# 14. Stage 11 — YouTube Upload

Activities:

- Upload
- Metadata verification
- Thumbnail
- Playlist
- Scheduling
- End screen
- Captions

Publishing should occur only after all quality gates pass.

---

# 15. Stage 12 — Post-Publication

Collect:

- Watch time
- CTR
- Audience retention
- Viewer comments
- Engagement
- Performance insights

Lessons learned should feed back into future productions.

---

# 16. AI Agent Responsibilities

| Agent | Responsibility |
|---------|----------------|
| Master Director | Coordinate workflow |
| Research Agent | Research |
| Script Agent | Script writing |
| Storyboard Agent | Visual planning |
| Image Agent | Images |
| Video Agent | Video generation |
| Narration Agent | Voice generation |
| Quality Agent | Review |
| SEO Agent | Metadata |
| Publishing Agent | Upload preparation |

Each agent owns a clearly defined stage.

---

# 17. Production Artifacts

Each episode produces:

```
episode.md

research.md

script.md

storyboard.md

image_prompts.md

video_prompts.md

narration_prompt.md

quality_report.md

upload_metadata.md
```

These documents form the permanent production record.

---

# 18. Quality Gates

A stage cannot progress until:

- Previous deliverables are complete
- Quality checklist passes
- Required approvals are recorded
- Dependencies are satisfied

Automation should enforce these gates wherever practical.

---

# 19. Continuous Improvement

Every completed episode should contribute to improving:

- Prompts
- Workflows
- Templates
- Knowledge base
- Production Bible
- Automation rules

Continuous refinement is part of the production process.

---

# 20. Related Documents

| Document | Purpose |
|----------|---------|
| `production_bible/STYLE_GUIDE.md` | Visual identity |
| `production_bible/VOICE_IDENTITY.md` | Narration identity |
| `production_bible/STORYTELLING_FRAMEWORK.md` | Narrative framework |
| `production_bible/AI_GENERATION_RULES.md` | AI standards |
| `production_bible/QUALITY_STANDARDS.md` | Quality expectations |
| `automation/workflow.md` | Technical automation workflow |
| `docs/content_strategy.md` | Editorial planning |

---

# 21. Summary

The Mahy Mythic Labs Production Workflow defines the complete creative lifecycle from idea to published video. It combines rigorous research, cinematic storytelling, structured quality control, and AI-assisted production into a repeatable process that supports both manual creation today and fully automated production in the future.