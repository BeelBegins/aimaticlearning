# Recipient verification

To optimise payment success rates and reduce returned transfer incidents, Wise performs a two-tier check during recipient creation: **validation** and **verification**.

## Validation

**Validation** is the preliminary check performed immediately upon a [create recipient account request](/api-reference/recipient/recipientcreate). This process ensures that the submitted recipient data conforms to the required schema and regional formatting rules (for example, account number length and format).

If validation fails, the API returns an HTTP error response and the recipient resource is not created. You must surface the specific error details to the customer so they can correct the input before retrying the request.

## Verification

**Verification**, also called confirmation of payee (CoP), is a more in-depth check that runs once all validations have passed. For supported currencies, this step confirms details such as whether the account exists at the destination bank, or whether the recipient's name matches the records held by the receiving institution.

### Supported currencies

Recipient verification is currently active for:

* **CNY** (Chinese Yuan)
* **EUR** (Euro, for Enterprise/Embedded payouts to SEPA accounts)
* **IDR** (Indonesian Rupiah)
* **INR** (Indian Rupee)
* **KRW** (South Korean Won)


The following currencies will be supported soon:

- **GBP** (British Pound)
- **EUR** (Euro, for all partner and payout types)
- **JPY** (Japanese Yen)
- **AUD** (Australian Dollar)
- **USD** (US Dollar)
- **MYR** (Malaysian Ringgit)
- **THB** (Thai Baht)
- **BRL** (Brazilian Real)
- **TRY** (Turkish Lira)
- **PKR** (Pakistani Rupee)


For a full reference of supported recipient types, validated fields, verification behaviour, and possible outcomes per currency, see the [Recipient verification reference guide](/guides/product/send-money/recipient-verification/recipient-verification-reference).

## Validation and verification process

All checks run **sequentially** during recipient creation. If an earlier step fails, later steps do not run.

### Step 1: Field-level validation

Field-level validation checks the format and correctness of each input field. It runs first, before any external verification call is made.

If any field fails validation, the **recipient resource is not created** and the API returns an error response in the following format:

```json
{
  "errors": [
    {
      "code": "NOT_VALID",
      "path": "name/fullName",
      "message": "The name provided is not valid."
    }
  ]
}
```

The `path` field identifies which input field failed. Multiple errors can be returned in a single response if more than one field is invalid. Surface these details to the customer and allow them to correct the input before retrying the `POST /accounts` request.

To see the validation rules for a specific field, send a [retrieve recipient account requirements request](/api-reference/recipient/recipientaccountrequirementsget) and check the `group` array in the response for the field in question.

This example shows the `group` array for the `IBAN` field:

```json
{
    "name": "IBAN",
    "group": [
      {
        "key": "IBAN",
        "name": "IBAN",
        "type": "text",
        "refreshRequirementsOnChange": false,
        "required": true,
        "displayFormat": "**** **** **** **** **** **** **** ****",
        "example": "DE12345678901234567890",
        "minLength": 14,
        "maxLength": 42,
        "validationRegexp": "^[a-zA-Z]{2}[a-zA-Z0-9 ]{12,40}$",
        "validationAsync": null,
        "valuesAllowed": null
      }
    ]
}
```

For currencies *without* verification, a recipient that passes all field validations is created immediately. For currencies *with* verification, the process continues to step 2.

### Step 2: Verification (CoP)

Verification only runs after all field-level validations have passed. It calls an external provider (like a receiving bank, payment scheme, or third-party data service) to confirm the validity of the recipient details.

Two types of verification can occur, depending on the currency:

- `ACCOUNT_EXISTENCE`: Confirms that the account number is valid and reachable at the destination bank or payment provider.
- `NAME_MATCHING`: Confirms that the name provided matches the name registered on the account. For currencies that support `NAME_MATCHING`, account existence is implied.


In some cases, the account existence and name are verified together as a combined unit. The type of check that applies to each currency is specified in the [Recipient verification reference guide](/guides/product/send-money/recipient-verification/recipient-verification-reference).

