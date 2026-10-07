# Transfers

Once you've created a quote and recipient, you need to:

1. [Check the transfer requirements](/guides/product/send-money/transfers#transfer-requirements): Each currency, region and market may require different information. This check ensures you have everything needed to create the transfer.
2. [Update the quote](/guides/product/send-money/quotes/update-quote): This allows you to include additional payment or recipient information and ensure final cost is as accurate as possible.


## Transfer requirements 

Each transfer can have additional requirements before you can process the transfer. To determine the transfer requirements, your application should use the [transfer requirements endpoint](/api-reference/transfer/transferrequirementsvalidate) to request the requirements for the transfer.

Requirements are returned in a dynamic form, with form types, restrictions, and validation included in a consistent method. This allows your application to present these to users in a consistent way.

Once all transfer requirements have been gathered, they should be added to the `details` object of the create transfer request.

For full details about the request, see the [request transfer requirements API reference](/api-reference/transfer/transferrequirementsvalidate).

## Transfer creation

Different integration types will require different transfer types. All transfers may require additional transfer requirements, which should be requested and captured before creation of the transfer.

Once ready to create a transfer, your application should use one of the following transfer creation types:

Standard transfers
Create and manage transfers over API, either from your own Wise account or on behalf of your customers.

Third party transfers
Create and manage transfers over API on behalf of your customers, under your own financial license.

Swift network transfers
For transfers via the Swift network, typically by banks and financial institutions with a Swift or BIC code.

Only one type of transfer will be made available to your integration, with others resulting in a `403 - Unauthorized` response. If you feel this is incorrect, please speak with the Wise team.