# Payment instrument

This flow allows for direct debit mandate collection to take place and for payment instrument creation for that given method. These flows are up-to-date with local guidance and are fully compliant with the regulations set out for each method.

- Full reference: [Payment instrument link request](/api-reference/link-requests/paymentinstrumentembeddedlinkrequestcreate)
- Webhook reference: [Payment instrument state changed](/guides/product/send-money/funding/direct-debit/create-payment-instrument#webhook-payload-fields)


## Completed flow data

When this flow is completed, you receive the created payment instrument ID via `postMessage` or query parameters.

View the [implementation guide](/guides/product/embedded-flows) for how to best access this data.

| Parameter name | Type | Description |
|  --- | --- | --- |
| `paymentInstrumentId` | string (UUID) | The ID of the payment instrument created. |