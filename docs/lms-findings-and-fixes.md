# Examic LMS findings and fixes

Use this as the repository record for verified learner-facing quality findings
and their corrections. It is not a scratchpad and is not a substitute for a
backup, test result, or source approval.

## 2026-10-26 — MCQ explanation labels normalized

**Scope:** All learner-facing `LMS Question.explanation_1..10` values on
`examic.study`.

**Finding:** The live question bank used `Reason:`, `Reasoning:`, and
`Explanation(s):` as interchangeable explanation headings.

**Source checked:** Current live `LMS Question` values. No source files or
explanation wording were changed.

**Correction:** Added the idempotent `normalize_explanation_reason_labels`
maintenance helper in `mcq_import.py` and ran it against the live site. It
changed 152 explanation fields to use `Reason:` and preserved all remaining
text. Existing `Reason:` labels were retained.

**Verification:** The dry run identified 152 fields. A post-update scan of all
3,175 questions found zero `Reasoning:` or `Explanation(s):` labels and 393
`Reason:` labels. The quiz API returned a normalized explanation for a linked
question. No test suite was run. The existing full database snapshot from
2026-10-25 17:45 remains available; restoring it would also roll back other
site changes since then.

**Remaining risk:** Future direct edits or imports can introduce another label
variant; the maintenance helper is safe to re-run.

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

## 2026-10-01 — Criminal Litigation Chapter 2 had the wrong display title

**Finding:** User pasted the source "Criminal Litigation" document (11
chapters, 220 MCQs) for QA. Cross-checked against live data: all 11 content
chapters' titles, question counts (20/20 each), and Q1 stems matched the
source verbatim, confirming the colon-prefix fix above preserved content
correctly. One defect found: `Course Chapter` idx 2 (docname `1090 Chapter
2: Criminal Litigation`) had `title = "Chapter 2: Criminal Litigation"` — a
generic placeholder that broke the "Chapter N: <topic>" pattern every other
chapter follows. The source document's actual Chapter 2 is "Police
Investigation and Evidence Gathering"; the question content was already
correct, only the chapter's own display title (shown in course navigation)
was wrong.

**Fix:** Updated `title` to `"Chapter 2: Police Investigation and Evidence
Gathering"` via `.save()` (Version-logged). No question/quiz data touched.

**Verification:** Re-read the chapter after save — title confirmed updated.
The document's internal name/docname still carries the old string
(`1090 Chapter 2: Criminal Litigation`) since that's just the record's
system identifier, not a student-facing field.

