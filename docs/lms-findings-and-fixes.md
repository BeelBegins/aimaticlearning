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
