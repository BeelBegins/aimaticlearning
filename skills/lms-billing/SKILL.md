---
name: lms-billing
description: Use for Examic Study pricing, the free month, paid plans, access locking, payment providers (Stripe cards, manual Wise bank transfer), Examic Billing Settings, the /pricing and /billing pages, payment emails and reminders. Not for course content or mock sitting UI.
---

# LMS billing and access

Read `wise.md` or `stripe.md` here before touching a provider. Provider research and
fees: `docs/payment-providers.md`. Resumable record: `tasks/pricing-subscription-20261007/task.md`.
Update this skill and `docs/current-state.md` whenever prices, plans, access rules or
payment facts change.

## Final pricing (owner, 2026-10-07)

- Month 1 free, no payment to start. Free month = all courses and Mock 1 and Mock 2.
- Monthly: then GBP 49 per month, renews each month.
- 3-Month: then GBP 99 paid once for months 2 to 4 (33 a month), no auto renewal.
- Paid plans: all mocks, full resources, detailed analytics. Prices, trial days (30),
  free mock count (2) and reminder days (3) are editable in Desk, never hard-coded
  (defaults live in `billing.py` only as fallbacks).

## Who is affected

Only NEW signups get an `Examic Subscription` (created by `complete_student_signup`).
Accounts without a row (the 28 existing students) are never locked; Mock 3 and 4 stay
locked for them until they pay. Staff roles see everything.

## Access states (`billing.access_state`)

| State | Who | Access |
|---|---|---|
| staff | staff roles | everything |
| full | no subscription row | all courses, Mock 1 and 2 |
| trial | free month | all courses, Mock 1 and 2 |
| paid | `paid_until` today or later | everything |
| locked | free month over, unpaid | only `/billing` and public pages |

Lock is server side: `billing.enforce_access` is a `before_request` hook (page paths
redirect to `/billing`, app APIs answer 402). `is_locked_path` holds the allow-list.
Mock locks: `exam_product.is_sitting_locked` and `page_renderer`.

## Code map

- `lms_learning/billing.py`: `settings`, `provider`, `access_state`, `status_for`,
  `extend_paid_until`, `apply_payment` (the ONE place that opens a paid period),
  `confirm_payment` (staff), `start_checkout`, `open_portal`, `request_payment`,
  `process_stripe_event`, `stripe_webhook`, `daily_billing_job`.
- `lms_learning/billing_providers/`: `manual.py`, `stripe.py` (signature check,
  `interpret_event`, Checkout and portal calls). New provider = new module ending in `apply_payment`.
- DocTypes: `Examic Billing Settings` (single; all configuration, secrets as Password),
  `Examic Subscription` (one per student), `Examic Payment` (child log),
  `Examic Payment Event` (webhook idempotency and "Needs review").
- Pages: `www/pricing`, `www/billing`; copy in `www/sqe.html`, `terms`, `refund-policy`
  (prices come from settings through `pricing.py` and `terms.py`).
- Emails (templates created by `enrollment.create_email_templates`): Payment Reminder,
  Payment Receipt, Payment Problem, Welcome.

## Staff and rollout

- Manual provider: student sends the bank transfer with reference `EXM-xxxxxx`, presses
  "I have paid"; staff open the subscription in Desk and call Confirm payment.
- Switch provider in Examic Billing Settings; `Manual` always works as the fallback.
- Bench rules: apply DocType changes with `bench --site lms.aimatic.tech reload-doc "LMS Learning" doctype <name>`
  (never `migrate`: the leftover `aimatic` app fails there); restart with
  `sudo -n supervisorctl restart frappe-bench-web: frappe-bench-workers:`.
- Test without waiting: set `trial_ends_on` in the past for a throwaway student; unit tests:
  `../../env/bin/python -m unittest aimaticlearning.lms_learning.test_billing aimaticlearning.lms_learning.test_stripe_provider`.

## Safety

No keys, tokens, bank numbers or webhook secrets in code, git, tasks or logs; they live in
Examic Billing Settings. Never mix live and test keys. Terms, Privacy and Refund pages
are drafts needing owner or legal review. Existing students are never changed without approval.
