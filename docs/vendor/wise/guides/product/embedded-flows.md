# Embedded Flows

Embedded Flows are Wise-hosted flows for partners integrating Wise Platform into their own products. They reduce the engineering uplift of implementing Wise-specific frontend patterns, such as the dynamic flows used by recipient creation, so you can integrate, test, and prove value earlier.

With a standard API integration, your team usually builds the full user-facing experience and connects each screen to specific Wise Platform endpoints. With Embedded Flows, your backend requests the flow you need along with the return URL, and receives a URL in the response you can redirect your customer to or embed directly in your application via iframe or mobile WebView.

## Implementation guides

Choose an implementation guide for step-by-step instructions:

Web
Embed the flow in an iframe and listen for optional window messages.

iOS
Load the flow in a `WKWebView` and bridge flow messages to native code.

Android
Load the flow in a `WebView` and bridge flow messages to your app.

Web SDK coming soon
A web SDK is planned to make iframe setup, resizing, events, and theme updates easier. Until then, handle iframe or WebView integration directly in your product.

## Styling

You can apply limited styling to the flows so they reflect your application's brand colours and logo. Currently, you must contact your Wise solutions engineer to have these updated for your brand.

## Example flow: recipient creation 

All Embedded Flows use the following pattern: your backend requests a flow URL, your frontend opens it, and your product handles the result.

This example uses [hosted recipient creation](/api-reference/link-requests/recipientembeddedlinkrequestcreate) (`RECIPIENT`) to show how the pieces fit together.

Workflow summary:

1. Create a short-lived flow URL from your backend.
2. Open the URL in an iframe, mobile WebView, pop-up, or full-page redirect.
3. Handle completion, cancellation, or errors in your frontend or redirect handler.
4. Use webhooks to reconcile the resource created or changed by the flow.


### Step 1: Request a flow URL

Call the [Recipient creation link request endpoint](/api-reference/link-requests/recipientembeddedlinkrequestcreate) from your backend.

In this example, the `redirectUrl` tells Wise where to return the user once the flow is complete and `targetCurrency` starts the recipient flow for EUR. The `redirectUrl` must match the redirect URL allowlist configured for your integration.

**Create recipient embedded link request**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/14966143/embedded-flows/link-requests/recipients \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "redirectUrl": "https://partner.example/recipient-return",
    "targetCurrency": "EUR"
  }'
```

Wise returns a unique URL for this flow. Open this URL for the user before it expires.

Response
```json
{
  "url": "https://wise-sandbox.com/embedded-flows?embeddedLinkRequestId=ea5eb6ca-3af7-4e88-a2e2-6a68dd92f198#token=0d0bdc88-bcf4-43dd-85be-7ca65441db20",
  "expiresAt": "2026-06-15T13:23:20.265Z"
}
```

### Step 2: Open the flow

Render the returned `url` in your chosen surface. See [Embed on web](/guides/product/embedded-flows/web), [Embed on iOS](/guides/product/embedded-flows/ios), or [Embed on Android](/guides/product/embedded-flows/android) for platform-specific steps.

Your frontend should handle these flow messages:

| Message | When it is sent | Typical use |
|  --- | --- | --- |
| `ready` | The flow is ready to be shown. | Hide a loading state or make the iframe visible. |
| `resize` | The flow content height changes. | Update the iframe height. |
| `done` | The user completes the flow. | Close the iframe or move the user to the next step. |
| `error` | The flow cannot continue, or the user cancels. | Show a retry option or return the user to your previous step. |


If the user cancels inside an embedded iframe or WebView, the flow sends:

Cancellation message
```json
{
  "type": "error",
  "code": "cancelled"
}
```

If the flow is opened as a standalone page and the user cancels, Wise redirects to your `redirectUrl` with `status=cancelled`. A successful standalone completion redirects with `status=success`, and other errors redirect with `status=error`.

Standalone cancellation redirect
```text
https://partner.example/recipient-return?status=cancelled
```

### Step 3: Reconcile with webhooks

For recipient creation, [subscribe to the webhook](/api-reference/webhook) and listen for `recipients#state-change`. The event is available in schema version `4.0.0`.

See the [Recipient state change reference](/api-reference/webhook-event/eventrecipientsstatechange) for the full schema.

Recipient state-change event
```json
{
  "data": {
    "resource": {
      "id": "700525176",
      "occurred_at": "2026-06-15T13:18:20.265Z",
      "data": {
        "recipientId": 700525176,
        "profileId": 14966143,
        "currency": "EUR",
        "state": "CREATE",
        "clientId": "hosted-kyc-test-client"
      }
    }
  },
  "subscription_id": "ced03af9-be76-46ac-ada8-7fe935792290",
  "event_type": "recipients#state-change",
  "schema_version": "4.0.0",
  "sent_at": "2026-06-15T13:18:20.265Z"
}
```

Use `data.resource.data.recipientId` as the created or changed recipient ID. Webhooks typically include a trimmed subset of data, so use the recipient ID with requests like [Get account by ID](/api-reference/recipient/recipientget) when you need full recipient details. Use `data.resource.occurred_at` when reconciling event order, and return any `2xx` response to acknowledge delivery.

The Embedded Flows section in the API reference includes the request and response details for `POST /profiles/{profileId}/embedded-flows/link-requests/recipients`. The [Recipient state change reference](/api-reference/webhook-event/eventrecipientsstatechange) includes the webhook event emitted after recipient creation changes state.