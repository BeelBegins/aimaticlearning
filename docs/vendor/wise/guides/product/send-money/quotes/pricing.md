# Flexible partner pricing

Wise will configure standard pricing for each route in your integration. However, partners on occassion may need flexibility to offer tiered services, discounts, or special pricing.

Flexible partner pricing allows you to customize or replace Wise’s standard fees.

Using the `pricingConfiguration` object, partners can set specific pricing parameters when creating or updating a quote. This lets you customize fee structures based on your business needs.

Flexible Partner Pricing is still in beta and will only be available to select partners depending on integration method. Please speak with your Implementation or Account Manager to learn more.

## How it works

1. **Passing `pricingConfiguration`**: When enabled for your client ID, include the `pricingConfiguration` in your `POST` or `PATCH` call to `/quote`.
2. **Mandatory fields**: Provide all values in the `fee` object, setting `0` for any fields where you want a zero charge.
3. **Quote calculations**: The `pricingConfiguration` determines fees calculated on the quote, which appear in the response as configured fees.
4. **Fee limits**: Wise will work with you to set up limits and alerts on fees you charge customers.


Wise will use the details included in the `pricingConfiguration` to configure pricing and run calculations for fees on the quote. The pricing configuration as well as the calculated fees are returned in the quote body.

Wise configures controls on the fees that can be charged, and will work with you to set these limits and alerting.

If your request does not include a pricing configuration object, we will default to non-flexible pricing and use the default configuration for your client key.

## Variable, fixed, and deferred fees 

Pricing consists of two types of fees: a variable percentage fee, applied to the amount being converted, and a fixed fee, which is added on top.

To change these values, partners need to pass in a pricing configuration.

When Wise receives a pricing configuration, it uses the variable and fixed fee given to calculate the fees on the quote. This typically results in a partner convenience fee being applied, denoted as `PARTNER` in the response.

In some cases, the requested fees may calculate to less than the agreed fee Wise will charge. When this occurs, the difference is added as a **Deferred Fee**.

There are examples of this below to illustrate the various pricing configurations that can be sent, and how their calculations are returned.

All the examples below quotes 200 GBP being sent to EUR, with Wise charging 0.5% variable fee and £1 to send the funds.

**Example request**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "GBP",
    "targetCurrency": "EUR",
    "sourceAmount": 200,
    "targetAmount": null,
    "pricingConfiguration": {
      "fee": {
        "type": "OVERRIDE",
        "variable": 0.005,
        "fixed": 1
      }
    }
  }'
```

## Calculating Wise fees 

Flexible partner pricing calculates fees based on the **Amount to Convert**, the target amount before conversion.

For target amount quotes, calculating the amount to convert is straightforward. For quotes where a `sourceAmount` is provided, the process is slightly more complex.

- For **target amount quotes**: We convert the target amount to the source currency with the rate of the quote, then use this to calculate fees, building up to the returned `sourceAmount`.
- For **source amount quotes**: We use an algorithm to determine the unrounded amount to convert and calculate the fees on top of that. Once the fees are calculated, they are subtracted from the `sourceAmount` to get the true amount to convert.


These calculations are difficult to do, so Wise completes these for you and returns everything you need to calculate fees yourself and ensure they are correct.

### Calculating target amount quote

In this example, let's calculate fees of 0.5% and £1 fee on a GBP to EUR transfer. The partner has provided a target amount of €180, and the current exchange rate is 0.9000.

- Step 1: Convert Target to Source Currency - €180 / 0.9000 = £200
- Step 2: Calculate the variable fee - £200 * 0.5% = £1 = £201
- Step 3: Add the fixed fee - £201 + £1 = £202


SourceAmount is returned as £202.

### Calculating source amount quote

In this example, let's calculate fees of 0.5% and £1 fee on a GBP to EUR transfer. The partner has provided a source amount of £200, and the current exchange rate is 0.9000.

- Step 1: Wise uses algorithm to determine the unrounded amount to convert - £198.00995
- Step 2: Calculate the variable fee - £198.00995 * 0.5% = 0.99 + 198.00995 = 198.999999
- Step 3: Add the fixed fee - £198.999999 + 1 = £199.999999
- Step 4: Calculate actual amount to be sent - £200 - 0.99 - 1 = £198.01
- Step 5: Convert Amount to Convert to Target Currency = £198.01 * 0.9000 = €178.21


TargetAmount is returned as €178.21.

Due to the complexity of the second calculation, the resulting quote will include the `unroundedAmountToConvert` along with all of the fees. This ensures you can calculate the fees easily without needing an algorithm.

## Error handling 

If the provided pricing configuration results in a calculation that falls outside the defined controls, the system will return a `422 - Unprocessable Entity` status code with a standard error message. In such cases, no quote is generated, and an updated pricing configuration is required to proceed.

Example response - pricing configuartion invalid
```json
{
  "errors": [
    {
      "code": "error.quote.pricing.configuration.invalid",
      "message": "Invalid pricing configuration",
      "arguments": []
    }
  ]
}
```

## Example 1: Additional partner fee 

In this example, the partner wants to add a custom convenience fee to the transfer, adding a 0.5% variable partner fee on top of the Wise 0.5% fee, with no additional fixed fee.

The partner sends this as an `OVERRIDE` type. In the `OVERRIDE` type, the variable and fixed values are used instead of the configured Wise amounts, then used to calculate fees. Therefore, the values in the pricing configuration are:

- Variable: 0.5% (Partner) + 0.5% (Wise) = 1.0% or 0.01
- Fixed: 0 (Partner) + 1 (Wise) = 1


**Example request**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "GBP",
    "targetCurrency": "EUR",
    "sourceAmount": 200,
    "targetAmount": null,
    "pricingConfiguration": {
      "fee": {
        "type": "OVERRIDE",
        "variable": 0.01,
        "fixed": 1
      }
    }
  }'
```

