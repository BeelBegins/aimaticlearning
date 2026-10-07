# Essential webhooks

The webhooks considered essential for your integration depend on your integration model and which products you are using. This page lists Wise Platform's most essential webhooks, who they apply to, and under what circumstances.

Once [subscribed to a webhook](/guides/developer/webhooks/subscribe-to-webhooks), you'll receive event notification payloads you can use to keep your system and customers updated, as well as trigger automated actions.

Additional webhooks
See our full [Webhook event reference](/api-reference/webhook-event) for details about all webhooks available on Wise Platform.

## Transfer webhooks

When sending money, use transfer webhooks to track the status of transfers and get alerted if there is a payout failure or a refund event.

Applicable to **all partner integrations**, regardless of integration model.

- [Transfer state change](/api-reference/webhook-event/eventtransfersstatechange)
- [Transfer payout failure](/api-reference/webhook-event/eventtransferspayoutfailure)
- [Transfer refund](/api-reference/webhook-event/eventtransfersrefund)
- [Transfers active cases](/api-reference/webhook-event/eventtransfersactivecases)


### Example payloads

Transfer state change
```json
{
  "data": {
    "resource": {
      "type": "transfer",
      "id": 111,
      "profile_id": 222,
      "account_id": 333
    },
    "current_state": "processing",
    "previous_state": "incoming_payment_waiting",
    "occurred_at": "2020-01-01T12:34:56.789Z"
  },
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#state-change",
  "schema_version": "4.0.0",
  "sent_at": "2020-01-01T12:34:56.123Z"
}
```

Payout failure
```json
{
  "data": {
    "transfer_id": 111,
    "profile_id": 222,
    "failure_reason_code": "WRONG_ID_NUMBER",
    "failure_description": "Invalid recipient's ID document number",
    "occurred_at": "2023-08-10T10:17:23.123Z"
  },
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#payout-failure",
  "schema_version": "4.0.0",
  "sent_at": "2023-08-10T10:17:28.123Z"
}
```

Transfer refund
```json
{
  "data": {
    "resource": {
      "type": "transfer",
      "id": 111,
      "profile_id": 222,
      "account_id": 333,
      "refund_amount": 5000,
      "refund_currency": "EUR"
    },
    "occurred_at": "2024-01-01T12:34:56.789Z"
  },
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#refund",
  "schema_version": "4.0.0",
  "sent_at": "2024-01-01T12:34:56.123Z"
}
```

Transfers active cases
```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "transfers#active-cases",
  "sent_at": "2026-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "type": "transfer",
      "id": 111,
      "profile_id": 222,
      "account_id": 333
    },
    "active_cases": [
      "deposit_amount_less_invoice"
    ]
  }
}
```

## Funding webhooks

When funding transfers, use the funding-related webhooks to track balance and payin events.

Applicable to **Correspondent** and **Enterprise** integration models.

- [Balance update](/api-reference/webhook-event/eventbalancesupdate): Subscribe if funding transfers from a multi-currency balance account.
- [Create payment instrument status change](/guides/product/send-money/funding/direct-debit/create-payment-instrument): Subscribe if funding transfers via direct debit.
- [Payin status change](/guides/product/send-money/funding/direct-debit/create-payin): Subscribe if funding transfers via direct debit.


### Example payloads

#### Balance update credit

```json
{
  "data": {
    "resource": {
      "id": 2,
      "profile_id": 2,
      "type": "balance-account"
    },
    "amount": 70,
    "balance_id": 111,
    "channel_name": "TRANSFER",
    "currency": "GBP",
    "occurred_at": "2023-03-08T14:55:38.123Z",
    "post_transaction_balance_amount": 88.93,
    "step_id": 1234567,
    "transaction_type": "credit",
    "transfer_reference": "BNK-1234567"
  },
  "subscription_id": "f2264fe5-a0f5-4dab-a1b4-6faa87761425",
  "event_type": "balances#update",
  "schema_version": "4.0.0",
  "sent_at": "2023-03-08T14:55:39.456Z"
}
```

#### Payment instrument status changes

