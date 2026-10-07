# List or create recipients

A recipient is the party receiving funds from a transfer, sometimes called the beneficiary. A recipient account is the resource that represents the beneficiary and includes details like the type of entity (PRIVATE or BUSINESS), the currency the account can receive, and the account details (like account number, sort code, routing number, etc).

As the recipient account resource `id` is required in the [transfer request body](/guides/product/send-money/use-cases/correspondent/correspondent-create-transfer), your customer must either select a recipient from an existing list, or create a new recipient before creating the transfer.

## List recipient accounts

Use the [List recipient accounts endpoint](/api-reference/recipient/recipientlist) to request a list of existing recipient accounts for your customer.

Sample request
```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/accounts?creatorId=0&profileId=0&profile=0&currency=string&active=true&type=string&ownedByCustomer=true&size=20&seekPosition=0&sort=id%2Casc' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Sample response
```json 200 application/json
{
  "content": [
    {
      "id": 40000000,
      "creatorId": 41000000,
      "profileId": 30000000,
      "name": {
        "fullName": "John Doe",
        "givenName": null,
        "familyName": null,
        "middleName": null,
        "patronymicName": null,
        "cannotHavePatronymicName": null
      },
      "currency": "GBP",
      "country": "GB",
      "type": "SortCode",
      "legalEntityType": "PERSON",
      "active": true,
      "details": {
        "reference": null,
        "sortCode": "040075",
        "accountNumber": "37778842",
        "hashedByLooseHashAlgorithm": "ad245621b974efa3ef870895c3wer419a3f01af18a8a5790b47645dba6304194"
      },
      "commonFieldMap": {
        "accountNumberField": "accountNumber",
        "bankCodeField": "sortCode"
      },
      "hash": "666ef880f8aa6113fa112ba6531d3ed2c26dd9fgbd7de5136bfb827a6e800479",
      "accountSummary": "(04-00-75) 37778842",
      "longAccountSummary": "GBP account ending in 8842",
      "displayFields": [
        {
          "key": "details/sortCode",
          "label": "UK sort code",
          "value": "04-00-75"
        },
        {
          "key": "details/accountNumber",
          "label": "Account number",
          "value": "37778842"
        }
      ],
      "isInternal": false,
      "ownedByCustomer": false
    }
  ],
  "seekPositionForNext": 40000001,
  "seekPositionForCurrent": 40000000,
  "sort": {
    "empty": true,
    "sorted": false,
    "unsorted": true
  },
  "size": 20
}
```

```json 429 application/json
{}
```

When generating an authenticated quote (for recipient-first flows) and creating a transfer, use the selected recipient `id` value for the `targetAccount` property.

### Filter recipient list

Wise offers multiple query parameters to filter and sort the response, including `currency` and `type`, so you filter out recipients that don’t match a quote’s target currency (in the case of the quote-first flow) and suppress any recipient accounts with unsupported currency or recipient types.

For correspondent partners, recipient accounts are linked to the correspondent partner’s business profile ID. Since your customers do not have a Wise profile in our system, the recipient accounts they create are not linked to them as the “originator” and therefore cannot be filtered by originator data.

To ensure you serve your customers only a list of recipient accounts they’ve created, you’ll need to maintain a mapping from your customers (the originator of a transfer) to the Wise recipient IDs they create. You can then use that mapping to further filter the response and show your customers only the recipients they created, rather than all recipients created under your profile.

## Create a recipient account

If your customer hasn’t created a recipient yet, or needs to send funds to a recipient that doesn’t yet have a recipient account, you must create the recipient account.

Before you begin, note that recipient accounts are:

- **Currency-specific**: A recipient account accepts a single `currency` (`GBP`, `EUR`, `USD`, etc).
- **Type-specific**: Each currency supports one or more account `type` values (for example, `sort_code`, `iban`, `aba`, `indian`), which determine the structure of the `details` object in the request body.


### Requirements

Recipient account requirements, specifically what must be included in the `details` object of the request, can vary depending on currency, type, and other properties. The following table describes the required, conditional, and optional fields for the create recipient account request:

| Field  | Required? | Description |
|  --- | --- | --- |
| `currency` | Yes | The recipient account target currency (ISO 4217). Recipient accounts are specific to the currency they receive. |
| `type` | Yes | The recipient account type. Available values determined by `currency` (for example `sort_code`, `iban`, `aba`, `indian`).


The `type` determines the required shape of the `details` object. Use the [account requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget) to discover supported `type` values for a corridor. |
| `profile` | No | The Wise profile ID that owns the recipient account (for correspondent partners, this is your business profile ID). If omitted, defaults to the business profile ID used for the request. |
| `accountHolderName` | Yes | The recipient’s name. This field is subject to validation. Review the [account holder name field section](#account-holder-name-field) for further guidance. |
| `ownedByCustomer` | Conditional | Boolean indicating the recipient account belongs to the customer (commonly `false` for payout recipients).


When creating a [refund recipient](#creating-refund-recipients) (using `refund=true` query parameter), set this field to `true`. |
| `details` object | Yes | Object containing **currency + type–specific** account fields (bank details and sometimes address/metadata).


The exact required keys under `details.*` vary by corridor and may change over time. Retrieve them from the [account requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget) before submitting the create recipient account request. |
| `details.legalType` | Yes | Legal type of the recipient account owner: `PRIVATE` or `BUSINESS`. Determines some of the recipient data that must be collected. |
| `details.*` | Conditional | Bank account identifiers required for the selected `currency` + `type`. Examples include `details.iban`, `details.sortCode`, `details.accountNumber`, `details.abartn`, `details.ifscCode`


Always source required keys, regex, min/max lengths, and allowed values from the [account requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget). |
| `details.address` | Conditional | Recipient address object required for certain corridors.


For example, required when target currency is USD, PHP, THB, TRY, or source currency is USD or AUD. Use [account requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget) as the source of truth for which address subfields are required. |
| `details.dateOfBirth` | Conditional | The date of birth of the recipient (used for `PRIVATE` `legalType` only). Only required for some currencies. |


The `details` object has several more conditionally required fields. Review the [details object section](#the-details-object) for further information.

### Account holder name field

The `accountHolderName` field is validated on **recipient creation**. General guidance for this field:

- **Provide full first and last name** for individual (`PRIVATE`) recipients.
- Avoid initials or single-word names unless that is the true legal name and allowed for the route.
- Use the **registered legal business name** for business recipients.
- Some currencies/routes perform name matching (matching the name provided in the request with the name registered for the bank account). “Decorative” or truncated names can cause verification issues.


### The details object

The `details` object is the most important and most variable part of the request body.

The `details` object:

- Is **required** for all recipients.
- Has different structure per `currency` + `type`.
- Must conform exactly to the expectations encoded in the account handler for that type.


Below are representative examples for some of the most common currencies in Correspondent Send flows. These are **illustrative**. Always validate against the [account requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget).

GBP
Required fields/values:

- `currency` is `GBP`
- `type` is `sort_code`
- `legalType` is either `PRIVATE` or `BUSINESS`
- `details.sortCode` is the recipient account sort code (usually 6 digits, may include dashes)
- `details.accountNumber` is the recipient’s account number


Example request body:

```JSON
{
  "currency": "GBP",
  "type": "sort_code",
  "profile": {{profileId}},
  "ownedByCustomer": false,
  "accountHolderName": "John Doe",
  "details": {
    "legalType": "PRIVATE",
    "sortCode": "231470",
    "accountNumber": "28821822"
  }
}
```

EUR
Required fields/values:

- `currency` is `EUR`
- `type` is `iban`
- `legalType` is either `PRIVATE` or `BUSINESS`
- `details.iban` is the recipient account IBAN


Example request body:

```JSON
{
  "currency": "EUR",
  "type": "iban",
  "profile": {{profileId}},
  "ownedByCustomer": false,
  "accountHolderName": "Hans Mueller",
  "details": {
    "legalType": "PRIVATE",
    "iban": "DE89370400440532013000"
  }
}
```

USD
Required fields/values:

- `currency` is `USD`
- `type` is `aba`
- `legalType` is either `PRIVATE` or `BUSINESS`
- `details.abartn` is the ABA routing number
- `details.accountNumber` is the recipient’s account number
- `details.accountType` could be, for example, `CHECKING` or `SAVINGS` (confirm the exact allowed values via account-requirements response)
- `details.address` is the recipient address object (especially important when target currency is USD, or source currency is USD or AUD)


Example request body:

```JSON
{
  "currency": "USD",
  "type": "aba",
  "profile": {{profileId}},
  "ownedByCustomer": false,
  "accountHolderName": "Jane Doe",
  "details": {
    "legalType": "PRIVATE",
    "abartn": "026009593",
    "accountNumber": "12345678",
    "accountType": "CHECKING",
    "address": {
      "country": "US",
      "state": "NY",
      "city": "New York",
      "firstLine": "123 Main St",
      "postCode": "10001"
    }
  }
}
```

INR
Required fields/values:

- `currency` is `INR`
- `type` is `indian`
- `legalType` is either `PRIVATE` or `BUSINESS`
- `details.ifscCode` is the IFSC code of the bank branch
- `details.accountNumber` is the bank account number


INR also supports **UPI recipients** with `type: indian_upi` where `details` includes a UPI VPA (`details.vpa`).

Example request body:

```JSON
{
  "currency": "INR",
  "type": "indian",
  "profile": {{profileId}},
  "ownedByCustomer": false,
  "accountHolderName": "Priya Sharma",
  "details": {
    "legalType": "PRIVATE",
    "ifscCode": "HDFC0001234",
    "accountNumber": "50100123456789"
  }
}
```

BRL
For **transfers to BRL**:

- The recipient `email` field is **required** if the recipient is a business or the recipient is a consumer and the transfer is above 10K BRL (excluding transfers to self).
- While some account requirement responses may flag it as optional, partners should treat `email` as required in these scenarios to avoid recipient creation failures.


You should explicitly hardcode this condition into your BRL recipient UI/backend until the upstream behaviour is aligned.

ZAR
- Personal ZAR recipients typically require a `dateOfBirth` field.
- Business ZAR recipients require a local business identifier (for example, `zarIdentificationNumber`).


These fields appear under `details` and are surfaced via the [account requirements response](/api-reference/recipient/recipientaccountrequirementsget). If you hardcode ZAR forms, ensure these are included.

### Retrieve recipient requirements

Because the `details` structure and validation rules vary by currency, type, and other properties, Wise provides an [account requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget) to tell you exactly which details to collect.

The response returns an array of objects that indicate which **recipient account types** are available for the corridor, the fields that apply to that type, and attributes about those fields (like whether they are required, min/max length, values allowed, and more). You can then choose to use Wise’s [dynamic forms](/guides/product/send-money/recipient-verification/account-requirements) to gather the required data from your customer, hard-code the requirements into your system, or use a combination of both hard-coded and dynamic forms.

Hardcode or dynamic forms
Many correspondent integrations hardcode “known good” field requirements per corridor instead of implementing dynamic forms. This is acceptable, but you must be aware of evolving requirements and plan for updates. For example, ZAR added mandatory DOB and BRL now requires the `email` property.

The **account requirements endpoint** is always your source of truth.

#### Endpoint operation variants

The account requirements endpoint has two operation variants: with quote and without quote.

With quote
Recommended for quote-first flow.

```
 GET  /quotes/{{quoteId}}/account-requirements
