# Funding a transfer

Once you've created a transfer, it needs to be funded. Wise offers several methods to fund transfers and settle the funds owed.

Once you have successfully created a transfer, the correct amount should be funded to the transfer as soon as possible. This ensures that any FX rates do not expire, which can result in the target amount changing. The correct amount to fund is always the amount provided in the [final quote object](/api-reference/quote/quoteupdate) after any recipient updates. Certain funding options take care of this for you automatically.

Once the settlement funds are received, the transfer status will change from `incoming_payment_waiting` to `processing`.

## Funding options 

Wise provides multiple options for funding transfers:

- Direct bank transfer (push)
- Direct debit bank transfer (pull)
- Fund from balance
- Bulk settlement


### Direct bank transfer (push)

A direct bank transfer sends the funds directly from the customer's account to our bank account in your currency. Below describes the direct transfer by transfer funding mechanism.

For Wise to connect an incoming domestic payment with a corresponding transfer order, the individual creating the external push of funds must include specific text in the "payment reference" field. Get the `transfer id` for the transfer you want to fund and append the letter `T` as a prefix. For example, a transfer with ID `80106743` will use `T80106743` in the "payment reference" field. Include this string in the reference when sending the funds to Wise's bank account.

For a full reference, see the [retrieve bank transfer deposit details for a transfer](/api-reference/payin-deposit-detail/payindepositdetailget) API reference.

### Direct debit bank transfer (pull)

In certain countries and currencies, Wise offers the ability to fund transfers via direct debit. This requires creating a direct debit account with Wise on a profile and then instructing us to pull funds from that account.

This option is only available to select partners. If you are interested in this model,  get in touch with the Wise team to discuss the option and for technical documentation on how it works.

### Fund from Wise balance

Wise accounts can hold funds in a balance, and these funds can be used to fund a transfer directly. To do so, a transfer must be created in the currency of the balance  used to fund it. We currently do not support cross-balance funding.

For a full reference, see the [fund a transfer from balance](/api-reference/transfer/transferfund) API reference.

### Bulk settlement

Wise offers a "prefunded" model for partners who want to speed up transfers for their customers in regions where the domestic payment networks are slow or otherwise do not allow for instant funding. If you are interested in this model, get in touch with the Wise team to discuss the option and for technical documentation on how it works.

## Testing funding 

There are some differences between the Sandbox and Production environments. Please keep these in mind as you test.

We provide a [balance top-up simulation endpoint](/api-reference/simulation/simulationbalancetopup) to top up your balance if you want to test funding a transfer from balance.

It is possible to test funding via bulk settlement, but you'll need a configuration. Contact the Wise team for assistance if you'd like to test this.

Speak with the Wise team if you have further questions about testing funding.