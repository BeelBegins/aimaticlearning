# About profiles

In the Wise Platform API, a **profile** is the core resource representing a distinct legal and financial identity. Every transactional resource across the platform—including quotes, recipients, balance accounts, multi-currency account details, and transfers—is scoped to a specific `profileId`.

Understanding how profiles are structured, linked, and authenticated is essential for building an integration that satisfies global regulatory requirements, sanctions screening, and financial settlement flows.

## The profile resource

A profile establishes **legal ownership** over financial activities within Wise Platform. It decouples the authenticated API caller from the legal entity originating or holding funds.

Wise uses the `profileId` to:

- Identify the originator of payments
- Enforce KYC/AML rules
- Ensure other resources (like recipients, card tokens, and currency balances) are private to the profile that created them
- Ensure thresholds, volume caps, and enhanced due diligence (EDD) triggers


### Profile types

Wise Platform supports two distinct profile types: personal and business

- **Personal profiles**: Represent a natural person (individual).
  - Key attributes: Full legal name, date of birth, residential address, personal email, phone number, and occupation.
  - Verification scope: Identity document verification (passport, driver's licence, national ID) and proof of residential address.
- **Business profiles**: Represents a legal entity (Ltd, LLC, etc).
  - Key attributes: Registered company name, registration number, company type (for example, `LIMITED_COMPANY`, `SOLE_TRADER`, `LLC`), registered address, industry classification category codes, and website.
  - Authorised representative relationship: A business entity cannot act on its own behalf. Every business profile must reference an authorised representative (director, controlling person, or account administrator).
  - Verification Scope: Company registry verification, Ultimate Beneficial Owner (UBO) screening, and verification of the authorised representative.


## Profiles and integration models

Creating and managing profiles differs depending on your integration model.

| Integration model | Profile description |
|  --- | --- |
| Embedded solutions | These partners create a unique profile for each of their end users (personal or business).- Each profile undergoes KYC, either performed by Wise (using a hosted or API approach) or by the partner (if licensed to do so).
- Transfers belong to the customer’s profile while settlement can be funded via the partner’s prefunded operational balance or customer balance.

 |
| Enterprise partners | These partners operate under one primary business profile (representing the corporate entity itself), created during their partner account setup process.- Wise verifies the business profile during initial onboarding.
- The enterprise funds transfers directly from its own Wise multi-currency balances or linked corporate bank accounts. End recipients are created as external payees attached to the corporate profile.

 |
| Correspondent partners | The financial institution operates under business profile(s) representing the partner entity, created during their partner account setup process.- Wise verifies the business profile(s) during initial onboarding.
- The FI passes the underlying end-customer details as **originator metadata** directly within the payment instruction, rather than creating customer profiles for every indirect remitter.
- Funds are settled via net settlement or prefunded clearing via the partner's NOSTRO account.

 |


## Data requirements

Some regions demand more profile data to be compliant with local regulations. Requirements are based on jurisdiction of operation and customer demographics of your bank or other financial institution. *We are currently in the process of documenting region-specific profile data requirements. These will be published soon*!

## Profile verification

Wise is obliged to verify the identity of personal and business profiles as part of our *Know Your Customer* (KYC) policy. We must be satisfied that we know our customers well enough before conducting financial transactions with them.

For Correspondent and Enterprise partners, Wise verifies the business profile you create during account setup and informs you when the profile is verified and ready to use.

Embedded solutions partners, however, create unique profiles for each of their end users and each of these profiles is subject to KYC verification. How this occurs depends on your KYC approach, as defined in your partner contract. Partners licensed to perform their own KYC verify their customers using their own process. Partners not licensed to perform their own KYC use Wise's customer onboarding flow.

### Checking verification status

You can check the verification status of a profile using two methods:

- Subscribe to the [verification state change webhook](/api-reference/webhook-event/eventprofilesverificationstatechange) to be notified when a profile status has changed.
- Send a request to the [Check profile verification status endpoint](/api-reference/profile/profileverificationstatuscheck).


#### Verification state change webhook

Create an application webhook subscription with the `trigger_on` value set to `profiles#verification-state-change`.

```bash
curl -i -X POST \
  'https://api.wise.com/2026Q3/applications/{clientKey}/subscriptions' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "name": "Profile verification check",
    "trigger_on": "profiles#verification-state-change",
    "delivery": {
      "version": "4.0.0",
      "url": "https://your.webhook.url/12345"
    }
  }'
```

Listen for the webhook payload:

```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "profiles#verification-state-change",
  "sent_at": "2026-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "type": "profile",
      "id": 111
    },
    "current_state": "verified",
    "occurred_at": "2026-01-01T12:34:56.789Z"
  }
}
```

#### Check profile verification status

This request returns the verification status of a profile when funding with a bank transfer. It specifies the verification status for each route queried in the response (via the `source_currencies` query parameter).

*Verification status* is an indicator of the current level of verification that has been made for a profile to some particular level of confidence: a level that is likely to allow money transfers to occur without being delayed by verification-related issues.

Sample request
```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/verification-status/bank-transfer?source_currencies=GBP%2CUSD%2CEUR' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Sample response
The `routes` array of objects lists the verification check results for each queried source currency.

```json 200 application/json
{
  "routes": [
    {
      "source_currency": "GBP",
      "maximum_entitled_amount": 100000,
      "current_status": "verified"
    },
    {
      "source_currency": "USD",
      "maximum_entitled_amount": 0,
      "current_status": "not_verified"
    },
    {
      "source_currency": "EUR",
      "maximum_entitled_amount": 10000,
      "current_status": "not_verified"
    }
  ],
  "request_id": "e66da5f6-2456-403c-bfcb-908885ee1a61"
}
```

```json 429 application/json
{}
```

Note that the `maximum_entitled_amount` is the maximum amount that can be transferred with the user's given verification state.

**Understanding the response**:

The `current_status` field:

- `verified`: The profile is sufficiently verified to start making payments.
- `not_verified`: The profile is currently awaiting verification or there are pending issues with the verification process.


| `current_status`  | `maximum_entitled_amount`  | How to process |
|  --- | --- | --- |
| `verified` | any value | Profile is verified. `maximum_entitled_amount` field can be ignored (though some regional limits may still apply). |
| `not_verified` | value = 0 | Profile is not verified. Any payments from the user will be delayed by verification. |
| `not_verified` | value is > 0 | Profile is not verified yet but is allowed to make payments up to a certain limit. Once the limit is reached, following payments might be delayed due to additional verification requirements. Limit is cumulative and not per transfer.

This state allows some profiles to experience the product immediately even if the verification process isn't complete yet. |


Although we expose verification status as a profile-level property, there are implicit limits to which any `VERIFIED` status applies.

Some individual transfers may require additional verification, even after we have given the profile a `VERIFIED` status. Therefore, you should be prepared for verification issues to affect money transfers regardless of the profile's status, although this is relatively uncommon.