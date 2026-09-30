# Examic LMS findings and fixes

Use this as the repository record for verified learner-facing quality findings
and their corrections. It is not a scratchpad and is not a substitute for a
backup, test result, or source approval.

## Entry format

For every entry include:

- date and LMS scope;
- evidence and affected record count;
- source checked and whether it is the latest approved source;
- exact corrective action;
- tests and non-destructive learner-route verification;
- remaining risk or a clear statement that none is known.

## 2026-09-30 — MCQ quality standard

**Scope:** Chapter MCQs and mock questions.

**Finding:** Learner-facing MCQ quality needs one shared gate across imports,
mapped content, feedback, and display rather than agent-specific instructions.

**Correction:** Added `skills/lms-mcq-quality/` as the canonical shared quality
workflow. It requires one stored correct option, source/mapping checks,
correct-answer-only handling for duplicated general explanations, no internal
source trails, and the shared A-E full-row selection treatment.

**Verification:** The workflow is available through the repository adapters for
Codex, Claude Code, and Cursor. Individual question-bank corrections remain
separate, evidence-led work and require their own entry.

**Remaining risk:** Historical reports may contain stale content status. Verify
the latest source file, database state, and learner route before changing a
question bank.

## 2026-09-30 — Word-source retirement and recurring import gaps

**Scope:** Content import guidance (`lms-course-upload`, `lms-learning`,
`lms-mcq-quality`), not a specific content sweep.

**Finding:** Guidance previously implied the Word source stays an ongoing
sync target after import. In practice, once Content Studio has edited a
chapter, re-importing from Word would silently overwrite the live edit —
Studio becomes the source of truth for that chapter after first publish.
Separately, three defect patterns have recurred across imports without a
standing check: MCQs published with no explanation, chapters short of their
target MCQ count, and end-of-chapter summary/glossary banners leaking into
the notes body instead of the Module Assessment Quick Revision lesson (the
latter already fixed once each for Dispute Resolution and Legal Services,
2026-09-25).

**Correction:** Added a "Word source retirement" rule to `lms-course-upload`
and `lms-learning` (Word is authoritative only up to first verified publish;
never re-import over a Studio edit without explicit, evidenced sign-off).
Added explicit post-import/quality gates for the three recurring gaps to
`lms-course-upload`'s "Post-import verification" and `lms-mcq-quality`'s
gate 5.

**Verification:** Guidance-only change; no content was audited or modified.

**Remaining risk:** No current field marks "edited in Studio since import,"
so agents must ask rather than infer. The three named gaps have not been
swept across existing published subjects yet — that audit is separate,
evidence-led work and needs its own entry when run.

## 2026-09-30 — Dispute Resolution Ch.8 MCQ not visible to students

**Scope:** One chapter MCQ lesson, `dispute-resolution` / Chapter 8:
Commencing Proceedings.

**Finding:** Student reported the chapter's MCQs didn't show, despite the
question bank existing and being visible in Content Studio. A full sweep of
all 23 quiz lessons in the course found the other 22 structurally healthy
(published course, correct chapter-rail links, valid `quiz_id`/`LMS Quiz`
pairing, empty `content`, well-formed questions, permission check passing for
a real enrolled member). The broken lesson (`3915 Chapter MCQ — Chapter 8`)
had already been deleted by the user via Content Studio before root cause was
found; recovered via Frappe's `Deleted Document` snapshot. Root cause:
`content = ""` (correct) but `body = null` — Frappe LMS only mounts the quiz
widget through the `body` fallback when `content` is empty, so a lesson with
both empty renders blank with no visible error. Identical root cause to the
2026-09-17 "SQE1 hard mocks empty lesson fix," recurring here outside the
mock system.

**Correction:** No code fix applied — the user deleted the broken lesson from
Content Studio and a replacement (`6626 Chapter MCQ — Chapter 8`) with a
correct placeholder body already exists and is healthy. Added an explicit
"quiz lesson with empty body renders blank" check to
`lms-course-upload`'s Post-import verification so this stops recurring
silently.

**Verification:** Confirmed the replacement lesson has `content=""` and a
non-empty placeholder `body` (74 chars), matching every other healthy quiz
lesson in the course.

**Remaining risk:** The code path that creates/ensures chapter MCQ lessons
(shared by multiple ensure-lesson helpers across `course_presentation.py`,
`content_studio.py`, `outline_sync.py`) was not audited for *why* it
sometimes omits the placeholder body — this was root-caused and fixed by
deletion, not by finding or fixing the code defect that created the broken
lesson in the first place. A recurrence elsewhere is possible until that
importer-side gap is found.
