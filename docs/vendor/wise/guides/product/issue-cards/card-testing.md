# Test your integration

Simulate card transactions in sandbox environment

Once everything's been set-up, we also provide you with endpoints that allow you to simulate transactions on your card, providing you with data that you can use to better optimize your flows in production.

## Simulate a balance top-up

Fund a balance to use for card spend.

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/simulation/balance/topup \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "profileId": 2,
    "balanceId": 5,
    "currency": "EUR",
    "amount": 100,
    "channel": "TRANSFER"
  }'
```

For request/response details, see the [API reference](/api-reference/simulation/simulationbalancetopup).

## Simulate a card transaction authorisation

Simulate POS purchases, e-commerce transactions, ATM withdrawals, and refund authorisations.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/authorisation' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "pos": "CHIP_AND_PIN",
    "transactionType": "GOODS_AND_SERVICES",
    "amount": {
      "value": 10,
      "currency": "SGD"
    },
    "mcc": 5499,
    "cardNumber": "4242424242424242"
  }'
```

For request/response details, see the [API reference](/api-reference/simulation/simulationcardtransactionauthorisation).

## Simulate a card transaction clearing

Clear a previous authorisation. The `ref` field can be copied from the `reference` object in the authorisation response.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/clearing' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "amount": {
      "value": 10,
      "currency": "SGD"
    },
    "transactionType": "GOODS_AND_SERVICES",
    "ref": {
      "transaction": {
        "acquirer": {
          "institutionId": "430010",
          "name": "ACQUIRER NAME",
          "city": "CITY NAME",
          "merchantCategoryCode": 5499,
          "country": "GB",
          "acceptorTerminalId": "TERMID01",
          "acceptorIdCode": "CARD ACCEPTOR",
          "forwardingInstitutionId": "400050"
        },
        "card": {
          "token": "59123122-223d-45f9-b840-0ad4a4f80937",
          "schemeName": "VISA",
          "pan": "4242424242424242",
          "pin": "1234",
          "cvv1": "123",
          "icvv": "456",
          "cvv2": "789",
          "expiration": [
            2029,
            7
          ],
          "sequenceNumber": 1,
          "profileId": 2,
          "userId": 5,
          "cardStatus": "ACTIVE",
          "country": "SG",
          "currencies": [
            "SGD"
          ]
        },
        "pos": {
          "type": "CHIP_AND_PIN",
          "acceptsOnlinePins": true,
          "maxPinLength": 12,
          "supports3ds": false,
          "hasChip": true
        },
        "transactionStartTime": 1667541087.0476434,
        "stan": "363054",
        "schemeTransactionId": "932290252416153",
        "retrievalReferenceNum": "230805363054"
      },
      "requestMti": "0200",
      "authorizationIdResponse": "123646"
    }
  }'
```

For request/response details, see the [API reference](/api-reference/simulation/simulationcardtransactionclearing).

## Simulate a card transaction reversal

Fully or partially reverse an authorisation.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/reversal' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "amount": {
      "value": 3,
      "currency": "SGD"
    },
    "transactionType": "GOODS_AND_SERVICES",
    "ref": {
      "transaction": {
        "acquirer": {
          "institutionId": "430010",
          "name": "ACQUIRER NAME",
          "city": "CITY NAME",
          "merchantCategoryCode": 5499,
          "country": "GB",
          "acceptorTerminalId": "TERMID01",
          "acceptorIdCode": "CARD ACCEPTOR",
          "forwardingInstitutionId": "400050"
        },
        "card": {
          "token": "59123122-223d-45f9-b840-0ad4a4f80937",
          "schemeName": "VISA",
          "pan": "4242424242424242",
          "pin": "1234",
          "cvv1": "123",
          "icvv": "456",
          "cvv2": "789",
          "expiration": [
            2029,
            7
          ],
          "sequenceNumber": 1,
          "profileId": 2,
          "userId": 5,
          "cardStatus": "ACTIVE",
          "country": "SG",
          "currencies": [
            "SGD"
          ]
        },
        "pos": {
          "type": "CHIP_AND_PIN",
          "acceptsOnlinePins": true,
          "maxPinLength": 12,
          "supports3ds": false,
          "hasChip": true
        },
        "transactionStartTime": 1667541087.0476434,
        "stan": "363054",
        "schemeTransactionId": "932290252416153",
        "retrievalReferenceNum": "230805363054"
      },
      "requestMti": "0200",
      "authorizationIdResponse": "123646"
    }
  }'
```

For request/response details, see the [API reference](/api-reference/simulation/simulationcardtransactionreversal).

## Simulate a card transaction refund

A refund is a 2-step process: first authorise with `transactionType` set to `REFUND`, then clear using the clearing endpoint with the same transaction type.

### Step 1: Authorisation

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/authorisation' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "pos": "CHIP_AND_PIN",
    "transactionType": "REFUND",
    "amount": {
      "value": 10,
      "currency": "SGD"
    },
    "mcc": 5499,
    "cardNumber": "4242424242424242"
  }'
```

### Step 2: Clearing

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/clearing' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "amount": {
      "value": 10,
      "currency": "SGD"
    },
    "transactionType": "GOODS_AND_SERVICES",
    "ref": {
      "transaction": {
        "acquirer": {
          "institutionId": "430010",
          "name": "ACQUIRER NAME",
          "city": "CITY NAME",
          "merchantCategoryCode": 5499,
          "country": "GB",
          "acceptorTerminalId": "TERMID01",
          "acceptorIdCode": "CARD ACCEPTOR",
          "forwardingInstitutionId": "400050"
        },
        "card": {
          "token": "59123122-223d-45f9-b840-0ad4a4f80937",
          "schemeName": "VISA",
          "pan": "4242424242424242",
          "pin": "1234",
          "cvv1": "123",
          "icvv": "456",
          "cvv2": "789",
          "expiration": [
            2029,
            7
          ],
          "sequenceNumber": 1,
          "profileId": 2,
          "userId": 5,
          "cardStatus": "ACTIVE",
          "country": "SG",
          "currencies": [
            "SGD"
          ]
        },
        "pos": {
          "type": "CHIP_AND_PIN",
          "acceptsOnlinePins": true,
          "maxPinLength": 12,
          "supports3ds": false,
          "hasChip": true
        },
        "transactionStartTime": 1667541087.0476434,
        "stan": "363054",
        "schemeTransactionId": "932290252416153",
        "retrievalReferenceNum": "230805363054"
      },
      "requestMti": "0200",
      "authorizationIdResponse": "123646"
    }
  }'
```

For request/response details, see the [authorisation](/api-reference/simulation/simulationcardtransactionauthorisation) and [clearing](/api-reference/simulation/simulationcardtransactionclearing) API references.

## List simulated card transactions

Retrieve recent simulated transactions for a card.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions?limit=10' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/simulation/simulationcardtransactions).