Verification results in one of two outcomes:

- **Non-blocking**: The recipient resource is created and the verification result is returned in the `confirmations` object of the response. Depending on the outcome, further action may be required before the recipient can be used for a transfer.
- **Blocking**: An error is returned and the recipient resource is not created. Blocking outcomes occur when the external provider confirms that the account or details are definitively invalid (for example, an account number does not exist at the given bank). You must correct the input and retry the `POST /accounts` request.


Blocking errors follow the same format as field validation errors, with the relevant `path` and `code` values. For blocking error codes per currency, see the [Recipient verification reference guide](/guides/product/send-money/recipient-verification/recipient-verification-reference).

### The confirmations object

When a recipient resource is successfully created after the verification step, the verification result is returned in the `confirmations` object of the response. If the `confirmations` object is not present in the response, you can retrieve it separately via `GET /accounts/{accountId}`.

The `confirmations` object has the following structure:

```json
{
  "confirmations": {
    "acceptedOutcomes": false,
    "acceptedAt": null,
    "quoteId": null,
    "outcomes": [
      {
        "type": "NAME_MATCHING",
        "outcome": "SUCCESS",
        "timestamp": "2026-03-07T10:30:00Z",
        "requiresCustomerAcceptance": false,
        "fieldsChecked": ["name/fullName", "details/iban"],
        "message": null,
        "resolvedName": null,
        "providedName": "John Doe",
        "recommendedUpdates": []
      }
    ]
  }
}
```

Notable fields in the `confirmations` object:

