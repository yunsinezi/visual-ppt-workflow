# Changelog

## [2.3.0] - 2026-11-02

- Integrated 29 approved audit decisions into the normative workflow and new [policy matrix](references/upgrade-policy-v2.3.md).
- Routing now uses **animation OR element-level editability**, allowing A with no animation; B requires neither.
- A enforces risk-based content outline review, eight style previews (8 or 16 example images), full artwork approval, visual fidelity, actual requested animation or explicitly approved downgrade, and PPTX+PDF+previews+overview by default.
- B supports revisable paired previews, identical base prompts and unchanged B2 quality sentence with art-style protection, independent variant QA, adaptive typography and resolution, **PNG+ZIP+flattened PPTX per selected variant** by default.
- Added batch checkpoint/readback, severity-based repair, adaptive concurrency, permission-aware tool switching, font/safe-area QA, incremental version synchronization and graded validation boundaries.
- Updated templates and regression checks for v2.3 delivery and route semantics; prior B schemas can resume without repeated approvals.



## [2.2.0] - 2026-11-02

- B branch now **requires two paired previews of the same representative slide** before any full-deck generation.
- B1 adds **no built-in visual style/quality constraints** beyond the user's own content and essential page specifications; B2 appends the user's exact natural-photographic-finish restriction.
- New user-confirmation Gate: B1 only, B2 only, or both full decks by default **after user confirms**. Selection B alone does not authorize batching.
- In `both` mode, generate and QA **two complete independent decks** (2 × slide count), saved separately in `B1/` and `B2/`.
- Added `b_preview` and `b_await_confirmation` states, schema 1.2, prompt provenance, and new branch-specific validation tests; preserves legacy 1.1 ongoing B projects.



## [2.1.0] - 2026-11-02

- Added a mandatory **A/B animation decision** before creating any new PPT: A = original editable/animated workflow; B = directly batch-generate complete slide images.
- **B bypasses** all original eight-style previews, pilot layering, full-deck artwork approval, editable reconstruction, and animation QA.
- Added explicit image-only output caveat: high-quality page images by default, optional flattened PPTX/PDF only on request; no element editability or animation.
- Added independent B state machine (`image_generate → image_qa → image_delivered`), route gates, B project template, and branch validation tests.
- Preserved the A workflow intact after the branch decision; excluded ongoing/review tasks from redundant branch selection.


## [2.0.0] - 2026-11-01 (release candidate)

- Migrated the full V1.9 workflow into a portable Agent Skills `SKILL.md` with focused reference files.
- Formalized visual-preview and artwork approval Gates; added a one-complex-page pilot as an internal validation step.
- Clarified editable/hybrid/image-only/PDF/review delivery mode boundaries; added foreground move test.
- Defined 4 separate test layers: PPTX structure, rendered fidelity, real editability, and target-software playback.
- Added dependency-light skill/project validation, PPTX risk scanner, image diff helper, sample manifest, and unit tests.
- Codified incremental repair, checkpoint/recovery and build-id consistency.

## [1.9] - 2026-10-22 (prompt baseline)

- Quality-first speed improvements: caching, parallel independent tasks, incremental rebuild, targeted repair, resumable saves.
- Explicit user approval Gates and same-build exports; honest validation terminology.

## [1.6–1.8] - 2026-10-21

- Added full artwork review, editable decomposition, motion preplanning, independent foreground requirements, and actual target-app checks.
- Hard lessons: screenshot-only PPTs falsely claimed as editable; cropping objects from a full-page screenshot does not remove source ghosts; all-fade animations are not high-end choreography; some shapes/fonts produce blank WPS pages.

## [1.0–1.5] - earlier iterations

- Established requirement intake, at least eight visual style previews, narrative planning, editable PPTX, reference-image comparison, iterative QA and delivery discipline.
