# Welcome to the Wise API documentation portal

Wise Platform’s API enables banks, financial institutions, and enterprise businesses to embed faster, better-value international transfers, card issuing, and multi-currency account features directly into their own products.

The Wise Platform developer guides and API reference provide the details developers need to integrate successfully with our services.

Wise offers multiple ways to integrate with our API to suit your specific business use cases, whether that’s correspondent banking, payroll, enterprise payments, and more.

If you have not yet entered into a direct integration partnership with Wise, go to [Wise Platform](https://wise.com/platform) to find out more.

## Core functions

The Wise API is designed around the following core functions: sending money (transfers), managing balances, issuing and managing cards, and receiving incoming international transfers.

Send money
Sending money includes actions like generating quotes, creating and selecting recipients, creating transfers, and funding transfers.

Manage balances
Holding and managing funds is done with multi-currency accounts, which are accounts that can hold balances in more than one currency and transfer or convert funds from one balance to another.

Issue cards
The Wise card issuance product includes the capabilities and actions for issuing and managing physical and digital cards for users on your account.

Receive money
Receive both local and international transfers (via Swift) to a Wise account balance.

Partner accounts are scoped to specific functions based on integration model and business type, which you’ll work closely with your implementation team to define.

## Use cases

Wise Platform supports many use cases and business models, from correspondent send to enterprise payroll management.

We’ve grouped these use cases into three integration models. The model you use determines how you perform onboarding and account authorization tasks, as well as how you handle transfers, manage balances, issue cards, and more. When actions differ between models, our documentation will indicate this is the case.

Your implementation team will help you determine the right model for your use case(s). It is also possible for partners to implement more than one integration model, if that is what is needed.

### Embedded partners

The embedded integration model is for regulated financial institutions and fintech platforms that want to offer their customers access to Wise services directly within their own product interface.

In this model, the partner's customers have Wise accounts that are linked to the partner platform, which is authorized to transact on their behalf.

### Enterprise partners

The enterprise integration model is for large-scale and enterprise-level businesses that want to use the Wise API to manage their own funds in their Wise business account. For example, paying employees, vendors, and service providers in multiple currencies.

In this model, Wise has a relationship with the enterprise partner only, not with the partner's end customers or payout recipients.

### Correspondent partners

The correspondent integration model is for regulated financial institutions that want to use the Wise infrastructure to process cross-border payments on behalf of their customers. Examples of these types of financial institutions include:

- Tier 1 traditional banks
- Small and mid-size banks
- Neo and challenger banks
- Electronic money institutions (EMIs)
- Brokerages


In this model, the partner holds a Wise account and executes transactions on their customers' behalf. The partner's customers are the “originators” of the financial transactions but do not have their own Wise accounts in this scenario. They are often not aware that Wise is being used to process their transactions.

## KYC

Know Your Customer (KYC) and Know Your Business (KYB) is a mandatory verification process used by financial institutions to ensure they know who their client is and comply with anti-money laundering (AML) regulations.

Wise Partners are verified by the Wise team during the initial partner contracting and onboarding stages. If a partner is performing transactions on behalf of their own customers, those customers must also be verified before Wise can perform financial transactions for them.

The process for customer KYC/B depends on whether the partner is a regulated entity licensed to perform customer due diligence (CDD) and KYC or not. Both Wise-performed and partner-performed KYC models are available and you’ll work closely with your implementation team to determine which applies to your integration.

## Integration support

Wise provides technical support to assist with API integration issues and troubleshooting for both partner accounts and business accounts. Our Enterprise support team also provides operational assistance for partners managing transactions for their customers.

See our [Wise Platform support guide](/guides/product/partner) for details about contact methods and frequently asked questions.