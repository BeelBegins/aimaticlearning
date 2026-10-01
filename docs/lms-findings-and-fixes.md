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

## 2026-09-30 — Content Studio edits bypassed the Version audit trail

**Scope:** `aimaticlearning/lms_learning/content_studio.py`, the staff-facing
editor for notes, chapter MCQs, flashcards, and chapter structure.

**Finding:** Surfaced while investigating this session's earlier unlogged
bulk-publish incident (all FLK1/FLK2 subject courses set back to
`published=1` in one write with no git commit and no `Version` record).
Auditing `content_studio.py` for the same class of gap found several raw
`frappe.db.set_value()` writes that bypass Frappe's automatic
`Document.save()` versioning, so they leave no timestamped diff: chapter
notes (`Learning Chapter Profile.notes_html`, deliberately raw because the
field is `read_only=1` and `.save()` skips it), the mirrored learner-facing
`Course Lesson.body`/`content`, `Course Chapter`/`Course Lesson`/`LMS Quiz`
title renames on chapter rename, and the chapter-removal housekeeping that
retires flashcards, clears `Learning Question Meta.course_chapter`, and
rehomes a lesson's `chapter` link. MCQ and flashcard edits were already safe
— `save_chapter_mcq`/`save_flashcard` use `.save()`/`.insert()`, which Frappe
versions automatically (confirmed today: 87 `LMS Question` + 7 `Learning
Question Meta` Version rows from real Studio edits this morning).

**Fix:** Added `_log_manual_version(doctype, docname, changed)` — inserts a
`Version` doc with the same diff shape Frappe's own save() produces, so
manual writes show up in the standard "View Version" history alongside
normal saves. Called it at every raw-write site above (captures the old
value via `get_value` immediately before the write). Left
`_refresh_profile_mcq_count`'s raw write unlogged on purpose — it's a derived
cache of `LMS Quiz Question` count, not independent content; logging every
refresh would be noise, not signal.

**Verification:** `python3 -m py_compile` clean; full
`test_content_studio.py` suite (24 tests) passes unchanged. Those tests only
cover pure helper functions (0.002s run time, no DB writes), so they don't
exercise the new Version-insert calls directly — not yet confirmed against a
live Studio edit end-to-end.

**Remaining risk:** Not yet verified live (e.g. editing chapter notes in
Studio and confirming a `Version` row appears with the correct before/after
diff). Should be spot-checked next time notes or a chapter title are edited
through Studio.

**Update (same day):** Verified live during the leaked-notes cleanup below —
`Learning Chapter Profile` and `Course Lesson` Version rows were created with
correct before/after diffs for every chapter touched, timestamped at the
apply run. Confirmed working, not just compiled.

## 2026-09-30 — Embedded quiz/glossary content leaking into student notes, 6 subjects

**Scope:** 22 chapters across 5 published, enrolled courses: Solicitors
Accounts (2), Criminal Litigation (10), Wills & Administration of Estates
(6), Tort Law (2), Public Law (2). A 23rd chapter (Dispute Resolution Ch.6
"Remedies") was checked and correctly excluded — see below.

**Finding:** The user had previously set up a "glossary and key terms go to
a Module Assessment revision lesson, not the chapter notes" convention
(documented in `lms-course-upload/SKILL.md`'s Post-import verification, and
partly built as a one-off `dr_clean_notes.py` script for Dispute Resolution
only) but it was never generalized or run for other subjects. A full sweep
of every `Learning Chapter Profile.notes_html` in the LMS for junk-heading
patterns found real leaks well beyond glossaries: Solicitors Accounts Ch.8
had a literal **answer key with explanations** embedded in student notes
(`Question 1: Answer C`, `Question 2: Answer C`, ... with full reasoning per
question) — a genuine academic-integrity leak, since a student could read
the answers directly from their notes without attempting the quiz. Criminal
Litigation (all 10 chapters) and Wills (6 of 6) had full "Scenario-Based
Multiple Choice Questions" / "CHAPTER N: MULTIPLE CHOICE QUESTIONS" sections
with embedded Q&A. Tort Law had exam-technique/"how questions are tested"
guide prose, not actual MCQs. All 6 courses (including Dispute Resolution)
are `published=1` with real enrolled learners (2–4 each) at the time of this
finding.

