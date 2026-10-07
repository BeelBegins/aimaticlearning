# Security and access

OAuth 2.0 and token types for Wise Platform partners 

To use the Wise Platform API, you must authenticate your requests. Authentication verifies your identity and ensures only authorised users and applications can access the API.

The Wise Platform API implements **OAuth 2.0** for all partner accounts. Wise also offers enhanced security frameworks — mTLS, JOSE, and SCA & 2FA — for partners requiring additional protection.

## OAuth 2.0

OAuth 2.0 lets your application access the Wise API on behalf of your customers or as an enterprise integration. It requires a partnership agreement and [mTLS setup](/guides/developer/auth-and-security/mtls).

During the partner onboarding process, Wise provides partner accounts with:

- A **client ID** to identify their application.
- A **client secret** to authenticate their application.
- Access to the [Developer Hub](https://wise.com/developer-hub) for managing credentials and other tasks.


Additionally, partners must provide Wise with a **redirect URL**, which Wise uses during the OAuth flow to redirect users to after authorising the partner application.

### Token types

Wise issues the following types of OAuth 2.0 tokens: client credentials tokens, user access tokens, and refresh tokens.

Each token type is used for specific actions with the Wise API. Select a token type to learn how to generate and use that type of token.

Client credentials tokens 
For application-level requests, including unauthenticated quotes and application webhoooks.

User access tokens
For profile-level requests, including creating recipients, submitting transfers, and tracking statuses.

Refresh tokens
For obtaining new user access tokens without requiring the user to re-authenticate.

Partners on the embedded model
Embedded solutions partners no longer use user access tokens to make requests, as this model has changed to no longer rely on user objects. Partners on this integration model should instead use [client credentials tokens](/guides/developer/auth-and-security/client-credentials-token) for all authenticated requests.

If you are uncertain which token to use for your integration, contact your integration team to confirm.

### Security best practices

- Never expose client credentials or tokens in client-side code, logs, or URLs.
- Store credentials and tokens in a secrets manager.
- Use separate credentials for sandbox and production.
- Encrypt refresh tokens at rest.
- Rotate your client secret periodically via Developer Hub.
- Request only the scopes your application needs.


If you suspect a breach, revoke credentials immediately via Developer Hub and contact your implementation manager.

## Enhanced security methods 

Wise offers advanced security for partners requiring additional protection. Select a method to learn how to implement it with your partner integration.

mTLS 
Learn how to set up mTLS to support stronger security in API calls and webhooks.

JOSE
Implement signing or encryption keys (or both) for tamper-proof, confidential API calls.

SCA & 2FA
Learn how to configure strong customer authentication and two-factor authentication.

## About personal API tokens

In addition to partner accounts, a sub-set of Wise Platform API capabilities are available to individual Wise business accounts. These are typically used by small-to-medium businesses (SMBs) that want to automate parts of their payouts workflow.

These accounts can generate a **personal API token** that they can then use in the `authorization` header of their API requests when calling the supported endpoints. Review the [Personal API token guide](/guides/developer/auth-and-security/personal-api-token) for details about generating and using a personal API token.

Which type should you use?
Personal API tokens should be used by SMBs that wish to automate their own Wise.com business accounts. OAuth 2.0 should be used by large enterprise partners and partners building applications for their customers to perform financial transactions.