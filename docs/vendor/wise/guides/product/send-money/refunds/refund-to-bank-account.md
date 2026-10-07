# Refund to sender bank account

This refund method most often applies to partners using the [direct bank transfer (push)](/guides/product/send-money/funding#direct-bank-transfer-push) funding model. However, some partners on the [fund from balance](/guides/product/send-money/funding/fund-from-balance) model may be configured for the refund to bank account method.

## How it works

When a transfer is cancelled after it has been funded, Wise sends the refund to the sender's original pay-in account using local payment rails at the standard speed for that currency.

Wise determines the refund destination account using one of the two following methods:

- Pulling it from the original bank transaction that funded the transfer.
- Using the [refund recipient](/api-reference/recipient/recipientcreate) supplied in the transfer request body `sourceAccount` field.


## Using a refund recipient

You'll need to specify a refund recipient in the transfer request in the following scenarios:

- You want the refund destination to differ from the account that funded the transfer.
- Funds are sent using a slow domestic payment network. In this case, proactively sharing the bank details of the funding bank account gives Wise the refund destination account when we can't reliably pull it from the transaction itself.


For either scenario, provide the refund recipient ID in the `sourceAccount` field of each transfer request body.

**Transfer example request:** Refund recipient ID in sourceAccount

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/transfers \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceAccount": 12345678,
    "targetAccount": 8692237,
    "quoteUuid": "8fa9be20-ba43-4b15-abbb-9424e1481050",
    "customerTransactionId": "54a6bc09-cef9-49a8-9041-f1f0c654cd88",
    "details": {
      "reference": "Invoice 2026-001"
    }
  }'
```

To create a refund recipient, use the [Create recipient account](/api-reference/recipient/recipientcreate) endpoint and include `refund=true` as a query parameter in the request. The `id` returned in the response is the refund recipient ID.

The account used for the refund recipient resource must be owned by the sender.

If Wise cannot confirm account ownership, the refund may be delayed or held pending proof of ownership (for example, with a bank statement). If the receiving bank cannot match the refund to the account holder, it may reject the payment entirely.

## Detecting a refund

With this refund method, Wise automatically refunds the sender account. However, you may want to detect when a refund has occured so you can notify your customer or trigger other automated processes.

Subscribe to the following webhook events to ensure you receive relevant notifications about refunds.

| Webhook event  | Description |
|  --- | --- |
| `transfers#refund` | Provides the refund amount and currency.

Note that for Swift partial refunds, the refund amount may be less than the original transfer amount due to intermediary bank fees. |
| `transfers#state-change` | Reflects the current transfer status.

The `cancelled` and `funds_refunded` states are the most relevant for refunds.- If a transfer is cancelled after being funded, it is most likely a refund.
- When the transfer state moves to `funds_refunded`, this means Wise has sent the refund. *Note that we cannot detect if or when the funds actually arrive in the destination bank account.*

 |
| `transfers#payout-failure` | Provides the specific reason for a payout failure (for example, incorrect account details). |


### Sample webhook payloads

Transfer refund
```json
{
  "data": {
    "resource": {
      "type": "transfer",
      "id": 111,
      "profile_id": 222,
      "account_id": 333,
      "refund_amount": 5000,
      "refund_currency": "EUR"
    },
    "occurred_at": "2024-01-01T12:34:56.789Z"
  },
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#refund",
  "schema_version": "4.0.0",
  "sent_at": "2024-01-01T12:34:56.123Z"
}
```

Transfer state change
```json
{
  "data": {
    "resource": {
      "type": "transfer",
      "id": 111,
      "profile_id": 222,
      "account_id": 333
    },
    "current_state": "processing",
    "previous_state": "incoming_payment_waiting",
    "occurred_at": "2020-01-01T12:34:56.789Z"
  },
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#state-change",
  "schema_version": "4.0.0",
  "sent_at": "2020-01-01T12:34:56.123Z"
}
```

Payout failure
```json
{
  "data": {
    "transfer_id": 111,
    "profile_id": 222,
    "failure_reason_code": "WRONG_ID_NUMBER",
    "failure_description": "Invalid recipient's ID document number",
    "occurred_at": "2023-08-10T10:17:23.123Z"
  },
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#payout-failure",
  "schema_version": "4.0.0",
  "sent_at": "2023-08-10T10:17:28.123Z"
}
```