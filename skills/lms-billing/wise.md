# Wise (manual provider and payout bank)

Full API docs: `docs/vendor/wise/`. Summary: `docs/wise-payments.md`.

- Wise receives money (GBP account details) and receives Stripe payouts. It cannot confirm
  payments for us: the account is UK-based, and a personal API token cannot read statements
  or create balance webhooks there (US, CA, AU, NZ, SG, MY only). Webhooks
  (`balances#update`, `incoming-transfer#credited`) need a Wise Platform partnership.
- Payment links exist only in the Wise.com interface (single-use or reusable); bank transfer
  or Pay with Wise; no cards for new Business accounts; no recurring charges; no API to create them.
- Manual provider = the fallback: bank details come from Examic Billing Settings
  (account holder, sort code, account number), student reference `EXM-` plus six characters
  (`billing._reference`), staff confirm in Desk.
- If Wise Platform access ever arrives, add `billing_providers/wise.py`: verify the webhook
  signature, match the `EXM-` reference in `transfer_reference`, call `billing.apply_payment`.

## What to ask the Wise account owner

GBP account holder, sort code and account number (typed into Desk, not git); whether Stripe can
pay out to this account; who checks payments; never a login or password.