| Field  | Type | Description |
|  --- | --- | --- |
| `acceptedOutcomes` | boolean | Whether the customer has explicitly accepted a non-SUCCESS outcome via the PATCH endpoint. `false` until accepted. |
| `acceptedAt` | string | Timestamp of acceptance. `null` until PATCH is called. |
| `quoteId` | string | If the confirmation check was run as part of a quote compatibility check, then the `quoteId` is included in the result. If `quoteId` is present, the outcome acceptance needs the `quoteId` to be specified as well. |
| `outcomes.type` | enum string | The type of check performed: `ACCOUNT_EXISTENCE` or `NAME_MATCHING`. |
| `outcomes.outcome` | enum string | The actual result of the check. Possible values: `SUCCESS`, `PARTIAL_FAILURE`, `FAILURE`, `COULD_NOT_CHECK`. See [Verification outcomes](#verification-outcomes) for more details. |
| `outcomes.requiresCustomerAcceptance` | boolean | If `true`, the customer must explicitly accept this outcome before the recipient can be used for a transfer.

Requiring customer acceptance is relatively rare, and in most cases is specific to regions with regulations that require the customer to see the result (such as partners in the European Economic Area, or EEA). |
| `outcomes.fieldsChecked` | array of strings | Indicates which fields were submitted to the verification provider. |
| `outcomes.message` | string | A human-readable description of the outcome, suitable for display to the customer. `null` for `SUCCESS` outcomes. |
| `outcomes.resolvedName` | string | The name returned by the verification provider for the account, where available. If not available, will be `null` or may be omitted from response. |
| `outcomes.providedName` | string | The name submitted in the request. |
| `outcomes.recommendedUpdates` | array of strings | Suggested field corrections from the provider, where supported. Empty for most currencies. |


## Verification outcomes

The value in the `outcomes.outcome` field indicates the result of the verification check.

| Outcome  | Meaning |
|  --- | --- |
| `SUCCESS` | Verification passed. The account exists and, where applicable, the name matches.

The recipient is ready for immediate use and no further action is required. |
| `PARTIAL_FAILURE` | A close but not exact name match was found. A minor discrepancy exists. |
| `FAILURE` | Name does not match the records at the destination bank, or the account was not found. |
| `COULD_NOT_CHECK` | Verification could not be completed due to a provider timeout, error, or service unavailability. |


`PARTIAL_FAILURE`, `FAILURE`, and `COULD_NOT_CHECK` are non-blocking outcomes. The recipient resource is created, but further action may be required before it can be used for a transfer. Check the `requiresCustomerAcceptance` field to determine what to do next.

Not all currencies support all four outcomes. For the outcomes possible per currency, see the [Recipient verification reference guide](/guides/product/send-money/recipient-verification/recipient-verification-reference).

### Handling verification outcomes

When the outcome is anything other than `SUCCESS`, check the
`outcomes.requiresCustomerAcceptance` field to determine whether explicit customer action is required:

- `requiresCustomerAcceptance: false`: In this case, a minor discrepancy may exist, but the recipient is usable without further action. You can choose to inform the customer of the discrepancy, but no PATCH request is required to proceed with a transfer.
- `requiresCustomerAcceptance: true`: This means the recipient cannot be used for a transfer until the customer has explicitly acknowledged the outcome. Present the verification result to the customer and obtain their confirmation before proceeding.
  - If the customer chooses to correct the details, create a new recipient by submitting corrected data via a new `POST /accounts` request.
  - If the customer confirms the existing details and accepts the outcome, [call the PATCH endpoint](/api-reference/recipient/recipientconfirmationsaccept) to record their acceptance and unblock the recipient for use.


#### Accepting a non-SUCCESS outcome

To move a recipient to a usable state after the customer has acknowledged a non-SUCCESS outcome, call the [confirmation acceptance endpoint](/api-reference/recipient/recipientconfirmationsaccept).

Request
```shell curl
curl -i -X PATCH \
  'https://api.wise.com/2026Q4/accounts/{accountId}/confirmations?quoteId=497f6eca-6276-4993-bfeb-53cbbbba6f08' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "acceptedOutcomes": true
  }'
```

Response
The response mirrors the original `confirmations` object, with `acceptedOutcomes` set to true and `acceptedAt` populated with the acceptance timestamp:

```json
{
  "confirmations": {
  "acceptedOutcomes": true,
  "acceptedAt": "2026-03-07T10:35:00Z",
  "quoteId": null,
  "outcomes": [
    {
      "type": "NAME_MATCHING",
      "outcome": "PARTIAL_FAILURE",
      "timestamp": "2026-03-07T10:30:00Z",
      "requiresCustomerAcceptance": true,
      "fieldsChecked": ["name/fullName", "details/iban"],
      "message": "The name you entered doesn't exactly match the account holder's name.",
      "resolvedName": null,
      "providedName": "John Doe",
      "recommendedUpdates": []
    }
   ]
  }
}
```

Once `acceptedOutcomes` is `true`, the recipient can be used for a transfer.

Important!
When a customer accepts a `FAILURE` or `PARTIAL_FAILURE` outcome, this constitutes an explicit risk acknowledgement.

Ensure your integration presents the mismatch details clearly before calling the PATCH endpoint, as the acceptance is treated as informed consent and may affect liability for any resulting loss of funds under applicable regulations.

## Workflow summary

The standard integration flow for creating and using a verified recipient:

1. Submit a `POST /accounts` request with the recipient's details.
2. Check the `confirmations.outcomes.outcome` field in the response.
3. If `requiresCustomerAcceptance` is `true`, present the verification result to the customer. If they choose to proceed, call `PATCH /accounts/{accountId}/confirmations` with `{"acceptedOutcomes": true}`.
4. Create a transfer using the recipient.


If the `POST /accounts` request returns an error (blocking outcome or field validation failure), correct the input based on the `errors` array and retry from step 1.

## Testing in the sandbox

You can test recipient verification for supported currencies in the sandbox with the following basic flow:

1. **Create a recipient** via `POST /accounts/` with valid details.
2. **Inspect the response**. Check the `confirmations.outcomes.outcome` field.
3. **If outcome requires acceptance** (`requiresCustomerAcceptance: true`), call `PATCH /accounts/{accountId}/confirmations` with `{"acceptedOutcomes": true}`.
4. **Create a transfer** using the accepted recipient.


Note that some currencies have unique testing behaviours. Additional details about testing recipient verification coming soon.