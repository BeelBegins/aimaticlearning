# Client credentials tokens

A client credentials token provides partner accounts with application-level access to the Wise Platform API, and is used for requests that aren't tied to a specific Wise user.

Client credentials tokens are most frequently used to:

- Create and retrieve [application webhook subscriptions](/api-reference/webhook/webhookapplicationsubscriptioncreate).
- Create a [user resource](/api-reference/user/usercreate) during onboarding for correspondent and enterprise partners using the API auth flow.
- Create [un-authenticated quotes](/api-reference/quote/quotecreateunauthenticated).
- Set [spend controls on issued cards](/api-reference/spend-controls).


Partners on the embedded model
The Embedded partner integration model has recently been updated to not rely on the user object. As such, these integrations also use client credential tokens for all authenticated requests.

## Prerequisites

Before you begin, make sure you have:

- Your **client ID** and **client secret** (retrieve via [Developer Hub](https://wise.com/developer-hub)).
- [Configured mTLS](/guides/developer/auth-and-security/mtls), which is required for all OAuth 2.0 partners.


## Obtain a client credentials token

Make a [create an OAuth token request](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `client_credentials`.

Token requests must use a form-encoded body and `Content-Type: application/x-www-form-urlencoded`. See the [OAuth integration requirements](/guides/developer/auth-and-security/oauth-2-setup).

Request
```shell curl
curl -i -X POST \
  -u '<client_id>:<client_secret>' \
  https://api.wise.com/2026Q4/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d grant_type=client_credentials
```

Response
The response returns the token value in the `access_token` field.

```json 200 application/json
{
  "access_token": "01234567-89ab-cdef-0123-456789abcdef",
  "token_type": "bearer",
  "refresh_token": "01234567-89ab-cdef-0123-456789abcdef",
  "expires_in": 43199,
  "expires_at": "2025-04-11T03:43:28.148Z",
  "refresh_token_expires_in": 628639555,
  "refresh_token_expires_at": "2045-03-12T13:49:23.552Z",
  "scope": "transfers",
  "created_at": "2020-01-01T12:33:33.12345Z"
}
```

```json 400 application/json
{
  "error": "invalid_request",
  "error_description": "Missing grant type"
}
```

```json 401 application/json
{
  "error": "invalid_grant",
  "error_description": "Invalid user credentials."
}
```

```json 429 application/json
{}
```

This sample response includes a `refresh_token` field, as it is a comprehensive sample for all grant types. However, the `client_credentials` grant flow will not include this field as refresh tokens do not apply to client credential tokens.

## Using the client credentials token

Include the client credentials token in the `Authorization` header of any application-level API requests:

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "GBP",
    "targetCurrency": "USD",
    "sourceAmount": null,
    "targetAmount": 110,
    "pricingConfiguration": {
      "fee": {
        "type": "OVERRIDE",
        "variable": 0.011,
        "fixed": 15.42
      }
    }
  }'
```

Token format migration
Client credentials tokens are migrating from UUID format to JWT format. Do not assume a fixed token size or format.

See the [client credentials token migration guide](/guides/developer/auth-and-security/client-credentials-token-migration) for details and timelines.

## Managing tokens

Client credentials tokens expire after **12 hours**. Your application must proactively request a new token before expiry to avoid service interruption.

To obtain a new client credentials token, send another [create OAuth token request](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `client_credentials`.

To avoid expiration errors, your application should:

- Track the expiry time using the `expires_in` value from the token response.
- Request a new token at application startup and again for each "session" (for example, per payment or each time you onboard a customer).
  - An alternative approach is to request a new token when approximately 80% of the TTL has elapsed (roughly every 9–10 hours).


### Token issuance errors

Token issuance errors occur when calling `POST /oauth/token` with `grant_type=client_credentials`.

| HTTP code | Error  | Cause and solution |
|  --- | --- | --- |
| `400` | `invalid_request` | **Cause**: The `grant_type` parameter is missing from the request body.
**Solution**: Set `grant_type` in the request body to `client_credentials`. |
| `401` | `invalid_client` | **Cause**: Client authentication failed. The `client_id` or `client_secret` in the Basic Authentication header is incorrect.
**Solution**: Verify your `client_id` and `client_secret`. Retrieve the current values from the [Developer Hub](https://developer.wise.com). If you recently rotated your client secret, ensure you are using the active secret. |


**Example `invalid_client` response:**

```json
{
  "error": "invalid_client",
  "error_description": "Client authentication failed"
}
```

Legacy error format
Some partners on the legacy token issuance path may receive `{"error": "unauthorized"}` instead of `invalid_client`. Both indicate the same issue — incorrect client credentials.

This will be standardised to `invalid_client` as part of the
[token format migration](/guides/developer/auth-and-security/client-credentials-token-migration).

### Token validation errors

Validation errors occur when making requests with a client credentials token in the `Authorization` header.

| HTTP code | Error  | Cause and solution |
|  --- | --- | --- |
| `401` | `invalid_token` | **Cause**: The token is expired, was never valid, has been revoked, or was invalidated when a newer token was issued.
**Solution**: Request a new token with `grant_type=client_credentials`. |


**Example `invalid_token` response:**

```json
{
  "error": "invalid_token",
  "error_description": "Invalid token"
}
```

When your application receives a `401 invalid_token` error, it should:

1. Discard the current token.
2. Request a new client credentials token via `POST /oauth/token`.
3. Retry the failed API call with the new token.


### Troubleshooting

If you're experiencing persistent token-related errors, check the following:

1. **Verify your credentials**. Confirm your `client_id` and `client_secret` match the values shown in Developer Hub for the correct environment (sandbox vs production).
2. **Check the Basic Auth encoding**. The `Authorization` header must be `Basic base64(client_id:client_secret)`. Ensure there are no trailing whitespace characters or newlines in the encoded value.
3. **Check for a recent secret rotation**. If you recently rotated your client secret via Developer Hub, confirm you've promoted the new secret and updated your application. During the overlap period, both the old and new secrets are valid — but once the new secret is promoted, the old one is permanently revoked.
4. **Confirm the token hasn't expired**. Client credentials tokens are valid for 12 hours. Use the `expires_in` value from the token response to track expiry.
5. **Confirm the environment**. Sandbox tokens are not valid in production, and vice versa.


For a complete reference of all OAuth 2.0 error codes and recovery procedures, see [Token-related errors](/guides/developer/auth-and-security/oauth-2-setup#token-related-errors) in the OAuth 2.0 Setup guide.