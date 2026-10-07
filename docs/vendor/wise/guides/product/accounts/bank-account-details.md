# Bank account details

Account details allow the account holder, or their customers, to receive funds like a local in that currency's country, without needing a physical bank account there. Account details are optional and not created by default when you open a balance.

Wise provides bank account detail endpoints to create, view, and manage bank account details for an account balance.

Once you create a [Multi-currency account](/guides/product/accounts/managing-accounts) and [balance accounts](/guides/product/accounts/balance-accounts), you can then request and list local account details for currencies that support them.

After the account details are issued, any incoming payment sent to those scheme credentials (IBAN, sort code and account number, routing and account number, etc.) will generate an `incoming-transfer` resource and trigger an [`incoming-transfer#credited`](/guides/product/receive-money/incoming-transfer-notifications) webhook notification. Refer to the [Receive money guide](/guides/product/receive-money) for the full integration pattern for handling incoming payments.

The bank account details endpoints allow you to:

1. [Retrieve bank account details](#get): View existing bank account details for the profile.
2. [Create a bank account details order](#create): Request bank account details for a balance currency.
3. [List bank account detail orders](#list): Check the status of open orders.


## Retrieve bank account details 

This endpoint retrieves account details by ID. Account details identify an account that can receive funds (for example, an IBAN, or a sort code and account number). GB, US, and BE account details are supported. Requesting account details for an unsupported country returns `404 Not Found`.

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/balances/account-details/12345678 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/bank-account-details/getaccountdetails).

## Create a bank account details order 

This endpoint creates an order to issue bank account details. The order uses the same currency as a previously created balance. Fulfilling all requirements will complete the order and transition it to `status = DONE`, at which point the issued account details become `ACTIVE` and ready to receive payments.

### Order lifecycle

An order progresses through a series of requirement statuses before it can be fulfilled. Each requirement must be resolved in sequence before the order completes.

**Requirement statuses:**

- `PENDING_USER`: Requires action from the user before the order can proceed.
- `PENDING_TW`: Wise is processing the requirement; no user action is needed at this stage.
- `DONE`: The requirement has been fulfilled.


**Common requirement types:**

- `VERIFICATION`: The user must be fully verified before account details can be issued.
- `TOP_UP`: A fee must be paid via wise.com to complete the order.


### Verification requirement

If account order is pending `VERIFICATION` requirement, use the [KYC Review API](/api-reference/kyc-review) to get the list of outstanding evidence and documentation items awaiting submission. When all pending evidence is submitted and verified, the corresponding requirements transition to `DONE` and the order can complete.

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/12345678/account-details-orders \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "currency": "EUR"
  }'
```

For request/response details, see the [API reference](/api-reference/bank-account-details/bankaccountdetailsordercreate).

## List bank account detail orders 

Returns the bank account assignment requests for a profile and multi-currency account. Use this endpoint to monitor the status of open orders and check whether any requirements are `PENDING_USER` and awaiting action.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345678/account-details-orders?currency=GBP' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/bank-account-details/bankaccountdetailsorderslist).

## Next steps 

* Use the [KYC Review API](/api-reference/kyc-review) to check for any pending verification or compliance evidence required to complete account detail orders.
* [Subscribe to the `incoming-transfer#credited` webhook](/guides/product/receive-money/incoming-transfer-notifications) to be notified when funds are credited to your issued account details.
* Use the [Incoming Transfers API](/api-reference/incoming-transfer) to retrieve full payment, debtor, and clearing details for each credited transfer.
* Test incoming payments to your issued account details in the [Wise Platform sandbox environment](/guides/product/receive-money/test-and-go-live#simulate-local-account-details).