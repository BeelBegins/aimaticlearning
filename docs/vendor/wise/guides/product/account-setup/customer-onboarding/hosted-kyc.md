# Hosted customer onboarding

With Wise-hosted customer onboarding, you direct your customers to a Wise-hosted page branded with your logo and theme colors to collect the required KYC/B data.

With this method, you don't need to build the verification screens yourself, as Wise manages the forms and handles the collection of all data requirements.

## Hosted flow summary

Once initiated, hosted customer onboarding follows this path:

1. You receive a KYC review state change event indicating data is needed for the customer to proceed (requires subscribing to an application webhook).
2. You fetch a single-use link which you use to direct the customer to your branded and Wise-hosted onboarding page.
3. Your customer completes the onboarding tasks presented to them.
4. Wise redirects your customer back to your application, indicates if your customer successfully completed the onboarding flow, and sends a KYC review state change event.
5. Wise reviews the customer-provided information and sends a KYC review state change event to indicate the customer has passed or more input is required.


## Hosted onboarding process

Once you have [subscribed to the KYC state change webhook](/guides/product/account-setup/customer-onboarding/kyc-statechange-webhook), you can then initiate onboarding for customer profiles that require it.

### Proactive KYC

To perform **proactive KYC**, send a [create KYC review request](/api-reference/kyc-review/kycreviewcreate) before attempting to submit the customer's first transfer.

In the request body, set the `triggerReferences.​type` field to `PROACTIVE_SEND_MONEY`.

Note that if the KYC review is not requested proactively, the first request to create a transfer automatically creates a KYC review resource.

The rest of the process is the same whether doing proactive KYC or initiating on the customer’s first transfer.

### Step 1: Check KYC review status

Check the `data.resource.state` field of the KYC review state change event payload.

When the status is `WAITING_CUSTOMER_INPUT`, you can then fetch the hosted onboarding link.

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
      "triggerReferences": [ … ],
      "requirements": [ … ],
      "requirementChanges": [ … ]
    }
  }
}
```

### Step 2: Fetch hosted onboarding link

Request the link for the hosted onboarding flow using the [update KYC review to get a hosted KYC link endpoint](/api-reference/kyc-review/kycreviewredirecturlupdate).

Sample request
- Use the `data.resource.id` value received in the state change event payload as the `{kycReviewId}` path parameter.
- The `redirectUrl` in the request body is the URL your customer should be redirected to once completing the onboarding flow.


```bash
  curl -L -X PATCH \
  'https://api.wise.com/{version}/profiles/{profileId}/kyc-reviews/{kycReviewId}' \
   -H 'Content-Type: application/json' \
   -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
   -d '{
        "redirectUrl": "https://example.com"
       }'
