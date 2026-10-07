# Changelog 2025

## November 2025

* Updated all sandbox URLs to point to the new sandbox environment.


* Added `creationTime` and `modificationTime` fields in [Payment Token list](/api-reference/legacy/digital-wallet/pushprovisioningpaymenttokenslist).


* Added missing fields in [Payin Deposit details](/api-reference/legacy/payin-deposit-detail/payindepositdetailget).


## October 2025

* Updating the description of the [Open Banking Transactions endpoint](/guides/developer/open-banking).
* Add details for submitting Account Intent Kyc Requirement [KYC Requirement Submit](/api-reference/legacy/kyc-review/kycreviewrequirementsubmit)


* Add new webhook event type `transfers#transfer-suspension`.


* Add [new strong customer authentication endpoints](/api-reference/legacy/sca-ott).
* Deprecated [SCA enrolment factors endpoints](/api-reference/legacy/user-security).
* Deprecated [SCA verification endpoints](/api-reference/legacy/sca-ott).


* Update [recipient confirmation API guide](/guides/product/send-money/recipients#confirmations-contract).


## September 2025

* Add new simulation endpoint to simulate [verify profile by id](/api-reference/legacy/simulation/simulationverification).


* Add new simulation endpoint to simulate [bank transaction import](/api-reference/legacy/simulation/simulationbanktransactionimport).


* Add `originatorLegalEntityType` field for transfer-requirements to include sender type [transfer-requirements](/api-reference/legacy/transfer/transferrequirementsvalidate).
* Updated the [Transfer resource](/api-reference/legacy/transfer) documentation, to include the `payinSessionId` field


* Update documentation for OpenBanking from v3.1 to v3.1.11 [OpenBanking](/guides/developer/open-banking).


## August 2025

* Add `replacementDetails` field in [Card Order creation](/api-reference/legacy/card-order/cardordercreate).


* Add `cardHolderProfileId` field in [Card Order creation](/api-reference/legacy/card-order/cardordercreate).


* Updated [Card Issuance guide](/guides/product/issue-cards) to reflect changes in card activation.
* Deprecated [complete card order](/api-reference/legacy/card-order/cardorderstatusupdate).
* Deprecated `unlockSpendingPermissions` in [Card resource](/api-reference/legacy/card).


## July 2025

* Restructured the hosted KYC guide with clearer content organization.
* Updated [Hosted KYC guide](/guides/product/kyc/wise-kyc/hosted-kyc) to include Proactive trigger.


* Add new [List KYC Review Items](/api-reference/legacy/simulation/simulationkycreviewrequirementslist) endpoint reference documentation.
* Add new [Simulate KYC Review Add requirement](/api-reference/legacy/simulation/simulationkycreviewrequirementsadd) endpoint reference documentation.
* Add new [Simulate KYC Review Submit requirement](/api-reference/legacy/simulation/simulationkycreviewrequirementssubmit) endpoint reference documentation.
* Add new [Simulate KYC Review Verify requirements](/api-reference/legacy/simulation/simulationkycreviewverify) endpoint reference documentation.


* Updated [Get Delivery Estimate](/api-reference/legacy/delivery-estimate/deliveryestimateget) to include the new `formattedEstimatedDeliveryDate` field


* Updated [Card Transactions Decline Reasons](/api-reference/legacy/card-transaction#card-transaction-decline-reasons) to include new decline reason codes


* Updated [Simulate Top-Up](/api-reference/legacy/simulation/simulationbalancetopup) to include new field (`Channel`) in request body.


* Updating [verification-documents](/api-reference/legacy/profile/profileverificationdocumentcreate) to state the characters limitation in the unique identifier field.


## June 2025

* Updating [Language Support](/guides/developer/language-support) with Danish, Norwegian and Swedish
* Add new [payment-returns](/guides/product/receive-money/initiate-a-return) guide.


## May 2025

* Updating the [swift-in#credit webhook](/api-reference/legacy/webhook-event/eventswiftincredit) supported subscriptions


* Updating the regions where `occupations` is required in [Create or update an address](/api-reference/legacy/address#create) and [Create a Personal Profile](/api-reference/legacy/profile/profilepersonalcreate)


* Add new [Create Business Profile V3 (beta)](/api-reference/legacy/profile/profilebusinesscreate) endpoint reference documentation.
* Add new [Get Business Representative API](/api-reference/legacy/profile/profilebusinessrepresentativeget) endpoint reference documentation.
* Add new [Transfer Business Representative API](/api-reference/legacy/profile/profilebusinessrepresentativeupdate) endpoint reference documentation.
* Add new [Update Business Representative API](/api-reference/legacy/profile/profilebusinessrepresentativeupdate) endpoint reference documentation.


* Updating hosted KYC webhook trigger references information with card, proactive and bank details information


* Merchant name and location added to the [card transaction state change webhook](/api-reference/legacy/webhook-event/eventcardstransactionstatechange)


## April 2025

* Adding new endpoint for US combined receipt for partners servicing US retail consumers (instead of existing receipt endpoint) which is a regulatory requirement.


* Add new [Create SCA session](/api-reference/legacy/sca-sessions/scasessioncreate) endpoint reference documentation.
* Updated [SCA over API](/guides/developer/auth-and-security/sca-over-api) guide


* Updated [swift-in test message](/guides/product/receive-money/test-and-go-live) in sandbox to accept more custom fields


* Updated [Refund Recipient](/api-reference/legacy/recipient/recipientcreate) endpoint reference documentation and sample


* Added new expiration related fields to [OAuth Token](/api-reference/legacy/oauth-token/oauthtokencreate)


* Updated [dispute sub status and transition diagram](/api-reference/legacy/disputes#dispute-sub-status)


## March 2025

* The [v3 upload dispute file](/api-reference/legacy/disputes/disputefileuploadv3) endpoint will be deprecated in favor of [v4 upload dispute file](/api-reference/legacy/disputes/disputefileupload) endpoint that does not require additional permission setup for the endpoint to be accessible.
* The `billingAddress` field is now changed to the `address` field. You'll still be able to send `billingAddress` in the [`/card-order`](/api-reference/legacy/card-order/cardordercreate) request, but we recommend switching to `address` as soon as possible. We'll deprecate the `billingAddress` field at a later date.


* Added guide on [card kiosk collection](/guides/product/issue-cards/card-kiosk-collection#card-kiosk-collection)
* Added a new section for card kiosk collection [APIs](/api-reference/legacy/card-kiosk-collection)
* Added [card production simulation endpoint](/api-reference/legacy/simulation/simulationcardproduction) to simulate different card production statuses
* Added [card production status change](/api-reference/legacy/webhook-event/eventcardscardproductionstatuschange) webhook


* Move '#update-phone-number' of 'card' to 'deprecated-api'
* Updated the field description of `phone-number` in the [card object](/api-reference/legacy/card-order/cardordercreate) to indicate that it is deprecated and refer them to profile endpoints.


* Renamed `triggerReference` field in [KYC Review](/api-reference/legacy/kyc-review/) to
`triggerReferences`. Updated the field
in [KYC Review webhook](/api-reference/legacy/webhook-event/eventkycreviewsstatechange)
accordingly.


* Removed `/features` page. Migrated content into [api-reference](/api-reference/legacy) pages.


* Added new `includeWise` parameter to [comparison v4](/api-reference/legacy/comparison/comparisonget)


* Remove `purge_timestamp` from [cards#transaction-state-change](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) webhook. Please use `data.purge_time` instead


* Added Business profile creation step to [Hosted KYC guide](/guides/product/kyc/wise-kyc/hosted-kyc#hosted-kyc-flow)


* Added new [Strongly Authenticated Session Section](/guides/developer/auth-and-security/sca-over-api#sca-session).


* Deprecate `purge_timestamp` and add `purge_time` in the [cards#transaction-state-change](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) webhook.


* Added a new `unlockSpendingPermissions` field to the [card object](/api-reference/legacy/card).
* Added new fields `pin_validation_result`, `approval_code` and `purge_timestamp` to the [cards#transaction-state-change](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) webhook.
* Updated the guide for partner control to enable contactless and magstripe card payments, detailing suggested methods of checking that the end user has received their card.
* Updated the API for [update card order status](/api-reference/legacy/card-order/cardorderstatusupdate).


* Updated the [Quote API Reference](/api-reference/legacy/quote) - Corrected the price explanation id by adding plainText, so it reads `option.price.items[n].explanation.plainText`


## February 2025

* Added `accountDetails` field to [Partner License Transfer](/api-reference/legacy/transfer/transferpartnerlicencecreate).


* Updated [Upload Document](/api-reference/legacy/verification#upload-document) endpoint by adding `BUSINESS_AUTH_REP_PROOF_BY_AUTH_LETTER` to the list of allowed values for `documentType` field.


* Updated acceptable list of transfer funding types for [`Fund a Transfer`](/api-reference/legacy/transfer/transferfund) endpoint.


* Moved information about duplicate account handling from the reference to the appropriate integration guides.
* Added the mTLS API endpoints into the [Environment](/guides/developer/environments) section.
* Updated the [Updating Profiles](/guides/product/kyc/partner-kyc/updating-profiles) guide to more clearly describe how to handle profiles that are due annual review but no updates are required.


* Added the optional `externalCustomerId` field to [Personal](/api-reference/legacy/profile/profilepersonalcreate) and [Business](/api-reference/legacy/profile/profilebusinesscreate) profile creation. This allows integrators to map a profile entity to a customer in their own system.


* Added `accountDetails` field to [Third Party Transfer](/api-reference/legacy/third-party-transfer/createthirdpartytransfer).


* Updated the [comparison docs](/api-reference/legacy/comparison) with a new response field `isConsideredMidMarketRate` to show whether a provider's rate can be classified as the mid-market rate or not.


* Added a new `currentState` field to the [Profile](/api-reference/legacy/profile/profile) object resource.


## January 2025

* Updated the [comparison docs](/api-reference/legacy/comparison) with the new `/v4/comparisons` endpoint.


* Published a new version (v5) of the [Upload Evidences](/api-reference/legacy/verification#upload-evidences) endpoint.


* The personal token SCA documentation is no longer publicly available. Partners need to contact their CSM if they are still require access to this guide.


* Added `changed_by` to the [cards#card-status-change](/api-reference/legacy/webhook-event/eventcardscardstatuschange) webhook.