# Case handling

Receive requests for information, respond, and raise cases yourself.

Wise may need more information before a transfer or account-related process can continue. For Enterprise partners, this can relate to your own transfer or account. For Embedded solutions or Correspondent partners, this can relate to your customers’ transfers or accounts. Use the cases service to resolve cases faster, reduce delays for you and your customer, and improve customer experience.

With the cases service, you can:

- Receive RFIs.
- Submit required information.
- Upload supporting documents.
- Track a case and its message history.
- Automate case handling processes.
- Raise cases with us from your own operations or support tooling.
- Build your own customer or operations experience for handling these requests.


Cases can be created automatically by us, manually by our support team, or by you through the Wise API. A case can contain either structured messages that you can parse and act on, or freeform messages from our support team.

Case handling is in beta. Contact your account team before building with these endpoints.

## Case handling flows

We offer two case handling flows.

| Flow | Description |
|  --- | --- |
| Respond to RFIs | We open a case when we need more information from you or your customer. You receive a webhook event, review what we need, collect and submit the information, and track the case until it is resolved. This flow is for non-onboarding RFIs. |
| Raise cases with Wise | You open a case when you need us to review or answer a support or operations query. You can add comments, retrieve case updates, and track changes through webhooks. |


If you are an Embedded solutions partner onboarding customers, see the [Onboarding & KYC guide](/guides/product/kyc) for onboarding verification requests.

### Respond to RFIs

A request for information, or RFI, occurs when we need more information before proceeding with a transfer or account-related process.

We can send RFIs in two ways:

- **Automated RFIs**: We send a request with the data fields you need to submit. You parse these fields, collect the required information from your records or your customer, and submit the response to us.
- **Freeform RFIs**: Our support team sends a message explaining what information is needed. This can happen when the request is not automated or when we need more information after reviewing your response.


If we request documents, you can upload files and link them to the case using the returned file IDs.

To build these flows, see the [Respond to RFIs guide](/guides/product/partner/respond-to-rfis).

### Raise cases with Wise

Raise a case when you need us to review or answer a support or operations query.

Use this flow to communicate with our support team in a structured, secure way from your own backend tooling. You can create a case, retrieve the latest case status, add comments, and receive webhook events when the case changes.

## Webhook for case changes

Subscribe to the `partner-support#case-changed` event type to receive case updates.
You must create an [application webhook subscription](/api-reference/webhook/webhookapplicationsubscriptioncreate) and set the `trigger_on` value to `partner-support#case-changed`. The notification tells you when we need information from you or your customer, what information we need, when we are reviewing your response, and when the case is resolved or fails.

Use webhook event notifications as the trigger for your case handling workflow. You can then retrieve the case details, read the latest messages, and decide what action to take.