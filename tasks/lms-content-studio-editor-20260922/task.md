# Task: lms-content-studio-editor-20260922

Goal: Make Content Studio usable for daily SQE editing: 5-option MCQs, searchable collapsed lists, unsaved-edit protection, persist flashcard source quotes, and keep exam courses out of the subject list.

Project and environment (verified role, or unknown): LMS `lms.aimatic.tech` (Examic Study). Code in `apps/aimaticlearning`. No SZL mutation.

Relevant apps/files (repository and allowed edit paths):
- `apps/aimaticlearning/aimaticlearning/lms_learning/content_studio.py`
- `apps/aimaticlearning/aimaticlearning/lms_learning/page/learning_content_console/`
- `apps/aimaticlearning/aimaticlearning/lms_learning/doctype/learning_flashcard/`
- `apps/aimaticlearning/aimaticlearning/lms_learning/test_content_studio.py`

Acceptance criteria:
- New MCQs default to five options; editor can add/remove options (2–10).
- Chapter MCQ/card lists are collapsed, searchable, and do not dump every stem as a full form.
- Switching chapter/subject/tab or leaving the page warns when notes/MCQ/card drafts are unsaved; Ctrl/Cmd+S saves the active pane.
- Flashcard source quote round-trips (stored on `Learning Flashcard`, returned in the chapter bundle).
- Studio subject list excludes `sqe1-hard-mocks`; FLK1/FLK2 labels on known subjects.
- Save failures surface an error; last subject is remembered.
- Unit tests for quote field presence, exam-course filter, and default option count.
- No Word-import rewrite, no BLP mega-chapter auto-split, no live question-bank edits.

Constraints (excluded scope, production approval, API/data compatibility):
- Do not modify Frappe/LMS core.
- Adding `source_quote` uses DocType reload on LMS only, not a full `bench migrate` (aimatic Item patch still fails on this site).
- Do not restart queue/redis; Desk asset cache-clear is enough unless workers hold old Python.

Base commit and existing local changes: aimaticlearning exam-product work already uncommitted on this checkout.

Lead / worker / reviewer: this session implements; no separate worker.

Worker branch and isolated worktree: n/a (solo LMS app on main).

Selected skills and project references: `lms-learning`, Desk page `learning-content-console`.

Verification commands:
- `./env/bin/python -m unittest aimaticlearning.lms_learning.test_content_studio`
- `node --check apps/aimaticlearning/.../learning_content_console.js`
- LMS `clear-cache`; ping LMS and szl.

Limits: one implementation pass.

Status: working

Questions and lead answers: user asked for self-chosen Studio improvements while away four hours.

Worker result: implemented in `apps/aimaticlearning` Content Studio. Tests: 17 unittest ok; `node --check` ok. Deployed LMS-only after backup `20260922_140928-lms_aimatic_tech-database.sql.gz`.

Reviewer result:

Result and remaining issues:
- Pass 2 (mounted notes editor, coverage chips, reorder/duplicate, quote paste) also shipped in the same deploy.
- Later: local notes autosave; quote-in-notes UI check before publish.
- Do not auto-split BLP.
