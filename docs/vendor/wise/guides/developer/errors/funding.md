# Funding errors

Handle rejected transfer funding, insufficient funds, and SCA responses.

This page covers transfer funding and retrieving funding attempts.

Funding is a separate lifecycle action after transfer creation. The available funding methods and error responses depend on your settlement model and integration configuration.

On this page:

- [Fund a transfer](#fund-a-transfer)
- [Retrieve funding attempts](#retrieve-funding-attempts)
- [Handle SCA responses](#handle-sca-responses)
- [Retry funding requests](#retry-funding-requests)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely.

## Fund a transfer

**Endpoint:** `POST /profiles/{profileId}/transfers/{transferId}/payments`

Use the [fund a transfer operation](/api-reference/transfer/transferfund) as the source of truth for the current request and response schema.

**Interpret the funding result**

A successful HTTP response does not always mean that Wise funded the transfer. Always check `status` and `errorCode` in the response body.

Depending on when the failure occurs, the operation can return a non-success HTTP response or a funding result with `status: REJECTED`. Detect the response format before reading the code.

The optional `errorMessage` is diagnostic text. It is not localised or safe to display directly to end users.

**Completed funding**

```json
{
  "type": "BALANCE",
  "status": "COMPLETED",
  "errorCode": null
}
```

Mark the transfer as funded only after the response reports `COMPLETED`.

### Shared funding errors

These codes can apply across more than one funding type.

Wise cannot find the transfer identified by the request in the current profile context.

**What to do**

- Verify the transfer and profile identifiers.
- Confirm that the transfer was created in the same environment.


**Retry conditions**

Do not retry until the identifiers or context change.

The transfer's current state does not allow funding. It can already be funded, cancelled, or being processed.

**What to do**

- Retrieve the latest transfer state.
- Reconcile whether an earlier funding request succeeded.
- Do not create a second funding attempt for the same completed action.


**Retry conditions**

Retry only when the latest transfer state allows funding.

**Example error response**

```json
{
  "type": "TRUSTED_PRE_FUND_BULK",
  "status": "REJECTED",
  "errorCode": "transfer.invalid-state",
  "errorMessage": null
}
```

A funding payment already exists for the transfer or logical funding attempt.

**What to do**

Reconcile the existing payment and transfer state instead of creating another payment.

**Retry conditions**

Do not retry as a new funding attempt.

The authenticated user cannot access or fund the transfer.

**What to do**

Verify the token, profile ownership, and agreed permissions for the funding operation.

**Retry conditions**

Retry only with an identity that can access the transfer.

Wise cannot find the expected funding payment. In delayed funding, this can occur when completion is requested before initiation.

**What to do**

- Verify the funding sequence and payment state.
- Initiate delayed funding before completing it when the integration uses that flow.


**Retry conditions**

Retry only after restoring the required funding sequence.

The funding request is missing required data or does not match the selected funding type.

**What to do**

Compare the request with the current schema for `BALANCE`, `TRUSTED_PRE_FUND_BULK`, or `TRUSTED_PRE_FUND_TX`.

**Retry conditions**

Retry after correcting the request.

Wise could not complete the funding operation because of an unexpected service failure.

**What to do**

- Return a safe system-error message.
- Record a redacted response signature.
- Reconcile the transfer and funding state before creating another attempt.


**Retry conditions**

Do not automatically retry an unexplained failure. Retry only if a transient cause and safe replay are confirmed, using bounded backoff after reconciliation.

The selected funding option is not available for the transfer or integration context.

**What to do**

Choose an available funding type or confirm the funding model enabled for the integration.

**Retry conditions**

Do not retry with the same unavailable option.

### Balance funding errors

These codes apply when the request uses `type: BALANCE`.

The authenticated identity does not have the required security role for balance funding.

**What to do**

Verify the token type, profile, permissions, and any applicable authentication requirement.

**Retry conditions**

Retry only after resolving access.

Balance funding is not available for this transfer or profile context.

**What to do**

Confirm that balance funding is supported and choose another available funding approach when applicable.

**Retry conditions**

Do not retry the same option until its availability changes.

Wise cannot find the balance identified by the request in the current profile context.

**What to do**

Verify `balanceId`, profile ownership, currency, and environment.

**Retry conditions**

Retry after providing an accessible balance identifier.

The selected balance is not active and cannot fund the transfer.

**What to do**

Choose an active eligible balance or resolve the balance state before funding.

**Retry conditions**

Retry only after selecting an active balance.

The selected Wise balance does not contain enough available funds.

**What to do**

- Do not mark the transfer as funded.
- Add sufficient funds or choose another supported funding approach.


**Retry conditions**

Retry after sufficient funds are available.

**Example error response**

```json
{
  "type": "BALANCE",
  "status": "REJECTED",
  "errorCode": "balance.insufficient-funds"
}
```

The profile does not have an eligible balance for the transfer's funding currency.

**What to do**

Select or fund a balance in the required currency, or use another supported funding approach.

**Retry conditions**

Retry after an eligible balance is available.

The selected currency is not supported for balance funding.

**What to do**

Use a supported funding currency or another available funding type.

**Retry conditions**

Do not retry with the same unsupported currency.

### Trusted pre-funding errors

These codes apply to funding models enabled by agreement with Wise.

The integration is not enabled to use bulk trusted pre-funding for this request.

**What to do**

Use the funding type agreed for the integration or confirm the bulk settlement configuration with Wise.

**Retry conditions**

Do not retry with `TRUSTED_PRE_FUND_BULK` until it is available.

The integration is not enabled to use per-transfer trusted pre-funding for this request.

**What to do**

Use the funding type agreed for the integration or confirm the per-transfer funding configuration with Wise.

**Retry conditions**

Do not retry with `TRUSTED_PRE_FUND_TX` until it is available.

### Integration-specific funding errors

Some funding integrations can return identifiers outside the standard fund transfer catalogue. Interpret these only for the operation and response format in which they are documented.

The selected Wise balance does not contain enough available funds to fund the transfer.

**What to do**

- Do not mark the transfer as funded.
- If the customer owns the funding balance, explain that more funds are needed. If it is a partner or correspondent balance, notify your operations team and show the customer an appropriate payment-unavailable message.
- Add funds or choose another supported funding approach.


**Retry conditions**

Call the funding operation again after sufficient funds are available.

**Example error response**

```json
{
  "type": "BALANCE",
  "status": "REJECTED",
  "errorCode": "transfer.insufficient_funds"
}
```

## Retrieve funding attempts

**Endpoint:** `GET /transfers/{transferId}/payments`

See the [list transfer payments operation](/api-reference/transfer/transferpaymentslist) for the current request and response schema.

Wise could not find the transfer identified by `transferId`.

**HTTP status:** `404`

**What to do**

- Verify the transfer ID, profile, environment, and access context.
- Return a generic not-found message when revealing the transfer could disclose unauthorised information.


**Retry conditions**

Retry only after correcting the lookup context.

**Example error response**

```json
{
  "errors": [
    {
      "code": "error.transfer.not.found",
      "message": "We couldn't find a transfer with that ID (111111111)",
      "arguments": [111111111]
    }
  ]
}
```

## Handle SCA responses

Funding can return `403` when strong customer authentication applies. Check the documented SCA response headers before treating the response as a permanent permission denial.

**Complete the SCA challenge**

1. Check for `X-2FA-Approval` and `X-2FA-Approval-Result`.
2. Complete the required SCA challenge.
3. Retry the funding operation with the approved one-time token.


See [SCA and two-factor authentication](/guides/developer/auth-and-security/sca-and-2fa) for the supported flow.

## Retry funding requests

- Correct the funding method, profile, or transfer context before retrying a request error.
- Complete SCA before retrying an applicable `403` response.
- Add sufficient funds before retrying a rejected balance funding request.
- Follow `Retry-After` for `429` responses.
- Retry transient `5xx` responses only when the operation is safe to repeat, using bounded exponential backoff and jitter. Reconcile an uncertain funding outcome first.
- Reconcile the funding result after a timeout or other uncertain response.


For transfer creation, retrieval, and cancellation errors, see the [transfer error overview](/guides/developer/errors/transfers).