Example response
```json
{
  "fee": {
    "transferwise": 1.99,
    "payIn": 0,
    "discount": 0,
    "partner": 0.99,
    "total": 2.98
  },
  "price": {
    "priceSetId": 238,
    "total": {
      "type": "TOTAL",
      "label": "Total fees",
      "value": {
        "amount": 2.98,
        "currency": "GBP",
        "label:": "2.98 GBP"
      }
    },
    "items": [
      {
        "type": "PARTNER",
        "label": "Convenience Fee",
        "value": {
          "amount": 0.99,
          "currency": "GBP",
          "label": "0.99 GBP"
        }
      },
      {
        "type": "TRANSFERWISE",
        "label": "Our fee",
        "value": {
          "amount": 1.99,
          "currency": "GBP",
          "label": "1.99 GBP"
        }
      }
    ],
    "calculatedOn": {
      "unroundedAmountToConvert": {
        "amount": 197.029702,
        "currency": "GBP"
      }
    }
  }
}
```

## Example 2: Fee free transfer 

In this example, the partner wants to display or charge zero fees to the customer. Here, the partner agrees to cover the Wise fee themselves.

The partner sends this as an `OVERRIDE` type. In the `OVERRIDE` type, the variable and fixed values are used instead of the configured Wise amounts, then used to calculate fees. Therefore, the values in the pricing configuration are:

- Variable: 0
- Fixed: 0


In the resulting quote, the Wise fee which was calculated now includes a deferred fee. This means the partner needs to pay this amount.

**Example request**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "GBP",
    "targetCurrency": "EUR",
    "sourceAmount": 200,
    "targetAmount": null,
    "pricingConfiguration": {
      "fee": {
        "type": "OVERRIDE",
        "variable": 0,
        "fixed": 0
      }
    }
  }'
```

Example response
```json
{
  "fee": {
    "transferwise": 0,
    "payIn": 0,
    "discount": 0,
    "partner": 0,
    "total": 0
  },
  "price": {
    "priceSetId": 238,
    "total": {
      "type": "TOTAL",
      "label": "Total fees",
      "value": {
        "amount": 0,
        "currency": "GBP",
        "label:": "0.00 GBP"
      }
    },
    "items": [
      {
        "type": "TRANSFERWISE",
        "label": "Our fee",
        "value": {
          "amount": 0,
          "currency": "GBP",
          "label": "0.00 GBP"
        }
      }
    ],
    "deferredFee": {
      "amount": 1.99,
      "currency": "GBP"
    },
    "calculatedOn": {
      "unroundedAmountToConvert": {
        "amount": 198.00995,
        "currency": "GBP"
      }
    }
  }
}
```

## Example 3: Set variable fee 

In this example, the partner wants to charge the customer exactly 0.9% for the transfer, covering both the Wise fee and the partner convenience fee within this amount.

The partner sends this as an `OVERRIDE` type pricing configuration.

Notice how in the resulting quote, the Wise fee which was calculated is present, as well as the partner convenience fee. This means the partner does not need to pay any fees to Wise.

**Example request**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/101/quotes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "sourceCurrency": "GBP",
    "targetCurrency": "EUR",
    "sourceAmount": 200,
    "targetAmount": null,
    "pricingConfiguration": {
      "fee": {
        "type": "OVERRIDE",
        "variable": 0.009,
        "fixed": 0
      }
    }
  }'
```

Example response
```json
{
  "fee": {
    "transferwise": 1.99,
    "payIn": 0,
    "discount": 0,
    "partner": 0.79,
    "total": 0
  },
  "price": {
    "priceSetId": 238,
    "total": {
      "type": "TOTAL",
      "label": "Total fees",
      "value": {
        "amount": 2.78,
        "currency": "GBP",
        "label:": "2.78 GBP"
      }
    },
    "items": [
      {
        "type": "PARTNER",
        "label": "Convenience Fee",
        "value": {
          "amount": 0.79,
          "currency": "GBP",
          "label": "0.79 GBP"
        }
      },
      {
        "type": "TRANSFERWISE",
        "label": "Our fee",
        "value": {
          "amount": 1.99,
          "currency": "GBP",
          "label": "1.99 GBP"
        }
      }
    ],
    "calculatedOn": {
      "unroundedAmountToConvert": {
        "amount": 197.22495,
        "currency": "GBP"
      }
    }
  }
}
```