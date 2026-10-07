# Balance limits

Certain countries have regulatory hold limits, please speak to the implementation manager to know if your integration applies.

- [Singapore](https://wise.com/help/articles/2978043/holding-and-spending-limits-if-you-live-in-singapore)
- [Malaysia](https://wise.com/help/articles/5sL5X2V2PbxUBIsQ1Fyfn4/holding-limits-if-you-live-in-malaysia)
- [Japan](https://wise.com/help/articles/3GBSRou4DTXxYz1piNbzN5/holding-limits-if-you-live-in-japan)


To mitigate any risks that the hold limits are breached, we have 2 APIs that should be integrated.

1. [Check the deposit limit](#capacity) - Use the balance capacity API to check the deposit limits of a balance before making a top up to a balance. Only top up the balance by the deposit limit amount or less.
2. [Set an excess money account](#excess-money-account) -  Set an excess money account to the profile so that any excess money (money that exceeds the limit) will be transferred out of the Wise balance at the end of the day.


## Retrieve the deposit limits of an account 

This endpoint allows a user to check how much money they are able to deposit in their balance based on regulatory limits.

It is useful for personal profiles located in countries that have hold limits. We advise calling this API before depositing money into an account if the profile is located in Singapore or Malaysia.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/{profileId}/balance-capacity?currency=SGD' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

```json 200 application/json
{
  "hasLimit": true,
  "depositLimit": {
    "amount": 2000,
    "currency": "SGD"
  }
}
```

```json 429 application/json
{}
```

For request/response details, see the [API reference](/api-reference/balance/balancecapacity).

## Managing hold limit breaches

Some countries, such as Singapore and Malaysia, impose regulatory hold limits on balance accounts for personal profiles. When a customer's balance exceeds this limit, a hold limit breach is created and the deposit amount will not be added to the balance, it'll be reserved. Reserved funds cannot be spent or transferred — they remain locked until the breach is resolved.

A single individual customer can hold one or more accounts with Wise. The hold limits applies to the total balance amount all the customer's account.

If you are unsure if this applies to your customers, reach out to your implementation manager.

This guide explains how to check deposit limits before topping up, how to handle a breach when one occurs, and how to resolve it.

## Overview

The hold limit breach flow involves the following steps:

1. **Check deposit limits** before a customer deposits funds into their balance.
2. **Receive a webhook notification** if a hold limit breach is created or updated.
3. **List open breaches** to inspect active cases for a profile.
4. **Resolve the breach** either by closing it manually with a refund to a recipient, or by withdrawing funds from the balance directly.


## Step 1: Check deposit limits before a deposit

Before initiating a deposit into a customer's balance, call the [Retrieve Deposit Limits](/api-reference/balance/balancecapacity) endpoint to check whether a regulatory hold limit applies and how much capacity remains.

If `hasLimit` is `true`, the `depositLimit` field indicates the maximum amount the customer can hold in that currency. We recommend checking this before every deposit for profiles in Singapore or Malaysia to avoid breaching the limit.

> **Note:** If the deposit would cause the balance to exceed the regulatory limit, the deposit amount will be reserved and a hold limit breach will be created.


## Step 2: Receive a webhook notification

When a hold limit breach is opened or closed, Wise sends a `hold-limit-breach#update` event to your webhook subscription. Subscribe to this event to be notified in real time. For the full event schema and payload examples, see the [Hold Limit Breach Update event](/api-reference/webhook-event/eventholdlimitbreachupdate) reference.

Use `data.state` to determine whether a breach has been opened (`OPEN`) or resolved (`CLOSED`), and `data.closing_reason` to understand how it was resolved.

> **Note:** Webhook events may arrive out of order. Use `data.occurred_at` to reconcile the ordering of events.


For details on setting up webhook subscriptions, see the [Webhooks](/guides/developer/webhooks) guide.

## Step 3: List open breaches

After receiving a `hold-limit-breach#update` event, call the [List Hold Limit Breaches](/api-reference/balance/holdlimitbreachlist) endpoint to retrieve all active cases for the profile. You can filter by `state=OPEN` to see only unresolved breaches.

The `amount` field in the response shows how much is currently in a reserved state due to the breach. Reserved funds cannot be spent or transferred. You can use this to inform the customer about the funds that are locked and unavailable for use.

## Step 4: Resolve the breach

There are two ways a hold limit breach can be resolved.

### Option A: Close the breach manually (refund to a recipient)

If the customer wants to move the excess funds out, call the [Close Hold Limit Breach](/api-reference/balance/holdlimitbreachclose) endpoint. You must specify a recipient account where the reserved amount will be sent.

Once closed, you will receive another `hold-limit-breach#update` event with `data.state: "CLOSED"` and `data.closing_reason: "MANUALLY_RESOLVED"`.

> **Note:** Only breaches with `state: OPEN` can be closed via this endpoint. Attempting to close an already closed breach will return a `400` error.


### Option B: Withdraw from the balance

Alternatively, the customer can withdraw or spend from their remaining available balance — the portion that has not been reserved. Once the available balance drops sufficiently to bring the total held amount within the regulatory limit, the reserved funds are automatically unlocked and the breach is resolved. You will receive a `hold-limit-breach#update` event with `data.closing_reason: "AUTOMATICALLY_RESOLVED"` once Wise processes the release.

> **Note:** Customers can only spend from the available (non-reserved) portion of their balance while a breach is open. The reserved amount remains locked until the breach is resolved.


## Closing reason reference

| Closing reason | Description |
|  --- | --- |
| `MANUALLY_RESOLVED` | The breach was closed by calling the [Close Hold Limit Breach](/api-reference/balance/holdlimitbreachclose) endpoint with a specified recipient. |
| `AUTOMATICALLY_RESOLVED` | The breach was resolved automatically after the customer withdrew funds and the balance dropped below the hold limit. |


## Next steps

- Set up a [webhook subscription](/guides/developer/webhooks) for the `hold-limit-breach#update` event to receive real-time notifications.
- Use the [Retrieve Deposit Limits](/api-reference/balance/balancecapacity) endpoint to proactively surface hold limit information to your customers before they deposit.
- See the [Multi-Currency Accounts](/guides/product/accounts) guide for a full overview of balance account management.