```

Sample response
The response provides a short-lived, single-use link to direct the customer to your branded and Wise-hosted onboarding page. The link currently **expires after 5 minutes** and can only be used once. Use the `expiresAt` field from the response as the source of truth for the exact expiry time.

```json
{
 "id": "46e1a5c4-4a9b-4563-39d3-18174d3ac0f8",
 "status": "WAITING_CUSTOMER_INPUT",
 "link": {
   "value": "https://wise-sandbox.com/embedded-flows/verification?token=d7332edb-25bf-41af-a4e9-09f5efe39ded&checkId=3120073",
   "expiresAt": "2024-09-03T16:29:41.203225146"
 },
"createdAt": "2024-09-03T16:22:02.257725",
"updatedAt": "2024-09-03T16:29:41.147522",
"requiredBy": "2024-09-03T16:22:02.257725",
"triggerReferences": [ … ],
"redirectUrl": "https://example.com",
"requirements": [ … ]
}
```

If the link expires or has already been used, you must fetch a new link before redirecting the customer. To get a new link, make another request to the [Update KYC review](/api-reference/kyc-review#update-redirect-url) endpoint.

### Step 3: Direct customer to the hosted page

Direct your customer to the URL received in the `link.value` field of the response. How you implement this depends on the platform your customer is using:

* **Web**: Open the link in a new browser tab or redirect the customer to the link.
* **Android**: Embed the page within your app using [Custom Tabs](https://developer.chrome.com/docs/android/custom-tabs).
* **iOS**: Embed the page within your app using [Safari View Controller](https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller).


The hosted page guides the customer through multiple forms to gather the required details. Customers may be asked to perform “liveness checks” and upload documents, like images of government-issued IDs.

Requirements vary!
The exact requirements for a specific customer will vary based on multiple factors, including the customer type and country of residence. If onboarding is initiated on the customer’s first transfer action, other factors like source currency, target currency, and transfer amount can also impact requirements.

Once the customer provides all necessary information, Wise redirects them back to your application using the `redirectUrl` you provided.

### Step 4: Completing hosted onboarding

Upon redirecting the customer back to your application, Wise appends a query parameter to the URL to indicate success:

- `status=success`: The data submission has been completed successfully.
- `status=error`: The data submission failed. While this is a rare occurrence, the URL query parameter lets you track which customers did not complete their onboarding steps. Should this occur, contact Wise for assistance.


If all requirements have been submitted successfully, you also receive a KYC review status change event with the status `PROCESSING`. Wise then reviews the submission.

### Step 5: Monitor review state change events

Wise reviews the information provided by the customer and determines if the information is sufficient to pass the KYC review, or if we require more information.

#### Information accepted

If the customer's information is accepted, you receive a state change event with a `PASSED` KYC review state. The customer's profile is then allowed to perform transactions, like transferring money, via the Wise Platform API.

**Sample payload**:

```json
{
  "schema_version": "5.0.0",
  "subscription_id": "8df95817-8085-40aa-9bda-e3bf46e7a21a",
  "event_type": "kyc-reviews#state-change",
  "sent_at": "2026-09-03T16:35:42.123Z",
  "data": {
    "resource": {
      "id": "46e1a5c4-4a9b-4563-39d3-18174d3ac0f8",
      "state": "PASSED",
      "prevState": "PROCESSING",
      "profileId": 22016766,
      "createdAt": "2026-09-03T16:22:02.258Z",
      "updatedAt": "2026-09-03T16:35:41.148Z",
      "triggerReferences": [
        {
          "type": "QUOTE",
          "triggerData": {
            "id": "ba83s43a-f623-46f0-956d-196c13e2ab01"
          }
        }
      ],
      "requirements": [
        [
          {
            "key": "ID_DOCUMENT",
            "state": "VERIFIED",
            "apiCollectionSupported": true,
            "additionalRequirements": [],
            "versions": [
              {
                "version": "V1"
              }
            ],
            "attributes": {}
          }
        ]
      ],
      "requirementChanges": [
        {
          "key": "ID_DOCUMENT",
          "newState": "VERIFIED",
          "prevState": "IN_REVIEW",
          "additionalRequirements": []
        }
      ]
    }
  }
}
```

#### More information required

If we require more information from the customer, you receive a state change event with a `WAITING_CUSTOMER_INPUT` KYC review state.

Outstanding or rejected requirements have a state of `NOT_PROVIDED`. If a requirement is rejected, its object includes a `reasons` object with a description.

Direct the customer back to the hosted onboarding flow, with a new redirect link, so they can resubmit or provide the additional information (the hosted flow surfaces the reason to the customer so they understand what happened and what they need to do to submit successfully).

**Sample payload**:

```json
{
  "schema_version": "5.0.0",
  "subscription_id": "8df95817-8085-40aa-9bda-e3bf46e7a21a",
  "event_type": "kyc-reviews#state-change",
  "sent_at": "2024-09-03T16:29:42.123Z",
  "data": {
    "resource": {
      "id": "46e1a5c4-4a9b-4563-39d3-18174d3ac0f8",
      "state": "WAITING_CUSTOMER_INPUT",
      "prevState": "WAITING_CUSTOMER_INPUT",
      "profileId": 22016766,
      "requiredBy": "2024-09-03T16:22:02.258Z",
      "createdAt": "2024-09-03T16:22:02.258Z",
      "updatedAt": "2024-09-03T16:29:41.148Z",
      "triggerReferences": [
        {
          "type": "QUOTE",
          "triggerData": {
            "id": "ba83s43a-f623-46f0-956d-196c13e2ab01"
          }
        }
      ],
      "requirements": [
        [
          {
            "key": "ID_DOCUMENT",
            "state": "NOT_PROVIDED",
            "apiCollectionSupported": true,
            "additionalRequirements": [
              {
                "reasons": {},
                "attributes": {}
              }
            ],
            "versions": [
              {}
            ]
          }
        ]
      ],
      "requirementChanges": [
        {
          "key": "ID_DOCUMENT",
          "newState": "IN_REVIEW",
          "prevState": "NOT_PROVIDED",
          "additionalRequirements": [
            {
              "additionalRequirementId": "8b789c45-60ae-475d-b667-c8714db9a6a4",
              "newState": "IN_REVIEW",
              "prevState": "NOT_PROVIDED"
            }
          ]
        }
      ]
    }
  }
}
```