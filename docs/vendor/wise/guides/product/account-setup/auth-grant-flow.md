# Authorisation code grant flow

Create an account and profiles with the Wise.com interface

When using the [Wise.com interface](https://wise.com/register#/email) to create an account and related profiles, you perform the following basic steps:

1. Register for an account.
2. Create personal and business profiles.
3. Authorise access to your application via OAuth.
4. Capture the authorisation code.
5. Exchange the authorisation code for tokens.


Wise reviews the profiles and may request additional details and related documents, if necessary.

## Step 1: Register for an account

To register for a Wise account:

1. Go to [Wise.com](https://wise.com/register#/email) and select **Sign up**.
2. Enter an appropriate business email address.
3. Select **Business account** as your account type.
4. Select the country where your business is registered (or where you pay taxes, if unregistered).
5. Verify the phone number for two-factor authentication (be sure to use an appropriate mobile phone number that can receive 2FA notifications).
6. Create your password.


Make note of the username and password created in this step. You will need them during the OAuth flow.

Phone number already used
If the phone number entered during account signup is already used on a personal Wise account, you may be blocked from creating the new account. In this case, contact your Wise implementation team to have the `dup-override` tag applied to the account.

## Step 2: Create personal and business profiles

Once logged in, set up a personal profile using the details of the person designated as the authorised signatory during your onboarding.

Then, create a business profile. Ensure you enter your registered business name and an **actively monitored email address** accessible to your back office team for handling RFIs.

The Wise interface will guide you through providing business details, director information, UBO information, and identity verification.

Access for additional users
You can give other trusted users access to the business profile with specific permissions. Review our [help article about adding team members](https://wise.com/help/articles/2977953/how-do-i-add-or-remove-team-members) for detailed instructions.

## Step 3: Authorise access to your application via OAuth

After setting up the profiles, grant your application access to the Wise account through a browser-based consent flow.

### Redirect to Wise authorisation page

Paste the Wise authorisation URL into your browser, replacing the `<CLIENT_ID>` and `<REDIRECT_URI>` with the corresponding values:

```
https://wise.com/oauth/authorize?response_type=code&client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>
```

- `<CLIENT_ID>` is your application's client ID.
- `<REDIRECT_URI>` is the callback URI Wise provided.


Log in using the username and password you created when registering for the account. When prompted, grant access to your application.

## Step 4: Capture authorization code

After granting access, Wise redirects back to your `redirect_uri` with an authorisation code in the URL's `code` query parameter:

```
https://your-redirect-uri.com/callback?code=<AUTHORIZATION_CODE>
```

Your application should capture the `code` parameter from this redirect URL.

Sandbox testing behaviour
Note that when testing this flow in the sandbox, upon redirect you'll see a **site can't be reached** page. *This is expected behavior*. The authorization code, however, is available in the URL.

## Step 5: Exchange auth code for tokens

To exchange the authorisation code for a user access token, send a [create OAuth token request](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `authorization_code`.

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

## Verification and activation

Wise reviews the profiles and informs you when the account is fully verified and ready for use.

In some cases, Wise may request additional verification documents for enhanced due diligence (EDD). If additional verification is requested, use the [upload evidences endpoint](/api-reference/verification/verificationuploadevidences) to send the requested data, and use the [upload documentation endpoint](/api-reference/verification/verificationuploaddocument) to send related documentation.

**Do not use the account until Wise notifies you that verification is complete.**

Evidences example
Note that the request bodies vary depending on whether the evidence is for a personal or business profile.

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

Documents example
```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/verification-status/upload-document' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: multipart/form-data' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -F files=@/Users/test/file.png \
  -F documentType=SOURCE_OF_WEALTH
```