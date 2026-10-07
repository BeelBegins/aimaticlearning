# Webhooks for multi-currency accounts

Wise provides several webhooks for you to receive notifications about multi-currency account-related events.

| Event type  | Description |
|  --- | --- |
| `transfers#state-change` | Monitor state change of a transfer and trigger updates in your UI or other user notifications. |
| `profiles#verification-state-change` | Monitors and notifies if the user/profile is not verified initially and becomes verified. |
| `transfers#active-cases` | Monitors and alerts for any issues with a transfer. |
| `balances#update` | Monitors and alerts if any credits or debits are applied to a balance. Useful for when a payin may take time to complete or if being paid from another source. |


See our [Webhooks guides](/guides/developer/webhooks) for details on how to subscribe to webhooks and manage event payloads.

## Example payloads

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

See the [transfer state change event reference](/api-reference/webhook-event/eventtransfersstatechange) for the full schema and details. When subscribing, do so at the [application-level](/api-reference/webhook/webhookapplicationsubscriptioncreate).

Profile verification state change
```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "profiles#verification-state-change",
  "sent_at": "2026-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "type": "profile",
      "id": 111
    },
    "current_state": "verified",
    "occurred_at": "2026-01-01T12:34:56.789Z"
  }
}
```

See the [profile verification state change event reference](/api-reference/webhook-event/eventprofilesverificationstatechange) for the full schema and details. When subscribing, do so at the [application-level](/api-reference/webhook/webhookapplicationsubscriptioncreate).

Transfer active cases
```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#active-cases",
  "sent_at": "2026-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "type": "transfer",
      "id": 111,
      "profile_id": 222,
      "account_id": 333
    },
    "active_cases": [
      "deposit_amount_less_invoice"
    ]
  }
}
```

See the [transfer active cases event reference](/api-reference/webhook-event/eventtransfersactivecases) for the full schema and details. When subscribing, do so at the [profile-level](/api-reference/webhook/webhookprofilesubscriptioncreate).

Balances update
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

See the [balances update event reference](/api-reference/webhook-event/eventbalancesupdate) for the full schema and details. When subscribing, do so at the [profile-level](/api-reference/webhook/webhookprofilesubscriptioncreate).