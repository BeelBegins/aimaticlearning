# Getting started with Wise API

A developer's guide to start working with the Wise Platform API.

Integrating with the Wise API allows you to build key Wise Platform functionality directly into your application.

This guide will help you understand the foundations and key concepts of the Wise API and provide links to guides and references to help you get started more quickly.

## API access

During the partner onboarding process with the Wise sales and implementation teams, Wise provides a **client ID** and **client secret** for each environment, sandbox then production. These credentials are required for obtaining the tokens you’ll need to make requests to the Wise API and can be accessed and managed via our Developer Hub.

Your client credentials are scoped to your integration and access model determined during the partner onboarding process.
The scope of your credentials determines how you interact with the API and its resources.

### Personal API tokens

Limited access to certain endpoints is also available to Wise business accounts so they can automate parts of their send money flow. These accounts generate a personal API token in the Wise.com app, instead of receiving a client ID and secret, and do not have access to Developer Hub.

If you are a small-to-medium business with a Wise business account, rather than a Wise Platform partner, read our [Personal API token guide](/guides/developer/auth-and-security/personal-api-token) and [Payouts for SMBs guide](/guides/product/send-money/use-cases/payouts-smbs) to learn more.

Personal tokens are limited to a subset of endpoints and not intended for partner account integrations. If in doubt, please contact your CSM to ensure you are using the correct token type.

### Developer hub

Developer Hub is your dedicated portal for managing credentials and security certificates. You can rotate and revoke client credentials as well as upload your mTLS certificate and retrieve the Wise certificate for your truststore.

Wise provides both a sandbox and production Developer Hub:

