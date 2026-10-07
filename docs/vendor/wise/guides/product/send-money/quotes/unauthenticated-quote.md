# Unauthenticated quotes

Unauthenticated quotes let you fetch example exchange rates and fees without authentication and including only basic transfer details. These quotes show potential costs and exchange rates, making them ideal for marketing pages and product displays without user sign-up.

## Important limitations

Unauthenticated quotes:

- Cannot be used to create actual transfers.
- Are for display and estimation purposes only.
- Should not be stored long-term or relied upon for transactions.
- Rates expire and should be refreshed regularly.


To create actual transfers, you must use the [authenticated quote endpoint](/api-reference/quote/quotecreate).

## Creating an unauthenticated quote

To create a unauthenticated quote, send an HTTP `POST` request to [`/quotes`](/api-reference/quote/quotecreateunauthenticated).

### Request body

The body of your request is where you specify all the information about the FX payment quote you want to create.

You must provide the currencies to exchange:

| Parameter | Description | Example |
|  --- | --- | --- |
| `sourceCurrency` | Currency you are sending from (ISO 4217) | `"USD"` |
| `targetCurrency` | Currency to be received in (ISO 4217) | `"EUR"` |


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
  https://api.wise.com/2026Q4/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "USD",
    "targetCurrency": "EUR",
    "sourceAmount": 100
  }'
```

**Option B: Fixed receive amount**

Use when you know how much the recipient should receive.

**Example Request**:

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "USD",
    "targetCurrency": "EUR",
    "targetAmount": 85
  }'
```

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
| `rate` | Current exchange rate (targetCurrency per 1 sourceCurrency) | Display "1 USD = 0.9215 EUR" |
| `sourceAmount` | Total amount user needs to send | Show "You send $100.00" |
| `targetAmount` | Amount recipient receives after fees | Show "Recipient gets €92.15" |
| `createdTime` | When this quote was created (ISO 8601) | Log for debugging |
| `rateExpirationTime` | When this rate expires (ISO 8601) | Show "Rate valid for 30 minutes" |
| `paymentOptions.fee.total` | Total fee charged | Show "Fee: $2.58" |
| `paymentOptions.formattedEstimatedDelivery` | Human-readable delivery estimate | Show "Arrives by Tuesday" |