Connected status payload
When a payment instrument is successfully connected:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-19T17:43:23Z",
  "data": {
    "resource": {
      "id": "7f0f9dda-7755-4b4f-bd53-637129291308"
    },
    "from_status": "PENDING",
    "to_status": "CONNECTED",
    "occurred_at": "2025-01-19T17:43:22Z"
  }
}
```

Disconnected status payload
When a payment instrument becomes disconnected, the `disconnect_reason` field is included in `data.resource`:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-20T14:22:18Z",
  "data": {
    "resource": {
      "id": "7f0f9dda-7755-4b4f-bd53-637129291308",
      "disconnect_reason": "REFER_TO_PAYER"
    },
    "from_status": "CONNECTED",
    "to_status": "DISCONNECTED",
    "occurred_at": "2025-01-20T14:22:17Z"
  }
}
```

#### Payin status changes

Processing status payload
When a payin enters the processing state:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments-payins#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-19T10:15:23Z",
  "data": {
    "resource": {
      "id": "67136333-0b4d-4f72-49bf-24088f687416",
      "payment_instrument_id": "67133810-d4f6-47b4-a948-09b2d8438b43"
    },
    "from_status": null,
    "to_status": "PROCESSING",
    "occurred_at": "2025-01-19T10:15:22Z"
  }
}
```

Settled status payload
When a payin successfully settles:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments-payins#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-22T14:30:46Z",
  "data": {
    "resource": {
      "id": "67136333-0b4d-4f72-49bf-24088f687416",
      "payment_instrument_id": "67133810-d4f6-47b4-a948-09b2d8438b43"
    },
    "from_status": "CONFIRMED",
    "to_status": "SETTLED",
    "occurred_at": "2025-01-22T14:30:45Z"
  }
}
```

Failed status payload
When a payin fails, the `failure_reason` field is included in `data.resource`:

```json
{
  "subscription_id": "36f45c7e-e4bf-4342-88fc-ead33500f9b8",
  "event_type": "payment-instruments-payins#status-change",
  "schema_version": "0.0.1",
  "sent_at": "2025-01-20T16:45:19Z",
  "data": {
    "resource": {
      "id": "78247444-1c5e-5083-5acf-35199f798c527",
      "payment_instrument_id": "67133810-d4f6-47b4-a948-09b2d8438b43",
      "failure_reason": "REFER_TO_PAYER"
    },
    "from_status": "PROCESSING",
    "to_status": "FAILED",
    "occurred_at": "2025-01-20T16:45:18Z"
  }
}
```

## Manage balances webhooks

For partners with multi-currency accounts, use the balance update webhook to get notified when either credit or debit events occur on a balance account.

Applicable to **Correspondent** and **Enterprise** integration models.

- [Balance update](/api-reference/webhook-event/eventbalancesupdate)


### Example payloads

Balance update credit
```json
{
  "data": {
    "resource": {
      "id": 2,
      "profile_id": 2,
      "type": "balance-account"
    },
    "amount": 70,
    "balance_id": 111,
    "channel_name": "TRANSFER",
    "currency": "GBP",
    "occurred_at": "2023-03-08T14:55:38.123Z",
    "post_transaction_balance_amount": 88.93,
    "step_id": 1234567,
    "transaction_type": "credit",
    "transfer_reference": "BNK-1234567"
  },
  "subscription_id": "f2264fe5-a0f5-4dab-a1b4-6faa87761425",
  "event_type": "balances#update",
  "schema_version": "4.0.0",
  "sent_at": "2023-03-08T14:55:39.456Z"
}
```

Balance update debit
```json
{
  "data": {
    "resource": {
      "id": 2,
      "profile_id": 2,
      "type": "balance-account"
    },
    "amount": 9.6,
    "balance_id": 111,
    "channel_name": "TRANSFER",
    "currency": "GBP",
    "occurred_at": "2023-03-08T15:26:07.891Z",
    "post_transaction_balance_amount": 106.93,
    "step_id": 1234567,
    "transaction_type": "debit",
    "transfer_reference": "47500002"
  },
  "subscription_id": "f2264fe5-a0f5-4dab-a1b4-6faa87761425",
  "event_type": "balances#update",
  "schema_version": "4.0.0",
  "sent_at": "2023-03-08T15:26:07.234Z"
}
```

## Receive money webhooks

When using the [international receive product](/guides/product/receive-money), use these webhooks to receive notifications when an account receives an incoming transfer.

Applicable to partners on the **Correspondent** and **Enterprise** integration models.

- [Incoming transfer credited](/api-reference/webhook-event/eventincomingtransfercredited)
- [Swift message received](/api-reference/webhook-event/eventswiftmessagereceived)


