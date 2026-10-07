# Recipient creation by target currency

This section provides a condensed, corridor-by-corridor reference for the most common target currencies in Correspondent Send flows. Each section includes the recipient `type`, required `details` fields, a sample JSON payload, and any special handling notes.

Important!
These examples represent the most common *local* recipient type per currency. Some currencies support additional types (`swift_code`, `iban`, etc).

For correspondent partners, Wise recommends blocking global currency recipient types (`swift_code` for USD, EUR, GBP; non-local IBANs for GBP and EUR) unless your agreement explicitly includes them. Always verify current requirements using the [account requirements endpoint](/api-reference/recipient/recipientaccountrequirementsget).

## EMEA

GBP
| Field | Value |
|  --- | --- |
| `type` | `sort_code` |
| `details.sortCode` | UK sort code (6 digits) |
| `details.accountNumber` | UK account number |
| Address required? | No |


Verification performed: Field formatting + sort code validity check + name matching (GBP Confirmation of Payee)

Special notes:

- Also supports `iban` type for GB IBANs.
- Block non-GB IBANs for local-only scope.
- Reference field limit: 18 characters.


```json
{
  "currency": "GBP",
  "type": "sort_code",
  "profile": {{profileId}},
  "accountHolderName": "Jane Smith",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "sortCode": "231470",
    "accountNumber": "28821822"
  }
}
```

EUR
| Field | Value |
|  --- | --- |
| `type` | `iban` |
| `details.iban` | SEPA IBAN |
| `details.bic` | Not required (resolved by Wise from IBAN) |
| Address required? | No |


Verification performed: IBAN format + validity check. Account existence check planned (Phase 3).

Special notes:

- Block non-local SEPA IBANs and `swift_code` type for local-only scope.
- SEPA Instant limit: €100k.
- SEPA standard limit: €6m.
- Reference field limit: 35 characters. |


```json
{
  "currency": "EUR",
  "type": "iban",
  "profile": {{profileId}},
  "accountHolderName": "Hans Mueller",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "iban": "DE89370400440532013000"
  }
}
```

AED
| Field | Value |
|  --- | --- |
| `type` | `emirates` |
| `details.iban` | UAE IBAN (23 characters) |
| Address required? | No |


Verification performed: Field formatting checks.

Special notes:

- Transfer purpose is required on the *transfer* (keys: `GDI`, `GDE`, `IFS`, `STR`, `TOF`, `OAT`, `CHC`).
- Reference field limit: 35 characters.


```json
{
  "currency": "AED",
  "type": "emirates",
  "profile": {{profileId}},
  "accountHolderName": "Fatima Al Maktoum",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "iban": "AE410035161858974862233"
  }
}
```

IBAN-based
The following currencies all use `type: iban` with `details.iban` in the `details` object. No address is required.

| Currency | Notes |
|  --- | --- |
| CHF | Only LI and CH country IBANs supported. Max: CHF 250m. |
| BGN | — |
| DKK | — |
| NOK | Max: NOK 1B. |
| SEK | Max: SEK 1B. |
| PLN | Max: PLN 5m. |
| PKR | — |
| RON | — |


```json
{
  "currency": "CHF",
  "type": "iban",
  "profile": {{profileId}},
  "accountHolderName": "Stefan Brunner",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "iban": "CH9300762011623852957"
  }
}
```

## APAC

INR
| Field | Value |
|  --- | --- |
| `type` | `indian` |
| `details.ifscCode` | IFSC code (11 characters) |
| `details.accountNumber` | Indian bank account number |
| Address required? | No |


Verification performed: IFSC validity check + account existence check + name matching (live).

Special notes:

- Also supports `indian_upi` type (UPI VPA) — check your corridor scope.
- Transfer purpose is required for INR transfers.
- Taxes (TCS) may apply.
- Reference field limit: 35 characters.


```json
{
  "currency": "INR",
  "type": "indian",
  "profile": {{profileId}},
  "accountHolderName": "Priya Sharma",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "ifscCode": "HDFC0001234",
    "accountNumber": "50100123456789"
  }
}
```

SGD
| Field | Value |
|  --- | --- |
| `type` | `singapore` |
| `details.bic` | SWIFT/BIC of the recipient bank (converted to `bankCode` internally by Wise) |
| `details.accountNumber` | Singapore bank account number |
| Address required? | No |


