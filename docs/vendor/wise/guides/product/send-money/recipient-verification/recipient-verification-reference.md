# Recipient verification reference

Recipient verification behaviour and outcomes.

## Supported recipient types

The following currencies and corresponding recipient types currently support recipient verification. Wise is adding support for more currencies soon.

| Currency | Recipient type | `type` value |
|  --- | --- | --- |
| CNY | Chinese Alipay | `chinese_alipay` |
| EUR | IBAN (SEPA-reachable) | `iban` |
| IDR | Indonesian local bank | `indonesian` |
| INR | Indian bank account | `indian` |
| INR | Indian UPI | `indian_upi` |
| KRW | South Korean (personal) | `south_korean_paygate` |
| KRW | South Korean (business) | `south_korean_paygate_business` |


**Availability notes**:

- **EUR**: EUR recipient verification is currently available to Embedded and Enterprise partners when making payments to a SEPA account only. Correspondent partner support is planned for a future release.


## Verification behaviour

This table describes which type of verification occurs (account existence or name matching) and which fields are submitted to the verification provider. Note that for currencies that support `NAME_MATCHING`, account existence is implied.

| Currency | Recipient type | Verification type | Fields checked |
|  --- | --- | --- | --- |
| CNY | `chinese_alipay` | `ACCOUNT_EXISTENCE` | `accountNumber`, `name/fullName` |
| EUR | `iban` | `NAME_MATCHING` | `iban`, `name/fullName` |
| IDR | `indonesian` | `NAME_MATCHING` | `bankCode`, `accountNumber`, `name/fullName` |
| INR | `indian` | `NAME_MATCHING` | `ifscCode`, `accountNumber`, `name/fullName` |
| INR | `indian_upi` | `NAME_MATCHING` | `accountNumber`, `name/fullName` |
| KRW | `south_korean_paygate` | `ACCOUNT_EXISTENCE` | `bankCode`, `accountNumber` |
| KRW | `south_korean_paygate_business` | `ACCOUNT_EXISTENCE` | `bankCode`, `accountNumber` |


**Behaviour notes**:

- **CNY**: The Alipay ID and name are submitted together as a combined unit and the provider confirms whether the pair is valid. As there is no separate name matching, Wise returns `ACCOUNT_EXISTENCE` as the `outcomes.type` for CNY.
  - If the check fails, the recipient is not created (blocking error) and the error will not indicate whether the ID or name is incorrect. Ensure that you prompt the customer to verify both the Alipay ID and registered name if a blocking error occurs.
- **EUR**: Name-matching tolerance is more strict when the recipient `legalType` is `PRIVATE`. When the recipient `legalType` is `BUSINESS`, name matching is more lenient, making room for common legal abbreviations (for example, "GmbH", "S.A.", etc).


## Non-blocking outcomes

The table below documents which outcome values are supported by currency. The `COULD_NOT_CHECK` outcome value is possible for all currencies when the external provider is unavailable or times out.

| Currency | Recipient type | `SUCCESS`  | `PARTIAL_FAILURE`  | `FAILURE`  | `COULD_NOT_CHECK`  |
|  --- | --- | --- | --- | --- | --- |
| CNY | `chinese_alipay` | ✓  | —  | —  | ✓  |
| EUR | `iban` | ✓  | ✓  | ✓  | ✓  |
| IDR | `indonesian` | ✓  | ✓  | —  | ✓  |
| INR | `indian` | ✓  | ✓  | ✓  | ✓  |
| INR | `indian_upi` | ✓  | ✓  | ✓  | ✓  |
| KRW | `south_korean_paygate` | ✓  | —  | —  | ✓  |
| KRW | `south_korean_paygate_business` | ✓  | —  | —  | ✓  |


**Notes about outcomes**:

- **CNY**:
  - A failed combined account-and-name check results in a blocking outcome (recipient not created).
