# Quote errors

Handle quote validation, access, route, and state errors.

Quote errors depend on the operation used by your integration. Match the error to the endpoint first, then use the code, `path`, and structured `arguments` to decide what to correct.

Process the complete response
A response can contain more than one error. Process every item in the `errors` array instead of stopping after the first code. Examples labelled "Response excerpt" show only the entries for the named code from a documented response.

On this page:

- [Create an unauthenticated quote](#create-an-unauthenticated-quote)
- [Create an authenticated quote](#create-an-authenticated-quote)
- [Retrieve a quote](#retrieve-a-quote)
- [Update a quote](#update-a-quote)
- [Check a successful quote response](#check-a-successful-quote-response)
- [Retry quote operations](#retry-quote-operations)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely.

## Create an unauthenticated quote

**Endpoint:** `POST /quotes`

See the [related API Reference operation](/api-reference/quote/quotecreateunauthenticated) for the current request and response schema.

A currency field does not contain a valid ISO 4217 alpha-3 code. Use `path` to identify the affected field.

**HTTP status:** `400`

**What to do**

Use `path` to identify the currency field and provide a valid ISO 4217 alpha-3 code. A valid currency code does not by itself establish that the currency route is supported.

**Retry conditions**

Retry after correcting the currency.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "CurrencyCode",
      "message": "That wasn't a valid ISO-4217 currency code (like GBP, USD or EUR).",
      "path": "targetCurrency"
    }
  ]
}
```

A currency specified in the request has been deprecated. Use `path` to identify the affected field.

**HTTP status:** `400`

**What to do**

Replace the deprecated currency with a currently supported currency.

**Retry conditions**

Retry after changing the currency.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "CurrencyDeprecated",
      "message": "Currency has been deprecated.",
      "path": "targetCurrency"
    }
  ]
}
```

An amount must be greater than zero. Use `path` to identify whether the source or target amount failed validation.

**HTTP status:** `400`

**What to do**

Validate amounts greater than zero before sending the request. Use `path` to identify a rejected amount. If the customer controls it, let them correct it; also investigate why local validation did not catch it.

**Retry conditions**

Retry after correcting the amount.

**Response excerpt**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.greaterThanZero",
      "message": "Please type in a number that's larger than 0.",
      "path": "sourceAmount"
    }
  ]
}
```

The amount exceeds the maximum accepted by the quote operation. Use `path` to identify the amount and check the applicable limit.

**HTTP status:** `400`

**What to do**

Reduce the amount to the accepted range for the selected currency.

**Retry conditions**

Retry after reducing the amount.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.amount.tooLarge",
      "message": "Amount is too large, it should not exceed 1 trillion in any currency",
      "path": "sourceAmount"
    }
  ]
}
```

The amount is below the minimum accepted for the selected currency. Use `path` to identify the affected amount.

**HTTP status:** `400`

**What to do**

Increase the amount to the accepted range for the selected currency.

**Retry conditions**

Retry after increasing the amount.

**Response excerpt**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.amount.tooSmall",
      "message": "Amount is too small for specified currency",
      "path": "targetAmount"
    }
  ]
}
```

The request does not satisfy the authentication or profile-access requirements for the quote operation.

**HTTP status:** `401`

**What to do**

Keep token type and profile mappings correct before sending requests. If this error occurs, verify that mapping; stop safely, show an appropriate customer message, and record the issue for investigation if the cause is unexpected or unresolved. This response can occur when a valid token cannot access the requested profile. Renew the token only if the response separately identifies it as invalid.

**Retry conditions**

Retry after correcting authentication.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.mustBeAuthenticated",
      "message": "You need to be authenticated to do that."
    }
  ]
}
```

Rate volatility prevents Wise from creating a quote with a fixed target amount for this request.

**HTTP status:** `422`

**What to do**

Send `sourceAmount` instead so Wise can calculate the target amount at the available rate.

**Retry conditions**