Verification performed: Field formatting checks. Account existence via proxy (limited).

Special notes:

- Also supports `singapore_paynow` type.
- `bankCode` field is not required if `bic` is provided.
- FAST limit: SG$200k (direct connection).
- PayNow limit: SG$2m.
- Reference field limit: 35 characters.


```json
{
  "currency": "SGD",
  "type": "singapore",
  "profile": {{profileId}},
  "accountHolderName": "Wei Lin Tan",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bic": "DBSSSGSGXXX",
    "accountNumber": "1234567890"
  }
}
```

HKD
| Field | Value |
|  --- | --- |
| `type` | `hongkong` |
| `details.bic` | SWIFT/BIC of the recipient bank |
| `details.accountNumber` | HK bank account number |
| Address required? | No (was shown as "New Field" in some partner implementations, check account-requirements) |


Verification performed: Branch code validity + account existence check (FPS).

Special notes:

- Also supports `hong_kong_fps` type (FPS ID, email, or mobile number).
- FPS limit: HK$1m.
- Autopay limit: HK$10m.
- Domestic HK→HK payouts may not be supported under certain MSO licenses — check your regulatory scope.
- Reference field limit: 35 characters.


```json
{
  "currency": "HKD",
  "type": "hongkong",
  "profile": {{profileId}},
  "accountHolderName": "Wei Lin Tan",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bic": "HABORSC1XXX",
    "accountNumber": "231289112"
  }
}
```

MYR
| Field | Value |
|  --- | --- |
| `type` | `malaysian` |
| `details.swiftCode` | SWIFT/BIC of the Malaysian bank |
| `details.accountNumber` | Malaysian bank account number |
| Address required? | No |


Verification performed: Account number format check + name format check. DuitNow proxy validity check available.

Special notes:

- DuitNow proxy type may also be available.
- Reference field limit: 35 characters.


```json
{
  "currency": "MYR",
  "type": "malaysian",
  "profile": {{profileId}},
  "accountHolderName": "Ahmad bin Ibrahim",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "swiftCode": "RHBBMYKLXXX",
    "accountNumber": "1234567890"
  }
}
```

AUD
| Field | Value |
|  --- | --- |
| `type` | `australian` |
| `details.bsbCode` | BSB code (6 digits) |
| `details.accountNumber` | Australian bank account number |
| Address required? | No (but required when *source* currency is AUD) |


Verification performed: BSB validity check + bank-level account number length check. Name matching via PayID (live for Wise.com, Phase 3 for WP).

Special notes:

- Max payout: AUD 1.5m (local).
- Reference field limit: 18 characters.


```json
{
  "currency": "AUD",
  "type": "australian",
  "profile": {{profileId}},
  "accountHolderName": "Sarah Collins",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bsbCode": "802985",
    "accountNumber": "12345678"
  }
}
```

PHP
| Field | Value |
|  --- | --- |
| `type` | `philippines` |
| `details.bic` | SWIFT/BIC of the Philippine bank (converted to `bankCode` internally) |
| `details.accountNumber` | Philippine bank account number |
| `details.address` | **Required** (recipient address) |
| Address required? | **Yes** (fields) |


Verification performed: Field formatting checks only. Account existence planned (Phase 3).

Special notes:

- Transfer purpose is required on the *transfer* (not the recipient).
- Instapay limit: ₱50k.
- PESONet limit: up to ₱9m (residency dependent).
- Payment purpose required for transfers >₱500k.
- Reference field limit: 35 characters.


```json
{
  "currency": "PHP",
  "type": "philippines",
  "profile": {{profileId}},
  "accountHolderName": "Maria Santos",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bic": "ABORPHPHXXX",
    "accountNumber": "0044123456",
    "address": {
      "country": "PH",
      "city": "Manila",
      "firstLine": "123 Rizal Ave",
      "postCode": "1000"
    }
  }
}
```

THB
| Field | Value |
|  --- | --- |
| `type` | `thailand` |
| `details.bic` | SWIFT/BIC of the Thai bank (converted to `bankCode` internally) |
| `details.accountNumber` | Thai bank account number |
| `details.address` | **Required** (recipient address including state) |
| Address required? | **Yes** (fields) |


Verification performed: Bank-level account number length check + name format check. Account existence check planned (Phase 2).

Special notes:

