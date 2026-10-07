# Correspondent partner integrations

Make cross-border payments on behalf of your customers.

With Wise Platform, licensed banks and financial institutions that want to execute transactions on their customer’s behalf integrate with Wise Platform as a *correspondent partner*.

For correspondent partners, transfers are funded from your Wise Nostro account or other agreed funding source. The initial account setup and authorization process differ from other types of integrations, as do certain steps to send money on behalf of your customers.

## Before you begin

- Read through this intro guide to understand the overall process and the two send money flows you can implement.
- Make sure you have access to the [sandbox Developer Hub](https://wise-sandbox.com/developer-hub) and [production Developer Hub](https://wise.com/developer-hub) to access client credentials and manage security certificates.
- Understand the scope of your integration. You’ll work closely with your implementation team to determine the scope, which includes supported currency corridors, payment rails, and funding and settlement methods.


## Account setup and authorization

For correspondent partners, profile setup and authorization is a **one-time** process.

You will:

- Create a Wise account with a business profile (either using the API or on Wise.com).
- Authorize Wise Platform to access your application.
- Exchange your auth code for access tokens.


Once you have your access tokens, you can start sending money on behalf of your customers.

The [Correspondent partner onboarding guide](/guides/product/send-money/use-cases/correspondent/correspondent-partner-onboarding) provides you with the one-time setup steps to create a Wise user and business profile, authorize your application, and obtain OAuth tokens.

## Sending money

Sending money via the Wise API requires creating and interacting with multiple resource types:

- The **recipient account** defines who is receiving the money and how.
- The **authenticated quote** defines the currencies and amounts involved in the transfer.
- The **transfer** combines the quote and recipient resources into a set of instructions for moving the money from the profile to the recipient.
- The **funding request** triggers the actual movement of funds (and relies on your funding/settlement model).


### Send flow patterns

Wise supports two patterns for sending money: **recipient-first** and **quote-first**.

Both flows are valid and have different advantages. Your choice depends on your business context and the user experience you want to create.

#### Recipient-first

The recipient-first flow creates (or selects) the recipient account before creating the quote. This is the most common flow and is the flow the Wise.com app uses.

**Recipient → Quote → Transfer → Fund** (RQTF)

Benefits and considerations:

- The fees/ETA are precise for the exact recipient from the start.
- No separate [update quote](/guides/product/send-money/use-cases/correspondent/correspondent-create-auth-quote#update-quote) step required.
- You will not have a `quoteId` when retrieving recipient requirements, so you must enter the source and target currencies and amounts as query parameters (certain corridors have limitations around this method).


When using the recipient-first flow, follow the correspondent send guides in this order:

1. [List or create recipients](/guides/product/send-money/use-cases/correspondent/correspondent-create-recipient)
2. [Create authenticated quote](/guides/product/send-money/use-cases/correspondent/correspondent-create-auth-quote)
3. [Create third party transfer](/guides/product/send-money/use-cases/correspondent/correspondent-create-transfer)
4. [Fund the transfer](/guides/product/send-money/use-cases/correspondent/correspondent-fund-transfer)


#### Quote-first

The quote-first flow creates the quote resource before creating (or selecting) the recipient.

**Quote → Recipient → Transfer → Fund** (QRTF)

Benefits and considerations:

- Starts with an early price signal before the recipient is finalized.
- Useful when your system prioritizes cost preview up-front.
- You will not have a `targetAccount` value when creating the quote, so you must [update the quote](/guides/product/send-money/use-cases/correspondent/correspondent-create-auth-quote#update-quote) once the recipient is known (can change pricing and delivery estimates).
- If the quote changes, you must check if the recipient and transfer requirements have changed (if so, you may need to provide additional data points in your requests).


When using the quote-first flow, follow the send guides in this order:

1. [Create authenticated quote](/guides/product/send-money/use-cases/correspondent/correspondent-create-auth-quote)
2. [List or create recipients](/guides/product/send-money/use-cases/correspondent/correspondent-create-recipient)
3. [Update the quote](/guides/product/send-money/use-cases/correspondent/correspondent-create-auth-quote#update-quote)
4. [Create third party transfer](/guides/product/send-money/use-cases/correspondent/correspondent-create-transfer)
5. [Fund the transfer](/guides/product/send-money/use-cases/correspondent/correspondent-fund-transfer)


### Recipient and transfer requirements

Recipient account and transfer requirements vary by corridor, so the data needed to create a valid recipient and successfully process a transfer differs depending on the source and target currencies, the payout country, the payment method, and whether the transfer originator is an individual or a business. Requirements can change over time as local payment regulations and anti-money laundering (AML) obligations evolve.

To handle this variability, Wise provides endpoints to retrieve the exact requirements for any given payment scenario at the time of the request, rather than relying on hardcoded field lists that risk becoming outdated.

Sending incomplete or incorrect recipient or transfer payloads is one of the most common causes of integration failures. Partners who do not retrieve and validate requirements are more likely to encounter unexpected validation errors and transfer failures.

Whether you use Wise’s dynamic forms or hardcode requirements into your system, ensure your integration automatically adapts to changes by leveraging the recipient account and transfer requirements endpoints.

#### Retrieving recipient account requirements

The retrieve recipient account requirements [GET](/api-reference/recipient/recipientaccountrequirementsget) and [POST](/api-reference/recipient/recipientaccountrequirementspost) operations work together to ensure you collect the complete set of recipient details before creating a recipient account.

- The `GET` endpoint returns the initial set of required fields for a given currency and payment route (for example, the recipient's name, account number format, bank code, etc). When the `refreshRequirementsOnChange` field in the response is `true`, this signals that selecting a value for that field may reveal *additional* required fields.
- The `POST` endpoint handles this follow-up step. As your end user provides recipient details, you submit the in-progress recipient payload to the `POST` endpoint, which returns any additional fields that have become required based on the values provided so far.


This back-and-forth ensures no required field is missed before submitting the [Create recipient account](/api-reference/recipient/recipientcreate) request.

Dynamic forms
Using Wise’s [dynamic forms](/guides/product/send-money/recipient-verification/account-requirements) with these two endpoints replaces the need to maintain static mappings of what data is needed per currency or route.

#### Validating transfer requirements

Certain transfers require additional information depending on regional regulations or Wise's compliance obligations. The [Validate transfer requirements](/api-reference/transfer/transferrequirementsvalidate) endpoint surfaces these requirements based on the combination of sender, quote, and recipient for a transfer.

Transfer-level requirements can include details like transfer purpose, source of funds, and payment references — data points that vary by corridor and may be mandated by local and AML regulations.

Like recipient requirements, transfer requirements are **dynamic** in that new fields may be required based on the values in earlier fields, as indicated when the `refreshRequirementsOnChange` field is `true`.

## Tracking third party transfers

Once a transfer is created and funded, webhooks provide visibility into its lifecycle. Webhooks are the foundation of a responsive, operationally sound integration. Without them, you must resort to repeatedly polling the API, which introduces latency and risks missing time-sensitive events. Rather than repeatedly polling the API for status updates, subscribe to webhooks for real-time event payloads as key state changes occur.

By subscribing to the appropriate set of webhook events, you can build event-driven workflows that react to transfer and funding state changes as they happen. Automatically update internal records, trigger downstream processes, surface real-time status to end users, and flag exceptions for review.

See the [Track third party transfers guide](/guides/product/send-money/use-cases/correspondent/correspondent-track-transfers) for details about the required and recommended webhooks for tracking third party transfers.

## Testing

Wise provides a sandbox environment with [simulation endpoints](/api-reference/simulation) to test key actions as you develop your integration. For testing correspondent partner integrations, Wise recommends the following:

- Use sandbox credentials and endpoints to test creating recipients, quotes, and transfers end-to-end.
- Validate corridor-specific behaviors, for example:
  - Recipient address requirements
  - Transfer purpose
  - BRL transfer nature on quotes
  - Blocking “global currencies”
- Test transfer tracking with state-change simulation endpoints and verify your webhook handler.
- If you fund from a balance, test balance debit webhooks and reconciliation workflows.


## Common pitfalls to avoid

We have found the most common situations causing issues with correspondent integrations to be:

- Using unauthenticated quotes for pricing. Always use authenticated quotes to reflect partner-specific pricing.
- Skipping the update quote step in quote-first flows after recipient selection.
- Allowing customers to select out-of-scope corridors or recipient types, leading to transfer creation failures.
- Hardcoding forms without a process to update corridor requirements when they change.
- Creating a standard transfer rather than a third party transfer.
- Omitting `originalTransferId` for idempotency on third-party transfer creation.