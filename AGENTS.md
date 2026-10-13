# Examic Study (aimaticlearning)

This repository is the Examic Study product. The live student URL is
`https://www.examic.study/`, served by the `examic.study` site on this bench.
`lms.aimatic.tech` is a retired server domain. Use the Frappe site name
`examic.study` in bench commands and `https://www.examic.study/` for student
links.

Identify this product, then load only `lms-learning` (and `lms-course-upload`
for Word import). Read `docs/current-state.md` for this site only.

## Canonical LMS agent guidance

All reusable LMS instructions, quality standards, findings, and operating
records belong in this repository. Do not treat a personal agent memory,
global skill folder, or another checkout as the source of truth.

- `AGENTS.md` is the shared routing and safety baseline.
- `skills/` contains reusable LMS workflows for every supported agent.
- `docs/lms-agent-guidance.md` maps the active guidance and client adapters.
- `docs/lms-findings-and-fixes.md` records verified findings and completed
  fixes. Update it, and refresh affected facts in `docs/current-state.md`,
  after verified LMS work.
- Dated handoffs and reports are historical evidence, not current facts,
  unless re-verified against code and the LMS site.

## Authority

1. current local code and uncommitted diff;
2. verified read-only runtime on the `examic.study` site;
3. rules here, facts in `docs/`, procedures in `skills/`.

## Code

Owned features live in `aimaticlearning/lms_learning/`. Never modify
`apps/lms`, Frappe, ERPNext, or HRMS core. Install this app only on the Examic
Study site.

GitHub: `BeelBegins/aimaticlearning`, branch `main`. The Frappe app name stays
`aimaticlearning` so `bench get-app` matches the Python package.

## Safety

This is the Examic production bench. Verify site role, current configuration,
and rollback path before any live mutation, import, migration, deployment, or
impactful restart. Do not take a backup unless asked.

Keep Word sources private. A self-service signup is enrolled in every published
subject course by `complete_student_signup`; staff-invited and existing students
are never auto-enrolled or backfilled without approval. Do not put credentials
in code, guidance, or prompts.

## Design and copy: no AI-template decoration

Every element must carry information or an action. Do not add:

- decorative bars, dashes or dots before headings and kickers (`::before`
  lines), glowing pulse dots, gradient blobs or orbs;
- em dashes or double hyphens in UI copy; use a comma, a colon or a new sentence;
- filler taglines, emoji bullets, or stat chips with numbers not read from data;
- tiny uppercase letter-spaced labels as a default heading style.

Reuse the dashboard tokens (`lms_student_dashboard.css`) instead of inventing a
new look. Use real course, exam and learner data only. A reviewer rejects a page
that looks generated.

## Examic site apps

The Examic site uses frappe, payments, lms, and this app. Study Buddy reads
the OpenRouter key from Examic Study Settings, then site config.

## Skills

| Task | Skill |
|---|---|
| Courses, notes, MCQs, flashcards, revision, learner UX | `lms-learning` |
| Word import / empty-lesson fill | `lms-course-upload` |
| MCQ or mock quality, feedback, mapping, and learner display | `lms-mcq-quality` |
| Mock exam sitting UI (Pearson style, review grid, timer, calculator) | `lms-exam-mode` |
| Pricing, free month, payments, Stripe/Wise, access lock | `lms-billing` |
| Site, backup, Caddy, workers, restore | `bench-ops` |
| New production server | `docs/production-server.md` |

Keep `lms-billing` and `docs/current-state.md` current when pricing or payment facts change.

Read `docs/priorities.md` before choosing work. Track resumable work in
`tasks/<id>/task.md` from `tasks/template.md`; run `scripts/audit_guidance.py`
after guidance edits.

**Commit** when a task completes. Push and deploy stay separately approved.
