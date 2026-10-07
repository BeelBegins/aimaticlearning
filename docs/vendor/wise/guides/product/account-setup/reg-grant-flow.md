# Registration code grant flow

Securely create an account and profiles via API

When using the API to create an account and its related profiles, you perform the following basic steps:

1. Generate a client credentials token.
2. Create a user account with a registration code.
3. Retrieve user access tokens with the registration code.
4. Create the business profile.
5. Add directors and UBOs to the business profile.


Wise reviews the profiles and may request additional verification documents, if necessary.

## Step 1: Generate client credentials token

Send a [create OAuth token request](/api-reference/oauth-token/oauthtokencreate) to generate the client credentials token.

The `Content-Type` must be sent as `x-www-form-urlencoded` and `grant_type` set to `client_credentials`.

```shell curl
curl -i -X POST \
  -u '<client_id>:<client_secret>' \
  https://api.wise.com/2026Q4/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d grant_type=client_credentials
```

The `access_token` value in the response is your client credentials token, which is valid for **12 hours**. You’ll use this token in the authorization header of the create user account request, as well as other application-level requests like subscribing to webhooks.

### Potential client credential errors

| Error | Cause | Resolution |
|  --- | --- | --- |
| `401` `{"error": "invalid_client", "error_description": "..."}` | The client ID or secret is incorrect. | Verify your client ID and secret and try again. |


## Step 2: Create user with registration code

User accounts serve as the primary entity that holds the profile created in a later step. Send a [create user with registration code request](/api-reference/user/usercreate) to create a new Wise user resource.

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

**Required request body fields**:

| Field  | Description |
|  --- | --- |
| `email` | The email address of the user (acts as the unique identifier for a user resource).

Correspondent partners use the dummy email Wise provides, in the format `<unique-identifier>@partner.wise.com`. |
| `registrationCode` | Generate a secure, random string of **at least 32 characters**. This code acts as the single point of access for the Wise account. Wise does not have access to this code. |


Keep your registration code secure and encrypted!
Should the need to generate a new refresh token arise, you **must** have the registration code used to create the user resource. Without it, you must contact Wise support to assist with generating a new refresh token, which can result in disruption to your integration.

### Potential user account creation errors

| HTTP status | Error code  | Cause and resolution |
|  --- | --- | --- |
| `400` | `NotNull` | The `email` or `registrationCode` field is missing from the request body. Ensure both fields are provided in every request. |
| `400` | `Size` | The registration code is shorter than 32 characters. Generate a registration code that is at least 32 characters long. |
| `409` | `NOT_UNIQUE` | The email address is already associated with an existing account. Use a different email address, or use the authorisation code flow to access the existing account. |
| `422` | `ERROR` | The email address is poorly formatted. Provide a valid email address. |


## Step 3: Retrieve user tokens

The user access token allows your application to make requests to the Wise Platform API on behalf of the user you just created, including the next step of creating a profile.

Send a [create OAuth token request](/api-reference/oauth-token/oauthtokencreate) with the `registration_code` grant type to exchange the registration code for the tokens.

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
- `grant_type` is always `registration_code`
- `email`
- `registration_code` is the same registration code value generated for the create user account request.


**The response includes**:

| Field | Description |
|  --- | --- |
| `access_token` | The user access token, valid for **12 hours** by default. |
| `refresh_token` | A long-lived token, valid for **20 years** by default, used to generate new user access tokens. |


