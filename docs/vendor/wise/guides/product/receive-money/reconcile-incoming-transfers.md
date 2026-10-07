# Reconcile incoming transfers

You can reconcile incoming transfers with actual balance changes using the [get balance statement endpoint](/api-reference/balance-statement/balancestatementget). Balance statements contain a `referenceNumber` field which can be used to get an incoming transfer via the [incoming transfer endpoint](/api-reference/incoming-transfer).

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For full endpoint details, see the [balance statement endpoint](/api-reference/balance-statement) in the full API reference.