# Payout failures

Subscribe to [transfer payout failure event webhook](/api-reference/webhook-event/eventtransferspayoutfailure) to understand why a payout failed.

Use this event when you want to either understand the reason or guide customers to fix payout issues (for example, incorrect account details). The `transfers#state-change` and `transfers#payout-failure` events differ in purpose and most effective when used together.

- `transfers#state-change` provides high-level understanding of a transfer's status.
- `transfers#payout-failure` provides payout failure details, reason code and description, when failures occur.


## Failure reason codes

| Code  | Description |
|  --- | --- |
| `ACCOUNT_CLOSED` | The recipient details are correct, but beneficiary account is closed. |
| `ACCOUNT_FROZEN` | The recipient details are correct, but beneficiary account is frozen. |
| `ACCOUNT_BLOCKED` | The recipient details are correct, but beneficiary account is blocked. |
| `ACCOUNT_LIMIT_REACHED` | The recipient details are correct, but beneficiary account has a limit that can be unblocked by the recipient. |
| `WRONG_ACCOUNT_NUMBER` | Invalid account number. |
| `WRONG_CARD_NUMBER` | Invalid card number. |
| `WRONG_ACCOUNT_DETAILS` | Invalid account number and/or invalid bank code. |
| `WRONG_ACCOUNT_TYPE` | Incorrect account type. |
| `WRONG_BANK_CODE` | Invalid sort/BIC/routing/etc number. |
| `WRONG_BRANCH_CODE` | Invalid branch code. |
| `WRONG_NAME` | Account number matches, but the name is not 100% correct. |
| `WRONG_PHONE_NUMBER` | Recipient phone number is incorrect. |
| `WRONG_ID_NUMBER` | Invalid recipient's ID document number |
| `WRONG_RUT_NUMBER` | Invalid recipient's RUT (Rol Unico Tributario) number. |
| `TAX_ID_NOT_MATCHING` | Tax ID doesn't match recipient's name. |
| `TAX_ID_SUSPENDED` | Tax ID is suspended. |
| `WRONG_REFERENCE` | Invalid payment reference. |
| `WRONG_PAYMENT_PURPOSE` | Invalid or not accepted payment purpose. |
| `ACCOUNT_DOES_NOT_EXIST` | Format is correct but this account does not exist in recipient bank. |
| `WRONG_CURRENCY` | Recipient account is in different currency. |
| `WRONG_CARD_TYPE` | Recipient account doesn't support payments to this card type. |
| `CANNOT_ACCEPT_FROM_3RD_PARTY` | Recipient bank can't accept the payments from 3rd party. |
| `CREDITING_ACCOUNT_FORBIDDEN` | Terms and Conditions of Account do not permit crediting of these funds. |
| `DUPLICATE_ENTRY` | Recipient bank informs that there has been another payment in the same amount. |
| `FUNDS_NOT_EXPECTED_RETURNED` | Beneficiary not expecting funds/instructed return. |
| `MANDATE_NOT_FILLED_IN` | Recipient didn't fill out the mandate form on time or the email address is incorrect. |
| `BUSINESS_PAYMENTS_FORBIDDEN` | Payment to business accounts are not allowed. |
| `SENDER_REQUESTED_TO_CANCEL` | Sender requested cancellation. |
| `REQUEST_FOR_INFORMATION_EXPIRED` | Request for information expired. |
| `RETURN_REQUESTED_BY_RECIPIENT` | Recipient requested return. |
| `EXTERNAL_IDENTIFIER_DETAILS_HAVE_CHANGED` | External identifier details have changed. |
| `TECHNICAL_ISSUE` (available v5.0.0 onwards) | Payment failed due to a technical issue |
| `TECHNICAL_ISSUE_RETRYABLE` (available v5.0.0 onwards) | Payment failed due to a technical issue, Wise will retry |
| `REASON_NOT_SPECIFIED` | Reason not specified. |


## Notes about payout failures

General
- Payout failures can occur while a transfer remains in `outgoing_payment_sent`. Not every payout failure triggers a transfer state change.
- A transfer may emit multiple `transfers#payout-failure` events.
  - Not every rejected transfer (for example `bounced_back` or `funds_refunded`) will have a corresponding `transfers#payout-failure` webhook.
- Wise may add new failure codes over time. Your system should handle unrecognised codes.


V5.0.0 release notes
Version 5.0.0 adds two public reason codes: `TECHNICAL_ISSUE` and `TECHNICAL_ISSUE_RETRYABLE`. The payload fields are unchanged, but the API contract now defines `failure_reason_code` as an enum rather than an unrestricted string.

| Code  | Description | Recommended handling |
|  --- | --- | --- |
| `TECHNICAL_ISSUE` (available v5.0.0 onwards) | Payment failed due to a technical issue | Record the event and reconcile it with `transfers#state-change`. Do not infer the final outcome from this event alone. |
| `TECHNICAL_ISSUE_RETRYABLE` (available v5.0.0 onwards) | Payment failed due to a technical issue, Wise will retry | Do not trigger a final-failure or refund workflow based only on this event. |


**Action Required from Partners**

1. Prepare your handler. Add the two v5 values, keep a safe fallback for future unrecognised codes and use `failure_description` only for display or logging.
2. Create a v5 subscription. Use the same callback URL and scope. Application-level subscriptions are recommended for most partners; profile-level subscriptions remain available when needed.
3. Validate before cutover. Return a `2xx` response to the automatic test event, then use the sandbox payout-failure simulation and confirm `schema_version` is 5.0.0.
4. Retire the earlier subscription. After v5 is verified, delete the earlier subscription so only the intended subscription remains active.


## Testing payout failures in the sandbox

Before you can test payout failures, you must create and fund a transfer in the sandbox. Once you have a funded transfer and have the `transferID`, you can test payout failures using the following steps:

### Step 1: Simulate transfer into bounced_back

Use the [simulation transfer state change](/api-reference/simulation/simulationtransferstatechange) endpoint to move the transfer through states in order:

`processing` → `funds_converted` → `outgoing_payment_sent` → `bounced_back`

This ensures the transfer is in the correct state for payout failure simulation.

### Step 2: Trigger payout failure

Use the [simulation payout failure endpoint](/api-reference/simulation/simulationtransferpayoutfailure).

You can do either of the following:

- Omit the body to get a random failure reason (for the transfer’s route/currency pair).
- Specify a particular `failure_reason_code` in the body.


Example request
```json Payload application/json
{}
```

Example response
```json 200 application/json
{
  "failure_reason_code": "WRONG_ID_NUMBER",
  "failure_description": "Invalid recipient's ID document number",
  "occurred_at": "2023-08-10T10:17:23.123Z"
}
```

```json 400 application/json
{
  "errors": [
    {
      "arguments": [],
      "code": "invalid_failure_reason_code",
      "message": "The provided failure reason code 'INVALID_CODE' is not recognized"
    }
  ]
}
```

```json 429 application/json
{}
```

```json 500 application/json
{
  "errors": [
    {
      "code": "system_error",
      "message": "Something went wrong in our side. Please try again in 5 minutes. If this does not help, please let us know api@wise.com"
    }
  ]
}
```

### Step 3: Verify the webhook you receive

After you trigger the simulation, Wise sends a `transfers#payout-failure` webhook to your subscribed endpoint.

#### Recommended handling

- Treat `failure_reason_code` as the stable machine-readable value.
- Use `failure_description` for display/logging, but don’t hard-depend on the exact text.
- Store/trace `transfer_id`, `occurred_at`, and (in your logs) the request `x-trace-id` to simplify support/debugging.
- Be prepared for new reason codes over time (fallback messaging).