# Create third party transfer

Partners on the correspondent model use the [Create third party transfer endpoint](/api-reference/third-party-transfer/createthirdpartytransfer), which includes the `originator` object. This endpoint requires an `originator` block representing the **true sender** (your customer) of the funds.

Correspondent partners do not use the standard transfer endpoint, `POST /transfers`, because the correspondent send flow requires originator data which the standard create-transfer operation does not include.

## Requirements

Third party transfer requirements can vary based on the corridor, amount, recipient type, and sender context. The following table describes the required, optional, and conditional fields for the third party transfer request:

| Field  | Required? | Description |
|  --- | --- | --- |
| `targetAccount` | Yes | This is the recipient account ID for the funds to be transferred to. |
| `quote` | Yes | This is the authenticated quote id (UUID). |
| `originalTransferId` | Yes | Your unique transfer id used for idempotency. Retry with the same value to avoid creating duplicate resources. |
| `details` object | Conditional | The object containing conditional details-related fields like `reference` or `transferPurpose`. |
| `details.reference` | No (recommended) | Text the recipient may see in their statement. Length/charset rules vary by corridor. Validate using the [transfer requirements endpoint](/api-reference/transfer/transferrequirementsvalidate). |
| `details.transferPurpose` | Conditional | Enum describing the purpose of the transfer. Required for some corridors. Use the [transfer requirements endpoint](/api-reference/transfer/transferrequirementsvalidate) to determine if it’s required and to retrieve allowed values. |
| Other `details.*` fields | Conditional | Some corridors require extra fields (sometimes nested objects). Always source from [transfer requirements endpoint](/api-reference/transfer/transferrequirementsvalidate). |
| `originator` object | Yes | This object contains the details of the ultimate sender (your customer). See the [Originator object section](#originator-object) for details. |


### Confirm transfer requirements

Transfer requirements can vary based on the corridor, amount, recipient type, and sender context. To avoid transfer delays or rejections, make a request to the [transfer requirements endpoint](/api-reference/transfer/transferrequirementsvalidate) to determine which additional fields are needed and which values are allowed before submitting the create transfer request.

Sample request
```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/transfer-requirements \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "targetAccount": 8692237,
    "quoteUuid": "8fa9be20-ba43-4b15-abbb-9424e1481050",
    "originatorLegalEntityType": "PRIVATE",
    "details": {
      "reference": "Invoice 2026-001",
      "sourceOfFunds": "verification.source.of.funds.salary",
      "transferPurpose": "verification.transfers.purpose.pay.bills"
    }
  }'
```

Sample response
- The response returns a list of requirement fields (with regex, min/max lengths, allowed values).
- Each returned field key maps to a field to include in the `details` object of the create transfer request.
- If any field has `refreshRequirementsOnChange: true`, you must re-call transfer requirements after providing a value to discover additional conditional requirements.

```json 200 application/json
[
  {
    "type": "transfer",
    "fields": [
      {
        "name": "Transfer reference",
        "group": [
          {
            "key": "reference",
            "name": "Transfer reference",
            "type": "text",
            "refreshRequirementsOnChange": false,
            "required": false,
            "displayFormat": null,
            "example": null,
            "minLength": null,
            "maxLength": 10,
            "validationRegexp": "[a-zA-Z0-9- ]*",
            "validationAsync": null,
            "valuesAllowed": null
          }
        ]
      },
      {
        "name": "Transfer purpose",
        "group": [
          {
            "key": "transferPurpose",
            "name": "Transfer purpose",
            "type": "select",
            "refreshRequirementsOnChange": true,
            "required": true,
            "displayFormat": null,
            "example": null,
            "minLength": null,
            "maxLength": null,
            "validationRegexp": null,
            "validationAsync": null,
            "valuesAllowed": [
              {
                "key": "verification.transfers.purpose.purchase.property",
                "name": "Buying property abroad"
              },
              {
                "key": "verification.transfers.purpose.pay.bills",
                "name": "Rent or other property expenses"
              },
              {
                "key": "verification.transfers.purpose.mortgage",
                "name": "Mortgage payment"
              },
              {
                "key": "verification.transfers.purpose.pay.tuition",
                "name": "Tuition fees or studying expenses"
              },
              {
                "key": "verification.transfers.purpose.send.to.family",
                "name": "Sending money home to family"
              },
              {
                "key": "verification.transfers.purpose.living.expenses",
                "name": "General monthly living expenses"
              },
              {
                "key": "verification.transfers.purpose.other",
                "name": "Other"
              }
            ]
          },
          {
            "key": "transferPurposeSubTransferPurpose",
            "name": "Please select a specific reason for your transfer",
            "type": "select",
            "refreshRequirementsOnChange": true,
            "required": true,
            "displayFormat": null,
            "example": null,
            "minLength": null,
            "maxLength": null,
            "validationRegexp": null,
            "validationAsync": null,
            "valuesAllowed": [
              {
                "key": "INTERPRETATION_SERVICE",
                "name": "Interpretation service"
              },
              {
                "key": "TRANSLATION_SERVICE",
                "name": "Translation service"
              },
              {
                "key": "HUMAN_RESOURCE_SERVICE",
                "name": "Human resource service"
              },
              {
                "key": "SOFTWARE_DEVELOPMENT_SERVICE",
                "name": "Software development service"
              }
            ]
          }
        ]
      },
      {
        "name": "Source of funds",
        "group": [
          {
            "key": "sourceOfFunds",
            "name": "Source of funds",
            "type": "select",
            "refreshRequirementsOnChange": true,
            "required": true,
            "displayFormat": null,
            "example": null,
            "minLength": null,
            "maxLength": null,
            "validationRegexp": null,
            "validationAsync": null,
            "valuesAllowed": [
              {
                "key": "verification.source.of.funds.salary",
                "name": "Salary"
              },
              {
                "key": "verification.source.of.funds.investment",
                "name": "Investments (stocks, properties, etc.)"
              },
              {
                "key": "verification.source.of.funds.inheritance",
                "name": "Inheritance"
              },
              {
                "key": "verification.source.of.funds.loan",
                "name": "Loan"
              },
              {
                "key": "verification.source.of.funds.other",
                "name": "Other"
              }
            ]
          }
        ]
      }
    ]
  }
]
```

```json 429 application/json
{}
```


### Originator object

The originator object represents your customer (the ultimate sender). You must use KYC-verified data collected from your customer, including:

| Field  | Description |
|  --- | --- |
| `reference` | The originator customer ID from your system. This allows Wise to identify each originator for compliance purposes.

All transfers sent by the same originator must use the same `originator.reference` value. |
| `legalEntityType` | Either `BUSINESS` or `PRIVATE`.

Note that each value for this field has its own conditionally required fields in the `originator` object. |
| `name` | For `PRIVATE` entity, include either `givenName` or `familyName`.

For `BUSINESS` entity, include `fullName`. |
| `businessRegistrationCode` | Required for `BUSINESS` entities starting 1st July, 2026.

Note that some UK-based partners can be explicitly exempted from this requirement. In such cases, the field must have a `null` value. |
| `businessRegistrationDate` | Required for `BUSINESS` entities on certain corridors.

Use [validate transfer requirements](/api-reference/transfer/transferrequirementsvalidate) to confirm the registration date is required for the specific transfer. |
| `dateOfBirth` | Required for `PRIVATE` entities. |
| `address` | Required for certain currency corridors.

When required, always include `firstLine`, `city`, `postCode`, `countryCode` (and `stateCode` when applicable). Some third-party transfer validations can be strict about address structure. Avoid sending `stateCode` for countries where it’s not applicable, as it may cause validation errors.

Use [validate transfer requirements](/api-reference/transfer/transferrequirementsvalidate) to confirm address is required for the specific transfer. |


## Third party transfer request

**Endpoint**: `POST /profiles/{profileId}/third-party-transfers`

Upon successful creation, the transfer status will be `incoming_payment_waiting`, indicating it is awaiting funding.

### GBP/EUR/USD sample request body

```JSON
{
  "targetAccount": 123456789,
  "quote": "8fa9be20-ba43-4b15-abbb-9424e1481050",
  "originalTransferId": "d781a26a-cc20-440b-89b7-2d41de5df416",
  "details": {
    "reference": "Invoice 22092"
  },
  "originator": {
    "legalEntityType": "PRIVATE",
    "reference": "cust_001234",
    "name": {
      "givenName": "John",
      "middleNames": ["Ryan"],
      "familyName": "Goodspeed"
    },
    "dateOfBirth": "1977-07-01",
    "address": {
      "firstLine": "10025 Alterra Pkwy",
      "city": "Austin",
      "stateCode": "TX",
      "postCode": "78758",
      "countryCode": "US"
    }
  }
}
```

### Corridor-required purpose sample request body

This sample request would apply to corridors like AED / THB / PHP / KRW / INR. First call transfer requirements, then include the returned fields under `details`.

```JSON
{
  "targetAccount": 123456789,
  "quote": "8fa9be20-ba43-4b15-abbb-9424e1481050",
  "originalTransferId": "d781a26a-cc20-440b-89b7-2d41de5df416",
  "details": {
    "reference": "Payment",
    "transferPurpose": "SERVICES"
  },
  "originator": {
    "legalEntityType": "BUSINESS",
    "reference": "biz_98765",
    "name": { "fullName": "Hot Air Balloon Services Ltd" },
    "businessRegistrationCode": "1999212",
    "address": {
      "firstLine": "Aiandi tee 1431",
      "city": "Tallinn",
      "postCode": "12112",
      "countryCode": "EE"
    }
  }
}
```

BRL and INR corridor
BRL “transfer nature” and INR "transfer purpose" are set in the quote request(`paymentMetadata.transferNature` and `paymentNetadata.transferPurpose`, respectively), not in the transfer creation payload.

## Using the response

On success, the transfer is created in a “needs funding” state:

- Typically the status is `incoming_payment_waiting` until funded.
- Store the returned `id` for:
  - [Funding the transfer](/api-reference/transfer/transferfund)
  - Tracking via webhooks
  - Customer support & reconciliation


If you need to retrieve `originalTransferId` and `originator` later, use the [get a third party transfer by ID request](/api-reference/third-party-transfer/getthirdpartytransfer), rather than the standard [get transfer by ID request](/api-reference/transfer/transferget) as the these fields are not present on the standard transfer response.

## Error handling

| HTTP | Code | Cause and resolution |
|  --- | --- | --- |
| 422 | `INVALID_RECIPIENT` | Recipient is missing mandatory corridor data (for example, `address`).


Create a new recipient with required fields. Update quote if needed, and retry transfer creation. |
| 422 | `NotNull` / `null.property.error` | Missing required fields like `targetAccount`, `quote`, or `originalTransferId`.


Fix payload. Retry with same `originalTransferId` if request may have partially succeeded. |
| 422 | purpose validation errors | Invalid or missing `details.transferPurpose` for the route.


Call transfer requirements. Submit a valid Transfer Purpose V2 option. |
| 500 | `internal.server.error` | Server error (can occur for incompatible quote/recipient combinations).


Retry safely using the same `originalTransferId`. If persistent, log `x-trace-id` and escalate. |


## Cancel a transfer

Transfers in the `incoming_payment_waiting` state can be cancelled via the API.

To cancel a transfer, use the [Cancel transfer endpoint](/api-reference/transfer/transfercancel) and include the `transferId` of the transfer to cancel in the path.

**Sample request**:

```shell curl
curl -i -X PUT \
  'https://api.wise.com/2026Q4/transfers/{transferId}/cancel' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

The response returns the cancelled transfer object with the `originator` object. *A successful cancel transfer request cannot be undone*.

If the transfer has moved to another state or is being held, the request will return a **409 Conflict** error with the code `transfer.cancellation.not.allowed`.