# Profile errors

Handle personal and business profile validation errors.

Profile operations validate identity, contact, address, and business information. Treat the current operation schema as the source of truth for required fields. Process every returned error and use `path` to associate it with an input.

Response excerpts show only the entries for the named code from a documented response. The complete response can contain additional errors.

On this page:

- [Create a personal profile](#create-a-personal-profile)
- [Create a business profile](#create-a-business-profile)
- [Send only one business category format](#send-only-one-business-category-format)
- [Handle a profile conflict](#handle-a-profile-conflict)
- [Build country-specific addresses](#build-country-specific-addresses)
- [Legacy personal profile errors](#legacy-personal-profile-errors)
- [Legacy address errors](#legacy-address-errors)
- [Handle profile error messages](#handle-profile-error-messages)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely. Ask the customer to correct details only when they can edit them. If your integration supplies or changes those values, correct its validation or mapping instead.

## Create a personal profile

**Endpoint:** `POST /profiles/personal-profile`

See the [create a personal profile operation](/api-reference/profile/profilepersonalcreate) for the current request and response schema.

Use the current schema for required fields and process any returned validation items. The legacy identifiers listed later on this page are documented for different endpoints and should not be assumed to apply to this operation.

## Create a business profile

**Endpoint:** `POST /profiles/business-profile`

See the [create a business profile operation](/api-reference/profile/profilebusinesscreatev3) for the current request and response schema. The operation can return several field-specific `api.*` errors in one response.

The request does not contain a business name.

**HTTP status:** `400`

**What to do**

- Provide `businessName`.
- Process every remaining error in the response.


**Retry conditions**

Retry after providing all required business fields.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.businessName.missing",
      "message": "Please specify the name of your business",
      "path": "businessName",
      "arguments": null
    }
  ]
}
```

A registration number is required for the selected company type.

**HTTP status:** `400`

**What to do**

Provide `registrationNumber`, or confirm that the selected company type does not require one.

**Retry conditions**

Retry after correcting the registration details.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.registrationNumber.missing",
      "message": "Please specify the registration number of your business ",
      "path": "registrationNumber",
      "arguments": null
    }
  ]
}
```

The request does not contain at least one current, valid industry category.

**HTTP status:** `400`

**What to do**

Provide `industryCategories` using values accepted by the current operation.

**Retry conditions**

Retry after correcting the category list.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.industryCategories.invalid",
      "message": "Please provide at least one valid industry category",
      "path": "industryCategories",
      "arguments": null
    }
  ]
}
```

The required business address is absent.

**HTTP status:** `400`

**What to do**

Provide the address object and all fields required for its country.

**Retry conditions**

Retry after providing the address.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.address.missing",
      "message": "Please specify the address of your business",
      "path": "address",
      "arguments": null
    }
  ]
}
```

The request does not identify the business's company type.

**HTTP status:** `400`

**What to do**

Provide a supported `companyType` value.

**Retry conditions**

Retry after providing the company type.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.companyType.missing",
      "message": "Please select a company type",
      "path": "companyType",
      "arguments": null
    }
  ]
}
```

The business name contains content that the operation does not accept.

**HTTP status:** `400`

**What to do**

Correct `businessName` using the returned message and current field constraints.

**Retry conditions**

Retry after correcting the business name.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.businessName.invalid",
      "message": "Business name contains invalid characters",
      "path": "businessName",
      "arguments": null
    }
  ]
}
```

The business name is shorter than the accepted minimum length.

**HTTP status:** `400`

**What to do**

Provide a non-empty `businessName` that meets the current length constraint.

**Retry conditions**

Retry after correcting the business name.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.businessName.size.too.short",
      "message": "Business name must be at least 1 character long",
      "path": "businessName",
      "arguments": null
    }
  ]
}
```

The supplied company type is not accepted by the operation.

**HTTP status:** `400`

**What to do**

Replace `companyType` with a supported current value.

**Retry conditions**

Retry after correcting the company type.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.companyType.invalid",
      "message": "Invalid company type selected",
      "path": "companyType",
      "arguments": null
    }
  ]
}
```

One or more industry categories are not permitted for this profile.

**HTTP status:** `400`

**What to do**

Check that the categories accurately describe the business. Correct a classification mistake; if the correct category is not permitted, ask Wise to confirm eligibility before resubmitting.

**Retry conditions**

Retry only after correcting a classification mistake or resolving eligibility with Wise.

**Response excerpt (2026Q3)**

```json
{
  "errors": [
    {
      "code": "api.industryCategories.forbidden",
      "message": "One or more supplied industry categories is not permitted",
      "path": "industryCategories",
      "arguments": null
    }
  ]
}
```

**Validate owners and directors**

- Validate every object in an owners or directors array.
- Provide the complete identity, role, contact, and address data required by the current schema.
- Process every returned error because different objects can fail for different reasons.
- Use the returned `path` to map the error to the correct person and field.


## Send only one business category format

**Endpoints:** `POST /profiles/business-profile`, `PUT /profiles/{profileId}/business-profile`

`industryCategories` and the deprecated `firstLevelCategory`/`secondLevelCategory` pair are mutually exclusive. A request that supplies both is rejected with a `400` on the `industryCategories` path.

