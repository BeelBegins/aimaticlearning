# Create a portal session

Creates a session of the customer portal.

## Prerequisites

Before you can run the following code snippet, you need to call these APIs with the provided parameters to set up the prerequisite API object(s).

1. createCustomer
POST /v1/customers {"name":"Jenny Rosen","email":"jennyrosen@example.com"}

## Request

```curl
curl https://api.stripe.com/v1/billing_portal/sessions \
  -u "<<YOUR_SECRET_KEY>>" \
  -d customer={{CUSTOMER_ID}} \
  --data-urlencode "return_url=https://example.com/account"
```

### Response

```json
{
  "id": "bps_1MrSjzLkdIwHu7ixex0IvU9b",
  "object": "billing_portal.session",
  "configuration": "bpc_1MAhNDLkdIwHu7ixckACO1Jq",
  "created": 1680210639,
  "customer": "cus_NciAYcXfLnqBoz",
  "flow": null,
  "livemode": false,
  "locale": null,
  "on_behalf_of": null,
  "return_url": "https://example.com/account",
  "url": "https://billing.stripe.com/p/session?secret=test_YWNjdF8xTTJKVGtMa2RJd0h1N2l4LF9OY2lBYjJXcHY4a2NPck96UjBEbFVYRnU5bjlwVUF50100BUtQs3bl"
}
```

## Parameters

- `configuration` (string, optional)
  The ID of an existing [configuration](https://docs.stripe.com/api/customer_portal/configurations.md) to use for this session, describing its functionality and features. If not specified, the session uses the default configuration.

- `customer` (string, optional)
  The ID of an existing customer.

- `customer_account` (string, optional)
  The ID of an existing account.

- [`flow_data`](https://docs.stripe.com/api/customer_portal/sessions/create.md?query=flow_data) (object, optional)
  Information about a specific flow for the customer to go through. See the [docs](https://docs.stripe.com/customer-management/portal-deep-links.md) to learn more about using customer portal deep links and flows.

- `locale` (enum, optional)
  The IETF language tag of the locale customer portal is displayed in. If blank or auto, the customer’s `preferred_locales` or browser’s locale is used.

- `on_behalf_of` (string, optional)
  The `on_behalf_of` account to use for this session. When specified, only subscriptions and invoices with this `on_behalf_of` account appear in the portal. For more information, see the [docs](https://docs.stripe.com/connect/separate-charges-and-transfers.md#settlement-merchant). Use the [Accounts API](https://docs.stripe.com/api/accounts/object.md#account_object-settings-branding) to modify the `on_behalf_of` account’s branding settings, which the portal displays.

- `return_url` (string, optional)
  The default URL to redirect customers to when they click on the portal’s link to return to your website.

## Returns

Returns a portal session object.
