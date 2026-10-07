# Recipient errors

Handle recipient identity, bank, address, and access errors.

Recipient requirements vary by currency, country, recipient type, and payment route. Retrieve the current requirements before creating a recipient, then handle every validation error returned by [create a recipient account](/api-reference/recipient/recipientcreate).

Recipient validation commonly uses a generic `code` such as `NOT_VALID`. In these responses, `path` is the most useful field for associating the error with your form.

Validation status
Recipient validation failures can use different `4xx` statuses across operations and service paths. Handle the documented response body instead of assuming all recipient validation uses only `400` or only `422`.

On this page:

- [Recipient error format](#recipient-error-format)
- [Create a recipient](#create-a-recipient)
- [NOT_VALID field path catalogue](#notvalid-field-path-catalogue)
- [Handle multiple field errors](#handle-multiple-field-errors)
- [Use dynamic recipient requirements](#use-dynamic-recipient-requirements)
- [Display recipient messages](#display-recipient-messages)
- [Retry recipient requests](#retry-recipient-requests)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely. Ask the customer to correct details only when they can edit them. If your integration supplies or changes those values, correct its validation or mapping instead.

## Recipient error format

A recipient response can contain several field errors in an `errors` array. See the [`NOT_VALID` example](#NOT_VALID) for a verified response.

Use the fields as follows:

- Use `path` to identify the affected form field.
- Use `code` within the recipient operation, not as a globally unique identifier.
- Use `message` as display text only when the error is user-correctable and the text suits your interface.
- Use `arguments` as error-specific context. Do not assume that every response uses the same argument positions.


## Create a recipient

**Endpoint:** `POST /accounts`

See the [create a recipient operation](/api-reference/recipient/recipientcreate) for the current request and response schema. The codes below can apply when Wise validates or creates the recipient.

A recipient field is missing or invalid for the selected recipient type or payment route.

**What to do**

- Use `path` to map the error to the affected input.
- Use the current recipient requirements to correct the field.
- Process every item in the `errors` array.


**Retry conditions**

Retry after correcting the identified fields.

**Example error response**

```json
{
  "timestamp": "2026-08-18T10:15:30Z",
  "errors": [
    {
      "code": "NOT_VALID",
      "message": "Please specify an IBAN.",
      "path": "IBAN",
      "arguments": ["IBAN"]
    }
  ]
}
```

A required recipient, identity, bank, or address field is absent.

**What to do**

- Retrieve the current recipient requirements.
- Request the missing value and verify the request mapping.


**Retry conditions**

Retry after adding the required field.

The route requires the recipient's date of birth or the supplied date is invalid.

**What to do**

- Request a complete valid date in `YYYY-MM-DD` format.
- Preserve the recipient's full legal name when updating the recipient data.


**Retry conditions**

Retry after correcting the date of birth.

The recipient is not available to the authenticated profile.

**What to do**

- Verify the profile, environment, token, and recipient ID.
- Show a generic unavailable-recipient message.


**Retry conditions**

Retry only after correcting the access context.

The referenced recipient is not available in the profile's recipient list.

**What to do**

- Retrieve the profile's recipients and reconcile the identifier.
- Create the required recipient if it does not exist.


**Retry conditions**

Retry after selecting or creating the correct recipient.

Wise could not create the recipient because of an unexpected service condition.

**What to do**

- Do not ask the end user to change valid input without evidence.
- Reconcile whether the recipient was created before sending another create request.
- Record the status, code, path, and trace identifier.


**Retry conditions**

Do not automatically retry an unexplained failure. If a transient cause is confirmed, use bounded backoff only when duplicate creation is prevented or the original outcome has been reconciled.

Recipient validation or creation failed without a more specific public identifier.

**What to do**

- Use a generic end-user message and do not display technical details.
- Record the HTTP status, code, path, operation, and trace identifier.


**Retry conditions**

Do not automatically retry the unchanged request without a confirmed recovery path. Establish the cause and replay safety first.

## NOT_VALID field path catalogue

`NOT_VALID` is a generic recipient validation code. Its meaning comes from `path`, the recipient type, and the selected currency route. The same path can have several constraints, so do not map `NOT_VALID` to one universal message.

| Path | Meaning | Handling |
|  --- | --- | --- |
| `accountHolderName` or `name` | The recipient or account-holder name is missing, too short, or contains characters unsupported by the route. | Request the recipient's full legal name. Follow the character and name-structure rules returned by recipient requirements. |
| `legalEntityType` or `legalType` | The selected personal or business recipient type is missing or not supported for the account type. | Preserve the intended recipient type, refresh requirements, and submit an allowed value. |
| `dateOfBirth` | Date of birth is required, malformed, in the future, or outside the accepted age range. | Request a complete date in `YYYY-MM-DD` format and validate calendar and range constraints before retrying. |
| `email` | The email is missing or malformed for a recipient type that requires it. | Request a valid email address. Do not substitute an email-recipient flow unless the requirements make that type available. |
| `accountNumber` | The account identifier is missing, has an invalid length or format, or is incompatible with the selected bank or recipient type. | Apply the current route constraints and ask for corrected details. Do not infer that a structurally valid number belongs to an account. |
| `accountType` | The account type is missing or is not one of the values supported by the route. | Render the options supplied by requirements and submit the selected value unchanged. |
| `IBAN` | The IBAN is missing, malformed, or uses a country code that is incompatible with the route. | Ask for the complete IBAN and validate its basic structure before retrying. |
| `sortCode` | The GBP bank sort code is missing, malformed, or unknown. | Ask for a supported sort code and keep it associated with the submitted account number. |
| `bsbCode` | The Australian BSB is missing, not 6 digits, or unknown. | Ask for the 6-digit BSB and validate the format before retrying. |
| `abartn` | The US routing number is missing, malformed, unknown, or not supported for the selected payment rail. | Ask for a valid routing number. If the response identifies an ACH or wire incompatibility, select a compatible recipient type. |
| `ifscCode` | The Indian Financial System Code (IFSC) is missing or malformed. | Ask for a valid IFSC and preserve leading characters or zeroes. |
| `bankCode` | A route-specific bank code is missing, malformed, unknown, or unsupported. | Use the bank list or autocomplete data supplied for the route instead of maintaining a permanent local list. |
| `branchCode` | A route-specific branch is missing, malformed, or unsupported. | Ask the user to select or enter a supported branch using the format returned by requirements. |
| `address.country` or `country` | The country is missing or is not a supported ISO country code for the field. | Submit the ISO format required by the operation and refresh dependent address requirements. |
| `address.city` | The recipient city is required but missing or invalid. | Request a valid city and preserve the complete nested address object. |
| `address.firstLine` | The first address line is missing or exceeds the supported length. | Request the street address and enforce the current maximum length before retrying. |
| `address.postCode` | The postal code is missing, malformed, or too long for the selected country. | Apply the country-specific requirement and request a corrected postal code. |
| `address.state` | The state or region is required or invalid for the selected country. | Render the state field when required and submit a supported state value or code. |
| No usable `path` | The request failed a recipient-level rule rather than one field rule, or the response did not expose the target field. | Place the error in a form-level summary. Use a suitable returned message or a safe generic fallback and record the complete signature for investigation. |


These are common observed paths, not a replacement for the recipient requirements response. New fields and constraints can be introduced for additional routes.

## Handle multiple field errors

Do not stop after the first item in `errors`.

1. Iterate over the complete `errors` array.
2. Normalise each `path` to your form's field identifier.
3. Group errors that target the same field.
4. Display suitable field-level feedback.
5. Place errors with no usable `path` in a form-level summary.
6. Log unknown combinations of status, `code`, and `path` for review.


## Use dynamic recipient requirements

Prevent avoidable validation errors by using the requirements operations:

1. [Retrieve recipient account requirements](/api-reference/recipient/recipientaccountrequirementsget) for the selected currency and recipient type.
2. Render the returned fields and validation constraints.
3. Refresh the requirements when a field indicates that a selection can change the remaining form.
4. Validate the current form using the available requirements operation before creating the recipient.
5. Preserve values that remain applicable after a requirements refresh.


Do not maintain a static list of required bank fields for every currency corridor. Requirements can vary by route and recipient type.

## Display recipient messages

Recipient validation messages are often suitable for field-level feedback, but not every recipient error is safe to pass through.

- Display messages for clearly identified, user-correctable fields after checking that the wording suits your interface.
- Map access, ownership, unexpected, and service errors to your own safe messages.
- Do not parse a message to determine the field or validation rule.
- Do not expose rejected bank details in logs or monitoring labels.


## Retry recipient requests

- Do not retry `NOT_VALID` or `MISSING` responses until the input changes.
- Do not retry `ACCESS_DENIED` until you correct the profile or recipient context.
- Retry transient service failures with backoff only when duplicate creation is prevented or can be reconciled.
- After a timeout, check whether the recipient was created before sending another create request.