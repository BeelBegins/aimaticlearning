# Test and prepare to go live

Testing directly over the real payment rails is complex and can be slow and expensive. The Wise Platform [Sandbox environment](/guides/developer/environments#sandbox-environment) allows you to test your integration end-to-end by simulating incoming payments without actual money movement.

The Sandbox environment supports simulation for both [Wise-issued Local Account Details](#simulate-local-account-details) and [International Receive via connected BIC](#simulate-swift). Each simulation triggers the same webhook events and API responses you will encounter in production, allowing you to verify your full integration before going live.

## What to verify during testing 

Regardless of the payment rail you are testing, your integration should be verified end-to-end against the following steps:

1. **Webhook delivery**: Confirm that your webhook endpoint receives the `incoming-transfer#credited` event after the simulated payment is processed.
2. **Payload parsing**: Verify that your integration correctly extracts the `data.incoming_transfer_id` field of the webhook payload.
3. **Transfer detail retrieval**: Confirm that calling `GET /v1/incoming-transfers/{incomingTransferId}` returns a complete transfer record with the expected fields — amount, currency, debtor details, debtor bank details, and clearing identifiers.
4. **Customer identification**: Verify that your integration correctly identifies the receiving customer by matching the account details in the transfer record to your internal records.
5. **Reconciliation**: Confirm that the credited amount and value date are correctly recorded in your internal ledger.


If you have subscribed to legacy webhook events (`swift-in#credit`, `swift#message-received`) in addition to `incoming-transfer#credited`, verify that your integration handles all subscribed events correctly and without duplication.

## Simulate payment into Wise-issued account details 

Use the following endpoint in the Sandbox environment to simulate an incoming payment to a set of Wise-issued Local Account Details (IBAN, sort code and account number, routing and account number, etc.).

The simulation triggers the full credit processing pipeline, including balance update and `incoming-transfer#credited` webhook delivery, in the same way as a real incoming payment over the corresponding local rail (SEPA, Faster Payments, ACH, etc.).

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/simulation/profiles/{profileId}/bank-transactions/import' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "currency": "USD",
    "amount": 2000
  }'
```

For the full list of supported parameters, currency-specific constraints, and error responses, see the [API reference](/api-reference/simulation/simulationbanktransactionimport).

### What to check after simulation

After triggering a simulation, verify the following:

- Your webhook endpoint receives an `incoming-transfer#credited` event within a few seconds.
- The `incoming_transfer_id` in the webhook payload can be used to successfully retrieve the transfer record from the Incoming Transfers API.
- The simulated debtor name, amount, and currency are reflected correctly in the transfer record.
- The `accountDetailsId` field in the transfer record matches the Local Account Details you simulated the payment to.


## Simulate incoming Swift payment to connected BIC 

Use the following endpoint in the Sandbox environment to simulate an incoming Swift message to your connected BIC. This allows you to verify your end-to-end integration for the International Receive flow, including Swift message processing, credit notification, and transfer detail retrieval.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/simulation/profiles/{profileId}/swift-in' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "currencyCode": "EUR",
    "amount": 100
  }'
```

For request/response details and the list of supported Swift message types, see the [API reference](/api-reference/simulation/simulationswiftin).

### What to check after simulation

After triggering a Swift simulation, verify the following:

- Your webhook endpoint receives an `incoming-transfer#credited` event.
- If you are subscribed to `swift#message-received`, verify that the event is also received and that `data.resource.content` contains a valid Base64-encoded PACS message of the expected type (e.g. `pacs.008.001.08`).
- The `incoming_transfer_id` from the `incoming-transfer#credited` payload can be used to retrieve the full transfer record, including Swift-specific fields such as debtor bank BIC, LEI, and Clearing System Member ID where applicable.
- If you are subscribed to the legacy `swift-in#credit` event, verify it is received and that the Swift transaction reference in the payload matches the simulated payment.


## Going live with Swift configuration 

Once configuration and Sandbox testing is complete, you will need to update your Standing Settlement Instructions (SSI) to point your production BIC to the Wise BIC. This is a mandatory step to ensure that live Swift payments sent to your BIC are correctly routed to Wise for processing.

It is also strongly recommended that you notify other members of the Swift network that your SSI has been updated. Without this notification, correspondent banks may continue routing payments using outdated instructions, which can result in delays or misrouted payments.

Notification to the Swift network is done through an MT670 message sent directly to Swift. Wise will need to send this message on your behalf — coordinate with your Wise implementation manager to initiate this step at the appropriate time in your go-live process.

Do not update your production SSI until you have fully completed Sandbox testing and received sign-off from your Wise implementation manager. Premature SSI updates can disrupt live payment routing for your existing customers.