1. Send `industryCategories` and omit `firstLevelCategory` and `secondLevelCategory` from the request entirely.
2. Do not send the new field alongside the legacy pair to move an existing profile across. Drop the legacy fields in the same request.
3. Apply the same rule on update. A request that changes both formats at once is rejected.


No dedicated error code is documented for this rejection. Use the `industryCategories` path to identify it rather than the message text.

For the values accepted by each operation, see the [Wise business categories list](/guides/product/account-setup/customer-onboarding/business-categories). To move an existing integration off the legacy pair, see [Migrating to industry categories](/guides/product/account-setup/customer-onboarding/migrate-business-profile-industry-categories).

## Handle a profile conflict

Profile creation can return `409` when a matching profile already exists, particularly when the original request did not use an idempotency identifier.

1. List the user's profiles before creating another one.
2. Reconcile whether the original request succeeded.
3. Reuse the same `X-idempotence-uuid` only when retrying the same logical creation attempt.


Do not treat the status alone as a reusable error code. Add a returned identifier to this catalogue only after its public meaning is confirmed.

## Build country-specific addresses

Before creating or updating an address:

1. Call the [get address requirements operation](/api-reference/address/addressrequirementsget).
2. Render the returned fields and validation constraints.
3. Preserve field names exactly when mapping the form to the request.
4. Process every returned validation error.


Country requirements can change. Do not maintain a permanent client-side list as your only source of truth.

## Legacy personal profile errors

**Endpoint:** `POST /v1/profiles`

These identifiers are documented for the legacy profile operation. Their applicability to `POST /profiles/personal-profile` is not established here.

Wise cannot process the request structure or supplied object.

**HTTP status:** `400`

**What to do**

- Compare the complete request with the legacy operation schema.
- Correct unsupported profile data or incomplete nested objects.


**Retry conditions**

Retry after correcting the request.

**Example error response (POST /v1/profiles): missing details**

```json
{
  "errors": [
    {
      "code": "BAD_REQUEST",
      "message": "Missing details property",
      "arguments": []
    }
  ]
}
```

A required identity, contact, or address field is absent or blank.

**HTTP status:** `422`

**What to do**

- Use `path` to identify the affected input.
- Apply the applicable country and profile requirements.
- Process every missing field returned in the array.


**Retry conditions**

Retry after providing the required fields.

**Response excerpt (POST /v1/profiles)**

```json
{
  "errors": [
    {
      "code": "MISSING",
      "message": "Please enter your first name",
      "path": "firstName",
      "arguments": [
        "firstName"
      ]
    },
    {
      "code": "MISSING",
      "message": "Property [lastName] cannot be blank",
      "path": "lastName",
      "arguments": [
        "lastName"
      ]
    }
  ]
}
```

A field failed validation and the response uses a generic identifier. Use `path` to identify the affected field; the example shows an unparseable date of birth.

**HTTP status:** `422`

**What to do**

- Compare the identified field with the legacy operation schema.
- Correct the value using the applicable field requirements.


**Retry conditions**

Retry after correcting the identified field.

**Response excerpt (POST /v1/profiles)**

```json
{
  "errors": [
    {
      "code": "ERROR",
      "message": "Unparseable date",
      "path": "dateOfBirth",
      "arguments": [
        "dateOfBirth"
      ]
    }
  ]
}
```

A supplied value is shorter than its minimum accepted length.

**HTTP status:** `422`

**What to do**

- Use `path` to identify the field.
- Apply the current schema and any limits supplied in `arguments`.


**Retry conditions**

Retry after correcting the value.

**Response excerpt (POST /v1/profiles)**

```json
{
  "errors": [
    {
      "code": "TOO_SMALL",
      "message": "Value provided is too short. Please enter a valid phone number",
      "path": "phoneNumber",
      "arguments": [
        "phoneNumber",
        "+123",
        "5",
        "25"
      ]
    }
  ]
}
```

A value failed operation-specific validation without a more specific public identifier.

**HTTP status:** `422`

**What to do**

- Use the endpoint, `path`, and message together.
- Use a safe form-level fallback when no field is identified.
- Record the response signature for monitoring.


**Retry conditions**

Retry only after the request changes.

**Response excerpt (POST /v1/profiles)**

```json
{
  "errors": [
    {
      "code": "UNEXPECTED",
      "message": "Please enter a valid phone number",
      "path": "phoneNumber",
      "arguments": [
        "phoneNumber",
        "+123"
      ]
    }
  ]
}
```

## Legacy address errors

**Endpoint:** `POST /v1/addresses`

The published legacy address guide documents `UNEXPECTED_ERROR` with HTTP `500` for missing request details or a required postcode. Correct these known request defects before resubmitting; do not assume every `500` is transient.

Wise encountered an unexpected validation or service failure.

**What to do**

- Confirm that the request matches the current operation schema.
- Log a redacted response signature for investigation.
- Do not display diagnostic text directly to the end user.


**Retry conditions**

Correct the missing details or required postcode before resubmitting. Reconcile an uncertain create result before repeating it.

## Handle profile error messages

- Display returned messages only for user-correctable input.
- Map authentication, ownership, and service failures to safe messages.
- Do not parse message text or use it for programmatic branching.
- Redact identity, contact, address, and business data from logs.