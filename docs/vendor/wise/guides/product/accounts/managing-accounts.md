# Multi-currency accounts

Multi-currency account management endpoints allow you to manage the user's multi-currency account overall. We have also included information on getting profile information for an authenticated customer.

Generally, the following flow should be taken to open a multi-currency account:

1. [Get profile](#get) - Get the profile ID of the profile you want to operate on.
2. [List available currencies](#get-currencies) - Determine which currencies are supported for the user.
3. [Get multi-currency Account](#get-account) - Get current multi-currency accounts and balance accounts for the profile, determine next steps.
4. [Check eligibility](#get-eligibility) - Check the eligibility of the profile for multi-currency accounts.
5. [Create a multi-currency account](#create-mca-account) - Create a multi-currency account and first balance account for the profile, if not already created.


## Retrieve a profile by ID

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/{profileId}' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/profile/profileget).

## Retrieve available currencies 

Two endpoints exist to retrieve all the currencies available for balance accounts.

**Available Currencies** — Lists all currencies that are available for balance accounts, including those that can have funds added from external accounts.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/borderless-accounts-configuration/profiles/{profileId}/available-currencies' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Payin Currencies** — Lists all currencies available for balance accounts that also support bank account details.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/borderless-accounts-configuration/profiles/{profileId}/payin-currencies' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

## Retrieve multi currency account for a profile 

Returns the multi-currency account details for the specified profile. If the user does not yet have a multi-currency account, a `404 Not Found` will be returned.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/{profileId}/multi-currency-account' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/multi-currency-account/mcaget).

## Retrieve multi currency account eligibility 

Checks eligibility for a multi-currency account for either a specific profile or for a location. Customers in some countries and states/provinces may not be eligible.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/multi-currency-account/eligibility?profileId=0&country=FR&state=CA' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/multi-currency-account/mcaeligibilityget).

## Create a multi-currency account 

To create a multi-currency account, you simply need to open a balance in at least one currency. When doing so, a multi-currency account will automatically be created. To move forward, you should [create a balance account](/guides/product/accounts/balance-accounts#create).