# Task: Examic student journey polish

Goal: Improve continuity between the Examic dashboard, revision board, mock lobby and post-mock feedback, with a consistent LMS side navigation and clear study/payment next steps.

Environment: Production site `examic.study`, deployed from branch `student-journey-review-20261008`.

Files / allowed edit paths: Examic-owned `aimaticlearning/www/`, `aimaticlearning/public/`, and learner UX modules only.

Acceptance criteria:
- Dashboard, revision and mock lobby share a persistent learner navigation pane; it adapts for narrow screens and marks the current page.
- Revision retains its data, course selector, and filters while fitting the shared content area.
- Student next action and mock feedback make a useful path from results back to relevant revision.
- Billing/mock access copy clearly differentiates free mocks and paid unlocks, price, and timing.
- No changes to Frappe LMS core.

Constraints: Keep all existing uncommitted user changes. Do not stage or commit unrelated files. No database changes or payments. Avoid tests unless requested.

Base commit and existing local changes: `main` at task start, with unrelated existing working-tree edits. Branch created from the current checkout state without cleaning or resetting files.

Skills used: `lms-learning`, `lms-billing`.

Verification: `git diff --check`; production HTML, linked assets, and route responses checked after deployment. No tests.

Status: deployed; logged-in learner visual review pending.

Remaining issues / next step: Owner review in a logged-in student browser; no student credentials were used during deployment verification.
