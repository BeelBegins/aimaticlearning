# Convert from balance to balance

Converting funds from one balance account to another occurs in two parts. It's easiest to think of it as a transfer, with a standard quote being required first, and then the funding being made from balance to a balance.

To complete the transfer, follow these two steps:

1. [Create a quote](#create-quote) - Use the quotes api to generate a quote for the transfer between balance accounts.
2. [Execute the quote](#execute-transfer) - Approve the transfer and execute it.


## Create a quote 

To begin the process of converting funds from one balance account to another, you first need to generate a quote. Please review the full [Quote Create API Reference](/api-reference/quote/quotecreate)  for specific details.

Creating the quote will require input data that includes the source and target currency, the amount of either the source or target, and the payout of `BALANCE`. If you supply both source and target amounts, the call will fail.

The returned quote will return multiple payout options, with one having a value for `payIn` and `payOut` of `BALANCE`. If the profile does not have a balance account in each of those currencies, then this option will be returned with `"disabled": true`.

The balance to balance option contains further details on the cost of the conversion, including the fees included and either the final source or target amount.

The quote will also contain the `rate`, which will be locked for 30 minutes to give time to create the transfer, after which the rate lock is extended.

## Execute the transfer 

Once a quote is generated, you are able to execute that transfer from one balance to the other. This endpoint converts funds between those balance accounts using the quoteId.

Please review the full [Balance Conversion API Reference](/api-reference/balance/balancemovement) for specific details.

Please also note that this call needs an extra field in the header called "X-idempotence-uuid". This should be generated and used for any subsequent retry call in the case that the initial `POST` fails.