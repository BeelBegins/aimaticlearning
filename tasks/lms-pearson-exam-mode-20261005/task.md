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

Reference: `docs/pearson-reference.md` (observed 2026-10-05; has the gap table).

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

Remaining issues / next step: close the gaps in the reference's table (radio-only
options, no Skip, yellow flag, row-list review screen), then finish the open items, test on a real
mock sitting (desktop + phone), then commit and ask for deploy approval.

2026-10-05 update: JS/CSS rewritten to the reference (no Skip, radio-only
options, yellow flag, last Next opens a row-list Item Review Screen, footer
Previous/Next only). Assets bumped to `20261005-pearson1`. JS syntax and CSS
brace balance checked only; NOT yet seen in a browser. Next: `bench build --app
aimaticlearning` + cache clear on a test sitting (needs approval), compare
side by side with the MCT screenshots, then commit.

2026-10-05 fix after user report (review screen could not open a question or end the test): goToQuestion now steps native Previous/Next (pager only shows 5 numbers); LMS confirm Dialog z-index raised above the review overlay. Assets `20261005-pearson2`. Still unverified in a browser.

2026-10-05: added "Exit to Mock Exams" link (/learning-mock-exam) in the Pearson top bar and review bar; user could not leave a sitting. Assets `20261005-pearson3`.

2026-10-05: mock exam style is now asked on every Start click (no early return on stored choice); lobby redesigned with dashboard tokens (nav pills, hero chips, session tiles, attempt dots, disabled when attempts used up). Assets `20261005-pearson4`. Browser check pending.

2026-10-05 harness run: all 24 checks pass in headless Chromium against a stand-in DOM (`scripts/exam-mode-harness`). Fixed three real bugs it found: review rows re-rendered forever (observer loop) so they could not be clicked, stale saved style closed the Start modal immediately, far jumps needed stepping. Remaining: confirm once on a real mock sitting at lms.aimatic.tech (Start creates no server record; never confirm Submit). Not observed in MCT: Calculator look, Instructions text, End Test confirm text.

2026-10-05 learner test: (1) no way to open the review screen mid-test: added a footer 'Review Screen' button; (2) a review row walked through every question ('zombie' slow): now one native step then a direct jump (291ms vs ~6s in the harness), selection zeroed so the stepped-through answer cannot leak, answers still saved; harness now models switchQuestion/selected refs with latency, 32 checks. Assets `20261005-pearson6`. Still to confirm on a real sitting.
