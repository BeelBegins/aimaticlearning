---
name: lms-course-upload
description: >-
  Reusable LMS course-content upload at lms.aimatic.tech. Use when importing
  Word notes or question banks, filling empty Course Lessons, mapping source
  headings to lessons, publishing notes-only, or building MCQ/flashcard dry-run
  reports. One LMS Course per subject. Never assume an MCQ answer key.
---

# LMS course upload

Reusable pipeline for `lms.aimatic.tech` / examic.study. Owned code only:
`aimaticlearning/lms_learning/`. Never edit `apps/lms`, Frappe core, or SZL sites.

**Model:** use Claude Opus thinking (high) for Word-to-lesson rendering, source
coverage audits, legal gap drafts, and MCQ review packs. Do not use fast/flash
models for answer keys or student-facing legal HTML.

Read [pipeline.md](pipeline.md) before mutating. Implementation:
`aimaticlearning.lms_learning.course_upload`.

## Every upload

1. Verify site role is `lms.aimatic.tech`. Do not take an LMS backup unless asked.
2. Keep Word sources private. Never attach them as learner downloads.
3. Render student HTML into `Course Lesson.body`. Always set `content = ""`.
4. Record source File name, content hash, and section locator on the Learning
   Chapter Profile. Preserve lesson names and progress.
5. Do not auto-enrol. Do not merge subjects into BLP. No broad BLP re-import
   without a dry run.
6. After import, run the checks in "Post-import verification" below before
   calling a subject done. A rendered lesson with a non-empty body is not
   proof the import is complete or correct.

## Word source retirement

The Word file is the source of truth **only up to first verified publish** of
a chapter. Once a human has edited that chapter's notes or MCQs directly in
Content Studio, the Word file is historical import evidence only — never
re-render or re-import over Studio-edited content, even to "fix" it against
the source. A Studio edit is the newer fact; blind re-import from Word
silently destroys it. If a chapter genuinely needs re-importing from Word
after Studio edits exist, that is a deliberate, user-approved decision: list
what the Studio edit changed, get explicit sign-off that it's fine to lose,
and say so in the commit/finding record. Studio has no field marking "edited
since import" today — when unsure whether a chapter was hand-edited, ask
before touching it, don't assume the Word file still wins.

## Post-import verification

Before a subject is called imported/published, check all of these — each has
recurred as a real, separately-fixed defect:

- **Missing MCQ explanation.** Every published MCQ has a non-empty
  explanation, not just a stored correct option. A parsed question with no
  explanation is a parser gap, not an acceptable gap — fix the importer, do
  not publish it bare and move on.
- **Missing MCQs per lesson.** Compare each chapter/module's actual published
  quiz question count against its target spec (e.g. `FLK2_MCQ_SPECS` or the
  equivalent for the subject). A short count is a gap to report and fix, not
  something to publish silently short.
- **Glossary/key-concepts leaking into notes.** Chapter study notes must not
  contain an embedded end-of-chapter summary/glossary bank (literal banners
  like `CHAPTER N SUMMARY` or `Key Glossary Terms`). That content belongs in
  the subject's Module Assessment "Quick Revision Notes — Key Concepts &
  Glossary" lesson, before the assessment — not inside the notes body. Scan
  every imported chapter's notes for these banners before publish.

## Notes

- Map every source heading to a non-empty lesson. A non-empty body is not proof
  of coverage — audit heading-by-heading.
- Heading hierarchy, paragraphs, tables, and lists must be readable on desktop
  and mobile. Strip document controls, author names, and tool links.
- Source gaps: add `Review draft — supplement` only, unpublished, with a cited
  UK authority. Do not fabricate statute, case, procedure, or SQE claims.

## Activities

Never assume the correct option because it is first or labelled A. Publish an
MCQ only after answer, explanation, difficulty, concept, chapter, source
locator and revision are explicit and reviewed. Flashcards need the same tags.
Mocks only from reviewed items — never pad by duplicating questions.
SQE1 FLK papers follow `docs/sqe1/` (January 2027 format and SRA topic
checklists). Do not copy Kaplan. A subject module assessment is not an FLK
paper.

Quiz/MCQ/assessment lessons: set `quiz_id` and `content = ""`. Non-empty
EditorJS `content` hides the LMS quiz widget. Before publish, list every
`Course Lesson` with `quiz_id` and non-empty `content` and clear those blobs.
Do not write CodeX/EditorJS onto chapter MCQ or module assessment lessons.

Legal Services / Public Law have no question-bank files: coverage-gap report
plus expert-authored reviewed items. Do not invent scored questions as sourced.

## Labels

Catalogue and FLK1 switcher must match readiness. Show `Study notes` until
practice/revision have passed review. Do not show personal stats to new
students.
