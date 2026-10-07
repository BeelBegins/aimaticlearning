# Correspondent partner onboarding

Set up accounts, profiles, and access for a correspondent partner.

This guide provides partners using the Correspondent integration model with the complete account creation and OAuth 2.0 authentication flow. Partners using this model rely on a single account to perform transactions on behalf of all of their users, and as such only need to go through this process once.

By the end of this guide, you will have:

- Created a Wise account with the required business profile, including its authorised representative.
- Authenticated your application to the Wise API using your client credentials.
- Generated user access tokens to make authenticated requests on behalf of your Wise account.


You can create the Wise account either **via the Wise.com interface** or **via API**. Wise then supports two OAuth grant flows for obtaining user tokens—the **authorisation code flow** or the **registration code flow**. Your implementation team will help you decide which path best fits your integration needs. This guide provides instructions for each account setup method with a specific OAuth token grant flow.

| Setup method  | Token grant flow | Best for |
|  --- | --- | --- |
| API | Registration code flow | Fully automated, headless integrations where you programmatically obtain credentials and tokens as well as create profiles. |
| Wise.com interface | Authorisation code flow | Partners who prefer to create their account interactively through the Wise web interface. |


Confirm with your implementation team if you are unsure which setup method and token grant flow to use.

Postman collection: Partner access tokens
## Environments

We provide two environments, production and sandbox, to allow you to develop, test, and deploy your applications. The sandbox environment may be made available prior to an executed partnership agreement, and your onboarding team will issue sandbox-specific credentials to you.

For each environment we offer an endpoint that requires mutual TLS (mTLS) and a separate endpoint for non-mTLS. For most situations we recommend using mutual TLS, which requires some [additional setup](/guides/developer/auth-and-security/mtls).

During development, you’ll follow the setup steps in the sandbox environment with your sandbox credentials. Once ready to move into production, you’ll follow the same steps in the production environment.

| Environment | Base URL | mTLS enabled |
|  --- | --- | --- |
| Sandbox | `https://api.wise-sandbox.com` | `https://api-mtls.wise-sandbox.com` |
| Production | `https://api.wise.com` | `https://api-mtls.transferwise.com` |


## Requirements

The onboarding process requires your client credentials, redirect URI, and multiple pieces of data to complete the profile creation. Be sure to review this section thoroughly to ensure you have the necessary information before you begin.

### Credentials and redirect URI

