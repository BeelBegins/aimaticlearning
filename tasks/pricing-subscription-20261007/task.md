# Task: pricing-subscription-20261007

Goal: Final pricing and paid access for the 2026-10-10 launch, payments through
Wise. Supersedes the earlier "2 months free, £25" copy in `launch-oct10-20261005`.

Environment (site `lms.aimatic.tech`; local-only or live): local first; live steps
need approval (reload-doc, restart with `sudo -n supervisorctl restart
frappe-bench-web: frappe-bench-workers:`; do not run `migrate`, it fails on the leftover `aimatic` app).

Owner decisions (2026-10-07):
- Monthly: month 1 free (no payment, cancel anytime), then £49 per month. Free
  month = Mock 1 and Mock 2 (4 FLK1 + 4 FLK2 sessions), limited mock access.
- 3-Month (best value): month 1 free, then £99 once for months 2 to 4 (£33/month).
- Both paid plans: all mocks, full resources, detailed performance analytics.
- Only new signups get a subscription. Existing 28 students: no lock, mocks 3 and 4 stay locked as today.
- After month 1 unpaid: ALL access locked, only the billing page; data kept.
- Payments: Wise only (no Stripe now). Manual confirmation, see `docs/wise-payments.md`.

Files / allowed edit paths: `lms_learning/billing.py`, `lms_learning/doctype/examic_{subscription,payment,billing_settings}/`, `hooks.py`, `lms_learning/{enrollment,exam_product,page_renderer}.py`, `www/{pricing,billing,sqe,terms,refund-policy}.*`, `public/css/sqe_frappe_theme.css`, tests.

Acceptance criteria: new signup gets Trial subscription (+30 days); locked student
is redirected to `/billing` and app APIs answer 402; Confirm payment opens the paid
period (monthly +1 month, 3-month +3 months, counted from the end of the free month);
mocks 3 and 4 open only when paid or staff; reminders 3 days before and on the day.

Constraints: no core edits; Wise account details live in Examic Billing Settings
(DB), never in code or git; live approval; legal wording needs owner review.

Base commit and existing local changes: base `46edab7`; Wise docs saved in `docs/vendor/wise/`.

Skills used: `lms-learning`, `lms-exam-mode`.

Verification: unit tests for state, date maths, allow-list; throwaway signup then
time-shift (set `trial_ends_on` in the past) to test lock, Confirm payment, both plans.

Status: review (Stripe sandbox test pending live check; see below).

Remaining issues / next step: build and test locally; owner supplies Wise GBP
account details (enter in Desk); optional later: Wise statement CSV import.

Update 2026-10-07 (supersedes the Wise-only decision above): owner dropped Dodo and chose
Stripe for cards and automatic renewals, Wise as payout bank and manual fallback.
Built: provider framework (`billing_providers/`), `Examic Billing Settings` as the
configuration interface, Stripe Checkout, portal and signed webhook, event log, docs in
`skills/lms-billing/` and `docs/payment-providers.md`. Open: Stripe live approval for
EXAMIC LTD (non-resident directors), written confirmation of GBP payouts to Wise,
Wise GBP details in Desk, legal wording, rotate the sandbox keys shared in chat.

Sandbox rollout 2026-10-07 (done): Stripe test Products/Prices, webhook endpoint and portal
configuration created through the API; ids and secrets stored in Examic Billing Settings
only. Lifecycle test on a throwaway student passed and its data was removed. Two bugs
found and fixed: `frappe.local.__dict__` in `access_state` (use an attribute) and the
payment Method select lacking "Stripe card". Provider stays `Manual` until the owner goes live.

Owner clarification 2026-10-08: the free signup month includes Mock 1 and Mock 2 only.
Choosing Monthly starts a paid subscription immediately: charge GBP 49 at Checkout, unlock
all mocks when Stripe confirms the payment, and renew monthly from the checkout date. The
free month is optional; choosing Monthly ends the free-only mock limit. The 3-Month plan
remains a GBP 99 one-time charge, with its paid period following the free month and all
mocks unlocking as soon as payment is confirmed. Monthly Checkout must not add a Stripe
trial. The live implementation is in `billing.py`, `billing_providers/stripe.py`, and
`www/billing.html`; restart only web/workers after static review. Do not run a live charge
as a verification step.

Owner report 2026-10-08: `frutyfriend@gmail.com` had no subscription row. Billing UI
incorrectly treated that as full access, while Mock 4 remained locked and Checkout
refused to start. No-row students now have a distinct `unsubscribed` billing state, keep
their courses and Mocks 1 and 2, see plan choices, and get a pending subscription record
only when starting Checkout. A paid webhook opens all mocks. Staff and non-student users
cannot create student subscriptions through Checkout.
