# Task: lms-pearson-exam-mode-20261005

Goal: Optional Pearson VUE-style sitting for mock exams. A student picks
"Pearson" or the normal style before starting; Pearson hides LMS chrome and
shows a fixed top bar (title, progress, time, calculator) and footer
(prev/next, skip, flag for review, review screen, end).

Environment: `lms.aimatic.tech`. Local code only so far; nothing deployed.

Files / allowed edit paths:
- `aimaticlearning/public/js/lms_exam_tools.js` (shell, review grid, style modal)
- `aimaticlearning/public/css/lms_exam_tools.css`
- `aimaticlearning/public/js/lms_student_experience.js` (small hook)
- `aimaticlearning/lms_learning/page_renderer.py` (asset `?v=` cache busters)

Acceptance criteria (to confirm; not yet verified):
- Style modal appears once per start and the choice is remembered (`styleKey`).
- Pearson shell appears only on a mock sitting, never on chapter MCQs.
- Answered/flagged/current states in the review grid match saved answers.
- Prev/next/skip/flag/end work; timer matches the native one; end submits.
- Leaving Pearson (or choosing normal) restores all hidden chrome (`clearPearson`).
- Works on phone width; calculator toggle still works.
- Normal-style mocks behave exactly as before.

Constraints: no `apps/lms` core edits; no auto-enrol; deploy needs approval.
Bump `?v=` strings in `page_renderer.py` whenever these assets change.

Base commit and existing local changes: `ae1ccc0`; the four files above are
uncommitted (~790 lines added). Status: **working, incomplete** (user,
2026-10-05).

Skills used: `lms-exam-mode`, `lms-learning`.

Verification: `ruff check .`, then drive a mock on a local/test LMS and check
each acceptance line. Live checks are read-only until deploy is approved.

Remaining issues / next step: finish the open acceptance items, test on a real
mock sitting (desktop + phone), then commit and ask for deploy approval.
