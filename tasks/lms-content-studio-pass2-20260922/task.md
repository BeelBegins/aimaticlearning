# Task: lms-content-studio-pass2-20260922

Goal: Second Content Studio editor pass while the operator is away: keep the notes editor mounted across tabs, stop full chapter reloads on notes/MCQ/card save, SQE option letters, chapter coverage chips, MCQ reorder/duplicate, learning objective, and paste a notes selection as a flashcard source quote.

Project and environment (verified role, or unknown): LMS `lms.aimatic.tech`. Code in `apps/aimaticlearning`. No SZL mutation.

Relevant apps/files (repository and allowed edit paths):
- `apps/aimaticlearning/aimaticlearning/lms_learning/content_studio.py`
- `apps/aimaticlearning/aimaticlearning/lms_learning/page/learning_content_console/`
- `apps/aimaticlearning/aimaticlearning/lms_learning/test_content_studio.py`

Acceptance criteria:
- Notes Text Editor stays mounted when switching Notes/MCQs/Cards; Ctrl/Cmd+S still saves the open pane.
- Saving notes, an MCQ, or a card does not remount the notes editor unless the chapter heading rewrite changed the notes HTML.
- New/edited MCQs show A–E (up to J) letters in the editor only; no `option_letter` database field.
- Chapter list can filter Empty notes and Short MCQ (below the module target).
- Move up/down reorders only the chapter quiz child table; Duplicate creates a new LMS Question with a `(copy)` stem and a confirm step before it is linked to the live chapter quiz.
- Flashcard source quote can be filled from a notes selection captured before leaving the Notes tab.
- Unit tests cover quote field list, reorder neighbours, and copy-stem suffix.

Constraints (excluded scope, production approval, API/data compatibility):
- Do not auto-split BLP mega-chapters or rewrite Word imports.
- Do not modify Frappe/LMS core or restart SZL queues.
- Duplicate is an explicit editor action; do not silently clone banks.

Base commit and existing local changes: Content Studio and exam-product work already uncommitted on `apps/aimaticlearning`.

Lead / worker / reviewer: this session implements; no separate worker.

Worker branch and isolated worktree: n/a.

Selected skills and project references: `lms-learning`, `bench-ops`.

Verification commands:
- `./env/bin/python -m unittest aimaticlearning.lms_learning.test_content_studio`
- `node --check apps/aimaticlearning/.../learning_content_console.js`
- LMS backup, `reload-doc` Learning Flashcard, `bench build --app aimaticlearning`, site `clear-cache`, web-only restart, ping LMS and szl.

Limits: one implementation pass.

Status: working

Questions and lead answers: operator asked for self-chosen Studio improvements for ~4 hours.

Worker result: shipped with the editor pass. Unittest 17 ok. LMS web-only restart. Backup `20260922_140928-lms_aimatic_tech-database.sql.gz`.

Reviewer result:

Result and remaining issues:
- Still later: local notes autosave, quote-must-exist-in-notes UI check before publish, keep MCQ pane scroll when returning to the tab.
- Do not auto-split BLP.
