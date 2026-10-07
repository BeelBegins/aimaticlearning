# Create customer profiles

To start onboarding a customer, you first need to create a profile for them. The customer's profile ID is the primary identifier for most transactions your customers will perform.

## Retrieve client credentials token

Client credential tokens are required to create profiles. Send a [Create OAuth token request](/api-reference/oauth-token/oauthtokencreate) with `grant_type` set to `client_credentials`.

```shell curl
curl -i -X POST \
  -u '<client_id>:<client_secret>' \
  https://api.wise.com/2026Q4/oauth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d grant_type=client_credentials
```

The `access_token` value is your bearer token for the create profile requests.

## Create a personal profile

For customers that are individual natural persons, rather than business entities, send a [create personal profile request](/api-reference/profile/profilepersonalcreate).

Sample request
```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/personal-profile \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -H 'X-idempotence-uuid: 497f6eca-6276-4993-bfeb-53cbbbba6f08' \
  -d '{
    "firstName": "Oliver",
    "lastName": "Wilson",
    "preferredName": "Olivia",
    "firstNameInKana": null,
    "lastNameInKana": null,
    "address": {
      "addressFirstLine": "50 Sunflower Ave",
      "city": "Phoenix",
      "countryIso3Code": "usa",
      "postCode": "10025",
      "stateCode": "AZ"
    },
    "nationality": "usa",
    "dateOfBirth": "1977-07-01",
    "externalCustomerId": "12345-oliver-wilson",
    "contactDetails": {
      "email": "o.wilson@example.com",
      "phoneNumber": "+3725064992"
    },
    "occupations": [
      {
        "code": "Software Engineer",
        "format": "FREE_FORM"
      }
    ]
  }'
```

Sample response
```json 200 application/json
{
  "id": 30000001,
  "type": "PERSONAL",
  "details": {
    "firstName": "Oliver",
    "lastName": "Wilson",
    "preferredName": "Olivia",
    "firstNameInKana": null,
    "lastNameInKana": null,
    "address": {
      "addressFirstLine": "50 Sunflower Ave",
      "city": "Phoenix",
      "countryIso3Code": "usa",
      "postCode": "10025",
      "stateCode": "AZ"
    },
    "nationality": "usa",
    "dateOfBirth": "1977-07-01",
    "externalCustomerId": "12345-oliver-wilson",
    "contactDetails": {
      "email": "o.wilson@example.com",
      "phoneNumber": "+3725064992"
    },
    "occupations": [
      {
        "code": "Software Engineer",
        "format": "FREE_FORM"
      }
    ],
    "localizedInformation": [
      {}
    ]
  }
}
```

```json 429 application/json
{}
```

## Create a business profile

For customers that are business entities, rather than individual natural persons, send a [create business profile request](/api-reference/profile/profilebusinesscreatev3).

Sample request
The business profile and its authorised representative are created together in a single request. Provide the authorised signatory's details (name, date of birth, address, and contact details) in the `businessRepresentative` object, or pass a `businessRepresentativeId` to reuse a representative already created for another business.

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

If necessary, you can add business directors and ultimate business owners (UBOs) to the business profile.

### Add business directors

Send a [Create business director request](/api-reference/profile/profiledirectorcreate).

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

### Add UBO

Send a [Create ultimate business owner request](/api-reference/profile/profileubocreate).

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

## Notable fields

Some fields in the profile creation request bodies are worth noting:

* Personal profile `contactDetails` fields (including those for business representative profiles) are mandatory. We require this information for KYC and other mandatory contact scenarios. *We do not use these details for marketing*.
* The `externalCustomerId` is optional but is recommended so we can offer ways to look up profiles for a customer in the future.