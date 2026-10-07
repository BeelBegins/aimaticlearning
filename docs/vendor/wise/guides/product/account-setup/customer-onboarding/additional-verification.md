# Additional customer verification

In certain situations, additional evidence is required to complete customer verification and ensure compliance with KYC regulations.

Based on Wise.com average customer base, most customers do not need to provide documents or additional information after the initial upload-evidences information is submitted.

## Summary of steps

1. Subscribe to the [additional verification state change event](/api-reference/webhook-event/eventprofilescddcheckstatechange) webhook to receive updates about your customers' additional verification status.
2. Fetch the required evidence for a profile using the [required evidences endpoint](/api-reference/verification/verificationgetrequiredevidences).
3. Submit text-based, structured evidence (i.e., non-document) using the [Upload evidences endpoint](/api-reference/verification/verificationuploadevidences).
4. Upload required documents using the [Upload document endpoint](/api-reference/verification/verificationuploaddocument).


### Subscribe to state change webhook

Subscribe to [additional verification state change event](/api-reference/webhook-event/eventprofilescddcheckstatechange) webhook to receive updates about your customers' additional verification status. This webhook will also inform you if any further evidence or documents are required to complete the review.

### Fetch required evidence

Send a request to the [Required evidences endpoint](/api-reference/verification/verificationgetrequiredevidences) to determine what evidence is required for a profile to complete the additional customer verification.

If one or more evidences are returned, gather that evidence from your customer and submit using the [Upload evidences endpoint](/api-reference/verification/verificationuploadevidences).

### Submit evidence

During onboarding, customers need to provide additional evidence that is then submitted via the [Upload evidences endpoint](/api-reference/verification/verificationuploadevidences).

We use this to perform an initial automated check before either verifying the customer, or requesting more information. Successful verification is returned within a few seconds. Unsuccessful verification creates a case for our team to review, so it can take longer to receive an update.

### Upload documents

Provide those additional evidence by using [Upload document endpoint](/api-reference/verification/verificationuploaddocument).

You can upload multiple files at once.

A valid document must fulfil these requirements:

- The document must be clear.
- The document needs to be a .jpg, .png, or .pdf file type up to 10MB in size.


### Monitor webhook payloads

[Create an application webhook subscription](/api-reference/webhook/webhookapplicationsubscriptioncreate) for the `profiles#cdd-check-state-change` event type.

Sample payload:

```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "profiles#cdd-check-state-change",
  "sent_at": "2026-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "type": "profile",
      "id": 111
    },
    "current_state": "VERIFIED",
    "review_outcome": "DOCUMENT_OUT_OF_DATE",
    "required_evidences": [
      "SOURCE_OF_INCOME"
    ],
    "occurred_at": "2026-01-01T12:34:56.789Z",
    "source_of_income": "INVESTMENTS",
    "source_of_funding": "REVENUE"
  }
}
```