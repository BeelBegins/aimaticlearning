# EFT debits in Canada

EFT debits are payments collected from a payer's Canadian bank account under Payments Canada's Pre-Authorized Debit (PAD) framework.

This guide explains the PAD Agreement, authorization, pre-notification, record-keeping, and funding requirements to follow when using the Wise Platform [Direct Debit endpoints](/api-reference/direct-debit-account) to fund transfers from Canadian bank accounts.

## PAD Agreement requirements

You must obtain a **PAD Agreement**, which is the payer's legal authorization for you to debit their account. As the initiator, you are responsible for obtaining and retaining this agreement before initiating any debit.

Your PAD Agreement must include:

- The payer's full name and bank account details (transit number, institution number, and account number).
- Your company's legal name as it will appear on the payer's bank statement.
- Specific legal wording that authorizes you to pull funds from the account.


## Compliance details

Beyond the legal requirement to obtain a PAD Agreement, any customer-facing pages you create must display specific information to be compliant.

### Authorization language

The PAD Agreement page must contain language that clearly identifies the payment amount (or how a variable amount is determined), the debit schedule, the start date, and how the payer can cancel.

EFT/PAD is governed by [Payments Canada Rule H1](https://www.payments.ca/sites/default/files/h1eng.pdf).

### Reimbursement rights

The agreement must clearly state the payer's right to seek reimbursement for any debit not in accordance with the agreement.

Reimbursement timeframes differ by customer type:

- **Consumer (Personal PAD)**: The payer has the right to seek reimbursement for any unauthorized or non-compliant debit within **90 calendar days** of the debit date.
- **Business (Business PAD)**: The payer has the right to seek reimbursement within **10 business days** of the debit date. This may be extended to **90 calendar days** only if no prior agreement existed between the parties.


### Cancellation rights

The agreement must include the following standard cancellation language from Payments Canada:

> "You, the Payer, may revoke this authorization at any time, subject to providing notice of 30 calendar days. Note: Business PADs may specify a different cancellation timeframe if mutually agreed, however 30 days is standard. To obtain a sample cancellation form, or for more information on your right to cancel a PAD Agreement, you may contact your financial institution or visit www.payments.ca."


### Other details to include

The agreement must also include:

- **Amount of transfer**: The agreement must identify if the transfer is a fixed amount or a variable amount. If variable, it must state how the amount is calculated and include a clause stating that you will provide **10 calendar days' advance notice** of the amount before the debit occurs, unless the consumer waives this window. Retain this waiver as evidence.
- **Timing, schedule, and start date**: Define how often the money is debited, for example weekly, bi-weekly, monthly, on a specific date, or after a triggering event. Provide the explicit date that the first debit is authorized to occur.
- **Company information**: Your company's legal name and contact details must be visible on the PAD Agreement page.
- **Agreement reference**: Assign a unique reference number that identifies the PAD Agreement and keep it consistent for the lifetime of the agreement.


## Visual and functional guidance

- **Confirmation**: The payer must take an explicit action, such as clicking a button or signing, to give their authorization. This action must be logged and stored.
- **Payment confirmation page**: After a successful PAD Agreement setup, the payment confirmation page should reiterate the key details of the agreement and provide a clear, positive message confirming that the PAD Agreement has been created.
- **Record keeping**: You are legally required to securely store all PAD Agreements for the duration of their validity and for a minimum of **7 years** after the last debit initiated under the agreement. This is required for verification or legal purposes if a reimbursement claim arises.


## Pre-notification rules

Canadian PAD rules require advance written notice to the customer in two distinct scenarios.

### First-time setup confirmation

Before pulling the first debit, you must send the customer a confirmation summarising the agreed terms at least **10 calendar days before** the first scheduled debit. This notice must include the debit amount, the interval or schedule, your company contact information, and the unique PAD Agreement reference number.

**Waiver option**: Your PAD Agreement may include a clause allowing the customer to explicitly waive or shorten the 10-day notice period, for example through a checkbox during authorization. If waived, funds may be debited sooner, but a confirmation notification must be sent within **5 calendar days after the first transaction settles**.

### Variable amount or date change

If the debit amount varies or the scheduled payment date changes, you must provide written notice at least **10 calendar days before** the withdrawal, stating the exact amount and collection date.

**Waiver option**: As with the first-time setup, customers may waive or shorten this 10-day window if agreed upfront in the PAD Agreement. This is standard practice for monthly subscriptions with minor fluctuations.

## Funding transfers

Once a payment is collected, the funds will be used to directly fund a transfer. This process typically takes **T+3 to T+5**, depending on submission timing.