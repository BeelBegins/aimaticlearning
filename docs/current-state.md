# Examic Study — current state

Last updated: 2026-09-13. Verify read-only before any site mutation.

## Product

| | |
|---|---|
| Brand | Examic Study |
| Site | `lms.aimatic.tech` |
| Public hosts | `examic.study`, `www.examic.study` (Caddy aliases; URL stays examic.study) |
| Apps | frappe, payments, lms, aimatic, aimaticlearning |
| Code | this repo, branch `main` |
| GitHub | https://github.com/BeelBegins/aimaticlearning |

This site still runs on the shared `/home/nabeel/frappe-bench` workers with live
SZL (`szl`). There is no LMS staging site. A new server is planned; it is not
ready.

## Hosting (until the move)

Caddy site block `lms.aimatic.tech, examic.study, www.examic.study` → gunicorn
`:8000` with `X-Frappe-Site-Name lms.aimatic.tech`. Let’s Encrypt on all three
hosts. Source: `/home/nabeel/caddy/Caddyfile`.

`host_name` in site config is still `https://lms.aimatic.tech`.

## Coupling to keep in mind

`required_apps` is `lms` only. Study Buddy no longer imports the SZL `aimatic`
app. This shared bench still has `aimatic` installed on the LMS site; leave it
until the server move rather than uninstalling here. A new LMS-only bench
should not install it.

Do not auto-enrol students on signup.

## Unpublished on `/sqe`

`dispute-resolution`, `legal-services`, and `criminal-law` are unpublished
pending academic review (`LMS Course.published = 0`). Re-publish only after
that review.

Operational diary (incidents, backups, content publishes) is
`docs/lms-operational-log.md` in this repo — migrated 2026-09-30 from the
shared bench file, which now only carries a routing pointer to this repo.

**SQE1 hard mocks (2026-09-30):** Exam product `Learning Mock Exam` `sqe1-hard-mocks`
holds four January 2027 sittings (16 timed 85-question sessions, 1360 unique
reviewed 5-option items; Mock 4 added 2026-09-30 without touching Mocks 1–3).
Learners use `/learning-mock-exam`; Start enrols on the exam and opens
`/lms/quiz/<quiz>?fromLesson=1`. LMS Course `sqe1-hard-mocks` is unpublished
(`published = 0`, `disable_self_learning = 1`) and is only the ACL parent for
`can_access_quiz`. Hidden from student catalogues via `exam_surface`. Coverage
is staff-only on `/learning-mock-report`, regenerated 2026-09-30 to include
Mock 4 (`docs/sqe1/HARD-MOCKS-REPORT.md`, the public JSON, and the in-course
notes lesson all cover Mocks 1–4 now, 1360 unique questions, no duplicates).

**Post-submission feedback PDF (added 2026-09-30):** New module
`aimaticlearning/lms_learning/mock_feedback.py` + whitelisted endpoints
`api.get_mock_feedback`/`api.download_mock_feedback_pdf`. Released immediately
per student after their own submission (their explicit choice over gating by
cohort/retirement). Covers score/percentage/pass-fail, per-subject-area
breakdown, strengths/weaknesses by `concept` tag, and the full answer key with
explanations/source references — deliberately excludes timing/pace (no
start/answer timestamp field exists anywhere in `LMS Quiz Submission`/`LMS
Quiz Result`; would have to be invented). `LMS Quiz.show_answers` stays `0`
(exam itself stays closed-book); this is a separate download action. Wired
into `/learning-mock-exam` (`www/learning_mock_exam.html`) as a "Download
feedback (PDF)" link per session once the learner has an attempt, sourced from
`exam_product.student_lobby()`'s per-quiz latest-submission lookup. Permission-
tested live (owner allowed, other learner denied, staff allowed) and PDF
render verified against a real (partial) submission.

**Lobby/exam-record drift (found and fixed 2026-09-30):** `/learning-mock-exam`
reads `Learning Mock Exam.sessions`, a separate synced copy of the course
outline — not live `Course Chapter` data. It was stale before this session's
work: missing Mock 1's FLK1 sessions entirely (pre-existing, unrelated to the
Mock 4 add) and, until `sync_from_hard_mock_course()` was re-run, missing Mock
4 too. That function is idempotent and safe to re-run after any future
sitting-count change — it does not auto-enrol anyone not already enrolled in
the underlying course.

