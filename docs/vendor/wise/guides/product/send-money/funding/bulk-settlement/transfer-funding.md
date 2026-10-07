# Mark transfers as funded

When using the bulk settlement method, the [fund transfer](/api-reference/transfer/transferfund) step is used to **mark** the transfers as funded.

To mark a transfer as funded from a bulk settlement, use `TRUSTED_PRE_FUND_BULK` as the `type` when making the fund transfer request.

If you are using the cross-currency bulk settlement option, you must also include the `partnerReference` field with the **same partner reference** that you used in the settlement journal."

**Example request body**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/transfers/16521632/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "TRUSTED_PRE_FUND_BULK",
    "partnerReference": "ref_12345"
  }'
```

Upon funding completion, the transfer will move from the `incoming_payment_waiting` status to the `processing` status.

The fund transfer endpoint acts as a guarantee that you will send the funds to Wise at the end of the agreed settlement period. This is legally binding. Only call the endpoint when you are certain you will send the funds to us.

## Delayed funding 

If you want to lock an FX rate and fund a transfer later, you can use delayed funding.

Delayed funding is only available to partners who have an active agreement for this feature with Wise.

Delayed funding works by setting a `status` parameter in the request body in the two following steps:

1. **INITIATE**: The FX rate is locked for the transfer.
2. **COMPLETE**: The transfer is completed and paid out.


**Example Request Body**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/transfers/16521632/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "TRUSTED_PRE_FUND_BULK",
    "status": "INITIATE"
  }'
```

## Error handling 

When calling the fund transfer endpoint for bulk settlement, you may encounter the following error responses:

| HTTP code | Error code | Description | Reason |
|  --- | --- | --- | --- |
| 403 | `transfer.not-accessible-for-user` | Unauthorized access | You can only fund a transfer with a user token that owns the transfer being funded. |
| 422 | `trustedprefundbulk.payment-option-unavailable` | Using a non-permitted `type` parameter | Bulk settlement is not enabled. |


Of these errors, the only one you are likely to see after going live should be `transfer.invalid-state`. The others should never happen if your integration works and passes the testing phase.

This error will normally only occur if you attempt to retry calling the fund transfer endpoint for a transfer that you already called it for, as it is unlikely the customer will fund the transfer directly, although this is possible. In the case of a failed retry, you can generally assume that the first call was successful and the transfer will be processed.

Regardless of whether this request returns `CREATED` or `REJECTED`, you should still send the funds to Wise .

In the unlikely event a transfer has had no successful payment attempts, the transfer will still be processed on receipt of the funds and/or settlement file containing the transfer. The difference is the customer will have to wait rather than having an instant payment experience.

Example Response
```json
{
  "type": "TRUSTED_PRE_FUND_BULK",
  "status": "REJECTED",
  "errorCode": "transfer.invalid-state",
  "errorMessage": null
}
```

## Settlement limits 

To limit exposure and risk, Wise might prevent payments from being paid out instantly in case the total amount owed to Wise for the current settlement period is above the collateral we are currently holding for your institution. In this case, you will still receive a successful response with an **HTTP status code `200`**.

The payment will still be created, but the payout to the recipient will be **delayed** until we confirm the funds arrival at the end of the settlement period.

You should not cause the user process to fail or error at this point, and should consider the request successful (hence the 200). However, you may wish to trigger some logic based on this response to run your settlement process earlier or alert a member of staff to do so, in order to prevent delays in the processing of transfers.

Please discuss and agree on a suitable process with our implementation team on how to proceed once the limits are reached.

Example Response
```json
{
  "type": "TRUSTED_PRE_FUND_BULK",
  "status": "CREATED",
  "errorCode": "trustedprefundbulk.limit-reached",
  "errorMessage": null
}
```