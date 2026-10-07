# Changelog 2023

* Added a new API to allow [listing payment tokens](/api-reference/legacy/digital-wallet/pushprovisioningpaymenttokenslist).


* Added guide on [dispute handling via API](/guides/product/issue-cards/card-disputes-api).


* Added `deliveryEstimate` field to [`Card Order`](/api-reference/legacy/card-order/cardorderget).


* Added a new API to add more [spend-controls](/api-reference/legacy/spend-controls) on your card transactions.


* Added API guide for push provisioning.


* Added an API to get a list of card transactions marked for deprecation.


* Updated [card spend limits](/api-reference/legacy/spend-limits/spendlimitscardget) to support transaction limit.


* Published a new version (v4) of the [`/{{cardToken}}/spend-limits`](/api-reference/legacy/spend-limits/spendlimitscardget) endpoint, which has a new request/response format.


* The `billingAddress` field is now changed to the `address` field. You'll still be able to send `billingAddress` in the [`/card-order`](/api-reference/legacy/card-order/cardordercreate) request, but we recommend switching to `address` as soon as possible. We'll deprecate the `billingAddress` field at a later date.
* Support for BR addresses is now available.


* Added a new API, [`/address/validate`](/api-reference/legacy/card-order/cardordervalidateaddress). If you currently don't retrieve the address via another endpoint, please be sure to validate all addresses with the above endpoint before you send them in the [`/card-order`](/api-reference/legacy/card-order/cardordercreate) request.


* Return all the possible card statuses in both the [`/status`](/api-reference/legacy/card/cardstatusupdate) API and [cards#card-order-status-change](/api-reference/legacy/webhook-event/eventcardscardorderstatuschange) webhook.


* Ordering a physical card over the API is now available.


* Added new fields to the [cards#transaction-state-change](/api-reference/legacy/webhook-event/eventcardstransactionstatechange) webhook.