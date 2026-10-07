# Supporting customer queries

This operational guide explains the webhooks and API endpoints your ops teams can use when supporting your customer queries.

The sections below cover the following customer flows:

- Customer has a question about payment status or money hasn’t reached the recipient.
- Customer needs a receipt or proof of payout.
- Customer asks why the funds were returned to them.
- Customer is unable to create transfers because their account is no longer active.


Each of these cases could have multiple solutions. In most cases, you have two implementation options:

- Implement in your customer-facing UI so customers can self-serve and will not need to reach out to you.
- Implement in your back office UI so your operations teams can help your customers when they contact you.


For convenience, we’ve pulled all helpful resources into a table.

## Necessary webhooks and endpoints

Here is a compiled list of commonly used webhooks and endpoints.

### Webhooks

The links in the table redirect you to the event type in the Webhooks section of our API reference.

| Link  | Description |
|  --- | --- |
| [balance-update](/api-reference/webhook-event/eventbalancesupdate) | Notification when a multi-currency account is credited or debited. |
| [transfer-state-change](/api-reference/webhook-event/eventtransfersstatechange) | Notification when a transfer state changes. |
| [transfer-active-cases](/api-reference/webhook-event/eventtransfersactivecases) | Notification when a transfer’s list of active cases is updated (active cases indicate potential problems with transfer processing). |
| [transfer-payout-failure](/api-reference/webhook-event/eventtransferspayoutfailure) | Notification of payout failure reason when a payout fails and funds bounce back. |
| [profile-state-change](/api-reference/webhook-event/eventprofilesstatechange) | Notification that triggers when a profile state changes. Subscribe to this webhook to be notified when a profile state changes between `ACTIVE`, `WITHDRAW_ONLY`, `VIEW_ONLY`, and `DEACTIVATED`. |


### Endpoints

The links in the table redirect you to the endpoint in the API reference.

| Link  | Description |
|  --- | --- |
| [get delivery estimate](/api-reference/delivery-estimate/deliveryestimateget) | Allows you to get the time at which we currently expect the transfer to arrive. |
| [get receipt-pdf](/api-reference/transfer/transferreceiptget) | Allows you to get the payout receipt PDF detailing sender, recipient, and some additional information about the transfer. |
| [get banking partner payout information](/api-reference/transfer/transferpayoutinfoget) | Allows you to get payout information on which you can generate your own payout receipt (in-app, PDF or some other format). Transfer must have reached the `processing` or later state for this endpoint to return data. Otherwise, it returns a `404` error. |
| [cancel transfer](/api-reference/transfer/transfercancel) | Allows you to cancel the transfer before it has been sent. |


## Payment status or money hasn't reached recipient

A common customer query is asking for an update on the payment status when it’s taking longer than they expected or when the beneficiary claims they haven’t yet received the funds. Some customers simply want to know the status or ETA, others might ask to cancel, amend, trace, or recall.

There are several ways to help the customer in these situations:

- The [transfer-state-change](/api-reference/webhook-event/eventtransfersstatechange) webhook allows you to see the latest state the payment is in. See our [list of transfer-statuses](/guides/product/send-money/tracking/transfer-statuses).
- The [transfer-active-cases](/api-reference/webhook-event/eventtransfersactivecases) webhook notifies you of any issues with the transfer, even if there is no action you can take to resolve the issue. Wise might simply be doing additional checks on our side, so this webhook gives an indication of delays in processing the payment.
- The [delivery estimate](/api-reference/delivery-estimate/deliveryestimateget) endpoint gives you the current estimate of when the payment should hit the recipient’s account.


Read more about tracking transfers in our [Tracking transfers guide](/guides/product/send-money/tracking/transfer-statuses).

## Receipt or proof of payout

Sometimes the customer needs to provide the recipient with proof of the payment being made, or they request this for their own records or peace of mind.

- The [receipt-pdf](/api-reference/transfer/transferreceiptget) endpoint allows you to download a Wise-branded PDF.
- The [banking partner payout information](/api-reference/transfer/transferpayoutinfoget) endpoint allows you to fetch specific payout information so that you can generate your own transfer receipt. Transfer must have reached the `processing` or later state for this endpoint to return data. Otherwise, it returns a `404` error.


Read more about custom receipts in our [Custom receipt guide](/guides/product/send-money/receipts).

## Reason for returned funds

Sometimes we cannot pay the funds out or the funds are returned to us (for example, the recipient’s details were incorrect or their account is closed).

- The [transfer-state-change](/api-reference/webhook-event/eventtransfersstatechange) webhook helps you understand the current status of the payment. For example, was the payment already returned to us but we haven’t yet refunded to the customer, or the refund has already been made.
- The [transfer-payout-failure](/api-reference/webhook-event/eventtransferspayoutfailure) webhook allows you to see the specific reason for the bounce back.


## Profile state change

In the event we need to deactivate or reactivate a mutual customer's access to Wise, or set the profile to a view-only or withdraw-only state, we trigger a [Profile state change](/api-reference/webhook-event/eventprofilesstatechange) notification via webhook.

Wise profile deactivation (`DEACTIVATED` state) invalidates any access tokens, refresh tokens, or registration codes you possess for that customer. A symptom of this change can be `401` response errors when you try to generate new access tokens for the customer via `POST /oauth/token`.

Deprecating user state change webhook
The [User state change webhook](/api-reference/webhook-event/eventusersstatechange) previously provided notifications for account-related deactivations, and is now deprecated and will be removed by end 2026.

If you currently rely on the `users#state-change` event notification, create a new webhook subscription for `profiles#state-change`. You can then safely delete the user state change webhook subscription. The states in the `users#state-change` event map to the same states in the `profiles#state-change` event, and the `profiles#state-change` event contains one more `VIEW_ONLY` state that is not available in `users#state-change`.