# The Checkout Session object

### The Checkout Session object

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

## Attributes

- `id` (string)
  Unique identifier for the object.

- `object` (string, value is "checkout.session")
  String representing the object’s type. Objects of the same type share the same value.

- [`adaptive_pricing`](https://docs.stripe.com/api/checkout/sessions/object.md?query=adaptive_pricing) (object, nullable)
  Settings for price localization with [Adaptive Pricing](https://docs.stripe.com/payments/checkout/adaptive-pricing.md).

- [`after_expiration`](https://docs.stripe.com/api/checkout/sessions/object.md?query=after_expiration) (object, nullable)
  When set, provides configuration for actions to take if this Checkout Session expires.

- `allow_promotion_codes` (boolean, nullable)
  Enables user redeemable promotion codes.

- `allowed_payment_method_types` (array of strings, nullable)
  A list of the types of payment methods (e.g., `card`) this Checkout Session can accept.

- `amount_subtotal` (integer, nullable)
  Total of all items before discounts or taxes are applied.

- `amount_total` (integer, nullable)
  Total of all items after discounts and taxes are applied.

- [`automatic_tax`](https://docs.stripe.com/api/checkout/sessions/object.md?query=automatic_tax) (object)
  Details on the state of automatic tax for the session, including the status of the latest tax calculation.

- `billing_address_collection` (enum, nullable)
  Describes whether Checkout should collect the customer’s billing address. Defaults to `auto`.
Possible enum values:
  - `auto`
    Checkout will only collect the billing address when necessary. When using [automatic_tax](https://docs.stripe.com/api/checkout/sessions/object.md#checkout_session_object-automatic_tax-enabled), Checkout will collect the minimum number of fields required for tax calculation.

  - `required`
    Checkout will always collect the customer’s billing address.

- [`branding_settings`](https://docs.stripe.com/api/checkout/sessions/object.md?query=branding_settings) (object, nullable)
  Details on the state of branding settings for the session.

- `cancel_url` (string, nullable)
  If set, Checkout displays a back button and customers will be directed to this URL if they decide to cancel payment and return to your website.

- `client_reference_id` (string, nullable)
  A unique string to reference the Checkout Session. This can be a customer ID, a cart ID, or similar, and can be used to reconcile the Session with your internal systems.

- `client_secret` (string, nullable)
  The client secret of your Checkout Session. Applies to Checkout Sessions with `ui_mode: embedded_page` or `ui_mode: elements`. For `ui_mode: embedded_page`, the client secret is to be used when initializing Stripe.js embedded checkout. For `ui_mode: elements`, use the client secret with [initCheckout](https://docs.stripe.com/js/custom_checkout/init) on your front end.

- [`collected_information`](https://docs.stripe.com/api/checkout/sessions/object.md?query=collected_information) (object, nullable)
  Information about the customer collected within the Checkout Session.

- [`consent`](https://docs.stripe.com/api/checkout/sessions/object.md?query=consent) (object, nullable)
  Results of `consent_collection` for this session.

- [`consent_collection`](https://docs.stripe.com/api/checkout/sessions/object.md?query=consent_collection) (object, nullable)
  When set, provides configuration for the Checkout Session to gather active consent from customers.

- `created` (timestamp)
  Time at which the object was created. Measured in seconds since the Unix epoch.

- `currency` (enum, nullable)
  Three-letter [ISO currency code](https://www.iso.org/iso-4217-currency-codes.html), in lowercase. Must be a [supported currency](https://docs.stripe.com/currencies.md).

- [`currency_conversion`](https://docs.stripe.com/api/checkout/sessions/object.md?query=currency_conversion) (object, nullable)
  Currency conversion details for [Adaptive Pricing](https://docs.stripe.com/payments/checkout/adaptive-pricing.md) sessions created before 2025-03-31.

- [`custom_fields`](https://docs.stripe.com/api/checkout/sessions/object.md?query=custom_fields) (array of objects)
  Collect additional information from your customer using custom fields. Up to 3 fields are supported. You can’t set this parameter if `ui_mode` is `elements`.

- [`custom_text`](https://docs.stripe.com/api/checkout/sessions/object.md?query=custom_text) (object)
  Display additional text for your customers using custom text. You can’t set this parameter if `ui_mode` is `elements`.

- `customer` (string, nullable, expandable (can be expanded into an object with the `expand` request parameter))
  The ID of the customer for this Session. For Checkout Sessions in `subscription` mode or Checkout Sessions with `customer_creation` set as `always` in `payment` mode, Checkout will create a new customer object based on information provided during the payment flow unless an existing customer was provided when the Session was created.

- `customer_account` (string, nullable)
  The ID of the account for this Session.

- `customer_creation` (enum, nullable)
  Configure whether a Checkout Session creates a Customer when the Checkout Session completes.
Possible enum values:
  - `always`
    The Checkout Session will always create a [Customer](https://docs.stripe.com/api/customers.md) when a Session confirmation is attempted.

  - `if_required`
    The Checkout Session will only create a [Customer](https://docs.stripe.com/api/customers.md) if it is required for Session confirmation. Currently, only `subscription` mode Sessions and `payment` mode Sessions with [post-purchase invoices enabled](https://docs.stripe.com/receipts.md?payment-ui=checkout#paid-invoices) require a Customer.

- [`customer_details`](https://docs.stripe.com/api/checkout/sessions/object.md?query=customer_details) (object, nullable)
  The customer details including the customer’s tax exempt status and the customer’s tax IDs. Customer’s address details are not present on Sessions in `setup` mode.

- `customer_email` (string, nullable)
  If provided, this value will be used when the Customer object is created. If not provided, customers will be asked to enter their email address. Use this parameter to prefill customer data if you already have an email on file. To access information about the customer once the payment flow is complete, use the `customer` attribute.

- [`discounts`](https://docs.stripe.com/api/checkout/sessions/object.md?query=discounts) (array of objects, nullable)
  List of coupons and promotion codes attached to the Checkout Session.

- `excluded_payment_method_types` (array of strings, nullable)
  A list of the types of payment methods (e.g., `card`) that should be excluded from this Checkout Session. This should only be used when payment methods for this Checkout Session are managed through the [Stripe Dashboard](https://dashboard.stripe.com/settings/payment_methods).

- `expires_at` (timestamp)
  The timestamp at which the Checkout Session will expire.

- `integration_identifier` (string, nullable)
  The integration identifier for this Checkout Session. Multiple Checkout Sessions can have the same integration identifier.

- `invoice` (string, nullable, expandable (can be expanded into an object with the `expand` request parameter))
  ID of the invoice created by the Checkout Session, if it exists.

- [`invoice_creation`](https://docs.stripe.com/api/checkout/sessions/object.md?query=invoice_creation) (object, nullable)
  Details on the state of invoice creation for the Checkout Session.

- [`line_items`](https://docs.stripe.com/api/checkout/sessions/object.md?query=line_items) (object, nullable, includable (not returned by default; request it with the `expand` request parameter))
  The line items purchased by the customer.

- `livemode` (boolean)
  If the object exists in live mode, the value is `true`. If the object exists in test mode, the value is `false`.

- `locale` (enum, nullable)
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

- [`managed_payments`](https://docs.stripe.com/api/checkout/sessions/object.md?query=managed_payments) (object, nullable)
  Settings for Managed Payments for this Checkout Session and resulting [PaymentIntents](https://docs.stripe.com/api/payment_intents/object.md), [Invoices](https://docs.stripe.com/api/invoices/object.md), and [Subscriptions](https://docs.stripe.com/api/subscriptions/object.md).

- `metadata` (map, nullable)
  Set of [key-value pairs](https://docs.stripe.com/api/metadata.md) that you can attach to an object. This can be useful for storing additional information about the object in a structured format.

- `mode` (enum)
  The mode of the Checkout Session.
Possible enum values:
  - `payment`
    Accept one-time payments for cards, iDEAL, and more.

  - `setup`
    Save payment details to charge your customers later.

  - `subscription`
    Use Stripe Billing to set up fixed-price subscriptions.

- [`name_collection`](https://docs.stripe.com/api/checkout/sessions/object.md?query=name_collection) (object, nullable)
  Details on the state of name collection for the session.

- `optional_items` (array of objects, nullable, includable (not returned by default; request it with the `expand` request parameter))
  The optional items presented to the customer at checkout.

- `origin_context` (enum, nullable)
  Where the user is coming from. This informs the optimizations that are applied to the session.
Possible enum values:
  - `mobile_app`
    The Checkout Session originates from a mobile app that redirects customers to a Stripe-hosted payment page for an in-app purchase.

  - `web`
    The Checkout Session originates from a web page.

- `payment_intent` (string, nullable, expandable (can be expanded into an object with the `expand` request parameter))
  The ID of the PaymentIntent for Checkout Sessions in `payment` mode. You can’t confirm or cancel the PaymentIntent for a Checkout Session. To cancel, [expire the Checkout Session](https://docs.stripe.com/api/checkout/sessions/expire.md) instead.

- `payment_link` (string, nullable, expandable (can be expanded into an object with the `expand` request parameter))
  The ID of the Payment Link that created this Session.

- `payment_method_collection` (enum, nullable)
  Configure whether a Checkout Session should collect a payment method for sessions with mode `payment`. Defaults to `always`.
Possible enum values:
  - `always`
    The Checkout Session will always collect a PaymentMethod.

  - `if_required`
    The Checkout Session will only collect a PaymentMethod if there is an amount due.

- [`payment_method_configuration_details`](https://docs.stripe.com/api/checkout/sessions/object.md?query=payment_method_configuration_details) (object, nullable)
  Information about the payment method configuration used for this Checkout session if using dynamic payment methods.

- [`payment_method_options`](https://docs.stripe.com/api/checkout/sessions/object.md?query=payment_method_options) (object, nullable)
  Payment-method-specific configuration for the PaymentIntent or SetupIntent of this CheckoutSession.

- `payment_method_types` (array of strings)
  A list of the types of payment methods (e.g. card) this Checkout Session is allowed to accept.

- `payment_status` (enum)
  The payment status of the Checkout Session, one of `paid`, `unpaid`, or `no_payment_required`. You can use this value to decide when to fulfill your customer’s order.
Possible enum values:
  - `no_payment_required`
    The Checkout Session is in `setup` mode and doesn’t require a payment at this time, or the Session uses a billing cycle anchor with no proration and payment will be collected at the anchor date.

  - `paid`
    The payment funds are available in your account. For subscriptions with a free trial, this indicates that the $0 trial invoice has been successfully processed.

  - `unpaid`
    The payment funds are not yet available in your account.

- [`permissions`](https://docs.stripe.com/api/checkout/sessions/object.md?query=permissions) (object, nullable)
  This property is used to set up permissions for various actions (e.g., update) on the CheckoutSession object.

  For specific permissions, please refer to their dedicated subsections, such as `permissions.update_shipping_details`.

- [`phone_number_collection`](https://docs.stripe.com/api/checkout/sessions/object.md?query=phone_number_collection) (object, nullable)
  Details on the state of phone number collection for the session.

- [`presentment_details`](https://docs.stripe.com/api/checkout/sessions/object.md?query=presentment_details) (object, nullable)
  A hash containing information about the currency presentation to the customer, including the displayed currency and amount used for conversion from the integration currency.

- `recovered_from` (string, nullable)
  The ID of the original expired Checkout Session that triggered the recovery flow.

- `redirect_on_completion` (enum, nullable)
  This parameter applies to `ui_mode: embedded_page`. Learn more about the [redirect behavior](https://docs.stripe.com/payments/checkout/custom-success-page.md?payment-ui=embedded-form) of embedded sessions. Defaults to `always`.
Possible enum values:
  - `always`
    The Session will always redirect to the `return_url` after successful confirmation.

  - `if_required`
    The Session will only redirect to the `return_url` after a redirect-based payment method is used.

  - `never`
    The Session will never redirect to the `return_url`, and redirect-based payment methods will be disabled.

- `return_url` (string, nullable)
  Applies to Checkout Sessions with `ui_mode: embedded_page` or `ui_mode: elements`. The URL to redirect your customer back to after they authenticate or cancel their payment on the payment method’s app or site.

- [`saved_payment_method_options`](https://docs.stripe.com/api/checkout/sessions/object.md?query=saved_payment_method_options) (object, nullable)
  Controls saved payment method settings for the session. Only available in `payment` and `subscription` mode.

- `setup_intent` (string, nullable, expandable (can be expanded into an object with the `expand` request parameter))
  The ID of the SetupIntent for Checkout Sessions in `setup` mode. You can’t confirm or cancel the SetupIntent for a Checkout Session. To cancel, [expire the Checkout Session](https://docs.stripe.com/api/checkout/sessions/expire.md) instead.

- [`shipping_address_collection`](https://docs.stripe.com/api/checkout/sessions/object.md?query=shipping_address_collection) (object, nullable)
  When set, provides configuration for Checkout to collect a shipping address from a customer.

- [`shipping_cost`](https://docs.stripe.com/api/checkout/sessions/object.md?query=shipping_cost) (object, nullable)
  The details of the customer cost of shipping, including the customer chosen ShippingRate.

- [`shipping_options`](https://docs.stripe.com/api/checkout/sessions/object.md?query=shipping_options) (array of objects)
  The shipping rate options applied to this Session.

- `status` (enum, nullable)
  The status of the Checkout Session, one of `open`, `complete`, or `expired`.
Possible enum values:
  - `complete`
    The checkout session is complete. Payment processing may still be in progress

  - `expired`
    The checkout session has expired. No further processing will occur

  - `open`
    The checkout session is still in progress. Payment processing has not started

- `submit_type` (enum, nullable)
  Describes the type of transaction being performed by Checkout in order to customize relevant text on the page, such as the submit button. `submit_type` can only be specified on Checkout Sessions in `payment` mode. If blank or `auto`, `pay` is used.
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

- `subscription` (string, nullable, expandable (can be expanded into an object with the `expand` request parameter))
  The ID of the [Subscription](https://docs.stripe.com/api/subscriptions.md) for Checkout Sessions in `subscription` mode.

- `success_url` (string, nullable)
  The URL the customer will be directed to after the payment or subscription creation is successful.

- [`tax_id_collection`](https://docs.stripe.com/api/checkout/sessions/object.md?query=tax_id_collection) (object, nullable)
  Details on the state of tax ID collection for the session.

- [`total_details`](https://docs.stripe.com/api/checkout/sessions/object.md?query=total_details) (object, nullable)
  Tax and discount details for the computed total amount.

- `ui_mode` (enum, nullable)
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

- `url` (string, nullable)
  The URL to the Checkout Session. Applies to Checkout Sessions with `ui_mode: hosted_page`. Redirect customers to this URL to take them to Checkout. If you’re using [Custom Domains](https://docs.stripe.com/payments/checkout/custom-domains.md), the URL will use your subdomain. Otherwise, it’ll use `checkout.stripe.com.` This value is only present when the session is active.

- [`wallet_options`](https://docs.stripe.com/api/checkout/sessions/object.md?query=wallet_options) (object, nullable)
  Wallet-specific configuration for this Checkout Session.
