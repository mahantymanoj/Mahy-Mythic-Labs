# 🧠 Prompt Engineering Standards

> **Mahy Mythic Labs Prompt Engineering Guide**
>
> Version: 1.0
>
> This document defines the prompt engineering principles, architecture, standards, templates, validation rules, and best practices used throughout Mahy Mythic Labs. It ensures that all AI providers generate consistent, high-quality, reproducible outputs.

---

# 1. Purpose

Prompt engineering is the foundation of AI-assisted production.

This guide establishes:

- Prompt architecture
- Prompt quality standards
- Reusable templates
- Context management
- Multi-agent communication
- Provider independence

Every AI prompt should be deterministic, maintainable, and reusable.

---

# 2. Scope

These standards apply to:

- Research prompts
- Script prompts
- Storyboard prompts
- Image prompts
- Video prompts
- Narration prompts
- SEO prompts
- Thumbnail prompts
- Quality review prompts
- Agent orchestration prompts

---

# 3. Design Principles

Every prompt should be:

✓ Explicit

✓ Context-aware

✓ Reusable

✓ Modular

✓ Deterministic

✓ Version controlled

Avoid one-off prompts whenever possible.

---

# 4. Prompt Architecture

Every production prompt should follow this structure:

```
SYSTEM

↓

ROLE

↓

OBJECTIVE

↓

CONTEXT

↓

INPUT

↓

CONSTRAINTS

↓

OUTPUT FORMAT

↓

QUALITY CHECKLIST

↓

EXAMPLES (Optional)
```

This structure should remain consistent across all agents.

---

# 5. Prompt Components

## System

Defines permanent behavior.

Example:

- Follow Mahy Mythic Labs standards.
- Follow AI Generation Rules.
- Follow Voice Identity.

---

## Role

Examples:

- Research Analyst
- Documentary Writer
- Storyboard Artist
- Cinematic Director
- Prompt Engineer
- SEO Specialist

The role should remain focused.

---

## Objective

A single, measurable task.

Example:

> Create a cinematic documentary script explaining black holes for a general audience.

---

## Context

Context may include:

- Episode summary
- Research findings
- Previous outputs
- Knowledge base
- Brand identity
- Style guide

Only include information relevant to the task.

---

## Input

Examples:

- Topic
- Script
- Storyboard
- Image description
- Research package

Inputs should be structured and complete.

---

## Constraints

Define:

- Length
- Tone
- Audience
- Accuracy requirements
- Formatting
- Forbidden content

Constraints reduce ambiguity.

---

## Output Format

Prefer structured formats such as:

- Markdown
- JSON
- Tables
- Bullet lists
- YAML

Avoid free-form text when automation will consume the output.

---

## Quality Checklist

Each prompt should include a self-review step.

Example:

- Is the output factually accurate?
- Is it consistent with the style guide?
- Are all requested sections present?

---

# 6. Context Hierarchy

Prompts should load context in this order:

```
Global Standards

↓

Production Bible

↓

Knowledge Base

↓

Episode Context

↓

Previous Agent Output

↓

Current Task
```

Higher-level context should not be overridden by lower-level context.

---

# 7. Prompt Categories

## Research

Objective:

Gather and organize verified information.

---

## Script

Objective:

Transform research into a compelling narrative.

---

## Storyboard

Objective:

Convert the script into visual scenes.

---

## Image

Objective:

Generate consistent cinematic imagery.

---

## Video

Objective:

Generate cinematic shots that match the storyboard.

---

## Narration

Objective:

Produce natural documentary narration.

---

## SEO

Objective:

Generate discoverable but accurate metadata.

---

## Quality

Objective:

Review outputs against project standards.

---

# 8. Prompt Templates

Every prompt should originate from a template.

Examples:

```
templates/

research_template.md

script_template.md

image_prompt.md

video_prompt.md

seo_template.md
```

Avoid duplicating prompt logic across agents.

---

# 9. Variable Placeholders

Use placeholders for dynamic values.

Example:

```
{{TOPIC}}

{{AUDIENCE}}

{{EPISODE_LENGTH}}

{{STYLE_GUIDE}}

{{VOICE_IDENTITY}}
```

Hardcoded values should be minimized.

---

# 10. Multi-Agent Prompting

Each agent should receive:

- Only the context it requires.
- Approved outputs from previous agents.
- Relevant production standards.

Avoid passing unnecessary information.

---

# 11. Chain of Responsibility

```
Research

↓

Script

↓

Storyboard

↓

Image

↓

Video

↓

Narration

↓

SEO

↓

Quality
```

Agents should not bypass established dependencies.

---

# 12. Provider Independence

Prompts should avoid provider-specific features unless necessary.

The same logical prompt should work with:

- GPT
- Claude
- Gemini
- Grok
- Local LLMs

Provider-specific optimizations should be isolated in adapter layers.

---

# 13. Prompt Versioning

Every prompt should include:

- Version
- Author
- Last Updated
- Purpose

Changes should be tracked through Git.

---

# 14. Prompt Testing

Test prompts using:

- Different AI providers
- Edge cases
- Long inputs
- Short inputs
- Ambiguous topics

Record observations for future refinement.

---

# 15. Prompt Evaluation

Evaluate prompts based on:

- Accuracy
- Consistency
- Completeness
- Formatting
- Creativity
- Efficiency
- Reproducibility

Refine prompts based on measurable outcomes.

---

# 16. Common Mistakes

Avoid:

- Ambiguous instructions
- Multiple unrelated objectives
- Missing context
- Conflicting constraints
- Excessive prompt length
- Hidden assumptions

One prompt should solve one primary problem.

---

# 17. Security

Never expose:

- API keys
- Credentials
- Internal configuration
- Proprietary information

Sensitive data should be injected securely through configuration, not embedded in prompts.

---

# 18. AI Hallucination Prevention

Prompts should instruct models to:

- State uncertainty.
- Avoid inventing facts.
- Request clarification when required.
- Separate evidence from speculation.

Trustworthiness is more important than confidence.

---

# 19. Continuous Improvement

Prompt quality should improve through:

- Episode reviews
- Performance metrics
- Human feedback
- Model updates
- A/B testing

Successful prompt patterns should be documented and reused.

---

# 20. Related Documents

| Document | Purpose |
|----------|---------|
| `production_bible/AI_GENERATION_RULES.md` | AI behavior standards |
| `production_bible/VOICE_IDENTITY.md` | Narration identity |
| `production_bible/STYLE_GUIDE.md` | Visual direction |
| `production_bible/STORYTELLING_FRAMEWORK.md` | Narrative structure |
| `automation/agent_orchestration.md` | Agent execution flow |
| `prompts/` | Prompt templates |

---

# 21. Summary

The Mahy Mythic Labs Prompt Engineering Standards provide a structured methodology for designing, testing, and maintaining AI prompts across every production stage. By separating system behavior, context, objectives, constraints, and output formats, the platform remains scalable, provider-independent, and capable of producing consistent, high-quality results regardless of the underlying AI model.