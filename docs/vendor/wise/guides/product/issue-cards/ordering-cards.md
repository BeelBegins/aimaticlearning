# Ordering cards

How to order cards for your customers.

This guide will teach you how to create and issue a new card for an account-owner. The card is associated to the account and all transactions will be reflected on the account's balance.

## Card eligibility

After [creating a profile](/api-reference/profile/profilepersonalcreate), cards can now be ordered.

The first step is to [retrieve the available card programs](/api-reference/card-order/cardorderprogramsget). A card program gives information on the type of card, the network that the card is on, as well as the default currency of the card.

If there are no card programs returned in the API call, it means that the profile cannot order any additional cards.

#### Type of card

- `Virtual`: No physical card will be printed. This card can be used for online transactions and added to digital wallets.
- `Physical`: A physical card will be printed. On top of virtual card capabilities, physical cards can also be used at physical terminals and ATMs.


## Ordering a card 

After retrieving the card program, use the [card order API](/api-reference/card-order/cardordercreate) to create a card order.

An address is required for physical cards. For virtual cards, the address is optional (the profile address is used as a fallback). In both cases, the address is used for AVS (address verification service) checks for transactions without a card present. When providing an address, it is also best practice to use the [card address validation API](/api-reference/card-order/cardordervalidateaddress) to ensure the formatting of the address is correct.