**Re-verified live 2026-10-02:** Chapter 2's title is still `Chapter 2: Police
Investigation and Evidence Gathering`; 0 Criminal Litigation questions start
with `": "`; all 220 question-meta rows are `ai_generated=0`. Both Criminal
Litigation fixes above are done and holding.

## 2026-10-02 — BLP Ch.3 Q16/Q17: answers confirmed correct, explanations and notes were the defect; remaining red-marked items not yet checked

**Scope:** `business-law-practice-blp` Chapter 3, `QTS-2026-00140` (Q16) and
`QTS-2026-00141` (Q17), plus lesson `0023 Notes — The Tax Year and Collection
Methods`.

**Finding:** User reported the marked-correct options and their reasons did not
match the notes. The newest BLP source is still the 2026-09-24 file
(`BLP notes75b9d6.docx`, identical to `BLP notes75b9d675b9d6.docx`); no newer
file exists on disk or as a `File` record. Its solicitor revisions are the text
coloured `EE0000` (not `FF0000`; a filter on pure red finds nothing). That file
has 41 red paragraphs; two are Ch3 Q16 = B and Q17 = C, matching the live keys.
Checked against the law: Model Articles for private companies (SI 2008/3229,
Sch 1) art. 26(5) lets the directors refuse to register a share transfer, so
Q16 = B is correct; Companies Act 2006 s.22(1) entrenchment makes Q17 = C
correct. The real defect was the chapter notes, which said the model articles
contain no transfer restrictions (in both the docx and lesson `0023`), and
explanations that did not quote either authority.

**Fix (user-approved):** User rewrote the lesson `0023` passage themselves
(now: pre-emption rights and consent restrictions are commonly added to the
articles). Rewrote the Q16 explanation (on B) to quote art. 26(5), the
directors' duties limit and the notes' pre-emption point; rewrote the Q17
explanation (on C) to cite s.22(1)/(3). Answer keys unchanged. Shortened
`source_reference` on both to name the authority (field max is 140
characters; a longer first attempt failed and wrote nothing). Backup before
edit: `private/files/lms_learning_exports/blp-ch3-q16-q17-explanations-before-20261002.json`.

**Verification:** Re-read both questions: exactly one correct option (B, C),
explanation present only on it; lesson `0023` no longer contains the old
sentence and contains the new pre-emption text.

**Remaining risk / next step:** The other red-marked blocks in the 09-24 file
have not been compared with the live explanations or the notes lesson text:
Ch1 Q14, Ch3 Q11, Ch4 Q13 and Q15, Ch5 Q14 (para 2572 area), Ch6 Q17 (no live
record), Ch7 Q20, Ch8 Q5, Ch9 Q23 and the Ch4 Q4 block. The 2026-10-01 entry
confirmed their answer letters match the live DB; it did not check the
explanations, or whether the notes contradict the solicitor's answer the way
Ch3 Q16 did. Do that check next, one question at a time, and ask before
changing any answer key.

## 2026-10-05 — Pearson-style mock sitting completed and verified

**Scope:** Mock sittings on `lms.aimatic.tech` (`/lms/quiz/mock-*`) and the `/learning-mock-exam` lobby. Development site only; `examic.study` is not yet serving.

**Finding:** The first Pearson-style attempt was built from a web search, not from the real player, so it mixed old and new styles, kept a Skip button, highlighted answer rows, and showed a number grid. After the real MCT player was walked in a browser (`docs/pearson-reference.md`) and learners tested it, three defects remained: review rows re-rendered forever (the DOM observer re-ran on every repaint) so they could not be clicked, a stale saved style closed the Start modal at once so the style was never asked again, and a review jump walked every question one at a time.

**Correction:** `lms_exam_tools.js/.css` now follow the observed player (radio-only options, no Skip, yellow flag, row-list Item Review Screen, footer Previous/Next). Deliberate additions: a footer Review Screen button, an Exit to Mock Exams link. Painting is idempotent. Start clears the saved style so the choice is asked on every attempt. A far jump takes one native step (so LMS saves the answer being left), clears the selection, then sets the active question directly. The lobby was rebuilt on the dashboard tokens, primary-button text colour fixed, decorative kicker bars and em dashes removed from learner copy.

**Verification:** `scripts/exam-mode-harness/run.js` (headless Chromium against a stand-in quiz DOM) passes 32 checks, including jump speed (291 ms vs about 6 s stepping), no stale selection, answers kept, End Test dialog above the review, and normal style unchanged. The owner then verified a real mock on the development site. No server record is created by Start, and Submit was not confirmed.

**Remaining risk:** Calculator look, Instructions text and the End Test confirm text were not observed in the MCT player and are Examic's own. The harness only imitates `Quiz.vue`; re-check on a real sitting after any LMS upgrade. If the LMS Vue refs cannot be found the jump falls back to one-at-a-time stepping, which is slower but correct.

## 2026-10-05 Launch readiness (local only, not live)

- Self-service signups are enrolled in all 13 published courses by `complete_student_signup`; one welcome email; `User.examic_free_until` = signup + 60 days (no access lock). Existing students untouched.
- Mock attempts 10 per session (`MAX_ATTEMPTS`); MCQ quizzes unlimited. Live data change is the idempotent patch `set_attempt_limits`, not yet run.
- Mocks 3 and 4 locked for non-staff (`FREE_SITTINGS = 2`) in lobby and by redirect in `page_renderer.py`.
- Signup email must be a plain address (`before_insert` hook); Terms, Privacy, Refund pages added as a draft.
- Notes and glossary share one CSS typography with semantic colour; lesson text unchanged.
- Read-only check: 13 courses published, self-learning on, none upcoming or paid; mocks reached only through the lobby.
- Needs live rollout with approval: migrate (two patches), worker restart. Backup `20261005_163213` (git `679eab8`).

## 2026-10-07 Pricing, subscription and Stripe (local commits, live on the LMS site)

- Free month, 49 monthly or 99 three-month plans, access lock, `/pricing`, `/billing`, daily reminders (`billing.py`).
- Wise cannot confirm payments for a UK account (docs saved in `docs/vendor/wise/`); Stripe provider added behind settings (`billing_providers/stripe.py`, webhook `billing.stripe_webhook`), manual confirmation kept as fallback. Dodo dropped.
- Stripe sandbox keys stored in Examic Billing Settings only. Stripe docs saved in `docs/vendor/stripe/`.

## 2026-10-08 New-server restore verified

- Target: `/home/ubuntu/frappe-bench`, site `examic.study` on `vps-6bdd605a`.
- Owner approved replacing the target database/files after the restore plan was presented.
- Restored the four `20261008_172510-lms_aimatic_tech-*` files from `/home/ubuntu/lms-backup`.
- Verified rollback database/files/config stored in `/home/ubuntu/restore-rollback-20261008`.
- Preserved target database credentials and `https://examic.study`; source encryption key matches.
- Removed the missing shared-server `aimatic` app registration from restored app metadata,
  without installing SZL code. Ran `bench --site examic.study migrate` successfully.
