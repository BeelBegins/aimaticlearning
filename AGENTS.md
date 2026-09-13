# Examic Study (aimaticlearning)

This repository is the Examic Study product. Sites: `lms.aimatic.tech`,
`examic.study`, `www.examic.study`. It is not SZL retail. Do not load POS,
FBR, purchase, Foodpanda, or other SZL skills.

Identify this product, then load only `lms-learning` (and `lms-course-upload`
for Word import). Read `docs/current-state.md` for this site only.

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

## Remaining coupling

`required_apps` still includes `aimatic` because Study Buddy imports
`aimatic.ai.nemotron_client`. Leave that until it is vendored here. A new LMS
server should not install the SZL ERP app.

## Skills

| Task | Skill |
|---|---|
| Courses, notes, MCQs, flashcards, revision, learner UX | `lms-learning` |
| Word import / empty-lesson fill | `lms-course-upload` |
| Site, backup, Caddy, workers, restore | shared bench `bench-ops` |

Prefer this folder as the Cursor workspace for LMS work.

**Commit** when a task completes. Push and deploy stay separately approved.
