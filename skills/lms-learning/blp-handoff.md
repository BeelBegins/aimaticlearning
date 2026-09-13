# LMS BLP handoff (lms.aimatic.tech)

**Updated:** 2026-08-30  
**Primary skill:** `lms-learning`  
**Site:** `lms.aimatic.tech` (apps: frappe, payments, lms, aimatic, aimaticlearning)

## Product goal

UK SQE1 prep platform (Imran Sb model): UK solicitor owns content/credibility; Pakistan tech owns LMS, MCQs, analytics, AI; separate UK EdTech brand target. Positioning: Kinnu-basic / QLTS-premium → all-in-one portal at sharper price. Pilot 50–100 candidates → July 2027 SQE1 commercial launch → ~1000 subscribers.

**Do not auto-enroll** students on signup. Solicitor/admin enrolls or invites.

## URLs

| URL | Purpose |
|-----|---------|
| https://lms.aimatic.tech/ | SQE marketing landing (`www/sqe.html`, home_page=`sqe`) |
| https://lms.aimatic.tech/sqe | Same landing |
| https://lms.aimatic.tech/login | Signup `#signup`, login |
| https://lms.aimatic.tech/lms | LMS SPA (post-login default_app=`lms`) |
| https://examic.study/ | Same LMS site (Caddy alias, URL stays examic.study) |
| https://www.examic.study/ | Same LMS site (Caddy alias) |
| https://lms.aimatic.tech/lms/courses/business-law-practice-blp | BLP course |
| https://lms.aimatic.tech/learning-revision | Student revision / weak-area board |

## Live data snapshot

| Item | Value |
|------|--------|
| Course | `business-law-practice-blp` — Business Law & Practice (BLP) |
| Learning Module Config | `LMOD-00017` |
| Chapters | 22 (tax/VAT from docx headings; idx 1–22 fixed) |
| Chapter MCQ target | 20/chapter (config) |
| Parsed/imported MCQs | ~180 from docx (company-law sections); spread across chapters |
| Module assessment | 150 MCQs on quiz `BLP Module Assessment (150 MCQs)` |
| Published flashcards | ~26 (seed from notes; target 200) |
| LMS enrollments | low (test users); `frutyfriend@gmail.com` was manually enrolled |

## Email (configured)

- **Email Account:** `Aimatic Zoho` on LMS + SZL sites
- **SMTP:** `hello@aimatic.tech` via `smtp.zoho.com:587` TLS
- **Secret file:** `~/.local/share/aimatic/site-secrets/lms.aimatic.tech.zoho-app-password` (do not commit; password was shared in chat once — consider rotate)
- **Admin password:** `~/.local/share/aimatic/site-secrets/lms.aimatic.tech.admin-password`
- Templates: `Aimatic LMS Student Welcome`, `Aimatic LMS Course Enrollment`

## Code ownership

All LMS product code: `apps/aimaticlearning/aimaticlearning/lms_learning/` — **never modify** `apps/lms`, frappe, erpnext core.

### Key modules

| File | Role |
|------|------|
| `import_pipeline.py` | Docx → course/chapters/profiles |
| `outline_sync.py` | Chapter/lesson links; notes lesson population |
| `mcq_import.py` | Parse MCQs from docx → LMS Question + chapter quizzes |
| `course_presentation.py` | **Chapter hub UI** — one lesson/chapter, Kinnu-style tabs; `repair_course_presentation()` |
| `lesson_macros.py` | Renders inline HTML hub (notes/MCQ/flashcards) into lesson `body` |
| `templates/lms_learning/chapter_hub.html` | Hub markup + embedded CSS (Bricolage + Source Serif) |
| `enrollment.py` | Signup config, Zoho helper, invite APIs, **no auto-enroll** |
| `zoho_email.py` | Shared Zoho SMTP setup (any site) |
| `api.py` | Protected notes, flashcards, learning map, repair API |
| `content_generation.py` | AI export bundle, MCQ/flashcard import, module assessment blueprint |
| `protected_notes.py` + `www/learning_notes.html` | Legacy full-page notes viewer (prefer hub tabs) |
| `www/sqe.html` | Public SQE marketing page |
| `IMPLEMENTATION.md` | Runbook |

### Hooks (`apps/aimaticlearning/aimaticlearning/hooks.py`)

