# Case message types

This page describes the submission data structure and accepted values for each message submission type supported by the [Submit a Message](/api-reference/case/casesubmitmessage) endpoint.

- Structured responses: Use the case subType appended with _SUBMISSION (e.g., DEPOSIT_SANCTION_HIT_SUBMISSION, RECIPIENT_LOCATION_HIT_SUBMISSION).
- Free text responses: Use FREEFORM.
- File attachments: Use FILE_SUBMISSION with previously uploaded file IDs.


## Supported submission types

| Submission type | Description | Valid for case sub-types |
|  --- | --- | --- |
| [`FREEFORM`](#freeform) | Free-text message for general communication. | All |
| [`FILE_SUBMISSION`](#file_submission) | Attach previously uploaded files to a case. | All |
| [`DEPOSIT_SANCTION_HIT_SUBMISSION`](#deposit_sanction_hit_submission) | Submit entity information for deposit sanction hit cases. | `DEPOSIT_SANCTION_HIT` |
| [`RECIPIENT_SANCTION_HIT_SUBMISSION`](#recipient_sanction_hit_submission) | Submit entity information for recipient sanction hit cases. | `RECIPIENT_SANCTION_HIT` |
| [`REFERENCE_SANCTION_HIT_SUBMISSION`](#reference_sanction_hit_submission) | Submit entity information for reference sanction hit cases. | `REFERENCE_SANCTION_HIT` |
| [`REFERENCE_LOCATION_HIT_SUBMISSION`](#reference_location_hit_submission) | Submit location-related information for reference location hit cases. | `REFERENCE_LOCATION_HIT` |
| [`RECIPIENT_LOCATION_HIT_SUBMISSION`](#recipient_location_hit_submission) | Submit location-related information for recipient location hit cases. | `RECIPIENT_LOCATION_HIT` |


## Entity types for sanction hit submissions

Sanction hit submissions support different entity types depending on the submission type:

| Entity type | DEPOSIT | RECIPIENT | REFERENCE |
|  --- | --- | --- | --- |
| `individual` | Yes | Yes | Yes |
| `organisation` | Yes | Yes | Yes |
| `vessel` | No | No | Yes |
| `multiple` | No | No | Yes |
| `other` | No | No | Yes |


## FREEFORM

Free-text message for general communication on a case. Use this to provide additional context, ask questions, or share documentation references.

**Prerequisites:**

- Case must not be in `RESOLVED` or `FAILED` status


Request Fields
type
Required. Must be `FREEFORM`

submissionData.freeText
Required. The free-text message to submit. Minimum length: 1 character. Maximum length: 10,000 characters.

submissionData example
```json
{
  "type": "FREEFORM",
  "submissionData": {
    "freeText": "Following up on the requested documentation. We have verified the recipient identity through our internal KYC process."
  }
}
```

## FILE_SUBMISSION

Attach previously uploaded files to a case as supporting documentation. Files must be uploaded via `POST /cases/{caseId}/files` before submitting.

**Prerequisites:**

- Case must not be in `RESOLVED` or `FAILED` status
- Files must have been uploaded via `POST /cases/{caseId}/files`
- All files must belong to the specified profile


Request Fields
type
Required. Must be `FILE_SUBMISSION`

submissionData.profileId
Required. The profile ID that the files belong to. Must match the profile associated with the uploaded files.

submissionData.fileIds
Required. List of file IDs to attach to the case. Must not be empty. Must not contain duplicates. All file IDs must reference existing files that were previously uploaded.

submissionData example
```json
{
  "type": "FILE_SUBMISSION",
  "submissionData": {
    "profileId": 14556049,
    "fileIds": [
      "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    ]
  }
}
```

## DEPOSIT_SANCTION_HIT_SUBMISSION

Submit entity information for deposit sanction hit cases. The deposit sanction hit occurs when a depositor's details match against sanctions screening.

**Valid entity types:** `individual` or `organisation` (exactly one required)

### Deposit Individual

Submit information about an individual depositor.

Request Fields
type
Required. Must be `DEPOSIT_SANCTION_HIT_SUBMISSION`

submissionData.individual.name
Required. Full name of the individual. Maximum length: 255 characters.

submissionData.individual.dob
Date of birth. Accepted formats: `DD/MM/YYYY` or `YYYY-MM-DD`. Maximum length: 10 characters.

submissionData.individual.nationality
Nationality of the individual. Maximum length: 100 characters.

submissionData example
```json
{
  "type": "DEPOSIT_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "individual": {
      "name": "Maria Garcia Rodriguez",
      "dob": "12/05/1988",
      "nationality": "Spanish"
    }
  }
}
```

### Deposit Organisation

Submit information about an organisation depositor.

Request Fields
type
Required. Must be `DEPOSIT_SANCTION_HIT_SUBMISSION`

submissionData.organisation.name
Required. Name of the organisation. Maximum length: 255 characters.

submissionData.organisation.streetAddress
Required. Street address of the organisation. Maximum length: 500 characters.

submissionData.organisation.city
Required. City where the organisation is located. Maximum length: 100 characters.

submissionData.organisation.postCode
Required. Postal code of the organisation's address. Maximum length: 20 characters.

submissionData.organisation.countryIso3
Required. ISO 3166-1 alpha-3 country code. Exactly 3 uppercase letters. Pattern: `^[A-Z]{3}$`. Example: `GBR`, `USA`, `DEU`.

submissionData.organisation.natureOfBusiness
Description of the organisation's business activities. Maximum length: 500 characters.

submissionData.organisation.website
Organisation's website URL. Must be a valid URI format. Maximum length: 500 characters.

submissionData example
```json
{
  "type": "DEPOSIT_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "organisation": {
      "name": "Tech Solutions Europe S.A.",
      "streetAddress": "Av. de la Liberté 25",
      "city": "Luxembourg",
      "postCode": "1931",
      "countryIso3": "LUX",
      "natureOfBusiness": "Software Development",
      "website": "https://www.techsolutions-eu.com"
    }
  }
}
```

## RECIPIENT_SANCTION_HIT_SUBMISSION

Submit entity information for recipient sanction hit cases. The recipient sanction hit occurs when a recipient's details match against sanctions screening.

**Valid entity types:** `individual` or `organisation` (exactly one required)

### Recipient Individual

Submit information about an individual recipient.

Request Fields
type
Required. Must be `RECIPIENT_SANCTION_HIT_SUBMISSION`

submissionData.individual.name
Required. Full name of the individual. Maximum length: 255 characters.

submissionData.individual.countryOfResidenceIso3
Required. ISO 3166-1 alpha-3 country code for country of residence. Exactly 3 uppercase letters. Pattern: `^[A-Z]{3}$`. Example: `GBR`, `SGP`, `USA`.

submissionData.individual.dob
Date of birth. Accepted formats: `DD/MM/YYYY` or `YYYY-MM-DD`. Maximum length: 10 characters.

submissionData.individual.nationality
Nationality of the individual. Maximum length: 100 characters.

submissionData example
```json
{
  "type": "RECIPIENT_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "individual": {
      "name": "Li Wei Chen",
      "countryOfResidenceIso3": "SGP",
      "dob": "03/11/1982",
      "nationality": "Singaporean"
    }
  }
}
```

### Recipient Organisation

Submit information about an organisation recipient.

Request Fields
type
Required. Must be `RECIPIENT_SANCTION_HIT_SUBMISSION`

submissionData.organisation.name
Required. Name of the organisation. Maximum length: 255 characters.

submissionData.organisation.streetAddress
Required. Street address of the organisation. Maximum length: 500 characters.

submissionData.organisation.city
Required. City where the organisation is located. Maximum length: 100 characters.

submissionData.organisation.postCode
Required. Postal code of the organisation's address. Maximum length: 20 characters.

submissionData.organisation.countryIso3
Required. ISO 3166-1 alpha-3 country code. Exactly 3 uppercase letters. Pattern: `^[A-Z]{3}$`.

submissionData.organisation.natureOfBusiness
Description of the organisation's business activities. Maximum length: 500 characters.

submissionData.organisation.website
Organisation's website URL. Must be a valid URI format. Maximum length: 500 characters.

submissionData example
```json
{
  "type": "RECIPIENT_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "organisation": {
      "name": "Pacific Rim Trading Co.",
      "streetAddress": "88 Marina Boulevard",
      "city": "Singapore",
      "postCode": "018984",
      "countryIso3": "SGP",
      "natureOfBusiness": "Commodities Trading"
    }
  }
}
```

## REFERENCE_SANCTION_HIT_SUBMISSION

Submit entity information for reference sanction hit cases. The reference sanction hit occurs when a payment reference or memo field matches against sanctions screening.

**Valid entity types:** `individual`, `organisation`, `vessel`, `multiple`, or `other` (exactly one required)

Important
For `individual` submissions, `countryOfResidenceIso3` is **REQUIRED**.

### Reference Individual

Submit information about an individual referenced in the payment.

Request Fields
type
Required. Must be `REFERENCE_SANCTION_HIT_SUBMISSION`

submissionData.individual.name
Required. Full name of the individual. Maximum length: 255 characters.

submissionData.individual.countryOfResidenceIso3
Required. ISO 3166-1 alpha-3 country code for country of residence. Exactly 3 uppercase letters. Pattern: `^[A-Z]{3}$`.

submissionData.individual.dob
Date of birth. Accepted formats: `DD/MM/YYYY` or `YYYY-MM-DD`. Maximum length: 10 characters.

submissionData.individual.nationality
Nationality of the individual. Maximum length: 100 characters.

submissionData example
```json
{
  "type": "REFERENCE_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "individual": {
      "name": "Robert Downy Jr",
      "countryOfResidenceIso3": "EGY",
      "dob": "22/08/1975",
      "nationality": "Egyptian"
    }
  }
}
```

### Reference Organisation

Submit information about an organisation referenced in the payment.

Request Fields
type
Required. Must be `REFERENCE_SANCTION_HIT_SUBMISSION`

submissionData.organisation.name
Required. Name of the organisation. Maximum length: 255 characters.

submissionData.organisation.streetAddress
Required. Street address of the organisation. Maximum length: 500 characters.

submissionData.organisation.city
Required. City where the organisation is located. Maximum length: 100 characters.

submissionData.organisation.postCode
Required. Postal code of the organisation's address. Maximum length: 20 characters.

submissionData.organisation.countryIso3
Required. ISO 3166-1 alpha-3 country code. Exactly 3 uppercase letters. Pattern: `^[A-Z]{3}$`.

submissionData.organisation.natureOfBusiness
Description of the organisation's business activities. Maximum length: 500 characters.

submissionData.organisation.website
Organisation's website URL. Must be a valid URI format. Maximum length: 500 characters.

submissionData example
```json
{
  "type": "REFERENCE_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "organisation": {
      "name": "Global Trading Partners LLC",
      "streetAddress": "1500 Commerce Street, Suite 400",
      "city": "Dubai",
      "postCode": "00000",
      "countryIso3": "ARE",
      "natureOfBusiness": "Import/Export Trading",
      "website": "https://www.globaltrading-partners.com"
    }
  }
}
```

### Reference Vessel

Submit information about a vessel referenced in the payment.

Request Fields
type
Required. Must be `REFERENCE_SANCTION_HIT_SUBMISSION`

submissionData.vessel.vesselImoNumber
Required. International Maritime Organization (IMO) number of the vessel. IMO numbers are 7-digit identifiers. Maximum length: 20 characters. Pattern: `^(IMO)?\s?\d{7}$`. Examples: `9074729`, `IMO 9074729`.

submissionData example
```json
{
  "type": "REFERENCE_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "vessel": {
      "vesselImoNumber": "9074729"
    }
  }
}
```

### Reference Multiple

Submit information when multiple entities are involved in the payment reference. Use this when the payment involves a consortium, group payment arrangement, or multiple beneficiaries.

Request Fields
type
Required. Must be `REFERENCE_SANCTION_HIT_SUBMISSION`

submissionData.multiple.explanation
Required. Explanation describing the multiple entities involved. Should include details about all parties and their relationship. Maximum length: 2,000 characters.

submissionData example
```json
{
  "type": "REFERENCE_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "multiple": {
      "explanation": "This payment reference involves a consortium of three companies: Alpha Corp (USA), Beta Ltd (UK), and Gamma GmbH (Germany). The payment is for a joint infrastructure project where funds are distributed proportionally: 40% to Alpha Corp, 35% to Beta Ltd, and 25% to Gamma GmbH."
    }
  }
}
```

### Reference Other

Submit information for entity types not covered by standard categories. Use this for government entities, NGOs, trusts, or other special entity types.

Request Fields
type
Required. Must be `REFERENCE_SANCTION_HIT_SUBMISSION`

submissionData.other.explanation
Required. Free-form explanation describing the entity. Should include the entity type, registration details, and any relevant compliance information. Maximum length: 2,000 characters.

submissionData example
```json
{
  "type": "REFERENCE_SANCTION_HIT_SUBMISSION",
  "submissionData": {
    "other": {
      "explanation": "The payment reference relates to a charitable foundation registered with the UN. The Foundation for Educational Development (FED) is a non-profit organization established in 2010, registered under Swiss law with headquarters in Geneva. Registration number: CH-660.0.000.000-1."
    }
  }
}
```

## REFERENCE_LOCATION_HIT_SUBMISSION

Submit location-related information for reference location hit cases. This occurs when a payment reference triggers a location-based compliance check.

Request Fields
type
Required. Must be `REFERENCE_LOCATION_HIT_SUBMISSION`

submissionData.other.relatedToLocation
Required. Explanation of how the reference is related to the flagged location. Maximum length: 2,000 characters.

submissionData.other.paymentExplanation
Required. Explanation of the purpose of the payment. Describe what goods or services are being paid for. Maximum length: 2,000 characters.

submissionData.other.location
Required. The specific location being addressed. Maximum length: 255 characters.

submissionData.other.referenceDescription
Required. Description of the payment reference that triggered the location hit. Maximum length: 2,000 characters.

submissionData example
```json
{
  "type": "REFERENCE_LOCATION_HIT_SUBMISSION",
  "submissionData": {
    "other": {
      "relatedToLocation": "The payment reference mentions Crimea due to historical business operations that were fully wound down in 2014.",
      "paymentExplanation": "Current payment is for consulting services rendered in London, UK.",
      "location": "Crimea, Ukraine",
      "referenceDescription": "Invoice CRM-2026-0042 - Consulting services for Q2 2026. The CRM prefix is a legacy system identifier."
    }
  }
}
```

## RECIPIENT_LOCATION_HIT_SUBMISSION

Submit location-related information for recipient location hit cases. This occurs when a recipient's location triggers a compliance check.

Request Fields
type
Required. Must be `RECIPIENT_LOCATION_HIT_SUBMISSION`

submissionData.other.relatedToLocation
Required. Explanation of how the recipient is related to the flagged location. Maximum length: 2,000 characters.

submissionData.other.paymentExplanation
Required. Explanation of the purpose of the payment. Maximum length: 2,000 characters.

submissionData.other.location
Required. The specific location being addressed. Maximum length: 255 characters.

submissionData.other.businessWebsite
Website of the recipient's business (optional). Must be a valid URI format. Maximum length: 500 characters.

submissionData example
```json
{
  "type": "RECIPIENT_LOCATION_HIT_SUBMISSION",
  "submissionData": {
    "other": {
      "relatedToLocation": "Recipient company has a branch registration in the flagged jurisdiction for administrative purposes only.",
      "paymentExplanation": "Payment for software licenses delivered electronically. Recipient's operational headquarters are in Dublin, Ireland.",
      "location": "Minsk, Belarus",
      "businessWebsite": "https://www.recipient-software.ie"
    }
  }
}
```

## Error responses

### Validation errors (400 Bad Request)

Returned when required fields are missing, field values are invalid, or the submission data structure is incorrect. The `errors` array contains field-level details with a `code`, `ref` (field name), and optional `detail`.

```json
{
  "type": "/errors/types/validation",
  "title": "Validation Error",
  "status": 400,
  "instance": "/public/v2/cases/12345678/messages",
  "errors": [
    {
      "code": "parameter_missing",
      "ref": "name",
      "detail": "name is required for individual submission"
    }
  ]
}
```

### Domain errors (409 Conflict)

Returned when the operation conflicts with the current state of the case, such as the case being in a final state, no Wise Agent being assigned, or the case not supporting the requested submission type.

```json
{
  "type": "/errors/types/domain",
  "title": "Conflict",
  "status": 409,
  "detail": "Cannot submit message for case in final state: RESOLVED",
  "instance": "/public/v2/cases/12345678/messages",
  "code": "operation_not_supported"
}
```

### Case not found (404 Not Found)

Returned when the case ID doesn't exist.

```json
{
  "type": "/errors/types/domain",
  "title": "Not Found",
  "status": 404,
  "detail": "case not found: 99999999",
  "instance": "/public/v2/cases/99999999/messages",
  "code": "resource_not_found"
}
```