- Source and restored counts match: 14 courses, 138 chapters, 408 lessons, 175 quizzes,
  3168 questions, 10588 flashcards, 124 enrolments, 83 quiz submissions, 22 users,
  30 File records and 1 subscription. All 48 archived file/link entries match.
- Verification report: `/home/ubuntu/restore-rollback-20261008/verification.json`.
- Site remains in maintenance mode; public launch and learner browser checks are pending.
  No changes were made to the old server.

## 2026-10-08 Maintenance mode disabled

Owner approved taking `examic.study` out of maintenance. Ran site-scoped
`set-maintenance-mode off` and `clear-cache`; config reads maintenance_mode=0.
Local gunicorn on port 8001 and public HTTPS `/sqe` both return HTTP 200.
Authenticated learner flows remain unverified.

## 2026-10-08 Student portal locked to the public website's theme

- Removed the student-facing theme picker. `lms_soft_themes.js` no longer
  reads/writes `localStorage` or offers a choice; it applies one fixed
  `EXAMIC_THEME` tokens object matching `sqe_frappe_theme.css` on every
  `/lms` page load, unconditionally.
- Removed every remaining hardcoded, off-brand hex in
  `lms_student_experience.css` (leftover navy/gold/teal/ivory from an older
  design: MCQ selected-answer highlight, nav arrows, flashcard states, topic
  kicker/intro, pathway card, course cards, flag button). Every colour there
  is now a `var(--aimatic-*, #hex-fallback)` token matching the locked
  palette, including the pre-mount/unscoped rules that used to flash the old
  colours before the learner body class was applied.
- Hid upstream LMS's own light/dark/system theme toggle for students only
  (it was already non-functional there, since `lms_soft_themes.js` forces
  light mode on every render): the desktop user-menu "Toggle Theme" row is
  hidden in `lms_soft_themes.js` by matching its rendered label, scoped to
  `[data-slot="item"]`; the mobile "You" "Colour mode" row and its sheet are
  hidden in pure CSS via `[aria-label="Colour mode"]` /
  `[data-testid="colour-mode-sheet"]`. Both scoped to
  `body.aimatic-lms-student`; staff/Administrator/Instructor/Moderator
  accounts keep a working toggle. Neither touches `apps/lms`.
- Bumped the cache-busting asset versions for `lms_soft_themes.css/js` and
  `lms_student_experience.css` to `v=20261008-themelock1` in
  `page_renderer.py`. Full detail in `skills/lms-learning/launch-and-theme.md`.
