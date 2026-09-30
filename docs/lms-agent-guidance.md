# Examic LMS agent guidance map

This `aimaticlearning` repository is the single source of truth for Examic
Study LMS agent work. It is separate from Aimatic/SZL retail. Keep reusable
guidance here; do not store LMS-only procedures as personal agent memory.

## Use this order

1. Current code and a verified read-only LMS runtime check.
2. `AGENTS.md` for product routing, ownership, and safety.
3. The relevant workflow in `skills/`.
4. `docs/current-state.md` and current source records for facts.
5. Dated handoffs/reports only as historical evidence.

## Shared skills

| Need | Source |
|---|---|
| Course, chapter, learner UX, analytics, Study Buddy | `skills/lms-learning/SKILL.md` |
| Private Word source import and lesson coverage | `skills/lms-course-upload/SKILL.md` |
| Chapter/mock MCQ data, explanations, mapping, and UI quality | `skills/lms-mcq-quality/SKILL.md` |
| Import commands and rollback requirements | `skills/lms-course-upload/pipeline.md` |

## Agent adapters

| Agent | Repository entry point | Shared skill target |
|---|---|---|
| Codex | `AGENTS.md` | `.codex/skills` -> `skills/` |
| Claude Code | `CLAUDE.md` -> `AGENTS.md` | `.claude/skills` -> `skills/` |
| Cursor | `.cursor/rules/shared-project.mdc` -> `AGENTS.md` | `.cursor/skills/*` -> `skills/*`; `.agents/skills` -> `skills/` |

Every adapter must resolve the same `SKILL.md` files. Add a new LMS skill in
`skills/<skill-name>/` first, then add any needed adapter link. Do not create a
second copy for one client.

## Documentation roles

| Role | Location |
|---|---|
| Current operational facts | `docs/current-state.md` |
| Architecture | `docs/architecture.md` |
| SQE1 mock requirements and source register | `docs/sqe1/` |
| Verified findings and corrections | `docs/lms-findings-and-fixes.md` |
| Dated import, coverage, and handoff evidence | `aimaticlearning/lms_learning/*REPORT.md`, `*HANDOFF.md`, `IMPLEMENTATION.md` |

When a live change is verified, add a concise evidence record and update any
affected current-state fact. Never silently promote a historic report into a
current operational claim.
