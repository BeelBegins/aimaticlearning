# Authentication and access errors

Handle invalid credentials, access denials, and SCA challenges.

Authentication errors indicate that Wise could not verify your credentials. Access errors indicate that the authenticated identity cannot perform the requested action. Both can use similar response formats, so inspect the HTTP status, error identifier, and response headers together.

On this page:

- [Request an access token](#request-an-access-token)
- [Call protected operations](#call-protected-operations)
- [Distinguish 401 from 403](#distinguish-401-from-403)
- [Handle an invalid access token](#handle-an-invalid-access-token)
- [Handle an SCA response](#handle-an-sca-response)
- [Map messages safely](#map-messages-safely)
- [Related authentication guides](#related-authentication-guides)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely.

## Request an access token

**Endpoint:** `POST /oauth/token`

See the [create an access token operation](/api-reference/oauth-token/oauthtokencreate) for the current request and response schema.

The authentication or token request is missing a required value or is malformed.

**What to do**

- Compare the request with the applicable token operation.
- Add or correct the required parameters.


**Retry conditions**

Do not retry the unchanged request.

Wise cannot authenticate the client application.

**What to do**

- Verify the current client credentials and authentication method.
- Check the header format without writing secrets to logs.


**Retry conditions**

Retry only after correcting the client authentication.

**Example error response**

```json
{
  "error": "invalid_client",
  "error_description": "Client authentication failed"
}
```

The OAuth grant is invalid, expired, revoked, or already used.

**What to do**

- Restart the applicable authorisation flow or obtain a new grant.
- Stop using the rejected value.


**Retry conditions**

Do not repeatedly submit the same grant.

## Call protected operations

**Endpoint:** Any operation that requires an access token

The following codes can apply across authenticated API domains. Interpret them with the operation, HTTP status, and response headers.

The bearer token is expired, revoked, replaced, or otherwise invalid.

**What to do**

- Discard the rejected token.
- Obtain and distribute a valid token before sending more requests.


**Retry conditions**

Retry the failed request once with the new token only when replay is safe, following the operation's idempotency rules where applicable. If renewal or replay fails, stop safely, show an appropriate customer message, and record the issue for investigation.

**Example error response**

```json
{
  "error": "invalid_token",
  "error_description": "Invalid token"
}
```

The request does not include a bearer token where one is required.

**What to do**

- Add `Authorization: Bearer <token>` using a token valid for the operation.
- Check intermediaries that may remove sensitive headers.


**Retry conditions**

Retry after adding the token.

**Example error response**

```json
{
  "error": "missing_token",
  "error_description": "Missing token"
}
```

The request is not authenticated or the authenticated identity cannot perform the operation.

**What to do**

- Use the HTTP status and response headers to distinguish authentication from permission or SCA problems.
- Verify the token, profile, and operation.


**Retry conditions**

Retry only after correcting the authentication or access context.

The authenticated identity is not permitted to access the operation or resource.

**What to do**

- Verify the token type, profile, ownership, and integration permissions.
- Display a generic permission message.


**Retry conditions**

Do not retry unchanged.

The authenticated identity cannot access the requested operation or resource.

**What to do**

- Verify authentication, profile ownership, and permissions.
- Do not reveal whether an inaccessible resource belongs to another user.


**Retry conditions**

Retry only after correcting the access context.

## Distinguish 401 from 403

Use the HTTP status as the first decision point:

- `401` can mean invalid credentials or a token that cannot access the requested profile. Inspect the identifier before renewing the token.
- `403` usually means that Wise recognised the request but did not permit the action.
- An SCA-protected operation also uses `403`. Check the documented SCA headers before treating it as a permanent access denial.


Do not refresh on every access error
Refreshing a token does not fix a profile ownership, permission, or SCA issue. Refresh only when the response indicates that the token is invalid.

## Handle an invalid access token

To recover from an invalid access token:

1. Stop using the rejected access token.
2. Obtain a new token using the appropriate grant.
3. Store and distribute the new token before sending more requests.
4. Retry the failed request once with the new token, following the operation's idempotency rules where applicable.
5. If token renewal or replay fails, stop safely, show an appropriate customer message, and record the issue for investigation. Do not expose token details to the customer.


For user access tokens, centralise refreshes so 2 services do not invalidate each other's tokens. See [refresh tokens](/guides/developer/auth-and-security/refresh-tokens) for concurrency and storage guidance.

## Handle an SCA response

An SCA-protected operation can return `403` with Wise-specific response headers. Inspect the headers before deciding that the caller lacks permission.

1. Check for `X-2FA-Approval` and `X-2FA-Approval-Result`.
2. Complete the required SCA challenge.
3. Retry the protected operation with the approved one-time token.


See [SCA and two-factor authentication](/guides/developer/auth-and-security/sca-and-2fa) for the supported flow.

## Map messages safely

Authentication and access messages are developer-facing by default:

- Do not display `error_description` directly to an end user.
- Do not reveal whether another profile owns a requested resource.
- Map invalid credentials to a generic authentication message.
- Map access denials to a generic permission message.
- Log the error identifier and operation without logging tokens or secrets.


## Related authentication guides

- [Client credentials tokens](/guides/developer/auth-and-security/client-credentials-token).
- [User access tokens](/guides/developer/auth-and-security/user-access-token).
- [Refresh tokens](/guides/developer/auth-and-security/refresh-tokens).
- [OAuth 2.0 setup](/guides/developer/auth-and-security/oauth-2-setup).
- [Mutual TLS](/guides/developer/auth-and-security/mtls).