- Transfer purpose is required on the *transfer*.
- Max payout: THB 2m.
- Email is mandatory for Wise.com recipients (as of Feb 2026) — check if your agreement requires it.
- Reference field limit: 35 characters.


```json
{
  "currency": "THB",
  "type": "thailand",
  "profile": {{profileId}},
  "accountHolderName": "Somchai Prasert",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bic": "KASITHBKXXX",
    "accountNumber": "1234567890",
    "address": {
      "country": "TH",
      "city": "Bangkok",
      "firstLine": "456 Sukhumvit Rd",
      "postCode": "10110",
      "state": "Bangkok"
    }
  }
}
```

JPY
| Field | Value |
|  --- | --- |
| `type` | `japanese` |
| `details.bankCode` | 4-digit Zengin bank code |
| `details.branchCode` | 3-digit branch code |
| `details.accountNumber` | 7-digit account number |
| `details.accountType` | `CHECKING`, `SAVINGS`, etc. |
| Address required? | No |


Verification performed: Branch code validity + account number and name validity check (Zengin).

Special notes:

- **Critical**: Recipient name must match the name on the Japanese bank account *exactly* — typically in **カタカナ (katakana)**, not romaji. Mismatches are the primary cause of JPY rejections. Display a banner in your UI instructing customers to enter the name as it appears on the recipient's Japanese bank account.
- Also supports `swift_code` type (for Swift payout, different field set).
- Reference field limit: 35 characters.


```json
{
  "currency": "JPY",
  "type": "japanese",
  "profile": {{profileId}},
  "accountHolderName": "タナカ タロウ",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bankCode": "0005",
    "branchCode": "001",
    "accountNumber": "1234567",
    "accountType": "CHECKING"
  }
}
```

IDR
| Field | Value |
|  --- | --- |
| `type` | `indonesian` |
| `details.bankCode` | Indonesian bank code |
| `details.accountNumber` | Indonesian bank account number |
| Address required? | No |


Verification performed: Bank-level account number length check + bank code validity + account existence check + name matching (live).

Special notes:

- Transfer purpose is required on the *transfer*.
- Reference field limit: 35 characters.


```json
{
  "currency": "IDR",
  "type": "indonesian",
  "profile": {{profileId}},
  "accountHolderName": "Budi Santoso",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bankCode": "014",
    "accountNumber": "1234567890"
  }
}
```

KRW
| Field | Value |
|  --- | --- |
| `type` | `swift_code` (most common for correspondent partners), also supports `south_korean` (via local) |
| `details.swiftCode` | SWIFT/BIC of the Korean bank (8–11 characters) |
| `details.accountNumber` | Korean bank account number |
| `details.phoneNumber` | Recipient phone number (required as of Nov 2025) |
| Address required? | No |


Verification performed: Bank code validity + account existence check + name matching (live).

Special notes:

- Transfer purpose is required on the *transfer*.
- `phoneNumber` is a **new mandatory field** added Nov 2025.
- Max payout: KRW 1B.
- Reference field limit: 35 characters.


```json
{
  "currency": "KRW",
  "type": "swift_code",
  "profile": {{profileId}},
  "accountHolderName": "Kim Minjun",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "swiftCode": "KOABORSCXXX",
    "accountNumber": "853229317",
    "phoneNumber": "+82-2-1234-5678"
  }
}
```

## North & South America

USD
| Field | Value |
|  --- | --- |
| `type` | `aba` |
| `details.abartn` | ABA routing number (9 digits) |
| `details.accountNumber` | US bank account number |
| `details.accountType` | `CHECKING` or `SAVINGS` |
| `details.address` | **Required** (US address: `country`, `state`, `city`, `firstLine`, `postCode`) |


Verification performed: Routing number validity check + name format check. Account existence check planned (Phase 2).

Special notes:

- Address is also required when USD is the *source* currency (regulatory).
- Block `swift_code` type for local-only scope.
Reference field limit: 35 characters.


```json
{
  "currency": "USD",
  "type": "aba",
  "profile": {{profileId}},
  "accountHolderName": "John Doe",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "abartn": "026009593",
    "accountNumber": "12345678",
    "accountType": "CHECKING",
    "address": {
      "country": "US",
      "state": "NY",
      "city": "New York",
      "firstLine": "123 Main St",
      "postCode": "10001"
    }
  }
}
```