- Owner restarted the web worker. Verified live: `/lms/courses` HTML now
  references `v=20261008-themelock1` for all three changed assets; the
  served `lms_soft_themes.js` contains `EXAMIC_THEME`/`hideUpstreamThemeToggle`
  and no longer contains `addPicker`; the served `lms_student_experience.css`
  has zero remaining `#c7a900`/`#8eb580`/`#307f73`/`#10233f`/`#c0392b` hits and
  75 `var(--aimatic-*)` token uses; the served `lms_soft_themes.css` has the
  `[aria-label="Colour mode"]` hide rule and zero remaining picker/`"blue"`
  theme selectors.
  **Still unverified**: this session has no browser/login tool, so the
  interactive logged-in-student walkthrough (MCQ selected-answer highlight,
  nav-arrow hover states, opening the desktop user-menu to confirm "Toggle
  Theme" is gone, opening mobile "You" to confirm "Colour mode" is gone,
  flashcards, mock lobby, login page) has not been done. Treat this as
  code/asset-level verified, visually unverified until a learner session
  confirms it.

## 2026-10-08 Monthly payment starts immediately and unlocks all mocks

- Owner clarified that the 30-day signup free period includes Mock 1 and Mock 2 only.
  A student choosing Monthly should pay £49 at Checkout, start the subscription that
  day, and unlock all mocks. The first charge is not deferred to the end of the free
  period; not subscribing retains the 30-day free access to Mock 1 and Mock 2.
- Monthly Stripe Checkout no longer sets `subscription_data[trial_end]`. The signed
  successful Checkout webhook links the Monthly subscription and grants all mocks
  during the brief interval before `invoice.paid`; the `subscription_create` invoice
  opens one paid month from the checkout date. An unpaid/failed Checkout does not unlock.
- `/billing` now says Monthly starts today and its trial-state button says the exact
  price and that it unlocks all mocks. `/pricing` identifies the two free mocks and
  explains the upfront Monthly and 3-Month charges. The locked mock lobby links to `/billing`.
- The earlier live Checkout failure was caused by missing Live Price IDs. Created and
  verified active GBP 49 recurring and GBP 99 one-time prices in the connected Stripe
  account, and saved them to Examic Billing Settings.
- Restarted web and worker supervisor groups. `py_compile` and `git diff --check` passed;
  all supervisor processes are running, and public `/pricing` and `/billing` return
  HTTP 200 with the new copy.
- Not verified with a real student Checkout: no Checkout session or charge was created.
  The signup account remains in Trial with no Stripe subscription; the student must
  complete Monthly Checkout for the charge and unlock to occur.

## 2026-10-08 Existing student without a subscription could not buy mock access

- Read-only inspection confirmed `frutyfriend@gmail.com` is an enabled Website User with
  no Examic Subscription row. The backend returned `state=full` for the billing page,
  so it said “You have full access” and hid plan choices, while the mock gate correctly
  kept Mocks 3 and 4 locked. `start_checkout` also rejected the account for lacking a row.
- No-row accounts now have a separate `unsubscribed` billing state: existing course
  access and Mock 1/2 remain available, the billing page shows plan choices, and
  Checkout creates a pending subscription row only when a student starts Checkout.
  It does not alter access until a confirmed payment/webhook; non-Website Users cannot
  create student subscriptions through this endpoint.
- Restarted web and worker groups. A fresh billing-state call for the account now returns
  `state=unsubscribed` and the £49 Monthly / £99 3-Month plan choices; `can_open_all_mocks`
  remains false until payment. Public `/billing` returns HTTP 200.
- Not yet verified end to end: the student must reload `/billing`, complete Checkout, and
  receive Stripe's paid webhook. No Checkout session or charge was created here.

## 2026-10-08 Portal sidebar site-link is the Examic mark, not text

