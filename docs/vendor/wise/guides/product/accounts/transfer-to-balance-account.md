# Transfer to balance account

There are two different ways you can transfer money to a multi-currency balance accounts:

1. Simply send domestic bank transfer from a bank account to **the balance account's bank account details** (e.g. IBAN, sort code & account number, etc.). There is no need to set up a quote/transfer in this case.


1) Create a quote/transfer and then fund that transfer as per requirements.


## Get multi-currency account recipientId 

Next, call [Check account balance](/api-reference/multi-currency-account/mcaget) endpoint and get the `recipientId` field value from the response.

Note that `recipientId` does not change so can be stored and reused.

## Create transfer 

Next, create a transfer. This is the same call as described in the [Transfer Create API Reference](/api-reference/standard-transfer/transfercreate), however the value for `targetAccount` should be the `recipientId` as determined from the previous step.

As per the standard create transfer flow, you also need to create and pass a `customerTransactionId` for idempotency.

## Fund transfer 

Once the transfer is created, a method will be required to fund the transfer. This will differ based on your specific integration.

### Fund transfer via PayNow

Region-specific funding methods such as PayNow for SGD are supported. To enable PayNow as a funding source for transfers to balance, contact your implementation team to request the required configuration be added to your integration.

Using the `payinSessionId` retrieved from the transfer, [create the PayNow details](/api-reference/payins/paynowcreate). This creates an encoded PayNow QR code which is returned along with manual payment details.

Display the decoded QR code to the customer in your app. Alternatively, the customer can make a manual PayNow transfer using the `virtualPaymentAddress`, `amount`, and `reference` values from the response. The reference field must be used exactly as returned — this is how Wise links the incoming PayNow payment to the transfer.

The customer scans the QR code or enters the details manually in their banking app and completes the PayNow transfer.

In order to simulate transfers in Sandbox, use the provided sandbox simulation API. [Simulate Transfers in Sandbox](/api-reference/simulation)