See our [Incoming transfers guide](/guides/product/receive-money/incoming-transfer-notifications) for more details.

### Example payload

**Incoming transfer credited**:

```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "incoming-transfer#credited",
  "sent_at": "2026-10-21T12:34:58.123Z",
  "data": {
    "incoming_transfer_id": "01234567-89ab-cdef-0123-456789abcdef",
    "occurred_at": "2026-08-21T12:34:56.789Z"
  }
}
```

## Issue cards webhooks

When using the [issue cards product](/guides/product/issue-cards), receive notifications every time a card order status updates or a [card status changes](/guides/product/issue-cards/card-transaction), including the initial card status.

Applicable to partners on the **Correspondent** and **Enterprise** integration models.

- [Card status changes](/api-reference/webhook-event/eventcardscardstatuschange)
- [Card order status changes](/api-reference/webhook-event/eventcardscardorderstatuschange)


### Example payloads

Card status change
```json
{
  "schema_version": "4.0.0",
  "subscription_id": "ABCD-1234-ABCD-1234-ABCD",
  "event_type": "cards#card-status-change",
  "sent_at": "2022-08-22T07:59:50.123Z",
  "data": {
    "resource": {
      "profile_id": 123456,
      "client_id": "your-bank",
      "card_token": "ABCD-1234-ABCD-1234-ABCD",
      "type": "card"
    },
    "card_status": "FROZEN",
    "changed_by": "internal_system",
    "occurred_at": "2022-08-22T07:49:50.789Z"
  }
}
```

Card order status change
```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "cards#card-order-status-change",
  "sent_at": "2023-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "profile_id": 123456,
      "type": "card",
      "client_id": "your-bank",
      "card_token": "35050a4a-9521-426e-8109-1396e3687a3e",
      "card_program": "VISA_DEBIT_CONSUMER_UK_1_PHYSICAL_CARDS_API"
    },
    "order_id": "1001L",
    "order_status": "PRODUCED",
    "delivery_vendor": "DHL",
    "occurred_at": "2023-01-01T12:24:56.789Z"
  }
}
```

## Profile and KYC webhooks

When creating profiles for your customers during customer onboarding, use the profile and KYC webhooks to be notified when a profile is ready to use or becomes inactive for some reason.

Applicable to the **Embedded finance** integration model.

- [Profile state change](/api-reference/webhook-event/eventprofilesstatechange)
- [Profile verification state change](/api-reference/webhook-event/eventprofilesverificationstatechange)
- [KYC review state change](/api-reference/webhook-event/eventkycreviewsstatechange): For partners using the [KYC review endpoint](/api-reference/kyc-review/kycreviewcreate) only.


### Example payloads

Profile state change
```json
{
  "schema_version": "4.0.0",
  "subscription_id": "f5b51f77-e14a-433b-9f7c-fc2834ffcff5",
  "event_type": "profiles#state-change",
  "sent_at": "2020-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "id": 1234,
      "type": "profile"
    },
    "current_state": "WITHDRAW_ONLY",
    "occurred_at": "2020-01-01T12:34:56.789Z",
    "requested_by_customer": false
  }
}
```

Verification state change
```json
{
  "schema_version": "4.0.0",
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "profiles#verification-state-change",
  "sent_at": "2026-01-01T12:34:56.123Z",
  "data": {
    "resource": {
      "type": "profile",
      "id": 111
    },
    "current_state": "verified",
    "occurred_at": "2026-01-01T12:34:56.789Z"
  }
}
```

KYC review state change
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

## Support case webhooks

If submitting support requests via API, subscribe to the support case change webhook to be notified about comments and status changes.

Applicable to **all partner integrations**.

- [Partner support case changed](/api-reference/webhook-event/eventpartnersupportcasechanged)


### Example payload

```json
{
  "schema_version": "4.0.0",
  "subscription_id": "017631af-326c-4a69-93f3-bd1ce987a743",
  "event_type": "partner-support#case-changed",
  "sent_at": "2023-06-23T09:45:36.123Z",
  "data": {
    "resource": {
      "type": "partner-support-case",
      "case_id": 136,
      "case_type": "GENERAL_ENQUIRY",
      "details": {
        "transfer_id": 12345678,
        "user_id": 12345678,
        "profile_id": 12345678
      },
      "status": "PENDING"
    },
    "type": "NEW_CASE",
    "occurred_at": "2023-06-23T09:45:34.789Z"
  }
}
```