Exchange client credentials or authorisation grants for OAuth 2.0 access tokens. All grant types use `POST /oauth/token` with basic authentication (your `client_id` and `client_secret`).

Depending on the grant type, this endpoint issues either a **client credentials token** or a **user token**.

Client credentials token 

An application-level token for requests that aren't tied to a specific Wise user, such as generating un-authenticated quotes and subscribing to application webhooks. Valid for 12 hours.

- `client_credentials` — the only grant type for this token.


User token 

A token for making API calls on behalf of a specific Wise user, such as creating transfers and managing balances. Access tokens are valid for 12 hours and can be refreshed using a refresh token. Grant types:

- `registration_code` — for partners that create Wise users via API. Exchanges a registration code for a user access token and refresh token.
- `authorization_code` — for partners using the OAuth redirect flow. Exchanges an authorisation code for a user access token and refresh token.
- `refresh_token` — obtain a new user access token without requiring the user to re-authorise.


Managing token expiration 

Access tokens are valid for 12 hours. You can request a new access token whenever it's close to expiring — there is no need to wait for the actual expiration to happen first. Depending on how your application uses the Wise Platform API, requesting a new access token before attempting a series of API calls on behalf of an individual user will avoid issues with expired access tokens.