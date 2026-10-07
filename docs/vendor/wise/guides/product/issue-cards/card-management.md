# Card controls

## Card Status 

A card's state can be changed using the [update card status API](/api-reference/card/cardstatusupdate).

- `ACTIVE` - The card is usable and able to transact. This is the default state.
- `FROZEN` - The card cannot be used. All authorisation requests will be declined. It is possible to move the card back to 'ACTIVE' state.
- `BLOCKED` - The card cannot be used. All authorisation requests will be declined. This state is irreversible and the card will no longer contribute to the limit of cards a profile can have.


It is best practice to advise users to set the card to `FROZEN` if any suspicious activity is noticed or if the user does not intend on using the card for long periods of time.
Setting the status to `BLOCKED` is irreversible, hence it is advisable to use this status if the card is permanently lost, the card sensitive details have been leaked or fraud has been determined on the card.

Wise may also change the status of the card should we suspect fraudulent activity.

We provide a [card status change webhook event](/api-reference/webhook-event/eventcardscardstatuschange) to notify partners of any status changes to a card.

## Spending Permissions 

A card's spending permission can be changed using the [spending permissions API](/api-reference/card/cardpermissionsbulkupdate)

- `ECOM` - Online transactions.
- `POS_CHIP` - Physical point-of-sale transactions requiring the card chip to be inserted in the machine.
- `POS_MAGSTRIPE` - Physical point-of-sale transactions requiring the card to be swiped on the machine. Card order status must be set to `COMPLETED` to enable.
- `POS_CONTACTLESS` - Physical point-of-sale transactions requiring the card to be tapped on the machine. Card order status must be set to `COMPLETED` to enable.
- `ATM_WITHDRAWAL` - Withdrawing money from an ATM machine.
- `MOBILE_WALLETS` - Digital wallet payments such as Apple Pay and Google Pay.


Users may choose to disable permissions for unwanted use cases to prevent possible fraudulent transactions.

## Spending Limits  

To control a user's spending, we have both profile and card level spending limits.
Transactions made beyond the spending limit will be declined.

#### Profile Spending Limits

Profile spend limits are shared by all the cards created by the same profile.
Profile spend limits can be changed using the [update profile limits API](/api-reference/spend-limits/spendlimitsprofileupdate).
It is not possible to remove the profile limits completely or to set the value beyond [the maximum allowed by Wise](https://wise.com/help/articles/2899986/what-are-my-spending-limits).

There are two types of profile spend limits.

- `ATM_WITHDRAWAL` - limit for ATM withdrawals
- `PURCHASE` - combined limit that applies to Contactless, Magnetic, Online purchase, Chip and PIN/mobile wallet transactions.


Profile spend limits may be aggregated with different windows:

- `DAILY` - limit aggregated in a day. Resets each day at midnight
- `MONTHLY` - limit aggregated in a calendar month. Resets on the 1st day of the month.


Reach out to your account manager if you require different profile spending limits.

#### Card Spending Limits

Card spend limits can be changed using the update [card limits API](/api-reference/spend-limits/spendlimitscardupdate).
Setting spend limits for an individual card is optional.

An individual card limit will apply to all transactions including ATM withdrawal.

Card spend limits may be aggregated with different windows:

- `TRANSACTION` - limit per single transaction.
- `DAILY` - limit aggregated in a day. Resets each day at midnight
- `MONTHLY` - limit aggregated in a calendar month. Resets on the 1st day of the month.
- `LIFETIME` - limit aggregated from the creation of the card. Does not reset. It is also possible to set the lifetime limit at [card order creation](/api-reference/card-order/cardordercreate)