When the status of the [card order](/api-reference/card-order/cardorderget) is `CARD_DETAILS_CREATED`, a [card](/api-reference/card) will now be available to be [retrieved](/guides/product/issue-cards/card-management#list).

The [card token](/api-reference/card) is the unique identifier for this card.

For physical card orders, it is recommended to subscribe to the [card order status change webhook event](/api-reference/webhook-event/eventcardscardorderstatuschange) to be notified of card order status changes.

You can cancel a card order by [updating the card order status](/api-reference/card-order/cardorderstatusupdate) to `CANCELLED` with a reason. This can only be done when the card order is still in the `PLACED` status.

Card order status transitions
Create card order statuses transition diagram
#### Card order limits

In order to control the number of cards a profile can create, we have card order limits in place.

On production, the number of card orders is limited to 1 active physical card and 3 active virtual cards per personal profile.
On sandbox, we allow up to 10 physical cards and 30 virtual cards for testing. Additionally, no more than 3 virtual cards can be ordered per day. This limit includes existing cards and card orders.

Reach out to your account manager if you require a higher limit on cards per user.

## Sensitive card details  

Retrieving the sensitive card details (PAN, PIN, CVV) of a card requires us to do so in a PCI-DSS compliant way. Follow our [sensitive card details guide](/guides/product/issue-cards/sensitive-card-details) on how to do so.

To retrieve sensitive card details, the card must be in either `ACTIVE` or `FROZEN` status. A `403` response is returned when getting sensitive card details for a card in any other status.

#### Card PIN

Some card terminals and ATMs require users to enter their card PIN to authenticate transactions.

By default, both physical and virtual card PINs are randomly set.

Optionally, we offer a feature to pre-set the PIN of the card during the card order process. Reach out to your account manager for this feature as Wise will first need to configure this on our side.

## Activate a card  

Virtual cards are activated upon issuance so no action is required from the end user, and the card order status moves to `COMPLETED` automatically.

For physical cards, to mitigate the possibility of fraudulent transactions on the card in the event of misdelivery, users need to activate their card before they can use it for certain transactions.

We offer two activation methods for physical cards: **Chip and PIN** or **Partner Control**.

The activation method for a physical card is determined by the `unlockSpendingPermissions` field in the [Card resource](/api-reference/card).

- A card with **Chip and PIN** activation has `unlockSpendingPermissions` as `WITH_FIRST_CHIP_AND_PIN_TRANSACTION`.
- A card with **Partner Control** activation has `unlockSpendingPermissions` as `WITH_PARTNER_API`.


For Chip and PIN activation, contactless and magnetic stripe transactions attempted prior to the first successful Chip and PIN transaction will be declined. *This activation method has been deprecated.*

For Partner Control activation, all transactions will be declined until the card status has been set to `ACTIVE`.

### Activate a physical card using Partner Control

There are two steps to activating a physical card using Partner Control.

#### Step 1: Set the card status to ACTIVE

Before the card can be used, it must be activated by updating the card status to `ACTIVE`.

Physical [Cards](/api-reference/card) are issued with an `INACTIVE` status, which means they cannot be used to perform any transactions until this is updated.

#### Step 2: Update the card spending permissions

Cards issued with Partner Control activation have all [spending permissions](/api-reference/card) disabled and unlocked. The card [spending permissions](/api-reference/card) must be set to determine which payment methods can be used with it.

Until the spending permission has been enabled for a permission type, all card transactions for the permission type will be declined even if the card status is set to `ACTIVE`. Make sure the spending permission for each transaction type is enabled before allowing users to use the physical card. This can be done using the [update spending permissions API](/api-reference/card/cardpermissionsbulkupdate) to update these permissions in bulk.

Activating a physical card moves the card order status to `COMPLETED`. Ensure that the card order has reached the `PRODUCED` status using the [card order status change webhook](/api-reference/webhook-event/eventcardscardorderstatuschange) before allowing activation. The `PRODUCED` status indicates that the card order has been produced and picked up by our delivery vendors to be dispatched to the cardholder.

It is recommended to have confirmation from the cardholder that they have received their physical card before updating the card status to `ACTIVE`. This can be done by requiring the cardholder to key in the last 4 digits of their physical card upon receiving it. This can be validated against the `lastFourDigits` in the [Card resource](/api-reference/card). To implement this, you should ensure that card details, such as the PAN (Primary Account Number), are initially hidden from the end customer.

### Activate a physical card using Chip and PIN (deprecated)

Physical [cards](/api-reference/card) issued with an `ACTIVE` card status require the cardholder to make a Chip and PIN transaction (inserting the card into the terminal and keying in the card PIN) to start using the card for contactless and magnetic stripe transactions.

Before the first Chip and PIN transaction, all [spending permissions](/api-reference/card) are enabled except `POS_CONTACTLESS` and `POS_MAGSTRIPE`, which are locked. At this point, the card is already `ACTIVE` and can be used for certain transactions.

After the first Chip and PIN transaction has been successfully performed, `POS_CONTACTLESS` and `POS_MAGSTRIPE` permissions are enabled, with no change to other permissions. The card order status is moved to `COMPLETED`.

## Replace a card  

You can replace a card if it is expiring, or if it has been damaged (for physical cards). To do so, create a new [card order](/api-reference/card-order/cardordercreate) with the `replacementDetails` object in the payload, specifying the `cardToken` of the card to replace and the `reason` for replacement: `CARD_EXPIRING` or `CARD_DAMAGED`.

The existing card remains usable until the replacement card is activated. Once the replacement card has been activated, the existing card is automatically blocked.

#### Sensitive card details of replacement card

All sensitive card details will change on the replacement card, including the PAN, CVV2, and expiry date. The card token will also be a new one as each token is uniquely tied to a single card.

- If pre-set PIN is included in your integration, the replacement card order will require the PIN to be pre-set as part of the [card order requirements](/api-reference/card-order/cardorderrequirementsget). This can be a different PIN from the existing card.
- If pre-set PIN is not included in your integration, the PIN will be automatically regenerated for the replacement card order.


#### Payment token replacement

If the existing card was tokenised, the new payment token for the replacement card will be automatically updated in each wallet provider upon activation of the replacement card. No action is required from the cardholder, and they can continue using their tokenised card as usual.

- Physical cards: the payment token is updated when the replacement card is activated.
- Virtual cards: the payment token is updated immediately upon issuance of the replacement card.