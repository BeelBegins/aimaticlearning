# User access tokens

A user access token lets your application make requests to the Wise API on behalf of a specific Wise user. Wise issues a user access token once the user authorises the partner application to perform transactions on their behalf.

Wise offers 2 ways to obtain a user access token:

- **Registration code grant flow**: For partners creating users and authorizing application access via API.
  - If you can log in to Wise.com, you can also follow the authorization code grant flow.
- **Authorization code grant flow**: For partners authorizing application access via Wise.com's authorization page.
  - If you created the user's Wise account, you can use the registration code grant to obtain a user access token for each user.


Correspondent and Enterprise partners go through this process only once during onboarding, then maintain access by [refreshing the token](/guides/developer/auth-and-security/refresh-tokens).

Both flows return a user access token and a refresh token. Once you have a valid access token, using it in requests is the same regardless of which grant type you used to obtain it.

Partners on the embedded model
Embedded solutions partners no longer use user access tokens to make requests, as this model has changed to no longer rely on user objects. Partners on this integration model should instead use [client credentials tokens](/guides/developer/auth-and-security/client-credentials-token) for all authenticated requests.

If you are uncertain which token to use for your integration, contact your integration team to confirm.

## Before you begin

Before you can obtain user access tokens, you must have:

- Your **client ID** and **client secret** (retrieve via Developer Hub).
- A **redirect URL** (coordinated during partner onboarding with the Wise implementation team and only required for the authorization code flow).
- Created a Wise account and user (how this occurs will depend on your integration model and you’ll be guided by your onboarding team).


## Obtain a user access token

Token requests must use a form-encoded body and `Content-Type: application/x-www-form-urlencoded`. See the [OAuth integration requirements](/guides/developer/auth-and-security/oauth-2-setup).

Select the flow you wish to view in detail:

