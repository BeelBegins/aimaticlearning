# SCA over API

Strong customer authentication (SCA) is a security measure that requires customers to provide multiple forms of identification to verify their identity before accessing sensitive information or performing high-risk transactions.

Wise provides endpoints that allow your customers to complete SCA, adding an extra layer of security to help reduce fraud. SCA is required for both high-risk and low-risk operations.

Examples of high-risk operations include:

- [Funding a transfer](/api-reference/transfer/transferfund)
- [3DS result notification](/api-reference/3ds/3dschallengeresultpost)
- [Funding a batch group](/api-reference/batch-group/batchgroupfund)


An operation like [retrieving a balance statement](/api-reference/balance-statement/balancestatementget) is considered low-risk.

You can access all SCA-protected endpoints using the authentication flow described below. However, we offer an alternative [SCA session](#sca-session) option, which allows users to perform lower-risk actions within a 5-minute window after successfully completing SCA once.

Before implementing SCA for your integration, be sure to discuss with your Implementation team to ensure you are using the right method for your use case.

## SCA methods 

Wise offers four authentication methods, categorized by authentication type. The SCA framework defines three authentication types:

- **Knowledge**: something the customer knows (like a password)
- **Possession**: something the customer owns (like a mobile phone)
- **Inherence**: something the customer is (like a fingerprint)


To perform a higher-risk operation, at least **two authentication methods of different types** must be registered with Wise. We recommend enrolling in a third authentication method to serve as an alternative in case one of the primary methods cannot be used.

| Method | Authentication type | Description |
|  --- | --- | --- |
| PIN | Knowledge | A 4-digit code only known by the customer. See the [pin example](#pin-example) section. |
| Device fingerprint | Possession | A unique identifier generated on the device that is tracked as a proof of authenticity showing that the device is owned by the customer.  See the [device fingerprint example](#device-fingerprint-example). |
| Phone-based OTP | Possession | An OTP code sent to a pre-registered phone number with Wise. See the [phone OTP example](#phone-otp-example). |
| FaceTec | Inherence | A digital representation of a customer's facial features used as biometric authentication. See the [facemap example](#facemap-example). |


## How it works 

An SCA flow is composed of two parts:

- **Enrollment**: First, determine which authentication factors you want your customers to use for accessing SCA-protected endpoints. Register these factors with Wise for each customer by calling the related SCA endpoints ([PIN](/api-reference/sca-pin), [Device fingerprints](/api-reference/sca-device-fingerprints), [OTP](/api-reference/sca-otp), or [Facemap](/api-reference/sca-facemaps)). They will serve as a reference when customers are required to complete SCA challenges.
- **Verification**: Certain high-risk endpoints require customers to verify their identity through SCA challenges. These endpoints remain inaccessible until a cleared authentication credential is provided. To clear this credential, the customer must successfully complete at least two challenges by verifying pre-enrolled authentication factors. Once the required challenges are passed, the authentication credential can be used to access the restricted resource.


### Enrollment 

The customer has to provide authentication factors that are used to prove their identity. These are commonly described by something they are, something they know, and something they have.

It's important to provide an onboarding flow in your application that sets up SCA enrollment for your end customers.

We strongly recommend providing fallback challenges for your customers in case they are unable to complete one of the primary challenge methods.

- [**PIN**](/api-reference/sca-pin/scapincreate):
For PIN-based authentication, it's important to collect the PIN information directly from the end customer through a secure client-side encryption method. This ensures that the PIN is not compromised during transmission.
- [**Device fingerprint**](/api-reference/sca-device-fingerprints/scadevicefingerprintcreate):
For device fingerprint-based authentication, it's important to use client-side encryption to collect the information directly from the device, and then forward the encrypted information securely to Wise. You should never persist the device fingerprint in any form. This ensures that the fingerprint is collected securely and accurately represents the user's device.
- [**Phone-based OTP**](/api-reference/sca-otp/usersecurityphonenumbercreate):
For phone-based OTP authentication, Wise offers multiple OTP methods such as SMS, Voice, and WhatsApp. Use a secure endpoint provided by Wise to update the end user's phone number, and perform phone number verification on your end before updating the information with Wise.
- [**FaceTec**](/api-reference/user-security/usersecurityfacemapenrol):
To implement FaceTec-based authentication, integrate with FaceTec and propagate the FaceMap to Wise for verification.


### Verification 

#### Restricted access endpoint

When your users are interacting with Wise, a high-risk endpoint might return a `403` status code along with these two fields in the response header:

- `x-2fa-approval-result` with value `REJECTED` indicating the request requires additional authentication.
- `x-2fa-approval` returning a unique identifier text that represent the authentication credentials (OTT) to be verified and cleared.


For more information on how to manage strong customer authentication using the response header values, refer to our [one-time token guide](/guides/developer/auth-and-security/one-time-token).

#### Get SCA challenges list

To obtain the list of challenges linked to the authentication credentials or to check the status of SCA challenges, use the [get status of a one time token endpoint](/api-reference/sca-ott/ottstatusgetv1) and set the `One-Time-Token` field in the request header.

#### Verify authentication factors

Use these endpoints to verify an authentication factor and clear a challenge:

- [PIN verification](/api-reference/sca-pin/ottpinverify)
- [Device fingerprint verification](/api-reference/sca-device-fingerprints/scadevicefingerprintverify)
- [Phone OTP verification](/api-reference/sca-otp/ottsmsverify)
- [FaceTec verification](/api-reference/sca-facemaps/scafacemapverify)


A verified authentication factor will return a successful HTTP status code. You can verify this by calling [get status of a one time token endpoint](/api-reference/sca-ott/ottstatusgetv1) and checking the `passed` field for the associated challenge.

Please note that for phone-based OTP authentication method, you have to call a [trigger endpoint](/api-reference/sca-otp/ottsmstrigger). This allows end users to choose when to send the OTP code and which phone number to send the message to.

#### Authorised access

When at least two authentication methods are verified, the authentication credential (OTT) is cleared.

You can now access the restricted endpoint by including the cleared authentication credential in the `x-2fa-approval` header of your request.

## SCA sessions 

An SCA session can be set up for low-risk operations. Once the customer successfully performs SCA, this session remains valid for 5 minutes until it expires. During this 5-minute period, customers can access any low-risk endpoints without performing SCA for each protected endpoint.

Please be aware that high-risk transactions, like payment transfers, may still require your users to perform SCA.

## Pin example 

This is a walkthrough of how to use PIN as an authentication method for SCA, including setting it up for your end customers.

All PIN-related endpoints use [Jose direct encryption](/guides/developer/auth-and-security) for secure data encryption in transit. It is essential to never persist this sensitive data in your application and only retrieve it directly from the customer.

### Setup

Use the [Create a PIN endpoint](/api-reference/sca-pin/scapincreate) to allow customers to set up their PIN with Wise directly.

This will allow customers to send their desired PIN to Wise in a direct encrypted manner, which does not expose the value to Wise.

### Verify flow

Once an end customer's PIN is created, it can be used as an **authentication factor** to clear an SCA challenge.

This image illustrates the interaction between the **partner** and **Wise**.

#### Step 1.

**Partner** makes an HTTP call to [get balance account statement](/api-reference/balance-statement/balancestatementget), which is an SCA protected endpoint.

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** rejects the request with status `403 Forbidden`.

Response - Get balance account statement
```text
HTTP/1.1 403 Forbidden
Date: Wed, 06 Dec 2023 08:57:34 GMT
x-2fa-approval: bb676aeb-7c4d-4930-bb55-ab949fd3fd87
x-2fa-approval-result: REJECTED
...other headers
```

#### Step 2.

**Partner** [gets status of a one time token](/api-reference/sca-ott/ottstatusgetv1) to get all required challenges to clear this OTT.

**Request - Get status of one time token**

```shell curl
curl -i -X GET \
  https://api.wise-sandbox.com/v1/identity/one-time-token/status \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'One-Time-Token: string' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns a [one time token](/api-reference/sca-ott/ottstatusgetv1) that describes all required challenges.

For the complete list of challenges available, refer to [ChallengeType](/api-reference/sca-ott).

Response - Get status of one time token
```json
{
  "oneTimeTokenProperties": {
    "oneTimeToken": "bb676aeb-7c4d-4930-bb55-ab949fd3fd87",
    "challenges": [
      {
        "primaryChallenge": {
          "type": "PIN",
          "viewData": {
            "attributes": {
              "userId": 6146956
            }
          }
        },
        "alternatives": [],
        "required": true,
        "passed": false
      }
    ],
    "validity": 3600,
    "actionType": "BALANCE__GET_STATEMENT",
    "userId": 6146956
  }
}
```

#### Step 3.

**Partner** [verifies PIN](/api-reference/sca-pin/scapinverify) by passing the OTT.

**Request - Verify PIN**

```bash cURL
curl -i -X POST \
  https://api.wise-sandbox.com/v1/one-time-token/pin/verify \
  -H 'Authorization: Bearer <YOUR_TOKEN_HERE>' \
  -H 'Accept: application/jose+json' \
  -H 'Accept-Encoding: identity' \
  -H 'Content-Type: application/jose+json' \
  -H 'Content-Encoding: identity' \
  -H 'X-TW-JOSE-Method: jwe' \
  -H 'One-Time-Token: <one time token>' \
  -d 'eyJlbmMiOiJBMjU2R0NNIiwi...'
```

**Wise** returns [one time token properties](/api-reference/sca-ott/ottstatusgetv1) after a successful pin verification.

- Assuming that the **challenges** array field is empty, indicating that the OTT is now usable.
- If you are unsure, you can always [get status of a one time token](/api-reference/sca-ott/ottstatusgetv1) again.
- It is possible that the **challenges** array returns type of challenge. In that case, please perform the verification flow as written in our guides.


**Response - Verify PIN**

```json 200 application/jose+json
eyJlbmMiOiJBMjU2R0NNIiwi...
```

```json 429 application/json
{}
```

#### Step 4.

**Partner** calls the Get Balance Statement endpoint with the approved OTT.

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns the balance account statement.

**Response - Get balance account statement**

```json 200 application/json
{
  "accountHolder": {
    "type": "PERSONAL",
    "address": {
      "addressFirstLine": "Veerenni 24",
      "city": "Tallinn",
      "postCode": "12112",
      "stateCode": "",
      "countryName": "Estonia"
    },
    "firstName": "Oliver",
    "lastName": "Wilson"
  },
  "issuer": {
    "name": "TransferWise Ltd.",
    "firstLine": "56 Shoreditch High Street",
    "city": "London",
    "postCode": "E1 6JJ",
    "stateCode": "",
    "country": "United Kingdom"
  },
  "bankDetails": {},
  "transactions": [
    {
      "type": "DEBIT",
      "date": "2018-04-30T08:47:05.832Z",
      "amount": {
        "value": -7.76,
        "currency": "EUR"
      },
      "totalFees": {
        "value": 0.04,
        "currency": "EUR"
      },
      "details": {
        "type": "CARD",
        "description": "Card transaction of 6.80 GBP issued by Tfl.gov.uk/cp TFL TRAVEL CH",
        "amount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "senderName": "HEIN LAURI",
        "senderAccount": "EE76 1700 0170 0049 6704",
        "paymentReference": "SVWZ+topup card",
        "category": "Transportation Suburban and Loca",
        "merchant": {
          "name": "Tfl.gov.uk/cp",
          "firstLine": "string",
          "postCode": "SW1H 0TL",
          "city": "TFL TRAVEL CH",
          "state": "",
          "country": "GB",
          "category": "Transportation Suburban and Loca"
        },
        "sourceAmount": {
          "value": 8.69,
          "currency": "GBP"
        },
        "targetAmount": {
          "value": 9.94,
          "currency": "EUR"
        },
        "fee": {
          "value": 0.03,
          "currency": "GBP"
        },
        "rate": 1.147806
      },
      "exchangeDetails": {
        "forAmount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "rate": 0
      },
      "runningBalance": {
        "value": 16.01,
        "currency": "EUR"
      },
      "referenceNumber": "CARD-249281"
    }
  ],
  "endOfStatementBalance": {
    "value": 9.94,
    "currency": "EUR"
  },
  "query": {
    "intervalStart": "2018-03-01T00:00:00Z",
    "intervalEnd": "2018-04-30T23:59:59.999Z",
    "currency": "EUR",
    "accountId": 64
  }
}
```

```json 429 application/json
{}
```

## Device fingerprint example 

This is a walkthrough of how to use device fingerprint as an authentication method for SCA, including setting it up for your end customers.

All related endpoints use [Jose direct encryption](/guides/developer/auth-and-security) for secure data encryption in transit. It is essential to never persist this sensitive data in your application and only retrieve it directly from the customer.

### Setup

Use the [Create a device fingerprint endpoint](/api-reference/sca-device-fingerprints/scadevicefingerprintcreate) to allow customers to set up their device fingerprint with Wise directly.

This will allow customers to send their device fingerprint to Wise in a direct encrypted manner to be used as an authentication method.

Wise allows up to three device fingerprints to be registered at any given time. If your customer has more than three devices connected to the account, you will need to delete unused device fingerprints using our [delete fingerprint endpoint](/api-reference/sca-device-fingerprints/scadevicefingerprintdelete).

### Verify flow

When an end customer's device fingerprint is set up, it can be used as an **authentication factor** to clear an SCA challenge.

The image below illustrates the interaction between the **Partner** and **Wise**.

#### Step 1.

**Partner** makes an HTTP call to the [get balance account statement endpoint](/api-reference/balance-statement/balancestatementget), which is an [SCA protected endpoint](/guides/developer/auth-and-security/sca-and-2fa).

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** rejects the request with status `403 Forbidden`.

Response - Get balance account statement
```text
HTTP/1.1 403 Forbidden
Date: Wed, 06 Dec 2023 08:57:34 GMT
x-2fa-approval: bb676aeb-7c4d-4930-bb55-ab949fd3fd87
x-2fa-approval-result: REJECTED
...other headers
```

#### Step 2.

**Partner** [gets status of a one time token](/api-reference/sca-ott/ottstatusgetv1) to get all required challenges to clear this OTT.

**Request - Get status of one time token**

```shell curl
curl -i -X GET \
  https://api.wise-sandbox.com/v1/identity/one-time-token/status \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'One-Time-Token: string' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns a [one time token](/api-reference/sca-ott/ottstatusgetv1) that describes all required challenges.

For the complete list of challenges available, refer to [ChallengeType](/api-reference/sca-ott).

Response - Get status of one time token
```json
{
  "oneTimeTokenProperties": {
    "oneTimeToken": "bb676aeb-7c4d-4930-bb55-ab949fd3fd87",
    "challenges": [
      {
        "primaryChallenge": {
          "type": "PARTNER_DEVICE_FINGERPRINT",
          "viewData": {
            "attributes": {
              "userId": 6146956
            }
          }
        },
        "alternatives": [],
        "required": true,
        "passed": false
      }
    ],
    "validity": 3600,
    "actionType": "BALANCE__GET_STATEMENT",
    "userId": 6146956
  }
}
```

#### Step 3.

**Partner** [verifies device fingerprint](/api-reference/sca-device-fingerprints/scadevicefingerprintverify) by passing the OTT.

Request - Verify device fingerprint
```shell
curl -X POST https://api.wise-sandbox.com/one-time-token/partner-device-fingerprint/verify \
     -H 'Authorization: Bearer <your api token>' \
     -H 'Accept: application/jose+json' \
     -H 'Accept-Encoding: identity' \
     -H 'Content-Type: application/jose+json' \
     -H 'Content-Encoding: identity' \
     -H 'X-TW-JOSE-Method: jwe' \
     -H 'One-Time-Token: <one time token>'
     -d 'eyJlbmMiOiJBMjU2R0NNIiwi...'
```

**Wise** returns [one time token properties](/api-reference/sca-ott/ottstatusgetv1)  after successful verification.

- Assuming that the **challenges** array field is empty, indicating that the OTT is now usable.
- If you are unsure, you can always [get status of a one time token](/api-reference/sca-ott/ottstatusgetv1) again.
- It is possible that the **challenges** array returns type of challenge. In that case, perform the verification flow as written in our guides.


Response - Verify device fingerprint
```text
eyJlbmMiOiJBMjU2R0NNIiwi...
```

#### Step 4.

**Partner** calls the Get Balance Statement endpoint with the approved OTT.

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns the balance account statement.

**Response - Get balance account statement**

```json 200 application/json
{
  "accountHolder": {
    "type": "PERSONAL",
    "address": {
      "addressFirstLine": "Veerenni 24",
      "city": "Tallinn",
      "postCode": "12112",
      "stateCode": "",
      "countryName": "Estonia"
    },
    "firstName": "Oliver",
    "lastName": "Wilson"
  },
  "issuer": {
    "name": "TransferWise Ltd.",
    "firstLine": "56 Shoreditch High Street",
    "city": "London",
    "postCode": "E1 6JJ",
    "stateCode": "",
    "country": "United Kingdom"
  },
  "bankDetails": {},
  "transactions": [
    {
      "type": "DEBIT",
      "date": "2018-04-30T08:47:05.832Z",
      "amount": {
        "value": -7.76,
        "currency": "EUR"
      },
      "totalFees": {
        "value": 0.04,
        "currency": "EUR"
      },
      "details": {
        "type": "CARD",
        "description": "Card transaction of 6.80 GBP issued by Tfl.gov.uk/cp TFL TRAVEL CH",
        "amount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "senderName": "HEIN LAURI",
        "senderAccount": "EE76 1700 0170 0049 6704",
        "paymentReference": "SVWZ+topup card",
        "category": "Transportation Suburban and Loca",
        "merchant": {
          "name": "Tfl.gov.uk/cp",
          "firstLine": "string",
          "postCode": "SW1H 0TL",
          "city": "TFL TRAVEL CH",
          "state": "",
          "country": "GB",
          "category": "Transportation Suburban and Loca"
        },
        "sourceAmount": {
          "value": 8.69,
          "currency": "GBP"
        },
        "targetAmount": {
          "value": 9.94,
          "currency": "EUR"
        },
        "fee": {
          "value": 0.03,
          "currency": "GBP"
        },
        "rate": 1.147806
      },
      "exchangeDetails": {
        "forAmount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "rate": 0
      },
      "runningBalance": {
        "value": 16.01,
        "currency": "EUR"
      },
      "referenceNumber": "CARD-249281"
    }
  ],
  "endOfStatementBalance": {
    "value": 9.94,
    "currency": "EUR"
  },
  "query": {
    "intervalStart": "2018-03-01T00:00:00Z",
    "intervalEnd": "2018-04-30T23:59:59.999Z",
    "currency": "EUR",
    "accountId": 64
  }
}
```

```json 429 application/json
{}
```

## Phone OTP example 

This is a walkthrough of how to use phone as an authentication method for SCA, including setting it up for your end customers.

Wise provides three methods for delivering one-time password (OTP) codes to your end-user devices:

1. SMS
2. WhatsApp
3. Voice


### Setup

Please note that you are responsible for managing the lifecycle of the phone number so Wise can send OTP codes to your end customers when necessary.

| Lifecycle | Description |
|  --- | --- |
| [Create](/api-reference/sca-otp/usersecurityphonenumbercreate) | After successfully onboarding a customer and verifying their phone number through your application, create the respective verified phone number with Wise. |
| [Delete](/api-reference/sca-otp/usersecurityphonenumberdelete) | If customer has removed or lost access to the phone number, delete the respective phone number with Wise. |


### Verify flow

When an end customer's phone number is set up, it can be used as an **authentication factor** to clear an SCA challenge.

The image below illustrates the interaction between the **Partner** and **Wise**.

#### Step 1.

**Partner** makes an HTTP call to the [get balance account statement endpoint](/api-reference/balance-statement/balancestatementget), which is an [SCA protected endpoint](/guides/developer/auth-and-security/sca-and-2fa).

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** rejects the request with status `403 Forbidden`.

Response - Get balance account statement
```text
HTTP/1.1 403 Forbidden
Date: Wed, 06 Dec 2023 08:57:34 GMT
x-2fa-approval: bb676aeb-7c4d-4930-bb55-ab949fd3fd87
x-2fa-approval-result: REJECTED
...other headers
```

#### Step 2.

**Partner** [gets status of a one time token](/api-reference/sca-ott/ottstatusgetv1) to get all required challenges to clear this OTT.

**Request - Get status of one time token**

```shell curl
curl -i -X GET \
  https://api.wise-sandbox.com/v1/identity/one-time-token/status \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'One-Time-Token: string' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns a [one time token](/api-reference/sca-ott/ottstatusgetv1) that describes all required challenges.

For the complete list of challenges available, refer to [ChallengeType](/api-reference/sca-ott).

The `alternatives` field suggests that the end user has the option to select a trigger channel to receive the OTP code, rather than receiving it via the default channel.

Response - Get status of one time token
```json
{
  "oneTimeTokenProperties": {
    "oneTimeToken": "bb676aeb-7c4d-4930-bb55-ab949fd3fd87",
    "challenges": [
      {
        "primaryChallenge": {
          "type": "SMS",
          "viewData": {
            "attributes": {
              "userId": 6146956
            }
          }
        },
        "alternatives": [
          {
            "type": "WHATSAPP",
            "viewData": {
              "attributes": {
                "userId": 6146956
              }
            }
          },
          {
            "type": "VOICE",
            "viewData": {
              "attributes": {
                "userId": 6146956
              }
            }
          }
        ],
        "required": true,
        "passed": false
      }
    ],
    "validity": 3600,
    "actionType": "BALANCE__GET_STATEMENT",
    "userId": 6146956
  }
}
```

#### Step 3.

**Partner** [verifies otp](/api-reference/sca-otp/ottsmsverify) by passing the OTT.

**Request - Verify SMS**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/one-time-token/sms/verify \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'One-Time-Token: string' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "otpCode": "111111"
  }'
```

**Wise** returns [one time token properties](/api-reference/sca-ott/ottstatusgetv1) after a successful OTP code verification.

- Assuming that the **challenges** array field is empty, indicating that the OTT is now usable.
- If you are unsure, you can always [get status of a one time token](/api-reference/sca-ott/ottstatusgetv1) again.
- It is possible that the **challenges** array returns type of challenge. In that case, please perform the verification flow as written in our guides.


**Response - Verify SMS**

```json 200 application/json
{
  "oneTimeTokenProperties": {
    "oneTimeToken": "9f5f5812-2609-4e48-8418-b64437c0c7cd",
    "challenges": [],
    "validity": 3600
  }
}
```

```json 429 application/json
{}
```

#### Step 4.

**Partner** calls the Get Balance Statement endpoint with the approved OTT.

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns the balance account statement.

**Response - Get balance account statement**

```json 200 application/json
{
  "accountHolder": {
    "type": "PERSONAL",
    "address": {
      "addressFirstLine": "Veerenni 24",
      "city": "Tallinn",
      "postCode": "12112",
      "stateCode": "",
      "countryName": "Estonia"
    },
    "firstName": "Oliver",
    "lastName": "Wilson"
  },
  "issuer": {
    "name": "TransferWise Ltd.",
    "firstLine": "56 Shoreditch High Street",
    "city": "London",
    "postCode": "E1 6JJ",
    "stateCode": "",
    "country": "United Kingdom"
  },
  "bankDetails": {},
  "transactions": [
    {
      "type": "DEBIT",
      "date": "2018-04-30T08:47:05.832Z",
      "amount": {
        "value": -7.76,
        "currency": "EUR"
      },
      "totalFees": {
        "value": 0.04,
        "currency": "EUR"
      },
      "details": {
        "type": "CARD",
        "description": "Card transaction of 6.80 GBP issued by Tfl.gov.uk/cp TFL TRAVEL CH",
        "amount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "senderName": "HEIN LAURI",
        "senderAccount": "EE76 1700 0170 0049 6704",
        "paymentReference": "SVWZ+topup card",
        "category": "Transportation Suburban and Loca",
        "merchant": {
          "name": "Tfl.gov.uk/cp",
          "firstLine": "string",
          "postCode": "SW1H 0TL",
          "city": "TFL TRAVEL CH",
          "state": "",
          "country": "GB",
          "category": "Transportation Suburban and Loca"
        },
        "sourceAmount": {
          "value": 8.69,
          "currency": "GBP"
        },
        "targetAmount": {
          "value": 9.94,
          "currency": "EUR"
        },
        "fee": {
          "value": 0.03,
          "currency": "GBP"
        },
        "rate": 1.147806
      },
      "exchangeDetails": {
        "forAmount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "rate": 0
      },
      "runningBalance": {
        "value": 16.01,
        "currency": "EUR"
      },
      "referenceNumber": "CARD-249281"
    }
  ],
  "endOfStatementBalance": {
    "value": 9.94,
    "currency": "EUR"
  },
  "query": {
    "intervalStart": "2018-03-01T00:00:00Z",
    "intervalEnd": "2018-04-30T23:59:59.999Z",
    "currency": "EUR",
    "accountId": 64
  }
}
```

```json 429 application/json
{}
```

## Facemap Example 

This is a walkthrough of how to use FaceMap as an authentication method for SCA, including setting it up for your end customers. By following these steps, you can enable secure and convenient authentication for your users while meeting the regulatory requirements for online transactions.

### Limitations

1. Wise only supports the [3D FaceMap Interoperability Between Organizations](https://dev.facetec.com/identity-issuers), which requires integration with FaceTec. This means that your organization must also be a consumer of FaceTec services in order to enable this flow.
2. This authentication method will only be enabled upon request. Contact your implementation manager to request.


### Setup

Wise leverages the [FaceTec import functionality](https://dev.facetec.com/api-guide#import-3d-facemap) when receiving 3D FaceMaps from customers, enabling seamless integration and secure authentication processes.

The image below illustrates the interaction between **frontend**, **backend** and **Wise**.

#### Step 1.

**Frontend** makes an HTTP call to enrol FaceMap to your **backend** application.

This is where the customer submits a FaceScan to your application for FaceTec [enrolment](https://dev.facetec.com/api-guide#enrollment-3d).

#### Step 2.

**Backend** makes an HTTP call to [get Wise's FaceTec public key](/api-reference/facetec/facetecpublickeyget) to acquire the public key needed to do a [FaceTec export](https://dev.facetec.com/api-guide#export-3d-facemap).

**Request - Get FaceTec public key**

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/facetec/public-key \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns the public key to **backend** in plain text. You are encouraged to cache this public key to minimize latency, as it is not subject to frequent rotation.

**Response - Get FaceTec public key**

```clike 200 text/plain
-----BEGIN PUBLIC KEY-----
Public Key Content
-----END PUBLIC KEY-----
```

```json 429 application/json
{}
```

The **backend** application will utilize the previously stored FaceMap and the acquired Wise's FaceTec public key as input parameters for the [export function](https://dev.facetec.com/api-guide#export-3d-facemap) provided by FaceTec.

Upon a successful export, we will possess an **encrypted FaceMap** that is ready to be transmitted to Wise.

#### Step 3.

**Backend** makes an HTTP call to [Enrol FaceMap](/api-reference/user-security/usersecurityfacemapenrol).

**Request - Enrol FaceMap**

```shell curl
curl -i -X POST \
  https://api.wise-sandbox.com/v1/user/facemap/enrol \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "faceMap": "string"
  }'
```

- **Wise** responds with a `204 - No Content` status code upon successful enrollment.
  - Please note that a `409 - Conflict` response indicates that the enrollment already exists and cannot be repeated.
- **Backend** should responds with a successful HTTP status code to customer upon successful enrollment.


### Verify flow

This guide uses the [retrieving balance account statement endpoint](/api-reference/balance-statement/balancestatementget) as an example.

The image below illustrates the interaction between **frontend**, **backend**, and **Wise**.

#### Step 1.

**Frontend** makes an HTTP call to the [get balance account statement endpoint](/api-reference/balance-statement/balancestatementget) which is an [SCA protected endpoint](/guides/developer/auth-and-security).

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** rejects the request with status `403 Forbidden`.

Response - Get balance account statement
```text
HTTP/1.1 403 Forbidden
Date: Wed, 06 Dec 2023 08:57:34 GMT
x-2fa-approval: bb676aeb-7c4d-4930-bb55-ab949fd3fd87
x-2fa-approval-result: REJECTED
...other headers
```

#### Step 2.

**Frontend** [gets status of a one time token](/api-reference/sca-ott/ottstatusgetv1) to get all required challenges to clear this OTT.

**Request - Get status of one time token**

```shell curl
curl -i -X GET \
  https://api.wise-sandbox.com/v1/identity/one-time-token/status \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'One-Time-Token: string' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns a [one time token](/api-reference/sca-ott/ottstatusgetv1) that describes all required challenges.

For the complete list of challenges available, refer to [ChallengeType](/api-reference/sca-ott).

Response - Get status of one time token
```json
{
   "oneTimeTokenProperties": {
      "oneTimeToken": "bb676aeb-7c4d-4930-bb55-ab949fd3fd87",
      "challenges": [
         {
            "primaryChallenge": {
               "type": "FACE_MAP",
               "viewData": {
                  "attributes": {
                     "userId": 6146956
                  }
               }
            },
            "alternatives": [],
            "required": true,
            "passed": false
         }
      ],
      "validity": 3600,
      "actionType": "BALANCE__GET_STATEMENT",
      "userId": 6146956
   }
}
```

#### Step 3.

**Frontend** makes an HTTP call to **backend** to perform a [match 3d 3d](https://dev.facetec.com/api-guide#match-3d-3d) check.

**Backend** makes an HTTP call to [get Wise's FaceTec public key](/api-reference/facetec/facetecpublickeyget) to acquire the public key needed to do a FaceTec [export](https://dev.facetec.com/api-guide#export-3d-facemap).

**Request - Get FaceTec public key**

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/facetec/public-key \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns the public key to **backend** in plain text. You are encouraged to cache this public key to minimize latency, as it is not subject to frequent rotation.

**Response - Get FaceTec public key**

```clike 200 text/plain
-----BEGIN PUBLIC KEY-----
Public Key Content
-----END PUBLIC KEY-----
```

```json 429 application/json
{}
```

The **backend** application will utilize the previously stored FaceMap and the acquired Wise's FaceTec public key as input parameters for the [export function](https://dev.facetec.com/api-guide#export-3d-facemap) provided by FaceTec.

Upon a successful export, we will possess an **encrypted FaceMap** that is ready to be transmitted to Wise.

#### Step 4.

**Backend** makes an HTTP call to [Verify FaceMap](/api-reference/sca-facemaps/scafacemapverify).

**Request - Verify FaceMap**

```shell curl
curl -i -X POST \
  https://api.wise-sandbox.com/v1/one-time-token/facemap/verify \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'One-Time-Token: string' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "faceMap": "<base64_encoded_string>"
  }'
```

**Wise** returns [one time token properties](/api-reference/sca-ott/ottstatusgetv1) after a successful FaceMap verification.

- Assuming that the **challenges** array field is empty, indicating that the OTT is now usable.
- If you are unsure, you can always [get status of a one time token](/api-reference/sca-ott/ottstatusgetv1) again.
- Depending on the action and conditions, the **challenges** array may return one or more challenge types. In that case, please perform the verification flow as written in our guides.


**Response - Verify FaceMap**

```json 200 application/json
{
  "oneTimeTokenProperties": {
    "oneTimeToken": "9f5f5812-2609-4e48-8418-b64437c0c7cd",
    "challenges": [],
    "validity": 3600
  }
}
```

```json 429 application/json
{}
```

**Backend** should respond with a successful HTTP status code to customer upon successful verification.

#### Step 5.

**Frontend** calls the Get Balance Statement endpoint with the approved OTT.

**Request - Get balance account statement**

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/profiles/12345/balance-statements/64/statement.json?currency=EUR&intervalStart=2025-03-01T00%3A00%3A00.000Z&intervalEnd=2025-04-30T23%3A59%3A59.999Z&type=COMPACT&statementLocale=en' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

**Wise** returns the balance account statement.

**Response - Get balance account statement**

```json 200 application/json
{
  "accountHolder": {
    "type": "PERSONAL",
    "address": {
      "addressFirstLine": "Veerenni 24",
      "city": "Tallinn",
      "postCode": "12112",
      "stateCode": "",
      "countryName": "Estonia"
    },
    "firstName": "Oliver",
    "lastName": "Wilson"
  },
  "issuer": {
    "name": "TransferWise Ltd.",
    "firstLine": "56 Shoreditch High Street",
    "city": "London",
    "postCode": "E1 6JJ",
    "stateCode": "",
    "country": "United Kingdom"
  },
  "bankDetails": {},
  "transactions": [
    {
      "type": "DEBIT",
      "date": "2018-04-30T08:47:05.832Z",
      "amount": {
        "value": -7.76,
        "currency": "EUR"
      },
      "totalFees": {
        "value": 0.04,
        "currency": "EUR"
      },
      "details": {
        "type": "CARD",
        "description": "Card transaction of 6.80 GBP issued by Tfl.gov.uk/cp TFL TRAVEL CH",
        "amount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "senderName": "HEIN LAURI",
        "senderAccount": "EE76 1700 0170 0049 6704",
        "paymentReference": "SVWZ+topup card",
        "category": "Transportation Suburban and Loca",
        "merchant": {
          "name": "Tfl.gov.uk/cp",
          "firstLine": "string",
          "postCode": "SW1H 0TL",
          "city": "TFL TRAVEL CH",
          "state": "",
          "country": "GB",
          "category": "Transportation Suburban and Loca"
        },
        "sourceAmount": {
          "value": 8.69,
          "currency": "GBP"
        },
        "targetAmount": {
          "value": 9.94,
          "currency": "EUR"
        },
        "fee": {
          "value": 0.03,
          "currency": "GBP"
        },
        "rate": 1.147806
      },
      "exchangeDetails": {
        "forAmount": {
          "value": 6.8,
          "currency": "GBP"
        },
        "rate": 0
      },
      "runningBalance": {
        "value": 16.01,
        "currency": "EUR"
      },
      "referenceNumber": "CARD-249281"
    }
  ],
  "endOfStatementBalance": {
    "value": 9.94,
    "currency": "EUR"
  },
  "query": {
    "intervalStart": "2018-03-01T00:00:00Z",
    "intervalEnd": "2018-04-30T23:59:59.999Z",
    "currency": "EUR",
    "accountId": 64
  }
}
```

```json 429 application/json
{}
```