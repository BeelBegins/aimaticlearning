# Create a custom receipt

This guide will walk you through how to create a custom transfer receipt that can be shared with your customers. Generally, this includes the following steps:

- Make a request to `GET /transfers/{{transferId}}` to fetch the transfer details.
- Make a request to `GET /transfers/{{transferId}}/invoices/bankingpartner` to fetch the banking partner details.
- Combine the information from both responses to create a custom transfer receipt.


## Get a transfer by ID

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/transfers/{transferId}' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For a complete reference, see the [Get a transfer by ID](/api-reference/transfer/transferget) endpoint.

## Get payout information

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/transfers/{transferId}/invoices/bankingpartner' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

The transfer must have reached the `processing` or later state (in most cases, this takes only a few seconds) for this endpoint to return data, otherwise it will return a `404` error.

For a complete reference, see the [Get payout information](/api-reference/transfer/transferpayoutinfoget) endpoint.

## Creating the custom transfer receipt 

Once you have fetched the transfer details and banking partner details, you can combine the information to create a custom transfer receipt. The custom transfer receipt should include the following information:

- Sender details (name and account number)
- Recipient details (name and account number)
- Amount transferred
- Currency
- Status of the transfer
- Date and time of transfer creation
- Processor name
- Delivery mode
- Banking partner reference
- Banking partner name
- MT103


With this information, you can format the transfer receipt in a manner that suits your needs and preferences. You can create a PDF, HTML, or plain text receipt, and share it with your customers via email or other communication channels.