```

Use this option when you have a quote ID. The Wise API references the currency corridor specified in that authenticated quote resource.

Without quote
For recipient-first flow.

```
 GET /account-requirements?source=EUR&target=USD&sourceAmount=1000
```

When you do not have a quote ID, specify the source and target currencies as query parameters in the request.

#### Request

- Correspondent partners must include the `originatorLegalEntityType` query parameter, indicating the sender is either `PRIVATE` or `BUSINESS`, so the correct requirements are returned in the response. When not included, the request is assumed to be for a `BUSINESS` entity, as we have no way of knowing if the true sender is a business or private individual.
- The `Accept-Minor-Version: 1` custom header extends the response to include **recipient name and email** fields, simplifying your form model.


```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/quotes/{quoteId}/account-requirements?originatorLegalEntityType=BUSINESS&addressRequired=false' \
  -H 'Accept-Minor-Version: 1' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

#### Response

- Returns a set of available recipient account types for the corridor (these effectively map to a payment rail).
- Each type includes a `fields` array, which describes what to include in the create recipient request body `details` object.


```JSON
"fields": [
   …
     {
      "name": "UK sort code",
      "group": [
          {
            "key": "sortCode",
            "name": "UK sort code",
            "type": "text",
            "refreshRequirementsOnChange": false,
            "required": true,
            "displayFormat": "**-**-**",
            "example": "40-30-20",
            "minLength": 6,
            "maxLength": 8,
            "validationRegexp": "^\d{2}-?\d{2}-?\d{2}$",
            "validationAsync": {
              "url": "https://api.sandbox.transferwise.tech/v1/validators/sort-code",
              "params": [
                 {
                   "key": "sortCode",
                   "parameterName": "sortCode",
                   "required": true
                    }
                  ]
                }
           "valuesAllowed": NULL
            }
         ]
      },
```

