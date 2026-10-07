# Payment instruments

Payment instruments represent saved funding sources, like a customer's bank account, that enable automated direct debit payins to fund transfers without requiring the payer to be present.

To set up a payment instrument, you must:

1. **Create** the payment instrument.
2. **Connect** the payment instrument.


## Supported schemes

| Scheme | Currency | Region | Status |
|  --- | --- | --- | --- |
| BACS | GBP | United Kingdom | Live |
| SEPA | EUR | Europe | Live |
| ACH | USD | United States | Beta |
| EFT | CAD | Canada | Beta |


**ACH** and **EFT** support is currently in beta. While fully functional and supported, the API may undergo changes based on partner feedback.

## Create a new payment instrument 

Before you begin, note that the create new payment instrument response returns a `PENDING` status, indicating it is not yet ready for use.

After creation, **you must complete authorization with your customer and use the manual confirmation endpoint to activate it**.

### Endpoint

```
POST /profiles/{profileId}/payment-instruments
```

### Path parameters

| Parameter | Type | Required? | Description |
|  --- | --- | --- | --- |
| `profileId` | integer | Yes | Your personal or business profile ID. |


### Request body

The request body fields vary by scheme. The following table provides scheme-specific requirements:

**Key**: ✅ Required | ⚪ Optional | ❌ Not Supported

| Field | Type | BACS | SEPA | ACH (beta) | EFT (beta) |
|  --- | --- | --- | --- | --- | --- |
| `type` | string | ✅ | ✅ | ✅ | ✅ |
| `accountNumber` | string | ✅ | ✅ | ✅ | ✅ |
| `accountHolderName` | string | ⚪ | ⚪ | ⚪ | ⚪ |
| `branchCode` | string | ✅ | ❌ | ❌ | ❌ |
| `bankCode` | string | ❌ | ❌ | ✅ | ✅ |
| `accountType` | string | ❌ | ❌ | ✅ | ✅ |
| `reference` | string | ⚪ | ⚪ | ❌ | ❌ |
| `accountOwnerDetails.email` | string | ✅ | ✅ | ⚪ | ⚪ |


#### Field descriptions

- `type`: Scheme type are `BACS`, `SEPA`, `ACH`, or `EFT`.
- `accountNumber`: Bank account number. For SEPA, this is the IBAN.
- `accountHolderName`: Account holder name. Defaults to associated business profile's company name if not provided.
- `branchCode`: UK sort code (format: `XX-XX-XX`). Required for BACS only.
- `bankCode`: Bank identifier code. For ACH, provide the 9-digit ABA routing number. For EFT, provide the 9-character routing number (institution + transit). Required for ACH and EFT.
- `accountType`: Account types are `CHECKING` or `SAVINGS`. Required for ACH and EFT.
- `reference`: This field behaves differently based on the currency, and may end up on the debtor's bank statement. See currency examples below for more details.
- `accountOwnerDetails.email`: Email for sending mandate creation notification and advanced payment notices. Required for BACS and SEPA.


**Account numbers** in responses are masked for security.

