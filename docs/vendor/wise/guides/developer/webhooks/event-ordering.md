# Event ordering

Reconcile the order of webhook events.

Webhook event notifications may not arrive in the order they occur due to retries, network conditions, or internal processing.

To determine the correct chronological order of events, use the ordering fields available within each event.

Event payloads can have two types of ordering fields:

- **Timestamp**: Most event types include a timestamp field that represents when the business event actually happened. Use this to determine the chronological order of events across a resource.
- **Sequence ID**: Some event types include a monotonically increasing sequence field you can use to reconcile the order of events within a single transaction.
  - A *higher* value always means a *later* event.
  - Values may not be contiguous and a gap between numbers does not indicate a missing event.
  - Currently, `balances#update` is the only event type that supports this (available in v3.0.0+). See [Sequence IDs](#sequence-ids) for more details.


A few event types do not yet have a dedicated ordering field. See the [Ordering fields by event type table](#ordering-fields) for full details. We aim to improve ordering support across event types over time.

The `sent_at` field reflects when the notification was dispatched, which may differ from when the event occurred, especially during retries.

For event types that do not yet have a dedicated ordering field, you can use `sent_at` as a best-effort fallback, depending on your requirements.

## How to reconcile event order 

If your application processes events in the order they are received, it may end up with an inaccurate view of the current state of a resource. To avoid this, compare the ordering fields of incoming events to determine when each event actually occurred.

### Example payloads

In this example, use `data.occurred_at` (`2024-06-15T10:30:00.123Z`) to determine event order, rather than `sent_at`.

```json
{
  "data": {
    "resource": { "type": "transfer", "id": 111 },
    "current_state": "processing",
    "previous_state": "incoming_payment_waiting",
    "occurred_at": "2024-06-15T10:30:00.123Z"
  },
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#state-change",
  "schema_version": "4.0.0",
  "sent_at": "2024-06-15T10:30:01.456Z"
}
```

See the [Ordering fields by event type table](#ordering-fields) for a list of which ordering fields each event type uses.

## Timestamp precision

Historically, webhook timestamps used second-level precision, and formatting was not always consistent across event types. From schema version `4.0.0`, all timestamps use a consistent ISO 8601 format with millisecond precision:

```
2024-06-15T10:30:00.123Z
```

This makes it possible to correctly order events that occur within the same second. If using an older schema version, timestamps may only have second-level precision (for example, `2024-06-15T10:30:00Z`), which can make it impossible to distinguish the order of rapid successive events.

For consistent millisecond-precision timestamps, use **schema version 4.0.0** or later when creating subscriptions.

## Ordering fields by event type 

This table lists the ordering field available for each event type. Use this field to reconcile event order.

| Event type | Timestamp ordering field | Sequence field | Notes |
|  --- | --- | --- | --- |
| `transfers#state-change` | `data.occurred_at` |  |  |
| `transfers#active-cases` | — |  | Currently no ordering field available. |
| `account-details-payment#state-change` | `data.occurred_at` |  |  |
| `allocations#state-changed` | `data.resource.occurred_at` |  |  |
| `balances#credit` | `data.occurred_at` |  |  |
| `balances#update` | `data.occurred_at` | `data.step_id` | Use `occurred_at` across transactions, `step_id` within a transaction. Available in v3.0.0+. |
| `balances#account-state-change` | `data.occurred_at` |  |  |
| `profiles#verification-state-change` | `data.occurred_at` |  |  |
| `batch-payment-initiations#state-change` | `data.occurred_at` |  |  |
| `transfers#payout-failure` | `data.occurred_at` |  |  |
| `transfers#refund` | `data.occurred_at` |  |  |
| `swift-in#credit` | `data.occurred_at` |  |  |
| `swift#message-received` | `data.occurred_at` |  |  |
| `cards#transaction-state-change` | `data.occurred_at` |  |  |
| `profiles#cdd-check-state-change` | `data.occurred_at` |  |  |
| `cards#card-status-change` | `data.occurred_at` |  |  |
| `cards#card-order-status-change` | `data.occurred_at` |  |  |
| `cards#card-production-status-change` | `data.occurred_at` |  |  |
| `partner-support#case-changed` | `data.resource.updatedAt` |  |  |
| `transaction-disputes#update` | `data.occurred_at` |  |  |
| `bulk-settlement#payment-received` | `data.occurred_at` |  |  |
| `users#state-change` | `data.occurred_at` |  |  |
| `kyc-reviews#state-change` | `data.resource.updatedAt` |  | Uses camelCase. |
| `cards#3ds-challenge` | `data.occurred_at` |  |  |
| `profiles#overdraft-limit-threshold` | — |  | Currently no ordering field available. |
| `account-details-order#order-state-change` | `data.modification_time` |  |  |
| `profiles#state-change` | `data.occurred_at` |  |  |
| `hold-limit-breach#update` | `data.occurred_at` |  |  |
| `settlement#funds-received` | `data.resource.occurred_at` |  |  |


## Recommended approach

1. **Subscribe using schema version `4.0.0` or later** for consistent millisecond-precision timestamps across all event types.
2. **Use each event type's ordering field(s) (as listed in the [Ordering fields by event type table](#ordering-fields))** to determine the true sequence of events.
  - Compare timestamp values to sort events chronologically.
  - For `balances#update`, consider also using `data.step_id` to reconcile the order of events within a single transaction. See the [Sequence IDs section](#sequence-ids) for more details.
3. **Handle out-of-order delivery**. Events may not arrive in chronological order. Your application should use the ordering fields to reconstruct the correct sequence (for example, by reordering events before processing, updating state only when a newer event is received, or any approach that suits your use case).


## Sequence IDs

Some event types include a monotonically increasing sequence field that tracks the order of events. Where available, use this field to reliably determine the order of events regardless of timestamp values. A *higher* value means the event occurred *later* in the sequence.

Sequence IDs are not guaranteed to be contiguous and there may be gaps between values. A gap does not indicate a missing event. They should only be used to determine relative order.

| Order | Sequence ID |
|  --- | --- |
| 1st | `100` |
| 2nd | `101` |
| 3rd | `105` |


See the [Ordering fields by event type table](#ordering-fields) for which event types support a sequence field.