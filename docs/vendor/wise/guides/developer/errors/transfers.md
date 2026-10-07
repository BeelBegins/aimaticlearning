# Transfer errors

Handle standard and third-party transfer operation errors.

Wise supports standard transfers and third-party transfers. Match the error to the endpoint and transfer model before applying recovery logic because the request fields and identifiers differ.

On this page:

- [Create a standard transfer](#create-a-standard-transfer)
- [Retrieve a standard transfer](#retrieve-a-standard-transfer)
- [Cancel a standard transfer](#cancel-a-standard-transfer)
- [Create a third-party transfer](#create-a-third-party-transfer)
- [Retrieve a third-party transfer](#retrieve-a-third-party-transfer)
- [Retry transfer operations](#retry-transfer-operations)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely. Ask the customer to correct details only when they can edit them. If your integration supplies or changes those values, correct its validation or mapping instead.

## Create a standard transfer

**Endpoint:** `POST /transfers`

See the [create a standard transfer operation](/api-reference/standard-transfer/transfercreate) for the current schema.

Standard transfers can require additional fields depending on the currency route and amount. Call the [transfer requirements operation](/api-reference/transfer/transferrequirementsvalidate), map every returned requirement to `details`, and correct the request before retrying.

Use `customerTransactionId` to identify the logical transfer. Reuse it when retrying the same uncertain creation attempt. A new identifier represents a different logical transfer and can create a duplicate.

The recipient does not meet the requirements for this transfer. The example shows a missing recipient address.

**HTTP status:** `422`

**What to do**

Retrieve the requirements for the final quote and recipient. Correct the recipient details identified by the response, then recheck the transfer requirements. For the missing-address example, update or create the recipient with the required address.

**Retry conditions**

Submit again only after the recipient meets the requirements. Preserve the logical transfer identifier when retrying the same transfer.

**Example error response (POST /v1/transfers)**

```json
{
  "errors": [
    {
      "code": "INVALID_RECIPIENT",
      "message": "Recipient address is mandatory for this payment, please update or create a new recipient.",
      "arguments": []
    }
  ]
}
```

## Retrieve a standard transfer

**Endpoint:** `GET /transfers/{transferId}`

See the [retrieve a standard transfer operation](/api-reference/transfer/transferget) for the current response schema.

The transfer is not available for the supplied transfer and profile context.

**What to do**

- Verify the transfer ID, profile, environment, and access context.
- Return a generic not-found result when revealing the resource would disclose unauthorised information.


**Retry conditions**

Retry only after correcting the lookup context.

## Cancel a standard transfer

**Endpoint:** `POST /transfers/{transferId}/cancel`

See the [cancel a transfer operation](/api-reference/transfer/transfercancel) for the current schema.

The transfer is no longer in a cancellable state or another cancellation restriction applies.

**What to do**

- Retrieve the latest transfer state.
- Disable cancellation when the current state does not permit it.


**Retry conditions**

Do not retry unless the latest state explicitly permits cancellation.

**Example error response**

```json
{
  "errors": [
    {
      "code": "transfer.cancellation.not.allowed",
      "message": "Transfer cannot be cancelled",
      "arguments": []
    }
  ]
}
```

## Create a third-party transfer

**Endpoint:** `POST /profiles/{profileId}/third-party-transfers`

See the [create a third-party transfer operation](/api-reference/third-party-transfer/createthirdpartytransfer) for the current schema.

These errors apply to integrations that create transfers for an underlying originator. Codes in the `validation.failure.*` family usually identify the affected field or constraint. Some codes retain older field names, so use the mapping described with the code and the current operation schema.

The recipient account is not supported for this payment.

**HTTP status:** `400`

**What to do**

Correct or replace the recipient details using the current recipient requirements.

**Retry conditions**

Retry only after correcting or replacing the recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-22T23:46:47.829754177Z",
  "errors": [
    {
      "code": "ACCOUNT_NOT_SUPPORTED",
      "message": "We cannot currently accept payments to this recipient.",
      "path": "account"
    }
  ]
}
```

Wise cannot register a transfer from the specified originator.

**HTTP status:** `400`

**What to do**

Record the response and investigate why transfers from this originator are not allowed. Correct confirmed data defects; do not assume changing the reference resolves the restriction. Keep the same originator reference for that originator.

**Retry conditions**

Submit again only after the restriction or a confirmed data defect is resolved. Do not automatically retry unchanged.

**Example error response**

```json
{
  "timestamp": "2026-08-23T02:06:27.793851746Z",
  "errors": [
    {
      "code": "validation.failure.originator.externalId.not.allowed",
      "message": "Can not register transfer from this originator",
      "path": "originator.externalId",
      "arguments": [
        "123124124"
      ]
    }
  ]
}
```

A field failed validation and the response uses a generic identifier. Documented cases include different character restrictions on the payment reference. Use `path` and the returned constraint to identify what needs correcting.

**HTTP status:** `400`

**What to do**

Use `path` to identify the field and apply the constraint for the selected route. For payment-reference errors, check the permitted character set; it differs between documented cases. Do not silently remove meaningful content.

**Retry conditions**

Retry after correcting the identified field.

**Example error response**

```json
{
  "timestamp": "2026-08-21T11:22:47.163082691Z",
  "errors": [
    {
      "code": "ERROR",
      "message": "Please use English characters only: A-Z, a-z, 0-9 and -./?:(),+",
      "path": "paymentReference",
      "arguments": [
        "parameter_invalid_format",
        "[a-zA-Z0-9- ./?:(),+]*"
      ]
    }
  ]
}
```

The transfer exceeds an applicable amount limit. Documented cases include a limit on a single transfer and a daily total for the same recipient. The amount, currency, and limit scope depend on the case.

**HTTP status:** `400`

**What to do**

Check whether the response identifies a per-transfer limit or an aggregate limit, such as a daily total for the same recipient. Reduce the amount where permitted, or wait until the applicable period resets. Splitting a transfer does not resolve an aggregate limit.

**Retry conditions**

Retry only when the transfer fits within the applicable limit, including any aggregate total.

**Example error response**

```json
{
  "timestamp": "2026-08-21T09:08:17.565936479Z",
  "errors": [
    {
      "code": "LIMIT_EXCEEDED",
      "message": "This transfer exceeds our KRW limit of 5,000 USD. Please send a smaller amount or split your transfer.",
      "path": "transferAmount",
      "arguments": [
        5000,
        "USD"
      ]
    }
  ]
}
```

The payment is not allowed under the applicable route restrictions. Documented cases include restrictions on donations to recipients in particular countries.

**HTTP status:** `400`

**What to do**

Do not continue with the restricted payment purpose or recipient. Offer a supported alternative when available.

**Retry conditions**

Do not retry the unchanged request.

**Example error response**

```json
{
  "timestamp": "2026-08-21T09:57:53.207717748Z",
  "errors": [
    {
      "code": "NOT_ALLOWED",
      "message": "Unfortunately, Wise can't be used to make donations in India.",
      "path": "paymentReference",
      "arguments": [
        "transfer.donation_not_allowed",
        "IN"
      ]
    }
  ]
}
```

The payment reference exceeds the maximum length allowed for this request.

**HTTP status:** `400`

**What to do**

Correct `paymentReference` using the returned character or length constraint. Do not silently remove meaningful content.

**Retry conditions**

Retry after correcting the reference.

**Example error response**

```json
{
  "timestamp": "2026-08-21T12:47:54.005121732Z",
  "errors": [
    {
      "code": "REFERENCE_TOO_BIG",
      "message": "Specified reference is too long.",
      "path": "paymentReference",
      "arguments": []
    }
  ]
}
```

The target amount exceeds the limit for the recipient account type.

**HTTP status:** `400`

**What to do**

Reduce the amount to the limit returned for the selected currency, recipient, or payment rail.

**Retry conditions**

Retry after reducing the amount or changing the recipient route.

**Example error response**

```json
{
  "timestamp": "2026-08-23T14:25:05.409091135Z",
  "errors": [
    {
      "code": "account.type.validation.failure.targetAmount.too.large",
      "message": "The most you can send to this recipient is 200,000 INR.",
      "path": "account/type",
      "arguments": [
        200000,
        "INR"
      ]
    }
  ]
}
```

The quote cannot be accepted because it has no target recipient account.

**HTTP status:** `400`

**What to do**

Check that the quote has a recipient attached. Where your flow creates the quote first, update it with the intended `targetAccount` and recheck the resulting payment option before creating the transfer.

**Retry conditions**

Retry after correcting the quote or recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-21T14:49:49.612313967Z",
  "errors": [
    {
      "code": "error.quote.accept.noTargetAccount",
      "message": "We couldn't accept your quote — there wasn't a target account specified.",
      "arguments": []
    }
  ]
}
```

The quote has expired and can no longer be used to create the transfer.

**HTTP status:** `400`

**What to do**

Create a new quote and submit the transfer with the new quote ID.

**Retry conditions**

Do not retry with the expired quote.

**Example error response**

```json
{
  "timestamp": "2026-08-24T10:03:14.330888734Z",
  "errors": [
    {
      "code": "error.quote.expired",
      "message": "Sorry, your quote has expired. Please get a new one.",
      "arguments": []
    }
  ]
}
```

The requested currency route is not currently supported for this transfer.

**HTTP status:** `400`

**What to do**

For an unexpected route rejection, stop and record the issue for Wise API Support. Prevent requests for routes already known to be unavailable. Do not automatically substitute a route.

**Retry conditions**

Do not automatically retry the same route.

**Example error response**

```json
{
  "timestamp": "2026-08-21T11:49:20.628106575Z",
  "errors": [
    {
      "code": "error.route.not.supported",
      "message": "Sorry, you can't send between these currencies right now.",
      "arguments": []
    }
  ]
}
```

The quote has already been used to create a transfer and cannot be reused for another.

**HTTP status:** `400`

**What to do**

Reconcile the existing transfer. Create a new quote only for a different logical transfer.

**Retry conditions**

Do not retry with the used quote.

**Example error response**

```json
{
  "timestamp": "2026-08-21T10:01:31.407453801Z",
  "errors": [
    {
      "code": "quote.duplicate",
      "message": "Cannot use one quote to create 2 transfers",
      "arguments": []
    }
  ]
}
```

The quote and target recipient account do not match for this transfer.

**HTTP status:** `400`

**What to do**

Use a quote and recipient that belong to the same profile and transfer context.

**Retry conditions**

Retry after correcting the quote or recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-22T09:20:18.758696538Z",
  "errors": [
    {
      "code": "quote.targetaccount.mismatching",
      "message": "Sorry, there's an issue with this transfer. To fix it, you'll need to update your Wise app. If you can't, start your transfer over.",
      "arguments": []
    }
  ]
}
```

The target amount exceeds the THB limit for recipients at Siam Commercial Bank (bank code `014`). Check the applicable limit rather than hard-coding the amount shown in the example.

**HTTP status:** `400`

**What to do**

Reduce the amount to the limit returned for the selected currency, recipient, or payment rail.

**Retry conditions**

Retry after reducing the amount or changing the recipient route.

**Example error response**

```json
{
  "timestamp": "2026-08-24T12:23:41.866175331Z",
  "errors": [
    {
      "code": "type.restriction.thb.target.amount.not.supported.by.bank.code.014",
      "message": "You can only send up to 1,499,999 THB to Siam Commercial Bank accounts. Try a lower amount or send to different account details.",
      "path": "account/type",
      "arguments": [
        1499999.0,
        "THB"
      ]
    }
  ]
}
```

The entered account number is not valid for the selected bank.

**HTTP status:** `400`

**What to do**

Correct or replace the recipient details using the current recipient requirements.

**Retry conditions**

Retry only after correcting or replacing the recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-22T08:46:52.870102700Z",
  "errors": [
    {
      "code": "validation.failure.accountNumber.invalid.account.bank",
      "message": "The entered account number is not valid for the selected bank.",
      "path": "details/accountNumber"
    }
  ]
}
```

Wise cannot identify the recipient's bank from the supplied account details.

**HTTP status:** `400`

**What to do**

Correct or replace the recipient details using the current recipient requirements.

**Retry conditions**

Retry only after correcting or replacing the recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-21T10:51:42.365988305Z",
  "errors": [
    {
      "code": "validation.failure.bankDetails.missing",
      "message": "We could not send to this account as we are unable to recognise the bank of the recipient.",
      "path": "account"
    }
  ]
}
```

The recipient is identified as a charity, which is not supported for this payment.

**HTTP status:** `400`

**What to do**

Stop the unsupported payment. Record the restriction and confirm eligibility if unexpected. Do not change accurate recipient details to bypass it.

**Retry conditions**

Do not retry the unchanged request. Continue only with a genuinely supported payment.

**Example error response**

```json
{
  "timestamp": "2026-08-24T17:47:31.685466881Z",
  "errors": [
    {
      "code": "validation.failure.charity.recipient.not.allowed",
      "message": "Sorry, charity recipients are not supported.",
      "path": "account/name/fullName",
      "arguments": [
        "Charity organization"
      ]
    }
  ]
}
```

The Alipay login ID and recipient name do not form a valid match.

**HTTP status:** `400`

**What to do**

Correct or replace the recipient details using the current recipient requirements.

**Retry conditions**

Retry only after correcting or replacing the recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-26T12:27:36.431741533Z",
  "errors": [
    {
      "code": "validation.failure.chinesealipay.accountNumber.not.matched",
      "message": "Please enter a valid login ID and recipient name for Alipay",
      "path": "details/accountNumber"
    }
  ]
}
```

A transfer purpose is required but has not been supplied.

**HTTP status:** `400`

**What to do**

Retrieve the current transfer requirements and provide `details.transferPurpose`.

**Retry conditions**

Retry after adding a supported transfer purpose.

**Example error response**

```json
{
  "timestamp": "2026-08-23T23:37:20.632865352Z",
  "errors": [
    {
      "code": "validation.failure.details.transferPurpose.missing",
      "message": "Transfer purpose is required",
      "path": "details.transferPurpose",
      "arguments": []
    }
  ]
}
```

The supplied recipient name does not match the name held by the bank for the account details.

**HTTP status:** `400`

**What to do**

Correct or replace the recipient details using the current recipient requirements.

**Retry conditions**

Retry only after correcting or replacing the recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-21T10:44:25.997356059Z",
  "errors": [
    {
      "code": "validation.failure.fullName.not.matched",
      "message": "Your recipient's bank has a different name listed for these account details. Please double-check who you're sending money to.",
      "path": "account/name/fullName"
    }
  ]
}
```

The payment targets a personal Wise account in India, which is not supported for this transfer.

**HTTP status:** `400`

**What to do**

Correct or replace the recipient details using the current recipient requirements.

**Retry conditions**

Retry only after correcting or replacing the recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-26T11:21:13.567305076Z",
  "errors": [
    {
      "code": "validation.failure.india.balance.personal.not.allowed",
      "message": "Sending to Indian customers Wise account is not allowed. Please use local bank details instead.",
      "path": "account/type",
      "arguments": [
        "balance"
      ]
    }
  ]
}
```

The recipient name does not meet the character restrictions for the Malaysian local payment route.

**HTTP status:** `400`

**What to do**

Correct or replace the recipient details using the current recipient requirements.

**Retry conditions**

Retry only after correcting or replacing the recipient.

**Example error response**

```json
{
  "timestamp": "2026-08-23T09:02:23.238972946Z",
  "errors": [
    {
      "code": "validation.failure.malaysianlocal.fullName.format.not.valid",
      "message": "This recipient name contains invalid characters. Please use latin characters only.",
      "path": "account/name/fullName",
      "arguments": [
        "John Doe"
      ]
    }
  ]
}
```

The first address line fails a length or character constraint. Use the returned message to identify which constraint applies.

**HTTP status:** `400`

**What to do**

Use the returned `path` to correct the originator record. Keep the same originator reference for that originator.

**Retry conditions**

Retry after correcting the originator data.

**Example error response**

Length constraint
```json
{
  "timestamp": "2026-08-25T07:45:30.267047402Z",
  "errors": [
    {
      "code": "validation.failure.originator.address.firstLine.not.valid",
      "message": "Originator address first line must be between 1 and 250 characters in length",
      "path": "originator.address.firstLine",
      "arguments": [
        "Very long first line address here..."
      ]
    }
  ]
}
```

Character constraint
```json
{
  "timestamp": "2026-08-26T03:35:17.023346694Z",
  "errors": [
    {
      "code": "validation.failure.originator.address.firstLine.not.valid",
      "message": "Originator address first line contains invalid characters",
      "path": "originator.address.firstLine",
      "arguments": [
        "16, Wrong characters806\n"
      ]
    }
  ]
}
```

The originator's state or region is not valid for the supplied country.

**HTTP status:** `400`

**What to do**

Use the returned `path` to correct the originator record. Keep the same originator reference for that originator.

**Retry conditions**

Retry after correcting the originator data.

**Example error response**

```json
{
  "timestamp": "2026-08-21T12:26:02.480755914Z",
  "errors": [
    {
      "code": "validation.failure.originator.address.stateCode.not.valid",
      "message": "Originator address state invalid for the given country",
      "path": "originator.address.stateCode",
      "arguments": [
        "NS"
      ]
    }
  ]
}
```

The following validation identifiers are also documented for this endpoint:

Wise cannot find the quote referenced by the current `quote` request field. The response code retains the older term `quoteId`.

**What to do**

- Verify the quote ID, profile, environment, and validity.
- Create a new quote when the original quote is no longer valid.
- Continue to send the current `quote` property. Do not add a `quoteId` request property.


**Retry conditions**

Retry with a valid quote.

The required `quote` value is absent or invalid. The response code retains the older term `quoteId`.

**What to do**

- Supply the current `quote` property with a quote that belongs to the transfer context.
- Validate that your request builder does not omit or rename the property.


**Retry conditions**

Retry after correcting `quote`.

Wise cannot find the recipient referenced by `targetAccount`.

**What to do**

- Verify the recipient ID and profile.
- Create the required recipient before creating the transfer.


**Retry conditions**

Retry with a recipient available to the authenticated profile.

The required recipient ID is absent or invalid. The response code retains `targetAccountId`, but the current request field is `targetAccount`.

**What to do**

- Supply `targetAccount` using a recipient available to the authenticated profile.
- Do not add a `targetAccountId` request property.


**Retry conditions**

Retry after correcting `targetAccount`.

The partner-provided `originalTransferId` is missing, blank, or outside its supported length.

**What to do**

- Supply a stable identifier that meets the operation requirements.
- Store the identifier before sending the request.


**Retry conditions**

Reuse the same `originalTransferId` when retrying the same uncertain request. Generate a new one only for a different logical transfer.

The `details` object is missing or is not valid for the selected route.

**What to do**

- Retrieve the current requirements for the transfer route.
- Provide the required `details` object and correct its nested fields.


**Retry conditions**

Retry after correcting the transfer details.

The recipient-facing `details.reference` is missing, too long, or uses unsupported formatting.

**What to do**

- Ask the sender for a valid reference.
- Enforce the current character and length rules before submitting the transfer.


**Retry conditions**

Retry after correcting `details.reference`.

The required `originator` object is missing or invalid.

**What to do**

- Supply the complete originator object.
- Rebuild the object using the requirements for the current legal entity type.


**Retry conditions**

Retry after correcting the originator.

The `originator.legalEntityType` value is missing or unsupported.

**What to do**

- Submit an allowed legal entity type.
- Rebuild the dependent originator fields for that type.


**Retry conditions**

Retry after correcting `originator.legalEntityType`.

The required `originator.name` data is missing or invalid.

**What to do**

- For a private originator, provide the required name parts.
- For a business originator, provide the full legal name.


**Retry conditions**

Retry after correcting `originator.name`.

The private originator's `dateOfBirth` is not valid.

**What to do**

- Supply a valid date in the documented format.
- Validate the date before submitting the transfer.


**Retry conditions**

Retry after correcting `originator.dateOfBirth`.

The originator reference is missing or invalid. The response code retains `externalId`, but the current request field is `originator.reference`.

**What to do**

- Supply a stable `originator.reference`.
- Use the same reference for subsequent transfers from that originator.
- Do not add an `originator.externalId` request property.


**Retry conditions**

Retry after correcting `originator.reference`.

The required `originator.address` object is missing or invalid.

**What to do**

- Supply the complete address.
- Collect and validate the country-specific address fields before submitting the transfer.


**Retry conditions**

Retry after correcting the originator address.

The originator's city is required but missing.

**What to do**

- Supply the originator's city.
- Check the mapping from your stored address to the Wise request.


**Retry conditions**

Retry after adding `originator.address.city`.

The originator's city is blank, malformed, or too long.

**What to do**

- Correct the city using the operation's current character and length constraints.


**Retry conditions**

Retry after correcting `originator.address.city`.

The originator country is missing or is not a valid ISO 3166-1 alpha-2 code. The response code retains `countryIso2Code`, but the current request field is `originator.address.countryCode`.

**What to do**

- Submit a valid two-letter `countryCode`.
- Do not add a `countryIso2Code` request property.


**Retry conditions**

Retry after correcting `originator.address.countryCode`.

The account currency is missing or is not a valid ISO 4217 alpha-3 code for the account type.

**What to do**

- Submit a supported three-letter currency code using the current request schema.
- Check the recipient requirements for the selected route.


**Retry conditions**

Retry after correcting the currency or recipient.

The recipient does not meet the requirements for the selected payment route.

**What to do**

- Check the current recipient requirements.
- Update or recreate the recipient with the missing information.


**Retry conditions**

Retry the transfer after correcting the recipient.

Wise cannot process the request body.

**What to do**

- Compare the request with the current operation schema.
- Correct the request structure and values.


**Retry conditions**

Do not retry the unchanged request.

## Retrieve a third-party transfer

**Endpoint:** `GET /profiles/{profileId}/third-party-transfers/{transferId}`

See the [retrieve a third-party transfer operation](/api-reference/third-party-transfer/getthirdpartytransfer) for the current schema.

Wise cannot find the third-party transfer in the supplied profile context.

**HTTP status:** `404`

**What to do**

Verify the transfer ID, profile, environment, and access context.

**Retry conditions**

Retry only after correcting the lookup context.

**Example error response**

```json
{
  "status": 404,
  "message": "Third-party transfer not found: profileId=1234 transferId=124123123",
  "code": "not.found"
}
```

A service failure prevented Wise from retrieving the third-party transfer. The code does not identify a specific cause.

**HTTP status:** `500`

**What to do**

Reconcile the transfer using `originalTransferId`, then record the response and request identifier for investigation.

**Retry conditions**

Do not automatically retry an unexplained service failure. If a transient cause is confirmed, retry the lookup with bounded backoff and the same `originalTransferId`.

**Example error response**

```json
{
  "status": 500,
  "message": "Internal Server Error",
  "code": "thirdpartypayment.client.failure"
}
```

## Retry transfer operations

- Correct validation, quote, recipient, originator, and state errors before retrying.
- Obtain a valid token before retrying authentication errors.
- Follow `Retry-After` for `429` responses.
- Retry transient service failures and timeouts with exponential backoff and jitter.
- Reuse the same idempotency identifier for the same logical transfer.
- Reconcile the transfer after any response where the outcome is uncertain.


For shared response formats and safe fallbacks, see the [error handling overview](/guides/developer/errors).