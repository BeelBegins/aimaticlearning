# Create third party transfers

Create and manage transfers over API on behalf of your customers, under your own financial license.

To allow for the third party model, correspondent partners must have a sponsor bank or their own license under which they can move funds to Wise.

## Create third party transfer request 

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/third-party-transfers \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "profileId": 123456789,
    "targetAccount": 7839323,
    "quote": "3522e360-356a-4e37-9f99-94a21898d8fa",
    "originalTransferId": "4711",
    "details": {
      "reference": "Ski trip"
    },
    "originator": {
      "legalEntityType": "PRIVATE",
      "accountDetails": "123456789",
      "reference": "CST-2991992",
      "name": {
        "givenName": "John",
        "middleNames": [
          "Ryan"
        ],
        "familyName": "Godspeed",
        "patronymicName": "Fitz"
      },
      "dateOfBirth": "1977-07-01",
      "nationality": "EE",
      "address": {
        "firstLine": "Salu tee 100, Apt 4B",
        "city": "Tallinn",
        "countryCode": "EE",
        "postCode": "12112"
      }
    }
  }'
```

For a complete reference, see the [Create a third party transfer](/api-reference/third-party-transfer/createthirdpartytransfer) endpoint.