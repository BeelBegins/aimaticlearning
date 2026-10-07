# Sandbox & Production Environments

Learn about our environments for testing and deploying your app.

We provide two distinct environments, Production and Sandbox, to allow developers to develop, test, and deploy their applications.

For each environment we offer an endpoint that requires mutual TLS (mTLS) and a separate endpoint for non-mTLS. For most situations we recommend to use mutual TLS, which requires some [additional setup](/guides/developer/auth-and-security/mtls).

## Production Environment

Production is the live environment that developers can use to send real-time requests to the Wise Platform API. This environment is intended to be used in the final stages of development when the application is ready for deployment.

| Security Type | URL |
|  --- | --- |
| mTLS enabled | `https://api-mtls.transferwise.com` |
| TLS only | `https://api.wise.com` |


## Sandbox Environment

Sandbox is the testing environment that developers can use to build and test the application. This environment allows developers to make API requests without affecting the production environment. It is ideal for testing API requests, because it is similar (but not identical) to the production environment.

Sandbox is a test environment. Therefore, only test data should be included in this environment. Do not include real data in sandbox when building your integration, as the data is not subject to the same access controls as our production environment.

The Sandbox environment is designed for testing and does not support real money transfers, actual financial controls, or all currency routes available in our Production environment. Endpoints will also have more latency in Sandbox than in Production.

We provide a [Simulation API](/api-reference/simulation) to test money movement flows and other features, supporting the testing of webhooks and their payloads, which otherwise would not be possible.

| Security Type | URL |
|  --- | --- |
| mTLS enabled | `https://api-mtls.wise-sandbox.com` |
| TLS only | `https://api.wise-sandbox.com` |


Sandbox UI:

`https://wise-sandbox.com`

## What you can test in Sandbox 

There are some differences between the Production and Sandbox environments. If you are a partner and you run into issues testing in Sandbox, please fall back on the following features, countries, and currencies, as these are most stable. If there is an issue with one of the listed flows that is reported by a partner, we will open an internal incident and prioritise fixing it.

Please note that your implementation team will give you a test plan during your implementation if you are a partner, and you will need to adhere to that. This is simply a list of what is and isn't available, for reference.

Sandbox does not support load or performance testing.

### Supported Regions and Currencies in Sandbox

If you are testing a different currency or region in Sandbox and it does not work, please fall back on the following currencies and regions:

| - | Personal | Business |
|  --- | --- | --- |
| Regions | UK | UK (Sole Trader) |
| Currencies | GBP, USD, EUR | GBP, USD, EUR |


The currencies and regions apply to all the following features. Please reach out to us if there is a problem in these regions or currencies, and fall back on these if another region or currency you are testing does not work.

The following sections outline the functionality you can test in Sandbox if you are a partner.

### Access the API

1. Receive API client credentials from our integration success team.
2. Obtain a client credentials token for your application.
3. Obtain access/refresh tokens from one of our onboarding flows.
4. Refresh an access token from a refresh token.
5. Update keys and certificates for testing mTLS, JWS, and JWE.


### Onboard Customers to Sandbox

1. Create personal and business profiles.
2. Create multiple business profiles.
3. Check that a user exists over API.
4. Create a new user over API.
5. Create a new Wise account in the UI and link it via OAuth UI.
6. Disconnect and reconnect Wise accounts.
7. Create a new Wise account via API and claim it with a registration code.
8. Simulate the verification of one of the supported profile types.
9. Receive a verification status completed webhook event.


### Send Money

1. Create fixed target and fixed source quotes.
2. Get realistic but **not live rates**.
3. Create a recipient over the API.
4. Create a quote over the API.
5. Request transfer requirements for the above.
6. Create a transfer from the above recipient and quote.
7. Create a third-party transfer from the above recipient and quote.
8. Create a partner license transfer from the above recipient and quote.
9. Create a batch payment from the above recipients and quotes.
10. Initiate the fund of a transfer with balance or bulk settlement.
11. Subscribe to and receive transfer state change webhook events.
12. Subscribe to and receive transfer refund webhook events.
13. Simulate [transfer state changes](/api-reference/simulation/simulationtransferstatechange).


### Hold Money

1. Create a balance for a supported currency.
2. Convert balance amounts between supported currencies.


### Receive Money into a Balance

1. Simulate a [top up](/api-reference/simulation/simulationbalancetopup) of a balance for a supported currency.
2. Subscribe to and receive a balance update webhook event.
3. Retrieve a statement with a simulated top-up present.
4. See sent and received payments in a statement.
5. See balances updated with received transfers.


### Receive Money via the SWIFT network

1. Simulate an MT103 message.
2. Subscribe to and receive a balance update webhook event.
3. Retrieve a statement with a simulated top-up present.


### Order Cards

1. Check card order availability in supported regions.
2. Create a card order.
3. Set a card PIN.
4. Get card order requirements.
5. Retrieve a list of card orders.
6. Subscribe to and receive card order state change webhook events.


### Manage Cards

1. Retrieve a list of cards.
2. Change the status of a card.
3. Retrieve sensitive details of a card (PAN, PIN, CVV).
4. Subscribe to and receive card state change webhook events.


### Manage Spending Controls

1. Add and delete spending limits of the card per card.
2. Manage spending limits of the card per profile.
3. Add spending controls (MCC and currency) to all cards of the application.


### Test Card Transactions

1. Retrieve a card transaction.
2. Subscribe to and receive card transaction state change webhook events.
3. Simulate a card transaction authorization and clearing for Visa.
4. Simulate a card transaction authorization for Mastercard.


### Test Card Transaction Disputes

1. Submit a dispute.
2. Retrieve a dispute status.
3. Withdraw a dispute.
4. Subscribe to and receive dispute state change webhook events.


### Test Strong Customer Authentication

1. Add PIN as a factor.
2. Add Facetec biometric as a factor.
3. Add device fingerprinting as a factor.
4. Verify an SCA protexted action through PIN, Facetec, or device fingerprinting challenges.


## What you can't test in Sandbox 

The Sandbox environment has some limitations, specifically that it does not support real money transfers, actual financial controls, or all currency routes available in our Production environment.

If a feature isn't specified in the above lists, it can be assumed that we don't officially support it in Sandbox.

We cannot guarantee all currencies will work the same in Sandbox as Production. If you run into issues, please fall back to the currencies and regions shared above.

In addition, we do not support:

1. Any other UI screen not explicitly stated above.
2. Movement of real money.
3. Notifications by email or phone (2FA code is always 111111).
4. Verification and payment issue flows (including cases and disputes), other than what is required in the supported onboarding flows.
5. Real verification or onboarding rules/fincrime checks (including what evidences we may ask for in different regions) due to compliance constraints.
6. Any deprecated APIs/versions for features covered in above sections.
7. Strong customer authentication with SMS, phone call, and Whatsapp (SCA can be disabled via your client credentials).
8. Direct Debit/ACH funding for USD.
9. Mobile tokenization flows (ex. Google Pay, Apple Pay).
10. 3DS transactions.
11. Simulations of credit transactions for cards.
12. Card manufacturing flows.
13. Live rates.
14. Realistic refund amounts in refund webhooks (simulated values are used instead).