Follow-up to the same-day theme-lock entry above. The portal-to-public-site
link in the chapter rail/sidebar read "Examic website", which was redundant
copy given a student is already inside Examic Study. `addSiteLink()` in
`lms_soft_themes.js` now renders only the Examic mark
(`examic-study-mark-uk.svg`, `aria-label="Examic Study home"` on the link,
decorative `alt=""` on the image) linking to `/sqe`; `lms_soft_themes.css`'s
`.aimatic-site-link` rule was restyled from a text link to a small circular
icon button. Bumped `lms_soft_themes.css`/`.js` to `v=20261008-themelock2`
in `page_renderer.py`. Not yet verified live: needs `bench build` and a
worker restart, then a logged-in-student check that the icon renders and
links to `/sqe`.

## 2026-10-08 Shared learner navigation deployed

On branch `student-journey-review-20261008`, added a shared Examic sidebar to
`/learning-dashboard`, `/learning-revision`, and `/learning-mock-exam`, with a
horizontal narrow-screen layout. The mock lobby now links completed attempts
to the revision board. The dashboard script URL was versioned to bypass the
immutable browser cache. No LMS records, payment state, or Frappe core changed.

Deployed with `bench --site examic.study clear-cache` and restarted only
`frappe-bench-web:frappe-bench-frappe-web`; app assets are served from the
`sites/assets/aimaticlearning` symlink, so no app-wide build was needed. Verified
the public CSS and JS return HTTP 200, the guest revision route redirects to
login, API ping returns `pong`, and the web process is RUNNING. A logged-in
student visual review remains pending. Rollback: restore the learner templates,
dashboard script, and new sidebar stylesheet/template to their pre-change
versions, clear the `examic.study` cache, and restart only the Frappe web
process.

## 2026-10-08 Site-link icon repositioned under "Mock Exams" in the LMS sidebar

Follow-up to the two theme-lock entries above; unrelated to the shared
`examic-student-sidebar`/`lms_student_shell.css` work in the entry directly
above — that is a separate static sidebar for `/learning-dashboard`,
`/learning-revision` and `/learning-mock-exam`, which `addSiteLink()` below
never touches (its path check only matches `/lms...`).

Prepending the site-link icon to the top of `.bg-surface-sidebar` /
`.aimatic-lms-chapter-rail` left an empty-looking grey gap above the real nav
rows. `addSiteLink()` in `lms_soft_themes.js` now finds the sidebar's own
"Mock Exams" row by its rendered text (that label comes from a live Frappe
Translation record over the stock "Quizzes" nav item, not from this app's
source, so it cannot be grepped here) and inserts the site link immediately
after it, cloning that row's `className` so it inherits the same padding,
icon size and hover state as every other row instead of a hand-tuned box.
Renders as an icon + "Examic Study website" label, linking to `/sqe`. If no
such row is found (e.g. a layout without the sidebar), the link is skipped
rather than falling back to the old top-of-rail placement.
Bumped `lms_soft_themes.css`/`.js` to `v=20261008-themelock4`.
Not yet verified live: needs `bench build` (done) and a worker restart, then
a logged-in-student check that the icon+label row appears directly under
"Mock Exams" with matching alignment.

### Revision layout refinement

After owner feedback that the page still looked separate and unfinished, the
custom student pages were switched to Frappe's full-width content area. The
navigation now uses a flat full-height rail, the Examic mark and Inter font;
Revision content takes the full portal canvas and uses the locked Examic palette.
The stylesheet URL was versioned to `20261008-student2`. Cleared the site cache
and restarted only the Frappe web process. Logged-in visual review is still
pending because no student browser session was available.
## 2026-10-09 Password-reset branding asset restored

The Examic /update-password page was loading its header logo and favicon
from the retired lms.aimatic.tech domain, producing a broken-image icon.
The correct public assets were already present in aimaticlearning:
 /assets/aimaticlearning/images/examic-study-header-uk.png and
 /assets/aimaticlearning/images/examic-study-mark-uk.svg. Updated the live
Website Settings app_logo and favicon to those local paths, cleared the
site cache, and updated enrollment.py so a future branding configuration does
not restore the retired URLs. Verified the page contains the local paths and
both assets return HTTP 200. No service restart was required.

