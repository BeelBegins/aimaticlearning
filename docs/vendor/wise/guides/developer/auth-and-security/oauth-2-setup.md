# OAuth 2.0 Setup

Get started with OAuth 2.0 and manage your tokens. 

During onboarding, Wise provides partners with a **client ID** and **client secret**, which you access via the [Developer Hub](https://wise.com/developer-hub). You’ll use them to generate the tokens you need for authenticating your application.

OAuth integration requirements
Requests to `POST /oauth/token` must use a UTF-8 form-encoded body and `Content-Type: application/x-www-form-urlencoded`, as required by [OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749.html). Other request formats are unsupported, even if previously accepted.

Partner integrations use an OAuth 2.0 authentication flow to obtain the following types of tokens:

| Token type  | Purpose | TTL |
|  --- | --- | --- |
| [Client credentials token](/guides/developer/auth-and-security/client-credentials-token) | Used for application-level requests, like subscribing to application webhooks and generating un-authenticated quotes.

Client credentials tokens are also used to authenticate a user with the registration grant flow.

Application-level requests are not specific to a profile. | 12 hours |
| [User access token](/guides/developer/auth-and-security/user-access-token) | Used for profile-level requests, which are requests that transact on behalf of a specific profile.

For Correspondent and Enterprise partner integrations, profile-level requests represent the majority of Wise API actions. | 12 hours |
| [Refresh token](/guides/developer/auth-and-security/refresh-tokens) | To generate new user access tokens without requiring the user to re-authorize. Maintains long-term user access. | Up to 20 years |


Both client credential tokens and user access tokens are **bearer** tokens. Include the token in the `Authorization` header of your requests:

```bash
curl -i -X POST https://api.wise.com/* \
  -H 'Authorization: Bearer <YOUR_TOKEN_HERE>' \
```

Partners on the embedded model
Embedded solutions partners no longer use user access tokens to make requests, as this model has changed to no longer rely on user objects. Partners on this integration model should instead use [client credentials tokens](/guides/developer/auth-and-security/client-credentials-token) for all authenticated requests.

If you are uncertain which token to use for your integration, contact your integration team to confirm.

## Token lifecycle

Both client credential tokens and user access tokens expire after **12 hours** by default. To maintain uninterrupted access and avoid expiration errors, your system should request new tokens well in advance of the token expiration.

### Token management strategy

Track your token expiry time using the `expires_in` value from the token response and request a new access token before the current one expires.

- **Client credentials tokens**: Wise recommends obtaining new client credential tokens for each "session" (for example, per payment or each time you onboard a customer). Review the [Client credential token guide](/guides/developer/auth-and-security/client-credentials-token) for details about obtaining new client credential tokens.
- **User access tokens**: Wise recommends refreshing user access tokens 6 hours prior to expiration. Review the [Refresh tokens guide](/guides/developer/auth-and-security/refresh-tokens) for details about using refresh tokens to obtain new user access tokens.


### Token invalidation behaviours

#### User access tokens

- Access tokens expire 12 hours after issuance.
- When you use a refresh token to obtain a new access token, the old access token is invalidated immediately, even if it has not yet expired.
  - If your system makes concurrent token requests — for example, multiple services refreshing at the same time — only the most recently issued token will work. All other tokens will return `401 invalid_token` (the most common cause of unexpected `401` errors in production).
- When users revoke access or reset passwords, the old access token is invalidated.


#### Refresh tokens

- Refresh tokens are valid for up to 20 years (the exact duration depends on your client configuration).
- When you use a refresh token to obtain a new access token, a new refresh token may also be issued (depending on your client configuration). If a new refresh token is issued, the old one is invalidated.
- When you generate a new refresh token using the `registration_code` grant, the previous refresh token is immediately invalidated.
- A refresh token is also invalidated if the user revokes your application's access, enables enhanced security on their account, or resets their password.
- Wise may revoke a refresh token due to security concerns.
- When profile ownership changes, for example moving your business profile from one user account to another, you may encounter an `invalid_grant` error, as this action invalidates the refresh token.


### Token-related errors

The Wise API returns one of the following error codes for token-related failures. Use this table to identify the cause and determine the correct recovery action.

| HTTP code | Error  | Cause and solution |
|  --- | --- | --- |
| `400` | `invalid_grant` | Occurs when requesting a new token.

Grant type: `authorization_code`

**Cause**: The authorisation code has expired (codes are valid for 10 minutes) or has already been exchanged for a token. Authorisation codes are single-use.
**Solution**: Restart the authorisation flow to obtain a new code. |
| `400` | `invalid_grant` | Occurs when requesting a new token.

Grant type: `authorization_code`

**Cause**: The `redirect_uri` in the token request does not match the `redirect_uri` used in the authorisation request. Both values must be identical, including query parameters.
**Solution**: Retry the token request with the exact same `redirect_uri` you used when directing the user to the authorisation page. |
| `400` | `invalid_grant` | Occurs when requesting a new token.

Grant type: `refresh_token`

**Cause**: The refresh token is expired, revoked, or not found.
**Solution**: If you have a valid registration code, use the `registration_code` grant to obtain a new token pair. Otherwise, the user must re-authorise your application. |
| `400` | `invalid_request` | Occurs when requesting a new token.

Grant type: Any

**Cause**: The `grant_type` parameter is missing from the request body.
**Solution**: Include `grant_type` in the request body. Valid values are `client_credentials`, `authorization_code`, `registration_code`, and `refresh_token`. |
| `401` | `invalid_client` | Occurs when requesting a new token.

Grant type: Any

**Cause**: Client authentication failed. The `client_id` or `client_secret` in the Basic Authentication header is incorrect.
**Solution**: Verify your `client_id` and `client_secret`. Retrieve the current values from the [Developer Hub](https://developer.wise.com). If you recently rotated your client secret, ensure you are using the active secret. |
| `401` | `invalid_grant` | Occurs when requesting a new token.

Grant type: `registration_code`

**Cause**: The registration code is invalid, or the user has reclaimed their Wise account.
**Solution**: If the user reclaimed their account, the registration code is permanently invalidated. Use the `refresh_token` grant if you have a valid refresh token. Otherwise, direct the user through the authorisation code flow or contact the Wise support team for assistance. |
| `401` | `invalid_token` | Occurs when the bearer token in the `Authorization` header is invalid.

Token type: Client credentials token, user access token

**Cause**: The token is expired, was never valid, has been revoked, or was invalidated when a newer token was issued.
**Solution**: Request a new token. For client credentials tokens, make a new `POST /oauth/token` request with `grant_type=client_credentials`. For user access tokens, use your refresh token. |


### Contacting support

If you've worked through the solutions above and are still experiencing issues, contact [api@wise.com](mailto:api@wise.com) with the following information:

- The **`x-trace-id`** from the error response headers.
- The **environment** (production or sandbox).
- The **grant type** you are using (`client_credentials`, `authorization_code`, `registration_code`, or `refresh_token`).
- The **HTTP status code** and **full error response body**.
- **Timestamps** of the failing requests.
- Your **client ID**.


## Rotating your client secret

Your client credentials are made up of your Wise-issued `client_id` and `client_secret`, which do not have any set expiration or rotation requirement. However, you can revoke and rotate your `client_secret` in [Developer Hub](https://wise.com/developer-hub) should you suspect a security breach or your company security policy requires regular rotation.

To rotate your client secret:

1. Log into [Developer Hub](https://wise.com/developer-hub).
2. Go to the **Authentication → Credentials** section.
3. Click **Rotate Secret**.
4. Enter your password and 2FA code when prompted.
5. Copy the new secret and store it in a secure place, then click **Done**.


At this point, both your prior and new secret are active. This allows you test that requests using the new secret work as expected.

Once confirmed the new secret works and the old secret is no longer being used, click **Complete Rotation**. This will promote your new secret and revoke the old one. Any tokens generated using your prior `client_secret` remain unaffected until you use the new secret to generate new tokens.