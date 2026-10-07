# Testing refunds

How to test refund webhooks in the sandbox.

Use the simulation endpoints to test how your integration handles refunds, including Swift partial refunds, without initiating real-world financial transactions.

When a transfer’s status becomes `funds_refunded`, Wise sends a `transfers#refund` webhook event to your subscribed URL.

Important!
- Even if funding moves the transfer to `processing`, you must still call the `/processing` simulation step.
- Simulation isn’t supported for email transfers.


## Refund behaviour in sandbox

In production, refund amounts can differ by payout method. For example, Swift intermediary bank fees may reduce the amount returned, resulting in a partial refund. The sandbox simulates this to help you test your webhook handling.

| Transfer payout type  | Refund amount |
|  --- | --- |
| Non-Swift transfer | Typically the full gross amount the customer paid for the transfer (including Wise fees). |
| Swift transfer | A random percentage from 5–15% is deducted from the gross amount to simulate intermediary bank fees. |


## Simulate a refund

To simulate a refund, you'll go throught the following steps in the sandbox environment (described in the sections below):

1. Create a quote.
2. Create a recipient.
3. Create and fund the transfer using your normal flow.
4. Subscribe to the `transfers#refund` event.
5. Simulate the transfer state changes. The change of transfer state to `funds_refunded` triggers the webhook event notification.


### Step 1: Create quote

Create an [athenticated quote](/guides/product/send-money/quotes/authenticated-quote) for the transfer.

- To test **Swift partial refunds**, set `payOut` to `SWIFT` when creating the quote. See the [Swift network transfers guide](/guides/product/send-money/swift-network-transfers) for more details.


#### Example request

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "USD",
    "targetCurrency": "EUR",
    "sourceAmount": 1000,
    "targetAccount": null,
    "payOut": "SWIFT"
  }'
```

### Step 2: Create recipient

[Create a recipient account](/api-reference/recipient/recipientcreate) for the transfer.

- For Swift, use recipient/account details that route via Swift as described in the [Swift network transfers guide](/guides/product/send-money/swift-network-transfers).
- If the recipient doesn’t support Swift for your currency/route, the quote changes to a non-Swift payout method when you update it with the recipient.


### Step 3: Create and fund transfer

Create the transfer using the quote and recipient, then fund it using your normal funding flow.

See the [Send money guide](/guides/product/send-money/use-cases/correspondent/send-money) for instructions on creating transfers.

### Step 4: Create application webhook subscription

Create an [application webhook subscription](/api-reference/webhook/webhookapplicationsubscriptioncreate) for `transfers#refund` using a **client credentials token**.

Endpoint: `POST /v3/applications/{clientKey}/subscriptions`

#### Example request

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/applications/{clientKey}/subscriptions' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "name": "Sandbox transfers refund subscription",
    "trigger_on": "transfers#refund",
    "delivery": {
      "version": "4.0.0",
      "url": "https://example.com/webhooks/wise"
    }
  }'
```

### Step 5: Simulate transfer state changes

Use [Simulate transfer state change](/api-reference/simulation/simulationtransferstatechange) to move the transfer through states **in this order**:

`processing` → `funds_converted` → `outgoing_payment_sent` → `bounced_back` → `funds_refunded`

Endpoint: `GET /v1/simulation/transfers/{transferId}/{status}`

#### Example requests

**Processing**:

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/simulation/transfers/15574445/processing \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Funds converted**:

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/simulation/transfers/15574445/funds_converted \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Outgoing payment sent**:

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/simulation/transfers/15574445/outgoing_payment_sent \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Bounced back**:

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/simulation/transfers/15574445/bounced_back \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Fund refunded**:

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/simulation/transfers/15574445/funds_refunded \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

### Step 6: Receive and verify webhook

After you simulate `funds_refunded`, Wise sends a `transfers#refund` webhook payload to your subscribed endpoint.

The webhook includes:

- `data.resource.refund_amount` — amount returned to the sender
- `data.resource.refund_currency` — currency of the refund


See the [transfers#refund](/api-reference/webhook-event/eventtransfersrefund) api reference for more details about the event.

#### Example webhook payload

See the [event type reference](/api-reference/webhook-event/eventtransfersrefund) for more details about the `transfers#refund` webhook.

## Sandbox limitations

- **Webhook-only simulation**: The simulated refund amount applies only to the webhook payload.
- **Not suitable for reconciliation**: Account balances and the sandbox UI can reflect different values (for example, a full refund), regardless of payout method. Don’t reconcile sandbox webhooks to balances/statements.


For more details, see the [Simulate transfer state change](/api-reference/simulation/simulationtransferstatechange#sandbox-refund) endpoint.