## 2026-10-13 Public website content handover

**Scope:** public marketing and legal pages, contact form, welcome/reminder email text.

**Finding:** The handover (`Examic_Website_Content_Updated.docx`) states 30 mocks of 90
questions, 5,000+ flashcards, 2,500+ questions, 1,000+ pages, expert validation of all
content, a calendar-month trial, "cancel anytime" and limited mock access. Code and data show
4 mocks (16 sessions of 85 questions, 153 minutes), a 30-day free period with every published
course plus Mock 1 and 2, no review record for every resource, and a Monthly plan charged at
checkout. Those handover lines were not published.

**Correction:** Shared site chrome and the new pages listed in `docs/current-state.md`;
figures come from settings and live data through `lms_learning/public_site.py`. Company name
EXAMIC LTD in the footer and legal pages and in internal payment notes.

**Verification:** Local only (see `tasks/website-content-20261013/task.md`). Live site not yet
deployed or checked.

**Remaining risk:** Legal pages need owner or solicitor review; privacy provider list and
retention are open; checkout cooling-off disclosure is not built.


## 2026-10-13: Home study rhythm background

Owner requested that the grey Prepare → Practice → Perform section match the white public website. Changed only `.sqe-how` background in `sqe_frappe_theme.css` to `#fff`, retaining the cards and section borders. Bumped its shared-template URL to `20261013-how-white` because static assets are served with immutable caching. Cleared the Examic site cache; no migration or service restart. Verified public HTTPS home HTML references the new version and the served CSS contains the white rule; `git diff --check` passed. Browser visual verification remains pending. Rollback: restore the previous CSS rule and version link, then clear site cache.

## 2026-10-14: Live Stripe webhook endpoint missing

**Scope:** Stripe billing on examic.study (Live mode).

**Finding:** A student completed Monthly Checkout and was charged £49, but their
Examic Subscription stayed "Awaiting Payment" with no payment row. Read-only Stripe API
checks found no webhook endpoint on the live account; every event showed
`pending_webhooks = 0`, and `Examic Payment Event` had no rows at all, so no live payment
had ever reached the site. One affected student.

**Correction:** The owner created the live endpoint
`https://www.examic.study/api/method/aimaticlearning.lms_learning.billing.stripe_webhook`
with `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed` and
`customer.subscription.deleted` (some extra events are also selected; the site logs them
as Ignored), and saved its signing secret in Examic Billing Settings. The student was
refunded in full and the Stripe subscription cancelled, so the missed events were not
replayed and no access was granted. No code change.

**Verification:** After the cancel, `customer.subscription.deleted` was stored in
Examic Payment Event as Matched for the student, with no Error Log. The site only logs
events whose signature passes, so delivery and the secret are confirmed. Stripe shows no
pending deliveries.

**Remaining risk:** A live `invoice.paid` has not yet been processed end to end; check
the next real payment shows Matched and opens the paid period. The refunded student's
site row has no `stripe_customer`, so `/billing` hides "Manage card and cancel" for them
until a new Checkout links one.

## 2026-10-15: Equity and Trust Law rebuilt to its six-chapter source

