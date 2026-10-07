# Webhook errors

Handle webhook subscription and test notification errors.

These errors apply when you create, retrieve, delete, or test a profile-level or application-level subscription. For event delivery and retry behaviour, see [webhook event handling](/guides/developer/webhooks/event-handling).

On this page:

- [Create a profile subscription](#create-a-profile-subscription)
- [Create an application subscription](#create-an-application-subscription)
- [Get or delete a subscription](#get-or-delete-a-subscription)
- [Test a subscription](#test-a-subscription)
- [Shared access errors](#shared-access-errors)
- [Handle response formats](#handle-response-formats)
- [Retry webhook operations](#retry-webhook-operations)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely.

## Create a profile subscription

**Endpoint:** `POST /profiles/{profileId}/subscriptions`

See the [create a profile subscription operation](/api-reference/webhook/webhookprofilesubscriptioncreate) for the current schema.

A required subscription field is missing or malformed.

**What to do**

- Process every item in `errors` and every string in `arguments`.
- Map the returned detail to the affected subscription field.


**Retry conditions**

Retry after correcting the request.

The event type is not available for profile-level subscriptions.

**What to do**

Choose a supported event or use the application-level operation when the event requires that scope.

**Retry conditions**

Retry after changing the event or subscription scope.

The callback URL fails formatting, accessibility, HTTPS, or security validation.

**What to do**

- Correct the endpoint and verify it from the public internet.
- Remove redirects or access controls that block validation.
- Avoid secrets in callback URL query parameters.


**Retry conditions**

Retry after the callback endpoint passes these checks.

**Example error response**

```json
{
  "code": "INVALID_CALLBACK_URL",
  "message": "The provided callback URL is invalid or not secure",
  "arguments": [
    "http://example.com/webhook"
  ]
}
```

The maximum number of subscriptions for the event type has been reached.

**What to do**

List and reconcile existing subscriptions, then reuse or delete one before creating another.

**Retry conditions**

Retry only after reducing the number of subscriptions.

## Create an application subscription

**Endpoint:** `POST /applications/{clientKey}/subscriptions`

See the [create an application subscription operation](/api-reference/webhook/webhookapplicationsubscriptioncreate) for the current schema.

A required application subscription field is missing or malformed.

**What to do**

Process every returned error and compare the request with the operation schema.

**Retry conditions**

Retry after correcting the request.

The event type is not available for application-level subscriptions.

**What to do**

Choose a supported event or use the profile-level operation when the event requires that scope.

**Retry conditions**

Retry after changing the event or subscription scope.

The callback URL fails formatting, accessibility, HTTPS, or security validation.

**What to do**

Correct and verify the public HTTPS callback endpoint.

**Retry conditions**

Retry after the callback URL passes validation.

The application has reached the subscription limit for the selected event type.

**What to do**

List and reconcile existing subscriptions, then reuse or delete one before creating another.

**Retry conditions**

Retry only after reducing the number of subscriptions.

## Get or delete a subscription

**Endpoints:**

- `GET /profiles/{profileId}/subscriptions/{subscriptionId}`
- `DELETE /profiles/{profileId}/subscriptions/{subscriptionId}`
- `GET /applications/{clientKey}/subscriptions/{subscriptionId}`
- `DELETE /applications/{clientKey}/subscriptions/{subscriptionId}`


The request contains an invalid subscription identifier or path parameter.

**What to do**

Compare the parameter with the applicable operation schema and correct it.

**Retry conditions**

Do not retry the unchanged request.

The subscription is not available for the supplied owner.

**What to do**

- Verify the owner and subscription ID together.
- Show a generic not-found message.
- Reconcile the appropriate subscription list before removing a cached record.


**Retry conditions**

Retry only after correcting the owner or subscription ID.

## Test a subscription

**Endpoint:** `POST /applications/{clientKey}/subscriptions/{subscriptionId}/test-notifications`

See the [test an application subscription operation](/api-reference/webhook/webhookapplicationsubscriptiontest) for the current schema.

The selected event schema version is not supported for the test notification.

**What to do**

Retrieve the available event information and choose a supported schema version.

**Retry conditions**

Retry after selecting a supported version.

## Shared access errors

**Endpoint:** Any webhook subscription operation

The request is not authenticated for webhook subscription management.

**What to do**

Obtain a valid token and verify the subscription owner.

**Retry conditions**

Retry after correcting authentication.

The authenticated identity cannot manage subscriptions for the selected profile or application.

**What to do**

- Verify token permissions, resource ownership, and subscription scope.
- Do not expose ownership details to an unauthorised caller.


**Retry conditions**

Retry only after correcting the access context.

## Handle response formats

Profile and application subscription operations can use different response envelopes. Support both a single error object and an `errors` array. Process every validation item and every string in `arguments`.

Do not assume all operations use the same envelope. Do not parse message text or use it for programmatic branching.

## Retry webhook operations

- Correct validation and callback URL errors before retrying.
- Change the event or scope for `EVENT_TYPE_NOT_PERMITTED`.
- Reconcile existing subscriptions for `SUBSCRIPTION_LIMIT_EXCEEDED`.
- Correct authentication or ownership before retrying access errors.
- Retry transient service failures with exponential backoff and jitter.
- Reconcile the subscription state after an uncertain create or delete result.