# 3D Secure Authentication

3D Secure (3DS) authentication adds an extra layer of protection to online shopping, all Wise issued cards have 3DS enabled by default.

This process can be entirely managed by Wise and requiring no implementation from your side. When 3DS authentication is triggered,
Wise sends a one-time password (OTP) to the customer's registered phone number through SMS or voice call.
The authentication is completed only after the customer submits the OTP within the specified time frame.

For partners onboarded after 1/3/2025, we will use the registered phone number from the profile, which we will obtained through the [create profile endpoint](/api-reference/profile/profilepersonalcreate) or [update profile endpoint](/api-reference/profile/profilepersonalupdate).
For existing and new partners our support team will need to whitelist your clientId for us to start using the registered phone number from the profile.

As part of regulators' anti-scam measures, SMS will no longer be supported as a verification method in some regions. We recommend integrating with the in-app verification flow described below. Please contact your implementation manager for more details.

We also offer an additional authentication flow by sending a push notification to the customer’s mobile app. For this flow, you need to subscribe
to the [webhook event](/api-reference/webhook-event/eventcards3dschallenge) and send a push notification using the transaction
information provided in the event. Once the customer has approved or rejected the transaction,
you must inform us of the result by calling this [API](/guides/product/issue-cards/3ds#inform-challenge-result).

The diagram below illustrates how push notifications works. If the customer falls back to use OTP as the challenge method,
everything will continue to be managed by Wise.

3DS push notification flow
## Inform Challenge Result

Once the customer has approved or rejected the 3DS challenge, you must notify Wise of the result. Use this endpoint to submit the outcome before the expiration time.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/spend/profiles/{profileId}/3dsecure/challenge-result' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "transactionReference": "148579538",
    "challengeStatus": "APPROVED"
  }'
```

For more details on the request, see the [3D Secure API Reference](/api-reference/3ds).