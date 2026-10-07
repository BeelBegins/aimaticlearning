# Wise Platform API

The Wise Platform API is a REST-based interface that enables programmatic access to Wise's payment infrastructure. All endpoints return JSON-formatted responses and use standard HTTP methods and status codes.
{% admonition type="success" name="New to wise?" %}
  We strongly recommend first reading our **[Getting Started Guide](/guides/developer/index.md)** to help you set up credentials and make your first call.
{% /admonition %}

Before you begin {% .title-2 .m-t-5 %}

To use this API reference effectively, you should have:

- Received Valid [API credentials from Wise](/guides/developer/auth-and-security/index.md) (Client ID and Client Secret)
- Understand OAuth 2.0 authentication
- Be familiar with RESTful API concepts

We recommend connecting to our Docs MCP Server.
{% connect-mcp /%}

Core API resources {% .title-2 .m-t-5 .m-b-0 %}

| Resource | Purpose |
|----------|---------|
| **[Quote](/api-reference/quote)** | Exchange rate and fee calculations |
| **[Recipient](/api-reference/recipient)** | Beneficiary account management |
| **[Transfer](/api-reference/transfer)** | Payment creation and execution |
| **[Balance](/api-reference/balance)** | Multi-currency account operations |
| **[Profile](/api-reference/profile)** | Account ownership details |
| **[Rate](/api-reference/rate)** | Current and historical exchange rates |

**Not sure which workflow to build?**<br>
Start with our [Integration Guides](/guides/product/send-money/use-cases/index.md) for step-by-step implementation examples.{% .m-t-3 .m-b-5 %}


Version: 2026Q4

## Servers

Production Environment
```
https://api.wise.com/2026Q4
```

Sandbox Environment
```
https://api.wise-sandbox.com/2026Q4
```

## Security

### UserToken

[object Object],[object Object],[object Object],[object Object]

Type: http
Scheme: bearer
Bearer Format: JWT

### PersonalToken

[object Object]

Type: http
Scheme: bearer
Bearer Format: JWT

### ClientCredentialsToken

[object Object],[object Object],[object Object],[object Object]

Type: http
Scheme: bearer
Bearer Format: JWT

### BasicAuth

[object Object],[object Object]

Type: http
Scheme: basic