Retry after changing the amount side.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.targetAmount.notSupported.volatility.partner",
      "message": "Rates are volatile so we can't guarantee how much the recipient gets. Specify a source amount instead."
    }
  ]
}
```

Wise cannot resolve a country specified in the request. Use `path` to identify the affected country field.

**HTTP status:** `400`

**What to do**

Use `path` to identify the country field, then provide a supported value. The example identifies `payInCountry`.

**Retry conditions**

Retry after correcting the country.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.recipient.country.notFound",
      "message": "Cannot find specified recipient country.",
      "path": "payInCountry"
    }
  ]
}
```

### Malformed request 

No error code is returned in this response.

Wise could not read or convert the request, and the response does not expose a stable operation-specific code.

**HTTP status:** `400`

**What to do**

Compare the request with the operation schema and use a safe fallback when no stable identifier is returned.

**Retry conditions**

Retry only after correcting the request. Treat service failures separately.

**Example error response**

```json
{
  "detail": "Failed to read request",
  "instance": "/public/v3/quotes/",
  "properties": null,
  "status": 400,
  "title": "Bad Request",
  "type": null
}
```

## Create an authenticated quote

**Endpoint:** `POST /profiles/{profileId}/quotes`

See the [related API Reference operation](/api-reference/quote/quotecreate) for the current request and response schema.

A currency field does not contain a valid ISO 4217 alpha-3 code. Use `path` to identify the affected field.

**HTTP status:** `400`

**What to do**

Use `path` to identify the currency field and provide a valid ISO 4217 alpha-3 code. A valid currency code does not by itself establish that the currency route is supported.

**Retry conditions**

Retry after correcting the currency.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "CurrencyCode",
      "message": "That wasn't a valid ISO-4217 currency code (like GBP, USD or EUR).",
      "path": "targetCurrency"
    }
  ]
}
```

A currency specified in the request has been deprecated. Use `path` to identify the affected field.

**HTTP status:** `400`

**What to do**

Replace the deprecated currency with a currently supported currency.

**Retry conditions**

Retry after changing the currency.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "CurrencyDeprecated",
      "message": "Currency has been deprecated.",
      "path": "targetCurrency"
    }
  ]
}
```

Wise cannot find the recipient account identified by the request.

**HTTP status:** `422`

**What to do**

Check `targetAccount`, the environment, and the profile/token context. If the customer selects the recipient, let them choose or add another. Use your own customer message without exposing the recipient ID.

**Retry conditions**

Retry with an account available to the profile.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        111111111
      ],
      "code": "error.account.notFound",
      "message": "We couldn't find an account with that ID (111,111,111)."
    }
  ]
}
```

The recipient account cannot receive this payment. Documented cases include an unusable account and changes to the recipient's receiving details.

**HTTP status:** `422`

**What to do**

Check the recipient and route context. If the response identifies changed receiving details, ask the recipient for updated account details. If it gives no actionable reason, investigate with Wise before choosing a recovery action.

**Retry conditions**

Do not retry with the same unusable account.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        111111111
      ],
      "code": "error.account.notUsable",
      "message": "We cannot currently accept payments to this recipient."
    }
  ]
}
```

Wise cannot find the referenced contact.

**HTTP status:** `422`

**What to do**

The current quote schema does not document a contact-ID field. If you receive this identifier, record the request and response and ask Wise to confirm the applicable contact flow. Do not substitute a contact UUID for the integer `targetAccount`.

**Retry conditions**

Do not retry automatically; resolve the applicable request contract first.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        "21ecd0bc-da9e-4f95-b378-2e9a05167104"
      ],
      "code": "error.contact.notFound",
      "message": "We couldn't find a contact with that ID (21ecd0bc-da9e-4f95-b378-2e9a05167104)."
    }
  ]
}
```

Wise cannot process the referenced contact for this request. The code alone does not identify the underlying reason.

**HTTP status:** `422`

**What to do**

The current quote schema does not document a contact-ID field. If you receive this identifier, record the request and response and ask Wise to confirm the applicable contact flow. Do not substitute a contact UUID for the integer `targetAccount`.

**Retry conditions**

Do not retry automatically; resolve the applicable request contract first.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        "21ecd0bc-da9e-4f95-b378-2e9a05167104"
      ],
      "code": "error.contact.notUsable",
      "message": "We couldn't process that contact."
    }
  ]
}
```

