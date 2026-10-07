# Using webhooks with subscriptions

Learn to use webhooks to receive notifications of subscription activity.

You receive notifications from Stripe in your app through webhook events. Process these events at a webhook endpoint or other destinations like Amazon EventBridge or Azure Event Grid by creating an [event destination](https://docs.stripe.com/events/set-up-events.md). A *subscription* (A Subscription represents the product details associated with the plan that your customer subscribes to. Allows you to charge the customer on a recurring basis) integration requires a destination that handles webhook events, because most subscription activity happens asynchronously.

To use webhooks with your subscriptions:

1. Create a webhook endpoint in your app.
2. Register your [webhook endpoint](https://docs.stripe.com/webhooks.md) in Workbench.
3. Add logic to handle Stripe events. For subscriptions, these include payment failures and subscription status changes (like moving from `trial` to an `active` status). You can use the [webhook quickstart](https://docs.stripe.com/webhooks/quickstart.md) to build a minimal webhook endpoint. Be sure to [verify that incoming events are from Stripe](https://docs.stripe.com/webhooks.md#verify-events).
4. Test your webhook endpoint to confirm that it’s working as expected.

If your application runs on AWS, you can [configure Stripe to send events directly to AWS EventBridge in your AWS account](https://docs.stripe.com/event-destinations/eventbridge.md). If your application runs on Azure, you can [configure Stripe to send events directly to Azure Event Grid in your Azure subscription](https://docs.stripe.com/event-destinations/eventgrid.md).

## Subscription events

Stripe triggers [events](https://docs.stripe.com/api.md#event_types) every time a subscription is created or changed. Some events are sent immediately when a subscription is created, while others recur on regular billing periods.

Make sure that your integration properly handles the events. For example, you might want to email a customer if a payment fails or revoke a customer’s access when a subscription is canceled.

The following table describes the most common events related to subscriptions and, where applicable, suggests actions for handling the events.

> The Accounts v2 API is in GA for Connect users, and in public preview for other Stripe users.
> 
> Regardless of whether you use [Accounts v2](https://docs.stripe.com/accounts-v2/use-accounts-as-customers.md) objects or [Customer](https://docs.stripe.com/api/customers.md) objects to represent your customers, use the `customer.subscription` events to track subscription events.

| Event | Description |
| --- | --- |
| `v2.core.account.created` | Sent when a [v2 Account](https://docs.stripe.com/api/v2/core/accounts/object.md) is successfully created. |
| `customer.created` | Sent when a [Customer](https://docs.stripe.com/api/customers/object.md) is successfully created. |
| `customer.subscription.created` | Sent when the subscription is created. The subscription `status` might be `incomplete` if customer authentication is required to complete the payment or if you set `payment_behavior` to [default_incomplete](https://docs.stripe.com/api/subscriptions/create.md#create_subscription-payment_behavior). |
| `customer.subscription.deleted` | Sent when a customer’s subscription ends. |
| `customer.subscription.paused` | Sent when a subscription’s `status` changes to `paused`. For example, we send this when you [configure](https://docs.stripe.com/api/subscriptions/create.md#create_subscription-trial_settings-end_behavior-missing_payment_method) a subscription to pause when a [free trial ends without a payment method](https://docs.stripe.com/billing/subscriptions/trials/free-trials.md#create-free-trials-without-payment). Invoicing won’t occur until the subscription [resumes](https://docs.stripe.com/api/subscriptions/resume.md). We don’t send this event if you [pause payment collection](https://docs.stripe.com/billing/subscriptions/pause-payment.md) because invoices continue to be created during that time period. |
| `customer.subscription.resumed` | Sent when you resume a subscription previously in a `paused` status. This doesn’t apply when you [unpause payment collection](https://docs.stripe.com/billing/subscriptions/pause-payment.md#unpausing). |
| `customer.subscription.trial_will_end` | Sent 3 days before the [trial period ends](https://docs.stripe.com/billing/subscriptions/trials.md). If the trial is less than 3 days, this event is triggered. |
| `customer.subscription.updated` | Sent when a subscription starts or [changes](https://docs.stripe.com/billing/subscriptions/change.md). For example, renewing a subscription, adding a coupon, applying a discount, adding an invoice item, and changing plans all trigger this event. |
| `entitlements.active_entitlement_summary.updated` | Sent when a customer’s active entitlements are updated. When you receive this event, you can provision or de-provision access to your product’s features. Read more about [integrating with entitlements](https://docs.stripe.com/billing/entitlements.md). |
| `invoice.created` | Sent when an invoice is created for a new or renewing subscription. If Stripe fails to receive a successful response to `invoice.created`, then finalizing all invoices with [automatic collection](https://docs.stripe.com/invoicing/integration/automatic-advancement-collection.md) is delayed for up to 72 hours. Read more about [finalizing invoices](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#finalized).
- Respond to the notification by sending a request to the [Finalize an invoice](https://docs.stripe.com/api/invoices/finalize.md) API. |
| `invoice.finalized` | Sent when an invoice is successfully finalized and ready to be paid.
- You can send the invoice to the customer. View [invoice finalization](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#finalized) to learn more.
- Depending on your settings, we automatically charge the default payment method or attempt collection. View [emails after finalization](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#emails) to learn more. |
| `invoice.finalization_failed` | The invoice failed to finalize. Learn more about [how to handle invoice finalization failures](https://docs.stripe.com/tax/customer-locations.md#finalizing-invoices-with-finalization-failures) and [invoice finalization](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#finalized).
- Inspect the invoice’s [last_finalization_error](https://docs.stripe.com/api/invoices/object.md#invoice_object-last_finalization_error) to determine the cause of the error.
- If you’re using Stripe Tax, check the `Invoice` object’s [automatic_tax](https://docs.stripe.com/api/invoices/object.md#invoice_object-last_finalization_error) field.
- If `automatic_tax[status]=requires_location_inputs`, the invoice fails to finalize and payments can’t be collected. Notify your customer, and collect the required [customer location](https://docs.stripe.com/tax/customer-locations.md).
- If `automatic_tax[status]=failed`, retry the request later. |
| `invoice.paid` | Sent when the invoice is successfully paid. You can provision access to your product when you receive this event and the subscription `status` is `active`. |
| `invoice.payment_action_required` | Sent when the invoice requires customer authentication. Learn how to handle the subscription when the invoice [requires action](https://docs.stripe.com/billing/subscriptions/overview.md#requires-action). |
| `invoice.payment_failed` | A payment for an invoice failed. The PaymentIntent status changes to `requires_action`. The status of the subscription continues to be `incomplete` *only* for the subscription’s first invoice. If a payment fails, you can take several possible actions:

- Notify the customer.
- Configure your [subscription settings](https://dashboard.stripe.com/settings/billing/automatic) in the Dashboard to enable [Smart Retries](https://docs.stripe.com/billing/revenue-recovery/smart-retries.md) and other revenue recovery features.
- If you’re using PaymentIntents, collect new payment information and [confirm the PaymentIntent](https://docs.stripe.com/api/payment_intents/confirm.md).
- Update the [default payment method](https://docs.stripe.com/api/subscriptions/object.md#subscription_object-default_payment_method) on the subscription. |
| `invoice.upcoming` | Sent a few days prior to the renewal of the subscription. The number of days is based on the number set for **Upcoming renewal events** in the [Dashboard](https://dashboard.stripe.com/settings/billing/automatic). For existing subscriptions, changing the number of days takes effect on the next billing period. You can still add [extra invoice items](https://docs.stripe.com/billing/invoices/subscription.md#adding-upcoming-invoice-items), if needed. |
| `invoice.updated` | Sent when a payment succeeds or fails. If payment is successful the `paid` attribute is set to `true` and the `status` is `paid`. If payment fails, `paid` is set to `false` and the `status` remains `open`. Payment failures also trigger  an `invoice.payment_failed` event. |
| `payment_intent.created` | Sent when a [PaymentIntent](https://docs.stripe.com/api/payment_intents.md) is created. |
| `payment_intent.succeeded` | Sent when a PaymentIntent has successfully completed payment. |
| `subscription_schedule.aborted` | Sent when a subscription schedule is canceled because payment delinquency terminated the related subscription. |
| `subscription_schedule.canceled` | Sent when a subscription schedule is canceled, which also cancels any active associated subscription. |
| `subscription_schedule.completed` | Sent when all [phases](https://docs.stripe.com/billing/subscriptions/subscription-schedules.md#subscription-schedule-phases) of a subscription schedule complete. |
| `subscription_schedule.created` | Sent when a new subscription schedule is created. |
| `subscription_schedule.expiring` | Sent 7 days before a subscription schedule is set to expire. |
| `subscription_schedule.released` | Sent when a subscription schedule is [released](https://docs.stripe.com/api/subscription_schedules/release.md), or stopped and disassociated from the subscription, which remains. |
| `subscription_schedule.updated` | Sent when a subscription schedule is updated. |

## Handle risk and customer data events 

The subscription lifecycle events above notify your integration about billing and entitlement changes. If your production integration accepts payments, also handle events for refunds, disputes, and fraud warnings. Otherwise, your integration won’t receive notifications when someone disputes a charge or flags it for potential fraud.

If your integration stores Customer data locally, also consider handling `customer.updated`.

| Event | Why it matters for subscriptions |
| --- | --- |
| `charge.dispute.created` | A customer or their bank disputed a charge. Use this event to decide whether to submit evidence, restrict account access, or take another action. See [Handle refund, dispute, and early fraud warning events](https://docs.stripe.com/billing/subscriptions/webhooks.md#refund-events) to resolve the associated subscription. |
| `charge.refunded` | A charge associated with a subscription invoice received a full or partial refund. See [Handle refund, dispute, and early fraud warning events](https://docs.stripe.com/billing/subscriptions/webhooks.md#refund-events) to resolve the associated subscription. |
| `radar.early_fraud_warning.created` | A card issuer or network identified a charge as potentially fraudulent, typically before a formal dispute. See [Handle refund, dispute, and early fraud warning events](https://docs.stripe.com/billing/subscriptions/webhooks.md#refund-events) to resolve the associated subscription. |
| `customer.updated` | Stripe sends this event when any property of a [Customer](https://docs.stripe.com/api/customers/object.md) changes. [Customer Portal](https://docs.stripe.com/customer-management.md) flows can update Customer-level details, such as billing information or the default payment method. Listen for this event if you store Customer data locally or depend on Customer field changes. If you use [Accounts v2](https://docs.stripe.com/accounts-v2/use-accounts-as-customers.md) to represent customers, listen for `v2.core.account[configuration.customer].updated` for customer configuration changes and `v2.core.account[identity].updated` for identity changes instead. |

Subscribe only to the events your integration requires. If you omit risk events, your application won’t learn about disputes or fraud warnings until you check the Dashboard.

## Handle payment failures 

Events provide a reliable way for Stripe to notify you of payment failures on subscription invoices. Some payment failures are temporary-for example, a card issuer might decline the initial charge but allow an automatic retry. Other payment failures are final and require action, like not having a usable payment method for the customer.

| Event | Description |
| --- | --- |
| `invoice.payment_failed` | A payment for an invoice failed. The status of the PaymentIntent changes to `requires_payment_method`. The status of the subscription changes to `incomplete`. If a payment fails, there are several possible actions to take:

- Notify the customer.
- If you’re using PaymentIntents, collect new payment information and [confirm the PaymentIntent](https://docs.stripe.com/api/payment_intents/confirm.md).
- Update the [default payment method](https://docs.stripe.com/api/subscriptions/object.md#subscription_object-default_payment_method) on the subscription.
- Consider enabling [Smart Retries](https://docs.stripe.com/billing/revenue-recovery/smart-retries.md). |

## Handle payments that require additional action 

Some payment methods might require additional steps to complete, such as customer authentication. If you receive these events, your app must notify the customer to complete the required action. To learn how to [handle events that require additional action](https://docs.stripe.com/billing/subscriptions/overview.md#requires-action), read the subscription overview guide.

| Event | Description |
| --- | --- |
| `invoice.finalization_failed` | The invoice couldn’t be finalized. Learn how to [handle invoice finalization failures](https://docs.stripe.com/tax/customer-locations.md#finalizing-invoices-with-finalization-failures) by reading the guide. Learn more about [invoice finalization](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#finalized) in the invoices overview guide.
- Inspect the Invoice’s [last_finalization_error](https://docs.stripe.com/api/invoices/object.md#invoice_object-last_finalization_error) to determine the cause of the error.
- If you’re using Stripe Tax, check the Invoice object’s [automatic_tax](https://docs.stripe.com/api/invoices/object.md#invoice_object-automatic_tax) field.
- If `automatic_tax[status]=requires_location_inputs`, the invoice can’t be finalized and payments can’t be collected. Notify your customer and collect the required [customer location](https://docs.stripe.com/tax/customer-locations.md).
- If `automatic_tax[status]=failed`, retry the request later. |
| `invoice.payment_failed` | A payment for an invoice failed. The PaymentIntent status changes to `requires_action`. The status of the subscription changes to `incomplete`. If a payment fails, there are several possible actions to take:

- Notify the customer.
- If you’re using PaymentIntents, collect new payment information and [confirm the PaymentIntent](https://docs.stripe.com/api/payment_intents/confirm.md).
- Update the [default payment method](https://docs.stripe.com/api/subscriptions/object.md#subscription_object-default_payment_method) on the subscription.
- Consider enabling [Smart Retries](https://docs.stripe.com/billing/revenue-recovery/smart-retries.md). |
| `invoice.payment_action_required` | Sent when the invoice requires customer authentication. Learn how to handle the subscription when the invoice [requires action](https://docs.stripe.com/billing/subscriptions/overview.md#requires-action). |

## Handle refund, dispute, and early fraud warning events 

When a charge associated with a subscription is refunded, disputed, or flagged for fraud, Stripe sends one of the following events:

- `charge.refunded`: Contains the updated [Charge](https://docs.stripe.com/api/charges/object.md).
- `charge.dispute.created`: Contains a [Dispute](https://docs.stripe.com/api/disputes/object.md), which exposes [charge](https://docs.stripe.com/api/disputes/object.md#dispute_object-charge) and a nullable [payment_intent](https://docs.stripe.com/api/disputes/object.md#dispute_object-payment_intent).
- `radar.early_fraud_warning.created`: Contains an [EarlyFraudWarning](https://docs.stripe.com/api/radar/early_fraud_warnings/object.md), which exposes [charge](https://docs.stripe.com/api/radar/early_fraud_warnings/object.md#early_fraud_warning_object-charge) and a nullable [payment_intent](https://docs.stripe.com/api/radar/early_fraud_warnings/object.md#early_fraud_warning_object-payment_intent).

Some charges and PaymentIntents aren’t associated with an invoice or subscription. How you identify the subscription depends on your API version.

### API version 2025-03-31.basil or later 

1. Get the [PaymentIntent](https://docs.stripe.com/api/payment_intents/object.md) ID. For `charge.refunded`, use the [payment_intent](https://docs.stripe.com/api/charges/object.md#charge_object-payment_intent) field on the Charge. For `charge.dispute.created` or `radar.early_fraud_warning.created`, use the `payment_intent` field on the Dispute or EarlyFraudWarning object. If `payment_intent` is null, [retrieve the Charge](https://docs.stripe.com/api/charges/retrieve.md) and use its [payment_intent](https://docs.stripe.com/api/charges/object.md#charge_object-payment_intent) field. If the Charge also has no `payment_intent` (for example, a legacy direct charge), this procedure doesn’t apply.
2. Use the [List all payments for an invoice](https://docs.stripe.com/api/invoice-payment/list.md) endpoint with [payment.type](https://docs.stripe.com/api/invoice-payment/list.md#list_invoice_payments-payment-type) set to `payment_intent`, [payment.payment_intent](https://docs.stripe.com/api/invoice-payment/list.md#list_invoice_payments-payment-payment_intent) set to the PaymentIntent ID, and [status](https://docs.stripe.com/api/invoice-payment/list.md#list_invoice_payments-status) set to `paid`. If the list is empty, this procedure can’t resolve an associated invoice.
3. A PaymentIntent can be associated with multiple invoices, so this endpoint may return more than one `InvoicePayment`. Paginate through all results while `has_more` is true—each `InvoicePayment` contains an [invoice](https://docs.stripe.com/api/invoice-payment/object.md#invoice_payment_object-invoice) field with the associated Invoice ID.
4. For each Invoice ID, retrieve the Invoice and verify [parent.type](https://docs.stripe.com/api/invoices/object.md#invoice_object-parent-type) is `subscription_details`. Then use [parent.subscription_details.subscription](https://docs.stripe.com/api/invoices/object.md#invoice_object-parent-subscription_details-subscription) to get the [Subscription](https://docs.stripe.com/api/subscriptions/object.md).

### API versions earlier than 2025-03-31.basil 

On older API versions, the Charge object includes an [invoice](https://docs.stripe.com/api/charges/object.md?api-version=2025-02-24.acacia#charge_object-invoice) field.

1. Get the Charge. For `charge.refunded`, use the Charge from the event. For `charge.dispute.created` or `radar.early_fraud_warning.created`, the `charge` field on the Dispute or EarlyFraudWarning is an ID. [Retrieve the Charge](https://docs.stripe.com/api/charges/retrieve.md) using that ID.
2. If the Charge’s `invoice` field is null, this procedure can’t resolve an associated invoice. Otherwise, retrieve the Invoice and use its [subscription](https://docs.stripe.com/api/invoices/object.md?api-version=2025-02-24.acacia#invoice_object-subscription) field to get the Subscription.

## Track active subscriptions 

Subscriptions require coordination between your site and Stripe-the success or failure of a customer’s recurring payments determines whether they can continue to access your product or service.

For typical integrations, you store customers’ credentials and a mapped timestamp value that represents the access expiration date for that customer on your site when a customer subscribes. When the customer logs in, you check whether the timestamp is still in the future. If the timestamp is in the future when the customer logs in, the account is active and the customer should still have access to the service.

When the subscription [renews](https://docs.stripe.com/billing/subscriptions/overview.md#subscription-lifecycle), Stripe bills the customer and tries to collect payment by either [automatically charging](https://docs.stripe.com/invoicing/automatic-charging.md) the payment method on file, or [emailing the invoice](https://docs.stripe.com/invoicing/integration.md#accept-invoice-payment) to customers. Stripe notifies your site of the invoice status by sending a webhook event:

1. Your site receives an `invoice.paid` event.

   - When automatically charging a payment method, your site first receives an `invoice.upcoming` event to your configured [webhook endpoint](https://docs.stripe.com/webhooks.md) a few days before renewal. You can listen for this event to [add extra invoice items](https://docs.stripe.com/billing/invoices/subscription.md#adding-upcoming-invoice-items) to the upcoming invoice. If `collection_method=send_invoice`, Stripe doesn’t send an `invoice.upcoming` event.

2. Your application finds the customer the payment was made for.

3. After receiving `invoice.paid`, retrieve the associated subscription and confirm that its status is `active` before extending the customer’s access expiration date. A paid invoice doesn’t necessarily transition the subscription to `active` when status resolution uses all invoices.

## Catch subscription status changes 

Make sure that your integration properly monitors and handles transitions between the subscription statuses described in the following table.

Some status changes require special attention:

- A few days before a trial ends and the subscription moves from `trialing` to `active`, you receive a `customer.subscription.trial_will_end` event. When you receive this event, verify that you have a payment method on the customer so you can bill them. Optionally, notify the customer that they will be charged.

- When a subscription changes to `past_due`, notify the customer directly and ask them to update their payment details. Stripe offers several features that help automate this process-read more about [revenue recovery](https://docs.stripe.com/billing/revenue-recovery.md).

- When a subscription changes to `canceled` or `unpaid`, revoke access to your product.

| Status | Description |
| --- | --- |
| `trialing` | The subscription is currently in a trial period and you can safely provision your product for your customer. The subscription transitions automatically to `active` when a customer makes the first payment. |
| `active` | The subscription is in good standing. Your [subscription settings](https://dashboard.stripe.com/settings/billing/subscriptions#manage-failed-payments) determine which invoices must be settled to transition a `past_due` subscription to `active`. When status resolution uses the most recent invoice, Stripe uses the most recent non-voided invoice to determine the subscription’s status. Paying that invoice or manually marking it as uncollectible transitions the subscription to `active`. When status resolution uses all invoices, settle all applicable outstanding invoices to transition the subscription to `active`.

`active` doesn’t necessarily indicate that all outstanding invoices associated with the subscription have been paid. When status resolution uses the most recent invoice, you can leave other outstanding invoices open for payment, mark them as uncollectible, or void them as you see fit. |
| `incomplete` | The customer must make a successful payment within 23 hours to activate the subscription. Or the payment [requires action](https://docs.stripe.com/billing/subscriptions/overview.md#requires-action), such as customer authentication. Subscriptions can also be `incomplete` if there’s a pending payment and the PaymentIntent status is `processing`. |
| `incomplete_expired` | The initial payment on the subscription failed and the customer didn’t make a successful payment within 23 hours of subscription creation. These subscriptions don’t bill customers. This status exists so you can track customers that failed to activate their subscriptions. |
| `past_due` | Payment on the latest finalized invoice either failed or wasn’t attempted. When status resolution uses all invoices, `past_due` can also indicate that an earlier applicable invoice remains outstanding. The subscription continues to create invoices. Stripe might retry payment while the subscription is `past_due`, but this status doesn’t guarantee another payment attempt. Your Dashboard [subscription settings](https://dashboard.stripe.com/settings/billing/subscriptions#manage-failed-payments) determine the subscription’s next status. If an invoice is still unpaid after all [payment retries](https://docs.stripe.com/billing/revenue-recovery/smart-retries.md), you can configure the subscription to move to `canceled` or `unpaid`, or to remain `past_due`.

To reactivate the subscription, pay the most recent non-voided invoice or manually mark it as uncollectible when status resolution uses the most recent invoice, or settle applicable outstanding invoices when status resolution uses all invoices. The subscription becomes `active` regardless of whether you settle the required invoices before or after their due dates. |
| `canceled` | The subscription was canceled. During cancellation, automatic collection for all unpaid invoices is disabled (`auto_advance=false`). This is a terminal state that can’t be updated. |
| `unpaid` | Stripe sets a subscription’s status to `unpaid` only when your Dashboard [subscription settings](https://dashboard.stripe.com/settings/billing/subscriptions#manage-failed-payments) select this outcome. The invoice or invoices governing subscription status haven’t been settled, but the subscription remains in place. The subscription continues to generate invoices but doesn’t attempt payment. Revoke access to your product when the subscription is `unpaid` because Stripe already attempted and retried payment while the subscription was `past_due`. To move the subscription to `active`, pay the most recent non-voided invoice or manually mark it as uncollectible when status resolution uses the most recent invoice, or settle applicable outstanding invoices when status resolution uses all invoices. |
| `paused` | The subscription has ended its trial period without a default payment method and the [trial_settings.end_behavior.missing_payment_method](https://docs.stripe.com/billing/subscriptions/trials/free-trials.md#create-free-trials-without-payment) is set to `pause`. Invoices are no longer created for the subscription. After attaching a default payment method to the customer, you can [resume the subscription](https://docs.stripe.com/billing/subscriptions/trials/free-trials.md#resume-a-paused-subscription). |

## Webhook endpoints and invoices 

Register a webhook endpoint to keep track of invoice statuses. Your subscription integration depends on correctly finalizing invoices and properly handling invoice finalization failures.

When you enable [automatic collection](https://docs.stripe.com/invoicing/integration/automatic-advancement-collection.md), Stripe automatically finalizes and begins automatic collection of the [invoice](https://docs.stripe.com/billing/invoices/subscription.md).

- If Stripe fails to receive a successful response to `invoice.created`, we delay finalizing all invoices with [automatic collection](https://docs.stripe.com/invoicing/integration/automatic-advancement-collection.md) for up to 72 hours, excluding those where you have [set a custom scheduled finalization time](https://docs.stripe.com/invoicing/scheduled-finalization.md).
- Responding properly to `invoice.created` includes handling all webhook endpoints configured for your account, along with the webhook endpoints of any platforms that you’ve connected to. This doesn’t include any webhook endpoints configured in an [organization](https://docs.stripe.com/get-started/account/orgs.md). While you can listen to `invoice.created` at the organization, a successful response doesn’t affect invoice finalization when using automatic collection.
- Updating a subscription in a way that synchronously attempts payment (on the initial invoice, and on some kinds of updates) doesn’t cause this delay.
- Invoice finalization failure prevents payment collection for the invoice. Make sure you listen for the `invoice.finalization_failed` event in your webhook endpoint.

### Webhook events related to invoice finalization

See a complete list of [invoice event types](https://docs.stripe.com/api/events/types.md#event_types-invoice.created).

| Event | Description |
| --- | --- |
| `invoice.created` | The invoice was successfully created and is ready to be finalized. Read the docs to learn more about [finalizing invoices](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#finalized).
- Respond to the notification by sending a request to the [Finalize an invoice](https://docs.stripe.com/api/invoices/finalize.md) API. |
| `invoice.finalized` | The invoice was successfully finalized and is ready to be paid.
- You can send the invoice to the customer. Read more about [invoice finalization](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#finalized).
- Depending on your settings, Stripe automatically charges the default payment method or attempts collection. Read more about [emails after finalization](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#emails). |
| `invoice.finalization_failed` | The invoice couldn’t be finalized. Learn how to [handle invoice finalization failures](https://docs.stripe.com/tax/customer-locations.md#finalizing-invoices-with-finalization-failures) by reading the guide. Learn more about [invoice finalization](https://docs.stripe.com/invoicing/integration/workflow-transitions.md#finalized) in the invoices overview guide.
- Inspect the Invoice’s [last_finalization_error](https://docs.stripe.com/api/invoices/object.md#invoice_object-last_finalization_error) to determine the cause of the error.
- If you’re using Stripe Tax, check the Invoice object’s [automatic_tax](https://docs.stripe.com/api/invoices/object.md#invoice_object-last_finalization_error) field.
- If `automatic_tax[status]=requires_location_inputs`, the invoice can’t be finalized and payments can’t be collected. Notify your customer and collect the required [customer location](https://docs.stripe.com/tax/customer-locations.md).
- If `automatic_tax[status]=failed`, retry the request later. |

### Successful invoice finalization

Stripe waits an hour after receiving a successful response to the `invoice.created` event before attempting payment. If we don’t receive a successful response within 72 hours, we attempt to finalize and send the invoice.

In case you want to treat one-off invoices differently than subscription invoices, check the `subscription` property in the webhook body. This indicates whether the invoice was created for a subscription.

In live mode, if your webhook endpoint doesn’t respond properly, Stripe continues retrying the webhook notification for up to 3 days with an exponential back off. In a sandbox, we retry three times over a few hours. During that time, we won’t attempt to charge the customer unless we receive a successful response. We’ll also send you an email to notify you that the webhook is failing.

This behavior applies to all webhook endpoints defined on your account, including cases where a [Connect application](https://stripe.com/works-with) or other third-party service is having trouble handling incoming webhooks.

### Invoice finalization failure

If Stripe can’t finalize an invoice, it sends a `invoice.finalization_failed` [event](https://docs.stripe.com/api/events/types.md#event_types-invoice.finalization_failed) to your webhook endpoint. Subscriptions remain active if invoices can’t be finalized, which means that users may still be able to access your product while you’re not able to collect payments. Make sure to take action on invoices that fail finalization. You can’t collect payments on an invoice that isn’t finalized.

To determine why the invoice finalization failed, look at the Invoice object’s `last_finalization_error` [field](https://docs.stripe.com/api/invoices/object.md#invoice_object-last_finalization_error), which provides more information about the failure, including how to proceed.

If you’re using Stripe Tax, check if the [automatic_tax.status](https://docs.stripe.com/api/invoices/object.md#invoice_object-automatic_tax-status) field is `requires_location_inputs`, indicating that the address details are invalid or insufficient. If Stripe Tax can’t find a recognized customer location, we can’t finalize the invoice. Learn how to [handle invoice finalization failures](https://docs.stripe.com/tax/customer-locations.md#finalizing-invoices-with-finalization-failures).

## Testing 

To test your webhook endpoint or [event destination](https://docs.stripe.com/events/how-events-work.md), choose one of these two options:

1. Perform actions in a sandbox that trigger real events to your event destination. For example, to trigger the [charge.succeeded](https://docs.stripe.com/api.md#event_types-charge.succeeded) event, you can use a [test card that produces a successful charge](https://docs.stripe.com/testing.md#cards).
2. [Trigger events using the Stripe CLI](https://docs.stripe.com/webhooks.md#test-webhook) or [using Stripe for Visual Studio Code](https://docs.stripe.com/stripe-vscode.md#webhooks).

## See also

- [Subscription lifecycle](https://docs.stripe.com/billing/subscriptions/overview.md#subscription-lifecycle)
- [Testing subscriptions](https://docs.stripe.com/billing/testing.md)