**Fix:** Generalized `dr_clean_notes.py` into
`aimaticlearning/lms_learning/clean_leaked_notes.py` — same heading-strip
approach (BeautifulSoup, regex-matched junk headings, remove heading +
following siblings up to the next same/higher-level heading), plus a new
`TERMINAL_JUNK_HEADING` category for whole-section MCQ dumps: verified
across every real instance that this heading is always the chapter's last
(or second-to-last, followed only by a stray malformed options-as-heading
fragment from the original Word import) section, so those consume to end of
document rather than stopping at the next heading — the non-terminal size
cap (3000 chars, a false-positive guard) doesn't apply to them since the
heading text itself is specific enough that false positives aren't a risk.
Ran dry-run first (read-only), manually checked the one non-terminal
oversized skip (DR Ch.6, 6197 chars) by reading its actual content —
legitimate substantive teaching on contract/tort remedies (Hadley v
Baxendale, penalty clauses), not junk, correctly left untouched — then
applied. Full per-chapter backup (`before`/`after` body, notes_html,
content) written to
`private/files/lms_learning_exports/leaked-notes-cleanup-backup-20260930-205037.json`
before any write. Every write now also logs a `Version` record via
`content_studio._log_manual_version` (see the audit-trail fix above),
timestamped at the apply run.

**Verification:** `verify()` after apply: only the DR Ch.6 false-positive
still shows its (legitimate) heading — every one of the 22 real leak
chapters is clean, no leftover junk headings, `content` empty on every
touched lesson, `<article>` tags balanced. Spot-checked Solicitors Accounts
Ch.8 directly: `"Answer C"` and `"Answers with Explanations"` no longer
present anywhere in the notes; `Version` rows exist for both the `Learning
Chapter Profile` and `Course Lesson` with the correct before/after diff.
182,438 characters removed across 22 chapters.

**Remaining risk:** This was a one-time sweep of content that existed today.
If future Word imports for these or other subjects reintroduce the same
"notes + embedded questions" combined-source pattern (seen earlier this
session in the raw `BLP notes and Questions .docx` / `PL MCQs.docx` source
files), the leak recurs — the fix is in the cleanup script, not the
importer. `lms-course-upload/SKILL.md`'s Post-import verification step
("Glossary/key-concepts leaking into notes") already tells future imports
to scan for this before publish; it should be extended to explicitly cover
embedded MCQ/answer-key blocks too, not just glossary banners, since that
turned out to be the more serious leak shape.

## 2026-09-30 — BLP Chapter 1 MCQs invisible to students, recurring defect finally root-caused

**Scope:** `business-law-practice-blp` Chapter 1 ("Forms of Business
Organisations") chapter MCQ lesson (`0062 Chapter MCQ — Introduction`,
quiz `introduction-chapter-mcq-20`). Same class of defect as the 2026-09-17
"SQE1 hard mocks empty lesson fix" and the 2026-09-30 Dispute Resolution
Ch.8 finding above — this is the third confirmed occurrence, and the first
one actually root-caused at the mechanism level rather than fixed by
deleting/recreating the broken lesson.

