# Affiliate partner integration guide

Affiliate partners can access the Wise Platform [Exchange rates](/api-reference/rate/rateget) and [Unauthenticated quotes](/api-reference/quote/quotecreateunauthenticated) endpoints to enrich their site or internal tools with live and historic exchange rates, transfer fees, and delivery speed information.

See our [Affiliate program onboarding guide](https://wise.com/gb/blog/affiliate-onboarding-guide#optimise-and-grow-your-campaigns) for further details on getting your tracking link, understanding commissions and reporting, along with other program rules and policies. If you are interested in becoming an affiliate partner, visit our [Become a Wise Partner page](https://wise.com/gb/affiliate-program/).

## API access

To access the Wise Platform API, you must first generate a personal API token through a Wise.com account.

If you don't have a Wise business account, go to [https://wise.com/register#/welcome](https://wise.com/register#/welcome) to register now.

To generate a personal API token in the Wise app:

1. Click on your profile icon.
2. Go to `Connect and manage apps` -> `API tokens`.
3. Click `Add new token`.
4. Complete 2-step verification when prompted.
5. Copy and securely store your token (it will only be shown once).


Once you have your personal API token, use it as the bearer token in the `Authorization` header of your get rates requests.

## Environments

- The sandbox environment for testing is located at `https://api.wise-sandbox.com`
- The production environment is located at `https://api.wise.com`


## Retrieve current rates

Use the [Retrieve current rates endpoint](/api-reference/rate/rateget) to fetch the latest exchange rates. This request includes several query parameter options so you can specify what kind of rate details are returned in the response.

For example, to fetch the latest exchange rates of **all currencies**:

`GET /rates`

To fetch the latest exchange rate of **one currency pair**, add the `source` and `target` query parameters to the endpoint path:

`GET /rates?source=EUR&target=USD`

Example request
```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/rates?source=EUR&target=USD&time=2019-02-13T14%3A53%3A01&from=2019-02-13T14%3A53%3A01&to=2019-03-13T14%3A53%3A01&group=day' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Example response
```json 200 application/json
[
  {
    "rate": 1.166,
    "source": "EUR",
    "target": "USD",
    "time": "2018-08-31T10:43:31+0000"
  }
]
```

```json 400 application/json
{
  "error": "Bad Request",
  "message": "Invalid parameters",
  "path": null,
  "status": 400,
  "timestamp": "2026-01-01T06:56:29.923935466Z"
}
```

```json 429 application/json
{}
```

See the [Retrieve current rates endpoint](/api-reference/rate) reference for full details and other examples.

## Get pricing and speed

To include details like exchange fees and estimated delivery time, send a request to the [Create a quote (unauthenticated) endpoint](/api-reference/quote/quotecreateunauthenticated).

`POST /quotes`

Example request
```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "targetCurrency": "GBP",
    "targetAmount": 600,
    "sourceCurrency": "EUR"
  }'
```

Example response
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

Authorization header not required
The unauthenticated quote request does not require including the `Authorization` header in the request. You can omit it and still receive a successful response.

### Quotes FAQs

**Is a specific currency route supported?**

If we don't support a route, this endpoint will respond with an error code `error.route.not.supported`.

**How much does a transfer cost?**

The Wise fee is included in the response.

**How long does a transfer take?**

Estimated delivery time is included in the response. This can vary quite a lot for different currency routes. For example, transfers often only take a few hours from EUR to GBP, while sending money from USD can take 1-2 business days.

This endpoint allows you to find out the estimated delivery time for each currency route.

## Postman collection

See our [Postman collection](https://documenter.getpostman.com/view/12156495/TVes8SL9) for more details and examples of how to use the Wise Platform API, including how to get comparison, rates, pricing, and speed data.