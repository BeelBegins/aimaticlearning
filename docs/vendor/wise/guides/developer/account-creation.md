# Setting up a Wise Account

## Onboarding via API

The API is a more secure method we recommend. Creating accounts via the web introduces potential risks, such as individual access to move funds, which is better mitigated through the API.

### Client Credentials

Please ensure you have your client key and secret for both sandbox and production environments. These credentials will be provided separately.

We strongly recommend or advise that this information is stored securely, for example in a credentials vault.

### API Process

1. **Create Client Credentials Token**
Use the API to generate this token, which is essential for authentication. See [Create an OAuth token](/api-reference/oauth-token/oauthtokencreate).
2. **New User Account**
Create a new user account with a Wise dummy email (e.g. `<unique-identifier>@customer.wise.com`) and a registration code.
  - It is crucial that this information is stored securely and not visible to members of the team.
  - This registration code will act as a single point of access/password for the Wise Account.
  - Wise will not be privy to this unique code, and hence only you can get subsequent tokens using this code.
See [Create a user with a registration code](/api-reference/user/usercreate).
3. **Refresh Token**
Collect this via the registration code authentication route and ensure it's securely stored.
See [Retrieve user tokens with registration code](/api-reference/oauth-token/oauthtokencreate).
4. **Generate User Access Tokens from Refresh Token**
Access tokens are valid for 12 hours, so upon expiry you need to use the refresh token to generate a new access token.
See [Retrieve user tokens with refresh token](/api-reference/oauth-token/oauthtokencreate).
5. **Create a business profile**
The name on this account should match your bank account name. The business profile and its authorised representative are created together in a single request—there is no need to create a separate personal profile first. Provide the authorised signatory's details in the `businessRepresentative` field, or pass a `businessRepresentativeId` to reuse a representative already created for another business.
Provide necessary details such as:
  - `businessName`: The name of the business.
  - `businessFreeFormDescription`: A description of the business.
    - Required if `companyType` is `"OTHER"`.
    - For other company types, it is highly recommended to provide this to avoid payment issues.
  - `registrationNumber`: The business registration number.
  - `companyType`: The legal form of the company. Allowed values include:
    - `LIMITED`
    - `PARTNERSHIP`
    - `SOLE_TRADER`
    - `LIMITED_BY_GUARANTEE`
    - `LIMITED_LIABILITY_COMPANY`
    - `FOR_PROFIT_CORPORATION`
    - `NON_PROFIT_CORPORATION`
    - `LIMITED_PARTNERSHIP`
    - `LIMITED_LIABILITY_PARTNERSHIP`
    - `GENERAL_PARTNERSHIP`
    - `SOLE_PROPRIETORSHIP`
    - `PRIVATE_LIMITED_COMPANY`
    - `PUBLIC_LIMITED_COMPANY`
    - `TRUST`
    - `OTHER`
  - `companyRole`: The role of the person creating the profile. Allowed values are `OWNER`, `DIRECTOR`, and `OTHER`.
  - `address`: The business address, including:
    - `addressFirstLine`
    - `city`
    - `countryIso2Code` (2-letter country code)
    - `countryIso3Code` (3-letter country code, must be lowercase)
    - `postCode`
    - `stateCode` (if applicable)
  - `actorEmail`: The email of the person creating the profile.
  - `industryCategories`: One or more categories classifying the business. See [Business Categories](/guides/product/kyc/business-categories) for the full list of valid values.
  - `operationalAddresses`: A list of operational addresses, each including:
    - `addressFirstLine`
    - `city`
    - `countryIso2Code`
    - `countryIso3Code`
    - `postCode`
    - `stateCode` (if applicable)
  - `webpage`: The business webpage.
    - Required if `companyType` is `"OTHER"`.
    - For other company types, it is highly recommended to provide this to avoid payment issues.
  - `businessRepresentative`: The authorised signatory for the business (a director, executive officer, or other senior leader). Provide either the full representative details or a `businessRepresentativeId` to reuse an existing representative. Full details include:
    - `firstName` and `lastName`
    - `preferredName` (optional)
    - `dateOfBirth` (format `yyyy-mm-dd`)
    - `address` (including `stateCode` for US, CA, BR, and AU addresses)
    - `contactDetails`: `email` and `phoneNumber` (in international phone number format)
See the [Create a business profile](/api-reference/profile/profilebusinesscreatev3) endpoint for the full schema.
6. **Create a Business Director**
Use the Create Director endpoint to add directors to your business profile.
Make sure to provide all necessary information:
  - **First Name:** The first name of the director.
  - **Last Name:** The last name of the director.
  - **Date of Birth:** The director's date of birth in the format `yyyy-mm-dd`.
  - **Country of Residence ISO3 Code:** The 3-character ISO country code representing the director's country of residence.
See [Create a business director for a profile](/api-reference/profile/profiledirectorcreate).
7. **Create a Business Ultimate Owner (UBO)**
Use the Create UBO endpoint to add ultimate beneficial owners to your business profile.
Submit the necessary information for each UBO:
  - **Name:** The full name of the owner.
  - **Date of Birth:** The date of birth in the format `yyyy-mm-dd`.
  - **Country of Residence ISO3 Code:** The 3-character ISO country code representing the UBO’s country of residence.
  - **Address First Line:** The first line of the address.
  - **Post Code:** The postal code of the address.
  - **Ownership Percentage:** The percentage of ownership.
    - Note that in some cases, this may not be required, and `null` should be passed as the value.
See [Create a business ultimate owner for a profile](/api-reference/profile/profileubocreate).
8. **Verification and Activation**
Wise will review the newly created profiles and gather any additional verification if needed.
See [Upload Evidences](/api-reference/verification#upload-evidences).


## Onboarding via UI on Wise.com

1. **Register for an Account**
Visit the portal address and choose to sign up. Fill in the necessary information to create an account. Be sure to remember your credentials for future logins.
2. **Create a Personal Profile**
Once logged in, ensure that you set up a personal profile on your account.
3. **Create a Business Profile**
Please ensure that the name on this account matches the name of your bank account.
Use an actively monitored email address accessible to your back office team for efficiently handling any Requests for Information (RFIs).
4. **Authorise Access to Your Application via OAuth**
After setting up the profiles, you will be prompted to authorise your application to access your Wise profiles. See [Linking an existing account](/guides/product/kyc/wise-kyc/redirect-to-wise/user-onboarding#link-account).
5. **Redirect Back to Your Application**
After you grant access, Wise will redirect you back to your application. This redirection includes an authorisation code in the URL.
6. **Exchange Authorisation Code for API Tokens**
Your application should capture the authorisation code from the redirect URL and use it to obtain access and refresh tokens via the Wise API. These tokens are necessary for making authenticated API requests on behalf of the user.