## Download OpenAPI description

 - [Wise Platform API](https://docs.wise.com/_bundle/api-reference/@latest/index.yaml)

## OAuth Token

 - [POST /oauth/token](https://docs.wise.com/api-reference/oauth-token/oauthtokencreate.md): Exchange credentials or authorisation grants for an OAuth 2.0 access token. The `grant_type` field determines which parameters are required and which response fields are returned. See [managing token
## JOSE

 - [GET /auth/jose/response/public-keys](https://docs.wise.com/api-reference/jose/joseresponsepublickeysget.md): Returns a public key issued by Wise. Depending on the scope requested, the key will be used for verifying HTTP responses signed by Wise or for for encrypting the payload prior to sending it to Wise. F
 - [POST /auth/jose/request/public-keys](https://docs.wise.com/api-reference/jose/joserequestpublickeyscreate.md): Upload a client public key for request payload signing or response payload encryption. This endpoint requires a client credentials token, not a user level access token. Make sure you use your client d
 - [POST /auth/jose/playground/jws](https://docs.wise.com/api-reference/jose/joseplaygroundjws.md): Send test signed HTTP requests and receive signed responses. Signing is mandatory for this endpoint — any message that is not a JSON Web Signature (JWS) will be rejected.
 - [GET /auth/jose/playground/jwe](https://docs.wise.com/api-reference/jose/joseplaygroundjweget.md): Send test HTTP GET requests and receive encrypted responses.
 - [POST /auth/jose/playground/jwe](https://docs.wise.com/api-reference/jose/joseplaygroundjwepost.md): Send test encrypted HTTP requests and receive encrypted responses. Encryption is mandatory for this endpoint — any message that is not in JSON Web Encryption (JWE) format will be rejected.
 - [POST /auth/jose/playground/jwe-direct-encryption](https://docs.wise.com/api-reference/jose/joseplaygroundjwedirectencryption.md): Send encrypted HTTP requests for testing purposes and receive responses encrypted with the original content encryption key. Encryption is mandatory for this endpoint — any message that is not in JSON
 - [GET /auth/jose/playground/jwsjwe](https://docs.wise.com/api-reference/jose/joseplaygroundjwsjweget.md): Send test signed and encrypted HTTP requests and receive signed and encrypted responses. Both signing and encryption are mandatory for this endpoint. The request must be a JSON Web Signature (JWS) wra
 - [POST /auth/jose/playground/jwsjwe](https://docs.wise.com/api-reference/jose/joseplaygroundjwsjwepost.md): Send test signed and encrypted HTTP requests and receive signed and encrypted responses. Both signing and encryption are mandatory for this endpoint. The request must be a JSON Web Signature (JWS) wra
## Users

 - [User](https://docs.wise.com/api-reference/user/user.md): Schema: #/components/schemas/user
 - [GET /me](https://docs.wise.com/api-reference/user/usergetbytoken.md): Get authenticated user details for the user's token submitted in the Authorization header.
 - [GET /users/{userId}](https://docs.wise.com/api-reference/user/usergetbyid.md): Get authenticated user details by user ID.
 - [POST /user/signup/registration_code](https://docs.wise.com/api-reference/user/usercreate.md): Wise uses email address as unique identifier for users. If email is new (there is no active user already) then a new user will be created. When you are submitting an email which already exists amongs
 - [POST /users/exists](https://docs.wise.com/api-reference/user/usercheckexists.md): Check if a user already exists by email. Wise uses email address as unique identifier for users. If email has already been used by a user, it cannot be reused to create a new user. Note that this uses
 - [PUT /users/{userId}/contact-email](https://docs.wise.com/api-reference/user/usercontactemailset.md): Sets a contact email address. The contact email address is used to send notifications to users who have been registered with a dummy email address.
 - [GET /users/{userId}/contact-email](https://docs.wise.com/api-reference/user/usercontactemailget.md): Retrieves a contact email address.
 - [POST users#state-change](https://docs.wise.com/api-reference/user/eventusersstatechange.md): Triggered every time a user's state is updated. This webhook is deprecated and will be removed by end 2026. If you are currently subscribed to it, please migrate to the new [profiles#state-change](/ap
## Claim Account

 - [POST /user/claim-account](https://docs.wise.com/api-reference/claim-account/claimaccountcreate.md): Generate a short-lived `claim_account_code` that allows a customer to take ownership of an account. Use the code when [redirecting the customer to Wise](/guides/product/kyc/wise-kyc/redirect-to-wise/c
## Profiles

 - [Profile](https://docs.wise.com/api-reference/profile/profile.md): Schema: #/components/schemas/profile
 - [GET /profiles](https://docs.wise.com/api-reference/profile/profilelist.md): List of all profiles belonging to user.
 - [POST /profiles/personal-profile](https://docs.wise.com/api-reference/profile/profilepersonalcreate.md): Create a personal profile for the authenticated user. A personal profile represents an individual and is required before creating transfers or business profiles. Use the `X-idempotence-uuid` header to
 - [POST /profiles/business-profile](https://docs.wise.com/api-reference/profile/profilebusinesscreatev3.md): Creates the business profile and its authorized representative in a single request. This request accepts an optional field in the header, `X-idempotence-uuid`. This should be unique for each Profile y
 - [GET /profiles/{profileId}](https://docs.wise.com/api-reference/profile/profileget.md): Get profile info by ID.
 - [PUT /profiles/{profileId}/personal-profile](https://docs.wise.com/api-reference/profile/profilepersonalupdate.md): Update user profile information for a personal profile. If user profile has been verified then there are restrictions on what information is allowed to change. Where permitted, use the update window f
 - [PUT /profiles/{profileId}/business-profile](https://docs.wise.com/api-reference/profile/profilebusinessupdate.md): Update user profile information for a business profile. If user profile has been verified then there are restrictions on what information is allowed to change. Where permitted, use the update window f
 - [GET /profiles/{profileId}/business-profile/business-representative](https://docs.wise.com/api-reference/profile/profilebusinessrepresentativeget.md): Get Business Representative info by Business Profile ID.
 - [PUT /profiles/{profileId}/business-profile/business-representative](https://docs.wise.com/api-reference/profile/profilebusinessrepresentativeupdate.md): Update or transfer the Business Representative for the specified Business Profile. Set `updateContext` to `UPDATE_DETAILS` to update the existing Business Representative's details, or `TRANSFER_OF_AUT
 - [POST /profiles/{profileId}/verification-documents](https://docs.wise.com/api-reference/profile/profileverificationdocumentcreate.md): Add an identification document to a personal profile. Not applicable to business profiles. For SSN submissions, only `type` and `uniqueIdentifier` (9 digits, no letters or symbols) are required.
 - [PUT /profiles/{profileId}/verification-documents](https://docs.wise.com/api-reference/profile/profileverificationdocumentupdate.md): Update an existing identification document on a personal profile. Not applicable to business profiles. This endpoint performs a full replacement of the document details. Any fields not provided in th
 - [POST /profiles/{profileId}/directors](https://docs.wise.com/api-reference/profile/profiledirectorcreate.md): Adds new directors to the business profile. Returns the list of all directors associated with the business profile.
 - [GET /profiles/{profileId}/directors](https://docs.wise.com/api-reference/profile/profiledirectorlist.md): Returns the list of director objects associated with the business profile.
 - [PUT /profiles/{profileId}/directors](https://docs.wise.com/api-reference/profile/profiledirectorupdate.md): Overrides directors in the business profile. Returns the list of all directors associated with the business profile.
 - [POST /profiles/{profileId}/ubos](https://docs.wise.com/api-reference/profile/profileubocreate.md): Adds new ultimate beneficial owners to the business profile. Returns the list of all ultimate beneficial owners associated with the business profile. All the shareholders that have at least 25% owners
 - [GET /profiles/{profileId}/ubos](https://docs.wise.com/api-reference/profile/profileubolist.md): Returns the list of all ultimate beneficial owners associated with the business profile.
 - [PUT /profiles/{profileId}/ubos](https://docs.wise.com/api-reference/profile/profileuboupdate.md): Replaces the entire collection of ultimate beneficial owners in the business profile. Returns the list of all ultimate beneficial owners associated with the business profile.
 - [POST /profiles/{profileId}/update-window](https://docs.wise.com/api-reference/profile/profileupdatewindowopen.md): Opens the update window for updating the profile information: details, addresses, directors, owners, others.
 - [DELETE /profiles/{profileId}/update-window](https://docs.wise.com/api-reference/profile/profileupdatewindowclose.md): Deletes the update window for updating the profile.
 - [POST /profiles/{profileId}/verification-status/bank-transfer](https://docs.wise.com/api-reference/profile/profileverificationstatuscheck.md): You can check the verification status of a profile using this API. This is a profile-specific API resource which should be accessed using an access token acquired for the profile. We do not expose an
 - [POST profiles#overdraft-limit-threshold](https://docs.wise.com/api-reference/profile/eventprofilesoverdraftlimitthreshold.md): Triggered when the overdraft limit usage has reached 70% threshold. The event at each threshold is triggered maximum once per hour. * Event type: `profiles#overdraft-limit-threshold` * Profile level s
 - [POST profiles#state-change](https://docs.wise.com/api-reference/profile/eventprofilesstatechange.md): Triggered every time a profile's state is updated. * Event type: `profiles#state-change` * Profile level subscriptions: Not Supported * Application level subscriptions: Supported Events may not be de
 - [POST profiles#verification-state-change](https://docs.wise.com/api-reference/profile/eventprofilesverificationstatechange.md): Triggered when the verification state of a connected profile changes. A profile's *verification state* can be `verified` or `not_verified`. - If the state is `verified`, then the user is ready to make
## Activity

 - [GET /profiles/{profileId}/activities](https://docs.wise.com/api-reference/activity/activitylist.md): List of activities belonging to user profile. Activities represent snapshots of performed actions and can be filtered by various parameters to narrow down the results.
## Addresses

 - [Address](https://docs.wise.com/api-reference/address/address.md): Schema: #/components/schemas/Address
 - [POST /addresses](https://docs.wise.com/api-reference/address/addresscreate.md): Adds address info to user profile. List of required fields are different for different countries. Use the [address requirements endpoint](#operation/addressRequirementsGet) to dynamically discover req
 - [GET /addresses](https://docs.wise.com/api-reference/address/addresslist.md): List of addresses belonging to user profile.
 - [GET /addresses/{addressId}](https://docs.wise.com/api-reference/address/addressget.md): Get address info by ID.
 - [GET /address-requirements](https://docs.wise.com/api-reference/address/addressrequirementsget.md): Returns the list of fields required to create a valid address. Use this as a starting point to discover required fields. The response contains 4 required top-level fields: - `country` (select field wi
 - [POST /address-requirements](https://docs.wise.com/api-reference/address/addressrequirementspost.md): Returns the list of fields required to create a valid address, based on the provided context. Use this endpoint to dynamically discover additional required fields based on selected values. For example
## KYC Review

 - [KYC Requirement](https://docs.wise.com/api-reference/kyc-review/kyc-requirement.md): Schema: #/components/schemas/kyc-requirement
 - [KYC Review](https://docs.wise.com/api-reference/kyc-review/kyc-review.md): Schema: #/components/schemas/kyc-review
 - [KYC Review with a Hosted KYC link](https://docs.wise.com/api-reference/kyc-review/kyc-review-with-link.md): Schema: #/components/schemas/kyc-review-with-link
 - [POST /profiles/{profileId}/kyc-reviews](https://docs.wise.com/api-reference/kyc-review/kycreviewcreate.md): Creates a KYC Review for a specific customer action.
 - [GET /profiles/{profileId}/kyc-reviews](https://docs.wise.com/api-reference/kyc-review/kycreviewlist.md): Retrieves a list of all active KYC Reviews for a given profile.
 - [GET /profiles/{profileId}/kyc-reviews/{kycReviewId}](https://docs.wise.com/api-reference/kyc-review/kycreviewget.md): Retrieves a single KYC Review by ID for a profile.
 - [PATCH /profiles/{profileId}/kyc-reviews/{kycReviewId}](https://docs.wise.com/api-reference/kyc-review/kycreviewredirecturlupdate.md): Updates the KYC Review with a redirect URL. Returns the KYC Review object with a `link` field containing a URL where the end customer needs to be directed in order to complete the Hosted KYC flow. **T
 - [POST /profiles/{profileId}/kyc-requirements/{requirementKey}](https://docs.wise.com/api-reference/kyc-review/kycreviewrequirementsubmit.md): Submit a KYC requirement for a KYC Review. - A KYC requirement can only be submitted if the KYC Review status is `WAITING_CUSTOMER_INPUT` or `PASSED_WITH_REQUIREMENTS`. - A KYC requirement should only
 - [POST kyc-reviews#state-change](https://docs.wise.com/api-reference/kyc-review/eventkycreviewsstatechange.md): Triggered when a KYC review state has changed. In previous versions, this event fired only when the overall KYC review state changed. In **v5.0.0**, it fires on every requirement or additional require
## Additional Verification

 - [POST /profiles/{profileId}/additional-verification/upload-evidences](https://docs.wise.com/api-reference/verification/verificationuploadevidences.md): Uploads verification evidence for a specific profile. The request body varies significantly between **Personal** and **Business** profiles. Submitting an evidence that was already uploaded will result
 - [POST /profiles/{profileId}/verification-status/upload-document](https://docs.wise.com/api-reference/verification/verificationuploaddocument.md): Uploads verification documents for review. You can upload multiple files at once. A valid document must fulfil these requirements: - The document must be clear. - The document needs to be a .jpg, .p
 - [GET /profiles/{profileId}/verification-status/required-evidences](https://docs.wise.com/api-reference/verification/verificationgetrequiredevidences.md): Fetches the required evidences for a profile to complete additional customer verification. If one or more evidences are returned, the customer should submit those evidences using the upload-evidences
 - [POST profiles#cdd-check-state-change](https://docs.wise.com/api-reference/verification/eventprofilescddcheckstatechange.md): This event pushes updates for the [Additional Customer Verification](/guides/product/kyc/partner-kyc/additional-verification) process. * Event type: `profiles#cdd-check-state-change` * Profile level s
## FaceTec

 - [GET /facetec/public-key](https://docs.wise.com/api-reference/facetec/facetecpublickeyget.md): Retrieve Wise's FaceTec public key to be used when [exporting 3D FaceMap](https://dev.facetec.com/api-guide#export-3d-facemap) from your FaceTec host to Wise.
## Link Requests

 - [POST /profiles/{profileId}/embedded-flows/link-requests/recipients](https://docs.wise.com/api-reference/link-requests/recipientembeddedlinkrequestcreate.md): Returns a link that allows a user to complete a recipient creation flow via either a redirect or embedded iframe/webview. View [Embedded Flows - Recipient Creation](/guides/product/embedded-flows/flow
 - [POST /profiles/{profileId}/embedded-flows/link-requests/payment-instrument](https://docs.wise.com/api-reference/link-requests/paymentinstrumentembeddedlinkrequestcreate.md): Returns a link that allows a user to complete a payment instrument flow via either a redirect or embedded iframe/webview. View [Embedded Flows - Payment Instruments](/guides/product/embedded-flows/flo
 - [POST /profiles/{profileId}/embedded-flows/link-requests/kyc-reviews](https://docs.wise.com/api-reference/link-requests/kycreviewsembeddedlinkrequestcreate.md): Returns a link that allows a user to complete a KYC review flow via either a redirect or embedded iframe/webview. View [Embedded Flows - KYC Review](/guides/product/embedded-flows/flows/kyc-reviews) t
 - [GET /embedded-flows/link-requests/{embeddedLinkRequestId}](https://docs.wise.com/api-reference/link-requests/embeddedlinkrequestget.md): Retrieves an Embedded Flow configuration by embedded link request ID. Typically this is not needed to be called as its used by the flow itself. Embedded Flows uses this endpoint to load the configurat
## One Time Token

 - [One-Time Token](https://docs.wise.com/api-reference/sca-ott/one-time-token.md): Schema: #/components/schemas/one-time-token
 - [GET /one-time-token/status](https://docs.wise.com/api-reference/sca-ott/ottstatusget.md): Retrieve necessary information to clear a OTT.
## SCA Sessions

 - [POST /profiles/{profileId}/sca-sessions/authorise](https://docs.wise.com/api-reference/sca-sessions/scasessioncreate.md): Manually triggers SCA, returning a one-time token along with a list of associated challenges. These challenges can be cleared with the verify endpoints.
## PIN

 - [POST /profiles/{profileId}/pin](https://docs.wise.com/api-reference/sca-pin/scapincreate.md): Creates a new PIN factor used to resolve a SCA knowledge challenge type. The request and response are encrypted using the JOSE framework. Please refer to the [SCA over API guide](/guides/developer/aut
 - [DELETE /profiles/{profileId}/pin](https://docs.wise.com/api-reference/sca-pin/scapindelete.md): Deletes a PIN associated to a profile. To update a PIN for a profile, use this endpoint followed by [Create a PIN](/api-reference/sca-pin/scapincreate). This operation is irreversible.
 - [POST /profiles/{profileId}/pin/verify](https://docs.wise.com/api-reference/sca-pin/scapinverify.md): Verifies a PIN challenge when calling a SCA-secured endpoint. Make sure to [create a PIN](/api-reference/sca-pin/scapincreate) before using this endpoint. The request and response are encrypted using
## Facemaps

 - [POST /profiles/{profileId}/facemaps](https://docs.wise.com/api-reference/sca-facemaps/scafacemapcreate.md): Creates a new facemap factor used to resolve a SCA inherence challenge type. A facemap should be exported from your FaceTec server using the SDK's [export API](https://dev.facetec.com/api-guide#export
 - [DELETE /profiles/{profileId}/facemaps](https://docs.wise.com/api-reference/sca-facemaps/scafacemapdelete.md): Deletes a facemap associated to a profile. To update a facemap for a profile, use this endpoint followed by [Create a facemap](/api-reference/sca-facemaps/scafacemapcreate). This operation is irrevers
 - [POST /profiles/{profileId}/facemaps/verify](https://docs.wise.com/api-reference/sca-facemaps/scafacemapverify.md): Verifies a facemap challenge when calling a SCA-secured endpoint. Make sure to [create a facemap](/api-reference/sca-facemaps/scafacemapcreate) before using this endpoint. A facemap should be exported
## Device Fingerprints

 - [POST /profiles/{profileId}/device-fingerprints](https://docs.wise.com/api-reference/sca-device-fingerprints/scadevicefingerprintcreate.md): Creates a new device fingerprint factor used to resolve a SCA possession challenge type. The request and response are encrypted using the JOSE framework. Please refer to the [SCA over API guide](/guid
 - [POST /profiles/{profileId}/device-fingerprints/verify](https://docs.wise.com/api-reference/sca-device-fingerprints/scadevicefingerprintverify.md): Verifies a device fingerprint challenge when calling a SCA-secured endpoint. Make sure to [create a device fingerprint](/api-reference/sca-device-fingerprints/scadevicefingerprintcreate) before using
 - [DELETE /profiles/{profileId}/device-fingerprints/{deviceFingerprintId}](https://docs.wise.com/api-reference/sca-device-fingerprints/scadevicefingerprintdelete.md): Deletes a device fingerprint associated to a profile. Include the `deviceFingerprintId` in the URL to delete a device fingerprint. This ID is provided in the response when the device fingerprint is cr
## OTP

 - [POST /application/users/{userId}/phone-numbers](https://docs.wise.com/api-reference/sca-otp/usersecurityphonenumbercreate.md): Create a verified phone number for a user. This endpoint is restricted and requires both a client credentials token and additional access to use. Please speak with your implementation manager if you w
 - [POST /one-time-token/sms/trigger](https://docs.wise.com/api-reference/sca-otp/ottsmstrigger.md): To trigger a SMS challenge by sending SMS to user verified phone number. Contains a 6 digit one time password (**OTP**). Use this **OTP** code to clear an SMS challenge by using the [Verify SMS endpoi
 - [POST /one-time-token/sms/verify](https://docs.wise.com/api-reference/sca-otp/ottsmsverify.md): To clear a **SMS** challenge listed in a OTT. Notes: 1. User is required to have a verified phone number. See [create phone number](/api-reference/sca-otp/usersecurityphonenumbercreate) for more infor
 - [POST /one-time-token/whatsapp/trigger](https://docs.wise.com/api-reference/sca-otp/ottwhatsapptrigger.md): To trigger a WhatsApp challenge by sending WhatsApp message to user verified phone number. Contains a 6 digit one time password (**OTP**). Use this **OTP** code to clear a WHATSAPP challenge by using
 - [POST /one-time-token/whatsapp/verify](https://docs.wise.com/api-reference/sca-otp/ottwhatsappverify.md): To clear a **WHATSAPP** challenge listed in a OTT. Notes: 1. User is required to have a verified phone number. See [create phone number](/api-reference/sca-otp/usersecurityphonenumbercreate) for more
 - [POST /one-time-token/voice/trigger](https://docs.wise.com/api-reference/sca-otp/ottvoicetrigger.md): To trigger a Voice challenge by sending voice message to user verified phone number. Contains a 6 digit one time password (**OTP**). Use this **OTP** code to clear a VOICE challenge by using the [Veri
 - [POST /one-time-token/voice/verify](https://docs.wise.com/api-reference/sca-otp/ottvoiceverify.md): To clear a **VOICE** challenge listed in a OTT. Notes: 1. User is required to have a verified phone number. See [create phone number](/api-reference/sca-otp/usersecurityphonenumbercreate) for more inf
 - [DELETE /application/users/{userId}/phone-numbers/{phoneNumberId}](https://docs.wise.com/api-reference/sca-otp/usersecurityphonenumberdelete.md): Delete a verified phone number for a user. This endpoint is restricted and requires both a client credentials token and additional access to use. Please speak with your implementation manager if you w
## Balances

 - [Balance](https://docs.wise.com/api-reference/balance/balance.md): Schema: #/components/schemas/Balance
 - [HoldLimitBreach](https://docs.wise.com/api-reference/balance/holdlimitbreach.md): Schema: #/components/schemas/HoldLimitBreach
 - [POST /profiles/{profileId}/balances](https://docs.wise.com/api-reference/balance/balancecreate.md): Opens a balance within the specified profile, in the currency and type specified in the request. For `STANDARD` balances, only one can be created per currency. For `SAVINGS` balances, multiple in the
 - [GET /profiles/{profileId}/balances](https://docs.wise.com/api-reference/balance/balancelist.md): Retrieves the user's multi-currency account balance accounts. Returns all balance accounts the profile has in the types specified. The `types` parameter must include at least one type. To return more
 - [GET /profiles/{profileId}/balances/{balanceId}](https://docs.wise.com/api-reference/balance/balanceget.md): Returns a balance based on the specified balance ID.
 - [DELETE /profiles/{profileId}/balances/{balanceId}](https://docs.wise.com/api-reference/balance/balancedelete.md): Closes a balance account for the user's profile. Balance accounts must have a zero balance to be closed. Bank account details for the balance will also be deactivated and may not be restored.
 - [POST /profiles/{profileId}/balance-movements](https://docs.wise.com/api-reference/balance/balancemovement.md): This endpoint allows conversion and movement of funds between balance accounts. **Convert across balance accounts:** Convert funds between two `STANDARD` balance accounts in different currencies. Requ
 - [GET /profiles/{profileId}/balance-capacity](https://docs.wise.com/api-reference/balance/balancecapacity.md): Returns the deposit limit for a profile based on regulatory requirements. Useful for personal profiles located in countries that have hold limits. We advise calling this API before depositing money i
 - [POST /profiles/{profileId}/excess-money-account](https://docs.wise.com/api-reference/balance/excessmoneyaccount.md): If a balance goes over the regulatory hold limit, excess funds are automatically moved to another account at the end of the day. Use this endpoint to specify a recipient where excess money will be tr
 - [GET /profiles/{profileId}/total-funds/{currency}](https://docs.wise.com/api-reference/balance/totalfunds.md): Provides an overview of your account's total valuation and available liquidity across all balances. Returns total worth, total available (including overdraft), total cash, and overdraft details. ####
 - [GET /profiles/{profileId}/balances/hold-limit-breach](https://docs.wise.com/api-reference/balance/holdlimitbreachlist.md): Returns a list of hold limit breaches for a profile. A hold limit breach occurs when a balance exceeds the regulatory hold limit for that profile's country (e.g. Singapore, Malaysia). You can optional
 - [POST /profiles/{profileId}/balances/hold-limit-breach/{holdLimitBreachId}](https://docs.wise.com/api-reference/balance/holdlimitbreachclose.md): Closes an open hold limit breach by performing a one-time refund to a specified recipient. The recipient will receive the excess amount that caused the breach. Only breaches with `state: OPEN` can be
 - [POST hold-limit-breach#update](https://docs.wise.com/api-reference/balance/eventholdlimitbreachupdate.md): Triggered whenever a hold limit breach is opened or closed for a profile. A hold limit breach occurs when a balance exceeds the regulatory hold limit (applicable in countries such as Singapore and Mal
 - [POST balances#update](https://docs.wise.com/api-reference/balance/eventbalancesupdate.md): Triggered every time a multi-currency account is credited or debited. * Event type: `balances#update` * Profile level subscriptions: Supported * Application level subscriptions: Supported Events may
 - [POST balances#account-state-change](https://docs.wise.com/api-reference/balance/eventbalancesaccountstatechange.md): Triggered every time a balance account is activated or deactivated. * Event type: `balances#account-state-change` * Profile level subscriptions: Not Supported * Application level subscriptions: Suppor
## Balance Statements

 - [GET /profiles/{profileId}/balance-statements/{balanceId}/statement.json](https://docs.wise.com/api-reference/balance-statement/balancestatementget.md): Retrieve a statement for the specified balance account. The response format depends on the URL path: - `statement.json` - JSON format - `statement.csv` - CSV format - `statement.pdf` - PDF format (inc
## Bank Account Details

 - [POST /profiles/{profileId}/bank-details](https://docs.wise.com/api-reference/bank-account-details/bankaccountdetailsbankdetailscreate.md): Creates and assigns a pair of local account details and international account details (where available) that are linked to the target balance specified in the request. Please reach out to our Support
 - [GET /balances/account-details/{id}](https://docs.wise.com/api-reference/bank-account-details/getaccountdetails.md): Retrieves account details by ID. Account details identify an account that can receive funds (e.g. an IBAN, or a sort code and account number). GB, US and BE account details are supported. Requesting a
 - [POST /profiles/{profileId}/account-details-orders](https://docs.wise.com/api-reference/bank-account-details/bankaccountdetailsordercreate.md): Creates an order which will issue account details. It should use the same currency as the balance previously created. Fulfilling all the requirements will complete the order, reaching status `DONE`. T
 - [GET /profiles/{profileId}/account-details-orders](https://docs.wise.com/api-reference/bank-account-details/bankaccountdetailsorderslist.md): Returns the bank account assignment requests for a profile and multi-currency account. The response includes bank-details orders in the following statuses: `PENDING_USER`, `PENDING_TW`, `REQUIREMENTS_
 - [POST account-details-order#order-state-change](https://docs.wise.com/api-reference/bank-account-details/eventaccountdetailsorderstatechange.md): The event contains information about the order state and requirement state. Triggered when there is a change in the state of an account details order. * Event type: `account-details-order#order-state-
 - [POST account-details-payment#state-change](https://docs.wise.com/api-reference/bank-account-details/eventaccountdetailspaymentstatechange.md): Triggered every time a pay-in is made into the specified account details. * Event type: `account-details-payment#state-change` * Profile level subscriptions: Supported * Application level subscription
## Multi Currency Account

 - [GET /borderless-accounts-configuration/profiles/{profileId}/available-currencies](https://docs.wise.com/api-reference/multi-currency-account/mcaavailablecurrenciesget.md): Lists all currencies that are available for balance accounts. This includes those that can have funds added from external accounts, as well as those that a balance can be held in.
 - [GET /borderless-accounts-configuration/profiles/{profileId}/payin-currencies](https://docs.wise.com/api-reference/multi-currency-account/mcapayincurrenciesget.md): Lists all currencies available for balance accounts that also support bank account details. You can use this list to create a balance account for the currency included and then subsequently create ban
 - [GET /profiles/{profileId}/multi-currency-account](https://docs.wise.com/api-reference/multi-currency-account/mcaget.md): Returns the multi-currency account details for the specified profile. If the user does not yet have a multi-currency account, a `404 Not Found` will be returned.
 - [GET /multi-currency-account/eligibility](https://docs.wise.com/api-reference/multi-currency-account/mcaeligibilityget.md): Checks eligibility for a multi-currency account for either a specific profile or for a location. Customers in some countries and states/provinces may not be eligible for a multi currency account. To c
## Incoming Transfers

 - [GET /incoming-transfers/{incomingTransferId}](https://docs.wise.com/api-reference/incoming-transfer/getincomingtransfer.md): Retrieves an incoming transfer by id. You can pull the incoming-transfer ID from the webhook payload.
 - [POST incoming-transfer#credited](https://docs.wise.com/api-reference/incoming-transfer/eventincomingtransfercredited.md): Triggered when an incoming transfer is credited to a Wise balance. This is a thin event, containing just the `incoming_transfer_id`. Fetch the full resource via the [incoming transfer endpoint](/api-r
## Cards

 - [Card](https://docs.wise.com/api-reference/card/card.md): Schema: #/components/schemas/Card
 - [Permission](https://docs.wise.com/api-reference/card/permission.md): Schema: #/components/schemas/Permission
 - [GET /spend/profiles/{profileId}/cards](https://docs.wise.com/api-reference/card/cardlist.md): Returns a paginated list of cards that belong to a specific profile.
 - [GET /spend/profiles/{profileId}/cards/{cardToken}](https://docs.wise.com/api-reference/card/cardget.md): Retrieves details for a specific card by its token.
 - [PUT /spend/profiles/{profileId}/cards/{cardToken}/status](https://docs.wise.com/api-reference/card/cardstatusupdate.md): Update the status of a card. For cards issued with an `INACTIVE` status, updating to `ACTIVE` will activate the card and move the card order status to `COMPLETED`. **Available status transitions:** -
 - [POST /spend/profiles/{profileId}/cards/{cardToken}/reset-pin-count](https://docs.wise.com/api-reference/card/cardpincountreset.md): If the wrong PIN has been entered more than 3 times, future transactions on the card will be blocked with a `PIN_ENTRY_TRIES_EXCEEDED` error message. Use this endpoint to reset the PIN count to 0 and
 - [PATCH /spend/profiles/{profileId}/cards/{cardToken}/spending-permissions](https://docs.wise.com/api-reference/card/cardpermissionsbulkupdate.md): Enable or disable multiple spending permissions on a card in a single request. This is the recommended endpoint for updating card permissions as it allows updating multiple permissions atomically.
 - [POST cards#card-status-change](https://docs.wise.com/api-reference/card/eventcardscardstatuschange.md): This event is triggered for the initial card status as well as any subsequent updates. * Event type: `cards#card-status-change` * Profile level subscriptions: Not Supported * Application level subscri
 - [POST cards#manual-provisioning-verification](https://docs.wise.com/api-reference/card/eventcardsmanualprovisioningverification.md): Triggered when a card is manually added to a wallet provider, and the verification methods required to complete the wallet provisioning are returned. * Event type: `cards#manual-provisioning-verificat
## Sensitive Card Details

 - [GET /twcard-data/v1/clientSideEncryption/fetchEncryptingKey](https://docs.wise.com/api-reference/card-sensitive-details/cardencryptionkeyget.md): Fetches Wise's RSA public key required for encrypting sensitive card data requests. This key is used in the [sensitive card details flow](/guides/product/issue-cards/sensitive-card-details) to create
 - [POST /twcard-data/v1/sensitive-card-data/details](https://docs.wise.com/api-reference/card-sensitive-details/cardsensitivedetailsget.md): Fetches the card's Primary Account Number (PAN), security code (CVV2), expiry date, and cardholder name. Requires an encrypted JWE payload for security. See the [sensitive card details guide](/guides/
 - [POST /twcard-data/v1/sensitive-card-data/pin](https://docs.wise.com/api-reference/card-sensitive-details/cardpinget.md): Fetches the card's PIN. Requires an encrypted JWE payload for security. See the [sensitive card details guide](/guides/product/issue-cards/sensitive-card-details) for implementation details. This endp
 - [POST /twcard-data/v1/sensitive-card-data/preset-pin](https://docs.wise.com/api-reference/card-sensitive-details/cardorderpresetpin.md): Sets a PIN during the card order flow. This endpoint will be accessible for partners that require to set a PIN during the card order flow. Please follow [this guide](/guides/product/issue-cards/sensit
## 3D Secure Authentication

 - [POST /spend/profiles/{profileId}/3dsecure/challenge-result](https://docs.wise.com/api-reference/3ds/3dschallengeresultpost.md): Once the customer has accepted or rejected the push notification for a 3DS challenge, use this endpoint to notify Wise of the result. You must call this endpoint before the expiration time (provided i
 - [POST cards#3ds-challenge](https://docs.wise.com/api-reference/3ds/eventcards3dschallenge.md): Triggered when a customer initiates a push notification for 3DS. The provided information can be used to send a push notification to the customer's mobile app. * Event type: `cards#3ds-challenge` * Pr
## Card Kiosk Collection

 - [PUT /spend/profiles/{profileId}/cards/{cardToken}/production](https://docs.wise.com/api-reference/card-kiosk-collection/cardkioskcollectionproduce.md): Sends the card production request to a kiosk machine. To confirm that card information has been successfully created, listen to the [card-production-status-change](/api-reference/webhook-event/eventca
 - [GET /spend/profiles/{profileId}/cards/{cardToken}/production](https://docs.wise.com/api-reference/card-kiosk-collection/cardkioskcollectionproductionget.md): Retrieves the current production status of a card at a kiosk machine. **Best practice**: Subscribe to the [card production status change](/api-reference/webhook-event/eventcardscardproductionstatuscha
 - [POST cards#card-production-status-change](https://docs.wise.com/api-reference/card-kiosk-collection/eventcardscardproductionstatuschange.md): Triggered every time a card production status is updated. This webhook is solely used for physical cards with `KIOSK_COLLECTION` delivery method. For more details, see the [Card kiosk collection guide
## Card Orders

 - [Card Order](https://docs.wise.com/api-reference/card-order/cardorder.md): Schema: #/components/schemas/CardOrder
 - [POST /spend/profiles/{profileId}/card-orders](https://docs.wise.com/api-reference/card-order/cardordercreate.md): Creates a new card order. The `program` field value is retrieved from the [retrieve all card programs](/api-reference/card-order/cardorderprogramsget) endpoint. This request requires an extra field in
 - [GET /spend/profiles/{profileId}/card-orders](https://docs.wise.com/api-reference/card-order/cardorderlist.md): Retrieves a list of card orders created for the specified `profileId`.
 - [GET /spend/profiles/{profileId}/card-orders/{cardOrderId}](https://docs.wise.com/api-reference/card-order/cardorderget.md): Retrieves a card order based on the `cardOrderId`.
 - [GET /spend/profiles/{profileId}/card-orders/availability](https://docs.wise.com/api-reference/card-order/cardorderprogramsget.md): Retrieves the list of available card programs for each `profileId`.
 - [GET /spend/profiles/{profileId}/card-orders/{cardOrderId}/requirements](https://docs.wise.com/api-reference/card-order/cardorderrequirementsget.md): Retrieves all card requirements for a `cardOrderId`. A valid card order needs all its requirements status to be `COMPLETED`. The type of requirements are: - `PIN (optional)`: [Set a PIN](/api-referenc
 - [PUT /spend/profiles/{profileId}/card-orders/{cardOrderId}/status](https://docs.wise.com/api-reference/card-order/cardorderstatusupdate.md): Updates the status of a card order based on its `cardOrderId`. The status can be updated to one of the following: 1. `CANCELLED` 2. `COMPLETED` (deprecated) The behaviour for card order cancellation
 - [POST /spend/address/validate](https://docs.wise.com/api-reference/card-order/cardordervalidateaddress.md): Validates the format of an address for a card order. Make sure to follow country-specific address fields and validation as described in the [card address validation guide](/guides/developer/api-guides
 - [POST cards#card-order-status-change](https://docs.wise.com/api-reference/card-order/eventcardscardorderstatuschange.md): This event is triggered every time a card order status is updated. Statuses depend on the type of card (virtual/physical). Additional statuses related to delivery exist for physical cards. * Event typ
## Card Transactions

 - [GET /spend/profiles/{profileId}/cards/transactions/{transactionId}](https://docs.wise.com/api-reference/card-transaction/cardtransactionget.md): Retrieve a card transaction by its ID. Use in conjunction with the [card transaction state change webhook](/api-reference/webhook-event/eventcardstransactionstatechange) for versions V2.1.0 and later.
 - [GET /spend/profiles/{profileId}/cards/{cardToken}/transactions](https://docs.wise.com/api-reference/card-transaction/cardtransactionlist.md): Retrieve a list of card transactions for a specific card. Transactions are ordered by transaction ID in descending order. Use in conjunction with the [card transaction state change webhook](/api-refer
 - [POST cards#transaction-state-change](https://docs.wise.com/api-reference/card-transaction/eventcardstransactionstatechange.md): Triggered whenever a new card transaction occurs or is modified. * Event type: `cards#transaction-state-change` * Profile level subscriptions: Not Supported * Application level subscriptions: Supporte
## Spend Limits

 - [Profile Limits](https://docs.wise.com/api-reference/spend-limits/profile-limits.md): Schema: #/components/schemas/profile-limits
 - [Card Limits](https://docs.wise.com/api-reference/spend-limits/card-limits.md): Schema: #/components/schemas/card-limits
 - [Card Holder Limits](https://docs.wise.com/api-reference/spend-limits/card-holder-limits.md): Schema: #/components/schemas/card-holder-limits
 - [GET /spend/profiles/{profileId}/spend-limits](https://docs.wise.com/api-reference/spend-limits/spendlimitsprofileget.md): Retrieves the spend limits that are configured for a profile.
 - [PATCH /spend/profiles/{profileId}/spend-limits](https://docs.wise.com/api-reference/spend-limits/spendlimitsprofileupdate.md): Update profile daily and monthly spend limits for `PURCHASE` or `ATM_WITHDRAWAL`. Both daily and monthly must be set.
 - [GET /spend/profiles/{profileId}/cards/{cardToken}/spend-limits](https://docs.wise.com/api-reference/spend-limits/spendlimitscardget.md): Retrieves the spend limits that are configured for a card.
 - [PATCH /spend/profiles/{profileId}/cards/{cardToken}/spend-limits](https://docs.wise.com/api-reference/spend-limits/spendlimitscardupdate.md): Create or update card transaction, daily, monthly or lifetime spend limits.
 - [DELETE /spend/profiles/{profileId}/cards/{cardToken}/spend-limits/{granularity}](https://docs.wise.com/api-reference/spend-limits/spendlimitscarddelete.md): Delete card spend limits for a specific granularity.
 - [GET /spend/profiles/{businessProfileId}/card-holder-profiles/{cardHolderProfileId}/spend-limits](https://docs.wise.com/api-reference/spend-limits/spendlimitscardholderget.md): Retrieves the spend limits that are configured for a cardholder. These limits apply across all cards belonging to that cardholder, not to an individual card.
 - [PATCH /spend/profiles/{businessProfileId}/card-holder-profiles/{cardHolderProfileId}/spend-limits](https://docs.wise.com/api-reference/spend-limits/spendlimitscardholderupdate.md): Create or update daily and monthly spend limits for a cardholder. Only the `PURCHASE` limit type is supported for cardholder limits.Any other value for `type`, including `ATM_WITHDRAWAL`, is rejected
 - [DELETE /spend/profiles/{businessProfileId}/card-holder-profiles/{cardHolderProfileId}/spend-limits](https://docs.wise.com/api-reference/spend-limits/spendlimitscardholderdelete.md): Removes all configured spend limits for a cardholder. Both the daily and monthly windows are removed together; individual windows cannot be removed separately. Succeeds whether or not limits are curr
## Spend Controls

 - [Authorisation Rule](https://docs.wise.com/api-reference/spend-controls/rule.md): Schema: #/components/schemas/rule
 - [POST /spend/applications/{clientId}/spend-controls/rules](https://docs.wise.com/api-reference/spend-controls/spendcontrolsrulecreate.md): Creates an authorisation rule. It won't be enabled unless it is [applied](/api-reference/spend-controls/spendcontrolsruleapply). An `ALLOW` rule permits only the transactions that match the specified
 - [GET /spend/applications/{clientId}/spend-controls/rules](https://docs.wise.com/api-reference/spend-controls/spendcontrolsruleslist.md): Retrieves all the existing authorisation rules, regardless of whether or not they are applied.
 - [POST /spend/applications/{clientId}/spend-controls/rules/apply](https://docs.wise.com/api-reference/spend-controls/spendcontrolsruleapply.md): Apply an authorisation rule. This will result in the rule being evaluated against every incoming card authorisation request.
 - [POST /spend/applications/{clientId}/spend-controls/rules/unapply](https://docs.wise.com/api-reference/spend-controls/spendcontrolsruleunapply.md): Deactivates an authorisation rule. This will result in all card transactions **not** being evaluated against this rule. The rule still [exists](/api-reference/spend-controls/spendcontrolsruleslist) an
 - [GET /spend/applications/{clientId}/spend-controls/rules/applied](https://docs.wise.com/api-reference/spend-controls/spendcontrolsappliedruleslist.md): Returns the list of all the active authorisation rules that have been applied.
 - [DELETE /spend/applications/{clientId}/spend-controls/rules/{ruleId}](https://docs.wise.com/api-reference/spend-controls/spendcontrolsruledelete.md): Deletes an authorisation rule that is **currently not applied**. If a rule is applied, you should [unapply](/api-reference/spend-controls/spendcontrolsruleunapply) the rule before deleting it.
## Digital Wallet

 - [POST /spend/profiles/{profileId}/cards/{cardToken}/payment-tokens](https://docs.wise.com/api-reference/digital-wallet/pushprovisioningpaymenttokenslist.md): You have the option to obtain the payment tokens associated with a card, which can assist in determining if it's already linked to a specific wallet. Note that the payment token status associated with
 - [POST /spend/profiles/{profileId}/cards/{cardToken}/payment-tokens/{paymentTokenUniqueReference}/activation](https://docs.wise.com/api-reference/digital-wallet/digitalwalletactivatepaymenttoken.md): This endpoint activates the payment token for a card that has been manually added to a wallet provider. Please read this [guide](/guides/product/issue-cards/card-digital-wallet.md) before implementing
 - [POST /twcard-data/v1/push-provisioning/encrypted-payload/google-pay](https://docs.wise.com/api-reference/digital-wallet/pushprovisioninggooglepayget.md): Returns encrypted cardholder information and other metadata needed for Google Pay push provisioning. This API is not available for sandbox testing.
 - [POST /twcard-data/v1/push-provisioning/encrypted-payload/apple-pay](https://docs.wise.com/api-reference/digital-wallet/pushprovisioningapplepayget.md): Returns encrypted cardholder information and other metadata needed for Apple Pay push provisioning. This API is not available for sandbox testing.
## Disputes

 - [POST /spend/profiles/{profileId}/dispute-form/flows/step/{scheme}/{reason}](https://docs.wise.com/api-reference/disputes/disputedynamicflowstep.md): Retrieves the JSON for initiating the dispute flow. Use this endpoint with Wise's [Dynamic Flow framework](https://www.npmjs.com/package/@transferwise/dynamic-flows). The JSON response must be passed
 - [GET /spend/profiles/{profileId}/dispute-form/reasons](https://docs.wise.com/api-reference/disputes/disputereasonsget.md): Retrieves the list of possible reasons for submitting a dispute. If a reason code has `subOptions`, those should be used as the reason code when submitting disputes.
 - [POST /spend/profiles/{profileId}/dispute-form/flows/{scheme}/{reason}](https://docs.wise.com/api-reference/disputes/disputesubmit.md): Submit a dispute for a card transaction. The request body structure varies per dispute reason code. All reasons share a common structure with `transaction`, `form`, `disclaimer`, and `files` objects,
 - [POST /spend/profiles/{profileId}/dispute-form/file](https://docs.wise.com/api-reference/disputes/disputefileupload.md): Upload a file for use in a dispute submission. Use the returned file ID in the `files` object when submitting a dispute. A dispute referencing the returned file ID must be submitted no later than **tw
 - [GET /spend/profiles/{profileId}/disputes](https://docs.wise.com/api-reference/disputes/disputelist.md): List disputes for a profile with optional filters.
 - [GET /spend/profiles/{profileId}/disputes/{disputeId}](https://docs.wise.com/api-reference/disputes/disputeget.md): Retrieve a dispute by its ID.
 - [PUT /spend/profiles/{profileId}/disputes/{disputeId}/status](https://docs.wise.com/api-reference/disputes/disputewithdraw.md): Withdraw a dispute by setting its status to `CLOSED`. You can only withdraw a dispute if `canWithdraw` is `true` on the dispute resource.
 - [POST transaction-disputes#update](https://docs.wise.com/api-reference/disputes/eventtransactiondisputesupdate.md): Triggered every time a transaction dispute is submitted or updated. You may receive update events even when there are no apparent changes in the dispute `status` or `subStatus`, as certain underlying
## Quotes

 - [Quote](https://docs.wise.com/api-reference/quote/quote.md): Schema: #/components/schemas/quote
 - [Types of quotes](https://docs.wise.com/api-reference/quote/types-of-quotes.md): ### Types of quotes With the Wise API you can create either **unauthenticated** or **authenticated** quotes. **Unauthenticated quotes** are for illustrative purposes only. Use this option to display e
 - [POST /quotes](https://docs.wise.com/api-reference/quote/quotecreateunauthenticated.md): Use this endpoint to get example quotes for illustrative purposes. This allows you to show the exchange rate and fees Wise offers before a user has created or linked an account. Often used to display
 - [POST /profiles/{profileId}/quotes](https://docs.wise.com/api-reference/quote/quotecreate.md): Create an authenticated quote when the quote is to be used for a transfer. Authenticated quotes require a user access token to authenticate. You must also include the profile the quote should be assoc
 - [GET /profiles/{profileId}/quotes/{quoteId}](https://docs.wise.com/api-reference/quote/quoteget.md): Get quote info by ID. If the quote has expired (not used to create a transfer within 30 minutes of quote creation), it will only be accessible for approximately 48 hours via this endpoint.
 - [PATCH /profiles/{profileId}/quotes/{quoteId}](https://docs.wise.com/api-reference/quote/quoteupdate.md): When generating a quote before a recipient, you must update the quote with the recipient `sourceAccount` value, as the recipient details may impact the quote properties like available payment options,
## Exchange Rates

 - [GET /rates](https://docs.wise.com/api-reference/rate/rateget.md): The `from`, `to`, and `group` parameters are not testable in our Sandbox environment at this time. `GET /rates` Fetch latest exchange rates of all currencies. `GET /rates?source=EUR&target=USD` Fetch
## Comparison

 - [GET /comparisons](https://docs.wise.com/api-reference/comparison/comparisonget.md): Request price and speed comparison data for money transfer providers on a given currency route. You must provide either `sendAmount` or `recipientGetsAmount` (but not both).
## Recipient Accounts

 - [Recipient Account](https://docs.wise.com/api-reference/recipient/recipient.md): Schema: #/components/schemas/recipient
 - [GET /accounts](https://docs.wise.com/api-reference/recipient/recipientlist.md): Fetches a list of the user's recipient accounts. #### Notes about query params - All query parameters are optional. - Pagination is supported. - Set the `size` parameter to determine the number of a
 - [POST /accounts](https://docs.wise.com/api-reference/recipient/recipientcreate.md): Creates a recipient account. A **recipient** is the person or institution who is the ultimate beneficiary of your payment. Recipient data includes: - The personal details of an individual or basic inf
 - [GET /accounts/{accountId}](https://docs.wise.com/api-reference/recipient/recipientget.md): Get recipient account info by ID. V1 and v2 versions are cross compatible, but the v2 endpoint provides additional features.
 - [DELETE /accounts/{accountId}](https://docs.wise.com/api-reference/recipient/recipientdeactivate.md): Deletes a recipient by changing its status to inactive (`"active": false`). A request to delete a recipient that is already inactive returns `HTTP 403 (Forbidden)`. Only active recipients can be delet
 - [GET /quotes/{quoteId}/account-requirements](https://docs.wise.com/api-reference/recipient/recipientaccountrequirementsget.md): The details required to create a recipient account vary by currency, type, and receiving entity. To determine which fields are required to successfully create a specific recipient, send a request to t
 - [POST /quotes/{quoteId}/account-requirements](https://docs.wise.com/api-reference/recipient/recipientaccountrequirementspost.md): If `refreshRequirementsOnChange=true` for any `group.key` in the [GET response](/api-reference/recipient/recipientaccountrequirementsget#recipient/recipientaccountrequirementsget/response&c=200), send
 - [POST /accounts/{accountId}/quotes/{quoteId}/compatibility](https://docs.wise.com/api-reference/recipient/recipientcompatibilitycheck.md): Use this endpoint to check the compatibility of a recipient account with a quote before creating a transfer. This validation includes: - Re-validating the recipient account details. - Checking all req
 - [PATCH /accounts/{accountId}/confirmations](https://docs.wise.com/api-reference/recipient/recipientconfirmationsaccept.md): When the confirmation outcome indicates `requiresCustomerAcceptance` is `true`, the recipient cannot be used for a transfer until the customer explicitly confirms the details. Present the mismatch to
 - [POST recipients#state-change](https://docs.wise.com/api-reference/recipient/eventrecipientsstatechange.md): Triggered when a recipient account created or changed through hosted recipient creation changes state. See the [Embedded Flows guide](/guides/product/embedded-flows/index.md#hosted-recipient-creation-
## Contacts

 - [POST /profiles/{profileId}/contacts](https://docs.wise.com/api-reference/contact/contactcreate.md): Finds an existing **discoverable** Wise profile and adds it to your recipient list. The recipient is found by an identifier — such as a Wisetag, email, or phone number — without needing bank details.
## Transfers

 - [Standard Transfer](https://docs.wise.com/api-reference/transfer/transfer.md): Schema: #/components/schemas/transfer
 - [Originator Transfer](https://docs.wise.com/api-reference/transfer/originator-transfer.md): Schema: #/components/schemas/originator-transfer
 - [GET /transfers/{transferId}](https://docs.wise.com/api-reference/transfer/transferget.md): Get transfer info by ID. To receive dynamic updates as the state of the transfer changes, see the [webhooks documentation](/guides/developer/webhooks).
 - [PUT /transfers/{transferId}/cancel](https://docs.wise.com/api-reference/transfer/transfercancel.md): Transfers can be cancelled via API when they are in the `incoming_payment_waiting` state. If the transfer is being held for compliance-related reasons or has moved into the `funds_converted` state, th
 - [POST /transfer-requirements](https://docs.wise.com/api-reference/transfer/transferrequirementsvalidate.md): Exposes transfer-specific requirements based on the sender, quote, and target recipient account. Requirements vary by currency route, transfer amount, and regulatory region. For example, the maximum a
 - [POST /profiles/{profileId}/transfers/{transferId}/payments](https://docs.wise.com/api-reference/transfer/transferfund.md): This endpoint is SCA protected when it applies. If your profile is registered within the UK and/or EEA, SCA most likely applies to you. Please read more about [implementing SCA](/guides/developer/auth
 - [GET /transfers/{transferId}/payments](https://docs.wise.com/api-reference/transfer/transferpaymentslist.md): Fetch completed payments used to fund the transfer. In most cases there should only be a single payment associated with the transfer. There are rare occasions that a transfer can be funded with multi
 - [GET /transfers/{transferId}/invoices/bankingpartner](https://docs.wise.com/api-reference/transfer/transferpayoutinfoget.md): Fetch banking reference information for transfers that are in `outgoing_payment_sent` status. Enables you to track transfers with the transfer recipient's bank. Querying this endpoint too soon after t
 - [GET /transfers/{transferId}/receipt.pdf](https://docs.wise.com/api-reference/transfer/transferreceiptget.md): Download transfer confirmation receipt in PDF format for transfers that are in status `outgoing_payment_sent`. There's also the [transfer state change webhook](/api-reference/webhook-event/eventtransf
 - [GET /transfers/{transferId}/us-combined-receipt.pdf](https://docs.wise.com/api-reference/transfer/transferuscombinedreceiptget.md): Download US combined receipt in PDF format for transfers that are in status `incoming_payment_initiated` and again when the status is updated to `outgoing_payment_sent`.
 - [GET /transfers/{transferId}/documents/noc](https://docs.wise.com/api-reference/transfer/transfernocget.md): Download transfer non objection certificate in PDF format for transfers that are in status `outgoing_payment_sent`. This document can be used to obtain a Foreign Inward Remittance Certificate (FIRC) f
 - [POST transfers#active-cases](https://docs.wise.com/api-reference/transfer/eventtransfersactivecases.md): Triggered every time a transfer's list of active cases is updated. Active cases indicate potential problems with transfer processing. * Event type: `transfers#active-cases` * Profile level subscriptio
 - [POST transfers#refund](https://docs.wise.com/api-reference/transfer/eventtransfersrefund.md): This event provides information about refund amount and currency. Triggered every time a transfer's status becomes `funds_refunded`. * Event type: `transfers#refund` * Profile level subscriptions: Sup
 - [POST transfers#payout-failure](https://docs.wise.com/api-reference/transfer/eventtransferspayoutfailure.md): Triggered every time a payout fails. Use this event to get further information about a failed payment. * Event type: `transfers#payout-failure` * Profile level subscriptions: Supported * Application l
 - [POST transfers#state-change](https://docs.wise.com/api-reference/transfer/eventtransfersstatechange.md): Triggered every time a transfer's status is updated. * Event type: `transfers#state-change` * Profile level subscriptions: Supported * Application level subscriptions: Supported For topup-to-balance
## Standard Transfers

 - [POST /transfers](https://docs.wise.com/api-reference/standard-transfer/transfercreate.md): Create a transfer to a recipient account based on a quote. Some fields are conditionally required depending on the currency route and transfer amount. Always call the [transfer requirements](/api-refe
 - [GET /transfers](https://docs.wise.com/api-reference/standard-transfer/transferlist.md): Get the list of transfers for a given user's profile (defaults to user's personal profile). You can add query parameters to specify user's profile (personal or business), time period and/or payment s
## Third Party Transfers

 - [POST /profiles/{profileId}/third-party-transfers](https://docs.wise.com/api-reference/third-party-transfer/createthirdpartytransfer.md): When creating a transfer on behalf of a third party, you must take note that: * The `originator` datablock is **required**. This details the ultimate sender of funds in the transfer. * Depending on th
 - [GET /profiles/{profileId}/third-party-transfers/{transferId}](https://docs.wise.com/api-reference/third-party-transfer/getthirdpartytransfer.md): Get third party transfer info by ID. To receive dynamic updates as the state of the transfer changes, see the [webhooks documentation](https://docs.wise.com/api-reference/webhook).
## Delivery Estimate

 - [GET /delivery-estimates/{transferId}](https://docs.wise.com/api-reference/delivery-estimate/deliveryestimateget.md): Get the live delivery estimate for a transfer by the transfer ID. The delivery estimate is the time at which we currently expect the transfer to arrive in the beneficiary's bank account. This is not
## Currencies

 - [GET /currencies](https://docs.wise.com/api-reference/currencies/currenciesget.md): Returns all currencies available for creating transfers. Currency names are returned in English by default — pass an `Accept-Language` header to receive localized names.
## Batch Payment Groups

 - [Batch Group](https://docs.wise.com/api-reference/batch-group/batchgroup.md): Schema: #/components/schemas/BatchGroup
 - [POST /profiles/{profileId}/batch-groups](https://docs.wise.com/api-reference/batch-group/batchgroupcreate.md): Create a new batch group. A batch group can hold up to 1000 transfers that will be funded together. After creating the group, add transfers to it, then complete the group to receive pay-in details.
 - [GET /profiles/{profileId}/batch-groups/{batchGroupId}](https://docs.wise.com/api-reference/batch-group/batchgroupget.md): Get an existing batch group by ID.
 - [PATCH /profiles/{profileId}/batch-groups/{batchGroupId}](https://docs.wise.com/api-reference/batch-group/batchgroupupdate.md): Update a batch group's status to complete or cancel it. **Complete a batch group:** Set `status` to `COMPLETED` to close the group for modifications and allow funding to proceed. Once completed, `payI
 - [POST /profiles/{profileId}/batch-groups/{batchGroupId}/transfers](https://docs.wise.com/api-reference/batch-group/batchgrouptransfercreate.md): Create a transfer in the batch group using a previously created recipient account and quote. For the request body format, see [transfer creation](/api-reference/transfer#create). For quote and recipie
 - [POST /profiles/{profileId}/batch-payments/{batchGroupId}/payments](https://docs.wise.com/api-reference/batch-group/batchgroupfund.md): Funds all transfers in a batch group from a multi-currency account balance. Transfers are paid out immediately. The batch group must first be completed and there must be enough funds in the account fo
 - [POST /profiles/{profileId}/batch-groups/{batchGroupId}/payment-initiations](https://docs.wise.com/api-reference/batch-group/batchgrouppaymentinitiationcreate.md): Funds all transfers in a batch group via direct debit. The batch group must be in the `COMPLETED` state. To use this funding method, you must link an external bank account first. See [direct debit acc
 - [GET /profiles/{profileId}/batch-groups/{batchGroupId}/payment-initiations/{paymentInitiationId}](https://docs.wise.com/api-reference/batch-group/batchgrouppaymentinitiationget.md): Get payment initiation info by ID. In addition to [webhooks](/api-reference/webhook-event/eventbatchpaymentinitiationsstatechange), this endpoint can be used for polling the status of a payment initia
 - [POST batch-payment-initiations#state-change](https://docs.wise.com/api-reference/batch-group/eventbatchpaymentinitiationsstatechange.md): Triggered when the payment initiation state of a batch group payment changes. The expected state of a batch payment initiation can be one of: - `NEW` - `PROCESSING` - `COMPLETED` - `FAILED` - `CHARGED
## Payin Deposit Detail

 - [GET /profiles/{profileId}/transfers/{transferId}/deposit-details/bank-transfer](https://docs.wise.com/api-reference/payin-deposit-detail/payindepositdetailget.md): Retrieve the bank details for the account that the customer should send funds to when paying for a Wise transfer via a bank transfer. `profileId` in the request URL refers to the profile that created
## Direct Debit Account

 - [POST /profiles/{profileId}/direct-debit-accounts](https://docs.wise.com/api-reference/direct-debit-account/directdebitaccountcreate.md): Register a new external bank account for funding batch transfers via direct debit.
 - [GET /profiles/{profileId}/direct-debit-accounts](https://docs.wise.com/api-reference/direct-debit-account/directdebitaccountget.md): Get a list of your direct debit accounts. Use the `type` and `currency` query parameters to filter accounts.
## Bulk Settlement

 - [POST /settlements](https://docs.wise.com/api-reference/bulk-settlement/bulksettlementjournalcreate.md): Sends the settlement journal to Wise. There are two types of settlement: - **Same Currency Settlement** — Settle in the same currency as the transfers (e.g., settle USD transfers with USD). - **Cross
 - [POST bulk-settlement#payment-received](https://docs.wise.com/api-reference/bulk-settlement/eventbulksettlementpaymentreceived.md): Triggered when a bulk settlement fund is received. Once there is a match, meaning the amount for this settlement journal is fully settled, the `amount_matched` is set to `true`. If it is not matched,
## Payins

 - [POST /profiles/{profileId}/payin-sessions/{payinSessionId}/paynow](https://docs.wise.com/api-reference/payins/paynowcreate.md): Creates the encoded QR code and details for the payin session so the user can fund a transfer or balance top-up via a PayNow transaction. This operation supports the SGD currency only.
## Payment Instruments

 - [POST /profiles/{profileId}/payment-instruments](https://docs.wise.com/api-reference/payment-instruments/paymentinstrumentscreate.md): Creates a payment-instrument
 - [GET /profiles/{profileId}/payment-instruments/{paymentInstrumentId}](https://docs.wise.com/api-reference/payment-instruments/paymentinstrumentsget.md): Retrieves a payment instrument.
 - [POST /profiles/{profileId}/payment-instruments/{paymentInstrumentId}/manual-confirmation](https://docs.wise.com/api-reference/payment-instruments/paymentinstrumentconfirm.md): Manually confirms a payment instrument
 - [GET /profiles/{profileId}/payment-instruments/{paymentInstrumentId}/payins](https://docs.wise.com/api-reference/payment-instruments/paymentinstrumentgetallpayins.md): Get all payins for a given payment instrument
 - [POST /profiles/{profileId}/payment-instruments/{paymentInstrumentId}/payins](https://docs.wise.com/api-reference/payment-instruments/paymentinstrumentcreatepayin.md): Create a payin for payment instrument
## Subscriptions

 - [POST /applications/{clientKey}/subscriptions](https://docs.wise.com/api-reference/webhook/webhookapplicationsubscriptioncreate.md): Create a webhook subscription at the application level. `clientKey` can be received upon obtaining client credentials from our tech support.
 - [GET /applications/{clientKey}/subscriptions](https://docs.wise.com/api-reference/webhook/webhookapplicationsubscriptionlist.md): List all webhook subscriptions for your application.
 - [GET /applications/{clientKey}/subscriptions/{subscriptionId}](https://docs.wise.com/api-reference/webhook/webhookapplicationsubscriptionget.md): Retrieve an application webhook subscription by its identifier.
 - [DELETE /applications/{clientKey}/subscriptions/{subscriptionId}](https://docs.wise.com/api-reference/webhook/webhookapplicationsubscriptiondelete.md): Delete an application webhook subscription by its identifier.
 - [POST /applications/{clientKey}/subscriptions/{subscriptionId}/test-notifications](https://docs.wise.com/api-reference/webhook/webhookapplicationsubscriptiontest.md): Generate test notifications for an existing application subscription. Test notifications will have the correct structure for their source subscription's event type and version, and will contain "dummy
 - [POST /profiles/{profileId}/subscriptions](https://docs.wise.com/api-reference/webhook/webhookprofilesubscriptioncreate.md): Create a webhook subscription at the profile level.
 - [GET /profiles/{profileId}/subscriptions](https://docs.wise.com/api-reference/webhook/webhookprofilesubscriptionlist.md): List all webhook subscriptions for a profile.
 - [GET /profiles/{profileId}/subscriptions/{subscriptionId}](https://docs.wise.com/api-reference/webhook/webhookprofilesubscriptionget.md): Retrieve a profile webhook subscription by its identifier.
 - [DELETE /profiles/{profileId}/subscriptions/{subscriptionId}](https://docs.wise.com/api-reference/webhook/webhookprofilesubscriptiondelete.md): Delete a profile webhook subscription by its identifier.
## Events

 - [POST transfers#active-cases](https://docs.wise.com/api-reference/webhook-event/eventtransfersactivecases.md): Triggered every time a transfer's list of active cases is updated. Active cases indicate potential problems with transfer processing. * Event type: `transfers#active-cases` * Profile level subscriptio
 - [POST transfers#refund](https://docs.wise.com/api-reference/webhook-event/eventtransfersrefund.md): This event provides information about refund amount and currency. Triggered every time a transfer's status becomes `funds_refunded`. * Event type: `transfers#refund` * Profile level subscriptions: Sup
 - [POST transfers#payout-failure](https://docs.wise.com/api-reference/webhook-event/eventtransferspayoutfailure.md): Triggered every time a payout fails. Use this event to get further information about a failed payment. * Event type: `transfers#payout-failure` * Profile level subscriptions: Supported * Application l
 - [POST transfers#state-change](https://docs.wise.com/api-reference/webhook-event/eventtransfersstatechange.md): Triggered every time a transfer's status is updated. * Event type: `transfers#state-change` * Profile level subscriptions: Supported * Application level subscriptions: Supported For topup-to-balance
 - [POST account-details-order#order-state-change](https://docs.wise.com/api-reference/webhook-event/eventaccountdetailsorderstatechange.md): The event contains information about the order state and requirement state. Triggered when there is a change in the state of an account details order. * Event type: `account-details-order#order-state-
 - [POST account-details-payment#state-change](https://docs.wise.com/api-reference/webhook-event/eventaccountdetailspaymentstatechange.md): Triggered every time a pay-in is made into the specified account details. * Event type: `account-details-payment#state-change` * Profile level subscriptions: Supported * Application level subscription
 - [POST allocations#state-changed](https://docs.wise.com/api-reference/webhook-event/eventallocationsstatechanged.md): Triggered when a settlement allocation request changes state. * Event type: `allocations#state-changed` * Profile level subscriptions: Not supported * Application level subscriptions: Supported Event
 - [POST cards#card-status-change](https://docs.wise.com/api-reference/webhook-event/eventcardscardstatuschange.md): This event is triggered for the initial card status as well as any subsequent updates. * Event type: `cards#card-status-change` * Profile level subscriptions: Not Supported * Application level subscri
 - [POST cards#card-production-status-change](https://docs.wise.com/api-reference/webhook-event/eventcardscardproductionstatuschange.md): Triggered every time a card production status is updated. This webhook is solely used for physical cards with `KIOSK_COLLECTION` delivery method. For more details, see the [Card kiosk collection guide
 - [POST cards#3ds-challenge](https://docs.wise.com/api-reference/webhook-event/eventcards3dschallenge.md): Triggered when a customer initiates a push notification for 3DS. The provided information can be used to send a push notification to the customer's mobile app. * Event type: `cards#3ds-challenge` * Pr
 - [POST cards#card-order-status-change](https://docs.wise.com/api-reference/webhook-event/eventcardscardorderstatuschange.md): This event is triggered every time a card order status is updated. Statuses depend on the type of card (virtual/physical). Additional statuses related to delivery exist for physical cards. * Event typ
 - [POST cards#transaction-state-change](https://docs.wise.com/api-reference/webhook-event/eventcardstransactionstatechange.md): Triggered whenever a new card transaction occurs or is modified. * Event type: `cards#transaction-state-change` * Profile level subscriptions: Not Supported * Application level subscriptions: Supporte
 - [POST cards#manual-provisioning-verification](https://docs.wise.com/api-reference/webhook-event/eventcardsmanualprovisioningverification.md): Triggered when a card is manually added to a wallet provider, and the verification methods required to complete the wallet provisioning are returned. * Event type: `cards#manual-provisioning-verificat
 - [POST hold-limit-breach#update](https://docs.wise.com/api-reference/webhook-event/eventholdlimitbreachupdate.md): Triggered whenever a hold limit breach is opened or closed for a profile. A hold limit breach occurs when a balance exceeds the regulatory hold limit (applicable in countries such as Singapore and Mal
 - [POST profiles#cdd-check-state-change](https://docs.wise.com/api-reference/webhook-event/eventprofilescddcheckstatechange.md): This event pushes updates for the [Additional Customer Verification](/guides/product/kyc/partner-kyc/additional-verification) process. * Event type: `profiles#cdd-check-state-change` * Profile level s
 - [POST profiles#overdraft-limit-threshold](https://docs.wise.com/api-reference/webhook-event/eventprofilesoverdraftlimitthreshold.md): Triggered when the overdraft limit usage has reached 70% threshold. The event at each threshold is triggered maximum once per hour. * Event type: `profiles#overdraft-limit-threshold` * Profile level s
 - [POST profiles#state-change](https://docs.wise.com/api-reference/webhook-event/eventprofilesstatechange.md): Triggered every time a profile's state is updated. * Event type: `profiles#state-change` * Profile level subscriptions: Not Supported * Application level subscriptions: Supported Events may not be de
 - [POST profiles#verification-state-change](https://docs.wise.com/api-reference/webhook-event/eventprofilesverificationstatechange.md): Triggered when the verification state of a connected profile changes. A profile's *verification state* can be `verified` or `not_verified`. - If the state is `verified`, then the user is ready to make
 - [POST kyc-reviews#state-change](https://docs.wise.com/api-reference/webhook-event/eventkycreviewsstatechange.md): Triggered when a KYC review state has changed. In previous versions, this event fired only when the overall KYC review state changed. In **v5.0.0**, it fires on every requirement or additional require
 - [POST balances#update](https://docs.wise.com/api-reference/webhook-event/eventbalancesupdate.md): Triggered every time a multi-currency account is credited or debited. * Event type: `balances#update` * Profile level subscriptions: Supported * Application level subscriptions: Supported Events may
 - [POST balances#account-state-change](https://docs.wise.com/api-reference/webhook-event/eventbalancesaccountstatechange.md): Triggered every time a balance account is activated or deactivated. * Event type: `balances#account-state-change` * Profile level subscriptions: Not Supported * Application level subscriptions: Suppor
 - [POST batch-payment-initiations#state-change](https://docs.wise.com/api-reference/webhook-event/eventbatchpaymentinitiationsstatechange.md): Triggered when the payment initiation state of a batch group payment changes. The expected state of a batch payment initiation can be one of: - `NEW` - `PROCESSING` - `COMPLETED` - `FAILED` - `CHARGED
 - [POST partner-support#case-changed](https://docs.wise.com/api-reference/webhook-event/eventpartnersupportcasechanged.md): Triggered every time a case is created or updated, including when a new message is added or the status changes. Note that you will also receive a webhook response when you have updated a case. * Event
 - [POST settlement#funds-received](https://docs.wise.com/api-reference/webhook-event/eventsettlementfundsreceived.md): Triggered when funds are received for settlement. * Event type: `settlement#funds-received` * Profile level subscriptions: Not supported * Application level subscriptions: Supported Events may not be
 - [POST swift-in#credit](https://docs.wise.com/api-reference/webhook-event/eventswiftincredit.md): Triggered every time a SWIFT message is received and a credit is deposited into a balance account. If you also subscribe to `balances#credit` or `transfers#state-change` on the same profile or applica
 - [POST swift#message-received](https://docs.wise.com/api-reference/webhook-event/eventswiftmessagereceived.md): Triggered when a SWIFT message (e.g., [pacs.008](/guides/product/receive-money/incoming-transfer-notifications#example-pacs008-message-content)) is received and processed by Wise on behalf of a partne
 - [POST transaction-disputes#update](https://docs.wise.com/api-reference/webhook-event/eventtransactiondisputesupdate.md): Triggered every time a transaction dispute is submitted or updated. You may receive update events even when there are no apparent changes in the dispute `status` or `subStatus`, as certain underlying
 - [POST bulk-settlement#payment-received](https://docs.wise.com/api-reference/webhook-event/eventbulksettlementpaymentreceived.md): Triggered when a bulk settlement fund is received. Once there is a match, meaning the amount for this settlement journal is fully settled, the `amount_matched` is set to `true`. If it is not matched,
 - [POST incoming-transfer#credited](https://docs.wise.com/api-reference/webhook-event/eventincomingtransfercredited.md): Triggered when an incoming transfer is credited to a Wise balance. This is a thin event, containing just the `incoming_transfer_id`. Fetch the full resource via the [incoming transfer endpoint](/api-r
 - [POST recipients#state-change](https://docs.wise.com/api-reference/webhook-event/eventrecipientsstatechange.md): Triggered when a recipient account created or changed through hosted recipient creation changes state. See the [Embedded Flows guide](/guides/product/embedded-flows/index.md#hosted-recipient-creation-
 - [POST users#state-change](https://docs.wise.com/api-reference/webhook-event/eventusersstatechange.md): Triggered every time a user's state is updated. This webhook is deprecated and will be removed by end 2026. If you are currently subscribed to it, please migrate to the new [profiles#state-change](/ap
## Settlement

 - [POST /settlement/allocations](https://docs.wise.com/api-reference/settlement/createfundsallocationrequest.md): Creates a new settlement allocation request with a Settlement Allocation Request (SAR) file containing payment intents
 - [GET /settlement/allocations/{allocationId}](https://docs.wise.com/api-reference/settlement/getsettlementallocation.md): Retrieves the details of a settlement allocation by its ID. Optionally includes paginated payment intents associated with the allocation.
 - [GET /settlement/allocations/{allocationId}/payment-intents/{paymentIntentId}](https://docs.wise.com/api-reference/settlement/getpaymentintent.md): Retrieves the details of a specific payment intent within a settlement allocation.
 - [POST allocations#state-changed](https://docs.wise.com/api-reference/settlement/eventallocationsstatechanged.md): Triggered when a settlement allocation request changes state. * Event type: `allocations#state-changed` * Profile level subscriptions: Not supported * Application level subscriptions: Supported Event
 - [POST settlement#funds-received](https://docs.wise.com/api-reference/settlement/eventsettlementfundsreceived.md): Triggered when funds are received for settlement. * Event type: `settlement#funds-received` * Profile level subscriptions: Not supported * Application level subscriptions: Supported Events may not be
## Simulations

 - [GET /simulation/transfers/{transferId}/{status}](https://docs.wise.com/api-reference/simulation/simulationtransferstatechange.md): Changes the transfer status to the specified state. The available state transitions are: - `processing` — from `incoming_payment_waiting` - `funds_converted` — from `processing`. Refer to regional gui
 - [POST /simulation/transfers/{transferId}/payout-failure](https://docs.wise.com/api-reference/simulation/simulationtransferpayoutfailure.md): Triggers transfers#payout-failure webhook for the transfer. The available payout failure reason codes are listed in the [transfers#payout-failure webhook guide](/guides/product/send-money/tracking/pay
 - [POST /simulation/transfers/{transferId}/delivery-update](https://docs.wise.com/api-reference/simulation/simulationtransferdeliveryupdate.md): Triggers a synthetic `transfers#delivery-update` webhook for a transfer accessible to the caller. Create an eligible webhook subscription before calling this endpoint. See the [delivery update guide](
 - [POST /simulation/profiles/{profileId}/verifications](https://docs.wise.com/api-reference/simulation/simulationverification.md): Changes a specific profile's verification state to `PASSED`. This is useful for testing the `profiles#verification-state-change` webhook and is a prerequisite for setting up a Multi-Currency Account (
 - [POST /simulation/verify-profile](https://docs.wise.com/api-reference/simulation/simulationverifyprofile.md): Verifies all profiles associated with the authenticated user, changing their verification state to `PASSED`. This is useful for testing the `profiles#verification-state-change` webhook and is a prereq
 - [POST /simulation/balance/topup](https://docs.wise.com/api-reference/simulation/simulationbalancetopup.md): Simulates a top-up so that a balance can be used to fund transfers and/or card spend.
 - [POST /simulation/settlement/funds](https://docs.wise.com/api-reference/simulation/simulatesettlementallocationsfunds.md): Simulates the receipt of funds for a specific settlement allocation. This endpoint allows you to simulate the receipt of funds associated with a given allocation, which can be useful for testi
 - [POST /simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/authorisation](https://docs.wise.com/api-reference/simulation/simulationcardtransactionauthorisation.md): Simulates a card transaction authorisation request in the sandbox environment. It can simulate ATM withdrawals, POS purchases, e-commerce transactions, and refunds. This is an authorisation hold, wher
 - [POST /simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/clearing](https://docs.wise.com/api-reference/simulation/simulationcardtransactionclearing.md): Simulates a transaction clearing request in the sandbox environment. This is done after the authorisation. The `ref` field can be copied from the `reference` object in the authorisation response. To c
 - [POST /simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions/reversal](https://docs.wise.com/api-reference/simulation/simulationcardtransactionreversal.md): Simulates a transaction reversal request in the sandbox environment. The `amount.value` field can be set to 0 for a full reversal, or a positive value that represents the intended final value of the t
 - [GET /simulation/spend/profiles/{profileId}/cards/{cardToken}/transactions](https://docs.wise.com/api-reference/simulation/simulationcardtransactions.md): Returns a list of simulated card transactions, in descending order of creation time. To retrieve more details of a transaction, use the [get card transaction by ID](/api-reference/card-transaction/car
 - [POST /simulation/spend/profiles/{profileId}/cards/{cardToken}/production](https://docs.wise.com/api-reference/simulation/simulationcardproduction.md): Simulates a card production status change in the sandbox environment. Please ensure that you have created a physical card order with KIOSK_COLLECTION delivery method and that you produce the card befo
 - [GET /simulation/profiles/{profileId}/kyc-reviews/{kycReviewId}/requirements](https://docs.wise.com/api-reference/simulation/simulationkycreviewrequirementslist.md): Lists all blocking requirements for a KYC (Know Your Customer) review. These outstanding KYC requirements typically act as "blocking requirements", preventing actions like creating transfers.
 - [POST /simulation/profiles/{profileId}/kyc-reviews/{kycReviewId}/requirements/add](https://docs.wise.com/api-reference/simulation/simulationkycreviewrequirementsadd.md): Creates a new requirement for a KYC (Know Your Customer) review for a business profile. This can only be used for business profiles. It creates a static `BUSINESS_USE_CASE` requirement only.
 - [POST /simulation/profiles/{profileId}/kyc-reviews/{kycReviewId}/requirements/submit](https://docs.wise.com/api-reference/simulation/simulationkycreviewrequirementssubmit.md): Simulates providing everything needed for a particular KYC requirement. This can be used in place of going through a hosted journey on the browser. This functionality only works for the following requ
 - [POST /simulation/profiles/{profileId}/kyc-reviews/{kycReviewId}/verify](https://docs.wise.com/api-reference/simulation/simulationkycreviewverify.md): Verifies requirement(s) on an existing KYC (Know Your Customer) review. Can be used after a user has provided input for a requirement through the hosted journey or simulated the requirement submission
 - [POST /simulation/profiles/{profileId}/bank-transactions/import](https://docs.wise.com/api-reference/simulation/simulationbanktransactionimport.md): Simulates a bank transfer into a profile's account details. This will create a payment into the user's account details and balance for the specified amount and currency. Please refer to the [Bank Acco
 - [POST /simulation/profiles/{profileId}/swift-in](https://docs.wise.com/api-reference/simulation/simulationswiftin.md): Simulates an incoming Swift transfer into a profile's account details. This will create a payment into the user's account details and balance for the specified amount and currency. Using sandbox, you
 - [POST /simulation/sanction-cases](https://docs.wise.com/api-reference/simulation/simulatesanctioncase.md): Simulates the creation or closure of a sanction case for testing partner integrations. When `status` is `OPEN`, a new sanction case is created with the specified type and subtype. When `status` is `CL
## Cases

 - [POST /cases](https://docs.wise.com/api-reference/case/casecreate.md): Cases are used to collect or transmit additional information between Partners and Wise. Use this endpoint to create a new case. Please do not include PII in the `subject` of a case. Any specific detai
 - [GET /cases/{caseId}](https://docs.wise.com/api-reference/case/caseget.md): Retrieves the complete details of a support case including all public messages and reference information. #### Response Returns the full case object with: - Case metadata (id, type, subType, status, t
 - [POST /cases/{caseId}/messages](https://docs.wise.com/api-reference/case/casesubmitmessage.md): See the [Case submission type](/guides/product/partner/submission-types.md) guide for details on each submission type along with an example.
 - [POST partner-support#case-changed](https://docs.wise.com/api-reference/case/eventpartnersupportcasechanged.md): Triggered every time a case is created or updated, including when a new message is added or the status changes. Note that you will also receive a webhook response when you have updated a case. * Event
## Files

 - [POST /cases/files](https://docs.wise.com/api-reference/case-files/casefileupload.md): Uploads a file that can be used as supporting documentation for cases. All files are scanned for malware before being accepted.
## GPI Tracking

 - [POST /gpi-tracking](https://docs.wise.com/api-reference/gpi-tracking/lookupgpitracking.md): Looks up GPI tracking data for a transfer identified by `identifierType` and `identifier`.
