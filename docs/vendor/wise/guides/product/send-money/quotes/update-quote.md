# Update a quote 

It is important to update the quote before creating a transfer as fees and expected delivery times can change based on the recipient, payout method, or payment metadata.

For example, the fees and delivery estimate are different in the case of sending USD to a country other than the USA. We call this *Global USD*. Multiple factors can play into this, so it is important to complete this step.

Updating the quote ensures you can show the customer the correct final price and delivery estimate before they commit to creating and funding the transfer.

To [update a quote](/api-reference/quote/quoteupdate), you use the `PATCH` operation to add the `targetAccount`. This will update the saved quote's data based on who and where the money will be sent to.

Updating the quote with a recipient may cause the available payment options, prices, and estimated delivery times to change from the original quoted amounts. This is because sending some currencies to some destinations costs a different amount based on the payment network. For example sending USD to a country outside the USA uses international rather than domestic payment networks, and sending CAD over the Interac network are both more expensive operations.