Registration code flow
Obtaining a user access token via the registration code flow involves making a [create OAuth token request](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `registration_code`.

**Example request**:

```bash
curl -X POST https://api.wise.com/oauth/token \
  -u '<client_id>:<client_secret>' \
  -d 'grant_type=registration_code' \
  -d 'client_id=<client_id>' \
  -d 'email=<user_email>' \
  -d 'registration_code=<registration_code>'
```

Required data for this request:

- `client_id` and `client_secret`
- `email` is the user’s email address (in the case of the Correspondent integration model, this is a dummy email provided by Wise).
- `registration_code` is the same registration code value generated for the create user account request.


Authorization code flow
Obtaining a user access token via the authorization code flow involves:

1. Directing the user from your application to the Wise authorisation page.
2. The user logging in and granting permission.
3. Wise redirecting the user back to your application with an authorisation code.
4. Your application exchanging the code for an access token and refresh token.


### Redirect to authorisation page

From your application, direct the user to the Wise authorisation page. This is where the user will grant your application permission to perform transactions via the Wise API.

**Wise authorisation page URL path**:

```
/oauth/authorize?client_id=<client_id>&redirect_uri=<redirect_uri>
```

**Query parameters**:

- `client_id`: Your application's client ID.
- `redirect_uri`: Your registered redirect URL (must match exactly).


The user will see a Wise authorisation page where they can log in to the Wise account (if not already logged in), review the permissions your application is requesting, and approve access.

### Receive authorisation code

After the user approves access, Wise redirects them back to your `redirect_uri` with an authorisation code.

The URL will appear in the browser in a format like this:

```
https://your-app.com/callback?code=<authorization_code>
```

You’ll exchange the `authorization_code` value for the token in the next step.

### Exchange auth code for tokens

Exchange the auth code returned in the previous step for an access token and refresh token by making a [create an OAuth token request](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `authorization_code`.

**Example request**:

```bash
curl -X POST https://api.wise.com/oauth/token \
  -u '<client_id>:<client_secret>' \
  -d 'grant_type=authorization_code' \
  -d 'client_id=<client_id>' \
  -d 'code=<authorization_code>' \
  -d 'redirect_uri=<redirect_uri>'
```

Required data for this request:

- `client_id` and `client_secret`
- `code` is the same authorization code value returned from the previous step.
- `redirect_uri` is the redirect URL coordinated with Wise during onboarding.


### Example response

The response is the same for both the authorization and registration code flows. It includes both the `access_token` and `refresh_token`.

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

You can now use the `access_token` in all profile-level requests and refresh the access token prior to its expiration.

## Using the token

Include the access token in the `Authorization` header when making requests on behalf of the user.

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/profiles \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

## Managing user access tokens

User access tokens expire after **12 hours**. Understanding how token invalidation works is critical to avoiding unexpected `401` errors in production.

### Access token invalidation

Only one access token is valid at a time.

When you obtain a new access token (whether via `refresh_token`, `authorization_code`, or `registration_code`) the previously active access token is immediately invalidated. Any requests using the old token will fail with `401 invalid_token`.

This means your application must always store and use the most recently issued access token.

This behaviour is the most common cause of unexpected `401` errors for partners in production. It typically occurs when:

- Multiple backend services independently refresh the token, and one service continues using the old token.
- A retry mechanism triggers a second refresh before the first response is processed.
- The new token is not propagated to all services that make API calls.


### Recovery paths by grant type

#### Authorization grant

If the user originally authorised via the OAuth redirect flow:

1. Attempt to refresh using your stored refresh token.
2. If the refresh token is also invalid, redirect the user to re-authorise then use the authorization code to obtain new tokens.


#### Registration grant

This flow is typically used by integrations using a single partner account and as such go through the flow only once:

1. Attempt to refresh using your stored refresh token.
2. Use your **registration code** to generate a new token pair. The registration code is your primary recovery mechanism — store it securely!


Using the authorization code flow
Correspondent and Enterprise partners cannot redirect a user to re-authorise. However, if both your refresh token and registration code are invalid, but you can log in to Wise.com, you may generate an access token via the authorization code flow.

Otherwise, contact your Wise implementation team or [Wise Platform support](https://docs.wise.com/guides/developer/support) for further assistance.

## User access token errors

This section covers the most common errors you may encounter when obtaining or using user access tokens.

### Errors when obtaining tokens

#### Authorization code grant

| HTTP status | Error  | Cause |
|  --- | --- | --- |
| `400` | `invalid_grant` — `"Authorization code expired."` | The authorisation code has a 10-minute TTL. You must exchange it for tokens within that window. |
| `400` | `invalid_grant` — `"Authorization code is not valid."` | The code has already been used. Each authorisation code can only be exchanged once. |
| `400` | `invalid_grant` — `"Redirect URI mismatch."` | The `redirect_uri` in your token request does not match the one used when redirecting the user to authorise. These must be identical, including query parameters. |
| `401` | `invalid_client` | Your `client_id` or `client_secret` is incorrect, or the Basic Auth header is malformed. |
| `400` | `invalid_request` — `"Missing grant type"` | The `grant_type` parameter is missing from the request body. |


#### Registration code grant

| HTTP status | Error  | Cause |
|  --- | --- | --- |
| `401` | `invalid_grant` — `"Invalid user credentials."` | The registration code is invalid, or the user has reclaimed their Wise account (for example, by resetting their password). |


#### Refresh token grant

| HTTP status | Error  | Cause |
|  --- | --- | --- |
| `400` | `invalid_grant` | The refresh token is expired, revoked, or not found. Can also be caused when a profile is moved to a different account. |
| `401` | `invalid_client` | Your `client_id` or `client_secret` is incorrect. If you recently rotated your client secret, ensure you are using the active secret. |


### Errors when using tokens

| HTTP status | Error  | Cause |
|  --- | --- | --- |
| `401` | `invalid_token` — `"Invalid token"` | The access token is expired, was never valid, was revoked, or was **replaced by a newer token**. Can also be caused by profile ownership change when there is an existing token. |


Legacy error format
Some API paths may return `{"error": "unauthorized"}` instead of `{"error": "invalid_token"}`. Both indicate the same issue — the token is not valid.

This inconsistency is being addressed as part of an ongoing migration.