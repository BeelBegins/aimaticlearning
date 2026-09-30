# Course upload pipeline

Site: `lms.aimatic.tech`. Code: `aimaticlearning.lms_learning.course_upload`.
Preferred model: Claude Opus thinking (high).

## Commands

```bash
cd /home/nabeel/frappe-bench
# Do not take an LMS backup unless asked.

# 1. Dry-run coverage (no write)
bench --site lms.aimatic.tech execute aimaticlearning.lms_learning.course_upload.coverage_report --kwargs '{"course":"contract-law","source_file":"ca1d016ce3"}'

# 2. Attach lessons to the LMS chapter rail (required for /learn/N-1)
bench --site lms.aimatic.tech execute aimaticlearning.lms_learning.course_upload.relink_notes_lessons
```

Rollback: revert the content change. Backup LMS only if asked.

## Lesson write rules

- `body` = student HTML from the matched Word chapter (headings, paras, tables).
- `content` = `""` always. Stale EditorJS in `content` duplicates/raw-dumps.
- Quiz/MCQ/assessment lessons: `quiz_id` set, `content = ""`. EditorJS in
  `content` hides the LMS quiz widget. Scan all `quiz_id` lessons before
  publish; clear leftovers with `clear_quiz_lesson_editorjs`.
- Do not rename lessons or delete progress.
- Profile: bump `source_revision`; store `source:<file> hash:<md5> locator:<heading>`
  in `concept_tags`; copy HTML to `notes_html`.

## Coverage report columns

| Source heading | Chapter # | LMS lesson | body chars | content chars | tables | gap |
|---|---|---|---:|---:|---:|---|

A lesson is a **gap** if body is empty, only a draft banner, or the source
heading has no mapped lesson. Do not start a question-bank import until this
report has been reviewed for that subject.

## MCQ dry-run (after notes coverage is reviewed)

Use `mcq_import.parse_mcqs_from_docx`. Output reviewer JSON/CSV with stem,
options, proposed answer, explanation, difficulty, chapter, concept, source
locator, hash, duplicate/malformed flags. **Proposed ≠ published.** Do not
treat option A as correct.

## Current FLK1 empty repairs (2026-09-02)

| Lesson title (match) | Course | Source File |
|---|---|---|
| Draft notes — Chapter 4: Money Laundering | `legal-services` | `56a723d3a4` |
| Draft notes — Chapter 5: JUDICIAL REVIEW | `public-law` | `e91c530519` |
| Draft notes — Chapter 7: The Legal System of England and Wales | `public-law` | `e91c530519` |

Then coverage reports for `contract-law` / `ca1d016ce3`, `tort-law` /
`8f112abe93`, `dispute-resolution` / `6f5a6a3e41`. Stop before question banks.

Canonical source IDs: Contract notes `ca1d016ce3`, questions `8921cae191`;
DR notes `6f5a6a3e41`, questions `44d3c2a638`; Tort notes `8f112abe93`,
questions `d7d445ef37`; Legal Services notes `56a723d3a4`; Public Law notes
`e91c530519`. Ignore hash-suffixed duplicate File rows.
