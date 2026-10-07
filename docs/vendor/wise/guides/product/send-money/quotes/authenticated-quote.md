# Authenticated Quotes

Authenticated quotes are profile-specific exchange rate quotes that serve as the foundation for creating actual money transfers. Unlike unauthenticated quotes (used for display purposes), authenticated quotes are used to create real transfers.

They are linked to the sender profile ID, include a unique quote ID, and lock in the rate for a limited time.

## When to create authenticated quotes

Use authenticated quotes when:

- Users are ready to create an actual transfer.
- You need to lock in an exchange rate.
- You're building the transfer creation flow.
- You need to show exact fees for a real transaction.


## Creating an authenticated quote

To create an authenticated quote, send an HTTP `POST` request to [`/profiles/{profileId}/quotes`](/api-reference/quote/quotecreate).

You must pass in the header:

| Parameter | Description | Example |
|  --- | --- | --- |
| `profileId` | The user or account's profile ID | `87654321` |


### Request body

The body of your request is where you specify all the information about the FX payment quote you want to create.

You must provide the currencies to exchange:

| Parameter | Description | Example |
|  --- | --- | --- |
| `sourceCurrency` | Currency you are sending from (ISO 4217) | `"USD"` |
| `targetCurrency` | Currency to receive in (ISO 4217) | `"EUR"` |


If the `targetAccount` is not yet known, you can pass `null`. You can then `PATCH` to [add the recipient information](/guides/product/send-money/quotes/update-quote) once you have it.

Then **EITHER** `sourceAmount` **OR** `targetAmount` (never both):

| Parameter | Description | Example |
|  --- | --- | --- |
| `sourceAmount` | Amount to send | `100.00` |
| `targetAmount` | Amount recipient should receive | `85.00` |


#### Sample scenarios

**Option A: Fixed send amount**

Use when you know how much the user wants to send.

**Example Request**:

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "USD",
    "targetCurrency": "EUR",
    "sourceAmount": 1000,
    "targetAccount": null
  }'
```

**Option B: Fixed receive amount**

Use when you know how much the recipient should receive.

**Example Request**:

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "USD",
    "targetCurrency": "EUR",
    "targetAmount": 850,
    "targetAccount": null
  }'
```

### Optional Parameters

#### Payment method selection

| Parameter | Type | Description | Example |
|  --- | --- | --- | --- |
| `payOut` | string | Payout method (if multiple available) | `"BANK_TRANSFER"`, `"SWIFT"`, `"INTERAC"` |


**Example**:

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "CAD",
    "targetCurrency": "USD",
    "sourceAmount": 1000,
    "targetAccount": null,
    "payOut": "INTERAC"
  }'
```

#### Pre-linking to recipient

Instead of `null`, you can provide a recipient account ID in the `targetAccount` field to get fees specific to that recipient:

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "USD",
    "targetCurrency": "EUR",
    "sourceAmount": 1000,
    "targetAccount": 98765432
  }'
```

**Benefits**:

- More accurate fees (some recipients may have different fee structures).
- Faster transfer creation.
- Better user experience.


### Complete response sample

