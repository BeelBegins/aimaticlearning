---
name: lms-mcq-quality
description: Audit and correct Examic LMS chapter MCQs and mock questions when importing, mapping, publishing, or reviewing learner feedback. Use for learner-facing content quality, not general course copy edits.
---

# Examic LMS MCQ Quality

Use this skill to protect learner-facing question quality in Examic Study's
Frappe LMS.

## Scope and boundaries

- Treat internal source references, filesystem paths, import traces, and
  content-review metadata as staff-only. Do not expose them in question text,
  option text, explanations, or learner feedback.
- Preserve legal content and the stored correct answer. Do not invent missing
  distractors or explanations to meet a visual convention.
- An audit is read-only. Get explicit user authority before mass-cleaning
  records, re-importing content, relinking quiz questions, or publishing a
  changed question bank.

## Source rules (learner-facing content)

- **Never author MCQs.** Chapter MCQs come only from the uploaded Practice
  Questions Word file, with its own answers and explanations, through
  `parse_mcqs_from_docx`. If a chapter has no source MCQs, report the gap;
  do not generate questions, even from the chapter notes. A model-written
  MCQ is `ai_generated = 1`, is never linked to a chapter quiz, and is kept
  out of learners' sight unless the user explicitly sends it to mocks.
- **Names:** scenarios use common English names (Emma, Oliver, James, Emily).
  Never use culturally specific names such as Nadia, Zoe or Zoha. Check
  question, option, and explanation text.
- **Flashcards:** each `source_quote` must match the notes text after tags are
  stripped to spaces, so keep quotes inside one formatted run (no bold terms or
  bracketed citations at their edges). Never split notes by paragraph into
  "What is the key point about…" cards.
- **Before importing a chapter,** count its MCQs, flashcards and notes in the
  database first; an empty chapter with notes is a content gap, not a layout
  problem. After import, confirm one correct option and a non-empty
  explanation per question, and read the learner deck/quiz as an enrolled
  student.

## Quality gates

For each affected chapter MCQ or mock item, verify:

1. **Mapping:** the question is linked to the intended Learning Chapter
   Profile, course chapter, and quiz; identify orphaned, duplicate, or
   cross-chapter items.
2. **Answer integrity:** a single-choice MCQ has exactly one correct option
   and the displayed choices match the stored option fields.
3. **Explanation integrity:** no `Source:` trail, filesystem path, attachment
   identifier, or internal metadata is visible to learners. If one general
   explanation has been copied to every choice, retain it only under the
   correct answer. Preserve genuinely distinct, option-specific explanations.
4. **Learner UI:** chapter MCQs and normal-style mocks use the same answer-label
   treatment: uppercase A-E in a letter circle, the selected answer row
   highlighted, and the native radio/checkbox visual hidden. Pearson-style mocks
   are the one exception: plain radio circles, no letters, no highlight
   (`docs/pearson-reference.md`). Check keyboard focus and a narrow mobile layout.
5. **Completeness, not just integrity of what exists:** every question has a
   non-empty explanation — an MCQ with a correct option but no explanation is
   a defect, not an acceptable minimum. Separately, count published questions
   per chapter/lesson against that subject's target spec; a short count is a
   coverage gap to report and fix, never something to leave silently short.
   Both of these have recurred as real defects — check for them explicitly,
   don't assume the importer caught them.

## Workflow

- Inspect the latest approved source, parser output, database values, and
  mapping records before proposing a correction. Count affected questions and
  fields first.
- Run focused parser, explanation-cleanup, and page-rendering tests. Check
  syntax for changed client assets.
- For a legacy cleanup, modify only evidenced bad fields, preserve useful
  explanation text, report exact counts, and query again to prove the invalid
  pattern is gone.
- Fix the importer or generation boundary that created the defect; do not
  rely only on hiding flawed data in CSS.
- Verify the deployed asset version and one non-destructive learner route for
  a chapter MCQ and a mock. Never consume a production attempt merely to test
  display.

## Completion record

Record verified findings and fixes in `docs/lms-findings-and-fixes.md`.
Separate data provenance (for example, automated generation or source import)
from a named human author unless authoritative records identify that person.
Include checks run, exact impact, and any remaining quality risk.
