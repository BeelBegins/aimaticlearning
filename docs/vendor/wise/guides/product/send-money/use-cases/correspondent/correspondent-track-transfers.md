# Track third party transfers

Use webhooks to keep transfer statuses and delivery estimates up-to-date.

Use **webhooks** as the primary mechanism to keep your system in sync with Wise transfer status changes.

By subscribing to the appropriate set of webhook events, you can build event-driven workflows that react to transfer and funding state changes as they happen. *Note that transfers are processed asynchronously*.

To keep your app and back-office systems in sync with Wise:

1. Subscribe to transfer tracking and funding-related webhooks.
2. Persist Wise `transferId` values and correlate them with your internal transfer identifiers.
3. Refresh delivery estimates when a transfer’s state changes. Use the **delivery estimate endpoint** to retrieve up-to-date ETA and show to your customer.


## Requirements

- Store the Wise `transferId` returned when you create the transfer. You’ll use it to fetch delivery estimates and correlate webhooks.
- Expose a **public HTTPS** endpoint that can receive `POST` requests from Wise webhooks.
- Return **HTTP** `200` quickly from your webhook handler (process asynchronously), otherwise Wise will retry delivery.


Webhook ordering is not guaranteed
Webhook events may not be delivered in the order they occurred. Use `data.occurred_at` to reconcile ordering. See the [Event ordering guide](/guides/developer/webhooks/event-ordering) for more details.

## Subscribe to tracking webhooks

For correspondent partners, subscribe to each event you want to track using the [Create application webhook subscription](/api-reference/webhook/webhookapplicationsubscriptioncreate).

### Create subscription request

