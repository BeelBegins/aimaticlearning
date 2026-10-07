# Create standard transfers

Create and manage transfers over API, either from your own Wise account or on behalf of your customers.

## Create a transfer request 

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/transfers \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "targetAccount": 8692237,
    "quoteUuid": "8fa9be20-ba43-4b15-abbb-9424e1481050",
    "customerTransactionId": "54a6bc09-cef9-49a8-9041-f1f0c654cd88",
    "details": {
      "reference": "Invoice 2026-001"
    }
  }'
```

For a complete reference, see the [Create a transfer](/api-reference/standard-transfer/transfercreate) endpoint.