# Balance accounts

Balance accounts are the accounts that sit inside the multi-currency account and hold the currency balance, ledger of transactions, and other details specifically for that account. For the purpose of this guide, only `STANDARD` balances will be included/discussed. Additional types, such as jars (type = `SAVINGS`) will be ignored.

The balance account endpoints are provided to create, view, and manage the balance accounts for a particular profile and a particular multi-currency account. They also are what is used to create a multi-currency account when one does not exist for a profile.

Before creating a balance account, you must know the `profileId` you want to operate on, what balance account currencies you want to open, and should have created the multi-currency account and first balance account for the profile.

The next steps are to:

1. [Create a balance account](#create) - Create the first or subsequent balance accounts in a different currencies.
2. [List all balance accounts](#list) - List the balance accounts currently included in the multi-currency account for this profile.
3. [Get balance account by ID](#get) - Get the details of a balance account by its ID.
4. [Delete balance account](#delete) - Remove a balance account from a multi-currency account.
5. [Get balance account statement](#get-balance-statement) - Get a balance account statement for a specified time range.


## Prerequisites and notes 

### Investment state

Balance accounts include a field of `investmentState`. This can include multiple different statuses, however the one to watch for is `NOT_INVESTED`. If a balance has any other value, then the balance should not and currently cannot be operated on via the API.

If a balance is invested, it should still be shown, however it should be shown as an un-operable balance in your integration. This should only be the case for user accounts that are linked and already have balances, but should be taken into account when building your integration.

## Create a balance account 

This endpoint opens a balance within the specified profile, in the currency and type specified in the request.

For `STANDARD` balances, only one can be created for a currency. For `SAVINGS` balances, multiples in the same currency can be opened.

When sending the request, the `currency` and `type` are required. If creating a `SAVINGS` type balance, a `name` is also required.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/balances' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -H 'X-idempotence-uuid: 497f6eca-6276-4993-bfeb-53cbbbba6f08' \
  -d '{
    "currency": "EUR",
    "type": "STANDARD"
  }'
```

For request/response details, see the [API reference](/api-reference/balance/balancecreate).

## List balances for a profile 

Retrieve the user's multi-currency account balance accounts. It returns all balance accounts the profile has in the types specified.

A parameter of `type` must be passed and include at least a single type. To return more than one type, comma separate the values. Acceptable values are `STANDARD` and `SAVINGS`.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/{profileId}/balances?types=STANDARD' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/balance/balancelist).

## Retrieve a balance by ID 

This endpoint returns a balance based on the specified balance ID.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/{profileId}/balances/{balanceId}' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/balance/balanceget).

## Remove a balance account 

Close a balance account for the user's profile. Balance accounts must have a zero balance in order for it to be closed.

Bank account details for a balance account will also be deactivated and may not be restored in the future.

```shell curl
curl -i -X DELETE \
  'https://api.wise.com/2026Q4/profiles/{profileId}/balances/{balanceId}' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/balance/balancedelete).

## Retrieving a balance account statement 

This endpoint allows for statements to be generated for the provided balanceId, with the response in JSON. To generate in CSV, PDF, XLSX, CAMT.053, MT940 or QIF, replace `statement.json` with `statement.csv`, `statement.pdf`, `statement.xlsx`, `statement.xml`, `statement.mt940` or `statement.qif` respectively.

The period between `intervalStart` and `intervalEnd` cannot exceed 469 days (around 1 year 3 months).

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/balance-statement/balancestatementget).

SCA protected endpoint
This endpoint is SCA protected. SCA requirements apply to profiles registered outside of the following regions: US, AU, NZ, SG, CA, MY.

This additional authentication is only required once every 90 days.

Note that viewing the statement on the website or in the mobile app also requires SCA.

Review the [Strong Customer Authentication guide](/guides/developer/auth-and-security/sca-and-2fa) for more details.