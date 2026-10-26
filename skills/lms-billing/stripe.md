# Stripe provider

Docs saved in `docs/vendor/stripe/` (Checkout, Billing, trials, webhooks, signatures, portal).
Code: `lms_learning/billing_providers/stripe.py` and `billing.py`.

## Flow

1. Student on `/billing` picks a plan; `billing.start_checkout` creates a hosted Checkout
   Session (card data never touches our server). Monthly = `subscription` mode and charges
   £49 at Checkout; the paid month and renewal cycle start that day. 3-Month = one-off
   `payment` mode for £99, paid at Checkout, with its paid period following the free month.
2. Stripe calls `/api/method/aimaticlearning.lms_learning.billing.stripe_webhook`.
   Signature: header `Stripe-Signature: t=...,v1=...`, HMAC SHA-256 of `t.payload` with the
   endpoint secret, 300 second tolerance (`verify_signature`).
3. Events (`interpret_event`): `checkout.session.completed` links the Stripe customer and
   subscription (subscription mode) or pays the 3-Month plan (payment mode);
   `invoice.paid` with an amount above zero extends a Monthly subscription by one month
   (first and renewal invoices alike); `invoice.payment_failed` stores a message and emails
   the student; `customer.subscription.deleted` unlinks the subscription (access runs to `paid_until`).
4. Events are logged by id in `Examic Payment Event`; unmatched ones show "Needs review".
5. Students use "Manage card and cancel" (Stripe customer portal) to update or cancel.

## Setup in Stripe (test mode first)

Create Products and Prices: Monthly (recurring, GBP 49, monthly) and 3-Month (one-time, GBP 99).
Add a webhook endpoint for the URL above with events: `checkout.session.completed`,
`invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`. Enable the customer
portal in Stripe settings. Put the keys, price ids and webhook secret in Examic Billing Settings
(Password fields), set Provider = Stripe. Stripe Tax: tick "Use Stripe Tax" only after tax
registrations exist and prices have a tax behaviour.

## Facts

- UK fees (checked 2026-10-07): UK cards 1.5% + 20p, EEA 2.5% + 20p, international 3.25% + 20p,
  Billing +0.7%; about 1.3 to 2.1 GBP on 49.
- EXAMIC LTD has non-resident directors, so live approval is not guaranteed
  (UK entity, tax ID, UK address, phone, website, ID, bank account). Payouts go to the Wise
  Business GBP account if Stripe accepts it. Fallback provider: Airwallex (not built).
- Sandbox keys (sk_test, pk_test) were shared in chat on 2026-10-07; rotate them when going live.

## Live verification (2026-10-26)

Examic Live webhook is enabled and includes all four required events; no event edits were needed. The previously absent customer portal configuration was created and verified as the active Live default with payment-method updates and cancellation at period end enabled. Return URL: https://www.examic.study/billing. No keys or prices changed. A real student portal click and payment lifecycle are still pending.
