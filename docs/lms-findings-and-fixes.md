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
