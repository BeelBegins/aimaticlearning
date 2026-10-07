# Amendments, traces, and recalls

When sending money via Swift, scenarios may arise that require amending, tracing, or recalling the transfer. This guide explains what the amendment, trace, or recall actions mean in practice, the most common scenarios where they’re used, and guidance on how to decide which option is appropriate.

If you need to request an amendment, trace, or recall for a Swift transfer, send a request to the support email address you were provided in your partner contract.

## Amendments

Amendments are used to correct an error in the recipient account number on a Swift payment that is still in progress, allowing the transfer to be completed successfully.

You should request an amendment when an incorrect account number has caused the transfer to be stuck with the beneficiary bank, preventing it from being credited to the beneficiary or rejected.

### Limitations

After a payment has been sent out, only the **recipient’s account number** can be amended. Under no circumstances can the following details be changed once the transfer has been initiated:

- Swift code / BIC
- Recipient name
- Recipient address
- Payment reference


## Traces

A trace is used to investigate the whereabouts of funds that **were
sent with the correct details** but have not been received by the intended
recipient.

Request a trace when:

- A payment was sent with the correct details, yet the recipient reports that the funds have not arrived.
- A Proof of Payment has already been provided to the recipient, but their bank is still unable to locate the transfer.


A trace serves primarily as an **investigative tool** and is not designed to retrieve or recall funds.

Wise will not trace a payment sent to incorrect recipient details.

### Trace results

If the trace confirms that the payment has been received by the
beneficiary bank, the recipient should follow up directly with their bank to resolve the issue.

## Recalls

A recall is used to request the receiving bank to return funds after a payment has already been sent and completed. It should only be applied **as a last resort** as recalls are not guaranteed to succeed and can take several weeks to process.

Request a recall when:

- Prior steps have failed. This includes the customer contacting the
recipient and an unsuccessful payment trace (when available).
- The recipient has been unable to resolve the issue directly with their bank.
- Funds were sent to incorrect recipient details and the customer is unable to reach the beneficiary.


### Limitations

- Recalls for payments require explicit acceptance from the recipient. Therefore, Wise can only attempt recalls when we have confirmation from the recipient of the payment that they are expecting and will accept a return of the funds.
- Recalls are not guaranteed to succeed and can take several weeks to process, though some may be resolved sooner.
- The first update is typically received within the first two weeks, but this is not guaranteed.
- Once the recall request is submitted, the outcome depends on the
cooperation of the beneficiary bank.
- The recall processing speed depends entirely on the beneficiary bank.
Wise cannot speed up their internal processes.


### Fraud recalls

A fraud recall is used to request return of funds after a confirmed or strongly suspected fraud event (for example, social engineering, impersonation, or phishing).

Request a fraud recall when:

- The customer confirms the transfer was fraudulent (they did not authorise it or were deceived).
- A trace or cancellation is not possible.
- Prior recovery steps (contacting recipient, available traces) have failed.


#### Minimum evidence and pre-steps

When reporting fraud to the Wise support team, provide the following information:

- Transfer details (transfer number/transfer reference)
- Information about what happened
- What the payment was for (what was promised?)
- How the sender found the recipient
- When the sender last spoke to the recipient
- When the sender was meant to get the product or service


For some currencies, a police report is mandatory for initiating a fraud
recall.

#### Limitations and expectations

- Recalls require beneficiary/beneficiary-bank cooperation and are not
guaranteed.
- The fraud recall process can take weeks. The initial update is often ~1–2 weeks, but varies.
- Recovery may be partial.
- Some countries/currencies/legal frameworks limit recall options.


### Steps before requesting a recall

- **Share the transfer confirmation with the customer**. This document
outlines the exact details used for the transfer (recipient name, account number, bank code) as well as the date the funds were sent and has the banking reference.
- Ask the customer to **review the transfer confirmation** and identify any potential issues, such as an incorrect account number, a misspelled recipient name, or the payment being sent to the wrong person.
- **Verify recall availability** using the currency table included in this guide before escalating to the Partner Support team. Some currencies have restrictions that cannot be changed.
- **Clearly identify the reason for the recall** (incorrect account details, closed account, recipient unreachable) before submitting the request. Ensure this information is included in the recall request.
- **For fraud-related recalls**, ensure you collect a full, detailed description of the incident and a bank report when available.
- **If the payment is still with Wise**, the fastest and most efficient method to cancel it is through the [cancel transfer endpoint](/api-reference/transfer/transfercancel), when available. If this cannot be used, contact [partnersupport@wise.com](mailto:partnersupport@wise.com), as we may be able to cancel the transfer manually. If cancellation is not possible, we may attempt a recall.


