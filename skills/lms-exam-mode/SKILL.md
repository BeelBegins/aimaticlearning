---
name: lms-exam-mode
description: Use for Examic mock-exam sitting UI in aimaticlearning - Pearson-style shell, style chooser, review grid, flags, timer, calculator, exam_tools JS/CSS, and asset cache-buster bumps. Not for question content (use lms-mcq-quality).
---

# LMS exam mode

Code: `aimaticlearning/public/js/lms_exam_tools.js`,
`public/css/lms_exam_tools.css`, assets wired in
`lms_learning/page_renderer.py` (`ASSET_TAGS`).

## Reference

Before touching Pearson style, read `docs/pearson-reference.md`: it records the
real player's layout and flow. Do not add controls (e.g. Skip) it does not show.

## Rules

- The sitting UI is a DOM overlay on the stock `apps/lms` quiz page. Never edit
  `apps/lms`; read state from the DOM (`questionCounter`, `quizSession`,
  `savedAnswerIds`) and drive the native buttons (`pagerButton`).
- Gate everything on `isMockSitting()`. Chapter MCQs must stay unchanged.
- Everything the Pearson style hides or adds must be undone by
  `clearPearson()`. Add the undo with the feature.
- Scope CSS under `body.aimatic-pearson-sitting` or an `.aimatic-pearson-*`
  class so normal pages are unaffected.
- Student choice persists through `styleKey()`; flags through `flagKey()`.
- After any JS/CSS change bump the matching `?v=` in `ASSET_TAGS`, or users
  keep stale assets.

## Verify

0. Run `scripts/exam-mode-harness/run.js` (see its README); it checks style prompt, review jump and End Test.
1. `ruff check .` for Python.
2. Check both styles, desktop and phone width, on a test mock.
3. Chapter MCQ page and normal-style mock still look and behave as before.
4. Before a live deploy, verify the target is `examic.study`, identify a
   rollback path, and restart only the required services.
