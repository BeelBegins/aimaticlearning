# Handle API errors

Understanding errors and how to recover from them.

When a Wise API request fails, your integration needs to decide how to continue. The error may be preventable from upfront validation, the customer may need to correct an entry, your application may need to retry, or the failure may need investigation.

This guide explains how to respond to errors and recover safely. Read our [error code guides](#error-guides) for guidance and examples for specific operations.

## Choose a recovery action 

Use the guidance for the operation you called to decide what needs correcting and whether the request can be retried. The same error code can require different actions depending on the affected field and who controls its value.

## Apply the handling safely 

Use the operation, HTTP status, error code, and affected field to identify the appropriate action. If the response has no code or you cannot confirm a handling path, stop safely, show an appropriate customer message, and record the issue for investigation.

Keep customer messages separate from automatic recovery. Retry only when the operation and its current state make it safe.

### Display or map error messages

1. When the customer can correct the input, associate a safe, actionable message with the affected field. Provide a form-level message when no field is identified.
2. For authentication, access, configuration, or unexpected failures, use your own generic customer message. Do not display raw diagnostic details.
3. Keep message text out of programmatic decisions. Use documented identifiers and response fields instead.


Match the message to the action available. Do not ask the customer to change details they do not control, or expose a partner's funding balance as a customer balance problem.

### Recover only when there is a defined action

For `invalid_token`, obtain a fresh token through your configured token flow and repeat the request once, provided replay is safe for that operation. If renewal or replay fails, stop safely, show an appropriate customer message, and record the issue for investigation.

Do not renew tokens for every `401` or `403`. Incorrect profile access, permissions, and strong customer authentication (SCA) require their own checks. See [authentication and access errors](/guides/developer/errors/authentication) for more details.

A `5xx` response alone does not establish a transient failure. Retry only when the condition has a confirmed recovery path and the operation is safe to repeat. Otherwise, record and investigate it.

### Rate limiting

An HTTP `429` response means a rate limit has been reached. When your process can safely wait and retry, follow `Retry-After` if supplied:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

Wait at least the specified interval. Use bounded exponential backoff with jitter: increase the delay between attempts, add a small random variation, and stop at a configured limit. Reduce request rate or concurrency if limits continue.

If the customer journey cannot safely wait and retry, stop safely, show an appropriate customer message, and record the issue for investigation. See [rate limiting](/guides/developer#rate-limiting) for gateway and service-level limits.

### Check uncertain outcomes before retrying 

A timeout or connection failure does not prove that Wise rejected the request.

- Retry read-only requests with bounded backoff where appropriate.
- For a state-changing operation, use its documented idempotency mechanism or check whether the original action completed before deciding to retry.
- Reuse the same idempotency identifier for the same logical attempt. A new identifier can create a duplicate.
- If you cannot establish safe replay, stop and investigate. Do not tell the customer the operation definitely failed or invite another submission while its outcome is uncertain.


## Record and investigate unresolved errors

Use one shared fallback for unrecognised responses and failed recovery. Stop the current operation safely, show a suitable generic message, and retain evidence.

Record the Wise trace ID (`x-trace-id`) when a response supplies it. Include it when contacting Wise API Support, together with:

- The HTTP method, versioned endpoint, environment, and timestamp with timezone.
- The HTTP status, content type, and relevant response headers.
- A redacted request and response, including every error item.
- The intended action, profile context, and any correction, recovery, or state check already attempted.


If no response arrived or no trace ID was supplied, record that explicitly. Never log tokens, client secrets, or unnecessary personal and bank data.

Report known integration defects to your integration owner. Report Wise-owned or unresolved API failures to Wise API Support. Add a new automated handling rule only after the cause and required action are confirmed.

## Test your handlers

Test your error handling before launch, including invalid input, failed recovery, an unrecognised response, and an uncertain request outcome. Verify that:

- Corrected input can be submitted without retrying the rejected values.
- Recovery stops at its retry limit and does not create duplicate actions.
- Documented business failures are detected even after HTTP success.
- Customer messages and support records do not expose sensitive information.


## HTTP status codes

Use HTTP status as a starting point, then inspect the operation-specific response.

| Status | Meaning for handling |
|  --- | --- |
| `2xx` | The HTTP request succeeded. Check documented business result fields before continuing. |
| `400` or `422` | The request failed parsing, field validation, or a business rule. Determine what needs correcting. |
| `401` | Authentication is missing, invalid, or unsuitable for the requested profile. Inspect the error before renewing a token. |
| `403` | Access is denied, or an additional authentication step such as SCA is required. |
| `404` | The resource does not exist or is not available in the current access context. |
| `408` | The request timed out. Its outcome may need checking before a retry. |
| `409` | The request conflicts with the resource's current state. Check that state before continuing. |
| `429` | A rate limit has been reached. Follow the safe retry guidance for your process. |
| `5xx` | Wise or a downstream service could not complete the request. Confirm the cause and retry safety before repeating it. |


## Error guides

Use the guide for the operation you called. Each example illustrates a documented case (its IDs, currencies, and limits do not define every occurrence). Match the endpoint and API version, and use the current operation requirements.

- [Authentication errors](/guides/developer/errors/authentication)
- [User errors](/guides/developer/errors/users)
- [Profile errors](/guides/developer/errors/profiles)
- [Quote errors](/guides/developer/errors/quotes)
- [Recipient errors](/guides/developer/errors/recipients)
- [Transfer errors](/guides/developer/errors/transfers)
- [Funding errors](/guides/developer/errors/funding)
- [Webhook subscription errors](/guides/developer/errors/webhooks)


These guides describe the operations listed on each page. They are not an exhaustive catalogue for every API reference domain.