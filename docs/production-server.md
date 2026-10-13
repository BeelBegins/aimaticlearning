# Examic Study: production server checklist

`examic.study` and `www.examic.study` will serve production from a separate
server. Until then they return 503 and `lms.aimatic.tech` is the development
site on the shared bench. Nothing below is done yet unless marked.

## Server
- Fresh bench with only `frappe`, `payments`, `lms` and `aimaticlearning`. Do not
  install `aimatic` (SZL ERP).
- `bench get-app` of the private GitHub repo `BeelBegins/aimaticlearning` needs a
  read-only deploy key or fine-grained token on the server. Keep it out of the repo.
- Run migrate once so patches create `User.examic_free_until` and set mock attempt
  limits (`add_user_free_until`, `set_attempt_limits`). Both are idempotent.
- Own workers and scheduler, so a Python change is a restart on this bench only.

## DNS and HTTPS
- A records for `examic.study` and `www.examic.study`; one certificate for both.
- Redirect `www` to the apex or the reverse, not both live. The canonical URL in
  code is `https://examic.study/sqe`.
- `site_config` host name and `host_name` must be `https://examic.study`.

## Email
- Outgoing mail is `hello@examic.study` through Zoho. Confirm the live Zoho
  account and app password before enabling outgoing mail. Decide whether production
  sends from an `examic.study` address. If so add SPF, DKIM and DMARC for that
  domain and update the Email Account.
- Send a test signup and check the welcome email lands in an inbox, not spam.
- The SMTP app password lives in a site-secrets file, never in the repo. It was
  shared in chat once: rotate it for production.

## Site config
- `openrouter_api_key` in site config for Study Buddy when Examic Study Settings has no key (not in code).
- Signup enabled, role `LMS Student`, home page `sqe`.
- Terms, Privacy and Refund pages (`/terms`, `/privacy`, `/refund-policy`) are a
  plain draft: the owner or a solicitor must review them before launch.

## Data
- Courses, lessons, quizzes and mock exam data move by restoring a database
  backup of `lms.aimatic.tech` plus its `public/files`, not by re-importing.
- After restore: delete the probe users created from SQL strings on 28 Sep.
- Existing students are not backfilled; only new signups are enrolled.

## Backups and restore
- Nightly database backup with off-server copy. Restore once into a scratch
  bench and open a course, a mock lobby and a quiz to prove it works.

## Launch checks
- Throwaway signup: 13 courses visible, one welcome email with the end date,
  mocks 1 and 2 open, 3 and 4 locked, `/lms/quiz/mock-3-*` redirects to the lobby.
- Payments and enforcement of `examic_free_until` are not built: after the free
  period nothing locks access. Decide before the period ends.
