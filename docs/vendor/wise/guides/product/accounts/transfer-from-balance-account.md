# Transfer from balance account

Transferring from a balance follows the exact same flow as a standard transfer, with the exception being that it is funded from balance.

The steps below illustrate the flow required to create a quote, recipient, and transfer. Once the transfer is created, it can then be funded from the balance account

## Generate transfer 

Follow the guides below to create a quote, recipient, and transfer as per the usual flow.

* [Quote API](/api-reference/quote/quotecreate)
* [Recipient API](/api-reference/recipient)
* [Transfer API](/api-reference/standard-transfer/transfercreate)


## Fund a transfer 

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/transfers/16521632/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "BALANCE",
    "balanceId": 45678901
  }'
```

For a complete reference, see the [Fund a transfer](/api-reference/transfer/transferfund) endpoint.