An amount must be greater than zero. Use `path` to identify whether the source or target amount failed validation.

**HTTP status:** `400`

**What to do**

Validate amounts greater than zero before sending the request. Use `path` to identify a rejected amount. If the customer controls it, let them correct it; also investigate why local validation did not catch it.

**Retry conditions**

Retry after correcting the amount.

**Response excerpt**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.greaterThanZero",
      "message": "Please type in a number that's larger than 0.",
      "path": "targetAmount"
    }
  ]
}
```

The request specifies both `sourceAmount` and `targetAmount`.

**HTTP status:** `400`

**What to do**

Send exactly one of `sourceAmount` or `targetAmount`.

**Retry conditions**

Retry after removing one amount.

**Example error response**

```json
{
  "errors": [
    {
      "code": "error.quote.amount.onlySingle",
      "message": "Please only specify a source or target amount.",
      "path": "sourceAmount",
      "arguments": []
    }
  ]
}
```

The amount exceeds the maximum accepted by the quote operation. Use `path` to identify the amount and check the applicable limit.

**HTTP status:** `400`

**What to do**

Reduce the amount to the accepted range for the selected currency.

**Retry conditions**

Retry after reducing the amount.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.amount.tooLarge",
      "message": "Amount is too large, it should not exceed 1 trillion in any currency",
      "path": "sourceAmount"
    }
  ]
}
```

The amount is below the minimum accepted for the selected currency. Use `path` to identify the affected amount.

**HTTP status:** `400`

**What to do**

Increase the amount to the accepted range for the selected currency.

**Retry conditions**

Retry after increasing the amount.

**Response excerpt**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.amount.tooSmall",
      "message": "Amount is too small for specified currency",
      "path": "targetAmount"
    }
  ]
}
```

The request does not satisfy the authentication or profile-access requirements for the quote operation.

**HTTP status:** `401`

**What to do**

Keep token type and profile mappings correct before sending requests. If this error occurs, verify that mapping; stop safely, show an appropriate customer message, and record the issue for investigation if the cause is unexpected or unresolved. This response can occur when a valid token cannot access the requested profile. Renew the token only if the response separately identifies it as invalid.

**Retry conditions**

Retry after correcting authentication.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.mustBeAuthenticated",
      "message": "You need to be authenticated to do that."
    }
  ]
}
```

The pricing configuration for the quote is invalid.

**HTTP status:** `422`

**What to do**

Verify the quote request and pricing configuration available to the integration. Contact Wise if the request is valid.

**Retry conditions**

Retry only after correcting the configuration or receiving confirmation that it is available.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.pricing.configuration.invalid",
      "message": "Invalid pricing configuration"
    }
  ]
}
```

Rate volatility prevents Wise from creating a quote with a fixed target amount for this request.

**HTTP status:** `422`

**What to do**

Send `sourceAmount` instead so Wise can calculate the target amount at the available rate.

**Retry conditions**

Retry after changing the amount side.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.targetAmount.notSupported.volatility.partner",
      "message": "Rates are volatile so we can't guarantee how much the recipient gets. Specify a source amount instead."
    }
  ]
}
```

The requested currency route is not currently supported for this request.

**HTTP status:** `422`

**What to do**

For an unexpected route rejection, stop and record the issue for Wise API Support. Prevent requests for routes already known to be unavailable. A customer choosing another route starts a new request; do not automatically substitute a route.

**Retry conditions**

