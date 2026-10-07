# Refund via net settlement

This refund method applies to partners using the [bulk settlement](/guides/product/send-money/funding/bulk-settlement) model, where Wise processes payouts ahead of receiving the settlement funds and reconciles via a daily settlement journal.

Under this model, Wise does not refund the sender directly. Instead, Wise notifies you that a transfer needs to be refunded, and you reimburse your customer. The refund amount is then accounted for in your next settlement cycle.

## How it works

Refunds via net settlement can apply to both settled and unsettled transfers. Unsettled transfers that are refunded must still be included in the settlement journal.

When a refund is triggered, Wise:

1. Cancels the transfer.
2. Notifies you that the transfer needs to be refunded with a webhook event payload.
3. Moves the transfer status to `funds_refunded`.


You will then process the webhook event payload to refund your customer and reconcile via the settlement journal.

CSV notification over sFTP
Alternatively, Wise can deliver a refund notification file to an sFTP server. This method is slower than webhooks and only used in cases where webhook integration is not feasible.

Contact your Implementation team if you'd like to use the CSV over sFTP notification method.

## Refund webhook for net settlement

To use the webhook for net settlement refunds, Wise must first configure your integration to use the `payout#create` webhook event.

You can then:

1. Process the webhook payload.
2. Validate the webhook signature.
3. Refund your customer.
4. Reconcile via settlement.


The event type name, `payout#create`, indicates that Wise is creating a payout record to track the refund obligation. Despite the name, this event means a refund is due, not that a new outbound payout has been made.

**Always treat `payout#create` webhooks as refund instructions.**

Once configured, Wise sends notifications containing the refund data to your callback URL.

Your system should respond with an **HTTP `200`** to acknowledge successful receipt. You do not need to process the refund synchronously. You can batch refunds and process them later, but you must store the refund request and manage it internally from that point.

If Wise does not receive a `200` response (or the request times out), Wise will resend the notification for the same transfer ID. Your system must handle duplicate deliveries and not process the same refund twice.

### Process the refund webhook payload

The webhook event data provides the details you need to apply the credit to the correct bank account or other payment mechanism, including:

- Amount
- Source currency
- Transfer ID


The payload for the `payout#create` notification includes the following fields:

| Field  | Type | Description |
|  --- | --- | --- |
| `event_type` | `string` | Type of event, which is always `payout#create`. This defines the data object. |
| `sent_at` | `timestamp` | Timestamp when the event happened. |
| `data` | `object` | Object with information about the updated resource. |
| `data.payoutId` | `long` | ID to refer to this payout attempt. **This is not the transfer ID.** |
| `data.amount` | `decimal` | Amount to credit or refund to the account. |
| `data.currency` | `string` | Currency of the amount to credit or refund. Useful for partners who support multiple source currencies. |
| `data.transferId` | `long` | ID of the transfer to refund. |
| `data.customerTransactionId` | `string` | The idempotency ID sent when creating the transfer. |


**Example payload**:

```json
{
  "event_type": "payout#create",
  "sent_at": "2025-10-14T12:43:37Z",
  "data": {
    "payoutId": 12345,
    "amount": 543.21,
    "currency": "EGP",
    "transferId": 98765,
    "customerTransactionId": "e592a7ba-d7d1-4c28-ac44-10cb091dad07"
  }
}
```

### Validate webhook signature

Wise sends a signature header with each refund webhook request. You should validate this signature to confirm the request genuinely came from Wise.

Use the following public keys depending on your environment:

Production key
`MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0U0YsuLEPaUL7RTaMswsQTI6EZujmp2tN+TYs7LEhI6vHaVN81ycMsivAgS+ZNywua3mW4v2KjQd8OrQcrdReRIdiKGqFZXOtvCXgGtDsZjt4dq3s+CUyfHzRPno1TuXt9IdUAD+G8y9PAvARNBRL7QehyRiyKoGaSWghqCek3rMBhxrd2WWSaRJX9QZgWnjgNMWHbDz7clfL3rRgMuYVg/WV7Wa0CVKaZJJJt2KZbUcJg2ONA1ysV4JdzK7t/f6NoxcWWpbZX1Dy8TGQhmOncNfoAXwHzievPzNQQyDcKTlp2f89ggctqHjNXjJp6XY7pO45SrAhzc80VVTLXHukQIDAQAB`

Sandbox key
`MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArQ8jMhD5Y8Hbk5UsmezF5yjxGrJV16ZzcXteRFgM0z8jjDHct1bBYYojr2tAmkIg78jjj8KvRcKeDmu2IPSj4kK3va+hyDpoa5QYGDbmjXJQaop07Vsdxv/IWSKBzBHfnl0+p3dfgvnId8uGx7M8/kmFBVF1uVcZg9WecFdOJTF4/mH5HIkc1SltCKmzrZdCHwicQ2t9ZAEaTpZJPa1tyIxW194D6yA3hWruPdVswOL4y5DnzD/cy5/FL3pvAqm8IhachdSodM9wOWse9sFRU3YS1tyn1gkhshgMadRlLwnXiDUeE7ZOHO9fMQ163AGkhWJhdvRzRtSF9cVoLNnTnwIDAQAB`

### Refund your customer

Use the `data.amount` and `data.currency` fields from the payload to refund your customer via their original payment method (bank account, wallet, etc.).

Important: Swift partial refunds!
For transfers routed via the Swift network, intermediary banks may deduct fees from a bounceback. In these cases, the `data.amount` in the webhook will be less than the original transfer amount.

Always use the amount from the webhook payload, not the original transfer amount, when refunding your customer and updating your records.

### Reconcile via settlement

Include refunded transfer IDs in the `refundedTransfers` array of your settlement journal. The refund amount is offset against your settlement — you pay Wise less (or nothing) for that settlement period.

## When refunds exceed settlements

There may be occasions where the total refund amount for a settlement period exceeds the total amount to be settled with Wise. When this happens, the net amount is negative — meaning **Wise owes you money**.

When this occurs:

1. Record the amount owed by Wise in the settlement currency.
2. Offset it against future settlements using the `balanceTransfer` field in the [Settlement Journal request](/api-reference/bulk-settlement/bulksettlementjournalcreate) request body.


### Rules for balance transfer

- The maximum `balanceTransfer` per settlement is capped at the expected settlement amount before balance transfer is applied. The final settlement amount must be **zero or positive**. You cannot claim more than is owed in a single period.
- If the amount Wise owes you is larger than a single settlement, spread it across multiple settlements.
- Update your internal record of the amount owed by Wise each time you apply a balance transfer.


### Calculation logic

```
balanceTransfer = min(amountOwedByWise, expectedSettlementAmount)
finalSettlementAmount = expectedSettlementAmount - balanceTransfer
amountOwedByWise = amountOwedByWise - balanceTransfer
```

Where:

- `expectedSettlementAmount` = total successful transfer payouts minus total refunds for the period.
- `balanceTransfer` = the portion of Wise's debt you are offsetting in this settlement.
- `finalSettlementAmount` = what you actually send to Wise (must be ≥ 0).


![Balance Transfer Logic](https://wise.com/public-resources/assets/api-docs/balance_transfer_logic.png)