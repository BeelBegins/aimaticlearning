# Updating profiles

As part of our compliance processes, we require annual updates of the details stored in personal and business profiles.

If any customer details have changed (such as address, surname due to marriage, etc) then the profile information at Wise must be updated.

To perform a profile update, you must first open a profile "update window", make the update profile request(s), and then close the profile "update window". This process informs Wise that a profile update is underway and then has been completed.

If the customer details remain the same, you **must still open and close an update window** to inform us that nothing has changed.

## Recommended strategy

A common strategy is to collect and send this data when a customer next interacts with the Wise integration in your product.

We recommend recording the most recent date each personal/business profile was last updated. Use this date to check whether it's been more than one year since the profile was last updated. If it has been over a year, you must perform a profile update using the steps described below.

## No updates required for profile

We require the update window to be opened and closed even if there were *no changes* to the profiles. This will let us know that nothing has changed for the profile and that the information is up to date.

If no changes to the profile are required:

1. [Open the update window](/api-reference/profile/profileupdatewindowopen).
2. [Close the update window](/api-reference/profile/profileupdatewindowclose).


Open update window request
```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/update-window' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Close update window request
```shell curl
curl -i -X DELETE \
  'https://api.wise.com/2026Q4/profiles/{profileId}/update-window' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

## Update a personal profile

To update a personal profile:

1. [Open the update window](/api-reference/profile/profileupdatewindowopen).
2. Send an [update personal profile request](/api-reference/profile/profilepersonalupdate) with the updated properties in the request body.
3. [Close the update window](/api-reference/profile/profileupdatewindowclose).


## Update a business profile

Business profiles may require general data updates (business name, address, category, etc), director updates, or UBO updates.

1. [Open the update window](/api-reference/profile/profileupdatewindowopen).
2. Submit an [update business profile request](/api-reference/profile/profilebusinessupdate) to update general business data.
3. If director data changed, submit an [update business directors request](/api-reference/profile/profiledirectorupdate) to update director data.
4. If UBO data changed, submit an [update business UBO request](/api-reference/profile/profileuboupdate) to update ultimate beneficial owner data.
5. [Close the update window](/api-reference/profile/profileupdatewindowclose).


## Sample update requests

For the personal and business profile `PUT` requests, you only need to include the properties to update. Omitted fields preserve their values.

The director and UBO `PUT` requests replace the full collection, so include every director or UBO and all of the properties needed for each entry.

When updating an object (like an address), provide the complete nested object to ensure it passes validation.

Update personal profile
```shell curl
curl -i -X PUT \
  'https://api.wise.com/2026Q4/profiles/{profileId}/personal-profile' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
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
    "contactDetails": {
      "email": "o.wilson@example.com",
      "phoneNumber": "+3725064992"
    },
    "externalCustomerId": "12345-oliver-wilson",
    "occupations": [
      {
        "code": "Software Engineer",
        "format": "FREE_FORM"
      }
    ]
  }'
```

Update business profile
```shell curl
curl -i -X PUT \
  'https://api.wise.com/2026Q4/profiles/{profileId}/business-profile' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "id": 14599371,
    "businessName": "ABC Logistics Ltd",
    "businessNameInKatakana": null,
    "businessFreeFormDescription": "Biz free form desc",
    "registrationNumber": "12144939",
    "acn": null,
    "abn": null,
    "arbn": null,
    "companyType": "LIMITED",
    "address": {
      "addressFirstLine": "1 A road",
      "city": "London",
      "countryIso2Code": "gb",
      "countryIso3Code": "gbr",
      "postCode": "11111",
      "stateCode": "strin"
    },
    "companyRole": "OWNER",
    "contactDetails": {
      "email": "contact@innovate-solutions.co.uk",
      "phoneNumber": "+441617891234"
    },
    "externalCustomerId": "67890-biz-acct",
    "industryCategories": [
      "SOFTWARE_DEVELOPMENT_PUBLISHING",
      "IT_CONSULTANCY_TECHNICAL_SUPPORT_SERVICES"
    ],
    "firstLevelCategory": "CONSULTING_IT_BUSINESS_SERVICES",
    "secondLevelCategory": "DESIGN",
    "operationalAddresses": [
      {
        "addressFirstLine": "1 A road",
        "city": "London",
        "countryIso2Code": "gb",
        "countryIso3Code": "gbr",
        "postCode": "11111",
        "stateCode": "strin"
      }
    ],
    "webpage": "https://abc-logistics.com"
  }'
```

Update business director
```shell curl
curl -i -X PUT \
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

Update business UBO
```shell curl
curl -i -X PUT \
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