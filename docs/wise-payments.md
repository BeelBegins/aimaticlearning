# Wise for Examic payments: what the official docs say

Saved copy of Wise's developer docs (232 pages, fetched 2026-10-07 from
`docs.wise.com/llms.txt`): `docs/vendor/wise/`. Read these before changing billing.
Do not edit the vendor files; refetch if Wise changes. Our summary:

| Question | Answer (file under `docs/vendor/wise/`) |
|---|---|
| Wise in an online checkout? | No. "We don't offer the option to build Wise into your checkout flow" (`guides/product/partner/business-account-support.md`). |
| Create payment links by API? | No. "Create these links using the Wise.com interface" (same file). |
| Recommended way to get paid | Use the local bank details of the Wise account (GBP sort code and account number) and reconcile incoming payments. |
| Personal API token | Only quotes, recipients, transfers, tracking transfers. Balance statements and funding transfers by API are not supported for UK accounts (`guides/developer/auth-and-security/personal-api-token.md`). |
| Webhooks (`balances#update`, `incoming-transfer#credited`) | Subscribing needs a client key and client-credentials token from Wise Developer Hub, application level, access by permission (`guides/developer/webhooks/subscribe-to-webhooks.md`). A plain business account with a personal token does not get this; it needs a Wise partnership. |
| Cards / auto-renew | Not offered for receiving; a payer pays each time by bank transfer or Pay with Wise (payment links, UK blog 2026). |

Consequences for the build (`tasks/pricing-subscription-20261007/task.md`):
- Payment confirmation is manual: student pays the GBP details with a unique
  reference (`EXM-xxxxxx`), staff click Confirm payment in Desk.
- Later, low-effort help: import the Wise statement CSV (Reference column) and
  match `EXM-` references. Full automation needs a Wise Platform agreement or Stripe.
- Monthly plan = student pays again every month after a reminder.