Store the refresh token securely and ensure it is never visible to a human. Using a vault service is generally [good practice](/guides/developer/auth-and-security#security-best-practices) to ensure token security as well as accessibility throughout your systems.

You can now use the user access token to create a business profile.

### Potential registration code errors

| HTTP status | Error | Cause and resolution |
|  --- | --- | --- |
| `401` | `invalid_grant` or `"Invalid user credentials."` | The registration code is incorrect, or the user has reclaimed the account. Verify the registration code. If the account was reclaimed, contact Wise. |
| `400` | `invalid_request` or `"Missing grant type"` | The `grant_type` parameter is missing from the request body. Include `grant_type=registration_code` in the request. |


## Step 4: Create business profile

The business profile and its authorised representative are created together in a single request, so there is no need to create a separate personal profile first. Once you create the business profile, you must then add at least one director and ultimate beneficial owner (UBO) to it.

### Create business profile request

Send the [Create business profile request](/api-reference/profile/profilebusinesscreatev3) with the required properties.

Sample request
**Guidance**:

- Use the registered business name when creating the profile.
- Provide the authorised signatory's details (name, date of birth, address, and contact details) in the `businessRepresentative` object.
- Date of birth and phone number are used for verification only.
- To reuse a representative already created for another business, pass their `businessRepresentativeId` instead of the full details.
- You can use the optional `X-idempotence-uuid` header (unique per profile creation) to safely handle retries. If omitted and a matching profile already exists, the request returns a `409`.


```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/business-profile \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -H 'X-idempotence-uuid: 497f6eca-6276-4993-bfeb-53cbbbba6f08' \
  -d '{
    "businessName": "ABC Logistics Ltd",
    "businessNameInKatakana": null,
    "businessFreeFormDescription": "Biz free form desc",
    "registrationNumber": "12144939",
    "acn": null,
    "abn": null,
    "arbn": null,
    "companyType": "LIMITED",
    "companyRole": "OWNER",
    "address": {
      "addressFirstLine": "1 A road",
      "city": "London",
      "countryIso2Code": "gb",
      "countryIso3Code": "gbr",
      "postCode": "11111"
    },
    "contactDetails": {
      "email": "contact@innovate-solutions.co.uk",
      "phoneNumber": "+441617891234"
    },
    "externalCustomerId": "67890-biz-acct",
    "actorEmail": "biz-acct@abcl.com",
    "industryCategories": [
      "SOFTWARE_DEVELOPMENT_PUBLISHING",
      "IT_CONSULTANCY_TECHNICAL_SUPPORT_SERVICES"
    ],
    "operationalAddresses": [
      {
        "addressFirstLine": "1 A road",
        "city": "London",
        "countryIso2Code": "gb",
        "countryIso3Code": "gbr",
        "postCode": "11111"
      }
    ],
    "webpage": "https://abc-logistics.com",
    "businessRepresentative": {
      "firstName": "Oliver",
      "lastName": "Wilson",
      "preferredName": "Olivia",
      "address": {
        "addressFirstLine": "50 Sunflower Ave",
        "city": "Phoenix",
        "countryIso3Code": "usa",
        "postCode": "10025",
        "stateCode": "AZ"
      },
      "dateOfBirth": "1977-07-01",
      "contactDetails": {
        "email": "o.wilson@example.com",
        "phoneNumber": "+3725064992"
      }
    }
  }'
```

Sample response
Use the `id` value from the response as the `{profileId}` value in future requests, including transfer activities.

```json 200 application/json
{
  "type": "BUSINESS",
  "id": 14599371,
  "publicId": "f0e9d8c7-b6a5-4321-fedc-ba9876543210",
  "userId": 9889627,
  "address": {
    "id": 36086782,
    "addressFirstLine": "24 Willow Creek Lane",
    "city": "Bristol",
    "countryIso2Code": "GB",
    "countryIso3Code": "gbr",
    "postCode": "BS1 6AE",
    "stateCode": null
  },
  "email": "info@innovate-solutions.co.uk",
  "createdAt": "2024-03-10T09:00:00",
  "updatedAt": "2025-06-18T14:22:00",
  "currentState": "VISIBLE",
  "contactDetails": {
    "email": "contact@innovate-solutions.co.uk",
    "phoneNumber": "+441617891234"
  },
  "businessName": "Innovate Solutions Ltd",
  "registrationNumber": "SC1234567890ABCD",
  "descriptionOfBusiness": "IT_DEVELOPMENT",
  "webpage": "https://www.innovate-solutions.co.uk",
  "companyType": "LIMITED_COMPANY",
  "companyRole": "OWNER",
  "businessFreeFormDescription": "We create cutting-edge software for businesses.",
  "firstLevelCategory": "CONSULTING_IT_BUSINESS_SERVICES",
  "secondLevelCategory": "IT_DEVELOPMENT",
  "industryCategories": [
    "SOFTWARE_DEVELOPMENT_PUBLISHING",
    "IT_CONSULTANCY_TECHNICAL_SUPPORT_SERVICES"
  ],
  "operationalAddresses": [
    {
      "id": 36086782,
      "addressFirstLine": "24 Willow Creek Lane",
      "city": "Bristol",
      "countryIso2Code": "GB",
      "countryIso3Code": "gbr",
      "postCode": "BS1 6AE",
      "stateCode": null
    }
  ],
  "fullName": "Innovate Solutions Ltd"
}
```

```json 429 application/json
{}
```

### Add a director

Send a [Create director request](/api-reference/profile/profiledirectorcreate) to add at least one director to the business profile.

Sample request
```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/directors' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '[
    {
      "firstName": "John",
      "lastName": "Doe",
      "dateOfBirth": "1982-05-20",
      "countryOfResidenceIso3Code": "usa"
    },
    {
      "firstName": "Jane",
      "lastName": "Doe",
      "dateOfBirth": "1981-12-07",
      "countryOfResidenceIso3Code": "usa"
    }
  ]'
```

Sample response
```json 200 application/json
[
  {
    "id": 10,
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1982-05-20",
    "countryOfResidenceIso3Code": "usa"
  },
  {
    "id": 11,
    "firstName": "Jane",
    "lastName": "Doe",
    "dateOfBirth": "1981-12-07",
    "countryOfResidenceIso3Code": "usa"
  }
]
```

```json 429 application/json
{}
```

### Add a UBO

Send a [Create UBO request](/api-reference/profile/profileubocreate) to add at least one ultimate beneficial owner (UBO) to the business profile.

Sample request
All the shareholders that have at least 25% ownership should be submitted via this request. If `ownershipPercentage` is not required, pass `null` as the value.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/ubos' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '[
    {
      "name": "John Doe",
      "dateOfBirth": "1982-05-20",
      "countryOfResidenceIso3Code": "usa",
      "addressFirstLine": "123 Fake St",
      "postCode": "FK 12345",
      "documentType": "PASSPORT",
      "documentId": "AA299822313",
      "documentCountryIso3Code": "usa",
      "nationality": "usa",
      "email": "john.doe@example.com",
      "placeOfBirthCity": "London",
      "placeOfBirthCountryIso3Code": "gbr",
      "city": "Phoenix",
      "state": "AZ",
      "ownershipPercentage": 30
    },
    {
      "name": "Jane Doe",
      "dateOfBirth": "1981-12-07",
      "countryOfResidenceIso3Code": "usa",
      "addressFirstLine": "125 Fake St",
      "postCode": "FK 12545",
      "documentType": "DRIVING_LICENSE",
      "documentId": "DL12345",
      "documentCountryIso3Code": "usa",
      "nationality": "usa",
      "email": "jane.doe@example.com",
      "placeOfBirthCity": "London",
      "placeOfBirthCountryIso3Code": "gbr",
      "city": "Phoenix",
      "state": "AZ",
      "ownershipPercentage": 70
    }
  ]'
```

Sample response
```json 201 application/json
[
  {
    "id": "013ab1c2688d0185b582ee7e0bcb28b2",
    "name": "John Doe",
    "dateOfBirth": "1982-05-20",
    "countryOfResidenceIso3Code": "usa",
    "addressFirstLine": "123 Fake St",
    "postCode": "FK 12345",
    "city": "Phoenix",
    "state": "AZ",
    "ownershipPercentage": 30
  },
  {
    "id": "912ce3f31c8b3a10572137e78417caa3",
    "name": "Jane Doe",
    "dateOfBirth": "1981-12-07",
    "countryOfResidenceIso3Code": "usa",
    "addressFirstLine": "125 Fake St",
    "postCode": "FK 12545",
    "city": "Phoenix",
    "state": "AZ",
    "ownershipPercentage": 70
  }
]
```

```json 429 application/json
{}
```

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