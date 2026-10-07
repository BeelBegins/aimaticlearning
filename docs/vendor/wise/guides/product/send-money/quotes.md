# Quote creation

Get FX transfer rates, fees, and delivery estimates.

Use the [quotes endpoints](/api-reference/quote) to check FX rates, fees, and delivery estimates, enabling seamless money transfers with Wise Platform.

Sending money with Wise Platform begins with the creation of a quote.

A quote defines:

- Which currencies are involved.
- How much to send or receive.
- Who is sending and receiving the money.


The response includes:

- The rate and any fees.
- Estimated delivery speed.
- Available methods to fund the transfer.


## Quote types

You can create two types of quotes:

Unauthenticated Quotes
`POST /quotes` *(optional)*  
**Purpose:**

-   - Optional to offer fast estimates for illustration
-   - No Auth or ProfileID needed
-   - But can’t be used to create real transfers


Authenticated Quotes
`POST /profiles/{profileId}/quotes`  
**Purpose:**

-   - Required to create a real transfer
-   - Must be associated with profile
-   - Needs updating with recipient for accurate fees


Providing payin and payout details improves the accuracy of the quote.

### Authenticated vs unauthenticated quotes

| Feature | Authenticated | Unauthenticated |
|  --- | --- | --- |
| **Authentication** | Required (OAuth 2.0) | Optional |
| **Profile ID** | Required | Not applicable |
| **Quote ID** | Generated | Not generated |
| **Can create transfer** | ✅ Yes | ❌ No |
| **Rate locking** | Available | Not available |
| **Use case** | Real transactions | Display/marketing |
| **Rate limits** | More restrictive | More permissive |


## The quote flow

Creating a quote for a transfer involves 2-3 steps.

Configure pricing 
(Optional) Allows you to override pricing per quote via pricing configuration.

Most partners can skip this step.

Create a quote
Provide a profile ID (the account sending the money), the currencies, and either the amount to send or to receive.

Add the recipient
Update the quote to include the transfer recipient. This ensures you have accurate fees and delivery estimates.

The mid‑market exchange rate is locked when the authenticated quote is created and typically remains valid for 30 minutes, giving your customer time to complete the flow.

## Quote response fee and price objects

The quote response includes `fee` and `price` objects for each payin option. They provide a summary and detailed views of the fees to be charged on the transfer.

- The `fee` object gives a summary of the fees.
- The `transferwise` fee includes any taxes or fees that Wise charges.
- Additional fields, such as `payIn`, `discount` and `partner`, include any amounts as applicable.
- The `total` field sums all fees and discounts for that payment option.
- The `price` object further enumerates the fees and discounts as line items. This includes any discounts, fees, or taxes and gives the appropriate name for each.


Any transfer **to or from BRL** will always include an IOF Tax fee, which is collected during the transfer funding process. This should be shown to your customers as a distinct line item separate from all other fees.

## Testing quotes in sandbox

The sandbox provides realistic but not live rates, so the quote you receive when you test may differ from what is available in the production environment.

In the sandbox, you cannot test a `rateType` of `FLOATING`.

Speak with the Wise team if you have further questions about testing quotes in the sandbox.