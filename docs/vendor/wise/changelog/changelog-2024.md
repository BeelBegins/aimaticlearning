# Changelog 2024

## December 2024

* Updated the International Receive webhook subscription guide
* Removed the V2.0.0 `swift-in-credit` webhook because it's no longer used.


* Added a new endpoint to get a [Third Party Transfer](/api-reference/legacy/third-party-transfer/getthirdpartytransfer) by ID.


* Added a new V2 endpoint to [update business profiles](/api-reference/legacy/profile/profilebusinessupdate).
* Added a new version V3.0.0 of the [bulk settlement payment received](/api-reference/legacy/webhook-event/eventbulksettlementpaymentreceived) webhook.


* Added a new V2 endpoint to [update personal profiles](/api-reference/legacy/profile/profilepersonalupdate).


* Added a new `balance_movements` field to the [cards#transaction-state-change](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) webhook.


## November 2024

* Added an update card order resource to add [Delivery Option](/api-reference/legacy/card-order).


* Added new guide for [3D Secure authentication](/guides/product/issue-cards/3ds).


* Updated the [Card Issuance guides](/guides/product/issue-cards) with partner control information to set a card order as `COMPLETED`.
* Updated the cancel card order endpoint to an [update card order status endpoint](/api-reference/legacy/card-order/cardorderstatusupdate) (a new `COMPLETED` status can be set for certain integrations).
* Updated the [permissions resource](/api-reference/legacy/card-transaction#permissions) to include the `isLocked` field.
* Added a transaction decline reason `ATM_PIN_CHANGE_NOT_ALLOWED`.


* Updated the [Card Issuance guides](/guides/product/issue-cards).


* Added a new API to allow the [cancellation of a card order](/api-reference/legacy/card-order/cardorderstatusupdate).


## August 2025

* Updated the APIs for [card transaction simulations](/api-reference/legacy/simulation/simulationcardtransactionauthorisation) (authorisation including refund, reversal, and clearing).


## July 2025

* Added a new `credit` field to the [cards#transaction-state-change](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) webhook.
* Added a new `credit` field to the [`card transaction resource`](/api-reference/legacy/card-transaction#object).


## May 2025

* Added new fields to the [cards#transaction-state-change](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) webhook.


* Added a new webhook event to allow [subscribing to dispute updates](/api-reference/legacy/webhook-event/eventtransactiondisputesupdate).


## March 2025

* Added new APIs to allow [managing disputes](/api-reference/legacy/disputes/disputelist).


* Exposed [delivery tracking details](/api-reference/legacy/card-order/cardorderget#delivery-details) if available.


## February 2025

* Added a new API to allow [deleting card spend limits](/api-reference/legacy/spend-limits/spendlimitscarddelete).


* Added explanation for [dispute handling via API reasons](/guides/product/issue-cards/card-disputes-api).


## January 2025

* Added explanation for [card transaction decline reason](/api-reference/legacy/card-transaction#card-transaction-decline-reasons).