**Finding:** User reported BLP Chapter 1 MCQs weren't showing for students;
editing one MCQ in Content Studio made all of them reappear, and asked why
this keeps recurring given it was "fixed" before. `Version` history on the
lesson gave the exact mechanism: Frappe LMS's `Lesson.vue` renders the
CodeX/EditorJS widget whenever `Course Lesson.content` is truthy, and only
falls through to the `body` + `quiz_id` quiz widget when `content` is empty
(documented in this repo's own `new_quiz_lesson_values` docstring — the
convention was known, just not enforced). On 2026-09-30 11:14–11:15, a real
content-team login (`sehrishishtiaq331@gmail.com`, not `Administrator`) made
three saves roughly 20 seconds apart, each one changing `content` from
empty to a one-paragraph EditorJS blob carrying the *same text as the
existing `body` placeholder* — the signature of the native Frappe LMS lesson
editor round-tripping `body` into its `content` working buffer and
committing it on save, with no real edit involved. This hid the quiz widget
behind a static paragraph for every student until the chapter re-render.
`_empty_quiz_lesson_content()` / `ensure_quiz_lesson()` already existed and
correctly clear `content` — but only as a side effect of specific Content
Studio actions (`save_chapter_mcq`, chapter add/remove), never as a general
invariant. Editing any MCQ in that chapter incidentally called
`ensure_quiz_lesson`, which is why that "fixed" it — coincidence, not
causation. A standalone manual sweep/fix utility
(`outline_sync.clear_quiz_lesson_editorjs`) already existed too, but nothing
called it automatically. Swept the whole LMS: zero other quiz lessons are
currently poisoned (BLP Ch.1 was already fixed by the user's Studio edit
before this investigation), so this was a preventive fix, not a live
cleanup.

**Fix:** Added `outline_sync.enforce_empty_quiz_content(doc, method=None)`
and wired it as a `Course Lesson` `validate` hook in `hooks.py`. Runs on
*every* save of a `Course Lesson`, regardless of which UI or script wrote
it — the native Frappe LMS lesson editor, Content Studio, a one-off script,
anything. Turns the "quiz lessons must keep `content` empty" convention from
a Studio-only side effect into an enforced doctype-level invariant.

**Verification:** `python3 -m py_compile` clean on `outline_sync.py` and
`hooks.py`. Added `TestEnforceEmptyQuizContent` (3 cases: clears when
`quiz_id`+`content` both set, leaves alone when no `quiz_id`, no-op when
already empty) to `test_outline_sync.py` — full module (5 tests) passes.
**Not yet effective on the running site** — `doc_events` hooks are read from
the app's hooks cache at process start; the web/worker processes need a
restart (or `bench clear-cache` at minimum) to pick up the new registration.
That is a live, impactful action on a shared bench that also runs
production `szl` — needs separate explicit approval before it's actually
enforced, not just written.

**Remaining risk:** Until that restart happens, this fix exists in code but
is not actually protecting anything yet — the next native-editor
open-then-save on any quiz lesson will still poison it exactly as before.
Also: this only guards `Course Lesson.content`; if a future defect turns out
to be `body` going null/empty instead (the exact shape of the earlier
Dispute Resolution Ch.8 incident), this hook won't catch that — that failure
mode still has no systemic guard, only the manual
`lms-course-upload/SKILL.md` checklist.

## 2026-09-30 — BLP Chapter 3 Q16/Q17 wrong answer key, traced to a source-file regression

