# Global Currencies

Global Currencies is a Wise product that allows customers to send currencies to countries other than the one they are domestic to. For example, sending US dollars to a person or business in Hong Kong, rather than the USA.

It is quite common, especially for businesses, to operate in USD, GBP or EUR despite being based outside of the respective country of these currencies. In some countries, these bank accounts do not use the standard account details that a domestic account would, for example an account number and sort code in UK. Instead, these accounts are more likely to be addressed using an IBAN.

The Wise Platform API supports this product in version 2 of the quotes API. The key difference this API provides against version 1 is the ability to update a quote with a recipient before a transfer is created, using the [Quote update](/api-reference/quote/quoteupdate) endpoint. If you set the ID of a recipient that represents an account of, for example, a USD recipient with an IBAN (an account with `"type": "swift_code"`) then the returned quote will be updated to represent that we will not be sending these funds domestically in the USA and as such charge different fees.

## Important caveats 

Global currencies are sent through the Swift network and will have multiple limitations. Wise has worked hard to reduce these as much as possible, but it's important to know the following:

### Unable to guarantee full amount

We cannot guarantee the full amount of the transfer will reach the intended recipient, regardless of the type of instruction (OUR or SHA). There is always a chance that a correspondent will remove a fee.

While the charging mechanism (OUR/SHA/BEN) is included and states the intention of the sending bank, it leaves two issues:

- Intermediary and recipient banks can and may ignore or not support the specific type.
- The instruction can get lost if the transfer ends up moving through a local scheme that doesn't support it.


This issue is a fundamental Swift issue. It is also a big part of why Wise exists as a company.

Wise has continuously worked to provide the best experience around global currencies that allows partners to properly inform customers as much as possible. The details below highlight how to best create transfers for Global Currencies, when and how we smart-select OUR vs SHA, and how you can override that logic if required.

When offering Global Currencies, you must be sure to display a message to customers that **there are potentially additional extra fees** for this type of transfer.

For example:

> To send this transfer, we need to use the Swift network, which is more expensive and slower than normal transfers. There may also be extra fees taken from the money by intermediary banks. We cannot guarantee the exact amount that will be received by your recipient for any of the instruction types with Swift.


## Creating global currency transfers 

There are three cases where we will use the Swift network to send a global currency transfer. These will be delineated by the type of recipient and currency of the transfer.

- A USD recipient of type `swift_code`
- A GBP recipient of type `iban` where the IBAN does *not* start with `GB`
- A EUR recipient of type `swift_code` where the IBAN does *not* start with one of the [SEPA country codes](https://wise.com/help/articles/2968880/sepa-countries-and-ibans) (the transfer is to a non-SEPA country).


To create a global currency transfer:

1. [Create a quote](/api-reference/quote/quotecreate) for the currencies you wish to send between, e.g. GBP to USD. If using Swift, ensure to set payOut to `SWIFT` which will give the best estimate on the fees charged for the transfer.
2. Based on the requirements set out in the [Recipient Account resource](/api-reference/recipient), create a recipient using the [account requirements](/api-reference/recipient/recipientaccountrequirementsget) endpoint.
3. [Update the quote](/api-reference/quote/quoteupdate) created in step 1 with the ID of the recipient created in step two.
4. You will now see the `payOut` field of the quote to have updated to be of type `SWIFT` or `SWIFT_OUR`, and the `paymentOptions` array to have all options updated to also have a `payOut` of type `SWIFT`, or `SWIFT_OUR` and different fees.


At this point, a full quote in a supported global currency with the correct recipient type patched is available. You should ensure that the updated information in the quote is communicated to the user. You should also take note of whether `SWIFT` or `SWIFT_OUR` will be used.

### Selecting SHA vs OUR

Wise automatically selects SHA or OUR based on aggregated data, previous transfer experience, and machine learning. This ensures that we accurately deliver the full amount of Global Currencies transfers 93%+ of the time, with only 37% of those being sent through OUR. It also ensures that this consistently gets better over time, and is something we consistently work to improve.

Following the steps above will ensure most transfers will be received in full without sacrificing fees to always push transfers via `OUR`.

#### Forcing SWIFT_OUR

In certain cases, partners will want to force the use of OUR with Swift. This is possible, however it must be configured by your implementation team, so please reach out if you would like this enabled.

Once configured, you will be able to supply `payOut` of type `SWIFT_OUR` when creating the quote. This will force the quote to be generated with fees and be processed as `OUR`.

## Refunds 

When a refund occurs, the refunded amount might be less than the original due to intermediary bank fees. Failing to read the correct refunded amount may result in reconciliation errors. The method to determine the exact refunded amount will vary depending on the settlement and refund model used.

### Bulk settlement

With bulk settlement, we offer two refund models:

#### Transfer-by-transfer

If you are using bulk settlement with the transfer-by-transfer refund model, you will need to subscribe to the `transfers#refund` webhook. When a transfer is refunded, you will receive a webhook notification with the updated status, followed by the actual refund being credited back to your account. To determine the final refunded amount, you should check your account balance. Note that the settlement journal does not need to include the refunded transfers.

#### Net-settlement

For those using the net settlement refund model, ensure you are subscribed to the `payout#create` webhook. The refund amount will be specified in the amount field. In the settlement journal, you only need to include the transfer reference in the refunds section, rather than the refund amount itself.

### Refund to balance

You will need to subscribe to the `balances#update` webhook to receive the actual refund amount in your balance. You can use the `transfer_reference` field to trace back to the transfer ID of the refunded transaction.

### Transfer-by-transfer

If you are using the transfer-by-transfer settlement model, you will need to subscribe to the `transfers#refund` webhook to receive the refund amount.