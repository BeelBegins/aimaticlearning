# Refresh tokens

Learn about generating new user access tokens. 

A refresh token lets your application obtain new user access tokens without requiring the user to re-authorise. Refresh tokens are valid for up to 20 years, enabling long-term access to user accounts.

## Using a refresh token

You’ll receive a refresh token in the same response as the [user access token](/guides/developer/auth-and-security/user-access-token).

User access tokens are valid for **12 hours** by default. Use the refresh token to generate a new user access token before the token expires (Wise recommends a **6 hour** refresh cadence).

Make a [create an OAuth token request](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `refresh_token`.

Token requests must use a form-encoded body and `Content-Type: application/x-www-form-urlencoded`. See the [OAuth integration requirements](/guides/developer/auth-and-security/oauth-2-setup).

Request
```shell curl
curl -i -X POST \
  -u '<client_id>:<client_secret>' \
  https://api.wise.com/2026Q4/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d grant_type=refresh_token \
  -d 'refresh_token=<REFRESH_TOKEN>'
```

Response
The response returns the [OAuth token response](/api-reference/oauth-token/oauthtokencreate) with a new access token.

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

Only one user access token is valid at a time!
When you use a refresh token to generate a new access token, the **previous access token is immediately invalidated**.

Your application must switch to the new token for all subsequent API calls. Any in-flight requests using the old token will receive a `401 invalid_token` error.

### Managing refresh tokens

- Encrypt refresh tokens at rest as they grant long-term access.
- Use centralised storage and avoid multiple services refreshing simultaneously.
- Monitor for anomalies as unusual refresh patterns may indicate compromise.
- If you suspect a token is compromised, prompt the user to re-authorise (for partners using the `authorization_code` grant) or request a new user access and refresh token pair (for partners using the `registration_code` grant flow).


## Invalid refresh tokens

An invalid token returns the error `invalid_grant`. A refresh token can be invalidated before its 20-year expiration for any of the following reasons:

- User revokes your application's access.
- User enables enhanced security on their account.
- Wise revokes token due to security concerns.
- Token validity period expires (if configured shorter than the default value).
- **A new refresh token is generated via a registration code** — this immediately
invalidates the previous refresh token for that user


### Recovery for user-authorised partners

For embedded finance partners, or other partners that use the `authorization_code` grant type.

When a refresh token becomes invalid, your application should:

1. Detect the `invalid_grant` error from the token response.
2. Clear the stored access token and refresh token for that user.
3. Redirect the user through the OAuth authorisation flow to obtain a new authorisation code, then exchange it for a new token pair.


### Recovery for partners using registration code flow

Correspondent and enterprise partners typically don't have a user-facing OAuth redirect flow. If your refresh token is invalidated:

1. Detect the `invalid_grant` error from the token response.
2. Clear the stored tokens for that user or profile.
3. Use your **registration code** to generate a new token pair via `POST /oauth/token` with `grant_type=registration_code`. The registration code is your primary recovery mechanism — store it securely!
  - If the registration code is also invalid (for example, because the user reclaimed the account), contact [api@wise.com](mailto:api@wise.com) for assistance.


Registration code behaviour
Exchanging a registration code generates a new refresh token and immediately invalidates any previous refresh token for that user. Ensure your application updates its stored tokens immediately after the exchange.

### Avoiding concurrent refresh issues

A common cause of token errors is multiple services or instances refreshing the same token simultaneously. When two concurrent refresh requests are made:

1. Both requests succeed and return different access tokens.
2. Only the **last** token issued is valid — the first is immediately invalidated.
3. Any service using the first token receives `401 invalid_token` errors.


To prevent situations where multiple services invalidate each other's tokens:

- **Centralise token management**: Use a single service or process responsible for refreshing tokens and distributing the current valid token to other services.
- **Never refresh in parallel**: If two refresh requests execute simultaneously, both will succeed, but only the token from the second response will be valid. The first token will immediately return `401 invalid_token`.
- **Use locking or queuing**: Implement a mutex or queue around your refresh logic to ensure only one refresh request is in-flight at any time.


## Refresh token errors

These errors can occur when calling `POST /oauth/token` with `grant_type=refresh_token`:

| HTTP status | Error code  | Cause |
|  --- | --- | --- |
| `400` | `invalid_grant` | The refresh token is expired, revoked, or not recognised. |
| `401` | `invalid_client` | Your `client_id` or `client_secret` is incorrect, or the Basic Auth header is malformed. |
| `400` | `invalid_request` | The `grant_type` parameter is missing from the request body. |


**Example `invalid_grant` response:**

```json
{
  "error": "invalid_grant",
  "error_description": "Invalid refresh token (expired or revoked)"
}
```

### Errors after refresh

If your requests fail with `401 invalid_token` immediately after a successful refresh:

1. **Check for concurrent refresh requests**. Another service may have refreshed the token after you did, invalidating your token. Fetch the latest token from your central token store.
2. **Confirm you're using the new token**. Verify your application updated its stored token and is not still using the previous access token.
3. **Check the environment**. Sandbox tokens are not valid in production, and vice versa.