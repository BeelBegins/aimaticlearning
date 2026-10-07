# Direct debit: Simulating in sandbox

This guide details the simulation endpoints available **exclusively in the sandbox environment** to help you test how your system handles various status changes and failure scenarios without initiating real-world financial transactions.

This is crucial for verifying your logic for handling disconnected instruments, failed payments, and successful settlements.

## Payment instrument status simulation 

You can simulate a **Payment Instrument** becoming disconnected to test your error handling logic for this scenario.
A Payment Instrument marked as **`DISCONNECTED`** is no longer authorised and cannot be used for initiating Payins.

| Method | Endpoint |
|  --- | --- |
| `POST` | `/simulation/profiles/{{profile_id}}/payment-instruments/{{payment_instrument_id}}` |


### Simulate a disconnected payment instrument

To simulate a Payment Instrument being marked as `DISCONNECTED` (for example, due to the customer cancelling their authorisation via their bank), send the following in the request body:

```json
{
  "scenario": "DISCONNECTED"
}
```

After a successful request (**`204`** response code), you should receive a **`payment-instruments#status-change`** webhook,
and a subsequent `GET` request for the Payment Instrument will show the status as **`DISCONNECTED`**.

## Payin status simulation 

These endpoints allow you to fast-forward a **Payin** into a key terminal status (**`FAILED`** or **`SETTLED`**) for testing purposes.

| Method | Endpoint |
|  --- | --- |
| `POST` | `/simulation/profiles/{{profile_id}}/payment-instruments/{{payment_instrument_id}}/payins/{{payin_id}}` |


### Simulate a failed payin

To test how your system handles a payment failure, use the **`FAILED`** scenario. When a Payin fails, the `status` is set to `FAILED`, and the response includes a **`failureReason`** field for more granular reasoning.

Sample request body for failed status:

```json
{
  "scenario": "FAILED"
}
```

The `FAILED` status means the payment has failed due to cancellation or issues encountered while processing the payment.

### Simulate a settled payin

To simulate a successful payment where the funds are available for the associated transfer, use the **`SETTLED`** scenario.

Sample request body for settled status:

```json
{
  "scenario": "SETTLED"
}
```

Upon a successful simulation, you should receive the relevant **`payment-instruments-payins#status-change`** webhook notification.