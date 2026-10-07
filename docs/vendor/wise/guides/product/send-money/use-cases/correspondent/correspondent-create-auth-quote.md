# Create quote

[Create an authenticated quote](/api-reference/quote/quotecreate) to get accurate, up-to-date pricing for a specific corridor (source/target currencies + amount), including fees, rate, and delivery estimate. You’ll use the quote `id` from the response to create a transfer as well as when you create recipient accounts in the quote-first flow.

When creating a quote, the mid-market exchange rate is locked for 30 minutes to ensure the rate is used for the transfer.

## Requirements

Authenticated quote requirements can vary depending on your settlement model and whether you are using the quote-first or recipient-first flow. The following table describes the required, conditional, and optional fields for the create authenticated quote request:

| Field  | Required? | Description  |
|  --- | --- | --- |
| `profileId` | No | The Wise profile ID that owns the recipient account (for correspondent partners, this is your business profile ID). If omitted, defaults to the business profile ID used for the request. |
| `sourceCurrency` | Yes | Currency the sender pays in (ISO 4217). |
| `targetCurrency` | Yes | Currency the recipient receives in (ISO 4217). |
| `sourceAmount` | Conditional | The total amount that Wise needs to receive to process the transfer. This amount includes all fees and the amount to be sent.


Provide either `sourceAmount` or `targetAmount`, not both. |
| `targetAmount` | Conditional | The total amount the recipient is to receive.


Provide either `sourceAmount` or `targetAmount`, not both. |
| `targetAccount` | Conditional | The recipient account id. Required for recipient-first send flow. If omitted (as in the quote-first flow), be sure to [update the quote](/api-reference/quote/quoteupdate) later once the recipient is selected/created to refresh fees and ETA. |
| `preferredPayIn` | No (recommended) | The preferred method of funding the transfer. When creating a quote for a balance-funded transfer, set to `BALANCE` to receive accurate pricing. If omitted, defaults to `BANK_TRANSFER` and the quoted fees may not match the actual fees applied at funding. |
| `payInMethod` / `payInId` / `preferredPayInId` | Conditional | The method that will be used to fund the transfer. Some balance-funded configurations require `payInMethod` (and optionally a specific balance id) to avoid pricing/funding mismatches. |
| `payOut` | No | The method that will be used for the payout. Defaults to `BANK_TRANSFER` if omitted. Use when you need to quote for a specific payout rail (`BALANCE`, `SWIFT`, `SWIFT_OUR`, `ALIPAY`, and `INTERAC`).
\ |
| `pricingConfiguration` object | Conditional | Used to set specific pricing parameters when creating or updating a quote. Only include if [Flexible Partner Pricing](/guides/product/send-money/quotes/pricing) is enabled. |
| `paymentMetadata` object | Conditional | Required for to/from BRL transfers and from INR transfers. Must be set at the quote level as it carries currency-specific metadata that directly **affects pricing and taxation** on the quote.


**BRL**: must have the `transferNature` field to describe the nature of the transfer (from a set of pre-defined enum values).


**INR**: must have the `transferPurpose` field to describe the purpose of the transfer (`GOODS`, `SERVICES`, or `PROPERTY_PURCHASE`). May required two sub-fields, `transferPurposeToInrMoreOptions` and `transferPurposeToInrInvoiceNumber` depending on the selected purpose.


Make a [validate transfer requirements](/api-reference/transfer/transferrequirementsvalidate) request to discover the allowed values. |


### PayIn selection

If you fund transfers from a Wise balance, ensure your quote uses the matching `payInMethod` to avoid fee mismatches or incorrect balance checks.

**Sample request body**:

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/<profileId>/quotes' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "USD",
    "targetCurrency": "IDR",
    "targetAmount": 39863162,
    "targetAccount": 1012724302,
    "payInMethod": "BALANCE",
    "preferredPayIn": "BALANCE",
    "preferredPayInId": "{{balanceId}}",
    "payInId": "{{balanceId}}"
  }'
```

Use the **payIn** fields your integration requires. If unsure, check with your implementation team.

## Create quote request

**Endpoint**: `POST /profiles/{profileId}/quotes`

Sample request
```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "GBP",
    "targetCurrency": "USD",
    "sourceAmount": 100,
    "targetAmount": null,
    "targetAccount": 12345,
    "payOut": null,
    "preferredPayIn": null,
    "paymentMetadata": {
      "transferNature": "MOVING_MONEY_BETWEEN_OWN_ACCOUNTS"
    },
    "pricingConfiguration": {
      "fee": {
        "type": "OVERRIDE",
        "variable": 0.011,
        "fixed": 15.42
      }
    }
  }'
```

Sample response
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

## Using the response

- The ‘id’ value (quote UUID) is needed for creating the transfer.
- The `paymentOptions` array provides the available pay-in/pay-out combinations
- Use the `payOut` field to select the correct entry in the `paymentOptions` array to know which fees to display to your customer.
  - Find the `paymentOption` that matches the `payOut` field shown at the top level of the quote resource and `payIn` based on the settlement model the bank is using. By default, this is `BANK_TRANSFER`, unless you are using a prefunded or bulk settlement model.
- Each `paymentOption` includes a `price` object. It gives a full breakdown of all the taxes, fees and discounts. It is preferable to refer to this structure to show breakdowns and totals, rather than the `fee` structure, which only gives a summary and does not surface important specifics such as taxes.
- When showing the price of a transfer, always show the 'price.total.value.amount' of a payment option.


Creating a quote without a recipient
Fees and delivery estimates can change after you attach a recipient (`targetAccount`). If you created the quote without a recipient (quote-first flow), [update the quote](#update-quote) before presenting final confirmation pricing.

### Disabled payment options

Each payment option is either enabled or disabled based on the `disabled` value. Disabled payment options should be shown to the user in a disabled state in most cases. This ensures your customers are given options they are familiar with regardless of their availability, as well as with options that can be beneficial to their accounts.

The `option.disabledReason` contains both the `code` and `message`, to explain why the option is disabled. The `message` is the user-friendly text you can surface to your customer, if necessary.

If a payment option is disabled, check the `disabledReason` for errors. Display generic errors like "insufficient balance" for most issues, but display specific messages for maximum/minimum amount limit errors.

## Timing rules

- **Quote expiration**: Quotes expire in approximately 30 minutes, during which time they must be converted into a transfer.
  - If a quote expires mid-flow, create a new quote and re-run downstream requirement checks that depend on it (recipient account requirements and transfer requirements).
- **Rate expiration**: After the quote becomes a transfer, the exchange rate is held for 24–48 hours. The transfer must be funded before the `rateExpirationTime`, otherwise the rate will float, or the transfer will be automatically canceled after 14 days if unfunded. Note that if the quote doesn’t get used for the transfer, the rate promise is voided.


## Update quote

[Updating a quote](/api-reference/quote/quoteupdate) is not required if creating or selecting the recipient before creating the authenticated quote (recipient-first flow). However, this step is necessary for quote-first flows (selecting/creating or changing recipient information *after* creating the initial authenticated quote) or for sending to **BRL** where the `transferNature` must be provided later.

If new recipient details are provided by the customer, create a new recipient and patch the new recipient ID to the existing quote.

**Endpoint**: `PATCH /profiles/{profileId}/quotes/{quoteId}`