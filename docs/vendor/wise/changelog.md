# Changelog

Track changes and upgrades to the Wise Platform API.

## October 2026

- Fixed the documentation for the ultimate beneficial owner [create](/api-reference/profile/profileubocreate), [update](/api-reference/profile/profileuboupdate), and [list](/api-reference/profile/profileubolist) endpoints:
  - Documented supported optional address, identity, nationality, email, and place-of-birth fields in create and update requests.
  - Documented returned `city` and `state` fields in responses for all three endpoints.
  - Corrected the documented success status for the create endpoint from `200 OK` to `201 Created`.
- Fixed the documentation for business profile [create](/api-reference/profile/profilebusinesscreatev3) and [update](/api-reference/profile/profilebusinessupdate) requests: documented supported optional business `contactDetails` object.


2026Q4 Version released. This consolidated entry covers the new, updated and removed endpoints for the version.

- Added a SAML endpoint (`POST /{gv}/login/saml2/sso`) to receive single sign-on responses from an identity provider.
- Added an endpoint (`GET /{gv}/saml2/metadata`) to retrieve Wise’s SAML service-provider metadata for configuring single sign-on with an identity provider.
- Replaced [Retrieve Bank Account Details](/api-reference/2026q3/bank-account-details/bankaccountdetailsget) with [Get account details by ID](/api-reference/bank-account-details/getaccountdetails) under Balances. The new endpoint supports GB, US and BE account details; requests for unsupported countries return `404 Not Found`. For other countries, continue to use the 2026Q3 endpoint.
- Added [file upload](/api-reference/case-files/casefileupload) under Cases to submit files as supporting documentation for cases.
- Removed [Create payment return](/api-reference/2026q3/bank-account-details/bankaccountdetailsreturnscreate) (`POST /profiles/{profileId}/account-details/payments/{paymentId}/returns`) from the 2026Q4 API.
- Updated [GPI tracking](/api-reference/gpi-tracking/lookupgpitracking) availability in the 2026Q4 API. Partners can retrieve SWIFT tracking information for transfers they own using a transfer ID or UETR.
- Added [transfer delivery update simulation](/api-reference/simulation/simulationtransferdeliveryupdate) to trigger a `transfers#delivery-update` webhook in sandbox without changing the transfer state.
- Added [Create a settlement allocation request](/api-reference/settlement/createfundsallocationrequest) to submit a Settlement Allocation Request (SAR) file containing instructions for allocating settled funds across payment intents.
- Added [Get a settlement allocation](/api-reference/settlement/getsettlementallocation) to retrieve a settlement allocation by ID, with the option to include a paginated list of its payment intents.
- Added [settlement funds simulation](/api-reference/simulation/simulatesettlementallocationsfunds) to simulate receipt of funds for a settlement allocation, allowing integrations to test settlement funding flows.


## September 2026

- [Payment Instrument API](/api-reference/payment-instruments) endpoints added to API reference.


- Business profile classification moves to `industryCategories` as a **field change only**. The existing [create](/api-reference/profile/profilebusinesscreatev3) and [update](/api-reference/profile/profilebusinessupdate) business profile endpoints accept it, so no endpoint migration is required. Earlier guidance describing separate endpoints for this change no longer applies.
- Documentation has been updated to reflect this, including the [business categories list](/guides/product/kyc/business-categories) and [Migrating to industry categories](/guides/product/kyc/migrate-business-profile-industry-categories).


- Updated Partner Support Domain name to Cases to better describe the endpoints within it.


## August 2026

