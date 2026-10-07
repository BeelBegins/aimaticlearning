# Set up to receive payments

Before you can receive incoming transfers, you need account details that senders can pay into. There are two models depending on your use case. Once either model is configured, all incoming payments are surfaced through the same [`incoming-transfer#credited`](/guides/product/receive-money/incoming-transfer-notifications) webhook event and the [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer), regardless of the originating payment rail.

## Wise-issued account details

Wise can issue local account details (e.g. IBAN, sort code and account number, routing number) for your customers' balances. Senders pay into these details over local rails such as SEPA, Faster Payments, and ACH.

To order and manage account details, follow the [bank account details guide](/guides/product/accounts/bank-account-details). Once issued account details reach `ACTIVE` status, any incoming payment sent to those scheme credentials will generate an `incoming-transfer` resource and trigger an `incoming-transfer#credited` notification.

## International Receive (BIC connection) 

International Receive uses a correspondent banking model where your own SWIFT BIC is used to receive payments into Wise on behalf of your customers. When a sender initiates a SWIFT payment using your BIC, it will arrive at Wise and be credited to your balance, generating an `incoming-transfer` resource in the same way as local scheme payments.

### Connect your BIC through our implementation team 

You cannot connect your BIC via our API, but your Wise implementation partners can help ensure this is set up correctly for you. All you need to do is provide us with the BICs you would like us to match and use to deposit funds into your Wise account.

This can be a list of specific BICs or can be based on a "starts with" match.

For example, if we configure `BANKDE12`, any branch code will also be matched, such as `BANKDE12XXX`. If you would like us to match specific branch codes, those should be provided.

### Provide an unused BIC for testing 

Due to the length of time it can take for the SWIFT network to update the standing settlement instructions for BICs, you should provide a BIC to be used for testing.

This should never be a BIC that is in use by your customers or in production. Often this is a separate BIC that is unused or reserved for testing.

Speak with your implementation manager further about this and when it is applicable to make this change.

## Next steps 

* [Subscribe to the `incoming-transfer#credited` webhook](/guides/product/receive-money/incoming-transfer-notifications) to be notified when funds are credited to your balance.
* Use the [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer) to retrieve full payment, sender, and clearing details for each credited transfer.
* Test your configuration in the [Wise Platform sandbox environment](/guides/product/receive-money/test-and-go-live).