**Scope:** `business-law-practice-blp` Chapter 3 ("Private Limited
Companies – Formalities, Statutory Filing and Disclosure"), quiz
`the-tax-year-and-collection-methods-chapter-mcq-20`, questions 16
(`QTS-2026-00140`) and 17 (`QTS-2026-00141`). Both tagged `ai_generated=0`
(human-reviewed).

**Finding:** User reported the marked-correct answers for Q16/Q17 were
wrong and didn't match the chapter notes. Checked the chapter's own
notes_html first: it states plainly, three separate times (main text,
glossary, chapter summary), that "the model articles do not include
restrictions on the transfer of shares... members are free to transfer
their shares to anyone." Q16's live answer key marked option B ("the model
articles give directors power to refuse transfers") correct, citing a
specific but unverifiable "Article 26" — directly contradicting the
chapter's own teaching 3-to-1 within the same document. Traced to the
source file: the question's `source_reference` cited the original `BLP
notes.docx` (uploaded 2026-08-30), which no longer exists on disk — it was
silently replaced by a 2026-09-24 re-upload (`BLP notes75b9d6.docx`, a
duplicate of `BLP notes75b9d675b9d6.docx`). That 09-24 file has the *same*
wrong answers live in the DB today (B for Q16, C for Q17) — but an older,
still-present file, `BLP notes and Questions .docx` (orphaned, no `File`
record, uploaded 2026-09-02 — the one already established as the real
source for this subject's 181 human-reviewed questions), has *correct*
answers for both, with explanations that quote the chapter's own notes
verbatim and properly engage with the competing options (Q17's correct
answer, D, explicitly rules out C: "Option C treats this as pure
entrenchment requiring procedural compliance" — a nuance the live/wrong
version's explanation never addressed). Conclusion: the 09-24 re-upload
regressed at least these two answer keys from a previously-correct state —
not an import bug, an authoring regression in the source material itself.

**Fix:** Updated both `LMS Question` docs directly: Q16 correct option
flipped B→C, Q17 correct option flipped C→D, explanations replaced with the
full reasoning from the correct (2026-09-02) source, and each question's
`Learning Question Meta.source_reference` repointed from `BLP notes.docx`
(gone, wrong-answer version) to `BLP notes and Questions .docx` (present,
correct-answer version). Backup of both full question + meta docs before
edit: `private/files/lms_learning_exports/blp-ch3-q16-q17-answer-fix-20260930.json`.
Both saved via `.save()` (Version-logged).

**Verification:** Re-read both questions after save — exactly one option
flagged correct on each (C for Q16, D for Q17), explanation present only on
the correct option, `source_reference` updated on both.

**Remaining risk:** This was a manual, evidence-led fix for two specific
flagged questions, not a systemic sweep. If the 09-24 re-upload regressed
other answer keys the same way, they're still live and wrong — this
incident is reason enough to diff `BLP notes and Questions .docx` (09-02,
correct) against `BLP notes75b9d6.docx`/`BLP notes75b9d675b9d6.docx` (09-24,
at least 2 answers regressed) question-by-question across all 8 BLP
chapters before trusting the rest of the bank, and to check whether any
other subject's "answer key" source file was similarly re-uploaded with
regressions. Not done in this session — flagging for a dedicated pass.

**Correction (2026-10-01): the above fix was backwards — reverted.**
See the next entry below.

## 2026-10-01 — BLP Ch.3 Q16/Q17 fix above was wrong direction; reverted, and the flagged wider sweep found no real defects

**Scope:** Same two questions as above (`QTS-2026-00140`/Q16,
`QTS-2026-00141`/Q17), plus the "dedicated pass" the prior entry flagged: a
full 09-02-vs-09-24 answer-key diff across all 8 BLP chapters.

**Finding:** Ran the flagged diff. Comparing each chapter's embedded
self-check "Questions: N,M | Answers: X,Y" table between the 09-02 and 09-24
files showed **zero differences** — that table is byte-identical in both
files. Comparing each question's full detailed-reasoning paragraph (the
"Question N: Answer X ... Reason: ..." text) found **11 mismatches** across 7
chapters (the 2 already "fixed," plus 9 more: Ch1 Q14, Ch3 Q11, Ch4 Q13, Ch4
Q15, Ch5 Q14, Ch6 Q17 [chapter not even imported into the live course — no
live impact], Ch7 Q20, Ch8 Q5, Ch9 Q23). The self-check table agreed with the
09-02 reasoning and disagreed with the 09-24 reasoning in every live-relevant
case, which read at first like proof 09-24 had regressed. **User corrected
this 2026-10-01**: the solicitor deliberately revised a set of answers and
sent the 09-24 file with the changed answers highlighted in red — 09-24's
detailed-reasoning paragraphs are the authoritative, intentionally-corrected
version. The self-check table is a stale leftover that was never updated
during the solicitor's revision, so its agreement with 09-02 is not evidence
of correctness — it's evidence of being unmaintained. Re-reading the full
reasoning paragraphs (not just the answer letters) on close inspection
supports this: several 09-02 reasoning blocks are internally confused or
self-contradicting (e.g. Ch4 Q13's own text says "the better interpretation…
appears to exceed… making it unlawful. However, Answer A is marked correct,
suggesting…"; Ch5 Q14's own text says "This makes option D potentially
correct" while marking A correct), while the matching 09-24 replacement text
is clean and cites specific authority (e.g. Companies Act 2006 s.307(4) for
short-notice meetings, *Garner v Murray* (1903) for partnership-deficiency
apportionment, *Hosking v Marathon Asset Management LLP* [2016] for LLP
member-admission default rules, PA 1890 s.9 for joint partner liability).

**Correction:** Reverted `QTS-2026-00140` (Q16) and `QTS-2026-00141` (Q17)
back to the 09-24/solicitor answers (B and C respectively) with the matching
explanation text, restoring the exact state the 2026-09-30 fix had
overwritten (confirmed via that fix's own pre-edit backup). Updated
`source_reference` on both to `BLP notes75b9d6.docx Ch3 Q16/Q17
(solicitor-revised answer)`. Backed up the incorrect intermediate (09-30 fix)
state before reverting:
`private/files/lms_learning_exports/blp-ch3-q16-q17-incorrect-fix-state-20261001.json`.
The other 9 flagged mismatches were **not** touched — live DB already carries
the correct 09-24/solicitor answer for all of them (verified directly against
each `LMS Question`'s stored `is_correct_*`), so no further action was
needed; Ch6 Q17 has no live record at all since that docx chapter was never
imported.

**Verification:** Re-read both reverted questions — Q16 correct option is
`option_2` (B) with explanation present, Q17 correct option is `option_3`
(C) with explanation present, matching the pre-09-30-fix backup exactly.
Cross-checked all 9 other flagged questions' live `is_correct_*` flags
against the 09-24 detailed-reasoning answer — all 9 already match.

**Remaining risk:** The self-check "Questions: N | Answers: X" tables
embedded in BLP chapter notes are confirmed stale relative to the solicitor's
answer revisions and should not be used as an answer-key source for any
future BLP work — the per-question detailed-reasoning paragraph is the only
reliable in-document source, and even that should be treated as provisional
unless it carries the solicitor's red-highlight marking. This session did not
check whether any *other* subject's source file has the same
revised-reasoning-vs-stale-table split; if a similar defect is suspected
elsewhere, diff detailed-reasoning paragraphs specifically, not summary
tables. Lesson learned: a document-internal-consistency argument (two
sections of the same file agreeing) is not a substitute for asking whose
revision is authoritative — should have asked before applying the 09-30 fix
instead of inferring it from file structure alone.

## 2026-10-01 — Criminal Litigation question bank: every question started with a stray ": "

**Scope:** `criminal-litigation` course (`LMOD-01087`), all 11 chapters, all
220 chapter-MCQ questions (`QTS-2026-01191`–`QTS-2026-01410` range).
Published, `ai_generated=0` (human-reviewed), live with 582 quiz links
across chapter quizzes, the module assessment, and mocks.

**Finding:** User reported a question rendering with a leading colon. A
database scan for `question like ': %'` found the defect was not isolated —
literally every question in the Criminal Litigation bank had the exact same
`": "` (colon-space) prefix, e.g. `": What is the primary purpose of PACE
1984..."`. Root cause not investigated further (importer/parser artifact
from stripping a "Question N:" label and leaving the trailing colon-space
behind) — scope was 100% of one course's bank, not a scattered issue, so no
further root-cause chase was needed to size the fix.

**Fix:** Backed up all 220 `question` field values before editing:
`private/files/lms_learning_exports/criminal-litigation-colon-prefix-fix-20261001.json`.
Stripped the leading `": "` from each via `.save()` (Version-logged).

**Verification:** Re-queried `question like ': %'` after the fix — 0 rows
remain. Spot-checked 5 fixed questions render clean stems with no leading
punctuation.

**Remaining risk:** Checked `option_1`–`option_5` and `explanation_1`–
`explanation_5` for the same `": "` prefix — 0 hits, so the artifact was
confined to the question stem. Other subjects were not swept for the same
pattern — this was scoped to the one course the user flagged.