Lost recalls
A recall will be considered “lost” if the beneficiary bank has not
provided a substantive response or consent within one month (≈30
calendar days) of the recall being opened. Exceptions may be
made case-by-case.

## Common scenarios

**Customer sent funds to an old, closed, frozen, or blocked bank account**.

- In most cases, the funds will be returned automatically. But, the timeline depends on the currency and recipient bank. The recipient of the payment may contact their bank directly to help expedite the return process.
- Some banks may retain the funds even if the account is closed. In these cases, ask Wise to initiate a **recall request**.


**Customer sent the funds to a person or entity they know, but the funds
were intended for another recipient**.

- The customer needs to contact the person who they sent the funds to in order to resolve it externally.


**Customer made a typo in the recipient details**.

- For currencies where name checks are performed (for example, USD, JPY, etc):
  - If the account number is correct and recipient name is incorrect,
the funds are likely to be returned back to the sender. Some
currencies allow a few character differences, but some require a
100% name match.
  - If the account number is incorrect, funds usually return
automatically. Customers can either wait for the return to be
processed, or contact the recipient bank and share the Wise
transfer receipt to ask whether the funds were received and when
they may be returned.
- For currencies where name checks are not performed (for example, AUD, CAD, etc):
  - If the account number is correct and recipient name is incorrect,
funds are likely to be credited to the beneficiary.
  - If the account number is incorrect and it matches an existing
account with the beneficiary bank, the funds will be credited to the
wrong recipient despite possible name mismatch. The funds will
not be returned to the sender.


## Currency trace and recall reference

The following table lists the trace and recall support for currencies.

Key:

- 🟢 Currency can be traced/recalled
- 🟠 Only for fraud cases
- 🔴 Trace/recall not available


| Target Currency | Can Trace? | Can Recall? |
|  --- | --- | --- |
| AED | 🟢 | 🟢 |
| ARS | 🔴 | 🔴 |
| AUD | 🟢 | 🟠 |
| BDT | 🟢 | 🟠 |
| BRL | 🔴 | 🔴 |
| CAD | 🟢Only EFT, no trace for Interac | 🔴 |
| CHF | 🟢 | 🟢 |
| CLP | 🟢Not available for all payout partners | 🔴 |
| CNY | 🔴 | 🔴 |
| COP | 🔴 | 🟢 |
| CRC | 🟢 | 🔴 |
| CZK | 🟢 | 🟢 |
| DKK | 🔴 | 🟢 |
| SWIFT DKK | 🟢 | 🟢 |
| EGP | 🟢Not available for all payout partners | 🟢Not available for all payout partners |
| EUR | 🟢 | 🟢 |
| SWIFT EUR | 🟢 | 🟢 |
| GBP | 🟢 | 🟢 |
| SWIFT GBP | 🟢 | 🟢 |
| GEL | 🟢 | 🟢Only payments to cards, not bank transfers |
| GHS | 🟢 | 🟢 |
| HKD | 🔴 | 🟠 |
| HUF | 🔴 | 🟢 |
| IDR | 🔴 | 🔴 |
| ILS | 🟢Not available for all payout partners | 🟢Not available for all payout partners |
| INR | 🟢 | 🟠 |
| KES | 🟢 | 🟢 |
| KRW | 🔴 | 🟠 |
| MAD | 🟢Not available for all payout partners | 🟢Not available for all payout partners |
| MYR | 🔴 | 🟠 |
| MXN | 🔴 | 🟢Not available for all payout partners |
| LKR | 🟢 | 🟠 |
| NGN | 🟢 | 🟢 |
| NOK | 🔴 | 🟢 |
| SWIFT NOK | 🟢 | 🟢 |
| NPR | 🟢 | 🟠 |
| NZD | 🟢 | 🟢 |
| PHP | 🔴 | 🟠 |
| PLN | 🟢 | 🟢Only payments to cards, not bank transfers |
| PKR | 🟢 | 🟠 |
| THB | 🔴 | 🔴 |
| TRY | 🟢 | 🔴 |
| TZS | 🟢 | 🟢 |
| JPY | 🔴 | 🟠 |
| RON | 🟢 | 🟢 |
| SWIFT RON | 🟢 | 🟢 |
| SEK | 🔴 | 🟢 |
| SWIFT SEK | 🟢 | 🟢 |
| SGD | 🔴 | 🟠 |
| UAH | 🔴 | 🟢 |
| UGX | 🟢 | 🟢 |
| USD | 🟢 | 🟢 |
| SWIFT USD | 🟢 | 🟢 |
| UYU | 🔴 | 🔴 |
| VND | 🔴 | 🟠 |
| ZAR | 🟢 | 🟢 |