- KYC Review API now supports [submitting](/api-reference/kyc-review/kycreviewrequirementsubmit) the [LEGAL_ENTITY_SHAREHOLDER](/guides/product/kyc/wise-kyc/kyc-requirement-types#legal_entity_shareholder) type.


- Added a [guide for fees and pricing](/guides/product/issue-cards/fees-and-pricing) for the issue card product.


- Add support for custom reference, sender and beneficiary details in [bank transaction import simulation](/api-reference/simulation/simulationbanktransactionimport).


- Added support for detailed sender bank information including LEI, Clearing System Member ID, Clearing System Code and structured address in [swift-in simulation](/api-reference/simulation/simulationswiftin).
- Added schema version `4.3.0` with LEI, Clearing System Member ID and Clearing System Code support to [`swift-in#credit` webhook](/api-reference/webhook-event/eventswiftincredit).
- Deprecated schema version `3.0.0` for [`swift-in#credit` webhook](/api-reference/webhook-event/eventswiftincredit). This version uses flattened unstructured addresses. Migrate to `4.3.0` for enhanced address and bank details information.


- Updated [v5.0.0 webhook usage](/guides/product/send-money/tracking/payout-failures#notes-about-payout-failures) in the payout failure guide.
- Updated [OAuth 2.0](/guides/developer/auth-and-security/oauth-2-setup) and [token guides](/guides/developer/auth-and-security/user-access-token) to indicate partners on the embedded integration model use client credentials tokens for all authenticated requests. This integration model no longer relies on user objects and so user access tokens no longer apply.


- KYC Review API now supports [submitting](/api-reference/legacy/kyc-review/kycreviewrequirementsubmit) the following requirement types:
  - [BUSINESS_CONTROLLING_PERSON](/guides/product/kyc/wise-kyc/kyc-requirement-types#business_controlling_person)
  - [BUSINESS_SHAREHOLDER_CONTACT_DETAILS](/guides/product/kyc/wise-kyc/kyc-requirement-types#business_shareholder_contact_details)
  - [BUSINESS_INCOME_CLASSIFICATION](/guides/product/kyc/wise-kyc/kyc-requirement-types#business_income_classification)


- Add newly exposed payout failure reasons `TECHNICAL_ISSUE`, `TECHNICAL_ISSUE_RETRYABLE` to [payout failure guide](/guides/product/send-money/tracking/payout-failures).
- Upgrade `failure_reason_code` from a free-text string to a committed enum in v5.0.0 of [transfers#payout-failure webhook](/api-reference/legacy/webhook-event/eventtransferspayoutfailure), ensuring stable, machine-readable values partners can rely on.


**New: Automated RFI case handling for Partners**
Partners can now receive, respond to, and track Requests for Information (RFIs) programmatically through the Cases API. This enables faster resolution of compliance and operations
queries through automated workflows.

- New [Case handling guide](/guides/product/partner/case-handling) - Receive RFIs, submit structured responses, track case status, and automate case handling in your backend systems.
- New [Respond to RFIs guide](/guides/product/partner/respond-to-rfis) - Step-by-step implementation for handling automated and freeform RFIs.


**Cases API (new)**

- [Create a case](/api-reference/case/casecreate) - Open support or operations cases with Wise.
- [Retrieve a case](/api-reference/case/caseget) - Get full case details including all messages and reference information.
- [Submit a message](/api-reference/case/casesubmitmessage) - Respond to RFIs with structured submission types or freeform messages.


***Deprecated: Legacy Cases API v1***
The following v1 Case endpoints are now deprecated. Migrate to the new Cases API for structured RFI handling, typed messages, and improved case management:

- Deprecated [GET /v1/cases/{caseId}](/api-reference/legacy/case/caseget) - Use [GET /cases/{caseId}](/api-reference/case/caseget) instead. New endpoint returns typed messages with structured content, reference information, and aligned status values.
- Deprecated [GET /v1/cases/{caseId}/comments](/api-reference/legacy/case/casecommentsget) - Use [GET /cases/{caseId}](/api-reference/case/caseget) instead. Messages are now included in the case response with full content structure.
- Deprecated [PUT /v1/cases/{caseId}/comments](/api-reference/legacy/case/casecommentcreate) - Use [POST /cases/{caseId}/messages](/api-reference/case/casesubmitmessage) instead. New endpoint supports structured submission types for RFI responses and freeform messages.


**partner-support#case-changed webhook**

- Add schema version `5.0.0` for [partner-support#case-changed](/api-reference/case/eventpartnersupportcasechanged) webhook with restructured payload.
- Deprecated schema versions `4.0.0` and `2.0.0` for [partner-support#case-changed](/api-reference/case/eventpartnersupportcasechanged) webhook. These versions use legacy payload
structure. Migrate to `5.0.0` for structured message content and full message history in each webhook
payload.


## July 2026

- 2026Q3 Version released, the first global, datebased API version is now available, enabling better compatibility, documentation and easier change management. This is currently opt-in. Previous endpoint-based versions remain available. See [Global API versioning](/guides/developer/global-versioning) for more.
- Business profile creation (global versions): Global versions do not support `POST /v2/profiles/business-profile`. Use `POST /v3/profiles/business-profile` instead (creates the business profile and authorised representative in one request via `businessRepresentative`). The v2 endpoint remains available in the previous endpoint-based API; authentication and scopes are unchanged.
- Deprecated endpoints in global versions: Some endpoints already deprecated in the non-versioned API are not included in global versions. If you use them, move to the documented replacements before adopting a global version. See [Global API versioning](/guides/developer/global-versioning).


- Add new [Partner pooled funding guide](/guides/product/issue-cards/partner-pooled-funding) for cards.
- Add `data.resource.incoming_transfer_type` enum to [swift-in#credit webhook](/api-reference/legacy/webhook-event/eventswiftincredit) `4.2.0` schema version.


- Added conditional attributes field to the [KYC requirement object](/api-reference/legacy/kyc-review/kyc-requirement). Certain requirement types now return additional contextual metadata.
- Attribute changes on KYC requirements now trigger a [kyc-reviews#state-change](/api-reference/legacy/webhook-event/eventkycreviewsstatechange) webhook notification.


- Deprecated `first_line` in favour of `address_lines` in [swift-in#credit webhook](/api-reference/legacy/webhook-event/eventswiftincredit) address properties.


- Updated [Client credentials token format migration](/guides/developer/auth-and-security/client-credentials-token-migration) with sandbox timeline.


## June 2026

- Card Orders: The `address` field is now optional when ordering virtual cards, but required for physical cards. See the [Card address validation guide](/guides/developer/api-guides/card-address-validation) for details.


- Updated [Subscribe to webhooks guide](/guides/developer/webhooks/subscribe-to-webhooks) to include both subscription methods: subscribe via Developer Hub and subscribe via API.


- Revised the [Send money refund guides](/guides/product/send-money/refunds) to provide more details about refund methods, how they work, what methods apply to which funding models, and partial refunds. Also added example webhook payloads.
  - [Refund to sender bank account](/guides/product/send-money/refunds/refund-to-bank-account)
  - [Refund to balance](/guides/product/send-money/refunds/refund-to-balance)
  - [Refund via net settlement](/guides/product/send-money/refunds/net-settlement)


- New guide for [Client credentials token format migration](/guides/developer/auth-and-security/client-credentials-token-migration).


## May 2026

- New guide for [Subscribing to webhooks](/guides/developer/webhooks/subscribe-to-webhooks)
- New guide for [Viewing and Retrying webhooks](/guides/developer/webhooks/view-retry-events)
- New guides for [Recipient verification](/guides/product/send-money/recipient-verification) and currency-specific guides for currencies that support additional recipient account verification checks:
  - [CNY recipient verification](/guides/product/send-money/recipient-verification/cny-verification)
  - [IDR recipient verification](/guides/product/send-money/recipient-verification/idr-verification)
  - [INR recipient verification](/guides/product/send-money/recipient-verification/inr-verification)
  - [KRW recipient verification](/guides/product/send-money/recipient-verification/krw-verification)


- Improve consistency regarding KYC review fields across the documentation.
- Document correct return response from the KYC review endpoints
- Improve wording in the [Update KYC review endpoint](/api-reference/legacy/kyc-review/kycreviewredirecturlupdate)


- Add `instructedAmount` and `instructedCurrencyCode` fields to [swift-in simulation endpoint](/guides/product/receive-money/test-and-go-live)


- Added a new value `VERIFIED` to the [KYC requirement state](/api-reference/legacy/kyc-review/kyc-requirement). This value will be returned in the webhook and API response if the requirement was submitted and verified on our side.
- Added new [transfer payout failure simulation](/api-reference/legacy/simulation/simulationtransferpayoutfailure) endpoint. Triggers [transfers#payout-failure webhook](/api-reference/legacy/webhook-event/eventtransferspayoutfailure) in Sandbox.


- Added sandbox support for [transfer refund webhooks](/api-reference/legacy/simulation/simulationtransferstatechange#sandbox-refund). Simulating `funds_refunded` now triggers a `transfers#refund` webhook with a simulated refund amount.


- Add `bank_details` fields within `recipient` and `sender` to [swift-in#credit webhook](/api-reference/legacy/webhook-event/eventswiftincredit)


- Update copy in [Get Wise JOSE public key](/api-reference/legacy/jose/joseresponsepublickeysget) to accomodate both JWS + JWE.


- Add `data.requested_by_customer` field to [profiles#state-change webhook](/api-reference/legacy/webhook-event/eventprofilesstatechange)


## April 2026

- New guide for [JOSE JWS Key Rotation](/guides/developer/auth-and-security/jose/jose-jws-key-rotation).


* New guide for [API and hybrid customer onboarding](/guides/product/kyc/wise-kyc/api-hybrid-kyc) for embedded partners.
* Significant updates to the [introduction to Wise-performed KYC](/guides/product/kyc/wise-kyc) and [Hosted customer onboarding](/guides/product/kyc/wise-kyc/hosted-kyc) guides. Provides more in-depth details about available customer onboarding methods and instructions for using the Wise-hosted method.


* Add structured addresses and `previous_instructing_agents` in [swift-in#credit](/api-reference/legacy/webhook-event/eventswiftincredit) webhook v4.0.0.


* Add `keyId` field to [Get Wise public signing key](/api-reference/legacy/jose/joseresponsepublickeysget) endpoint.
* Documented global `X-External-Correlation-Id` header on all API operations. See [correlation ID guide](/guides/developer/headers/correlation-id).
* Documented global `x-trace-id` header on all API operations.
* Documented `429 Too Many Requests` response with `Retry-After` and `X-Rate-Limited-By` headers on all API operations.


## March 2026

* Consolidated Client Credentials Token and User Tokens into a single [OAuth Token](/api-reference/legacy/oauth-token) endpoint


* Updated [Auth and Security guide](/guides/developer/auth-and-security)
* New [OAuth 2.0 setup guide](/guides/developer/auth-and-security/oauth-2-setup)
* New [Client credentials tokens guide](/guides/developer/auth-and-security/client-credentials-token)
* New [User access tokens guide](/guides/developer/auth-and-security/user-access-token)
* New [Refresh tokens guide](/guides/developer/auth-and-security/refresh-tokens)


* Rename `Push Provisioning` api reference section to `Digital Wallet`
* Update [digital wallet guide](/guides/product/issue-cards/card-digital-wallet)
* Add [payment token activation endpoint](/api-reference/legacy/digital-wallet/digitalwalletactivatepaymenttoken) to activate a card payment token for manual provisioning
* Add [cards#manual-provisioning-verification](/api-reference/legacy/webhook-event/eventcardsmanualprovisioningverification) webhook


* Add new [Event Ordering](/guides/developer/webhooks/event-ordering) guide. Webhook events may not be delivered in the order they occurred — this guide explains how to use ordering fields to reconcile the correct sequence.
* Add schema version `4.0.0` for all [webhook event types](/api-reference/legacy/webhook-event). This version provides consistent millisecond-precision timestamps across all events, making it easier to determine event order. We recommend updating your [subscriptions](/api-reference/legacy/webhook) to use `4.0.0` to order events reliably.


* Add [guide](/guides/developer/headers/correlation-id) for `X-External-Correlation-Id` header usage
* Update error codes for [verify PIN](/api-reference/legacy/sca-pin/scapinverify) and [verify device fingerprint](/api-reference/legacy/sca-device-fingerprints/scadevicefingerprintverify) endpoints


* Add [relayed authorisation guide](/guides/product/issue-cards/relayed-authorisation) to card issuance
* Update [card transaction api](/api-reference/legacy/card-transaction) to include relayed authorisation data
* Update [card transaction webhook](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) to include relayed authorisation data


* Add fees and previous instructing agent in [swift-in simulation endpoint](/guides/product/receive-money/test-and-go-live)


## February 2026

* Add details for submitting Tax Residency Kyc Requirement [KYC Requirement Submit](/api-reference/legacy/kyc-review/kycreviewrequirementsubmit)


* Adds support for providing the following on originators of third-party transfers
  * `nationality`: for `PRIVATE` originators
  * `businessRegistrationDate`: for `BUSINESS` originators


## January 2026

* Multiple ID fields are now explicitly documented as `int64` (64-bit integer). Please ensure your integration stores these IDs using the appropriate 64-bit type (e.g., Long in Java, BIGINT in SQL).
Key fields to note:
  - transfer ID - approaching the `int32` upper bound
  - recipient ID - approaching the `int32` upper bound
  - card transaction ID - past the `int32` upper bound
  - user ID
  - profile ID
  - balance ID


- See [detailed data type changelog](/changelog/int64-changes) for all updated fields and endpoints.