- **IDR**:
  - Account not found and account closed are both blocking outcomes (recipient not created).
  - All name discrepancies return `PARTIAL_FAILURE`, regardless of how close or how different the submitted name is from the registered name. There is no distinction between a minor mismatch and a complete mismatch at the API level.


## Blocking outcomes

Blocking outcomes occur when the verification provider definitively confirms that the submitted details are invalid. The recipient resource is not created, and you must correct the input and retry the `POST /accounts` request.

Blocking errors follow the same format as field validation errors:

```json
{
  "errors": [
    {
      "code": "INVALID_ACCOUNT_NOT_EXIST",
      "path": "account/details/accountNumber",
      "message": "The account number does not exist."
    }
  ]
}
```

| Currency | Recipient type  | Trigger condition  | Error code & path  |
|  --- | --- | --- | --- |
| CNY | `chinese_alipay` | Alipay provider confirms the account and name pair is invalid. | code: `ALIPAY_ACCOUNT_NUMBER_NOT_MATCHED`
path: `account/details/accountNumber` |
| EUR | `iban` | *No blocking outcomes. All verification results are non-blocking.* | n/a |
| IDR | `indonesian` | Provider confirms account does not exist at the given bank. | code: `INVALID_ACCOUNT_NOT_EXIST`
path: `details/accountNumber` |
| IDR | `indonesian` | Provider confirms account exists but is closed. | code: `INVALID_ACCOUNT_ACCOUNT_CLOSED`
path:`details/accountNumber` |
| INR | `indian` | Bank confirms account number is invalid. | code: `INVALID_ACCOUNT_NUMBER`
path: `details/accountNumber` |
| INR | `indian` | Bank confirms account number or IFSC code is invalid. | code: `INVALID_ACCOUNT_DETAILS`
path: `details/accountNumber` |
| INR | `indian` | Bank confirms IFSC code is invalid or the bank does not accept payments. | code: `INVALID_IFSC_CODE`
path: `details/ifscCode` |
| INR | `indian_upi` | UPI provider confirms the VPA is invalid/does not exist, or the provided name does not match the name on the account. | code: `INVALID_UPI_ID`
path: `details/accountNumber` |
| KRW | `south_korean_paygate` | Provider confirms account number is not valid for the given bank. | code: `INVALID_ACCOUNT_BANK_PAIR`
path: `account/details/accountNumber` |
| KRW | `south_korean_paygate_business` | Provider confirms account number is not valid for the given bank. | code: `INVALID_ACCOUNT_BANK_PAIR`
path: `account/details/accountNumber` |


## Other currency-specific notes

### EUR

**EEA versus non-EEA partners**

The `requiresCustomerAcceptance` behaviour differs depending on whether the partner is established within the EEA:

- **EEA partners** are partners within the European Economic Area subject to EU Regulation 2024/886.
  - If `requiresCustomerAcceptance` is `true` for `PARTIAL_FAILURE` and `FAILURE` outcomes, it requires explicit customer acknowledgement before a transfer can proceed.
- **Non-EEA partners** are not subject to verification of payee (VoP) risk acceptance requirements and so `requiresCustomerAcceptance` is always `false` for non-SUCCESS outcomes. The recipient is usable without explicit customer acceptance, regardless of the outcome.


**Verification occurs per payment, not per recipient**

For EEA partners, VoP checks are required at the point of initiating each individual payment, not only at recipient creation.

Wise provides a [compatibility endpoint](/api-reference/recipient/recipientcompatibilitycheck) to allow re-verification. EEA partners must call this endpoint to confirm compatibility for each transfer:

```
GET /accounts/{accountId}/quote/{quoteId}/compatibility
```

This endpoint runs the VoP check against an existing recipient without requiring a new `POST /accounts` request, which is also useful for previously created EUR recipients (for example, those created before VoP was active).

### IDR

**Suggested name corrections via `recommendedUpdates`**

Where the provider returns a suggested correction to the submitted name, this is available in the `outcomes.recommendedUpdates` field. You can use this value to pre-populate a correction prompt for the customer. The `resolvedName` field is not populated for IDR.