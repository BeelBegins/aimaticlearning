---
name: lms-learning
description: Build and operate Aimatic's Frappe Learning product at lms.aimatic.tech. Use for LMS course/chapter/lesson structure, protected study notes, chapter MCQs and feedback, flashcards, module assessments, learner analytics, AI-assisted content drafting, instructor tools, and LMS-specific site changes.
---

# Examic Study

Product repo for `lms.aimatic.tech` / examic.study. Do not load SZL retail
skills. Keep Frappe LMS upstream-compatible. Put every owned feature in
`aimaticlearning/lms_learning/`; never modify `apps/lms` or Frappe core.

## Working model

- Read `docs/current-state.md` in this repo. For BLP course state, `blp-handoff.md`.
  For Word import, empty-lesson fill, or coverage reports, load `lms-course-upload`.
- Do not install LMS features on `szl`, `siezal`, or `hsm`, or couple them to
  POS data. `siezal.aimatic.tech` is SZL test, not an LMS sandbox.
- Use `bench-ops` for site, proxy, worker, certificate, backup, or migration.
  This bench shares workers with live `szl`.
- Use Frappe LMS for course, chapter, lesson, enrolment, and baseline quiz
  behaviour. Keep Aimatic additions namespaced to avoid collisions.

## Content and privacy

- Store Word sources and original assets privately. Publish rendered lesson content,
  enforce authentication server-side, and do not claim screenshots/copying can be stopped.
- Tag every MCQ and flashcard with chapter, concept, learning objective, difficulty,
  source reference, and revision. Preserve attempts against their question revision.
- AI may only draft from approved source material. Require human review before
  publication and do not present generated legal content as authoritative advice.
  Generated flashcards must include an exact quote from the approved chapter notes;
  reject cards whose quote cannot be found in those notes.

## Learning data and release

- Record correctness, elapsed time, attempt order, and topic tags. Make mastery
  thresholds and revision recommendations transparent and auditable.
- Keep chapter MCQs, the 150-question module assessment blueprint, and the
  200-card target explicit; never silently duplicate or discard approved questions.
- Test permissions, lesson visibility, scoring, feedback, question selection,
  analytics, and generated-content approval. Obtain the live gate before a site
  mutation, then migrate/build/reload only what changed.
