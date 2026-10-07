# Recipient creation

This flow allows for recipient creation against a given profile. It includes validation of details for multiple account types, as well as a limited set of validation against other account types (i.e., GBP).

- Full reference: [Recipient creation link request](/api-reference/link-requests/recipientembeddedlinkrequestcreate)
- Webhook reference: [Recipient state changed](/api-reference/webhook-event/eventrecipientsstatechange)


## Completed flow data

When this flow is completed, you receive the created recipient ID via `postMessage` or query parameters.

View the [implementation guide](/guides/product/embedded-flows) for how to best access this data.

| Parameter name | Type | Description |
|  --- | --- | --- |
| `recipientId` | number | The ID of the recipient created against the given profile. |