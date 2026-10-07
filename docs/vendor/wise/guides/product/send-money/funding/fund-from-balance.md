# Fund transfers from your Wise balance

Fund transfers using your Wise multi-currency account balance.

The [fund transfer endpoint](/api-reference/transfer/transferfund) is the final step in executing a payout when using a Wise balance. Once called, Wise immediately begins processing the transfer if sufficient funds are available in the account balance.

**Endpoint:** `POST /profiles/{profileId}/transfers/{transferId}/payments`

## Requirements

- `transferId`: The transfer ID of the already-created transfer that the funds will apply to.
- Sufficient funds: Ensure you have sufficient funds in the appropriate currency balance.


## Fund a transfer

To fund a transfer from your balance, make a POST request with `type` set to `BALANCE`.

### Parameters

| Parameter | Type | Required | Description |
|  --- | --- | --- | --- |
| `profileId` | integer | Yes | The ID of the profile that created the transfer (personal or business). |
| `transferId` | integer | Yes | The ID of the transfer to fund. |
| `type` | string | Yes | Must be `"BALANCE"` to fund from your multi-currency account. |


### Request body

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/transfers/16521632/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "BALANCE"
  }'
```

## Successful funding

When your balance has sufficient funds, you'll receive a `COMPLETED` status in the response.

### Response body

```json 201 application/json
{
  "type": "BALANCE",
  "status": "COMPLETED",
  "balanceTransactionId": 987654321
}
```

```json 429 application/json
{}
```

After successful funding:

1. The transfer status changes from `incoming_payment_waiting` to `processing`.
2. Wise begins processing the payout to the recipient.
3. You receive [webhook notifications](/api-reference/webhook-event/eventtransfersstatechange) as the transfer progresses.
4. You can track the transfer status using the [Get transfer by ID endpoint](/api-reference/transfer/transferget).


## Insufficient funds

If your balance doesn't have enough funds, the request will fail:

### Response body

```json
{
  "type": "BALANCE",
  "status": "REJECTED",
  "errorCode": "transfer.insufficient_funds"
}
```

The transfer will remain in `incoming_payment_waiting` status until funded. When this occurs, you can:

1. Add funds to your balance.
2. Retry the request once funds are available.


## Testing in sandbox

In the sandbox environment, you can:

- Create test balances.
- Add test funds to practice the funding flow.
- Test insufficient funds scenarios.


[Learn more about testing](https://docs.wise.com/api-docs/guides/send-money).