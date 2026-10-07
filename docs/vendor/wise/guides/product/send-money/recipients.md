# Recipients

Before creating a transfer, your application needs to allow users to choose who will receive the funds. The receiving entity is often referred to as the recipient or beneficiary.

In your application, you can have your customer select a previously created recipient or they can create a new one. The data needed to create a new recipient is dependent on multiple factors, so we recommend using our dynamic forms option to ensure you gather all the required data.

You'll use the recipient account ID as the `targetAccount` value when creating a transfer as well as a quote.

## List current recipients

Each profile contains a list of active recipients that the user has previously sent funds to. To present a list of recipients to the user, [retrieve the list of recipients](/api-reference/recipient/recipientlist).

If you have already created a quote, use the `currency` query parameter to filter the response by the quote currency. Then, once the user selects a recipient, [update the quote](/api-reference/quote/quoteupdate) with the selected recipient.

Always load a fresh set of recipient details from the Wise API when displaying a list or specific information about the recipient.

## Create new recipient

When creating a new recipient, the required data needed is influenced by many factors, such as the currency pair, where the account is based, the amount of the transfer, and more. Additionally, regional regulatory situations can sometimes cause recipient account requirements to change over time.

To make recipient creation more manageable, Wise provides **dynamic forms** that work in a predictable and functional way, ensuring you always gather the data needed. This feature uses a single endpoint to retrieve requirements that you can then display to your users.

The [Retrieve recipient requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget) explains how to retrieve the account requirements, display and validate the data, and collect additional data when necessary. You can see this pattern in action in the [account requirements dynamic form demo](/guides/product/send-money/recipient-verification/account-requirements).

Once the user has provided all required details, submit the [Create recipient account request](/api-reference/recipient/recipientcreate).

Dynamic forms recommended
Using dynamic forms to gather recipient requirements is highly recommended for all integrations. Dynamic forms ensure your application always has the most up-to-date set of requirements for creating recipients, resulting in fewer errors.

Not using dynamic forms may result in your integration breaking upon a recipient requirements change, with your customers no longer able to create or update that type of recipient. For help implementing dynamic forms, speak with your Wise implementation team.

## Recipient validation and verification

Wise validates the data submitted when creating a recipient to ensure it conforms to the required schema and regional formatting rules (for example, account length and format).

For certain currencies, additional verification checks occur to confirm the existence of the account and that the recipient's account number and name match the records held by the destination bank.

This level of verification helps confirm the recipient of a transfer is the correct and intended beneficiary. Review our [Recipient verification guide](/guides/product/send-money/recipient-verification) to learn more about how Wise recipient verification works and how to handle different verification outcomes.