- `website_route_rules`: `/learning-notes/<profile>`, `/learning-flashcards`
- `lms_markdown_macro_renderers`: `AimaticChapterHub` (registered but **LMS lesson body does not run macros** — hub uses pre-rendered HTML in `body`)
- User `after_insert`: welcome email; LMS Enrollment `after_insert`: enrollment email
- LMS Student `home_page`=`/lms`; Website `home_page`=`sqe`

## Chapter UX (current design)

- **One `Course Lesson` per chapter** (not 3 separate lessons).
- Lesson `body` = collapsed HTML from `chapter_hub_renderer()` (not macro text).
- **CSS-only tabs** inside lesson: Study notes | Practice MCQs | Flashcards.
- Notes: chunked `<details>` sections (3 paragraphs each), serif body, soft mint UI.
- MCQs: `quiz_renderer()` HTML embedded in MCQ tab (rendered at repair time).
- Flashcards: `<details>` flip cards in Flashcards tab.
- Chapter 22 may also have **Module Assessment** as second lesson.

**Critical:** LMS `LessonContent.vue` splits `body` by `\n\n` and does not process `{{ macros }}`. Always store **single-line or no-double-newline HTML** via `repair_course_presentation()`.

## Known content issues

1. **Introduction profile** had ~750KB wrong blob (company law dumped into intro). **Fixed** to short welcome; full company law content is NOT in tax chapter titles.
2. **Docx MCQs** (~180) are **company law** sections; course chapters are **tax/VAT** headings — MCQs were spread by import, not topic-aligned.
3. **Full 20/chapter** needs ~260+ more MCQs (AI or new source).
4. **200 flashcards** target — only ~26 published seed cards.

## Commands

```bash
cd /home/nabeel/frappe-bench

# Repair chapter order + hub HTML + course description
bench --site lms.aimatic.tech execute aimaticlearning.lms_learning.course_presentation.repair_course_presentation --args '["business-law-practice-blp"]'

# Re-import MCQs from docx
bench --site lms.aimatic.tech execute aimaticlearning.lms_learning.mcq_import.import_mcqs_for_module --args '["LMOD-00017"]'

# Student access + email templates + home routes
bench --site lms.aimatic.tech execute aimaticlearning.lms_learning.enrollment.configure_lms_student_access

# Zoho email (needs secret file or password kwarg)
bench --site lms.aimatic.tech execute aimaticlearning.zoho_email.configure_zoho_outgoing_email

# Module assessment blueprint (150)
bench --site lms.aimatic.tech execute aimaticlearning.lms_learning.content_generation.build_module_assessment_blueprint --kwargs '{"learning_module": "LMOD-00017"}'

bench --site lms.aimatic.tech clear-cache
```

Desk API: `aimaticlearning.lms_learning.api.repair_blp_presentation` (System Manager).

## Signup / login flow

- Signup enabled; default role `LMS Student`; **no auto BLP enrollment**.
- Login → `default_app=lms` → `/lms`.
- Enroll via Desk, `invite_student`, or self-enroll on course if allowed.
- Test user: `frutyfriend@gmail.com` (Nabeel Ahmed) — was manually enrolled for QA.

## Next work (priority)

1. **Flashcards:** AI batch → review → import to 200 published (`import_generated_flashcard_json`).
2. **MCQs:** Generate tax-chapter-aligned MCQs (20/ch) or restructure course to match docx company-law MCQs.
3. **Hub UI polish:** User wants more Kinnu-like polish; may need LMS SPA-safe assets if inline `<style>` stripped by sanitizer — verify in browser.
4. **Learning map / analytics:** Wire quiz attempts to `Learning Attempt Detail`; Desk page exists.
5. **UK brand:** Replace “Aimatic Learning” on public surfaces when brand name finalized.
6. **Rotate Zoho app password** (was exposed in chat).

## Safety

- `lms.aimatic.tech` is a separate learning product — do not load SZL skills.
- Live gate for site mutations: backup, approval, rollback. This bench shares
  workers with live `szl`.
- Do not commit secrets. SZL also has Zoho configured — same hello@ account;
  do not mix site operations.

## Git state (frappe-bench guidance repo)

Uncommitted aimatic changes on `master` / guidance on `main` — check `git status` in `apps/aimatic` and `frappe-bench` before commits.

## Transcript

Full agent transcript: `agent-transcripts/299702c7-a3c8-4e09-9b54-1c6457b9d92a/299702c7-a3c8-4e09-9b54-1c6457b9d92a.jsonl`
