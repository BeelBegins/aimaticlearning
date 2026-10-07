# Batch transfers

Many of our partner’s customers need to make multiple payments at once. For instance, they may want to pay all their monthly bills or they may already be used to doing monthly or quarterly payment runs.

Batch Groups enable partners to group up to 1000 transfers under a single reference, this means that all the payments within the batch group can be funded at once.

Follow the guide below to understand more about how batch groups work, how to create a group, add transfers, and funding the batch once closed.

Batch Transfers Postman Collection
## The batch group resource 

Many Batch Group API endpoints return a *batch group resource*. See the [BatchGroup schema](/api-reference/batch-group/batchgroup) for full details on the structure and fields.

### Batch group statuses

| Status | Description |
|  --- | --- |
| `NEW` | New batch group with zero or more transfers. Able to have more transfers added to it. Any transfers in a `NEW` group cannot yet be funded and paid out. |
| `COMPLETED` | The batch group has had all the desired transfers added to it and is now closed to further changes. The transfers in the group are now able to be funded and paid out. Note: `COMPLETED` does not imply that payouts have been successfully completed. |
| `MARKED_FOR_CANCELLATION` | Cancellation of the transfers in the batch group was requested. |
| `PROCESSING_CANCEL` | Transfers in the group are being cancelled. |
| `CANCELLED` | Transfers in the group have been cancelled. |


### Pay-in details

Pay-in details describe how the batch group can be funded. They are only populated when a batch group is in the `COMPLETED` state. See the [PayInDetails schema](/api-reference/batch-group/batchgroup#path=payindetails) for full details.

## Create a batch group 

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/12345678/batch-groups \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "GBP",
    "name": "My batch group"
  }'
```

For request/response details, see the [API reference](/api-reference/batch-group/batchgroupcreate).

## Create a batch group transfer 

Create a transfer in the batch group, using a previously created recipient account and quote.
Please see [quote creation](/api-reference/quote/quotecreate) and [recipient account creation](/api-reference/recipient/recipientcreate) documentation.

For the request body format please see [transfer creation](/api-reference/standard-transfer/transfercreate).

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/12345678/batch-groups/54a6bc09-cef9-49a8-9041-f1f0c654cd88/transfers \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "targetAccount": 67890,
    "sourceAccount": 12345,
    "quoteUuid": "bd244a95-dcf8-4c31-aac8-bf5e2f3e54c0",
    "customerTransactionId": "a]1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "details": {
      "reference": "to my friend",
      "transferPurpose": "verification.transfers.purpose.pay.bills",
      "transferPurposeSubTransferPurpose": "verification.sub.transfers.purpose.pay.interpretation.service",
      "sourceOfFunds": "verification.source.of.funds.other"
    }
  }'
```

For request/response details, see the [API reference](/api-reference/batch-group/batchgrouptransfercreate).

## Complete a batch group 

Completes the batch group and allows funding to proceed. Note: this action prevents any further modification.

```shell curl
curl -i -X PATCH \
  https://api.wise.com/2026Q4/profiles/12345678/batch-groups/54a6bc09-cef9-49a8-9041-f1f0c654cd88 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "status": "COMPLETED",
    "version": 1234
  }'
```

For request/response details, see the [API reference](/api-reference/batch-group/batchgroupupdate).

## Fund a batch group 

Once the batch group is completed, you can fund all transfers at once. There are two funding options available: from your multi-currency account balance, or via direct debit from a linked external bank account.

### From balance 

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/12345678/batch-payments/54a6bc09-cef9-49a8-9041-f1f0c654cd88/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "BALANCE"
  }'
```

For request/response details, see the [API reference](/api-reference/batch-group/batchgroupfund).

### Via direct debit 

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/12345678/batch-groups/54a6bc09-cef9-49a8-9041-f1f0c654cd88/payment-initiations \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "DIRECT_DEBIT",
    "accountId": 1,
    "reference": "B1234567"
  }'
```

For request/response details, see the [API reference](/api-reference/batch-group/batchgrouppaymentinitiationcreate).

#### Retrieve a payment initiation 

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/profiles/12345678/batch-groups/54a6bc09-cef9-49a8-9041-f1f0c654cd88/payment-initiations/12345 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/batch-group/batchgrouppaymentinitiationget).

## Retrieve a batch group 

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/profiles/12345678/batch-groups/54a6bc09-cef9-49a8-9041-f1f0c654cd88 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/batch-group/batchgroupget).