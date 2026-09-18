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

Operational diary for this shared bench (incidents, backups, content publishes)
stays in the bench file `docs/reference/current-state.md` LMS section until the
site moves.

**SQE1 hard mocks (2026-09-17):** Published course `sqe1-hard-mocks` holds three
January 2027 sittings (12 timed 85-question sessions, 1020 unique reviewed
5-option items). Not listed on `/sqe`. Learners use `/learning-mock-exam`;
course overview redirects there. `/learn/1-1` is Mock 1 Session 1. Coverage
is staff-only on `/learning-mock-report`. Criminal Liability is a Criminal
Litigation proxy. Backup `20260918_062050-lms_aimatic_tech-*`. Rollback:
restore that backup. Expires when: the course is unpublished, rebuilt, or
removed.
