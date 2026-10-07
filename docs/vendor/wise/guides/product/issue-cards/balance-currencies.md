# Manage multi-currency balances

When your customers use their cards abroad or with international merchants, they may receive refunds or credits in currencies they don't yet hold a balance in.

Each card issued through Wise is linked to a Multi-Currency Account (MCA) that supports a wide range of currencies. When a refund or credit arrives in a new currency, Wise automatically creates a balance in that currency for the customer's account.

To provide the best experience for your customers and ensure your integration works seamlessly, we recommend that you support currencies outside your core set.

## Handling refunds in new currencies

When a customer receives a refund in a currency they don't yet hold a balance in, a new balance is created automatically.

To handle this gracefully, we suggest:

- Notifying your customer that they have received funds in a new currency.
- Giving the customer options to manage the funds:
  - Keep the balance and spend it directly in future transactions.
  - Convert the funds to another currency of their choice. You can use the [convert balance endpoint](/api-reference/balance/balancemovement) to perform the conversion. Note that standard conversion fees will apply.


## Restricting balance currencies

To restrict the balance currencies for an account, Wise can limit the currencies in which refunds are credited and use an alternative currency provided by the card scheme, applying the exchange rate supplied by the scheme.

If you would like to limit which currencies your customers can hold a balance in on their account, contact your account manager.

### How refund currency is resolved

When processing a card refund, the card scheme provides amounts in up to three currencies:

- **Transaction currency**: The currency the merchant used for the original transaction. This is typically the local currency of the merchant or the price currency shown to the customer.
- **Card billing currency**: A fixed currency configured for the card during integration setup, agreed between you and Wise as part of onboarding.
- **Settlement currency**: The currency used to settle between the card scheme and Wise. The settlement allows a set of currencies and the specific one used may vary from transaction to transaction.


Wise credits the refund using the following logic:

1. If the transaction currency is supported, the refund is credited in the transaction currency.
2. If the transaction currency is restricted, we fall back to the card billing currency.
3. If the billing currency is also restricted, we fall back to the settlement currency.


To ensure refunds are processed in one of your supported currencies, your integration must support the card's billing currency.

To enable this currency restriction or discuss your specific use case, contact your account manager for guidance.

## BRL limitations

When a transaction involves BRL, the following limitations apply:

- BRL as billing currency: Fallback to billing currency (for non-BRL transactions) is not allowed.
- Non-BRL as billing currency (for cards issued in Brazil): Even if BRL purchases are blocked, customers may still receive BRL refunds.


Your integration UX must support handling these refund scenarios.