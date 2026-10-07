# Refund to balance

This refund method applies to partners who fund transfers from their Wise multi-currency account (MCA) balance. This includes partners using:

- [Fund from balance](/guides/product/send-money/funding/fund-from-balance) as their settlement method, which is common with Correspondent and Enterprise partners.
- [Post-funding](/guides/product/send-money/use-cases/correspondent/correspondent-fund-transfer#post-funding), which is a bulk settlement option use by some Correspondent partners.


When refunding to a balance, Wise credits the refund to your Wise multi-currency account rather than to the sender's bank account. **You are then responsible for reimbursing the refund amount to your customer**.

## How it works

When a refund is triggered, Wise:

1. Cancels the transfer.
2. Credits the refund amount to your multi-currency account (MCA) balance in the **source currency** of the transfer.
3. Sends you a `balances#update` webhook with a credit event.
4. Moves the transfer status to `funds_refunded`.


Note that no currency conversion is performed in the refund process. Wise refunds the full source-currency amount, regardless of which currency the refund arrived in.

Swift partial refunds exception!
When a transfer is paid out via the Swift network, intermediary banks may deduct fees. When a refund occurs on this type of transfer, Wise receives *less than the full transfer amount*. Wise refunds only the amount actually received, converted from the target currency to the source currency.

## Detect refunds

Wise provides multiple webhooks to help you track transfer events, including refunds. Use the event notification payloads to keep informed of transfer states and to trigger your own internal processes.

Subscribe to the following webhook events to track the full refund lifecycle:

| Webhook event  | Description |
|  --- | --- |
| `balances#update` | Notifies you when your balance is credited.

Use the `data.transaction_type` (credit) and `data.transfer_reference` fields to identify refund credits. If `transfer_reference` maps to a transfer you have on record, this is the primary signal that a refund has occurred. |
| `transfers#refund` | Provides the refund amount and currency.

Especially important for Swift partial refunds, where the refund amount may be less than the original transfer amount. |
| `transfers#state-change` | Reflects the current transfer status. Confirm the status has moved to `funds_refunded`. |
| `transfers#payout-failure` | Provides the specific reason for a bounceback (for example, incorrect account details). |


Once you have confirmed the refund credit on your balance, reimburse your customer through your own channels. Wise does not refund the sender directly with this refund method.

### Sample webhook payloads

Balance update
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

### Reconciliation

Your [balance statement](/api-reference/balance-statement/balancestatementget) includes refunds in the `transactions` array, with the `type` set to `CREDIT` and further details included in the `details` object.

From the webhooks payloads, use the `data.occurred_at` timestamp for reconciliation with your own records, as webhook delivery order is not guaranteed.

Refund amount for Swift transfers
For Swift partial refunds, always use the `refund_amount` from the `transfer#refund` webhook, not the original transfer amount, when refunding your customer and reconciling your records.

### Refund credits vs settlement credits

If you are on the post-funding model, your balance will receive both refund credits and settlement credits. Use the `data.transfer_reference` field in the `balances#update` webhook to distinguish between them.

- Refund credits will reference a specific transfer ID you created.
- If the `transfer_reference` value does not match any of your transfers (for example, it has a BNK- prefix), it is a settlement top-up or other external deposit.


To reliably distinguish refunds from top-ups, you must maintain a mapping of transfer IDs you create.

## Transfers not funded from balance

In the rare cases where a transfer is not funded from balance, but you want to use your Wise balance as the refund destination, you must pass your Balance Recipient ID as the refund recipient in the create transfer request.

1. Call the [Retrieve multi-currency account for a profile](/api-reference/multi-currency-account/mcaget) endpoint.
2. Take the `recipientId` from the response. This is your Balance Recipient ID.
3. Pass the `recipientId` value in the `sourceAccount` field of each create transfer request body. This tells Wise to refund to your balance if the transfer is cancelled or bounced back.


## Holding a positive balance

Some partners have a contractual requirement not to hold funds with Wise. If a refund credit causes your balance to go positive, you may need an automated sweeping mechanism to move the funds out of your balance and back to your bank account.

If this applies to you, contact your Wise Platform Implementation team to discuss your options.