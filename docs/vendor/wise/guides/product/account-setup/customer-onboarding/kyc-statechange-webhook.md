# KYC state change webhook

Before initiating onboarding for any of your customers, you must [create an application webhook subscription](/api-reference/webhook/webhookapplicationsubscriptioncreate) for the `kyc-reviews#state-change` event type.

The state change event notification tells your system when a customer must go through the onboarding process, what data is required, and when the customer has passed the review.

## Create webhook subscription

In the subscription request body, set the `trigger_on` value to `kyc-reviews#state-change`.

```bash
curl -i -X POST \
  'https://api.wise.com/2026Q3/applications/{clientKey}/subscriptions' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "name": "KYC - verification status check",
    "trigger_on": "kyc-reviews#state-change",
    "delivery": {
      "version": "5.0.0",
      "url": "https://your.webhook.url/12345"
    }
  }'
```

## Event payload example

Your system will then receive event notifications when the KYC review state changes for any of your customers’ profiles as well as when a requirement changes.

```json
{
  "schema_version": "5.0.0",
  "subscription_id": "8df95817-8085-40aa-9bda-e3bf46e7a21a",
  "event_type": "kyc-reviews#state-change",
  "sent_at": "2026-09-03T16:29:42.123Z",
  "data": {
    "resource": {
      "id": "46e1a5c4-4a9b-4563-39d3-18174d3ac0f8",
      "state": "WAITING_CUSTOMER_INPUT",
      "prevState": "WAITING_CUSTOMER_INPUT",
      "profileId": 22016766,
      "requiredBy": "2026-09-03T16:22:02.258Z",
      "createdAt": "2026-09-03T16:22:02.258Z",
      "updatedAt": "2026-09-03T16:29:41.148Z",
      "triggerReferences": [...],
      "requirements": [
        [
          {
            "key": "ID_DOCUMENT",
            "state": "NOT_PROVIDED",
            "apiCollectionSupported": true,
            "additionalRequirements": [...],
            "versions": [...],
            "attributes": {}
          }
        ]
      ],
      "requirementChanges": [...]
    }
  }
}
```

When the KYC review status is `WAITING_CUSTOMER_INPUT`, KYC data is required for the customer identified in the `profileId` field. When the status is `PASSED`, no further customer action is required.

For the full event payload schema, see [KYC review state change event type](/api-reference/webhook-event/eventkycreviewsstatechange).