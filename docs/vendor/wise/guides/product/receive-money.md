# Receive money

Wise Platform enables your customers to receive transfers from around the world over supported payment rails including Swift, SEPA, Faster Payments, and ACH. Transfers are credited to your Wise balance, and you can then send the money to your customers according to your business needs.

Wise Platform image
## How it works 

Before you can receive transfers, you must set up your account details for the currencies you plan to receive. This step can be completed with help from your implementation team at Wise. Refer to the [Setup guide](/guides/product/receive-money/setup) for more information.

Wise Platform provides a unified API and webhook mechanism for handling incoming transfers across all supported currencies and payment rails — including [Local Account Details](/guides/product/accounts/bank-account-details) (SEPA, Faster Payments, ACH, domestic wire) and international Swift transfers. Regardless of the originating payment rail or currency, all incoming transfers are represented through the same `incoming-transfer` resource and notified via the same webhook event type.

Once your currencies are set up, the process of handling incoming transfers with Wise Platform looks like this:

1. A debtor directs a transfer to your Wise account details using the appropriate scheme credentials (Swift BIC and IBAN, local sort code and account number, ACH routing and account number, etc). As the money hits your balance, you receive an [`incoming-transfer#credited`](/guides/product/receive-money/incoming-transfer-notifications) webhook notification from Wise Platform. This event signals that funds have been credited and includes the `data.incoming_transfer_id` you need to retrieve full transfer details.
2. Using the `data.incoming_transfer_id` from the webhook, call the [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer) to fetch the complete transfer record, including:
  * The credited amount and currency.
  * Debtor and debtor bank details (name, address, account identifiers).
  * Clearing and regulatory identifiers (LEI, Clearing System Member ID).
  * The specific account details that received the payment, which you use to identify which of your customers the transfer is associated with.
  * Other details depending on the transfer type. Refer to [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer) for the full response schema.


1. Once the funds are in your account and you have identified the recipient customer, you can send the money to your customer using Wise Platform's API, or proceed according to your business arrangements.


Once the funds are credited to your balance, the receive flow is complete. Any subsequent money movement — such as sending funds to your customer, performing a sweep, or holding — is managed separately through the relevant Wise APIs, and should be reconciled independently.

If you are currently using legacy webhook events such as `swift-in#credit`, `transfers#state-change`, or `balances#update` to detect incoming payments, you should migrate to `incoming-transfer#credited`. This event unifies payment signals across both local scheme pay-ins and international Swift transfers into a single integration point, and provides a consistent resource model for all incoming transfer types.

## Next steps 

* If you are new to Wise Platform, use the [Getting started resources for developers](/guides/developer) to get ready to create and test any API integration.
* Learn how to [handle the business process for receiving transfers](/guides/product/receive-money/setup), including how to connect your BIC and share your account details.
* [Subscribe to the `incoming-transfer#credited` webhook](/guides/product/receive-money/incoming-transfer-notifications) to be notified when funds are credited to your balance.
* Use the [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer) to retrieve full payment, debtor, and clearing details for each credited transfer.


* Test your build in the [Wise Platform sandbox environment](/guides/product/receive-money/test-and-go-live).