- Your `client_id` and `client_secret`, accessible via the [Developer Hub](https://wise.com/developer-hub). *If you are currently testing with sandbox credentials, be sure to access the [sandbox Developer Hub](https://wise-sandbox.com/developer-hub) instead*.
- Your **redirect URI**, which is the registered callback URL for the authorisation code flow. For correspondent partners, Wise issues a dummy redirect URI solely for the purpose of providing the authorisation code during the redirect step.


### Profile information

Additionally, you will need *at minimum* the following data points to create the required personal and business profiles:

**Business representative (authorised signatory)**:

- Full legal name (first name, last name)
- Date of birth
- Residential address (state code required for US, CA, BR, and AU addresses)
- Contact email address
- Phone number (with international prefix)


The person your organization designates as the business representative should be someone considered an **authorised signatory**. This could be a director, executive officer, or other senior leader in your organization. Your implementation team can help you determine the appropriate individual. The representative's details are submitted as part of the business profile creation request (see below), rather than as a separate personal profile.

**Business profile**:

- Legal business name
- Business registration number
- Company type (from an [enumerated list](/api-reference/profile/profilebusinesscreatev3))
- Company role of the person creating the profile (`OWNER`, `DIRECTOR`, or `OTHER`)
- Registered business address
- Business industry categories (see [Business Categories](/guides/product/kyc/business-categories))
- Operational address(es)
- Business webpage
- An actively monitored email address for handling Requests for Information (RFIs)


**Business directors and ultimate beneficial owners (UBOs)**:

- Full name, date of birth, and country of residence (ISO3 code) for each director
- Full name, date of birth, country of residence (ISO3 code), address, and ownership percentage for each UBO


If you are uncertain about who to identify as business directors or UBOs, consult with your implementation team for assistance.

Additional information may be required
Depending on type of organization and region, Wise may require additional details and documentation beyond what is listed here. The Wise KYC team will review all details submitted and notify you of any additional requirements, if any.

Your implementation team can also assist with submitting the additional details and documents. See the [Verification and activation](#verification-and-activation) section of this guide for more details.

## Setup methods

Correspondent partners can do their onboarding using one of two methods: Using the Wise API or using the Wise.com interface.

Select your preferred method to view the instructions.

API
When using the API to create the necessary account and related profiles, you use the **registration code flow** to obtain tokens.

The API setup flow consists of the following basic steps:

1. Generate a client credentials token.
2. Create a user account with a registration code.
3. Retrieve user access tokens with the registration code.
4. Create the business profile, including its authorised representative.
5. Add directors and UBOs to the business profile.


Wise reviews the profiles and may request additional verification documents, if necessary.

### Generate a client credentials token

Use the [create an OAuth token endpoint](/api-reference/oauth-token/oauthtokencreate) to generate the token.

The `Content-Type` must be sent as `x-www-form-urlencoded` and `grant_type` set to `client_credentials`.

```shell curl
curl -i -X POST \
  -u '<client_id>:<client_secret>' \
  https://api.wise.com/2026Q4/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d grant_type=client_credentials
```

The `access_token` value in the response is your client credentials token, which is valid for **12 hours**. You’ll use this token in the authorization header of the request to create a user account, as well as other application-level requests like subscribing to webhooks.

**Potential errors**:

| Error | Cause | Resolution |
|  --- | --- | --- |
| `401` `{"error": "invalid_client", "error_description": "..."}` | The client ID or secret is incorrect. | Verify your client ID and secret and try again. |


### Create a user with a registration code

User accounts serve as the primary entity that holds the personal and business profiles that you’ll create in a later step. Use the [create a user with registration code endpoint](/api-reference/user/usercreate) to create a new Wise user account.

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/user/signup/registration_code \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "email": "user@email.com",
    "registrationCode": "a]#Et6(yLW@mq4Ky_+EAjXxpHGq7*&lr",
    "language": "EN"
  }'
```

Required request body fields:

- `email`: Use the dummy email provided by Wise, in the format `<unique-identifier>@partner.wise.com`. Wise uses the email address as the unique identifier for users.
- `registrationCode`: Generate a secure, random string of **at least 32 characters**. This code acts as the single point of access for the Wise account. Wise will not have access to this code.


Keep your registration code secure and encrypted!
Should the need to generate a new refresh token arise, you **must** have the registration code used to create the user resource. Without it, you must contact Wise support to assist with generating a new refresh token, which can result in disruption to your integration.

**Potential user account creation errors**:

| HTTP status | Error code  | Cause and resolution |
|  --- | --- | --- |
| `400` | `NotNull` | The `email` or `registrationCode` field is missing from the request body. Ensure both fields are provided in every request. |
| `400` | `Size` | The registration code is shorter than 32 characters. Generate a registration code that is at least 32 characters long. |
| `409` | `NOT_UNIQUE` | The email address is already associated with an existing account. Use a different email address, or use the authorisation code flow to access the existing account. |
| `422` | `ERROR` | The email address is poorly formatted. Provide a valid email address. |


### Retrieve user tokens with the registration code

The user access token allows your application to make requests to the Wise API on behalf of the user you just created, including the next step of creating personal and business profiles.

Use the [create an OAuth token endpoint](/api-reference/oauth-token/oauthtokencreate) with the `registration_code` grant type to exchange the registration code for the tokens.

```bash
curl -i -X POST \
  -u <client_id>:<client_secret> \
  https://api.wise.com/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d grant_type=registration_code \
  -d client_id=string \
  -d email=user@example.com \
  -d registration_code=string
```

Required data for this request:

- `client_id` and `client_secret`
- `grant_type` will always be `registration_code`
- `email` should be the dummy email provided by Wise
- `registration_code` will be the same registration code value generated for the create user account request.


The response includes:

| Field | Description |
|  --- | --- |
| `access_token` | The user access token, valid for **12 hours** by default. |
| `refresh_token` | A long-lived token, valid for **20 years** by default, used to generate new user access tokens. |


Store the refresh token securely and ensure it is never visible to a human. Using a vault service is generally [good practice](/guides/developer/auth-and-security#security-best-practices) to ensure token security as well as accessibility throughout your systems.

**Potential registration code errors**:

| HTTP status | Error | Cause and resolution |
|  --- | --- | --- |
| `401` | `invalid_grant` or `"Invalid user credentials."` | The registration code is incorrect, or the user has reclaimed the account. Verify the registration code. If the account was reclaimed, contact Wise. |
| `400` | `invalid_request` or `"Missing grant type"` | The `grant_type` parameter is missing from the request body. Include `grant_type=registration_code` in the request. |


### Create the business profile

You can now use the user access token to create the business profile. Currently, all transactions performed via the Wise API are connected to specific profiles.

The business profile and its authorised representative are created together in a single request—there is no need to create a separate personal profile first. Provide the authorised signatory's details in the `businessRepresentative` field of the business profile request, then add directors and UBOs:

| Request | Description |
|  --- | --- |
| [Create business profile](/api-reference/profile/profilebusinesscreatev3) | Use the registered business name when creating the profile. Provide the authorised signatory's details (name, date of birth, address, and contact details) in the `businessRepresentative` field; date of birth and phone number are used for verification only. To reuse a representative already created for another business, pass their `businessRepresentativeId` instead of the full details. You can use the optional `X-idempotence-uuid` header (unique per profile creation) to safely handle retries; if omitted and a matching profile already exists, the request returns a `409`. |
| [Create director](/api-reference/profile/profiledirectorcreate) | Adds a director to the business profile. |
| [Create UBO](/api-reference/profile/profileubocreate) | Adds an ultimate beneficial owner (UBO) to the business profile. For UBOs, if `ownershipPercentage` is not required, pass `null` as the value. |


Make note of the `profileId` for the business profile, as that value is used for all transfer activities.

### Verification and activation

After profiles have been created, Wise reviews the profiles and informs you when the account is fully verified and ready for use.

In some cases, Wise may request additional verification documents. If additional verification is requested, use the [upload evidences endpoint](/api-reference/verification/verificationuploadevidences) to send the requested documentation.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/additional-verification/upload-evidences' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "accountPurpose": "MOVING_SAVINGS",
    "intendedCountries": [
      "deu",
      "esp"
    ],
    "yearlyAnticipatedVolume": "0_2350",
    "mainSourceOfIncome": "SALARY",
    "annualIncome": "0_11500"
  }'
```

Note that the request bodies vary depending on whether the evidence is for a personal or business profile.

**Do not use the account until Wise notifies you that verification is complete.**

Wise.com
When using the [Wise.com interface](https://wise.com/register#/email) to create the necessary account and related profiles, you will use the **authorisation code flow** to obtain API tokens.

The Wise.com interface flow consists of the following basic steps:

1. Register for an account
2. Create personal and business profiles
3. Authorise access to your application via OAuth
4. Capture the authorisation code
5. Exchange the authorisation code for tokens


Wise will review the profiles and may request additional details and related documents, if necessary.

### Register for an account

To register for a Wise account:

1. Go to [Wise.com](https://wise.com/register#/email) and select **Sign up**.
2. Enter an appropriate business email address.
3. Select **Business account** as your account type.
4. Select the country where your business is registered (or where you pay tax if unregistered).
5. Verify the phone number for two-factor authentication (be sure to use an appropriate mobile phone number that can receive 2FA notifications).
6. Create your password.


Make note of the username and password created in this step as they will be needed during the OAuth flow.

Phone number already used
If the phone number entered during account sign up is already used on a personal Wise account, you may be blocked from creating the new account. In this case, contact your Wise implementation team to have the `dup-override` tag applied to the account.

### Create personal and business profiles

Once logged in, set up a personal profile using the details of the person designated as the authorised signatory during your onboarding. Currently, all transactions performed via the Wise API are connected to specific profiles.

Then, create a business profile ensuring that you enter your registered business name and an **actively monitored email address** accessible to your back office team for handling RFIs.

The Wise interface will guide you through providing business details, director information, UBO information, and identity verification.

Access for additional users
You can give other trusted users access to the business profile with specific permissions. Review our [help article about adding team members](https://wise.com/help/articles/2977953/how-do-i-add-or-remove-team-members) for detailed instructions.

### Authorise access to your application via OAuth

After setting up the profiles, grant your application access to the Wise account through a browser-based consent flow.

#### Step 1: Redirect to Wise authorisation page

Paste the Wise authorisation URL into your browser, replacing the `<CLIENT_ID>` and `<REDIRECT_URI>` with the corresponding values:

```
https://wise.com/oauth/authorize?response_type=code&client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>
```

- `client_id` is your application's client ID
- `redirect_uri` is the callback URI Wise provided


Log in using the username and password you created when registering for the account. When prompted, give access to your application.

#### Step 2: Capture the authorization code

After granting access, Wise redirects back to your `redirect_uri` with an authorisation code in the URL query parameter:

```
https://your-redirect-uri.com/callback?code=<AUTHORIZATION_CODE>
```

Your application should capture the `code` parameter from this redirect URL.

#### Step 3: Exchange auth code for tokens

To exchange the authorisation code for a user access token, use the [create an OAuth token endpoint](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `authorization_code`.

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
- `grant_type` is always `authorization_code`
- `code` is the authorization code value from the callback URL
- `redirect_uri` is the Wise-provided redirect URL


The response includes:

| Field | Description |
|  --- | --- |
| `access_token` | The user access token, valid for **12 hours** by default. |
| `refresh_token` | A long-lived token, valid for **20 years** by default, used to generate new user access tokens. |


Store the refresh token securely and ensure it is never visible to a human. Using a vault service is generally [good practice](/guides/developer/auth-and-security#security-best-practices) to ensure token security as well as accessibility throughout your systems.

## Refreshing user access token

Whether you set up via the Wise.com interface or via the API, you must refresh your user access tokens before they expire. User access tokens are valid for **12 hours**. Wise recommends refreshing user access tokens **6 hours** before they expire.

To refresh a user access token, use the [create an OAuth token endpoint](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `refresh_token`.

```bash
curl -X POST https://api.wise.com/oauth/token \
  -u <CLIENT_ID>:<CLIENT_SECRET> \
  -d 'grant_type=refresh_token' \
  -d 'refresh_token=<REFRESH_TOKEN>'
```

The response returns a new `access_token` value and the prior user access token is immediately invalidated.

### Expired, revoked, or lost refresh tokens

If you receive an `invalid_grant` error when attempting to refresh a user access token, you may have an expired or revoked refresh token.

Should your refresh token expire, get revoked, or you otherwise lose access to it, you must use the [create an OAuth token endpoint](/api-reference/oauth-token/oauthtokencreate) with your corresponding grant type (registration code or authorization code) to generate new user access and refresh tokens.

When you do this, the old refresh token is immediately invalidated. If the last user access token generated by that refresh token is not expired, it will remain active until it expires or is replaced.

Review the [OAuth 2.0 setup guide](/guides/developer/auth-and-security/oauth-2-setup) for more details about token management and lifecycles.