# Direct debits in the UK and Europe

To integrate direct debits into your platform, there are universal requirements you need to follow.

## Mandate requirements

You must obtain a **mandate**, which is the customer's legal authorization for you to debit their account. This consent can be in either paper or electronic form.

Your mandate must include:

- The customer's full name and bank account details (e.g., IBAN).
- Your company's name and Creditor ID.
- Specific legal wording that authorizes you to pull funds from the account.


## Required mandate information 

Beyond the legal requirement to create a mandate, any customer-facing pages you create must display specific information to be compliant. This includes:

- **Mandatory legal wording**: The mandate page must contain specific legal text as defined by the European Payments Council (EPC). The exact wording differs between the **Core** and **B2B** schemes. This text outlines the customer's rights, including their "no-questions-asked" refund period. [Explore the mandatory wording on the European Payments Council website](https://www.europeanpaymentscouncil.eu/what-we-do/epc-payment-schemes/sepa-direct-debit/sepa-direct-debit-core-rulebook-and-implementation).
- **Unique Mandate Reference (UMR)**: A unique reference number that identifies this specific mandate. This number must be assigned by you and remain consistent for the lifetime of the mandate.
- **Creditor Identifier**: Your company’s official SEPA Creditor ID (CI) must be clearly displayed. This ID allows banks to recognize you as the authorized entity collecting the funds.
- **Company information**: Your company's legal name, and often your full address, must be visible on the page.


## Visual and functional guidance

- **Logo**: While not explicitly a mandate requirement, the use of a Direct Debit logo is a best practice to build trust and recognition. You'll often need to obtain approval from your sponsoring payment service provider to use this logo in your documentation and on your forms.
- **Confirmation**: The customer must take an explicit action, such as clicking a button or signing, to give their authorization. This "electronic signature" must be logged and stored.
- **Payment confirmation page**: After a successful mandate setup, the payment confirmation page should reiterate the key details of the agreement and provide a clear, positive message confirming that the mandate has been created.
- **Record keeping**: You are legally required to securely store all mandates (both paper and electronic) for the duration of their validity and for a minimum of 36 months after the final collection. This is required for verification or legal purposes if a dispute arises.


## Pre-notification rules

Before each payment, you are required to send a **pre-notification** to your customer to inform them of the upcoming debit. This ensures transparency and gives them time to prepare.

- **Notice period**: You must send this notification at least **14 calendar days** before the collection date. This period can be shorter if you have agreed to this with your customer in the mandate.
- **Required information**: The pre-notification must clearly state the payment amount, the collection date, and the unique mandate reference.


### Funding transfers

Once a payment is collected, the funds will be used to **directly fund a transfer**. This process typically takes a few business days for the funds to settle.

## Custom reference constraints 

If you are sending reference fields when creating payment instruments, then different scheme constraints also apply.

### BACS reference constraints 

| Reference Type | Length (Characters) | Rules |
|  --- | --- | --- |
| **Mandate Reference** | Minimum: 6 charsMaximum: 18 chars | - Only alphanumeric **(a-z, A-Z, 0-9)**; exclude special characters- No leading or trailing spaces- Must not start with **“DDIC”**- Must not contain all the same characters |
| **Payment Reference** | Minimum: 0 charsMaximum: 17 chars | - Can be the same across multiple payments- No leading or trailing spaces |
| **Combined (Mandate & Payment) Reference** | Maximum: 17 chars | - The rules governing the Mandate Reference also apply to this field.- When both a Mandate Reference and a Payment Reference are supplied, their total length must not exceed 17 characters. They are later concatenated with a hyphen (`-`), resulting in a maximum combined length of 18 characters. |


### SEPA reference constraints 

| Reference Type | Length (Characters) | Validation (for Custom) |
|  --- | --- | --- |
| **Mandate Reference** | Maximum: **35** chars | - Alphanumeric **(a-z, A-Z, 0-9)**- Special symbols `/ - ? : ( ) & . , '` and a space- Characters can repeat |
| **Payment Reference** | Maximum: **140** chars | - Alphanumeric **(a-z, A-Z, 0-9)**- Special characters are not allowed, including `- ! @ # $ % ^ * _ { }` |
| **Combined (Mandate & Payment) Reference** | Maximum: **175** chars |  |