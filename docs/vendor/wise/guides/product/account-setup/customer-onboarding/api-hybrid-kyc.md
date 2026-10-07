# API and hybrid customer onboarding

With customer onboarding via API, you build your desired customer data collection experience directly into your application. Once you have collected all required data, you submit it to Wise via API.

The hybrid approach combines these steps with Wise-hosted flows to handle requirements that cannot be collected via API or may change over time. This ensures all required information can be collected without blocking your customers. Most integrations use the hybrid approach to ensure complete coverage of KYC requirements.

## API flow summary

Once initiated, API customer onboarding follows this path:

1. You receive a KYC review state change event indicating KYC/B data is needed for the customer to proceed (requires subscribing to an application webhook).
2. You check the `requirements` array from the webhook payload, collect any required details you don’t already have for the customer (if any), and send the data to Wise.
3. Wise sends a KYC review state change event to indicate the status is `PROCESSING` once all requirements have been submitted.
4. Wise reviews the submitted data and sends a state change event to indicate the customer has passed or more input is required.


## API onboarding process

Once you have [subscribed to the KYC state change webhook](/guides/product/account-setup/customer-onboarding/kyc-statechange-webhook), you can then initiate onboarding for customer profiles that require it.

### Proactive KYC

To perform **proactive KYC**, send a [create KYC review request](/api-reference/kyc-review/kycreviewcreate) before attempting to submit the customer's first transfer.

In the request body, set the `triggerReferences.​type` field to `PROACTIVE_SEND_MONEY`.

Note that if the KYC review is not requested proactively, the first request to create a transfer automatically creates a KYC review resource.

The rest of the process is the same whether doing proactive KYC or initiating on the customer’s first transfer.

### Step 1: Check KYC review status

Check the `data.resource.state` field of the KYC review state change event payload.

When the status is `WAITING_CUSTOMER_INPUT`, this means Wise requires some KYC/KYB details before the customer can send money and perform certain transactions.

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

### Step 2: Identify customer data requirements

The KYC review state change event payload also includes a `data.resource.requirements` array, which lists the required KYC/B data for your customer.

```json
"data": {
    "resource": {
      ...,
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
            "versions": [ … ],
            "attributes": {}
          }
        ]
      ],
```

Each object in the `data.resource.requirements` array indicates a required piece of data that must be submitted for the customer and consists of the following properties:

| Property  | Type | Description |
|  --- | --- | --- |
| `key` | Enum string | The name of the KYC requirement, from an enumerated list of values.


See the [KYC requirement types guide](/guides/product/account-setup/customer-onboarding/kyc-requirement-types) for the full list of available values and their descriptions. |
| `state` | Enum string | - `NOT_PROVIDED`: This data has not yet been submitted, or it was submitted previously but rejected (if a piece of data is submitted and reviewed but then rejected, the state of that requirement returns to `NOT_PROVIDED`).
- `IN_REVIEW`: This data has been submitted and is being reviewed.
- `VERIFIED`: This data has been reviewed and accepted.

 |
| `apiCollectionSupported` | boolean | - If `true`, this data can be submitted via API. To submit this data, use the [Submit KYC requirement endpoint](/api-reference/kyc-review/kycreviewrequirementsubmit).
- If `false`, this data cannot be submitted via API and the customer must go through the hosted onboarding flow to provide it. See the [Using the hybrid method section](#using-the-hybrid-method) for instructions.

 |
| `versions` | array | This represents the versions of the requirement key as an object containing a `version` property and `validUntil` property.


A new version for a requirement key can occur when the data structure or accepted values change. For example, if an enum value is added or removed as an accepted value for the `ACCOUNT_PURPOSE` key, that key would now have a new version while the prior version would be valid for an amount of time. |


### Step 3: Collecting and submitting requirements

What you do next depends on if you have all the required data already or need to collect more data from your customer, and whether the required data can be submitted via API or not.

- **You have all required data and it can be submitted via API**: Submit the data via the [Submit KYC requirement endpoint](/api-reference/kyc-review/kycreviewrequirementsubmit).
- **You do not have all required data but each data type can be submitted via API**: Direct your customer through your KYC collection process to gather the remaining requirements. Once collected, submit the data via the [Submit KYC requirement endpoint](/api-reference/kyc-review/kycreviewrequirementsubmit).
- **Some required data cannot be submitted via API**: In this case, submit the data you have collected that can be submitted via API, then get the redirect link to send your customer through the hosted onboarding to collect the rest. See [Using the hybrid method section](#using-the-hybrid-method) for details.


### Step 4: Monitor review state change events

Wise reviews the submitted details and determines if the information is sufficient to pass the KYC review or if we require more information.

#### Information accepted

If the customer's information is accepted, Wise sends a KYC state change notification with a `PASSED` KYC review state. The customer's profile is then allowed to perform transactions, like transferring money, via the Wise Platform API.

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

- In this case, check the `requirements` array for any requirement keys that are still in or have returned to the `NOT_PROVIDED` state.
- If the event includes an `additionalRequirements` array, this indicates additional details are needed that were not previously identified.
- If any of the submitted data was rejected, a `reasons` object for the requirement key includes a description for the rejection.


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

## Using the hybrid method

For any requirements that state `apiCollectionSupported` is `false`, or that you do not collect via your system, the customer must go through the hosted onboarding flow to provide that required data.

To use the hybrid method:

1. Submit all collected data that can be submitted via API to Wise using the [Submit KYC requirement endpoint](/api-reference/kyc-review/kycreviewrequirementsubmit).
2. Request the link for the hosted onboarding flow using the [update KYC review to get a hosted KYC link endpoint](/api-reference/kyc-review/kycreviewredirecturlupdate).
3. Direct your customer to the link. The hosted onboarding flow will collect only the remaining requirements and then redirect your customer back to your application.
4. Monitor the review state change events.


## KYC review statuses

KYC review statuses and what they mean:

| Status  | Description |
|  --- | --- |
| `NEW` | KYC review has been newly created and requirements are being determined. When you create a KYC review resource, this is the first status the resource will be in and the response will not include a `link` or `requirements` object. KYC Review will be in this state for, at most, a few seconds, and then will move to `WAITING_CUSTOMER_INPUT`. |
| `WAITING_CUSTOMER_INPUT` | The customer needs to provide some KYC information before they can perform any transactions. KYC review also returns to this status if the Wise review determines more data is required or rejects some piece of submitted data. |
| `PROCESSING` | Wise has received the submitted data and is reviewing it. KYC review will be in this state for, at most, a few seconds when processing is done automatically. However, when manual review is required the review will be in this state a bit longer, for example, when a provided document needs to be reviewed manually. |
| `PASSED` | No further customer action is required, and the initiating action can proceed. |
| `PASSED_WITH_REQUIREMENTS` | The initiating action can proceed, but additional non-blocking requirements must be completed by the customer to avoid later suspension. |
| `EXPIRED` | Signals that a KYC review can no longer be actioned. Occurs if a KYC review is initiated by a quote and that quote has expired. A new quote then needs to be created. |