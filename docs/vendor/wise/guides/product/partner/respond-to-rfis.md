# Respond to RFIs

Receive, respond to, and track requests for information.

A request for information, or RFI, occurs when we need more information from you or your customer.

We can send RFIs in two ways:

- **Automated RFIs**: We send a request with structured data that you can parse and respond to programmatically.
- **Freeform RFIs**: Our support team sends a message explaining what information is needed. These requests may need manual review by your operations or support team.


Use the cases service to receive requests and respond to them programmatically. Automating parts of the case handling process reduces delays for you or your customers and minimises the risk of transfer cancellations.

Case handling is in beta. Contact your account team before building with these endpoints.

## Supported automated RFI types

Automated RFIs include structured messages that tell you what information we need. Currently, we support only automated sanctions requests.

Do not show internal case `type` or `subType` values directly to your customer. Use neutral wording, such as *we need more information to process your transfer*.

### Sanctions requests

Sanctions screening helps us ensure compliance by checking whether a transfer may involve a restricted person, organisation, country, or region.

We send this type of request if there is a potential sanctions match for a transfer and we need more information to assess it.

For sanctions requests, you must respond within **seven calendar days** from when we send the request. If you do not respond in time, the related transfer may be cancelled.

The case may remain open after seven days if you are actively communicating with us to obtain all required information.

## Before you begin

Before you build an RFI handling flow:

- Confirm that your integration has access to [case endpoints](/api-reference/case) and [file endpoints](/api-reference/case-files/casefileupload).
- Subscribe to the `partner-support#case-changed` [webhook event type](/api-reference/case/eventpartnersupportcasechanged).
- Decide whether you can answer RFIs automatically from existing data, or whether you need to collect information from your customer.
- Build a process to route freeform requests to your operations or support team.


## RFI handling process

Follow these steps to respond to an RFI.

### Step 1: Check the case status

When you receive a `partner-support#case-changed` [webhook event](/api-reference/case/eventpartnersupportcasechanged), check the case `status`. If the status is `WAITING_CUSTOMER_INPUT`, we need information from you or your customer.

### Step 2: Identify the affected resource

Use the case fields to understand what the RFI is about.

| Property | Type | Description |
|  --- | --- | --- |
| `type` | Enum string | The high-level reason for the case. |
| `subType` | Enum string | The more specific reason for the case. |
| `reference.type` | Enum string | The type of resource that the case relates to. This is usually `TRANSFER`. |
| `reference.referenceId` | String | The ID of the resource that the case relates to. For `TRANSFER`, this is the transfer ID. |
| `messages` | Array | The message history for the case. Use this to find the latest request from us and any previous responses. |


Design your integration to read `reference.type` before using `reference.referenceId`. This helps you support other reference types if they are added later.

Request
```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/cases/12345678 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Response
```json 200 application/json
{
  "id": 485,
  "profileId": 220002553,
  "type": "SANCTIONS",
  "subType": "REFERENCE_SANCTION_HIT",
  "status": "RESOLVED",
  "externalId": null,
  "createdAt": "2026-07-29T16:06:06.003",
  "updatedAt": "2026-07-29T16:09:32.998",
  "reference": {
    "type": "TRANSFER",
    "referenceId": "2147513101"
  },
  "messages": [
    {
      "id": "67631430-77fd-4bbb-a8e0-fdfa67563d66",
      "caseId": 485,
      "createdAt": "2026-07-29T16:06:06.014",
      "content": {
        "attributes": {
          "business": {
            "name": {
              "type": "String",
              "required": true
            },
            "address": {
              "type": "Address",
              "required": true
            },
            "natureOfBusiness": {
              "type": "String",
              "required": false
            },
            "website": {
              "type": "String",
              "required": false
            }
          },
          "vessel": {
            "imoNumber": {
              "type": "String",
              "required": true
            }
          },
          "other": {
            "explanation": {
              "type": "String",
              "required": true
            }
          },
          "individual": {
            "name": {
              "type": "String",
              "required": true
            },
            "dob": {
              "type": "LocalDate",
              "required": false
            },
            "countryOfResidenceIso3": {
              "type": "String",
              "required": false
            },
            "nationality": {
              "type": "String",
              "required": false
            }
          }
        }
      },
      "type": "REFERENCE_SANCTION_HIT_REQUEST",
      "author": "WISE_SYSTEM"
    },
    {
      "id": "8c08894d-1e62-45c4-8332-cd1565916273",
      "caseId": 485,
      "createdAt": "2026-07-29T16:08:14.308",
      "content": {
        "submissionData": {
          "individual": {
            "name": "Mr. Robert Downy Junior",
            "countryOfResidenceIso3": "GBR"
          }
        }
      },
      "type": "REFERENCE_SANCTION_HIT_SUBMISSION",
      "author": "PARTNER"
    }
  ]
}
```

```json 401 application/json
{
  "type": "/errors/types/access",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required"
}
```

```json 403 application/json
{
  "type": "/errors/types/access",
  "title": "Forbidden",
  "status": 403,
  "detail": "Unauthorized",
  "code": "forbidden"
}
```

```json 404 application/json
{
  "type": "/errors/types/domain",
  "title": "Not Found",
  "status": 404,
  "detail": "case not found: 12345678",
  "instance": "/public/v2/cases/12345678",
  "code": "resource_not_found"
}
```

```json 429 application/json
{}
```

### Step 3: Identify what we need

Check the latest message from us in the `messages` array.

Read the message's `type` to understand what we need. A case can include both structured and freeform messages over time, so always check the latest message and its `content` before responding.

Structured messages include an `attributes` object. The `attributes` object tells you what information and/or supporting documents we need.

For some requests, `attributes` can include more than one response option. Each option represents a different entity type, such as an individual or business.

Choose the option that matches the entity you are providing information about, then submit the fields in that option.

If a field is marked as required for the option you choose, you must submit it before Wise can review the case. If the request includes optional fields, we recommend submitting them with the required fields.

### Step 4: Collect and submit the information

Use information and documents that you already hold, or collect them from your customer through your own application or support flow. Submit your response based on what we requested.

- For automated requests, respond with the matching submission type and include the required fields using [the case message endpoint](/api-reference/case/casesubmitmessage).
- For freeform requests, respond with a `FREEFORM` case message using [the case message endpoint](/api-reference/case/casesubmitmessage).
- For document requests, upload each file using [the file endpoint](/api-reference/case-files/casefileupload). Submit the returned `fileId` in a `FILE_SUBMISSION` message to attach the file to the case using [the case message endpoint](/api-reference/case/casesubmitmessage).


Case message request
```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/cases/12345678/messages \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "FREEFORM",
    "submissionData": {
      "freeText": "The transfer has been verified and approved by our compliance team."
    }
  }'
