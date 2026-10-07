# Create a Checkout Session

Creates a Checkout Session object.

## Prerequisites

Before you can run the following code snippet, you need to call these APIs with the provided parameters to set up the prerequisite API object(s).

1. createPrice
POST /v1/prices {"currency":"usd","unit_amount":1000,"recurring":{"interval":"month"},"product_data":{"name":"Gold Plan"}}

## Request

```curl
curl https://api.stripe.com/v1/checkout/sessions \
  -u "<<YOUR_SECRET_KEY>>" \
  --data-urlencode "success_url=https://example.com/success" \
  -d "line_items[0][price]={{PRICE_ID}}" \
  -d "line_items[0][quantity]=2" \
  -d mode=payment
```

### Response

```json
{
  "id": "cs_test_a11YYufWQzNY63zpQ6QSNRQhkUpVph4WRmzW0zWJO2znZKdVujZ0N0S22u",
  "object": "checkout.session",
  "after_expiration": null,
  "allow_promotion_codes": null,
  "amount_subtotal": 2198,
  "amount_total": 2198,
  "automatic_tax": {
    "enabled": false,
    "liability": null,
    "status": null
  },
  "billing_address_collection": null,
  "cancel_url": null,
  "client_reference_id": null,
  "consent": null,
  "consent_collection": null,
  "created": 1679600215,
  "currency": "usd",
  "custom_fields": [],
  "custom_text": {
    "shipping_address": null,
    "submit": null
  },
  "customer": null,
  "customer_creation": "if_required",
  "customer_details": null,
  "customer_email": null,
  "expires_at": 1679686615,
  "invoice": null,
  "invoice_creation": {
    "enabled": false,
    "invoice_data": {
      "account_tax_ids": null,
      "custom_fields": null,
      "description": null,
      "footer": null,
      "issuer": null,
      "metadata": {},
      "rendering_options": null
    }
  },
  "livemode": false,
  "locale": null,
  "metadata": {},
  "mode": "payment",
  "payment_intent": null,
  "payment_link": null,
  "payment_method_collection": "always",
  "payment_method_options": {},
  "payment_method_types": [
    "card"
  ],
  "payment_status": "unpaid",
  "phone_number_collection": {
    "enabled": false
  },
  "recovered_from": null,
  "setup_intent": null,
  "shipping_address_collection": null,
  "shipping_cost": null,
  "shipping_details": null,
  "shipping_options": [],
  "status": "open",
  "submit_type": null,
  "subscription": null,
  "success_url": "https://example.com/success",
  "total_details": {
    "amount_discount": 0,
    "amount_shipping": 0,
    "amount_tax": 0
  },
  "return_url": null,
  "ui_mode": "hosted_page",
  "url": "https://checkout.stripe.com/c/pay/cs_test_a11YYufWQzNY63zpQ6QSNRQhkUpVph4WRmzW0zWJO2znZKdVujZ0N0S22u#fidkdWxOYHwnPyd1blpxYHZxWjA0SDdPUW5JbmFMck1wMmx9N2BLZjFEfGRUNWhqTmJ%2FM2F8bUA2SDRySkFdUV81T1BSV0YxcWJcTUJcYW5rSzN3dzBLPUE0TzRKTTxzNFBjPWZEX1NKSkxpNTVjRjN8VHE0YicpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"
}
```

## Parameters

