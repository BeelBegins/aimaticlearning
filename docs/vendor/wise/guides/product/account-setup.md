# Wise Platform partner accounts

Integrating with Wise Platform allows organizations to leverage Wise’s global payment infrastructure to move, hold, and manage money across borders. Before executing transfers, generating quotes, or managing balances, you must establish an organizational identity with Wise Platform.

This is done by creating accounts and profiles:

- **Partner account**: Represents your organizational relationship and API credentials with Wise. It defines your authentication model, permissions, client credentials, and access to Wise Platform services.
- **Profile**: Represents a distinct legal and financial entity (either a corporate organization or an individual person). Every financial resource—including balances, payment routes, quotes, and transfers—is bound to a specific profile for legal ownership, regulatory reporting, and compliance monitoring.


How your partner account and profiles are set up depends on your integration model and business relationship with Wise.

## Partner integration models

Wise Platform supports three integration models, tailored to different business workflows, customer relationships, and regulatory requirements: Enterprise, Correspondent, and Embedded Solutions.

| Model | Description |
|  --- | --- |
| Enterprise | These partners are typically global businesses, payroll providers, marketplaces, and corporations making outbound payouts to international vendors, contractors, or employees.

In this model, your organization is the sole sender and legal owner of all transactions. Payments are originated from your corporate balances or linked business bank accounts to third-party recipients worldwide. |
| Correspondent | These partners are typically regulated banks and non-bank financial institutions routing customer cross-border payments over correspondent banking APIs or messaging networks (for example, SWIFT MT103, ISO 20022 `pacs.008`).

In this model, your institution operates institutional settlement accounts with Wise. The ultimate remitter (your customer) and beneficiary details are transmitted as structured payment metadata within the payment instruction rather than through individual user accounts on Wise. |
| Embedded Solutions | These partners are typically neobanks, fintech platforms, SaaS providers, ERPs, and treasury management platforms embedding Wise account and payment capabilities directly into their software.

In this model, your customers interact entirely within your native user interface. Under the hood, Wise manages or verifies distinct customer identities, giving each end customer their own isolated financial profile. |


## Provisioning accounts and profiles

The responsibility for provisioning partner accounts and initial business profiles differs fundamentally between Enterprise/Correspondent models and Embedded Solutions.

- **Enterprise and Correspondent partners** create their own partner accounts and profiles using standard Wise workflows. Once established, these partners transact out of their own primary business profile.
- **Embedded Solutions partners** operate under a different account architecture and so these accounts and business profiles are provisioned internally by the Wise implementation team. Dedicated integration credentials and application scope are established and handed over as part of onboarding engagement.


## Customer profiles for Embedded Solutions partners

A unique characteristic of the Embedded Solutions model is that the partner provisions and manages individual profiles for each of their end customers.

These unique profiles ensure the customer is the legal sender or recipient of funds. They also allow customers to hold multi-currency balances, obtain local bank account details (IBAN, routing numbers), and maintain their own transaction limits.

Individual profiles allow Wise to meet our AML responsibilities and assess risk at the individual rather than partner level.

## KYC models for Embedded Solutions partners

Every customer profile created under an Embedded Solution integration must undergo Customer Due Diligence (CDD) and Know Your Customer (KYC) verification before transacting.

Wise Platform supports two KYC approaches: **partner-performed onboarding** and **Wise-performed onboarding**.

### Partner-performed onboarding

With this approach, your organization already conducts full identity verification and AML screening on your customers under your own regulatory licenses. Subject to jurisdictional eligibility and compliance approval, Wise enters into a regulatory reliance agreement, accepting your customer due diligence.

While standard KYC is handled on your side, certain banking partners or local corridors may still require transmitting supplementary customer evidences via API.

### Wise-performed onboarding

With this approach, Wise onboards the customers for unlicensed institutions by collecting, validating, and verifying customer identity documents and proof of address. Partners that use Wise-performed onboarding can build a branded experience into their application using Wise's fully hosted, API, or hybrid onboarding options.

## Next steps

- Enterprise and Correspondent partners, see the [Creating an account guide](/guides/product/account-setup/create-partner-account).
- Embedded solution partners, see the [Onboarding your customers guide](/guides/product/account-setup/customer-onboarding).