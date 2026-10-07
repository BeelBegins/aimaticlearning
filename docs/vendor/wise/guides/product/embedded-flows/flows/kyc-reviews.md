# KYC reviews

This flow allows for a KYC review to be completed. Provide an ID for an existing review and then your users can utilise Wise's frontend, validation, and verification.

- Full reference: [KYC review link request](/api-reference/link-requests/kycreviewsembeddedlinkrequestcreate)
- Webhook reference: [KYC review state changed](/api-reference/webhook-event/eventkycreviewsstatechange)


## Completed flow data

When this flow is completed, you receive the finished KYC review ID via `postMessage` or query parameters.

View the [implementation guide](/guides/product/embedded-flows) for how to best access this data.

| Parameter name | Type | Description |
|  --- | --- | --- |
| `kycReviewId` | string (UUID) | The ID of the KYC review that has been completed. |