Do not automatically retry the same route.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        {
          "source": "AUD",
          "target": "INR"
        }
      ],
      "code": "error.route.not.supported",
      "message": "Sorry, you can't send between these currencies right now."
    }
  ]
}
```

### Malformed request 

No error code is returned in this response.

Wise could not read or convert the request, and the response does not expose a stable operation-specific code.

**HTTP status:** `400`

**What to do**

Compare the request with the operation schema and use a safe fallback when no stable identifier is returned.

**Retry conditions**

Retry only after correcting the request. Treat service failures separately.

**Example error response**

```json
{
  "detail": "Failed to read request",
  "instance": "/public/v3/profiles/111111111/quotes",
  "properties": null,
  "status": 400,
  "title": "Bad Request",
  "type": null
}
```

## Retrieve a quote

**Endpoint:** `GET /profiles/{profileId}/quotes/{quoteId}`

See the [related API Reference operation](/api-reference/quote/quoteget) for the current request and response schema.

Wise cannot find the quote identified by the request.

**HTTP status:** `404`

**What to do**

Verify the quote ID, profile, environment, and access context.

**Retry conditions**

Retry only after correcting the lookup context.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        "21ecd0bc-da9e-4f95-b378-2e9a05167104"
      ],
      "code": "error.quote.not.found",
      "message": "We couldn't find a quote with that ID (21ecd0bc-da9e-4f95-b378-2e9a05167104)"
    }
  ]
}
```

The request does not satisfy the authentication or profile-access requirements for the quote operation.

**HTTP status:** `401`

**What to do**

Keep token type and profile mappings correct before sending requests. If this error occurs, verify that mapping; stop safely, show an appropriate customer message, and record the issue for investigation if the cause is unexpected or unresolved. This response can occur when a valid token cannot access the requested profile. Renew the token only if the response separately identifies it as invalid.

**Retry conditions**

Retry after correcting authentication.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "error.quote.mustBeAuthenticated",
      "message": "You need to be authenticated to do that."
    }
  ]
}
```

The quote's current state does not permit the requested operation.

**HTTP status:** `422`

**What to do**

Retrieve the latest quote and continue only from a state that permits the operation.

**Retry conditions**

Retry only when the current quote state permits it.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        {
          "current": null,
          "expected": "NEW"
        }
      ],
      "code": "error.quote.status.unexpected",
      "message": "Current quote status does not allow this operation"
    }
  ]
}
```

The request does not meet the access requirements for the quote operation.

**HTTP status:** `403`

**What to do**

Verify the token, profile, environment, and quote ownership. Show a generic access message.

**Retry conditions**

Retry only after correcting the access context.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "security.error",
      "message": "We couldn't authorise your request."
    }
  ]
}
```

An unexpected technical failure prevented Wise from completing the quote operation. The code does not identify a specific cause.

**HTTP status:** `500`

**What to do**

Log a redacted response signature and reconcile the quote state before retrying.

**Retry conditions**

Do not automatically retry an unexplained failure. Retry only if a transient cause and safe replay are confirmed, using bounded backoff.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "unexpected.error",
      "message": "Sorry, there was a technical problem. Please try again."
    }
  ]
}
```

### Invalid quote identifier 

No error code is returned in this response.

Wise could not read or convert the request, and the response does not expose a stable operation-specific code.

**HTTP status:** `400`

**What to do**

Compare the request with the operation schema and use a safe fallback when no stable identifier is returned.

**Retry conditions**

Retry only after correcting the request. Treat service failures separately.

**Example error response**

```json
{
  "detail": "Failed to convert 'quoteId' with value: 'None'",
  "instance": "/public/v3/profiles/1111111/quotes/None",
  "properties": null,
  "status": 400,
  "title": "Bad Request",
  "type": null
}
```

## Update a quote

**Endpoint:** `PATCH /profiles/{profileId}/quotes/{quoteId}`

See the [related API Reference operation](/api-reference/quote/quoteupdate) for the current request and response schema.

The quote has expired and can no longer be used for this operation.

**HTTP status:** `422`

**What to do**

Create a new quote and continue with the new quote ID.

**Retry conditions**