| Field  | Required? | Description |
|  --- | --- | --- |
| `clientKey` | Yes | Path parameter. Your client key from [Developer Hub](https://wise.com/developer-hub). |
| `Authorization` | Yes | Header.

`Bearer <CLIENT_CREDENTIALS_ACCESS_TOKEN>` |
| `name` | Yes | Your label for the subscription (for example, `"Transfer status updates"`). |
| `trigger_on` | Yes | Event type to subscribe to (for example, `transfers#state-change`). Each subscription triggers on a specific event. To subscribe to multiple events, create multiple subscriptions, one for each event for which you want to receive notifications. |
| `delivery.url` | Yes | Your webhook URL that will receive Wise events. |
| `delivery.version` | Yes | Webhook schema version (use the latest supported version for that event type). |


Sample request
```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/applications/{clientKey}/subscriptions' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "name": "Webhook Subscription #1",
    "trigger_on": "transfers#state-change",
    "delivery": {
      "version": "4.0.0",
      "url": "https://your.webhook.url/12345"
    }
  }'
```

Sample response
```json 200 application/json
{
  "id": "72195556-e5cb-495e-a010-b37a4f2a3043",
  "name": "Webhook Subscription #1",
  "trigger_on": "transfers#state-change",
  "delivery": {
    "version": "4.0.0",
    "url": "https://your.webhook.url/12345"
  },
  "scope": {
    "domain": "application",
    "id": "<your client key>"
  },
  "created_by": {
    "type": "application",
    "id": "<your client ID>"
  },
  "created_at": "2019-10-10T13:55:57Z"
}
```

```json 429 application/json
{}
```

See our [Webhooks guide](/guides/developer/webhooks) for details about our delivery and retry policy.

### Transfer event types

The following event types are essential for effectively tracking transfer-related events.

To subscribe to an event type, use the event type value in the `trigger_on` field of the create webhook subscription request body.

| Event type  | Required? | Description |
|  --- | --- | --- |
| `transfers#state-change` | Yes | Primary tracker event. State change events notify you each time a transfer changes states, like from `processing` to `funds_converted` to `outgoing_payment_sent`. 

Use these payloads to keep your system synchronised with the current state of each transfer and to surface status updates to your users. |
| `transfers#payout-failure` | Yes | Triggered when Wise is unable to deliver funds to the recipient. Treat these events as a prompt to investigate the cause and update recipient details so the transfer can be retried. 

The payload provides **failure reason codes** when payout fails. Not all failures produce a state change event, so handle separately. |
| `transfers#refund` | Recommended | Triggered when a transfer status changed to `funds_refunded`. Refund events signal that funds for a failed transfer are being returned. 

Use these payloads to reconcile your records and, if applicable, notify your user that the original transfer was unsuccessful and funds are being returned. Payload includes refund amount + currency. |


### Funding event types

These webhooks provide visibility into the funding side of transactions. The webhook(s) you need to use for your integration depend on how you fund transfers (via balance or direct debit).

To subscribe to an event type, use the event type value in the `trigger_on` field of the create webhook subscription request body.

| Event type  | Funding method | Description |
|  --- | --- | --- |
| `balances#update` | Balance (Nostro/MCA) | Balance update events occur when your balance changes due to a transfer being funded, a refund being credited back, or other balance activity. These events let you monitor available funds in real time and trigger alerts or top-up workflows when balances fall below operational thresholds. 

Required if you want to track **topup-to-balance** transfers, as there is no `transfers#state-change` for balance top-up transfers. |
| `payment-instruments#status-change` | [Direct debit](/guides/product/send-money/funding/direct-debit) | Notifies you when the status of an instrument changes (for example, from `PENDING` to `CONNECTED` or `DISCONNECTED`). 

Monitor these to confirm that a funding instrument has been successfully established before attempting to fund transfers, and to detect when it has been revoked or expired. |
| `payment-instruments-payins#status-change` | [Direct debit](/guides/product/send-money/funding/direct-debit) | Notifies you of each payin status change. Payin status change events track each individual funding attempt against a connected instrument, reporting transitions such as `PROCESSING`, `CONFIRMED`, `SETTLED`, or `FAILED`. 

Use these to confirm that funds have been successfully collected and to handle failed collections. |


## Handle transfer and funding events

### Event: Transfer state change

Use the `transfers#state-change` event to update the status shown in your application and to trigger a [delivery estimate](/api-reference/delivery-estimate) refresh.

Example payload:

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

When you receive this payload:

1. Update your stored status to `data.current_state`.
2. Use the value in `data.resource.id` as the `TRANSFER_ID` when fetching the latest [delivery estimate](#get-delivery-estimates).


#### Transfer states path

The typical transfers **happy path** looks like this:

`incoming_payment_waiting` → `processing` → `funds_converted` → `outgoing_payment_sent`

The `outgoing_payment_sent` status is the final state of the normal flow and means Wise has sent the payout to the recipient bank/payment network. It does not guarantee the recipient bank has credited the beneficiary account yet.

If the payment fails and is returned, the following **unhappy path** occurs:

`outgoing_payment_sent` → `bounced_back` → `processing` → `cancelled` → `funds_refunded`

This type of flow can occur, for example, if the recipient bank account does not exist or the data is entered incorrectly and the payment is returned to Wise.

Most bounce backs occur within 2-3 business days. However, they can happen up to several weeks after a transfer is sent.

Payout speeds
Payment systems in different regions operate at different speeds and frequency. For example, in the UK funds will reach the recipient bank account within few minutes after Wise sends the outgoing payment. However, in the US it usually takes a day until funds are received.

### Event: Transfer payout failure

Use the `transfers#payout-failure` event to surface actionable failure reasons for ops/support workflows and (where appropriate) customer self-serve fixes. Process it separately from `transfers#state-change`.

Key behaviour:

- A payout can fail while the transfer is still in `outgoing_payment_sent`.
- Not every payout failure triggers a `transfers#state-change`.


Example payload:

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

When you receive this payload:

- Store the latest `failure_reason_code` + `failure_description` against the transfer in your database.
- Make it visible to your ops/system tooling so your teams can take action (for example, ask your customer to correct recipient details).


Testing payout failures
To test `transfers#payout-failure`, use the corresponding [simulation endpoint](/api-reference/simulation/simulationtransferpayoutfailure) in the sandbox.

### Event: Transfer refund

Use the `transfers#refund` event to record that Wise has triggered a refund and the amount/currency being returned. This event triggers when the transfer reaches the `funds_refunded` state and they payload includes the refunded amount and currency.

Example payload:

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

Testing refunds
To test the `transfers#refund` event, follow the steps provided in the [Testing refunds guide](/guides/product/send-money/refunds/testing-refunds).

### Event: Balances update

If you fund transfers from a Wise balance, `balances#update` helps you:

- Reconcile transfer debits/credits
- Monitor liquidity
- Track topup-to-balance transfers, as there is no `transfers#state-change` for those


Credit event sample
```json
{
  "data": {
    "resource": {
      "id": 2,
      "profile_id": 2,
      "type": "balance-account"
    },
    "amount": 70,
    "balance_id": 111,
    "channel_name": "TRANSFER",
    "currency": "GBP",
    "occurred_at": "2023-03-08T14:55:38.123Z",
    "post_transaction_balance_amount": 88.93,
    "step_id": 1234567,
    "transaction_type": "credit",
    "transfer_reference": "BNK-1234567"
  },
  "subscription_id": "f2264fe5-a0f5-4dab-a1b4-6faa87761425",
  "event_type": "balances#update",
  "schema_version": "4.0.0",
  "sent_at": "2023-03-08T14:55:39.456Z"
}
```

Debit event sample
```json
{
  "data": {
    "resource": {
      "id": 2,
      "profile_id": 2,
      "type": "balance-account"
    },
    "amount": 9.6,
    "balance_id": 111,
    "channel_name": "TRANSFER",
    "currency": "GBP",
    "occurred_at": "2023-03-08T15:26:07.891Z",
    "post_transaction_balance_amount": 106.93,
    "step_id": 1234567,
    "transaction_type": "debit",
    "transfer_reference": "47500002"
  },
  "subscription_id": "f2264fe5-a0f5-4dab-a1b4-6faa87761425",
  "event_type": "balances#update",
  "schema_version": "4.0.0",
  "sent_at": "2023-03-08T15:26:07.234Z"
}
```

### Event: Payment instrument status change

If you fund transfers via direct debit, the `payment-instruments#status-change` event lets you react in real time when an instrument’s status changes. For example:

- `PENDING` → `CONNECTED`: The mandate is now active and you can start collecting payments.
- `CONNECTED` → `DISCONNECTED`: The mandate has been cancelled or revoked. You should stop attempting collections, reflect this to the customer, and potentially prompt re-authorization.


Connected status payload
When a payment instrument is successfully connected:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-19T17:43:23Z",
  "data": {
    "resource": {
      "id": "7f0f9dda-7755-4b4f-bd53-637129291308"
    },
    "from_status": "PENDING",
    "to_status": "CONNECTED",
    "occurred_at": "2025-01-19T17:43:22Z"
  }
}
```

Disconnected status payload
When a payment instrument becomes disconnected, the `disconnect_reason` field is included in `data.resource`:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-20T14:22:18Z",
  "data": {
    "resource": {
      "id": "7f0f9dda-7755-4b4f-bd53-637129291308",
      "disconnect_reason": "REFER_TO_PAYER"
    },
    "from_status": "CONNECTED",
    "to_status": "DISCONNECTED",
    "occurred_at": "2025-01-20T14:22:17Z"
  }
}
```

### Event: Payin status change

If you fund transfers via direct debit, the `payment-instruments-payins#status-change` event lets you track the lifecycle of each payment as it moves through the payment rail.

- `PROCESSING` → `SETTLED`: Funds have arrived and you can credit the customer.
- `PROCESSING` → `FAILED`: The payment failed (insufficient funds, payer dispute, etc). You can trigger a retry flow, notify the customer, or update internal records with the specific `failure_reason`.


Processing status payload
When a payin enters the processing state:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments-payins#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-19T10:15:23Z",
  "data": {
    "resource": {
      "id": "67136333-0b4d-4f72-49bf-24088f687416",
      "payment_instrument_id": "67133810-d4f6-47b4-a948-09b2d8438b43"
    },
    "from_status": null,
    "to_status": "PROCESSING",
    "occurred_at": "2025-01-19T10:15:22Z"
  }
}
```

Settled status payload
When a payin successfully settles:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments-payins#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-22T14:30:46Z",
  "data": {
    "resource": {
      "id": "67136333-0b4d-4f72-49bf-24088f687416",
      "payment_instrument_id": "67133810-d4f6-47b4-a948-09b2d8438b43"
    },
    "from_status": "CONFIRMED",
    "to_status": "SETTLED",
    "occurred_at": "2025-01-22T14:30:45Z"
  }
}
```

