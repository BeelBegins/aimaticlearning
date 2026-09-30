# Examic Study (aimaticlearning)

This repository is the Examic Study product. Sites: `lms.aimatic.tech`,
`examic.study`, `www.examic.study`. It is not SZL retail. Do not load POS,
FBR, purchase, Foodpanda, or other SZL skills.

Identify this product, then load only `lms-learning` (and `lms-course-upload`
for Word import). Read `docs/current-state.md` for this site only.

## Canonical LMS agent guidance

All reusable LMS instructions, quality standards, findings, and operating
records belong in this repository. Do not treat a personal agent memory,
global skill folder, or another Aimatic/SZL checkout as the source of truth.

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
2. verified read-only runtime on `lms.aimatic.tech`;
3. rules here, facts in `docs/`, procedures in `skills/`.

## Code

Owned features live in `aimaticlearning/lms_learning/`. Never modify
`apps/lms`, Frappe, ERPNext, or HRMS core. Do not install this app on `szl`,
`siezal`, or `hsm`.

GitHub: `BeelBegins/aimaticlearning`, branch `main`. The Frappe app name stays
`aimaticlearning` so `bench get-app` matches the Python package.

## Safety

Until this site leaves the shared bench, web/queue restarts can still hit live
`szl`. Read-only diagnosis is allowed. Any live mutation, import, migrate,
deploy, or impactful restart needs explicit approval, a current verified LMS
backup, checks, and a rollback path.

Keep Word sources private. Do not auto-enrol students. Do not put credentials
in code, guidance, or prompts.

## Apps on a new server

Install frappe, payments, lms, and this app. Do not install `aimatic` (SZL ERP).
Study Buddy reads `openrouter_api_key` from site config. This shared bench may
still have `aimatic` installed until the site moves; that leftover is not a
code dependency.

## Skills

| Task | Skill |
|---|---|
| Courses, notes, MCQs, flashcards, revision, learner UX | `lms-learning` |
| Word import / empty-lesson fill | `lms-course-upload` |
| MCQ or mock quality, feedback, mapping, and learner display | `examic-lms-mcq-quality` |
| Site, backup, Caddy, workers, restore | shared bench `bench-ops` |

Prefer this folder as the Cursor workspace for LMS work.

**Commit** when a task completes. Push and deploy stay separately approved.
