# Onboarding EU-based customers

If you have customers that meet all the following criteria, then you must implement the steps in this guide to onboard them:

- You perform your own KYC for your customers.
- Your customer’s address is in an EEA country.
- Your customer creates a quote with source currency for an EEA currency.


## Source of Wealth document

Source of wealth is a document that proves the customer's main source of income.

If `SOURCE_OF_WEALTH` is required (as indicated by the [cdd-check-state-change](/api-reference/webhook-event/eventprofilescddcheckstatechange) webhook), your customer must provide a verification document.

Personal profiles
For personal profile, the acceptable documents depends on the `source_of_income` the customer provided in the [upload-evidences](/api-reference/verification/verificationuploadevidences) endpoint.

Here is a list of acceptable documents for personal profiles for each `source_of_income`.

| Source of income | Acceptable documents |
|  --- | --- |
| `SALARY` | - Payslip (3 months worth)
- 3 months of Bank statements/transaction details confirming salary deposits
- Statements from Payoneer/Paysera/PayAlly/PayPal etc
- Tax return
- Employment contract
- Proof of employment
- Unemployment allocation
- Maternity/Paternity allowance/benefit
- W2 Earnings Summary
- Bolt courier report / Wolt, Uber or Bolt driver report or other similar
- UpWork statement
- E-commerce platform statement
- Invoice (contractors only)

 |
| `INVESTMENTS` | - Employee stock plan exercise confirmation
- Investment/portfolio account statement
- Dividend voucher
- Share sale confirmation
- Crypto wallet statement
- Bank statement confirming income from investments

 |
| `PENSION` | - Pension statement
- Bank statement confirming pension income

 |
| `INHERITANCE` | - Grant of Probate
- Will
- Trust Deed
- Death certificate (as supporting doc)
- Bank statement, confirming income from inheritance

 |
| `LOAN` | Loan Agreement with supporting bank statement showing the amount being received |
| `OTHER` | For example documents that proves:- Gift
- Sold property
- Receive money from family
- Scholarship
- Dividends
- Renting out property
- Lottery winnings
- Divorce
- Child support
- Savings
- Freelancing/Self-employed/Contractor

 |


Business profiles
For business profile, the document depends on `source_of_funding`.

| Source of funding | Acceptable documents |
|  --- | --- |
| `REVENUE` | - Banks statements or invoices with 3-6 months of most recent transactions
- Audited financial statements or annual reports
- Business tax return or declaration

 |
| `BUSINESS_LOAN` | Loan agreements or contracts within the last 12 months |
| `INVESTMENT_INCOME` | Share sale certificates or asset sale agreements from the last 12 months |
| `FUNDING_AND_SHAREHOLDER_INVESTMENTS` | Equity or subscription agreements |
| `DONATIONS` | Donation receipts, tax receipts, or similar documents from the last 12 months |
| `GRANTS` | Grant award letter from the last 12 months |
| `OTHER` | Any official document showing where your funding comes from |


## Proof of Trading address document

Proof of trading address is a document that proves the business operates from the address provided in their profile.

If `TRADING_ADDRESS_PROOF` is required (as indicated via [cdd-check-state-change](/api-reference/webhook-event/eventprofilescddcheckstatechange) webhook), the customer must provide a verification document with the business name on it and issued to the business.

Acceptable sources:

- Bank/card statement
- Any document from a regulated financial services firm
- Gas/water/electricity/waste bill/rental agreement or valid contract
- Any document issued by an institution of the government


## Business Authorisation Letter document

Business Authorisation Letter is a document that authorises a person to act financially on behalf of the company while using the Wise Business account.

[Templates](https://wise.com/help/articles/4xT7V1U2AJ7btCEe4yicu8/how-do-i-get-verified-using-an-authorisation-letter) for the letter based on where the business is registered.

## Repapering EU customers

This functionality is in a closed BETA.

Repapering is the process of performing additional verification for *existing* customers.

Only use this if you began onboarding customers before 1/1/2023 and if you have customers that meet all the following criteria:

- You perform your own KYC for your customers.
- Your customer’s address is in an EEA country.
- Your customer creates a quote with source currency for an EEA currency.


Step-by-step
Before creating a transfer, send a request to the [required-evidences endpoint](/api-reference/verification/verificationgetrequiredevidences) endpoint.

This returns a list of required evidence for the customer.

- If no evidence is required, then proceed to transfer as usual.
- If one or more evidences are required, submit the them via the [upload-evidences endpoint](/api-reference/verification/verificationuploadevidences).


The process from that point will follow the same flow as  onboarding EU customers. Once verified, the customer may proceed with their transfer.

Example sequence diagram
![CDD Flow Sequence Diagram](/assets/cdd-repapering-flow.ae189e6a22a217c7a36b0c10a8129a81ed7e4c1b9ae01bfbc5d7807489245a8d.28b10c14.svg)

Endpoints