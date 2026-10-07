# Relayed authorisation

Please contact your Wise sales team to use this feature

Relayed authorisation allows partners to approve or decline card transactions in real time. By forwarding authorisation requests directly to the partner, Wise enables partners to decide instantly using their own internal fraud engines or spend controls.

This feature is optional. By default, Wise manages authorisations based on your pre-configured [spend controls](/api-reference/spend-controls) and [limits](/api-reference/spend-limits). Once enabled, Wise forwards authorisation requests directly to you for real-time decisioning. To configure and activate this service, please reach out to our implementation team.

Authorisation requests for the following transaction types are not relayed to partners:

* REFUND
* ACCOUNT_CREDIT
* CREDIT_TRANSACTION


## How it works

An example of this flow is shown in the diagram below:

relayed authorisation flow
1. When a cardholder makes a payment, the scheme initiates an authorisation request and sends it to Wise.
2. Wise runs authorisation rules, internal fraud checks, and any spend controls or spend limits set by you (the partner) or end customer. If any check fails, Wise declines the transaction and does not forward the authorisation request to the partner.
3. If Wise checks pass, the request is forwarded to you, unless the transaction type is `REFUND`, `ACCOUNT_CREDIT`, or `CREDIT_TRANSACTION`.
4. You decide to approve or decline the authorisation synchronously and respond within 2s. If no response is received, Wise approves the transaction by default. The transaction data and webhook events include additional data about your decision and whether Wise made the default decision.
5. If approved, Wise reserves the funds for the transaction and forwards the authorisation response to the scheme. The request can still be declined if funds are insufficient at the balance reservation.


While card schemes such as Visa and Mastercard allow 5 to 7 seconds for authorization requests, these should be processed as rapidly as possible to ensure an optimal user experience.

Additionally, the card scheme mandates that transaction acceptance rates remain above a specific threshold. Unexplained declines cause significant customer confusion, we require partners to decline transactions only when there is a specific, valid reason.

## Required configurations

Before enabling relayed authorisation, you must provide our implementation team with an endpoint to accept relay authorisation requests. This endpoint must have an open TCP port for HTTPs traffic on port 443.

### IP whitelisting

If the partner needs to whitelist our IP addresses, please reach out to our implementation team.

## Interfaces

### Authorisation request