**Finding:** The live course did not match the owner's Word source (`EQUITY AND
TRUSTS.docx`, File `bed22e0354`, six chapters). An unrecorded session on 13 and 14
October had split it into eight chapters and reworded all notes. At 00:19 on 14 October
it also moved the correct answer and explanation of five shared questions one option
along (QTS-2026-01462 to 01466, Chapter 2 Q1 to Q5). Those questions also sit in the
Module Assessment and FLK2 Mocks 2 and 3. The module's recorded source, `Eq nd
trust.docx` (`7e662d8062`), an older eight-section file, was no longer on disk.

**Correction:** The five keys and explanations were restored to the source answers.
`lms_learning/equity_rebuild.py` then rebuilt the course from the source:
- six reused Course Chapters, in source order, with source titles;
- the source notes verbatim, with summary and glossary moved to the Module Assessment
  revision lesson and the embedded MCQs, answers and self-assessment left out;
- 20 source questions per chapter quiz. 113 existing questions were reused with keys
  checked against the source, and 7 missing Chapter 4 questions were created.

Old Chapters 7 and 8 were removed through Content Studio after their cards and question
tags moved to the merged chapters. The retired File row was deleted, and the module now
points to `bed22e0354`. 120 new flashcards (20 per chapter) were written to the owner's
flashcard prompt from the new notes. They are imported as Under Review, and the earlier
published cards stay live until the owner approves the swap.

**Verification:** For every chapter quiz, each question's key and explanation match the
source answer. The course has 20 lessons: 6 times 3, plus 2 in the Module Assessment.
FLK2 Mocks 1 to 3 (85 each) and the 150-question assessment are unchanged. A notes leak
scan found nothing. Every card quote is found verbatim in its chapter notes. A
logged-in learner browser check is still pending.

**Rollback:** `bench --site examic.study execute
aimaticlearning.lms_learning.equity_rebuild.rollback --kwargs '{"confirm":"rollback equity"}'`
restores the snapshot at `sites/examic.study/private/equity_rebuild_snapshot.json`.

**Source wording kept from the site, not the Word file:** two UK spellings, Ch6 Q12
option C, Ch6 Q20 options B and E (the source has half-finished working). The source's
own answers to Ch1 Q12, Ch5 Q3 and Ch5 Q4 are doubtful in law and await owner review.

## 2026-10-24 — Signup messages, header name, sidebar exit, card at signup

**Scope:** `/login` signup form, public site header, `/lms` sidebar, billing.

**Finding:** (1) After signup nothing was shown: `.login-success-banner` and
`.login-error-banner` are `display: none` in Frappe's `login.bundle.scss` and only Frappe's own
`login.js` shows them; our form removed a `hidden` class instead. This also hid "Already
Registered". (2) The header said only "Open my portal" for a logged-in visitor. (3) The `/lms`
sidebar had no way back to the website (no such link in upstream or this app). (4) The free month
did not collect a card, so nothing could be charged afterwards.

**Correction:** `examic_login.css` shows the banners; `examic_signup_form.html` reports the sent
email, and an existing account lands on the login form with its email and a notice
(`www/login.html`); `base.html` shows the name; `lms_student_experience.js` adds the sidebar
link; billing now defers the charge through a Stripe subscription trial (see `lms-billing`).

**Verification:** `unittest` for `test_billing`, `test_stripe_provider`, `test_signup_enrolment`
pass (36 tests). The signup template renders and its script passes `node --check`. Not yet
checked: any browser view, Stripe test mode, or the DocType reload; nothing was deployed.

**Remaining risk:** The 3-Month `cancel_at` behaviour at the term boundary must be proven in
Stripe test mode. Legal pages need owner review. The Stripe charge happens at 00:00 UTC on the
day after the free month, so a student can see "checking your payment" for a few minutes.

## 2026-10-25: Back to Website sidebar navigation

Owner requested a website exit matching Mock exams, deployed on Ubuntu. The existing exit targeted the sidebar footer; it now follows the Mock exams row, copies its wrapper spacing, and uses native sidebar link classes with the label `Back to Website`, an exit icon and href `/`. It handles collapsed labels and avoids duplicate insertion. The shared server-rendered learner sidebar includes the same destination after Mock exams.

Deployment: static public assets are symlinked directly from this checkout; public HTTPS fetched the updated JS byte-for-byte. Cleared only the Examic site cache. No Python reload, migration, billing changes, or service restart: the checkout contains separate undeployed signup/billing work. The running renderer still uses its existing immutable JS URL, so existing browsers require a hard refresh to fetch the updated asset.

Validation: Node syntax check and git diff check passed. Headless Chromium using served live CSS and native sidebar markup confirmed matching 28px row height, 13px label font, insertion after Mock exams, one exit after repeated decoration, collapsed label hidden and `/` destination. Authenticated live sidebar verification remains pending. Rollback: revert this task commit and clear the site cache; hard refresh the browser.

2026-10-25 follow-up: owner requested sentence case, `Back to website`. Updated both sidebar render paths, including the JS title and accessible label. Node syntax and public served-asset checks passed; site cache cleared. Existing browsers still require a hard refresh.

## 2026-10-26: Account name in website header

Owner requested only the account name beside Open my portal. Removed the `Logged in as` prefix from both shared-header variants, retaining the dynamic full name. Cleared the Examic site cache. Both Jinja name spans render Nabeel Ahmed without the prefix; git diff check passed. No service restart. Rollback: revert the template change and clear cache.

## 2026-10-26: Live Stripe webhook and customer portal verified

Owner authorized the four webhook events and customer portal cancellation/card settings. Used the official Stripe API with the existing Live credential loaded from Examic Billing Settings in memory; no secret values were printed or changed. The enabled live Examic webhook already contained checkout.session.completed, invoice.paid, invoice.payment_failed and customer.subscription.deleted, so it was left unchanged (including its other event subscriptions).

No portal configurations existed. Created `bpc_1UUldEPQTqb5hoxzrFxCyRhw`, confirmed active, livemode and is_default, with payment_method_update enabled and subscription_cancel enabled at_period_end, no proration, return URL https://www.examic.study/billing. A fresh GET verified the settings. Rollback for this newly created portal configuration: deactivate it through the Stripe API; no earlier configuration existed. No prices, API keys, webhook secrets, email templates, site restarts, customer subscriptions, charges or refunds were changed. A real student portal click and live payment lifecycle remain unverified.

## 2026-10-26: Website exit remains last

Owner reported Mock coverage appearing after Back to website. Changed the sidebar decorator to place the exit after the final navigation row, excluding itself, instead of immediately after Mock exams. This handles staff-only and asynchronously added entries. Live HTTPS serves the changed script byte-for-byte; Node syntax and diff checks passed. Chromium fixture with native markup/live CSS checks placement after dynamically inserted Mock coverage, idempotence, matching row sizing, and collapsed mode. Existing immutable asset URL still requires browser hard refresh. No restart or backend change. Rollback: revert this JS change.

## 2026-10-26: Mocks 5 to 10 added, reuse allowed

Owner asked for 10 mocks in total with questions allowed to repeat (about 40% estimate). Added `allocate_with_reuse`, `validate_reuse`, `dry_run_reuse`, `live_summary` and `refresh_report_from_live` to `sqe1_hard_mocks.py` (commits e1ef296, d152e15, not pushed) and the reuse rule to `docs/sqe1/MOCK-BUILD.md`. Mocks 1 to 4 were not touched.

Built on `examic.study` by the owner running `apply_mock(5..10)`, then `sync_from_hard_mock_course()` and `refresh_report_from_live()`. Course stays unpublished; no enrolments created (sync reported 0); pricing, billing and access rules unchanged. No backup was taken (not requested).

Verified read-only afterwards: 40 quizzes, every session 85 questions, 340 per mock, 10 mocks in the lobby record (40 sessions) and the public report, 2,415 unique questions over 3,400 slots. Share of each mock already seen earlier: Mock 5 12%, 6 25%, 7 56%, 8 58%, 9 69%, 10 70%; largest overlap with any single earlier mock 27% (Mock 10 with Mock 4). Every mock has ethics items in at least two sessions plus tax and Wales items. Unit tests: 11 OK (`test_sqe1_hard_mocks`).

Remaining risk: criminal questions repeat heavily until more Criminal Law content is reviewed; 8 Easy criminal-law items sit in each of Mocks 5, 6 and 10 against the "Easy only if a heading is empty" rule; the lobby and an exam sitting were not opened as a signed-in student. Rollback: delete the "Mock 5" to "Mock 10" Course Chapters with their 24 LMS Quizzes and Course Lessons, then re-run the two sync functions. Mocks 1 to 4 and their submissions are unaffected.