- **BACS** masks all but the last 4 digits with `XXXX` (ex: `XXXX5678`).
- **SEPA** masks all but the last 4 with multiple `X's` (ex: `XXXXXXXXXXXXXXXX5685`).
- **ACH**/**EFT** mask all but the last 4 with `******` (ex: `******6789`).


## Examples by scheme 

### BACS (United Kingdom - GBP)

Example request
```json
{
  "type": "BACS",
  "accountHolderName": "John Smith",
  "accountNumber": "12345678",
  "branchCode": "00-00-00",
  "reference": "REFERENCE01",
  "accountOwnerDetails": {
    "email": "test@email.com"
  }
}
```

Example response
```json
{
  "id": "6713050b-e64f-4da7-0770-5b0583f81739",
  "type": "BACS",
  "status": "PENDING",
  "bankName": "BARCLAYS BANK PLC",
  "bankCode": null,
  "branchCode": "00-00-00",
  "accountNumber": "XXXX5678",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "GB",
    "state": null,
    "city": "London",
    "postCode": "EC2A 4JE",
    "firstLine": "65 Clifton St"
  },
  "reference": "REFERENCE01"
}
```

#### BACS reference constraints

If you are sending `reference` values, then you must adhere to the following constraints:

| Length (Characters) | Rules |
|  --- | --- |
| **Minimum**: 6 chars**Maximum**: 18 chars | - Only alphanumeric **(a-z, A-Z, 0-9)**; exclude special characters- No leading or trailing spaces- Must not start with **“DDIC”**- Must not contain all the same characters |


Reference constraints
If you are sending custom references when creating BACS payment instruments or payments, then also check the combined [reference constraints](/guides/product/send-money/funding/direct-debit/mandates-standards#bacs-constraints).

### SEPA (Europe - EUR)

Example request
```json
{
  "type": "SEPA",
  "accountHolderName": "John Smith",
  "accountNumber": "EE382200221020145685",
  "reference": "REFERENCE01",
  "accountOwnerDetails": {
    "email": "test@email.com"
  }
}
```

Example response
```json
{
  "id": "c1dca180-2939-461b-913c-d9638e6a93ee",
  "type": "SEPA",
  "status": "PENDING",
  "bankName": "SWEDBANK AS",
  "bankCode": null,
  "branchCode": null,
  "accountNumber": "XXXXXXXXXXXXXXXX5685",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "EE",
    "state": null,
    "city": "Tallinn",
    "postCode": "10135",
    "firstLine": "Veerenni tn 24"
  },
  "reference": "REFERENCE01"
}
```

#### SEPA reference constraints

If you are sending `reference` values, then you must adhere to the following constraints:

| Length (Characters) | Rules |
|  --- | --- |
| **Maximum**: 35 chars | - Alphanumeric **(a-z, A-Z, 0-9)**- Special symbols `/ - ? : ( ) & . , '` and a space- Characters can repeat |


Reference constraints
If you are sending custom references when creating SEPA payment instruments or payments, then also check the [reference constraints](/guides/product/send-money/funding/direct-debit/mandates-standards#sepa-constraints).

### ACH (United States - USD)

ACH support is currently in beta.
The API is stable and production-ready, but may change without notice.

Example request
```json
{
  "type": "ACH",
  "accountHolderName": "John Smith",
  "accountNumber": "123456789",
  "bankCode": "026009593",
  "accountType": "CHECKING"
}
```

Example response
```json
{
  "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "type": "ACH",
  "status": "PENDING",
  "bankName": "Bank of America",
  "bankCode": "026009593",
  "branchCode": null,
  "accountNumber": "******6789",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "US",
    "state": "NY",
    "city": "New York",
    "postCode": "10001",
    "firstLine": "123 Main Street"
  },
  "reference": null
}
```

#### Key differences from BACS/SEPA

- ✅ Requires `bankCode` field with 9-digit ABA routing number.
- ✅ Requires `accountType` field (`CHECKING` or `SAVINGS`).
- ❌ `reference` field not supported. Use `details.reference` in the [transfer request](/api-reference/standard-transfer/transfercreate) instead to customize the bank statement reference.
- ⚪ Email optional (authorization via IAV, micro-deposits, or trusted partner integration).


### EFT (Canada - CAD)

EFT support is currently in beta.
The API is stable and production-ready but may change without notice.

Example request
```json
{
  "type": "EFT",
  "accountHolderName": "John Smith",
  "accountNumber": "987654321",
  "bankCode": "000100210",
  "accountType": "SAVINGS"
}
```

Example response
```json
{
  "id": "f1e2d3c4-b5a6-4978-8c9d-0e1f2a3b4c5d",
  "type": "EFT",
  "status": "PENDING",
  "bankName": "Royal Bank of Canada",
  "bankCode": "000100210",
  "branchCode": null,
  "accountNumber": "******4321",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "CA",
    "state": "ON",
    "city": "Toronto",
    "postCode": "M5H 2N2",
    "firstLine": "100 King Street West"
  },
  "reference": null
}
```

#### Key differences from BACS/SEPA

- ✅ Requires `bankCode` field with 9-character routing number (institution + transit).
- ✅ Requires `accountType` field (`CHECKING` or `SAVINGS`).
- ❌ `reference` field not supported. Use `details.reference` in the [transfer request](/api-reference/standard-transfer/transfercreate) instead to customize the bank statement reference.
- ⚪ Email optional (authorization via IAV, micro-deposits, or trusted partner integration).


## Connect payment instrument

This step activates the payment instrument after completing authorization with the customer.

The payment instrument's status changes from `PENDING` to `CONNECTED`, indicating you can now use it to initiate Payins.

Important!
Only call this endpoint **after** you have obtained proper authorization from your customer according to scheme requirements listed below. This action confirms to Wise that you have followed all scheme rules.

### Endpoint

```
POST /profiles/{profileId}/payment-instruments/{paymentInstrumentId}/manual-confirmation
```

### Authorization requirements by scheme

| Scheme | Authorization method |
|  --- | --- |
| **BACS/SEPA** | Mandate document obtained and stored per scheme rules. |
| **ACH/EFT** | One of: IAV (Plaid/Yodlee/Flinks), Micro-deposits, Trusted partner integration. |


### Path parameters

| Parameter | Type | Required? | Description |
|  --- | --- | --- | --- |
| `profileId` | integer | Yes | Your personal or business profile ID. |
| `paymentInstrumentId` | uuid | Yes | Payment instrument ID from creation response. |


### Response examples

BACS connected
```json
{
  "id": "6713050b-e64f-4da7-0770-5b0583f81739",
  "type": "BACS",
  "status": "CONNECTED",
  "bankName": "BARCLAYS BANK PLC",
  "bankCode": null,
  "branchCode": "00-00-00",
  "accountNumber": "XXXX5678",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "GB",
    "state": null,
    "city": "London",
    "postCode": "EC2A 4JE",
    "firstLine": "65 Clifton St"
  },
  "reference": "REFERENCE01"
}
```

ACH connected
🟡 In BETA

```json
{
  "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "type": "ACH",
  "status": "CONNECTED",
  "bankName": "Bank of America",
  "bankCode": "026009593",
  "branchCode": null,
  "accountNumber": "******6789",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "US",
    "state": "NY",
    "city": "New York",
    "postCode": "10001",
    "firstLine": "123 Main Street"
  },
  "reference": null
}
```

## Get payment instrument

The get payment instrument operation retrieves details of a specific payment instrument.

Wise also exposes updates to the payment instrument via the `payment-instruments#status-change` webhook. See the [Webhooks](#webhooks) section below for more details.

### Endpoint

```
GET /profiles/{profileId}/payment-instruments/{paymentInstrumentId}
```

### Path parameters

| Parameter | Type | Required? | Description |
|  --- | --- | --- | --- |
| `profileId` | integer | Yes | Your personal or business profile ID. |
| `paymentInstrumentId` | uuid | Yes | Payment instrument ID. |


### Response

The response returns the payment instrument object with the current status. It uses the same structure as the [create payment instrument response](#create-payment-instrument-examples).

### Payment instrument statuses

| Status | Description |
|  --- | --- |
| `PENDING` | Awaiting manual confirmation. |
| `CONNECTED` | Authorised and ready for payin creation. |
| `DISCONNECTED` | No longer authorised (due to failure or manual disconnection). Cannot be used for payins. |


## Disconnect payment instrument

Disconnecting deactivates a payment instrument and changes the status to `DISCONNECTED`.

On disconnecting via API, Wise returns the disconnect reason as `MANUALLY_DISCONNECTED`. See the [Disconnect reasons](#disconnect-reasons) section below for more details.

### Endpoint

```
POST /profiles/{profileId}/payment-instruments/{paymentInstrumentId}/disconnection
```

### Path parameters

| Parameter | Type | Required? | Description |
|  --- | --- | --- | --- |
| `profileId` | integer | Yes | Your personal or business profile ID. |
| `paymentInstrumentId` | uuid | Yes | Payment instrument ID. |


### Response examples

BACS disconnected
```json
{
  "id": "6713050b-e64f-4da7-0770-5b0583f81739",
  "type": "BACS",
  "status": "DISCONNECTED",
  "bankName": "BARCLAYS BANK PLC",
  "bankCode": null,
  "branchCode": "00-00-00",
  "accountNumber": "XXXX5678",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "GB",
    "state": null,
    "city": "London",
    "postCode": "EC2A 4JE",
    "firstLine": "65 Clifton St"
  },
  "reference": "REFERENCE01",
  "disconnectReason": "MANUALLY_DISCONNECTED"
}
```

ACH disconnected
🟡 In BETA

```json
{
  "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "type": "ACH",
  "status": "DISCONNECTED",
  "bankName": "Bank of America",
  "bankCode": "026009593",
  "branchCode": null,
  "accountNumber": "******6789",
  "accountOwnerDetails": {
    "companyName": "ABC Logistics Ltd",
    "country": "US",
    "state": "NY",
    "city": "New York",
    "postCode": "10001",
    "firstLine": "123 Main Street"
  },
  "reference": null,
  "disconnectReason": "MANUALLY_DISCONNECTED"
}
```

### Handling a disconnected payment instrument 

A payment instrument may become disconnected for various reasons. For example:

- A customer bank account is not active.
- A customer cancels their authorisation via their bank.
- A payment instrument is cancelled via the API request above.


These cases all lead to the payment instrument being marked as `DISCONNECTED`, meaning it can no longer be used for initiating Payins.

#### Disconnect reasons

We provide a `disconnectReason` field to allow you to handle these scenarios gracefully.

The reason can be one of the following values:

- `AUTHORISATION_REMOVED`: The account has been disconnected by the customer or their bank.
- `ACCOUNT_NO_LONGER_VALID`: The bank account for this account has been closed or transferred.
- `REFER_TO_PAYER`: The customer's bank was unable to authorise the payment instrument. This could be due to the instrument type not being supported or the customer disputing authorisation with their bank. In these cases, please contact the customer.
- `INCORRECT_ACCOUNT_DETAILS`: The specified bank account does not exist or was closed.
- `PAYMENT_INSTRUMENT_TYPE_NOT_ENABLED`: The provided bank account does not support the selected instrument type.
- `MANUALLY_DISCONNECTED`: The payment instrument was disconnected via the supplied disconnect endpoint.
- `OTHER`: A catch-all for other disconnection reasons not covered by the specific categories above. This may include technical issues or less common bank-specific failure reasons.


## Webhooks

Webhooks provide real-time updates on status changes for your payment instruments. Subscribe to these events to avoid constantly polling the API for status changes.

The `payment-instruments#status-change` webhook notifies you when an instrument's status changes. For example:

- `PENDING` → `CONNECTED`: The mandate is now active and you can start collecting payments.
- `CONNECTED` → `DISCONNECTED`: The mandate has been cancelled or revoked. You should stop attempting collections, reflect this to the customer, and potentially prompt re-authorization.


Connected status payload
When a payment instrument is successfully connected:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-19T17:43:23Z",
  "data": {
    "resource": {
      "id": "7f0f9dda-7755-4b4f-bd53-637129291308"
    },
    "from_status": "PENDING",
    "to_status": "CONNECTED",
    "occurred_at": "2025-01-19T17:43:22Z"
  }
}
```

Disconnected status payload
When a payment instrument becomes disconnected, the `disconnect_reason` field is included in `data.resource`:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-20T14:22:18Z",
  "data": {
    "resource": {
      "id": "7f0f9dda-7755-4b4f-bd53-637129291308",
      "disconnect_reason": "REFER_TO_PAYER"
    },
    "from_status": "CONNECTED",
    "to_status": "DISCONNECTED",
    "occurred_at": "2025-01-20T14:22:17Z"
  }
}
```

### Webhook payload fields

| Field | Type | Description |
|  --- | --- | --- |
| `subscription_id` | uuid | ID of the webhook subscription that triggered the event notification. |
| `event_type` | string | The event that occurred in our system (always `payment-instruments#status-change` for this webhook). |
| `schema_version` | string | Webhook schema version (the notification structure used to model the event). Currently `0.0.1`. |
| `sent_at` | string | ISO 8601 timestamp when webhook was sent. |
| `data` | object | Contains the event type and schema version details specific to this webhook. |
| `data.resource.id` | uuid | Payment instrument identifier. |
| `data.resource.disconnect_reason` | string | Reason for disconnection (only present when `to_status` is `DISCONNECTED`). See [Disconnect Reasons](#disconnect-reasons) for possible values. |
| `data.from_status` | string | Previous status (`PENDING`, `CONNECTED`, or `null` for new instruments). |
| `data.to_status` | string | New status (`PENDING`, `CONNECTED`, or `DISCONNECTED`). |
| `data.occurred_at` | string | ISO 8601 timestamp when the status change occurred. |