```json 200 application/json
{
  "id": "11144c35-9fe8-4c32-b7fd-d05c2a7734bf",
  "sourceCurrency": "GBP",
  "targetCurrency": "USD",
  "sourceAmount": 100,
  "targetAmount": 129.24,
  "payOut": "BANK_TRANSFER",
  "preferredPayIn": "BANK_TRANSFER",
  "rate": 1.30445,
  "createdTime": "2019-04-05T13:18:58Z",
  "user": 55,
  "profile": 101,
  "rateType": "FIXED",
  "rateExpirationTime": "2019-04-08T13:18:57Z",
  "guaranteedTargetAmountAllowed": true,
  "targetAmountAllowed": true,
  "guaranteedTargetAmount": false,
  "providedAmountType": "SOURCE",
  "pricingConfiguration": {
    "fee": {
      "type": "OVERRIDE",
      "variable": 0.011,
      "fixed": 15.42
    }
  },
  "paymentOptions": [
    {
      "disabled": false,
      "estimatedDelivery": "2019-04-08T12:30:00Z",
      "formattedEstimatedDelivery": "by Apr 8",
      "estimatedDeliveryDelays": [
        {
          "reason": "sample reason"
        }
      ],
      "fee": {
        "transferwise": 3.04,
        "payIn": 0,
        "discount": 2.27,
        "partner": 0,
        "total": 0.77
      },
      "price": {
        "priceSetId": 238,
        "total": {
          "type": "TOTAL",
          "label": "Total fees",
          "value": {
            "amount": 0.77,
            "currency": "GBP",
            "label": "0.77 GBP"
          },
          "explanation": {}
        },
        "items": [
          {
            "id": "string",
            "type": "FEE",
            "label": "fee",
            "value": {
              "amount": 0,
              "currency": "GBP",
              "label": "0 GBP"
            },
            "explanation": {
              "plainText": "string",
              "markdown": "string"
            }
          }
        ],
        "deferredFee": {
          "amount": 14.79,
          "currency": "BRL"
        },
        "calculatedOn": {
          "unroundedAmountToConvert": {
            "amount": 179.97342,
            "currency": "BRL"
          }
        }
      },
      "sourceAmount": 100,
      "targetAmount": 129.24,
      "sourceCurrency": "GBP",
      "targetCurrency": "USD",
      "payIn": "BANK_TRANSFER",
      "payOut": "BANK_TRANSFER",
      "allowedProfileTypes": [
        "PERSONAL",
        "BUSINESS"
      ],
      "payInProduct": "CHEAP",
      "feePercentage": 0.0092,
      "disabledReason": {
        "code": "string",
        "message": "string"
      }
    }
  ],
  "status": "PENDING",
  "expirationTime": "2019-04-05T13:48:58Z",
  "notices": [
    {
      "text": "You can have a maximum of 3 open transfers with a guaranteed rate. After that, they'll be transferred using the live rate. Complete or cancel your other transfers to regain the use of guaranteed rate.",
      "link": null,
      "type": "WARNING"
    }
  ]
}
```

```json 429 application/json
{}
```

### Key response fields

| Field | Description | Example use |
|  --- | --- | --- |
| `id` | Unique quote identifier - **save this!** | Use to [create transfer](/guides/product/send-money/transfers) |
| `rate` | Exchange rate locked for this quote | Display "1 USD = 0.9215 EUR" |
| `sourceAmount` | Total amount user needs to send | Show "You send $1,000.00" |
| `targetAmount` | Amount recipient receives | Show "Recipient gets €921.50" |
| `rateType` | `"FIXED"` or `"FLOATING"` | Inform user if rate is guaranteed |
| `rateExpirationTime` | When the locked rate expires | Show countdown timer |
| `expirationTime` | When the entire quote expires | Must create transfer before this |
| `paymentOptions[0].fee.total` | Total fee in source currency | Show "Fee: $5.15" |
| `paymentOptions[0].formattedEstimatedDelivery` | Human-readable delivery time | Show "Arrives by Wednesday" |
| `paymentOptions[0].estimatedDelivery` | Exact estimated delivery timestamp | Calculate delivery time |
| `paymentOptions[0].payIn` | Payment method | `"BALANCE"`, `"BANK_TRANSFER"`, etc. |
| `status` | Quote status | `"PENDING"`, `"ACCEPTED"`, `"EXPIRED"`, `CANCELLED` |
| `profile` | Profile ID this quote belongs to | Verify correct profile |
| `providedAmountType` | Which amount was provided | `"SOURCE"` or `"TARGET"` |


### Quote status values

| Status | Description | Can create transfer? |
|  --- | --- | --- |
| `PENDING` | Quote is active and usable | ✅ Yes |
| `ACCEPTED` | Quote was used to create a transfer | ❌ No (already used) |
| `EXPIRED` | Quote has expired | ❌ No |
| `CANCELLED` | Quote was cancelled | ❌ No |