# mTLS for webhook notifications

Receiving events in the mTLS webhook endpoint.

For additional security, you can add mTLS certification to webhook notifications you receive from Wise Platform.

To do this, you need to import a Certificate Authority chain, provided by Wise, to your webhook server.

The setup process depends on your server infrastructure. Typically, the CA chain can be imported to the API gateway.

## Core concepts and overview of steps 

To secure your webhook notifications with mTLS, you must first import a **Certificate Authority (CA) chain** from Wise into your webhook server. Once the setup is complete, you can use the API to manage your mTLS-enabled webhook subscriptions.

To add mTLS certification to webhooks:

1. **Create Subscription:** Send a **POST** request to the `subscriptions` endpoint with `mtls_enabled` set to `true`.
  * `name` (string): A name for the subscription.
  * `trigger_on` (string): The event you want to be notified about (e.g., `transfers#state-change`).
  * `delivery` (object): Contains details about the notification delivery.
    * `url` (string): Your webhook endpoint URL.
    * `mtls_enabled` (boolean): Must be set to `true` to enable mTLS.
2. **Verify Setup:** After creating the subscription, you can test your mTLS configuration by sending a test webhook notification to your server. This is done with a **POST** request to the `subscriptions/{{subscriptionId}}/test-notifications` endpoint.


### Create a new subscription with mTLS enabled

Use the following sample curl request in the sandbox environment to create a new subscription with mTLS enabled.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/applications/{clientKey}/subscriptions' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "name": "Webhook Subscription #1",
    "trigger_on": "transfers#state-change",
    "delivery": {
      "version": "2.0.0",
      "url": "{{yourWebhookUrl}}",
      "mtls_enabled": true
    }
  }'
```

### Verify the mTLS by sending a test webhook event to your webhook server

Use the following sample curl request in the sandbox environment to verify the mTLS setup by sending a test webhook event to your webhook server. Specify the `subscriptionId` from [POST /applications/{{clientKey}}/subscriptions](/api-reference/webhook/webhookapplicationsubscriptioncreate).

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/applications/{clientKey}/subscriptions/{subscriptionId}/test-notifications' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```