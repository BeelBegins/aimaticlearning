# Payment providers: research and decision (2026-10-07)

Decision: Stripe for cards and automatic renewals; Wise only receives GBP payouts and
serves as the manual fallback; Dodo Payments dropped by the owner; Airwallex is the
documented fallback if Stripe declines. Build: `skills/lms-billing/`.

| Provider | Fees (checked 2026-10-07) | Fit |
|---|---|---|
| Stripe (UK) | UK cards 1.5% + 20p, EEA 2.5% + 20p, international 3.25% + 20p; Billing +0.7%; currency conversion +2%. About GBP 1.3 to 2.1 on GBP 49 | Cheapest; subscriptions and saved cards; needs a UK entity and approval |
| Dodo Payments | 4% + 40c, +1.5% international, +0.5% subscriptions; refund 1 USD, chargeback 30 USD; handles VAT as merchant of record; Pakistan merchants unsupported, UK supported. About GBP 3.2 on GBP 49 | Not chosen |
| Wise | Receiving fees vary; no checkout, no payment-link API, no recurring charges, no statement or balance webhook for UK accounts with a personal token | Payout bank and manual fallback only (`docs/wise-payments.md`) |
| Airwallex | Not researched | Fallback if Stripe declines (recurring payment and subscription APIs) |

Company: EXAMIC LTD, two non-resident directors. Stripe approval needs a UK legal
entity, tax ID, UK physical address, phone, working website, ID and a qualifying bank
account; approval is not guaranteed. Ask Stripe in writing whether GBP payouts to the Wise
Business account are accepted.

Stripe sandbox keys were shared in chat on 2026-10-07 and stored only in Examic Billing
Settings on the LMS site (never in git). Rotate them before going live.
