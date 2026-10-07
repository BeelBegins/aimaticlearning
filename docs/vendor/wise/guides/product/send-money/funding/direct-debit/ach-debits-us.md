# ACH debits in the US

ACH debits are payments collected from a payer's US bank account through the Automated Clearing House (ACH) network.

This guide explains the authorization, account validation, fraud detection, pre-notification, record-keeping, and settlement requirements to follow when using the Wise Platform [Direct Debit endpoints](/api-reference/direct-debit-account)  to fund transfers from US bank accounts.

## Authorization requirements

You must obtain an **ACH authorization**, which is the payer's legal authorization for you to debit their account. As the initiator, you are responsible for obtaining and retaining this authorization before submitting any debit entries.

Your authorization must include:

- The payer's full name and bank account details (ABA routing number and account number).
- Your company's legal name as it will appear on the payer's bank statement.
- Specific legal wording that authorizes you to pull funds from the account.


## Required authorization information

Beyond the legal requirement to obtain an authorization, any customer-facing pages you create must display specific information to be compliant. This includes:

- **Company information**: Your company's legal name must be visible on the authorization page.
- **Authorization reference**: A unique reference number that identifies this specific authorization. This number must be assigned by you and remain consistent for the lifetime of the authorization.


### Authorization language

The authorization page displayed to customers must include language that clearly identifies the payment amount (or how a variable amount is determined), the frequency of debits, the start date, and how the Payer can revoke authorization. ACH is governed by [National Automated Clearing House Association (NACHA) Operating Rules](https://www.nacha.org/) and we expect you to ensure that your authorization flows are NACHA compliant.

## Visual and functional guidance

The guidance in this section reflects the NACHA Operating Rules, which Wise is contractually required to follow under its bank partner agreements. We suggest following as general guidelines:

- **Confirmation**: The Payer must take an explicit action, such as clicking a button or signing, to give their authorization. This action must be logged and stored.
- **Payment confirmation page**: After a successful authorization setup, the payment confirmation page should reiterate the key details of the agreement and provide a clear, positive message confirming that the authorization has been created.
- **Record keeping**: You are legally required to securely store all authorizations for the duration of their validity and for a minimum of **2 years** after the authorization is revoked or the last entry is initiated, whichever is later. This is required for verification or legal purposes if a return or dispute arises.


Regulatory context
NACHA is not a federal statute. However, most state-level ACH regulations have been superseded by [Regulation E (Reg E)](https://www.federalreserve.gov/frrs/regulations/regulation-e-electronic-fund-transfers.htm) at the federal level. Partners should consult their own legal counsel to confirm whether any additional state-level requirements apply to their specific use case or jurisdiction.

Reg E consumer protections apply to **consumer** ACH transactions. If your use case involves debiting consumer accounts (for example, inward remittance flows), additional Reg E obligations will apply. Please consult your legal counsel for your specific use case and jurisdiction.

## Account validation and fraud detection

NACHA requires you to perform account validation if you debit money from **a personal consumer** bank account via online or a mobile device (*flagged with **'WEB' SEC code** in NACHA*). Account validation must confirm that the routing number and account are capable of receiving ACH debits before initiating the first debit.

Accepted validation methods include:

- Open banking or bank account verification
- Micro-deposits
- A NACHA-approved third-party validation service


NACHA supplemental fraud detection standards
**NACHA supplemental fraud detection standards** also apply to 'WEB' entries. You are contractually required to implement sufficient fraud controls as part of your integration obligations for either type of customers (personal consumer or businesses).

## Pre-notification rules

Pre-notification requirements differ based on transaction type: B2B ACH or Consumer ACH.

- **B2B ACH**: Pre-notification is **not required** under NACHA Operating Rules for business-to-business transactions. Check your Wise integration agreement to confirm whether your bank partner imposes any additional requirements.
- **Consumer ACH (WEB SEC code entries)**: Pre-notification is required in specific circumstances — it does not apply before every recurring debit. The two scenarios where notice is required are:
  - **Recurring date changes**: You must notify the Payer at least **7 calendar days** before the new collection date.
  - **Variable amounts**: If the debit amount varies and is not already covered by explicit authorization language, you must notify the Payer at least **10 calendar days** before the collection date. This requirement is defined in NACHA Article 2, section 2.3.2.6.
    - This does not apply to customer-initiated single transfers, or where authorization language already covers a range of amounts.


**Avoiding per-debit notifications**:

You can avoid per-debit notification obligations by including explicit, comprehensive language in your upfront authorization. The authorization must clearly state:

- The payment amount (or how a variable amount is determined)
- The frequency of debits
- The start date
- How the Payer can revoke authorization
- A minimum 30 calendar days' notice requirement for cancellation


**Example authorization language**:

> "You're authorizing [Partner Name] to debit your bank account ending in [XXXX] for amounts owed for your use of their services or products. This will continue until you cancel — just give [Partner Name] 30 days notice to do so. Your authorization was confirmed on [date]."


## Funding transfers

Once a payment is collected, the funds are used to directly fund a transfer. Settlement timing depends on your ACH entry class, submission cutoff, and your specific agreement with Wise. Typically, this process takes **T+3 to T+4** business days for standard ACH, depending on submission timing.

Key details:

- **Business days only**: ACH does not process on weekends or US federal bank holidays. A debit submitted on Friday after the cutoff, or on a holiday, will begin processing on the next business day — adding 1-3 days to effective settlement.
- **Cutoff times**: Submissions received after the daily cutoff are treated as next-day submissions.
- **Funds availability**: Funds are typically available in the Payer's account by the morning of the settlement day. Exact timing depends on the Payer's bank processing schedule.


Daily cutoff
Exact cutoff timings are confirmed in your integration agreement with Wise.