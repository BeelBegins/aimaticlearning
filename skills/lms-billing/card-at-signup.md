# Card at signup

New self-service signups must choose a plan and add a card before using the portal. Stripe
holds both the free month and the charge:

- Signup sets `Examic Subscription.card_required = 1` when Stripe is the ready provider.
  Older students and staff-invited students never get it, so nothing changes for them.
- A `card_required` student with no `stripe_subscription` is in state `setup`: only `/billing`
  and public pages open (`enforce_access`), and `/billing` shows Monthly and 3-Month.
- Checkout is a Stripe subscription with `subscription_data[trial_end]` set to the day after
  `trial_ends_on` (needs 49h or more ahead, else it charges now). The card is saved now, the
  first charge is automatic on that day. `payment_method_collection=always`; a missing card at
  trial end cancels the subscription.
- Monthly uses `stripe_monthly_price_id`. 3-Month needs a NEW recurring price of the 3-Month
  amount every 3 months, stored in `stripe_three_month_recurring_price_id`. After checkout the
  webhook sets Stripe `cancel_at` one term after the first charge (`_end_fixed_term`), so it never
  renews. Without that price the 3-Month plan is hidden from `setup` students and the old
  one-off price is used only for students who are not deferred.
- `checkout.session.completed` with `payment_status=no_payment_required` is the `trial` action:
  it stores `pending_plan`, never `plan`, so mocks stay locked and `monthly_subscription_active`
  stays false until the first `invoice.paid` (which carries the plan in subscription metadata)
  calls `apply_payment`.
- Cancelling the subscription during the free month sends the student back to `setup`.
- Reminder email (3 days and 0 days) states the charge date, plan and amount when a card plan exists.

Going live needs, in order and each with approval: create the 3-Month recurring price in Stripe
and save its id in Examic Billing Settings; `bench --site examic.study reload-doc "LMS Learning"
doctype examic_subscription` and `examic_billing_settings`; re-run
`enrollment.create_email_templates` for the welcome and reminder wording; restart; test the whole
path with Stripe test keys first (signup, trial Checkout for both plans, `invoice.paid` after a
test clock advance, 3-Month `cancel_at` not producing a second invoice). Public copy on
`/pricing`, `/introductory-offer`, `/terms`, `/refund-policy`, `/how-it-works` and `/sqe` was
changed to match and needs owner or legal review before launch (a charge after a free trial).


## Plan chosen at signup

The signup form shows Monthly and 3-Month with prices and the first charge date. The choice is kept in the browser (`examic_plan`) and `/billing` lists that plan first and marks it. It is a preselection only: the student still confirms the plan and adds the card on `/billing`. Nothing about it is stored server side.