Failed status payload
When a payin fails, the `failure_reason` field is included in `data.resource`:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments-payins#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-20T16:45:19Z",
  "data": {
    "resource": {
      "id": "78247444-1c5e-5083-5acf-35199f798c527",
      "payment_instrument_id": "67133810-d4f6-47b4-a948-09b2d8438b43",
      "failure_reason": "REFER_TO_PAYER"
    },
    "from_status": "PROCESSING",
    "to_status": "FAILED",
    "occurred_at": "2025-01-20T16:45:18Z"
  }
}
```

## Get delivery estimates

Use the [delivery estimate endpoint](/api-reference/delivery-estimate/deliveryestimateget) to retrieve the current ETA for a transfer.

**Endpoint**: `GET /delivery-estimates/{transferId}`

Recommended implementation pattern:

- Fetch delivery estimate:
  - After transfer creation (optional initial ETA).
  - On every `transfers#state-change` event, because the ETA can change as processing progresses.


Sample request
```CURL
curl -i -X GET \
  'https://api.wise.com/v1/delivery-estimates/<TRANSFER_ID>?timezone=Asia%2FSingapore' \
  -H 'Authorization: Bearer <USER_ACCESS_TOKEN>' \
  -H 'X-External-Correlation-Id: <UUID>'
```

Sample response
```JSON
{
  "estimatedDeliveryDate": "2018-01-10T12:15:00.000+0000",
  "formattedEstimatedDeliveryDate": "in seconds"
}
```

## Test transfer tracking in sandbox

Because sandbox doesn’t fully process real payouts, use the [simulate transfer state change endpoints](/api-reference/simulation/simulationtransferstatechange) to test your status tracker and webhook listener.

Available simulation statuses (must be called in this order):

`processing` → `funds_converted` → `outgoing_payment_sent` → `bounced_back` → `funds_refunded`

Simulation is asynchronous
Simulation requests return `200` immediately, but status changes and webhooks are triggered asynchronously. Allow at least 5 seconds between simulation calls.