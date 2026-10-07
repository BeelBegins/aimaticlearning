Create and manage balance accounts within a multi-currency account.

Each profile can hold multiple balance accounts in different currencies. A `STANDARD` balance is limited to one per currency, while `SAVINGS` balances (Jars) allow multiple in the same currency. Creating the first balance for a profile automatically creates the multi-currency account.

Balances include an `investmentState` field. Only balances with `NOT_INVESTED` can be operated on via the API. Invested balances should be shown but not actionable.

For a complete guide on multi-currency accounts, see [Multi-Currency Accounts](/guides/product/accounts).