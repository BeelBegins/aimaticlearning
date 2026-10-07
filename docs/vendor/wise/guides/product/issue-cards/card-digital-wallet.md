# Digital wallets

## Manual Provisioning 

Users can manually add their virtual and physical cards to their preferred wallet provider such as Google Pay, Apple Pay, or Samsung Pay.

To do this, they need to enter their card details, update their address, and accept the issuer’s terms and conditions.

Afterward, step-up verification methods are presented for users to authorise the provisioning operation.

### SMS

For partners onboarded after 1/3/2025, we will use the registered phone number from the profile, which we will obtain through the [create profile endpoint](/api-reference/profile/profilepersonalcreate) or [update profile endpoint](/api-reference/profile/profilepersonalupdate).

For partners onboarded before 1/3/2025, the phone number on the [card](/api-reference/card) will be used until you have been moved over to use the profile phone number by our support team

### In-app verification

This verification method is more secured and should be used for manual provisioning.

Subscribe to [cards#manual-provisioning-verification](/api-reference/webhook-event/eventcardsmanualprovisioningverification).
An event is triggered when a user reaches the verification methods step, regardless of the verification method selected.

The event contains information about the card to be provisioned, such as the last four digits, the provisioning request time, the wallet provider and the payment token unique reference. This information can be displayed within your mobile application to help the user decide which card is being provisioned.

To capture the user’s decision, we provide a [payment token activation endpoint](/api-reference/digital-wallet/digitalwalletactivatepaymenttoken). This endpoint allows you to `APPROVE` or `DECLINE` a payment token activation.
Upon successful approval, the payment token will be added to the wallet. If the activation is declined, the provisioning attempt will be discarded from the wallet and the user will need to restart the provisioning process from the beginning.

## Push Provisioning 

Push provisioning allows your cardholders to add their virtual and physical cards to their digital wallets by using your app.
The process allows customers to avoid entering their card data and allows to skip additional verification steps.

Wise offers [APIs](/api-reference/digital-wallet) that allow partners to implement push provisioning within their own mobile apps.

Reach out to your implementation manager for more details