```

Case message response
```json 201 application/json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "caseId": 12345678,
  "createdAt": "2026-07-27T15:00:00.000",
  "content": {
    "text": {
      "freeText": "The transfer has been verified and approved by our compliance team."
    }
  },
  "type": "FREEFORM",
  "author": "PARTNER"
}
```

```json 400 application/json
{
  "type": "/errors/types/validation",
  "title": "Validation Error",
  "status": 400,
  "instance": "/public/v2/cases/12345678/messages",
  "errors": [
    {
      "code": "parameter_missing",
      "ref": "type",
      "detail": null
    }
  ]
}
```

```json 401 application/json
{
  "type": "/errors/types/access",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required"
}
```

```json 403 application/json
{
  "type": "/errors/types/access",
  "title": "Forbidden",
  "status": 403,
  "detail": "Unauthorized",
  "code": "forbidden"
}
```

```json 404 application/json
{
  "type": "/errors/types/domain",
  "title": "Not Found",
  "status": 404,
  "detail": "case not found: 12345678",
  "instance": "/public/v2/cases/12345678/messages",
  "code": "resource_not_found"
}
```

```json 409 application/json
{
  "type": "/errors/types/domain",
  "title": "Conflict",
  "status": 409,
  "detail": "Cannot submit message for case in final state: RESOLVED",
  "instance": "/public/v2/cases/12345678/messages",
  "code": "operation_not_supported"
}
```

```json 429 application/json
{}
```

File request
```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/cases/files \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: multipart/form-data' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -F file=string \
  -F 'submissionData={"profileId":14556049,"purpose":"GENERAL"}'
```

File response
```json 201 application/json
{
  "profileId": 14556049,
  "fileId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "fileName": "company-registration.pdf"
}
```

```json 400 application/json
{
  "type": "/errors/types/validation",
  "title": "Validation Error",
  "status": 400,
  "instance": "/cases/files",
  "errors": [
    {
      "code": "parameter_missing",
      "ref": "profileId",
      "detail": "profileId must be provided"
    }
  ]
}
```

```json 401 application/json
{
  "type": "/errors/types/access",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication required"
}
```

```json 403 application/json
{
  "type": "/errors/types/access",
  "title": "Forbidden",
  "status": 403,
  "detail": "Unauthorized",
  "code": "forbidden"
}
```

```json 429 application/json
{
  "type": "/errors/types/domain",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Too many files uploaded recently. Please try again later.",
  "instance": "/cases/files",
  "code": "rate_limit_exceeded"
}
```

```json 500 application/json
{
  "type": "/errors/types/internal",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred. Please try again later.",
  "instance": "/cases/files"
}
```

### Step 5: Track case status changes

We review the submitted information and send another `partner-support#case-changed` webhook event to indicate the case has been resolved or needs more information.

Use the latest case status and message to decide what to do next.

| Status | Description | What to do next |
|  --- | --- | --- |
| `WAITING_CUSTOMER_INPUT` | We need more information from you or your customer before the case can continue. The case can also return to this status if we review submitted information and need more details. | Check the latest message in the `messages` array, collect the requested information, and submit another case message. |
| `IN_REVIEW` | We have received the submitted information and are reviewing it. | No action is needed. |
| `RESOLVED` | The case is closed and we do not need more information for this case. This does not always mean the related transfer or account-related request was successful. | No more action is needed on this case. Use `reference.type` and `reference.referenceId` to check status of the related resource. For example, if `reference.type` is `TRANSFER`, use the transfer ID in `reference.referenceId` to [check the transfer status](/api-reference/transfer/transferget). |