CAD
| Field | Value |
|  --- | --- |
| `type` | `canadian` |
| `details.institutionNumber` | 3-digit institution number |
| `details.transitNumber` | 5-digit transit number |
| `details.accountNumber` | Canadian bank account number |
| `details.accountType` | `CHECKING` or `SAVINGS` |
| Address required? | No |


Verification performed: Institution number validity + transit number validity (lookup against institution).

Special notes:

- `interac` type also exists but is not supported for most 3PIP partners.
- Max payout: CAD 1B.
- Reference field limit: 35 characters.


```json
{
  "currency": "CAD",
  "type": "canadian",
  "profile": {{profileId}},
  "accountHolderName": "Jean Tremblay",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "institutionNumber": "006",
    "transitNumber": "04841",
    "accountNumber": "1234567",
    "accountType": "CHECKING"
  }
}
```

BRL
| Field | Value |
|  --- | --- |
| `type` | `brazil` |
| `details.bankCode` | Brazilian bank code |
| `details.branchCode` | Branch code (4–5 characters) |
| `details.accountNumber` | Account number (4–12 characters) |
| `details.accountType` | `CHECKING` or `SAVINGS` |
| `details.cpf` | CPF (tax ID) for personal recipients |
| `email` | **Effectively required** for B2C and C2C >10k BRL (see notes) |
| Address required? | No |


Verification performed: Field formatting checks. Account existence via PIX (internal, Wise.com only currently).

Special notes:

- **`email` field**: Although account-requirements may mark it optional, BRL B2C transfers and C2C transfers over R$10k **will fail without it**. Hardcode as required.
- Transfer nature (`paymentMetadata.transferNature`) must be set on the *quote* — different values for B2B vs B2C.
- IOF tax display (VET — total effective rate) is a regulatory requirement.
- PIX limit: R$250k individual / R$15k business recipient.
- TED limit: same.
- Reference field limit: 20 characters.


```json
{
  "currency": "BRL",
  "type": "brazil",
  "profile": {{profileId}},
  "accountHolderName": "Ana Oliveira",
  "email": "ana.oliveira@example.com",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "bankCode": "001",
    "branchCode": "1234",
    "cpf": "12345678901",
    "accountNumber": "12345678",
    "accountType": "CHECKING"
  }
}
```

## Africa

ZAR
| Field | Value |
|  --- | --- |
| `type` | `southafrica` |
| `details.swiftCode` | SWIFT/BIC of the South African bank |
| `details.accountNumber` | SA bank account number |
| `details.dateOfBirth` | **Required** for personal recipients (format: `YYYY-MM-DD`) |
| Address required? | No |


Verification performed: Field formatting checks.

Special notes:

- **`dateOfBirth`** is mandatory for personal (PRIVATE) recipients as of late 2025.
- Business recipients require `zarIdentificationNumber` (business registration number).
- Transfers >ZAR 176k automatically route via Swift.
- Reference field limit: 18 characters.


```json
{
  "currency": "ZAR",
  "type": "southafrica",
  "profile": {{profileId}},
  "accountHolderName": "Thabo Mbeki",
  "ownedByCustomer": false,
  "details": {
    "legalType": "PRIVATE",
    "swiftCode": "ABSAZAJJXXX",
    "accountNumber": "9012345678",
    "dateOfBirth": "1990-01-15"
  }
}
```

## Summary of recipient-level special handling

| Condition | Action |
|  --- | --- |
| Target is USD, PHP, THB, or TRY | Recipient `details.address` object is **required**. |
| Source is USD or AUD | Recipient `details.address` object is **required**. |
| Target is BRL (B2C or C2C >10k) | Treat `email` as **required** on the recipient, even if account requirements say optional. |
| Target is ZAR (personal) | `details.dateOfBirth` is **required**. |
| Target is ZAR (business) | `details.zarIdentificationNumber` is **required**. |
| Target is KRW | `details.phoneNumber` is **required** (since Nov 2025). |
| Target is JPY (local/Zengin) | `accountHolderName` must be in **katakana** exactly as registered at the bank. |
| Target is GBP, EUR, or USD (local) | Block `swift_code` type and non-local IBANs unless global currencies are in scope. |
| CNY via Alipay | Requires specific configuration and Chinese character support for `accountHolderName`. Account requirements differ by sender type (personal vs business). |