The request is signed and packaged in accordance with the JOSE specification, with the ES256 algorithm. Upon receiving the encoded request, you must use the [Wise public key](/api-reference/jose#get-wise-jwt-public-key) (with parameters set as `algorithm=ES256`, `version=1`, and `scope=PAYLOAD_SIGNING`) to decode and verify the request. You do not need to sign the response.

Example Request
```shell
eyJ2ZXJzaW9uIjoxLCJhbGciOiJFUzI1NiJ9.eyJjYXJkVG9rZW4iOiI2MWY1YTgzNS00OTEyLTQ5MzMtNzdjMS1kYzcyZmRmMzVmOWYiLCJ0cmFuc2FjdGlvblR5cGUiOiJQT1NfUFVSQ0hBU0UiLCJpZGVtcG90ZW5jeUlkIjoiNmY5NDQ1NzQtOWZjMC00ZjYxLWRkOTktMmVjNzBmNDhkNWU3Iiwic2NoZW1lUmVmZXJlbmNlSWQiOiI0NTkxODA3ODY3MzE5NDAiLCJ0cmFuc2FjdGlvbkFtb3VudFdpdGhGZWVzIjp7ImFtb3VudCI6MTAsImN1cnJlbmN5IjoiS1JXIn0sImJpbGxpbmdBbW91bnRXaXRoRmVlcyI6eyJhbW91bnQiOjEwLCJjdXJyZW5jeSI6IktSVyJ9LCJmZWVzIjpbXSwibWVyY2hhbnQiOnsibmFtZSI6IkFDUVVJUkVSIE5BTUUiLCJjYXRlZ29yeSI6eyJjb2RlIjoiNTQ5OSJ9LCJsb2NhdGlvbiI6eyJjb3VudHJ5IjoiZ2JyIiwiY2l0eSI6IkNJVFkgTkFNRSIsInppcENvZGUiOiIiLCJzdGF0ZSI6IiJ9fSwiY3JlYXRpb25UaW1lIjoiMjAyNi0wMS0yMlQwOTozNzo1OVoiLCJiYWxhbmNlQmVmb3JlIjp7ImFtb3VudCI6ODg1ODQ2OCwiY3VycmVuY3kiOiJLUlcifSwib3JpZ2luYWxBdXRoRGF0YSI6eyJzY2hlbWVSZWZlcmVuY2VJZCI6IjQ1OTE4MDc4NjczMTk0MCJ9LCJwcm9wZXJ0aWVzIjp7ImlzSW5jcmVtZW50YWxSZXF1ZXN0IjpmYWxzZX19.brhggeprEzT0wnq8j3Ed4qVAoM7uILudVE68WEGK0Tlhz3A1g0B_VBWro9LGyjH8ckyiiR5G8su2wh-2smYGrA
```

After receiving and verifying the signature, you can decode the payload into its standard JSON format.

Example Request
```shell
Header:
{ 
  "version": 1,
  "alg": "ES256"
}

Body:
{
  "cardToken": "61f5a835-4912-4933-77c1-dc72fdf35f9f",
  "transactionType": "POS_PURCHASE",
  "idempotencyId": "6f944574-9fc0-4f61-dd99-2ec70f48d5e7",
  "schemeReferenceId": "459180786731940",
  "transactionAmountWithFees": {
    "amount": 10,
    "currency": "KRW"
  },
  "billingAmountWithFees": {
    "amount": 10,
    "currency": "KRW"
  },
  "fees": [],
  "merchant": {
    "name": "ACQUIRER NAME",
    "category": {
      "code": "5499"
    },
    "location": {
      "country": "gbr",
      "city": "CITY NAME",
      "zipCode": "",
      "state": ""
    }
  },
  "creationTime": "2026-01-22T09:37:59Z",
  "balanceBefore": {
    "amount": 8858468,
    "currency": "KRW"
  },
  "originalAuthData": {
    "schemeReferenceId": "459180786731940"
  },
  "properties": {
    "isIncrementalRequest": false
  }
}
```

The header simply identifies the algorithm and key version used for signing. The request body contains the following fields:

Authorisation Request
cardToken
Card token

transactionType
[Type](/api-reference/card-transaction#type) of the transaction

idempotencyId
Unique ID of authorisation request. Use this field to detect duplicate requests should they occur

schemeReferenceId
A unique identifier used to track a transaction within a specific payment network, or "scheme," like Visa or Mastercard

transactionAmountWithFees
Transaction amount + Wise ATM or account funding fees

billingAmountWithFees
Billing amount + Wise ATM or account funding fees

fees[n].amount
Fee amount

fees[n].currency
Currency code

fees[n].feeType
Fee type

merchant.name
Merchant name

merchant.category.code
Merchant category code

merchant.location.country
Merchant country

merchant.location.city
Merchant city

merchant.location.zipCode
Merchant ZIP code

merchant.location.state
Merchant state

creationTime
Authorisation request time (ISO 8601 format)

balanceBefore
Available balance converted to billing currency, excluding any conversion fees

originalAuthData.schemeReferenceId
Linked original transaction data for handling incremental authorisation

properties.isIncrementalRequest
Whether it is an incremental authorisation request (updating amount of an existing transaction)

### Authorisation response

You should respond with a 200 status code for both approved and declined transactions. The response should not be signed. A responseCode must be included in the response body, using one of the following codes:

* `APPROVED`: approves the transaction. All other codes decline the transaction.
* `PROCESSING_ERROR`
* `NON_SUPPORTED_CURRENCY`
* `NON_SUPPORTED_MCC_FOR_COUNTRY`
* `BLOCKED_COUNTRY`
* `TRANSACTION_TYPE_NOT_SUPPORTED`
* `SUSPECTED_FRAUD`


Example Response
```
{
  "responseCode": "APPROVED"
}
```

### Transaction webhook and object

You can retrieve the result of your authorisation decision in the returned [Transaction object](/api-reference/card-transaction) in API and [card transaction webhook](/api-reference/webhook-event/eventcardstransactionstatechange). These will both include a `relayAuthorisationData` (`relay_authorisation_data` for webhook) block that includes:

* `responseCode`  if provided
* `fallback` indicating whether there was a fallback applied by Wise


If authorisation relay is not enabled in your integration, `relayAuthorisationData` will always be null and can be ignored.

If you (the partner) approved the transaction but it was ultimately declined by insufficient funds, the `relayAuthorisationData.responseCode` would be `APPROVED`, though the transaction is declined with declineReason as `INSUFFICIENT_FUNDS`.

In rare cases of internal system issues in Wise, it is possible that you (the partner) responded but Wise still applied a fallback. In this case, the `relayAuthorisationData.responseCode` would be `null` and `relayAuthorisationData.fallback` would be `true`.