**Known state despite "unpublished/staff-only" (verified 2026-09-30):** 6 real
`LMS Quiz Submission` rows exist against Mocks 1–3, including two non-staff
learner accounts, not just admin QA — the catalogue-hiding via `exam_surface`
did not fully block access. Any future rebuild of this course must exclude
already-live question names (see `apply_mock()`) rather than recomputing all
sittings from scratch, or it will silently desync already-graded submissions
from the questions they were scored against.

**Criminal Law bank (verified 2026-09-30, supersedes the 2026-09-17/22 notes
below):** A genuine `criminal-law` course now exists with 117 structurally
valid (5-option, single-key) questions, added 2026-09-24/25 — the old "Criminal
Law has no 5-option reviewed items" claim is stale. Of those, only 20 are
human-reviewed (`ai_generated=0`); the other 97 went through the LLM
`content_generation.py` pipeline and are correctly excluded per the
ai_generated=1 eligibility rule pending academic review. `sqe1_hard_mocks.py`
now sources Criminal Liability from the genuine `criminal-law` pool first,
falling back to `criminal-litigation` as a proxy only where the reviewed bank
runs short (still the case: combined reviewed criminal supply is 240 items,
enough for 4 sittings' combined Criminal Liability + Criminal Law and Practice
demand of 224, not a 5th sitting's 280). A 5th sitting needs roughly 40 more
reviewed Criminal Law items — either fresh authoring or academic review
promoting some of the 97 AI-drafted items — not a script change. Also note:
DR/Legal Services/Legal System, previously reported "tight" for even 3
sittings (75/80/80 eligible), have grown substantially since 09-17 (362/160/220
eligible) and are no longer a blocker at 4 or 5 sittings.

**AI-drafted MCQs live in published courses (found and partly fixed
2026-09-30):** Auditing the Criminal Law AI-content gap above surfaced a wider
issue: `public-law`, `legal-services`, and `business-law-practice-blp` also
had `ai_generated=1` chapter-quiz MCQs from an earlier (2026-09-07) batch.
`public-law` and `criminal-law` were live in **published** courses — 241
never-reviewed AI items reachable by real students, mixed in with reviewed
content with no visible distinction. Root cause of the exposure: all 5 FLK1/
FLK2 subject courses (including the 3 explicitly gated `published=0` after the
2026-09-10 incident, see below) got set back to `published=1` in a single bulk
write at 2026-09-30 13:00:25 — no git commit, no Version record, timing
strongly tied to an unlogged `bench execute` fix for a real learner's course
access right before it. **Public Law resolved**: found a genuine, complete
source file, `PL MCQs.docx` (private files, uploaded 2026-09-24) — 140
scenario-based questions across 7 chapters with real answers/explanations,
already fully imported and correctly flagged `ai_generated=0`. The 144 AI
items were separate, generated 17 days before that source existed, added
nothing once it did, and lived in 19 quizzes disconnected from the live course
outline (no `Course Chapter`/`Course Lesson` linkage, zero submissions).
Deleted entirely — the 144 `LMS Question`/`Learning Question Meta` rows and
the 19 orphaned quizzes. Backup:
`private/files/lms_learning_exports/public-law-ai-content-removed-20260930.json`
(full doc dumps, not just names). Verified after: `public-law` bank is
220/220 non-AI; its 7 chapter quizzes (20/20 each) and module assessment
(140/140) untouched. **Not yet checked**: whether Legal Services and BLP have
similar real source files that would let their orphaned 65/40 AI items
(currently unlinked to any quiz, so not live-exposed) be deleted the same way.
No decision yet on re-gating `dispute-resolution`/`legal-services`/
`criminal-law` back to `published=0` pending review — doing so may re-break
whatever learner access problem the 13:00:25 write was fixing; left published
per explicit instruction. Expires when: Legal Services/BLP are checked, or the
publish/review-gate question is resolved.

Backup `20260922_134154-lms_aimatic_tech-*` (pre-dates the Mock 4 add; no new
backup was taken for the Mock 4 build per "don't back up LMS unless asked").
Rollback for Mock 4 specifically: delete `Course Chapter` "Mock 4" and its 4
linked `LMS Quiz`/`Course Lesson` records; Mocks 1–3 and their submissions are
untouched by that rollback. Expires when: a 5th sitting is added, the criminal
bank changes materially, or the staff coverage report is regenerated.