Do not retry with the expired quote.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        {
          "current": "EXPIRED",
          "expected": "NEW"
        }
      ],
      "code": "error.quote.expired",
      "message": "Sorry, your quote has expired. Please get a new one."
    }
  ]
}
```

Wise cannot find the quote identified by the request.

**HTTP status:** `404`

**What to do**

Verify the quote ID, profile, environment, and access context.

**Retry conditions**

Retry only after correcting the lookup context.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        "21ecd0bc-da9e-4f95-b378-2e9a05167104"
      ],
      "code": "error.quote.not.found",
      "message": "We couldn't find a quote with that ID (21ecd0bc-da9e-4f95-b378-2e9a05167104)"
    }
  ]
}
```

Wise cannot find the recipient account identified by the request.

**HTTP status:** `422`

**What to do**

Check `targetAccount`, the environment, and the profile/token context. If the customer selects the recipient, let them choose or add another. Use your own customer message without exposing the recipient ID.

**Retry conditions**

Retry with an account available to the profile.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        1111
      ],
      "code": "error.account.notFound",
      "message": "We couldn't find an account with that ID (1.111)."
    }
  ]
}
```

The requested currency route is not currently supported for this request.

**HTTP status:** `422`

**What to do**

For an unexpected route rejection, stop and record the issue for Wise API Support. Prevent requests for routes already known to be unavailable. A customer choosing another route starts a new request; do not automatically substitute a route.

**Retry conditions**

Do not automatically retry the same route.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [
        {
          "source": "EUR",
          "target": "GBP"
        }
      ],
      "code": "error.route.not.supported",
      "message": "Sorry, you can't send between these currencies right now."
    }
  ]
}
```

An unexpected technical failure prevented Wise from completing the quote operation. The code does not identify a specific cause.

**HTTP status:** `500`

**What to do**

Log a redacted response signature and reconcile the quote state before retrying.

**Retry conditions**

Do not automatically retry an unexplained failure. Retry only if a transient cause and safe replay are confirmed, using bounded backoff.

**Example error response**

```json
{
  "errors": [
    {
      "arguments": [],
      "code": "unexpected.error",
      "message": "Sorry, there was a technical problem. Please try again."
    }
  ]
}
```

### Malformed request 

No error code is returned in this response.

Wise could not read or convert the request, and the response does not expose a stable operation-specific code.

**HTTP status:** `400`

**What to do**

Compare the request with the operation schema and use a safe fallback when no stable identifier is returned.

**Retry conditions**

Retry only after correcting the request. Treat service failures separately.

**Example error response**

```json
{
  "detail": "Failed to read request",
  "instance": "/public/v3/profiles/1111/quotes/21ecd0bc-da9e-4f95-b378-2e9a05167104",
  "properties": null,
  "status": 400,
  "title": "Bad Request",
  "type": null
}
```

## Check a successful quote response

HTTP `200` means the quote request succeeded. Before using it, find the payment option matching the quote's `payOut` and your settlement model's `payIn`.

- Check that option's `disabled` flag and, if disabled, its `disabledReason.code` and `disabledReason.message`.
- Do not treat one disabled option as evidence that every option is unavailable.
- Show an actionable amount-limit message when suitable for the customer. Map technical or partner-funding conditions to your own message; do not expose a correspondent's balance shortage as the customer's balance problem.


A `FLOATING` rate is not itself an API error. Follow the [authenticated quote guide](/guides/product/send-money/quotes/authenticated-quote) for rate guarantees and customer communication. See the [quote response reference](/api-reference/quote/quotecreate) for payment-option fields.

## Retry quote operations

- Correct validation, amount, recipient, and route errors before retrying.
- Renew a token only for an invalid-token response. Check token type and profile access for `error.quote.mustBeAuthenticated`.
- Resolve access or ownership before retrying access errors.
- Create a new quote instead of retrying an expired quote.
- Follow `Retry-After` for `429` responses.
- Retry only confirmed transient failures with bounded exponential backoff and jitter, where replay is safe. Stop and investigate unexplained failures or exhausted recovery.