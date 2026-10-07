# Configure trial offers on subscriptions

Offer free or paid trials for items in a subscription.
![](https://b.stripecdn.com/docs-statics-srv/assets/trial-offer.2128af954f90482fce40e29d1604a01b.png)

Use the [Trial Offer](https://docs.stripe.com/api/product-catalog/trial-offer.md?api-version=2026-09-30.endive) API to manage both free and paid introductory periods for your [subscriptions](https://docs.stripe.com/subscriptions.md) with a single API integration. Trial offers enable you to qualify high-intent leads, reduce trial abuse, and provide discounted rates to your customers for a limited duration (for example, 1 USD for the first week of an offer).

## Use cases

With trial offers, you can run promotional pricing and product offering experiments directly in Stripe. Common use cases for trial offers include:

| Use case | Description |
| --- | --- |
| **Discounted trials** | To improve trial-to-paid conversion and generate revenue, you can set up discounted trials. For example, you offer a reduced introductory price of 4 USD for 4 weeks or a free 7-day trial. |
| **Free trials** | To offer a free trial subscription, include a 0 USD item in the subscription. |
| **Upgrade trials** | To upsell premium features, you can configure upgrade trials. For example, you offer a customer on a basic plan a 7-day trial to access premium features at the basic rate. Then, when the trial ends, you automatically convert them to the premium rate. |
| **Item-level trials** | To sell add-ons, AI packs, and other feature bundles, you can set up item-level trials. You can offer customers a trial for a single line item in a subscription while billing other items at their regular price. |

## Before you begin

- Your integration must use [2026-09-30.endive](https://docs.stripe.com/changelog.md#2026-09-30.endive) or later. Specify this [Stripe version](https://docs.stripe.com/api/versioning.md) in your request header.
- To use trial offers, you must create new subscriptions with the billing mode set to [flexible](https://docs.stripe.com/billing/subscriptions/billing-mode.md#create-a-new-subscription-with-flexible-billing-mode), or update existing subscriptions that use `classic` billing mode to use `flexible` instead.

### Limitations

**Integration restrictions**

- Trial offers are supported when creating or updating subscriptions in the Dashboard or with the Subscriptions API. The following UI integrations don’t support trial offers:

  - [Checkout](https://docs.stripe.com/payments/checkout.md) (instead use [legacy free trials](https://docs.stripe.com/payments/checkout/free-trials.md) with `trial_end`)
  - [Payment Links](https://docs.stripe.com/payment-links.md)
  - [Elements with Checkout Sessions](https://docs.stripe.com/payments/elements.md)

- You can’t use trial offers and the legacy `trial_end` parameter together. We recommend using the Trial Offer API to configure discounted trials and free trials. To choose between a trial offer and a subscription free trial period, [compare free trial periods and trial offers](https://docs.stripe.com/billing/subscriptions/trials/compare.md).

**Dashboard limitations**

- Trial offers with subscription schedules are in public preview and aren’t supported in the Dashboard. Use the API to manage them.
- You can use the customer portal to view and cancel trial offers. You can also reactivate subscriptions with trial offers. You can’t update, pause, or resume subscriptions with trial offers.

**Billing and analytics limitations**

- Trial offers apply to recurring subscription items only. Non-recurring items aren’t eligible for paid trials or discounted trial pricing.
- You can’t modify the trial length after you create the subscription or schedule trial extensions and reductions.
- You must make the post-trial price different from any price already on the subscription.
- Stripe removes the trial offer from the subscription after the trial ends.
- There’s no native way to schedule deletion of a single subscription item when its trial ends.
- In [Billing Analytics](https://docs.stripe.com/billing/subscriptions/analytics.md), trial offer items don’t contribute to MRR while they are in a trial period. Other items on the same subscription continue to contribute to MRR.

## How trial offers work

A subscription charges a customer for a product, at the specified price, on a recurring basis. When you create a trial offer, you specify a trial price and a duration of the trial for a product. When the trial ends, the subscription automatically transitions to the regular price or another price you configure.

> You need two separate recurring Price objects to create a trial offer—one for the trial period and one for the post-trial period.

Trial offers don’t replace [products or prices](https://docs.stripe.com/products-prices/how-products-and-prices-work.md). `Trial Offer` is a separate object that attaches a discounted or free price to a [Subscription item](https://docs.stripe.com/api/subscription_items.md) for a limited time. The item’s [price](https://docs.stripe.com/api/subscription_items/object.md?#subscription_item_object-price) is the trial price while the trial is active and the transition price after it ends.

## Create a trial offer

#### Dashboard

To create a trial offer in the Dashboard:

1. Go to the [Products](https://dashboard.stripe.com/products) page.
2. Click a product to open the product details page.
3. In the **Trials** section, click the plus symbol (+).
4. Fill in the **Create trial** dialog with the trial price, duration, and end behavior.
5. Click **Create**.

You can also create a trial offer from the subscription editor:

1. Go to the [Subscriptions](https://dashboard.stripe.com/subscriptions) page.
2. Click **+ Create subscription**, or click an existing subscription and select **Actions** > **Update subscription**.
3. Click **Add trial**.
4. In the dialog, select **+ Trial** to create a new trial offer.
5. Add the trial details, including the trial price, duration, and end behavior.
6. Click **Create**.

#### API

To [create a trial offer](https://docs.stripe.com/api/product-catalog/trial-offer/create.md?api-version=2026-09-30.endive), pass a [price](https://docs.stripe.com/api/product-catalog/trial-offer/create.md?api-version=2026-09-30.endive#create_product_catalog_trial_offer-price) using the [price.id](https://docs.stripe.com/api/prices/object.md#price_object-id) to define the cost during the trial period. You can set this to 0 USD for free trials or any positive amount for paid trials.

Set the trial [duration.type](https://docs.stripe.com/api/product-catalog/trial-offer/create.md?api-version=2026-09-30.endive#create_product_catalog_trial_offer-duration-type) to `relative`, and use [duration.relative.iterations](https://docs.stripe.com/api/product-catalog/trial-offer/create.md?api-version=2026-09-30.endive#create_product_catalog_trial_offer-duration-relative-iterations) to define the number of billing intervals.

Then, use [end_behavior.transition.price](https://docs.stripe.com/api/product-catalog/trial-offer/create.md?api-version=2026-09-30.endive#create_product_catalog_trial_offer-end_behavior-transition-price) to specify the price that the subscription uses when the trial ends. Optionally, set `nickname` to add an internal label for the trial offer.

### Create a trial offer with a relative duration

```curl
curl https://api.stripe.com/v1/product_catalog/trial_offers \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d price=price_trial \
  -d "duration[relative][iterations]=1" \
  -d "duration[type]=relative" \
  -d "end_behavior[transition][price]=price_regular"
```

### Create a trial offer with a timestamp duration

> Timestamp trial offer durations are in [public preview](https://docs.stripe.com/release-phases.md). Functionality might change during development.

```curl
curl https://api.stripe.com/v1/product_catalog/trial_offers \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-03-25.preview" \
  -d price=price_trial \
  -d "duration[type]=timestamp" \
  -d "end_behavior[transition][price]=price_regular"
```

To archive a trial offer and prevent it from being used on new subscriptions, [set `active` to `false`](https://docs.stripe.com/api/product-catalog/trial-offer/update.md?api-version=2026-09-30.endive). Set it to `true` to unarchive it.

## Attach a trial offer to a new subscription

#### Dashboard

To attach a trial offer to a new subscription in the Dashboard:

1. Go to the [Subscriptions](https://dashboard.stripe.com/subscriptions) page.
2. Click **+ Create subscription**.
3. Click **Add trial**.
4. In the dialog, select an existing trial offer, or select **New Trial** to create a new trial offer to add to the subscription.

#### API

To attach a trial offer to a [subscription](https://docs.stripe.com/api/subscriptions/object.md), specify the [trial_offer.id](https://docs.stripe.com/api/product-catalog/trial-offer/object.md?api-version=2026-09-30.endive#product_catalog_trial_offer_object-id) in the [items.current_trial.trial_offer](https://docs.stripe.com/api/subscriptions/update.md#update_subscription-items-current_trial) parameter:

#### Accounts v2

```curl
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "customer_account={{CUSTOMERACCOUNT_ID}}" \
  -d "billing_mode[type]=flexible" \
  -d "items[0][current_trial][trial_offer]=to_123" \
  -d "items[0][quantity]=1"
```

#### Customer v1

```curl
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "customer={{CUSTOMER_ID}}" \
  -d "billing_mode[type]=flexible" \
  -d "items[0][current_trial][trial_offer]=to_123" \
  -d "items[0][quantity]=1"
```

## Update subscriptions with a trial offer

### Add a trial offer to an existing subscription

#### Dashboard

To add a trial offer to an existing subscription in the Dashboard:

1. Go to the [Subscriptions](https://dashboard.stripe.com/subscriptions) page.
2. Click the subscription to update, then select **Actions** > **Update subscription**.
3. Click **Add trial**.
4. In the dialog, select an existing trial offer, or select **+ Trial** to create a new trial offer to add to the subscription.

#### API

To add a trial offer to an existing subscription, specify the [trial_offer.id](https://docs.stripe.com/api/product-catalog/trial-offer/object.md?api-version=2026-09-30.endive#product_catalog_trial_offer_object-id) in the [items.current_trial.trial_offer](https://docs.stripe.com/api/subscriptions/update.md#update_subscription-items-current_trial) parameter:

```curl
curl https://api.stripe.com/v1/subscriptions/{{SUBSCRIPTION_ID}} \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "items[0][current_trial][trial_offer]=to_123"
```

### Add a trial offer to a subscription with existing items

#### Dashboard

To add a trial offer as another item to a subscription that has existing items in the Dashboard:

1. Go to the [Subscriptions](https://dashboard.stripe.com/subscriptions) page.
2. Click the subscription to update, then select **Actions** > **Update subscription**.
3. Click **Add trial**.
4. In the dialog, select an existing trial offer, or select **+ Trial** to create a new trial offer to add to the subscription.

#### API

To add a trial offer as another item to a subscription that has existing items, add an item to the [items](https://docs.stripe.com/api/subscriptions/update.md#update_subscription-items) array and specify the [trial_offer.id](https://docs.stripe.com/api/product-catalog/trial-offer/object.md?api-version=2026-09-30.endive#product_catalog_trial_offer_object-id) in the [items.current_trial.trial_offer](https://docs.stripe.com/api/subscriptions/update.md#update_subscription-items-current_trial) parameter:

```curl
curl https://api.stripe.com/v1/subscriptions/{{SUBSCRIPTION_ID}} \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "items[0][id]={{SUBSCRIPTIONITEM_ID}}" \
  -d "items[1][current_trial][trial_offer]=to_123" \
  -d "items[1][quantity]=1"
```

### Convert a subscription item to a trial offer

To convert an existing subscription item to a trial offer, include the [items.id](https://docs.stripe.com/api/subscriptions/update.md#update_subscription-items-id) and specify the [trial_offer.id](https://docs.stripe.com/api/product-catalog/trial-offer/object.md?api-version=2026-09-30.endive#product_catalog_trial_offer_object-id) in the [items.current_trial.trial_offer](https://docs.stripe.com/api/subscriptions/update.md#update_subscription-items-current_trial) parameter:

```curl
curl https://api.stripe.com/v1/subscriptions/{{SUBSCRIPTION_ID}} \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "items[0][id]={{SUBSCRIPTIONITEM_ID}}" \
  -d "items[0][current_trial][trial_offer]=to_123"
```

### Change the item quantity for a trial offer

#### Dashboard

To change the item quantity for a trial offer in the Dashboard:

1. Go to the [Subscriptions](https://dashboard.stripe.com/subscriptions) page.
2. Click the subscription to update, then select **Actions** > **Update subscription**.
3. Edit the quantity field after adding the trial offer item.
4. Click **Update subscription**.

#### API

To change the item [quantity](https://docs.stripe.com/api/subscriptions/update.md#update_subscription-items-quantity) for a trial offer, update the subscription:

```curl
curl https://api.stripe.com/v1/subscriptions/{{SUBSCRIPTION_ID}} \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "items[0][id]={{SUBSCRIPTIONITEM_ID}}" \
  -d "items[0][quantity]=2"
```

## Add a trial offer to a subscription schedule

> Trial offers with subscription schedules are in [public preview](https://docs.stripe.com/release-phases.md). Functionality might change during development.

You can only use timestamp trial offers with [subscription schedules](https://docs.stripe.com/api/subscription_schedules.md?api-version=2026-03-25.preview). Unlike relative duration trials, which end after a set number of billing intervals, timestamp trials end on an absolute date. To create one, set the trial offer’s [duration.type](https://docs.stripe.com/api/product-catalog/trial-offer/object.md?api-version=2026-03-25.preview#product_catalog_trial_offer_object-duration-type) to `timestamp`:

```curl
curl https://api.stripe.com/v1/product_catalog/trial_offers \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-03-25.preview" \
  -d price=price_trial \
  -d "duration[type]=timestamp" \
  -d "end_behavior[transition][price]=price_regular"
```

Next, use [phases.items.trial_offer](https://docs.stripe.com/api/subscription_schedules/create.md?api-version=2026-03-25.preview#create_subscription_schedule-phases-items-trial_offer) to attach the trial offer to the schedule [phase](https://docs.stripe.com/api/subscription_schedules/create.md?api-version=2026-03-25.preview#create_subscription_schedule-phases) of the subscription schedule:

#### Accounts v2

```curl
curl https://api.stripe.com/v1/subscription_schedules \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-03-25.preview" \
  -d "customer_account={{CUSTOMERACCOUNT_ID}}" \
  -d start_date=1610403705 \
  -d "phases[0][items][0][trial_offer]=to_123" \
  -d "phases[0][end_date]=1610403706"
```

#### Customer v1

```curl
curl https://api.stripe.com/v1/subscription_schedules \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-03-25.preview" \
  -d "customer={{CUSTOMER_ID}}" \
  -d start_date=1610403705 \
  -d "phases[0][items][0][trial_offer]=to_123" \
  -d "phases[0][end_date]=1610403706"
```

## View subscriptions with trial offers

When you [retrieve a subscription](https://docs.stripe.com/api/subscriptions/retrieve.md), the response includes the configuration for each item, including trial offers:

```curl
curl https://api.stripe.com/v1/subscriptions/{{SUBSCRIPTION_ID}} \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive"
```

## Cancel a subscription at the end of a paid trial

To cancel the subscription when the paid trial ends:

1. Create a subscription with a trial offer.
2. Set the cancellation date to the end of the trial period.

This flow supports opt-in renewals, so customers aren’t automatically converted to a recurring subscription by default.

#### Dashboard

To cancel a subscription at the end of a paid trial in the Dashboard:

1. On the [Subscriptions](https://dashboard.stripe.com/subscriptions) page, find the applicable subscription, click the overflow menu (⋯), and select **Cancel subscription**.
2. Select **On a custom day** and set the date to end the trial and the subscription.
3. Click **Cancel subscription**.

For more information, see [Cancel subscriptions](https://docs.stripe.com/billing/subscriptions/cancel.md#canceling).

#### API

To cancel a subscription at the end of a paid trial, set the [cancel_at](https://docs.stripe.com/api/subscriptions/update.md?#update_subscription-cancel_at) parameter to the end of the trial period:

#### Accounts v2

```curl
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "customer_account={{CUSTOMERACCOUNT_ID}}" \
  -d "items[0][current_trial][trial_offer]=to_123" \
  -d "items[0][quantity]=1" \
  -d cancel_at=1610403706
```

#### Customer v1

```curl
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "customer={{CUSTOMER_ID}}" \
  -d "items[0][current_trial][trial_offer]=to_123" \
  -d "items[0][quantity]=1" \
  -d cancel_at=1610403706
```

## Use trial offers with other features

### Trial offers with usage-based billing

When creating a [Price](https://docs.stripe.com/api/prices/object.md) object, you can specify a metered price instead of a recurring price and attach it to a trial offer. This lets you offer the same [usage-based billing](https://docs.stripe.com/billing/subscriptions/usage-based.md) functionality at a discounted price.

To use a metered price, set the [usage_type](https://docs.stripe.com/api/prices/object.md?#price_object-recurring-usage_type) to `metered` and add an existing [meter](https://docs.stripe.com/api/prices/object.md?#price_object-recurring-meter) to track usage.

```curl
curl https://api.stripe.com/v1/prices \
  -u "<<YOUR_SECRET_KEY>>:" \
  -d currency=usd \
  -d billing_scheme=per_unit \
  -d unit_amount=1 \
  -d "recurring[interval]=week" \
  -d "recurring[usage_type]=metered" \
  -d "recurring[meter]=mtr_123" \
  -d "product_data[name]=Trial Period Price"
```

Next, attach the price to a trial offer as you would with any other recurring price:

```curl
curl https://api.stripe.com/v1/product_catalog/trial_offers \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d price=price_trial \
  -d "duration[relative][iterations]=1" \
  -d "duration[type]=relative" \
  -d "end_behavior[transition][price]=price_regular"
```

## Additional considerations

### Subscription trialing status and trial offer

When using trial offers, a subscription’s `status` is determined by the price of the trial:

- **Free Trials (0 USD)**: If a subscription only contains trial offers, and all trial offer prices are set to 0 USD, the subscription status is `trialing`. This matches the legacy `trial_end` behavior and is ideal for “no-card-required” or standard free trial flows.
- **Paid Trials (>0 USD)**: If the subscription has a regular price item, or the trial offers have a non-zero price, the subscription status will be `active`, `incomplete`, or `past_due`. This behavior mimics other subscriptions without trial offers. Because a paid trial requires an immediate successful payment to begin, the subscription follows the standard `PaymentIntent` lifecycle. This ensures that your existing billing logic—such as webhooks for successful payments—remains consistent, whether the customer is paying a promotional price or the full recurring amount.

### Events

Every time a trial changes, it triggers [Events](https://docs.stripe.com/api.md#event_types). Make sure that your integration handles them. For example, you might want to email a customer before a trial ends. Learn more about [handling subscription events](https://docs.stripe.com/billing/subscriptions/webhooks.md#events).

The following table describes the events that trigger before a trial ends, when a trial subscription pauses or cancels, and when a subscription resumes and becomes active.

| Event | Description | Use case |
| --- | --- | --- |
| `customer.subscription.deleted` | Sent when a subscription ends. | Stop providing access to your product in response to this event. The subscription moves to the `canceled` status and sends this event after a trial ends without a payment method, if the subscription’s `missing_payment_method` end behavior is set to `cancel`. |
| `customer.subscription.resumed` | Sent when a subscription is no longer paused. When you receive this event, grant the customer access to the product if they lost access while the subscription was paused. | Paused subscriptions are converted into active subscriptions when they resume. Resuming a subscription might generate an invoice and corresponding Payment Intent that must be paid before the subscription moves out of the `paused` status. |
| `customer.subscription.paused` | Sent when a subscription is fully paused. Invoicing won’t occur until the subscription resumes. When you receive this event, you can revoke the customer’s access to the product until they add a payment method and the subscription resumes. | Stop providing access to your product in response to this event. The subscription moves to the `paused` status and sends this event after a trial ends without a payment method, if the subscription’s `missing_payment_method` end behavior is set to `pause`. The subscription remains `paused` until explicitly resumed. |
| `customer.subscription.updated` | Sent when a subscription or its items change, including when a trial offer transitions to its post-trial price. | Update your access and billing state based on subscription item changes. |
| `customer.subscription.trial_will_end` | Sent according to the **Trial ending events** setting in the Dashboard, which defaults to 3 days before the trial ends. If the trial is shorter than the configured interval, it triggers immediately. | Use this event to send your own reminder email. Stripe-hosted reminder emails are sent 7 days before the trial ends. For more information, see [Manage compliance requirements for trials and promotions](https://docs.stripe.com/billing/subscriptions/trials/manage-trial-compliance.md). |

### Billing cycle anchor behavior

Adding a trial offer to an existing subscription doesn’t reset the subscription’s [billing cycle anchor](https://docs.stripe.com/api/subscriptions/object.md#subscription_object-trial_settings). For the trial duration, the trial offer item’s billing cycle is implicitly anchored at `trial_start`. For example, a two-month trial that starts on February 28 ends on April 28, not April 30. A two-month trial that starts on January 31 ends on March 31.

When the trial offer ends and transitions to the regular recurring price, you can configure whether the subscription’s billing cycle anchor resets using `trial_settings.end_behavior.billing_cycle_anchor`:

- `now` (default): Resets the subscription’s `billing_cycle_anchor` to the exact time the trial offer completes. This creates a new billing cycle for the regular price and generates a full-amount invoice with no proration.
- `unchanged`: Maintains the original anchor from when the subscription was first created. The period between the trial end and the next natural anchor date is billed as a prorated amount.

For example, if you offer a 7-day trial for 1 USD and want the first 20 USD monthly charge to cover a full month starting on day 8:

1. Jan 1: Subscription created with a 7-day trial offer.
2. Jan 8: Trial ends. The `billing_cycle_anchor` automatically resets to Jan 8.
3. Invoice: Stripe generates an invoice for the full 20 USD recurring price for the period of Jan 8–Feb 8. No proration is applied.

#### Accounts v2

```curl
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "customer_account={{CUSTOMERACCOUNT_ID}}" \
  -d "items[0][current_trial][trial_offer]={{TRIAL_OFFER_ID}}" \
  -d "trial_settings[end_behavior][billing_cycle_anchor]=unchanged"
```

#### Customer v1

```curl
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -H "Stripe-Version: 2026-09-30.endive" \
  -d "customer={{CUSTOMER_ID}}" \
  -d "items[0][current_trial][trial_offer]={{TRIAL_OFFER_ID}}" \
  -d "trial_settings[end_behavior][billing_cycle_anchor]=unchanged"
```

### Missing payment method behavior

When a trial offer ends, you can configure how Stripe acts if the customer doesn’t have a payment method attached using `trial_settings.end_behavior.missing_payment_method`. Stripe applies this behavior at the end of each trial offer. The options are:

- `create_invoice` (default): Creates an invoice. If the invoice can’t be paid, the subscription moves to `past_due`.
- `cancel`: Cancels the subscription.
- `pause`: Pauses the subscription until you resume it.

Trial offers have the same limitations as legacy free trials with no payment method, including the limitation that metered items aren’t supported. For configuration examples and additional details, see [Create free trials without collecting payment method](https://docs.stripe.com/billing/subscriptions/trials/free-trials.md#create-free-trials-without-payment).

> #### Prebilling overrides trial end behavior
> 
> Prebilling overrides `trial_settings.end_behavior.missing_payment_method` when it extends past the end of a trial, even if `missing_payment_method` is set to `pause` or `cancel`. The subscription continues its normal billing cycle after the trial ends. See [Prebilling](https://docs.stripe.com/billing/subscriptions/prebilling.md) for more information.

## See also

- [Products and prices](https://docs.stripe.com/products-prices/overview.md)
- [Prices](https://docs.stripe.com/api.md#prices)
- [Subscriptions](https://docs.stripe.com/api.md#subscriptions)
- [Managing subscription billing periods](https://docs.stripe.com/billing/subscriptions/billing-cycle.md)