- Sandbox: [https://wise-sandbox.com/developer-hub](https://wise-sandbox.com/developer-hub)
- Production: [https://wise.com/developer-hub](https://wise.com/developer-hub)


Wise must grant access to Developer Hub before you can log into it. Speak with your implementation team if you don’t have your access details.

### Security

The Wise Platform API implements **OAuth 2.0** for all partner accounts. Wise also offers the following enhanced security frameworks for partners requiring additional protection: mTLS, JOSE, and SCA & 2FA.

Read the [Security and access guide](/guides/developer/auth-and-security) to learn more about how Wise Platform handles security.

### API Documentation

The [Wise API reference](/api-reference) documents our publicly available endpoints and operations. It provides operation descriptions, auth requirements, details about parameters and properties for requests and responses, status codes, and code samples you can copy and modify for your own use.

Our [developer guides](/guides) supplement the API reference. While the reference provides the specifications for each endpoint and operation, the guides provide context and instructions for specific workflows and use cases.

## Environments

Wise provides a sandbox environment for development and testing before moving to the production environment.

**Sandbox**:
This is your initial playground. Use the sandbox environment for development and testing your integration without affecting live data or customer funds.

- Base URL: `https://api.wise-sandbox.com`
- mTLS-enabled: `https://api-mtls.wise-sandbox.com`


**Production**:
Once your integration is thoroughly tested and approved, you'll move to the production environment for live operations.

- Base URL: `https://api.wise.com`
- mTLS-enabled: `https://api-mtls.transferwise.com`


Visit the [Environments guide](/guides/developer/environments) to learn more about using each environment.

## Key concepts

When you start development with the Wise API, it’s good to understand some of the key concepts around different integration models, the core resources you’ll be interacting with, and how Wise implements rate limiting, idempotency, and custom headers.

### Integration models

Wise Platform offers three integration models for partners to integrate with the API:

- The Enterprise model
- The Correspondent model
- The Embedded model


The model you use determines how you perform onboarding and account authorization tasks, as well as how you handle transfers and balance conversions.

By the time you start development, you should understand which integration model you use. The developer guides provide integration model-specific guidance to help you self-serve as much as possible. When an integration model requires specific endpoints or properties/values to successfully accomplish a task or workflow, our developer guides will provide the necessary details.

### Core resources

The core resources you’ll interact with are related to account setup, account access, sending money, and managing balances.

These resources are the foundation of much of the Wise API functionality, though by no means represent *all* capabilities. However, when getting started, it’s important to understand what these core resources are and how they relate to each other in various workflows.

| Resource  | Description |
|  --- | --- |
| User
 | A [user](/api-reference/user) represents a Wise account holder and is the top-level identity in the Wise API hierarchy.
- The user resource contains profiles, which is the resource through which transactions take place.
- Access tokens are issued for a user and used to authenticate all subsequent API calls made on that user's behalf, including creating and accessing profiles.

 |
| Profile | A [profile](/api-reference/profile) represents the personal or business entity associated with a user resource. It serves as the central identifier for nearly all Wise Platform API operations. 

The `profileId` is a required parameter in requests to [create authenticated quotes](/api-reference/quote/quotecreate), [manage balance accounts](/api-reference/balance), and [fund transfers](/api-reference/standard-transfer/transfercreate). |
| KYC Review
 | A [KYC review resource](/api-reference/kyc-review) represents the verification state of a profile and allows you to track whether your customer has satisfied Wise's Know Your Customer (KYC) requirements.
- Its `status` property values, which include `WAITING_CUSTOMER_INPUT` and `PASSED`, determine whether a profile is permitted to create and process transfers without delay, and status changes are surfaced via the `kyc-reviews#state-change` webhook event.
- *KYC review applies to profiles for embedded solutions partners only*.

 |
| Quote
 | A [quote](/api-reference/quote) defines the basic information required for a Wise transfer: the currencies to send between, the amount to send, and the profile sending the money. An *authenticated quote* is one of the resources required to create a transfer, along with the recipient receiving the funds.
- An [unauthenticated quote](/api-reference/quote/quotecreateunauthenticated) can be used to get example quotes. These are useful for showing your customers the exchange rate and fees Wise offers prior to linking an account. Unauthenticated quotes cannot be used to create transfers. They are meant for illustration purposes in partner interfaces only.
- An [authenticated quote](/api-reference/quote/quotecreate) is required when creating a transfer, as its `id` is the property that associates the quoted pricing with the payment. The quote response contains details like the exchange rate, estimated delivery time, and transfer funding methods. Upon creating a quote, the current mid-market exchange rate is locked for 30 minutes and is used for the transfer that is created with the quote ID.

 |
| Recipient | A [recipient](/api-reference/recipient) (also called a recipient account) represents the beneficiary account that will receive funds in a transfer. The recipient resource stores information like the account holder name, bank account details, and other corridor-specific properties. 

The `id` returned when creating a recipient is used as the `targetAccount` value in the transfer creation request and can also be used to update a quote to ensure accurate pricing before the transfer is funded. |
| Transfer | A [transfer](/api-reference/transfer) represents the instruction to move money from a profile to a recipient, combining a quote and a recipient into a single payment object. 

The transfer `id` is used in the [fund transfer request](/api-reference/transfer/transferfund) to trigger the actual movement of funds. |
| Multi-currency account & balance account
 | A [multi-currency account](/api-reference/multi-currency-account) is the top-level account structure tied to a profile, capable of holding multiple currency-specific balance accounts.
- Each [balance account](/api-reference/balance) holds funds in a single currency.
- Each balance account has a unique `id` that can be used as the `targetAccount` in a transfer to top up the balance, as well as to retrieve balance details, view statements, or fund outbound transfers directly from the balance.

 |


### Rate Limiting

Wise enforces rate limiting to ensure the security and stability of the Wise Platform API. Rate limits apply at the gateway level, but some services have additional rate limits for specific operations.

**Gateway-level limits**:

- **Limits for partner accounts**: max 100 requests per second, 1000 requests per minute per client owned by that partner.
- **Limits for Wise business accounts** using a personal API token: applied per-user, not per-client.
  - For Android and Web: 100 requests per second, 900 requests per minute.
  - For iOS: 150 requests per second, 1500 requests per minute.


If you hit the rate limit, you’ll receive an `HTTP 429` status code in the response. The response includes a `retry-after` header, indicating how long to wait before retrying the request.

**Service-level limits**:

Rate limits can apply to certain actions, like the number of quotes or one-time tokens you can create in a specific time frame. These limits vary according to service and operation.

In most cases, you’ll receive the same `429` error if you reach the rate limit for these services.

### Idempotency

It’s important to ensure certain resources are not created twice in the event of a network error or other type of service issue that necessitates a retry. Wise includes idempotency methods on key operations to prevent creating duplicate resources.

Some key operations that support idempotency include:

- [Converting or moving money between balances](/api-reference/balance/balancemovement)
- [Creating a transfer](/api-reference/standard-transfer/transfercreate)
- [Creating a card order](/api-reference/card-order/cardordercreate)


Idempotency applies to specific endpoints and operations that need it, rather than globally. Additionally, different services support idempotency in different ways. Here are a few examples:

- The [convert or move money between balances operation](/api-reference/balance/balancemovement) and [create a card order operation](/api-reference/card-order/cardordercreate) use the **custom header** `X-idempotence-uuid` to hold the unique UUID you generate.
- The [create a transfer operation](/api-reference/standard-transfer/transfercreate) uses the `customerTransactionId` property in the request body.


Be sure to review the API reference for the operation you are performing to understand if and how idempotency is supported for that service.

## Next steps

- Learn about Wise [security and authentication methods](/guides/developer/auth-and-security).
- Look closer at the Wise Platform API with our comprehensive [API reference](/api-reference/).
- Understand how to use [webhooks](/guides/developer/webhooks) to receive real-time notifications about events, which is crucial for handling asynchronous processes.
- Understand Wise [error handling](/guides/developer/errors) to best manage API responses and ensure a smooth user experience.
- Familiarize yourself with Wise’s API [versioning strategy](/guides/developer/global-versioning) to ensure your integration remains compatible with future updates.
- Review information about [testing in the Wise sandbox](/guides/developer/environments).