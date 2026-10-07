# Configure authorisation rules

Using our [spend control APIs](/api-reference/spend-controls), you can block or allow transactions based on the MCC (merchant category code) or the currency of the transaction.

Currency codes follow the ISO-4217 standard, please refer to [iban.com](https://www.iban.com/currency-codes).

Note that the MCC list is based on [Visa](https://usa.visa.com/content/dam/VCOM/download/merchants/visa-merchant-data-standards-manual.pdf) or [Mastercard](https://www.mastercard.us/content/dam/public/mastercardcom/na/global-site/documents/quick-reference-booklet-merchant.pdf) schemes.

Spend controls are scoped at the application level. Meaning that the [client credentials token](/api-reference/oauth-token/oauthtokencreate) will be required to call these APIs

### Blocking a type of transaction

1. Identify the MCC or currency to block. For example, block gambling transactions - MCC `7995`.
2. [Create an authorization rule](/api-reference/spend-controls/spendcontrolsrulecreate) with the following:
  - `type` as `MCC`
  - `operation` as `BLOCK`
  - `values` as `[7995]`
  - `description` as `block gambling MCC 7995` (optional)
3. [Retrieve the authorization rules](/api-reference/spend-controls/spendcontrolsruleslist) to see that the rule has been created.
4. [Apply the rule](/api-reference/spend-controls/spendcontrolsruleapply) to start blocking transactions


An `ALLOW` rule permits only the transactions that match the specified criteria and blocks all others. For instance, a rule allowing `SGD` transactions will block all transactions that are not in `SGD`"