- [`adaptive_pricing`](https://docs.stripe.com/api/checkout/sessions/create.md?query=adaptive_pricing) (object, optional)
  Settings for price localization with [Adaptive Pricing](https://docs.stripe.com/payments/checkout/adaptive-pricing.md).

- [`after_expiration`](https://docs.stripe.com/api/checkout/sessions/create.md?query=after_expiration) (object, optional)
  Configure actions after a Checkout Session has expired. You can’t set this parameter if `ui_mode` is `elements`.

- `allow_promotion_codes` (boolean, optional)
  Enables user redeemable promotion codes.

- `allowed_payment_method_types` (array of enums, optional)
  A list of the types of payment methods (e.g., `card`) this Checkout Session can accept.

  Unlike `payment_method_types`, this acts as a filter on the dynamically computed set of eligible payment methods rather than an explicit static list. Only payment methods that are both dynamically eligible and present in this list will be offered to the customer.

- [`automatic_tax`](https://docs.stripe.com/api/checkout/sessions/create.md?query=automatic_tax) (object, optional)
  Settings for automatic tax lookup for this session and resulting payments, invoices, and subscriptions.

- `billing_address_collection` (enum, optional)
  Specify whether Checkout should collect the customer’s billing address. Defaults to `auto`.
Possible enum values:
  - `auto`
    Checkout will only collect the billing address when necessary. When using [automatic_tax](https://docs.stripe.com/api/checkout/sessions/object.md#checkout_session_object-automatic_tax-enabled), Checkout will collect the minimum number of fields required for tax calculation.

  - `required`
    Checkout will always collect the customer’s billing address.

- [`branding_settings`](https://docs.stripe.com/api/checkout/sessions/create.md?query=branding_settings) (object, optional)
  The branding settings for the Checkout Session. This parameter is not allowed if ui_mode is `elements`.

- `cancel_url` (string, optional)
  If set, Checkout displays a back button and customers will be directed to this URL if they decide to cancel payment and return to your website. This parameter is not allowed if ui_mode is `embedded_page` or `elements`.

- `client_reference_id` (string, optional)
  A unique string to reference the Checkout Session. This can be a customer ID, a cart ID, or similar, and can be used to reconcile the session with your internal systems.

  The maximum length is 200 characters.

- [`consent_collection`](https://docs.stripe.com/api/checkout/sessions/create.md?query=consent_collection) (object, optional)
  Configure fields for the Checkout Session to gather active consent from customers.

- `currency` (enum, required conditionally)
  Three-letter [ISO currency code](https://www.iso.org/iso-4217-currency-codes.html), in lowercase. Must be a [supported currency](https://docs.stripe.com/currencies.md). Required in `setup` mode when `payment_method_types` is not set.

- [`custom_fields`](https://docs.stripe.com/api/checkout/sessions/create.md?query=custom_fields) (array of objects, optional)
  Collect additional information from your customer using custom fields. Up to 3 fields are supported. You can’t set this parameter if `ui_mode` is `elements`.

- [`custom_text`](https://docs.stripe.com/api/checkout/sessions/create.md?query=custom_text) (object, optional)
  Display additional text for your customers using custom text. You can’t set this parameter if `ui_mode` is `elements`.

- `customer` (string, optional)
  ID of an existing Customer, if one exists. In `payment` mode, the customer’s most recently saved card payment method will be used to prefill the email, name, card details, and billing address on the Checkout page. In `subscription` mode, the customer’s [default payment method](https://docs.stripe.com/api/customers/update.md#update_customer-invoice_settings-default_payment_method) will be used if it’s a card, otherwise the most recently saved card will be used. A valid billing address, billing name and billing email are required on the payment method for Checkout to prefill the customer’s card details.

  If the Customer already has a valid [email](https://docs.stripe.com/api/customers/object.md#customer_object-email) set, the email will be prefilled and not editable in Checkout. If the Customer does not have a valid `email`, Checkout will set the email entered during the session on the Customer.

  If blank for Checkout Sessions in `subscription` mode or with `customer_creation` set as `always` in `payment` mode, Checkout will create a new Customer object based on information provided during the payment flow.

  You can set [`payment_intent_data.setup_future_usage`](https://docs.stripe.com/api/checkout/sessions/create.md#create_checkout_session-payment_intent_data-setup_future_usage) to have Checkout automatically attach the payment method to the Customer you pass in for future reuse.

- `customer_account` (string, optional)
  ID of an existing Account, if one exists. Has the same behavior as `customer`.

- `customer_creation` (enum, optional)
  Configure whether a Checkout Session creates a [Customer](https://docs.stripe.com/api/customers.md) during Session confirmation.

  When a Customer is not created, you can still retrieve email, address, and other customer data entered in Checkout with [customer_details](https://docs.stripe.com/api/checkout/sessions/object.md#checkout_session_object-customer_details).

  Sessions that don’t create Customers instead are grouped by [guest customers](https://docs.stripe.com/payments/checkout/guest-customers.md) in the Dashboard. Promotion codes limited to first time customers will return invalid for these Sessions.

  Can only be set in `payment` and `setup` mode.
Possible enum values:
  - `always`
    The Checkout Session will always create a [Customer](https://docs.stripe.com/api/customers.md) when a Session confirmation is attempted.

  - `if_required`
    The Checkout Session will only create a [Customer](https://docs.stripe.com/api/customers.md) if it is required for Session confirmation. Currently, only `subscription` mode Sessions and `payment` mode Sessions with [post-purchase invoices enabled](https://docs.stripe.com/receipts.md?payment-ui=checkout#paid-invoices) require a Customer.

- `customer_email` (string, optional)
  If provided, this value will be used when the Customer object is created. If not provided, customers will be asked to enter their email address. Use this parameter to prefill customer data if you already have an email on file. To access information about the customer once a session is complete, use the `customer` field.

  The maximum length is 800 characters.

- [`customer_update`](https://docs.stripe.com/api/checkout/sessions/create.md?query=customer_update) (object, optional)
  Controls what fields on Customer can be updated by the Checkout Session. Can only be provided when `customer` is provided.

- [`discounts`](https://docs.stripe.com/api/checkout/sessions/create.md?query=discounts) (array of objects, optional)
  The coupon or promotion code to apply to this Session. Currently, only up to one may be specified.

- `excluded_payment_method_types` (array of enums, optional)
  A list of the types of payment methods (e.g., `card`) that should be excluded from this Checkout Session. This should only be used when payment methods for this Checkout Session are managed through the [Stripe Dashboard](https://dashboard.stripe.com/settings/payment_methods).

- `expires_at` (timestamp, optional)
  The Epoch time in seconds at which the Checkout Session will expire. It can be anywhere from 30 minutes to 24 hours after Checkout Session creation. By default, this value is 24 hours from creation.

- `integration_identifier` (string, optional)
  The integration identifier for this Checkout Session. Multiple Checkout Sessions can have the same integration identifier.

  The maximum length is 200 characters.

- [`invoice_creation`](https://docs.stripe.com/api/checkout/sessions/create.md?query=invoice_creation) (object, optional)
  Generate a post-purchase Invoice for one-time payments.

- [`line_items`](https://docs.stripe.com/api/checkout/sessions/create.md?query=line_items) (array of objects, required conditionally)
  A list of items the customer is purchasing. Use this parameter to pass one-time or recurring [Prices](https://docs.stripe.com/api/prices.md). The parameter is required for `payment` and `subscription` mode.

  For `payment` mode, there is a maximum of 100 line items, however it is recommended to consolidate line items if there are more than a few dozen.

  For `subscription` mode, there is a maximum of 20 line items with recurring Prices and 20 line items with one-time Prices. Line items with one-time Prices will be on the initial invoice only.

- `locale` (enum, optional)
  The IETF language tag of the locale Checkout is displayed in. If blank or `auto`, the browser’s locale is used.
Possible enum values:
  - `auto`
  - `bg`
  - `cs`
  - `da`
  - `de`
  - `el`
  - `en`
  - `en-GB`
  - `es`
  - `es-419`
  - `et`
  - `fi`
  - `fil`
  - `fr`
  - `fr-CA`
  - `hr`
  - `hu`
  - `id`
  - `it`
  - `ja`
  - `ko`
  - `lt`
  - `lv`
  - `ms`
  - `mt`
  - `nb`
  - `nl`
  - `pl`
  - `pt`
  - `pt-BR`
  - `ro`
  - `ru`
  - `sk`
  - `sl`
  - `sv`
  - `th`
  - `tr`
  - `vi`
  - `zh`
  - `zh-HK`
  - `zh-TW`

- [`managed_payments`](https://docs.stripe.com/api/checkout/sessions/create.md?query=managed_payments) (object, optional)
  Settings for Managed Payments for this Checkout Session and resulting [PaymentIntents](https://docs.stripe.com/api/payment_intents/object.md), [Invoices](https://docs.stripe.com/api/invoices/object.md), and [Subscriptions](https://docs.stripe.com/api/subscriptions/object.md).

- `metadata` (map, optional)
  Set of [key-value pairs](https://docs.stripe.com/api/metadata.md) that you can attach to an object. This can be useful for storing additional information about the object in a structured format. Individual keys can be unset by posting an empty value to them. All keys can be unset by posting an empty value to `metadata`.

- `mode` (enum, required)
  The mode of the Checkout Session. Pass `subscription` if the Checkout Session includes at least one recurring item.
Possible enum values:
  - `payment`
    Accept one-time payments for cards, iDEAL, and more.

  - `setup`
    Save payment details to charge your customers later.

  - `subscription`
    Use Stripe Billing to set up fixed-price subscriptions.

- [`name_collection`](https://docs.stripe.com/api/checkout/sessions/create.md?query=name_collection) (object, optional)
  Controls name collection settings for the session.

  You can configure Checkout to collect your customers’ business names, individual names, or both. Each name field can be either required or optional.

  If a [Customer](https://docs.stripe.com/api/customers.md) is created or provided, the names can be saved to the Customer object as well.

- [`optional_items`](https://docs.stripe.com/api/checkout/sessions/create.md?query=optional_items) (array of objects, optional)
  A list of optional items the customer can add to their order at checkout. Use this parameter to pass one-time or recurring [Prices](https://docs.stripe.com/api/prices.md).

  There is a maximum of 10 optional items allowed on a Checkout Session, and the existing limits on the number of line items allowed on a Checkout Session apply to the combined number of line items and optional items.

  For `payment` mode, there is a maximum of 100 combined line items and optional items, however it is recommended to consolidate items if there are more than a few dozen.

  For `subscription` mode, there is a maximum of 20 line items and optional items with recurring Prices and 20 line items and optional items with one-time Prices.

  You can’t set this parameter if `ui_mode` is `elements` or `form`.

- `origin_context` (enum, optional)
  Where the user is coming from. This informs the optimizations that are applied to the session. You can’t set this parameter if `ui_mode` is `elements`.
Possible enum values:
  - `mobile_app`
    The Checkout Session originates from a mobile app that redirects customers to a Stripe-hosted payment page for an in-app purchase.

  - `web`
    The Checkout Session originates from a web page.

- [`payment_intent_data`](https://docs.stripe.com/api/checkout/sessions/create.md?query=payment_intent_data) (object, optional)
  A subset of parameters to be passed to PaymentIntent creation for Checkout Sessions in `payment` mode.

- `payment_method_collection` (enum, optional)
  Specify whether Checkout should collect a payment method. When set to `if_required`, Checkout will not collect a payment method when the total due for the session is 0. This may occur if the Checkout Session includes a free trial or a discount.

  Can only be set in `subscription` mode. Defaults to `always`.

  If you’d like information on how to collect a payment method outside of Checkout, read the guide on configuring [subscriptions with a free trial](https://docs.stripe.com/payments/checkout/free-trials.md).
Possible enum values:
  - `always`
    The Checkout Session will always collect a PaymentMethod.

  - `if_required`
    The Checkout Session will only collect a PaymentMethod if there is an amount due.

- `payment_method_configuration` (string, optional)
  The ID of the payment method configuration to use with this Checkout session.

  The maximum length is 100 characters.

- [`payment_method_data`](https://docs.stripe.com/api/checkout/sessions/create.md?query=payment_method_data) (object, optional)
  This parameter allows you to set some attributes on the payment method created during a Checkout session.

- [`payment_method_options`](https://docs.stripe.com/api/checkout/sessions/create.md?query=payment_method_options) (object, optional)
  Payment-method-specific configuration.

- [`permissions`](https://docs.stripe.com/api/checkout/sessions/create.md?query=permissions) (object, optional)
  This property is used to set up permissions for various actions (for example, update) on the CheckoutSession object. Can only be set when creating `embedded_page` or `elements` sessions.

  For specific permissions, please refer to their dedicated subsections, such as `permissions.update_shipping_details`.

- [`phone_number_collection`](https://docs.stripe.com/api/checkout/sessions/create.md?query=phone_number_collection) (object, optional)
  Controls phone number collection settings for the session.

  We recommend that you review your privacy policy and check with your legal contacts before using this feature. Learn more about [collecting phone numbers with Checkout](https://docs.stripe.com/payments/checkout/phone-numbers.md).

- `redirect_on_completion` (enum, optional)
  This parameter applies to `ui_mode: embedded_page`. Learn more about the [redirect behavior](https://docs.stripe.com/payments/checkout/custom-success-page.md?payment-ui=embedded-form) of embedded sessions. Defaults to `always`.
Possible enum values:
  - `always`
    The Session will always redirect to the `return_url` after successful confirmation.

  - `if_required`
    The Session will only redirect to the `return_url` after a redirect-based payment method is used.

  - `never`
    The Session will never redirect to the `return_url`, and redirect-based payment methods will be disabled.

- `return_url` (string, required conditionally)
  The URL to redirect your customer back to after they authenticate or cancel their payment on the payment method’s app or site. This parameter is required if `ui_mode` is `embedded_page` or `elements` and redirect-based payment methods are enabled on the session.

- [`saved_payment_method_options`](https://docs.stripe.com/api/checkout/sessions/create.md?query=saved_payment_method_options) (object, optional)
  Controls saved payment method settings for the session. Only available in `payment` and `subscription` mode.

- [`setup_intent_data`](https://docs.stripe.com/api/checkout/sessions/create.md?query=setup_intent_data) (object, optional)
  A subset of parameters to be passed to SetupIntent creation for Checkout Sessions in `setup` mode.

- [`shipping_address_collection`](https://docs.stripe.com/api/checkout/sessions/create.md?query=shipping_address_collection) (object, optional)
  When set, provides configuration for Checkout to collect a shipping address from a customer.

- [`shipping_options`](https://docs.stripe.com/api/checkout/sessions/create.md?query=shipping_options) (array of objects, optional)
  The shipping rate options to apply to this Session. Up to a maximum of 5.

- `submit_type` (enum, optional)
  Describes the type of transaction being performed by Checkout in order to customize relevant text on the page, such as the submit button. `submit_type` can only be specified on Checkout Sessions in `payment` or `subscription` mode. If blank or `auto`, `pay` is used. You can’t set this parameter if `ui_mode` is `elements`.
Possible enum values:
  - `auto`
    `pay` will used for `payment` mode sessions and `subscribe` will be used for `subscription` mode sessions

  - `book`
    Recommended when offering bookings. Submit button includes a ‘Book’ label

  - `donate`
    Recommended when accepting donations. Submit button includes a ‘Donate’ label

  - `pay`
    Submit button includes a ‘Buy’ label

  - `subscribe`
    Submit button includes a ‘Subscribe’ label

- [`subscription_data`](https://docs.stripe.com/api/checkout/sessions/create.md?query=subscription_data) (object, optional)
  A subset of parameters to be passed to subscription creation for Checkout Sessions in `subscription` mode.

- `success_url` (string, required conditionally)
  The URL to which Stripe should send customers when payment or setup is complete. This parameter is not allowed if ui_mode is `embedded_page` or `elements`. If you’d like to use information from the successful Checkout Session on your page, read the guide on [customizing your success page](https://docs.stripe.com/payments/checkout/custom-success-page.md).

- [`tax_id_collection`](https://docs.stripe.com/api/checkout/sessions/create.md?query=tax_id_collection) (object, optional)
  Controls tax ID collection during checkout.

- `ui_mode` (enum, optional)
  The UI mode of the Session. Defaults to `hosted_page`.
Possible enum values:
  - `elements`
    The Checkout Session is displayed using [Checkout elements](https://docs.stripe.com/checkout/custom/quickstart.md) on your website.

  - `embedded_page`
    The Checkout Session is displayed as an embedded form on your website.

  - `form`
    The Checkout Session is displayed using the Checkout form on your website.

  - `hosted_page`
    The Checkout Session is displayed on a hosted page that customers get redirected to.

- [`wallet_options`](https://docs.stripe.com/api/checkout/sessions/create.md?query=wallet_options) (object, optional)
  Wallet-specific configuration.

## Returns

Returns a Checkout Session object.
