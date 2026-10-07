# Open Banking

Faster payments with seamless bank account connections

The Wise Open Banking API is aimed for Financially Regulated Third Party Providers who can prove their regulatory status either by being a member of the [Open Banking Directory](https://www.openbanking.org.uk/providers/directory/) or possessing an [eIDAS Certificate](#open-banking-sandbox-access). Third Parties or individuals who do not meet these requirements are welcome to check out our [Public API](/api-reference).

The Wise Open Banking API is a collection of RESTful APIs that enable Third Party Providers (TPPs) to access account information, initiate payments and confirm availability of funds on behalf of Wise customers. The API implementation follows the [Open Banking UK standard](https://standards.openbanking.org.uk/api-specifications/), and Wise is a registered member of the [Open Banking Directory](https://www.openbanking.org.uk/providers/directory/).

Through this API you can:

* Query account information if you're an Account Information Service Provider (AISP).
* Initiate payments and/or confirm the availability of funds if you're a Payment Initiation Service Provider (PISP).


We currently support version [3.1.11](https://openbankinguk.github.io/read-write-api-site3/v3.1.11/profiles/read-write-data-api-profile.html) of the Open Banking API.

Base Open Banking URL in Sandbox
https://openbanking.wise-sandbox.com

Base Open Banking URL in Production
https://openbanking.transferwise.com

## Contingency Mechanism 

We offer our bespoke **Connected Applications** API as a secondary API, acting as a contingency mechanism. The Connected Applications API provide the same set of functionality for both AISPs and PISPs as our Open Banking API does. In order to avoid any delays in switching over to the contingency mechanism during a major outage of the Open Banking API, we encourage TPPs to preemptively seek out registration to our contingency mechanism by reaching out to [openbanking@wise.com](mailto:openbanking@wise.com) and specifically requesting access to the contingency mechanism.

## Prerequisites 

There are a couple of things you should be aware of in order to connect to the Wise Open Banking API:

* Being a registered TPP under the Open Banking Directory will ease the integration process.
* We are using [mutualTLS](https://tools.ietf.org/html/draft-ietf-oauth-mtls-17) as the means for authentication. Moreover, the `CN` of your client certificate is expected to match the `clientId` under which you are registered.
* You need to register your client, before you'll be able to call any of the APIs. Check out the [Sandbox Access](#sandbox-access) first.


For a detailed description of requirements and supported algorithms please check out the Well-Known Open Banking URL.

Well-Known Open Banking URL in Sandbox
https://wise-sandbox.com/openbanking/.well-known/openid-configuration

Well-Known Open Banking URL in Production
https://wise.com/openbanking/.well-known/openid-configuration

## Dynamic Client Registration 

If you're a registered TPP at the [Open Banking Directory](https://www.openbanking.org.uk/) you can simply use our [Dynamic Client Registration](https://openbankinguk.github.io/dcr-docs-pub/v3.3/dynamic-client-registration.html) endpoint to self-onboard your organization using the Software Statement Assertion issued by the Open Banking Directory.

## Sandbox Access 

We highly recommend that you get started with connecting to our sandbox first, before moving on to production. To get started with the registration process drop us an email to [openbanking@wise.com](mailto:openbanking@wise.com).

### Open Banking Directory

If you're a registered TPP in the Open Banking Directory you will probably be using a Signing and a Transport certificates issued by
Open Banking. The accepted Open Banking certificates are the eIDAS-like [OBWAC and OBSeal certificates](https://openbanking.atlassian.net/wiki/spaces/DZ/pages/1322979574/Open+Banking+Directory+Usage+-+eIDAS+release+Production+-+v1.9#OpenBankingDirectoryUsage-eIDASrelease(Production)-v1.9-9.GenerateandmanageTransportandSigningCertificatesforOpenBankingETSIcertificates(OBWACandOBSeal)).

Legacy Open Banking Transport and Signing certificates are no longer supported after 30 June 2021.

**You can easily onboard by providing a Software Statement Assertion (SSA) generated in the Open Banking Directory.**

Please make sure to have your list of **Redirect Uri**-s correctly configured in your Software Statement, otherwise you'll not be able to go through the whole flow.

### eIDAS Certificates

In case you're using an eIDAS certificates instead of the ones issued by the Open Banking Directory just contact us at [openbanking@wise.com](mailto:openbanking@wise.com) to
see how we can move forward.

## Sandbox Test User 

You can sign up for a test user account here [https://wise-sandbox.com/register](https://wise-sandbox.com/register). The 2FA code used for any subsequent logins to the sandbox will always be `111111`.

You'll be asked to set up a developer account by filling in your profile information. Once this is done, you'll see that your newly created profile comes with a couple of test accounts opened and some test funds in them.

You do **NOT** need to create an API Token via the web interface in case your intention is to use this test user for the Open Banking flow.

## Sandbox Test Flow 

After you've successfully applied for the Sandbox Access and you've set up a Sandbox Test User you are ready to test the Open Banking flow.
For the purpose of this test flow let's assume that your TPP is an AISP and it's registered with the following details

| Client ID | Redirect URI | Authorized Scopes |
|  --- | --- | --- |
| ob-dummy-tpp | https://ob-dummy-tpp/redirect | accounts |


## 1. Create an Access Token 

As a first step you'll need to request an access token from the Token Endpoint.

### Request

**`POST https://openbanking.wise-sandbox.com/open-banking/auth/token`**

| Field | Description | Format |
|  --- | --- | --- |
| grant_type | OAuth Grant Type | `client_credentials` |
| scope | The requested scopes | Space separated list |
| client_id | The client ID in accordance with [RFC8705](https://datatracker.ietf.org/doc/html/rfc8705#section-2) | Text |


You must include the requested scope in your token request. As an AISP your requested scope will be `accounts`.

### Response

| Field | Description | Format |
|  --- | --- | --- |
| access_token | The access token | Text |
| expires_in | Access Token expiration time in seconds | Long |
| expires_at | Access Token expiration timestamp (UTC) | Text |
| scope | The scopes you have been given access to | Text |


Example Token Request
```shell
curl -X POST \
  https://openbanking.wise-sandbox.com/open-banking/auth/token \
  --cacert CA.pem --cert client.pem --key client.key \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&scope=accounts&client_id=ob-dummy-tpp'
```

Example Token Response
```json
{
    "access_token": "abcd1234-abcd-1234-abcd-abcdef123456",
    "token_type": "bearer",
    "expires_in": 6000,
    "scope": "accounts openbanking"
}
```

## 2. Create a Consent 

**`POST https://openbanking.wise-sandbox.com/open-banking/v3.1.11/aisp/account-access-consents`**

Using the `access-token` returned from [Creating an Access Token](/guides/developer/open-banking#create-access-token) you can create a new consent object. Use the authorization header:

`Authorization: Bearer xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx`

The payload of this request will look different depending on whether you're an AISP, PISP or CBPII. For an AISP you'll need to specify a set of permissions describing the access that you wish to gain on behalf of the end user.

### Permissions

For AISPs the list of supported permissions is:

* ReadAccountsBasic
* ReadAccountsDetail
* ReadBalances
* ReadTransactionsBasic
* ReadTransactionsCredits
* ReadTransactionsDebits
* ReadTransactionsDetail
* ReadDirectDebits


### Response

The response will be JSON data reflecting the newly created consent object. There are two important return values to highlight here.

* `Data.Status` will contain `AwaitingAuthorisation` because this consent has not been authorized by the user yet.
* `Data.ConsentId` will contain the unique identifier assigned to your consent object. Save this, as you'll need it later.


Example Create Consent
```shell
curl -X POST \
  https://openbanking.wise-sandbox.com/open-banking/v3.1.11/aisp/account-access-consents \
  --cacert CA.pem --cert client.pem --key client.key \
  -H 'Authorization: Bearer abcd1234-abcd-1234-abcd-abcdef123456' \
  -H 'Content-Type: application/json' \
  -d '{
  "Data": {
    "Permissions": [
      "ReadAccountsBasic", "ReadTransactionsBasic", "ReadTransactionsDebits"
    ]},
    "Risk": {}}'
```

Example Create Consent Response
```json
{
    "Data": {
        "Status": "AwaitingAuthorisation",
        "ConsentId": "123"
    }
}
```

## 3. User Flow 

At the moment we are only supporting the browser redirect flow ([Hybrid Flow](https://openbanking.atlassian.net/wiki/spaces/DZ/pages/83919096/Open+Banking+Security+Profile+-+Implementer+s+Draft+v1.1.2#OpenBankingSecurityProfile-Implementer'sDraftv1.1.2-HybridFlowRequestwithIntentId)) for authorizing the created consent.

The customer journey will start from the TPPs website from where a user action will trigger a redirect to the Wise Open Banking Authorization Endpoint

**`GET https://wise-sandbox.com/openbanking/authorize`**

| Parameter | Required | Description |
|  --- | --- | --- |
| response_type | Mandatory | code id_token |
| redirect_uri | Mandatory | One of the pre-registered redirect URIs |
| scope | Mandatory | Must include `openid` plus any requested scope |
| client_id | Mandatory | Pre-registered clientId of the TPP |
| request | Mandatory | JWT Request Object |
| state | Optional | If present, it must also be present in the JWT |
| nonce | Optional | If present, it must also be present in the JWT |


You can take a look at the example JWT request object on the right. Please note that:

* Every request parameter sent in the URL **must** also be present in the signed JWT.
* The `aud` claim should be correctly filled as `https://openbanking.wise-sandbox.com`
* The `openbanking_intent_id` **must** be filled with a valid `ConsentId` issued to the TPP.
* The JWT **must** be signed with a valid signing certificate.


Once the TPP redirects the user browser to the Authorization Endpoint the following things will happen in order:

1. User Login (use the username and password from the [Test User Registration](#open-banking#sandbox-test-user))
2. Pass 2FA challenge (Use the code `111111` in sandbox)
3. Select profile you wish to give access to (Business or Personal)
4. Review and Authorize Consent
5. Redirect back to TPP


As part of the last step, the user browser is redirected to the TPP with the following parameters

| Parameter | Required | Description |
|  --- | --- | --- |
| code | Mandatory | The `authorization_code` issued as the request of the request |
| id_token | Mandatory | Signed JWT containing details about the authorization |
| state | Optional | In case it was provided with the request |


Note that in case the authorization request fails either because of a validation error on the request, or because the end user drops off, we still redirect the user browser to the TPP with an error response of the following format:

| Field | Description | Format |
|  --- | --- | --- |
| error | Error code according to [RFC6749](https://tools.ietf.org/html/rfc6749#section-4.1.2.1) | Text |
| error_description | Detailed explanation of error | Text |


Example Authorization Request
```shell
https://wise-sandbox.com/openbanking/authorize?
  response_type=code%20id_token&
  redirect_uri=https://ob-dummy-tpp/redirect&
  scope=openid%20accounts&
  client_id=ob-dummy-tpp&
  state=state123&
  nonce=nonce123&
  request=eyJ0...sYjmjJg
```

Example Authorization JWT Response
```json
{
  "kid": "er84c2cYa6dAe57BV3278Pf",
  "alg": "PS256",
  "typ": "JWT"
},
{
   "scope" : "openid accounts",
   "response_type" : "code id_token",
   "sub" : "user_id",
   "claims" : {
      "id_token" : {
         "openbanking_intent_id" : {
            "essential" : true,
            "value" : "123"
         },
         "acr" : {
            "values" : [
               "urn:openbanking:psd2:sca",
               "urn:openbanking:psd2:ca"
            ],
            "essential" : true
         }
      },
      "userinfo" : {
         "openbanking_intent_id" : {
            "value" : "123",
            "essential" : true
         }
      }
   },
   "iss" : "ob-dummy-tpp",
   "client_id" : "ob-dummy-tpp",
   "aud" : "https://openbanking.wise-sandbox.com",
   "exp" : 2499287201,
   "iat" : 2499283601,
   "max_age" : 86400,
   "redirect_uri" : "https://ob-dummy-tpp/redirect"
}
```

## 4. Exchange Authorization Token 

Once you get the authorization `code` after the browser redirect, you'll have to call the Token Endpoint to exchange this for a valid access token.

### Request

**`POST https://openbanking.wise-sandbox.com/open-banking/auth/token`**

| Field | Description | Format |
|  --- | --- | --- |
| grant_type | OAuth Grant Type | `authorization_code` |
| redirect_uri | Pre-registered redirect Uri | URI |
| code | Authorization Code | Text |
| client_id | The client ID in accordance with [RFC8705](https://datatracker.ietf.org/doc/html/rfc8705#section-2) | Text |


### Response

| Field | Description | Format |
|  --- | --- | --- |
| access_token | The access token | Text |
| expires_in | Access Token expiration time in seconds | Long |
| expires_at | Access Token expiration timestamp (UTC) | Text |
| scope | The scopes you have been given access to | Text |
| refresh_token | Refresh Token for refreshing access token | Text |
| refresh_token_expires_in | Refresh Token expiration time in seconds | Long |
| refresh_token_expires_at | Refresh Token expiration timestamp (UTC) | Text |


Example Exchange Authorization Code for Access Token Request
```shell
curl -X POST \
  https://openbanking.wise-sandbox.com/open-banking/auth/token \
  --cacert CA.pem --cert client.pem --key client.key \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code&redirect_uri=https%3A%2F%2Fob-dummy-tpp%2Fredirect&code=abcdauthcode&client_id=ob-dummy-tpp'
```

Example Exchange Authorization Code for Access Token Response
```json
{
    "access_token": "zzzzzzzz-1111-2222-3333-zzzzzzzzzzzz",
    "token_type": "bearer",
    "refresh_token": "refreshr-efre-shre-fres-hrefreshrefr",
    "expires_in": 43199,
    "expires_at": "2025-04-11T03:43:28.148Z",
    "refresh_token_expires_in": 628639555,
    "refresh_token_expires_at": "2045-03-12T13:49:23.552Z",
    "scope": "accounts consent-id:123 openbanking openid"
}
```

## 5. Query the API 

With the `access-token` from [Authorization Code Flow](#open-banking#exchange-auth--token) used in the Authorization header, you'll be able to query the data endpoints.

`Authorization: Bearer xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx`

Query API Request
```shell
curl -X GET \
  https://openbanking.wise-sandbox.com/open-banking/v3.1.11/aisp/accounts \
  --cacert CA.pem --cert client.pem --key client.key \
  -H 'Authorization: Bearer zzzzzzzz-1111-2222-3333-zzzzzzzzzzzz' \
```

Query API Response
```json
{
    "Data": {
        "Account": [
            {
                "AccountId": "504",
                "Currency": "GBP",
                "AccountType": "Personal",
                "AccountSubType": "EMoney",
                "Account": [
                    {
                        "SchemeName": "UK.OBIE.SortCodeAccountNumber",
                        "Identification": "230xxx1000xxxx",
                        "Name": "John Smith (GBP)"
                    }
                ],
                "Servicer": {
                    "SchemeName": "UK.OBIE.BICFI",
                    "Identification": "TRWIGB22"
                }
            }
        ]
    }
}
```

## Token Endpoint 

**`POST /open-banking/auth/token`**

The Token Endpoint supports the grant types: `client_credentials`, `authorization_code` and `refresh_token`. Every request made to the Token Endpoint should include the `client_id` request parameter as described by [RFC6749](https://tools.ietf.org/html/rfc6749#section-4.1.2.1), this helps us bind the client certificate used for the request with your client_id.

## AISP Interfaces 

### Accounts

Querying the accounts endpoint will return all open currency accounts of the consented user.

**`GET /open-banking/v3.1.11/aisp/accounts`**

**`GET /open-banking/v3.1.11/aisp/accounts/{id}`**

**Note:** Not every multi-currency account opened in Wise has a unique set of local bank details attached to it. Therefore, it's expected that some of the currency accounts returned will have an empty `OBReadAccount6/Data/Account/Account`. We encourage AISPs to instead use the unique ID `OBReadAccount6/Data/Account/AccountId` for identifying different accounts. There's nothing inherently different between accounts with and without bank details, you can call the **Balances** and **Transactions** endpoints for either of them.

### Balances

Querying the balances endpoint will return the current balance of each supported currency.

**`GET /open-banking/v3.1.11/aisp/accounts/{id}/balances`**

### Transactions

Querying the transactions endpoint will return a list of transactions similar to what the users see in their balance statements from within the consented time window.
If the consent associated with the request is recent (less than 90 days old), we will allow requests to fetch transactions as old as you like. However, if the consent is older than 90 days, we will only allow requests to fetch transactions up to 90 days before the consent creation date, no matter what the requested or consented time frames are. This endpoint supports a query span of 450 days.

**`GET /open-banking/v3.1.11/aisp/accounts/{id}/transactions`**

To ensure full transparency about our transaction charges, details about fees are returned as separate DEBIT transactions with an attached reference to the original transaction. Fees represented this way will not be embedded in the original transaction amount.

**Migration Note**: If you are migrating from 3.1, IDs of the transactions returned by the v3.1.11 version are different from the ones returned by the v3.1 version. However, you should be able to reconcile the vast majority of the new and old transactions simply by matching the Ids contained in the `supplementaryData` fields of each of them.

Also note that in v3.1 the "fee split" feature was enabled for some TPPs while in v3.1.11 it's enabled by default for everyone.

### Direct Debits

Querying the direct debits endpoint will return the list of set up direct debits on a specific account

**`GET /open-banking/v3.1.11/aisp/accounts/{id}/direct-debits`**

## PISP Interfaces 

Every consent object created for initiating payments will have a **`CutOffDateTime`** attached which is set to be **30 minutes** after the creation of the consent. After the 30 minutes have lapsed, the Payment Order creation will be rejected.

We are supporting both **`UK.OBIE.SortCodeAccountNumber`** as well as **`UK.OBIE.IBAN`** for account identification.

At the moment we are only able to pass on a single reference to the debtor, which is **`Initiation/RemittanceInformation/Reference`** if present, or **`Initiation/EndToEndIdentification`** otherwise. The accepted size of the reference field varies based on the currency of the transfer. For EUR transfers you'll be able to leverage the full length of **35** characters of this field, however for GBP transfers this field length is restricted to a maximum of **18** characters. The reason for this restriction is also detailed in [OB Payment Message Format Mapping](https://openbankinguk.github.io/read-write-api-site3/v3.1.11/references/domestic-payment-message-formats.html). In case of FPS, this field gets mapped to both ISO8583 Field 62 as well as Field 120.

### Domestic Payments

**`POST /open-banking/v3.1.11/pisp/domestic-payments`**

**`GET /open-banking/v3.1.11/pisp/domestic-payments/{id}`**

The Domestic Payments endpoint can be used to initiate same currency transfers. You can initiate domestic payments in any of the [supported currencies](https://wise.com/multi-currency-account) by Wise, assuming the consenting user already holds an open account in the requested currency.

### International Payments

**`POST /open-banking/v3.1.11/pisp/international-payments`**

**`GET /open-banking/v3.1.11/pisp/international-payments/{id}`**

The International Payments endpoint can be used to initiate transfers where the source currency is different than the target currency. You can use it to initiate a payment with:

* Fixed **Source** Amount : `OBInternational3/InstructedAmount/Currency` and `OBInternational3/CurrencyOfTransfer` are different.
  * The source currency and amount are specified using `OBInternational3/InstructedAmount`. The currency can be any of the [supported currencies](https://wise.com/multi-currency-account) by Wise, assuming the consenting user already holds an open account in the requested currency.
  * The target currency of the transfer is specified using `OBInternational3/CurrencyOfTransfer`. The instructed amount will be converted to the CurrencyOfTransfer and sent out to the specified CreditorAccount.
* Fixed **Target** Amount : `OBInternational3/InstructedAmount/Currency` and `OBInternational3/CurrencyOfTransfer` are the same.
  * The source currency of the transfer can either be specified using `OBInternational3/ExchangeRateInformation/UnitCurrency`, or it can be left unspecified, allowing the Wise customer to choose one of their eligible currency accounts during the **authorization flow**. The customer's choice of source currency, the exchange rate used, and any additional charges are clearly communicated to the customer as well as reflected to the TPP via the Payment Resource.
  * The target currency and amount are specified using `OBInternational3/InstructedAmount`.


We are only supporting **INDICATIVE** `ExchangeRateInformation` during the creation of the International Payment Consent. The real exchange rate used, along with any fees will be clearly communicated to the customer during the consent authorization, as well as reflected to the PISP during the creation of the International Payment Resource.

## Updating Certificates 

As part of regular maintenance or other special cases client certificates need to be changed from time to time. Depending on your integration type you might be able to do this in an automated or a manual way.

### Open Banking Directory Participants

* **OBWAC/OBSeal** certificates are automatically added to your JWKS resource endpoints and you should be able to use your new certificates automatically as soon as they get associated with your Software Statement in the Directory.
* **eIDAS** certificates are treated similarly to OBWAC/OBSeal certificates as long as the issuing and root certificates haven't changed. If any certificate in your eIDAS trust chain has changed, you'll need to reach out to [openbanking@wise.com](mailto:openbanking@wise.com) for a manual update.


### Other Participants

In case you're not an Open Banking Directory Participant we will only be able to update your certificates manually. Please reach out to [openbanking@wise.com](mailto:openbanking@wise.com) well ahead of your previous certificate becoming invalid to allow for enough time for our support team to handle your request.

## Open Banking Performance and Availability Reporting 

The latest version of our Open Banking performance and availability report can be found [here](/assets/wise-open-banking-reporting-q2-2026.af3953c4ce1f26755d90add67bd0634e1539883b387400eccfe4c941d12fe704.6b9bfc58.pdf).