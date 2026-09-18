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

1. Verify site role is `lms.aimatic.tech`.
2. `bench --site lms.aimatic.tech backup --with-files`, gzip -t, record rollback.
3. Keep Word sources private. Never attach them as learner downloads.
4. Render student HTML into `Course Lesson.body`. Always set `content = ""`.
5. Record source File name, content hash, and section locator on the Learning
   Chapter Profile. Preserve lesson names and progress.
6. Do not auto-enrol. Do not merge subjects into BLP. No broad BLP re-import
   without a dry run.

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
