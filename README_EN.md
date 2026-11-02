# Visual PPT Workflow v2.3.0

Agent Skill for reliable, high-fidelity presentation creation. [Chinese reference](SKILL.md) · [Reviewed policy matrix](references/upgrade-policy-v2.3.md).

**Route on animation OR element-level editability:** if either is required use **A**, including when editable slides need no animation. If neither is needed use **B**. For new ambiguous requests ask a single combined question; never infer B from silence about animation. Resume existing projects without repeating approved decisions.

**A:** DEFINE → EXPLORE (eight distinct visual approaches: one sample each for ordinary decks, cover+content each for important decks) → PILOT (internal complex-slide test) → ARTWORK (approve all final slide images) → REBUILD (visual fidelity first; ordinary text editable; animation subjects independent) → VERIFY → DELIVER. Actual animation implementation is required when requested; degradation needs explicit user approval. Default: editable PPTX, static PDF, per-slide previews and overview; source package on demand.

**B:** Generate **two real independent previews of the same representative slide**. B1 does not add Skill-invented quality/style constraints. B2 appends the unchanged fixed Chinese quality sentence from [B workflow](references/image-fast-path.md) to the identical base prompt. Preserve user-requested anime/ink style instead of forcing photography. If dissatisfied, revise the shared prompt and regenerate **both** previews. Only after showing both ask for B1, B2 or both (default only after confirmation). Generate each page of each selected deck independently. Default deliverables **for each variant**: full-resolution PNG slides, ZIP, **flattened image-only PPTX**. No element editing or native animation; optional PDF on request.

**Shared:** risk-adjusted fact checks, accurate Chinese text, adaptive 1080p/4K targets, fonts and safe areas, consistent design language with page-specific layouts, batch checkpoints with real file readback, incremental regeneration, independent B1/B2 versions, adaptive concurrency, authorized tool changes, and no unapproved loss of functionality. Never equate static XML checks with real PowerPoint/WPS playback.

### Install / validate

```bash
gemini skills install https://github.com/yunxinzi/visual-ppt-workflow.git
python3 scripts/validate_skill.py .
python3 scripts/validate_project.py assets/project-template.json
python3 scripts/validate_project.py assets/image-branch-template.json
python3 -m unittest discover -s tests -v
```

This is a workflow/validation Skill, not a standalone image generation or Office rendering engine. Integration tests are not guaranteed by static tests. MIT.
