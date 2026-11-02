# Visual PPT Workflow v2.4 · Full Edition

[中文说明](README.md) · [SKILL.md](SKILL.md) · [STYLE-FIRST gate](references/style-first.md)

This is the **full edition** of the workflow, hosted independently from [the fast edition](https://github.com/yunsinezi/visual-ppt-fast).

**Mandatory new-deck order:** understand the task → create eight **genuinely different, separately generated previews of the same representative content slide** → show all eight and receive the user's style selection → only then route to A/B → generate and validate the deck.

- **A:** animation OR element-level editability required. Reuse the selected style and proceed to PILOT, final-artwork user approval, editable reconstruction, verification and delivery. Do **not** repeat the eight-style exploration after routing. Default output: editable PPTX, static PDF, slide previews, overview.
- **B:** neither is required. Once a style is chosen, show a **B1/B2 quality-only comparison** of that **same chosen style**, then get explicit confirmation for B1, B2, or both before production. The B1/B2 previews are not a second style-choice round, nor four previews of each kind. Default per variant: full-size PNG slides, ZIP, image-only PPTX.

Users may state their animation/editing preference early, but execution cannot branch before eight real style images are shown and a style is chosen. Resume approved projects without repeating gates. The B2 constraint is preserved verbatim in [the B workflow](references/image-fast-path.md) and must not destroy a user's chosen anime/ink illustration style.

This is a workflow/QA Skill, **not** a bundled image generator or Office engine.

```bash
gemini skills install https://github.com/yunsinezi/visual-ppt-workflow.git
python3 scripts/validate_skill.py .
python3 scripts/validate_project.py assets/style-first-template.json
python3 -m unittest discover -s tests -v
```

Static tests do not establish real image quality, editability, target-app playback or actual user approval. MIT.
