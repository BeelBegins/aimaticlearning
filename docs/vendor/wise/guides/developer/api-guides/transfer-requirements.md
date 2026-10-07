# Transfer Requirements

Transfer requirements vary by currency route, transfer amount, and regulatory region. Use the transfer requirements endpoint to dynamically discover which fields are needed before creating a transfer. You can use this to build a dynamic UI that adapts to each transfer's specific needs.

Transfer requirements can change at any time. It is important to use this API to fetch requirements dynamically and avoid hardcoding them.

## How it works

### Step 1: Get initial requirements

Prepare the request body you would use to [create a transfer](/api-reference/standard-transfer/transfercreate), then post it to the [transfer requirements](/api-reference/transfer/transferrequirementsvalidate) endpoint to discover any additional required fields.

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

### Step 2: Check for dynamic fields

Analyze the returned list of fields. The example response includes `reference`, `sourceOfFunds` and `transferPurpose` fields. The `reference` field is optional in this example. The `sourceOfFunds` and `transferPurpose` fields are required and both have `refreshRequirementsOnChange: true`, which indicates that additional fields may become required depending on the selected value.

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

### Step 3: Refresh with selected values

POST to the endpoint again with values set for all fields that have `refreshRequirementsOnChange: true`. For example, selecting a `sourceOfFunds` value of `verification.source.of.funds.other` may require an additional `sourceOfFundsOther` text field.

### Step 4: Repeat until complete

Continue calling POST with updated values whenever a field with `refreshRequirementsOnChange: true` changes. Once all dynamic fields are resolved, you have the complete set of fields to compose a valid request to create a transfer.

## Common requirement fields

As transfer requirements are part of a dynamic form, the list of options can change. The fields below are the most common requirements and when they apply, but others may be included. Always design your integration to work dynamically with this endpoint.

- **Transfer Reference** (`reference`) — General reference or memo field. Mandatory for some transfers (`required` will be true). Use `minLength`, `maxLength` and `validationRegexp` in your interface to minimize errors.
- **Originator Legal Entity Type** (`originatorLegalEntityType`) — Feature flag to identify the type of sender. Allowed values are `PRIVATE` or `BUSINESS`. Note this field is **required** from March 2026 for all new and existing Correspondent Send integrations.
- **Transfer Purpose** (`transferPurpose`) — A select list of values to help understand the purpose of the transfer. Often required when transfers are over a certain size or through a particular route. As an option is selected, you must refresh requirements, as additional fields could become required.
- **Sub Transfer Purpose** (`transferPurposeSubTransferPurpose`) — A secondary select list of values to further help understand the purpose of the transfer.
- **Source of Funds** (`sourceOfFunds`) — A select list of values to help understand the source of the funds.
- **Transfer Nature** (`transferNature`) — A select list of values to help understand the reason for the transfer, only for routes to and from BRL. Note that transfer nature needs to be added to a quote through creation or update in order to correctly calculate the IOF tax.
- **Transfer Purpose Invoice Number** (`transferPurposeInvoiceNumber`) — Mandatory for trade related transfers (`required` will be true for these cases). Use `minLength`, `maxLength` and `validationRegexp` in your interface to minimize errors.


The `originatorLegalEntityType` field is currently optional, but will become **required** from March 2026 for all new and existing **Correspondent Send Integrations**. Please update your integration to include this field as soon as possible.

Transfers to-BRL or from-BRL require a transfer nature (see: `transferNature`). Transfer nature has some special handling:

- Be aware when rendering this field that labels might be present more than once under the same key.
- The chosen value must be added when creating a quote or via an update of an existing quote.
- Failure to include a transfer nature as instructed will prevent the transfer from being sent.


## Related endpoints

- [Create a transfer](/api-reference/standard-transfer/transfercreate)
- [Validate transfer requirements](/api-reference/transfer/transferrequirementsvalidate)