In this truncated example, the `fields.group` object for “UK sort code” includes a `key` with the value of `sortCode`. This value maps to the `details.sortCode` field in the create recipient account request body. The other values in the `group` array define important attributes for this item, some of which can impact recipient validation.

If `refreshRequirementsOnChange` is `true`:

- This means the value of this field in the `details` object could trigger additional required fields.
- Use `POST /quotes/{{quoteId}}/account-requirements` to re-query for any additional requirements that are conditional to that key’s value.
- The request body in this case is a partial [create recipient account](/api-reference/recipient/recipientcreate) body payload.


See our [Dynamic Form sandbox](https://sandbox.transferwise.tech/dynamic-forms-ui/v3) for an example of how to use this method to build a dynamic form.

#### Block global currencies

The term “global currencies” refers to sending a currency to a target bank account that is not within its origin country. For example, sending USD to a bank account located in Hong Kong. Currently, the global currencies are GBP, EUR, and USD.

The recipient requirements response will include all available recipient types for the currency specified in the request, even if out of scope for your integration.

If a global currency is out-of-scope for your integration, you will want to prevent it from appearing as a choice your customers can select, since out-of-scope currencies and recipient types will cause the transfer request to fail.

Global currencies to block when out-of-scope:

- GBP: non-GB IBANs
- EUR: non-Local SEPA IBANs and Swift recipient type (`swift_code`)
- USD: Swift recipient type (`swift_code`)


### Create recipient account request

When you have the values for all required fields of the `details` object, submit the [create recipient account](/api-reference/recipient/recipientcreate) request.

Sample request
```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/accounts?refund=false' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "currency": "GBP",
    "type": "sort_code",
    "profile": 30000000,
    "ownedByCustomer": true,
    "accountHolderName": "John Doe",
    "details": {
      "legalType": "PRIVATE",
      "sortCode": "040075",
      "accountNumber": "37778842",
      "dateOfBirth": "1961-01-01"
    }
  }'
```

Sample response
```json 200 application/json
{
  "id": 40000000,
  "creatorId": 41000000,
  "profileId": 30000000,
  "name": {
    "fullName": "John Doe",
    "givenName": null,
    "familyName": null,
    "middleName": null,
    "patronymicName": null,
    "cannotHavePatronymicName": null
  },
  "currency": "GBP",
  "country": "GB",
  "type": "SortCode",
  "legalEntityType": "PERSON",
  "active": true,
  "details": {
    "reference": null,
    "sortCode": "040075",
    "accountNumber": "37778842",
    "hashedByLooseHashAlgorithm": "ad245621b974efa3ef870895c3wer419a3f01af18a8a5790b47645dba6304194"
  },
  "commonFieldMap": {
    "accountNumberField": "accountNumber",
    "bankCodeField": "sortCode"
  },
  "hash": "666ef880f8aa6113fa112ba6531d3ed2c26dd9fgbd7de5136bfb827a6e800479",
  "accountSummary": "(04-00-75) 37778842",
  "longAccountSummary": "GBP account ending in 8842",
  "displayFields": [
    {
      "key": "details/sortCode",
      "label": "UK sort code",
      "value": "04-00-75"
    },
    {
      "key": "details/accountNumber",
      "label": "Account number",
      "value": "37778842"
    }
  ],
  "isInternal": false,
  "ownedByCustomer": false,
  "ultimateBeneficiary": {
    "accountNumber": "37778842",
    "bankName": "Wise Payments Limited",
    "bankCode": "026073150",
    "name": {
      "fullName": "John Doe"
    },
    "address": {
      "country": "US",
      "firstLine": "string",
      "postCode": "string",
      "city": "string",
      "state": "string"
    },
    "bankAddress": {
      "country": "US",
      "firstLine": "string",
      "postCode": "string",
      "city": "string",
      "state": "string"
    }
  },
  "confirmations": {
    "acceptedOutcomes": false,
    "acceptedAt": null,
    "quoteId": null,
    "outcomes": [
      {
        "type": "NAME_MATCHING",
        "timestamp": "2024-11-11T23:58:11.105916743Z",
        "outcome": "PARTIAL_FAILURE",
        "requiresCustomerAcceptance": true,
        "fieldsChecked": [
          "name/fullName",
          "details/accountNumber"
        ],
        "providedName": "John Doe",
        "resolvedName": "Joe Doe",
        "message": "The name entered is slightly different to the name on the account.",
        "recommendedUpdates": [
          {
            "path": "name/fullName",
            "value": "Joe Doe"
          }
        ]
      }
    ]
  }
}
```

```json 400 application/json
{
  "timestamp": "2024-12-06T06:43:52.472471344Z",
  "errors": [
    {
      "code": "NOT_VALID",
      "message": "Unknown bank code. Please check the sort code is correct, or contact customer support for more information.",
      "path": "sortCode",
      "arguments": [
        "sortCode",
        "231479"
      ]
    }
  ]
}
```

```json 401 application/json
{
  "error_description": "Invalid token",
  "error": "invalid_token"
}
```

```json 429 application/json
{}
```

### Recipient validation and verification

Recipient validation and verification is the process of verifying that the payment details provided by the sender are accurate before the payment is sent.

- **Validation** is the preliminary check performed immediately upon the `POST /accounts` request to ensure that the submitted recipient data conforms to the required schema and regional formatting rules, such as field lengths and format checks.
- **Verification** is a more in-depth verification process carried out to confirm details such as the existence of the account or the recipient's account number and name match the records held by the destination bank. Verification is only supported for certain target currencies.


Review our [Recipients guide](/guides/product/send-money/recipients) for more details about how verification and validation work and how to handle verification outcomes for the currencies verification applies to.

### Using the response

Important fields in the create recipient account response body:

- `id`: This is the recipient identifier, which you use as the `targetAccount` value when creating transfers. You can also use this as a foreign key in your own database for “saved recipients.”
- Routes with recipient verification (for example, INR, IDR, CNY, KRW, EUR) include a `confirmations` object that provides the outcome of the verification in an `outcomes` object. If any outcomes require customer acceptance, those must be handled before using the recipient for transfers. See our [Recipients guide](/guides/product/send-money/recipients) for more details.
- `accountSummary` and `longAccountSummary` are available in higher-level resources and can be cached for UI display.


Note that it is not possible to edit details for an existing recipient. If these need to change, you must create a new recipient.

### Creating refund recipients

In some correspondent setups, recipients are also created to support refunds back to the original sender account. Refund recipients are typically associated with the originating account used for funding a transfer.
When creating a refund recipient, use the [create recipient account endpoint](/api-reference/recipient/recipientcreate) and add the query parameter `refund=true` to the endpoint path.

Notes for specific currencies:

- For **USD refunds**, Wise often requires a stored account to push refunds via ACH.
- For **GBP and SGD**, refunds can often be pushed back directly via FPS/FAST using funding details without a separate refund recipient.


### Error handling

Common errors when creating recipient accounts:

| HTTP Status | Example error body | Meaning |
|  --- | --- | --- |
| 422 | `code: NOT_VALID`, `path: accountHolderName`, message: “Please enter the recipients first and last name.” | `accountHolderName` does not meet route-specific naming rules. |
| 422 | `code: NOT_VALID`, `path: currency`, message: “Please enter currency.” | Missing or invalid `currency`. |
| 422 | `code: NOT_VALID`, `path: type`, message: “Please enter account type.” | Missing or unsupported `type` for given `currency`. |
| 422 | `code: non_existent_account` | Account doesn’t exist or doesn’t belong to the provided bank code (commonly seen in KRW, CNY existence checks). |
| 422 | Validation errors on `details.*` | Regex/length/routing validations failed. Use the regex and example values from account-requirements to validate client-side. |
| 400 | Malformed JSON | Request body not parseable as valid JSON or field types mismatch expectations. |


For **recipient-first flows**, you may see `INVALID_RECIPIENT` errors when creating a transfer if the originally created recipient doesn’t satisfy the true requirements of the final quote. If this occurs:

1. Call the [account requirements](/api-reference/recipient#account-requirements) dynamic form endpoint with the customer’s actual quote they created in the flow.
2. Render the dynamic form for the customer, which now contains the correct options.
3. (optional) Attempt to pre-populate the form using the details from the originally chosen recipient. Where keys match the new form, you can populate the fields so the customer doesn’t need to re-type them.
4. [Delete](/api-reference/recipient#delete) the old recipient.
5. The customer creates a new recipient with the correct details.