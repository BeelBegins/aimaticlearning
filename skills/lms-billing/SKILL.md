---
name: lms-billing
description: Use for Examic Study pricing, the free month, paid plans, access locking, Stripe card payments, Examic Billing Settings, the /pricing and /billing pages, payment emails and reminders. Not for course content or mock sitting UI.
---

# LMS billing and access

Stripe is the only student-facing payment method. Wise is documented only as a
possible payout destination, not a checkout option. Read `stripe.md` before changing
Stripe. Provider research and fees: `docs/payment-providers.md`. Resumable record:
`tasks/pricing-subscription-20261007/task.md`.
Update this skill and `docs/current-state.md` whenever prices, plans, access rules or
payment facts change.

## Final pricing (owner, 2026-10-07)

- Signup includes a free 30-day period with all courses and Mock 1 and 2. Students who do not subscribe are not charged during it.
- A student who completes Monthly Stripe Checkout starts the Monthly subscription immediately, is charged £49 at checkout, and unlocks all mocks. The monthly renewal date is one month after checkout; choosing the paid plan ends the free-only mock limit.
- The 3-Month Stripe plan is a one-time £99 payment. A confirmed payment unlocks all mocks immediately; the paid period follows the free month.
- Monthly: GBP 49 at checkout and each month after, starting on the checkout date.
- 3-Month: then GBP 99 paid once for months 2 to 4 (33 a month), no auto renewal.
- Paid plans: all mocks, full resources, detailed analytics. Prices, trial days (30),
  free mock count (2) and reminder days (3) are editable in Desk, never hard-coded
  (defaults live in `billing.py` only as fallbacks).

## Who is affected

Only NEW signups get an `Examic Subscription` (created by `complete_student_signup`).
Accounts without a row (the existing students) keep their courses and Mock 1 and 2;
Mock 3 and 4 stay locked until payment. They see paid plans on `/billing`; their
subscription row is created when they start Checkout, without changing current access.
Staff roles see everything.

## Access states (`billing.access_state`)

| State | Who | Access |
|---|---|---|
| staff | staff roles | everything |
| unsubscribed | no subscription row, or checkout started with no free period | courses, Mock 1 and 2; paid plans shown |
| trial | free month | all courses, Mock 1 and 2 |
| paid | `paid_until` today or later | everything |
| locked | free month over, unpaid | only `/billing` and public pages |

The `trial` row assumes the student has not completed Monthly Checkout. A paid Monthly
Checkout is linked by Stripe's successful `checkout.session.completed` webhook and
unlocks all mocks immediately. Its first paid invoice starts the paid period on the
checkout date. The `/billing` response exposes `monthly_subscription_active` during
the short interval before the invoice webhook is processed.

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
- Pages: `www/pricing`, `www/billing`; offer copy also in `www/sqe.html`, `introductory-offer`,
  `terms`, `refund-policy`, `how-it-works`. Every price, trial length and free mock count on
  those pages comes from settings through `public_site.offer_facts()`; never type £49/£99/30 into copy.
- Emails (templates created by `enrollment.create_email_templates`): Payment Reminder,
  Payment Receipt, Payment Problem, Welcome. Template wording changes reach the site only
  when that function is run again on the site (a live mutation: needs approval).

## Staff and rollout

- Student checkout uses Stripe Checkout. Do not restore manual transfer or Wise
  payment instructions to `/pricing` or `/billing`.
- The legacy manual provider remains in backend code; it is not a customer-facing
  fallback. If Stripe is unavailable, show an unavailable message.
- Bench rules: apply DocType changes with `bench --site examic.study reload-doc "LMS Learning" doctype <name>`.
  Verify current installed apps before choosing a migration procedure; never
  rely on historical failures from the retired server. Restart only required
  services after confirming the rollback path.
- Test without waiting: set `trial_ends_on` in the past for a throwaway student; unit tests:
  `../../env/bin/python -m unittest aimaticlearning.lms_learning.test_billing aimaticlearning.lms_learning.test_stripe_provider`.

## Safety

No keys, tokens, bank numbers or webhook secrets in code, git, tasks or logs; they live in
Examic Billing Settings. Never mix live and test keys. Terms, Privacy and Refund pages
are drafts needing owner or legal review. Existing students are never changed without approval.
