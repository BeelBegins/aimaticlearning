# Bring Your Own PSP

Bring Your Own Payment Service Provider (BYO-PSP) enables you to settle funds to Wise from your acquirer, then instruct Wise how the funds should be split and sent to your customers' accounts.

The BYO-PSP flow consists of two parts:

1. **Settlement**: Send funds from your payment service provider to Wise.
2. **Payout instruction**: Tell Wise how to allocate and distribute those funds.


## Prerequisites

Before implementing BYO-PSP, ensure you have:

- An active Wise Platform integration with Embedded Solutions integration model
- A configured acquirer (PSP) that can send funds to Wise
- Onboarded your customers using the [customer onboarding process](/guides/product/account-setup/customer-onboarding)


## Settlement flow

### Step 1: Subscribe to webhooks 

Before sending funds, set up webhook subscriptions to receive notifications about your settlements and allocations:

| Webhook event | Description |
|  --- | --- |
| [`settlement#funds-received`](/api-reference/webhook-event/eventsettlementfundsreceived) | Triggered when Wise receives your settlement funds |
| [`allocations#state-changed`](/api-reference/webhook-event/eventallocationsstatechanged) | Triggered when the state of your allocation request changes |


See the [Webhooks guide](/guides/developer/webhooks) for setup instructions and best practices.

### Step 2: Send funds to Wise

Instruct your acquirer (PSP) to send the funds to the Wise collection account. The account details will be shared with you during integration.

The payment reference must follow this format: `BYOPSP_{your-client-id}_{your-reference}`. This reference is critical for Wise to identify and process your settlement.

Once Wise receives the funds, you will receive a `settlement#funds-received` webhook notification.

### Step 3: Create a settlement allocation request

After your funds are received, submit a settlement allocation request to tell Wise how to distribute the funds across your customers.

Use the [Create settlement allocation request](/api-reference/settlement/createfundsallocationrequest) endpoint to submit your allocation instructions along with a Settlement Allocation Request (SAR) file.

The SAR file is a CSV containing the payment intent details for each allocation:

| Field | Description |
|  --- | --- |
| `transactionId` | Your unique identifier for this allocation |
| `profileId` | The Wise profile ID of the recipient |
| `recipientType` | Type of recipient account |
| `sourceCurrency` | Currency of the source amount |
| `sourceAmount` | Amount in source currency |
| `targetCurrency` | Currency to pay out |
| `targetAmount` | Amount to pay out in target currency |
| `allocationType` | Type of allocation |
| `paymentReference` | Reference for the payment |
| `reason` | Reason for the payment |
| `createdAt` | Timestamp when the allocation was created |


### Step 4: Track allocation status

Subscribe to the [`allocations#state-changed`](/api-reference/webhook-event/eventallocationsstatechanged) webhook to track the progress of each allocation. Wise processes each allocation as an individual payment intent that can be tracked through to completion.

## Testing in sandbox

Contact the Wise team to configure your sandbox environment for BYO-PSP testing. They will provide you with test collection account details and help you simulate the settlement flow.

## API reference

| Endpoint | Description |
|  --- | --- |
| [Create settlement allocation request](/api-reference/settlement/createfundsallocationrequest) | Submit allocation instructions for settled funds |
| [Settlement funds received webhook](/api-reference/webhook-event/eventsettlementfundsreceived) | Notification when funds are received |
| [Allocations state changed webhook](/api-reference/webhook-event/eventallocationsstatechanged) | Notification when allocation status changes |