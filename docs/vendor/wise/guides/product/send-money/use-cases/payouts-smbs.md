# Payouts for small-to-medium businesses (SMBs)

Wise business accounts can automate certain actions in the payout workflow using the Wise Platform API.

By generating a **personal API token** in your Wise business account, you can authorize your application to programmatically do the following:

- Generate quotes
- Collect and store recipient account details
- Prepare payments by drafting transfers
- Track transfer statuses


This guide explains how Wise business accounts can access the Wise Platform public API to automate parts of their payouts workflow. This information does not apply to accounts with partner agreements.

If you have a partner agreement, visit our [Enterprise payouts](/guides/product/send-money/use-cases/enterprise), [Correspondent payouts](/guides/product/send-money/use-cases/correspondent), or [Embedded payouts](/guides/product/send-money/use-cases/embedded) guides instead.

## Requirements

To access the Wise Platform API, you must:

- Have a Wise business account.
- Generate a personal API token.


## Features and limitations

**Not all Wise Platform API capabilities are available to accounts using a personal API token**. In most cases, such an account can perform only the following actions via API:

- Create authenticated quotes
- Create recipients
- Create transfers (either single transfers or batch groups)
- Track transfers via profile webhooks


Note that **funding** individual transfers and batch groups via API is not supported for most countries at this time.

However, business accounts in the **US, Canada, Australia, New Zealand, Singapore, and Malaysia**, can fund transfers via the API as well as retrieve account statements. *Please note that access to these API capabilities is subject to regional regulatory requirements that might change in the future.*

If you need more advanced access to the Wise Platform API, [contact our team](https://wise.com/platform/contact) to discuss the Enterprise Account partnership model.

## Create a personal API token

To generate a personal API token:

1. Log into your Wise business account.
2. Go to `Your Account` -> `Connect and manage apps` -> `API tokens`.
3. Choose **Add new token** (2-factor authentication required for this step).
4. Name the token and set the access level (full or read only).


Your account will generate the personal API token, which you can then use in the `Authorization` header of your API requests.

You can edit the token name and access level at any time, or delete the token if necessary.

## Automated payment flows examples

Automating your payment workflow requires building specific requests for your application to send to Wise in a certain order, with subsequent requests using values returned in responses from prior requests.

The examples included here link to the full API reference for the endpoints used in each step. Review the endpoint reference for details on what is required for each request and what to expect in each response.

### Individual transfer example

This example illustrates the steps required to create a single transfer for a new recipient:

1. [Create an authenticated quote](/api-reference/quote/quotecreate).
2. [Retrieve recipient account requirements](/api-reference/recipient/recipientaccountrequirementsget).
Use the data in the response to know which fields are required to create a valid recipient for the specific currency route.
3. [Create the recipient account](/api-reference/recipient/recipientcreate) using the required datapoints.
4. [Update the quote](/api-reference/quote/quoteupdate).
This updates the saved quote's data based on who and where the money will be sent to.
5. [Retrieve transfer requirements](/api-reference/transfer/transferrequirementsvalidate).
Use the data in the response to know which fields are required to create a valid transfer based on the sender, the specific quote, and selected recipient account.
6. [Create a transfer](/api-reference/standard-transfer/transfercreate).
7. Log into the Wise account to fund the transfer.


NEW! Recipient creation using embedded flows
Simplify the process to create a recipient by using the [recipient creation embedded flow](/guides/product/embedded-flows).

The recipient creation embedded flow allows you to redirect or embed Wise-hosted recipient creation forms directly into your application, reducing the engineering effort and decreasing your time to deployment.

#### Select existing recipients

For accounts that have previously created recipients, use the [List recipient accounts endpoint](/api-reference/recipient/recipientlist) to retrieve those recipient resources and allow the user to select an existing recipient rather than create a new one.

## Batch groups transfer example

Batch groups allow you to draft up to 1,000 transfers to fund in a single action, either via a transfer from an external bank account or from funds already held in the Wise account balance.

Creating batch groups follows nearly the same steps as the individual transfer example, with two key changes.

First, the [create a batch group](/api-reference/batch-group/batchgroupcreate) response returns an `id` value, which is required for each batch group transfer resource. **For each transfer that is included in the batch group**, follow the same steps for creating a quote, retrieving recipient requirements, creating a recipient, updating the quote, and retrieving transfer requirements.

Then, for the create transfer step, use the [create batch group transfer endpoint](/api-reference/batch-group/batchgrouptransfercreate) in place of the create standard transfer endpoint.

For each transfer you want to include in the batch group:

1. [Create an authenticated quote](/api-reference/quote/quotecreate).
2. [Retrieve recipient account requirements](/api-reference/recipient/recipientaccountrequirementsget).
3. [Create the recipient account](/api-reference/recipient/recipientcreate) using the required datapoints.
4. [Update the quote](/api-reference/quote/quoteupdate).
5. [Retrieve transfer requirements](/api-reference/transfer/transferrequirementsvalidate).
6. [Create the batch group transfers](/api-reference/batch-group/batchgrouptransfercreate).
Use the `id` value returned in the response as the `batchGroupId` value in the endpoint path. The body of the request is the same as the request body for the [Create transfer endpoint](/api-reference/standard-transfer/transfercreate).


Once your batch group is complete, log into your Wise.com account to fund the batch group.

### Tracking transfer status

To track the statuses of your transfers, [create a profile webhook subscription](/api-reference/webhook/webhookprofilesubscriptioncreate) that triggers on the `transfers#state-change` [event type](/api-reference/webhook-event/eventtransfersstatechange).

To receive all state change event notifications for a transfer, be sure to create the webhook subscription prior to initiating the transfers you wish to track.

## Funding via API

Business accounts in the **US, Canada, Australia, New Zealand, Singapore, and Malaysia** are not required to log into their Wise account to fund transfers. These accounts can fund transfers and retrieve statements via the API using the following endpoints:

- [Fund individual transfers](/api-reference/transfer/transferfund)
- [Fund batch group transfers](/api-reference/batch-group/batchgroupfund)
- [Get balance statements](/api-reference/balance-statement/balancestatementget)