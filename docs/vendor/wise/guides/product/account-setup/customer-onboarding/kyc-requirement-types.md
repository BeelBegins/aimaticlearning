# KYC requirement types

This page describes the submission data structure and accepted values for each KYC requirement type supported by the [Submit a KYC Requirement](/api-reference/kyc-review/kycreviewrequirementsubmit) endpoint, and any additional [attributes](/api-reference/kyc-review/kyc-requirement#path=attributes) returned on the requirement object.

## Supported requirement types

| Requirement key | Description | Attributes |
|  --- | --- | --- |
| [`ACCOUNT_INTENT`](#account_intent) | The intended use of the account. |  |
| [`ACCOUNT_PURPOSE`](#account_purpose) | The purpose of the account. |  |
| [`ANNUAL_VOLUME`](#annual_volume) | A rough estimate of the yearly volume intending to be sent or received. |  |
| [`BUSINESS_ANNUAL_INCOME`](#business_annual_income) | Annual income of the business. |  |
| [`BUSINESS_AUTHORISATION_ID`](#business_authorisation_id) | Business authorisation identification. |  |
| [`BUSINESS_AUTHORISATION_LETTER`](#business_authorisation_letter) | Business authorisation letter. |  |
| [`BUSINESS_CONTROLLING_PERSON`](#business_controlling_person) | Declare exactly one shareholder as the person who controls the business. |  |
| [`BUSINESS_DIRECTORS_CHECK`](#business_directors_check) | Business directors check. |  |
| [`BUSINESS_INCOME_CLASSIFICATION`](#business_income_classification) | The business's Common Reporting Standard (CRS) classification. |  |
| [`BUSINESS_MONTHLY_VOLUME`](#business_monthly_volume) | Estimated monthly volumes the business intends to send or receive. |  |
| [`BUSINESS_REGISTRATION_DOCS`](#business_registration_docs) | Business registration documents. |  |
| [`BUSINESS_SHAREHOLDER_CONTACT_DETAILS`](#business_shareholder_contact_details) | Email addresses for all current shareholders. |  |
| [`BUSINESS_SHAREHOLDERS_CHECK`](#business_shareholders_check) | Business shareholders check. |  |
| [`BUSINESS_SOURCE_OF_WEALTH`](#business_source_of_wealth) | Source of wealth for the business. |  |
| [`BUSINESS_SOURCE_OF_WEALTH_INFO`](#business_source_of_wealth_info) | Source of wealth information. |  |
| [`BUSINESS_SOURCE_OF_WEALTH_PROOF`](#business_source_of_wealth_proof) | Proof of source of wealth. |  |
| [`BUSINESS_ULTIMATE_BENEFICIAL_OWNER_ID`](#business_ultimate_beneficial_owner_id) | Ultimate beneficial owner identification. | `requiredUbos` |
| [`BUSINESS_USE_CASE`](#business_use_case) | How the business intends to use the Wise account. |  |
| [`ID_DOCUMENT`](#id_document) | Identity document (passport, ID card, driver's licence, etc.). |  |
| [`INCOME`](#income) | Approximate gross yearly income. |  |
| [`INDIA_TRANSFER_PURPOSE`](#india_transfer_purpose) | Purpose for transfers from INR to one of GBP, USD, EUR, AUD, CAD, SGD. |  |
| [`JPN_BUSINESS_CERT`](#jpn_business_cert) | Certificate of Registered Matters for Japanese corporation. |  |
| [`JPN_PERSONAL_MYNUMBER`](#jpn_personal_mynumber) | Proof of Individual Number for Japan-resident customers. |  |
| [`LEGAL_ENTITY_SHAREHOLDER`](#legal_entity_shareholder) | Legal entity owners of the business. |  |
| [`PROOF_OF_TRADING_ADDRESS`](#proof_of_trading_address) | Proof of trading address. |  |
| [`SOURCE_OF_FUNDS`](#source_of_funds) | Source of funds. |  |
| [`SOURCE_OF_WEALTH`](#source_of_wealth) | Source of wealth. |  |
| [`SOURCE_OF_WEALTH_INFO`](#source_of_wealth_info) | Source of wealth information. |  |
| [`SOURCE_OF_WEALTH_PROOF`](#source_of_wealth_proof) | Proof of source of wealth. |  |
| [`TAX_RESIDENCY`](#tax_residency) | Tax residency declaration. |  |
| [`USE_CASE_COUNTRIES`](#use_case_countries) | Countries the account will be used with. |  |


## ACCOUNT_INTENT

How the customer intends to use their Wise account.

Request Fields
files
Not required

submissionData.data.accountIntent
Accepted values for personal profiles:

- `CONTRIBUTING_TO_PERSONAL_SAVINGS`
- `GENERAL_MONTHLY_LIVING_EXPENSES`
- `INVESTING_IN_FUNDS_STOCKS_BONDS_OPTIONS_FUTURES_OR_OTHER`
- `PAYING_FOR_GOODS_OR_SERVICES_ABROAD`
- `PAYING_RENT_MORTGAGE_BANK_LOAN_INSURANCE_CREDIT`
- `PAYING_RENT_UTILITIES_OR_PROPERTY_CHARGES`
- `RECEIVE_SALARY_IN_DIFFERENT_CURRENCY`
- `RECEIVE_PENSION_IN_DIFFERENT_CURRENCY`
- `SENDING_MONEY_REGULARLY_TO_FAMILY`
- `SENDING_MONEY_TO_MY_OWN_ACCOUNT_TO_BENEFIT_FROM_EXHCANGE_RATE`
- `EDD_BORDERLESS_PERSONAL_RECEIVING_SALARY_IN_DIFFERENT_CURRENCY`
- `EDD_BORDERLESS_PERSONAL_RECEIVING_FINANCIAL_SUPPORT_FROM_FAMILY`
- `EDD_BORDERLESS_PERSONAL_RECEIVING_MONEY_FOR_FREELANCE_OR_CONTRACTOR_SERVICES`
- `EDD_BORDERLESS_PERSONAL_STORING_MONEY_TO_MANAGE_RATE_FLUCTUATION_RISK`
- `EDD_BORDERLESS_PERSONAL_USING_AS_LOCAL_BANK_ACCOUNT_IN_FOREIGN_COUNTRY`
- `EDD_BORDERLESS_PERSONAL_PAYING_FOR_RENT_MORTGAGE_BANK_LOAN_INSURANCE_CREDIT_CARD`


Accepted values for business profiles:

- `EDD_BORDERLESS_BUSINESS_PAYING_SUPPLIERS_CONTRACTORS_EMPLOYEES`
- `EDD_BORDERLESS_BUSINESS_PAYING_SUPPLIERS_CONTRACTORS_EMPLOYEES_AND_RECEIVING_MONEY_FOR_SERVICES`
- `PAYING_SUPPLIERS_CONTRACTORS_EMPLOYEES_AND_RECEIVING_MONEY_FOR_SERVICES`
- `INVESTING_IN_FUNDS_STOCKS_BONDS_OPTIONS_FUTURES_OR_OTHER`
- `DISTRIBUTING_COMPANY_PROFITS_OR_PAYING_DIVIDENDS`
- `PAYING_RENT_MORTGAGE_BANK_LOAN_INSURANCE_CREDIT`
- `PAYING_FOR_GOODS_SERVICES_ABROAD`
- `PAYING_RENT_UTILITIES_OR_PROPERTY_CHARGES`
- `PAYING_SUPPLIERS_CONTRACTORS_EMPLOYEES`
- `PAYING_TAX_ON_PROFIT_OR_PROPERTY`
- `TRANSFER_WITHIN_COMPANY_OR_GROUP`
- `EDD_BORDERLESS_BUSINESS_MAKING_INTRA_COMPANY_TRANSFERS`


submissionData example
```json
{
  "data": {
    "accountIntent": "PAYING_FOR_GOODS_OR_SERVICES_ABROAD"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## ACCOUNT_PURPOSE

The purpose of the account.

Request Fields
files
Not required

submissionData.data.accountPurpose
Accepted values:

- `SENDING_MONEY_TO_FRIENDS_OR_FAMILY`
- `MOVING_SAVINGS`
- `GENERAL_LIVING_EXPENSES`
- `BUYING_GOODS_OR_SERVICES_ABROAD`
- `PAYING_FOR_MORTGAGE_OR_LOAN`
- `PAYING_BILLS`
- `RECEIVING_SALARY_OR_PENSION`
- `INVESTING`


submissionData example
```json
{
  "data": {
    "accountPurpose": "SENDING_MONEY_TO_FRIENDS_OR_FAMILY"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## ANNUAL_VOLUME

A rough estimate of the yearly volume the customer intends to send or receive.

Request Fields
files
Not required

submissionData.data.amount
The estimated annual volume amount. Must be greater than zero.

submissionData.data.currency
The currency code (e.g. `USD`, `EUR`).

submissionData example
```json
{
  "data": {
	"amount": 10000.00,
	"currency": "USD"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_ANNUAL_INCOME

The organisation's approximate gross yearly income.

Request Fields
files
Not required

submissionData.data.amount
The gross yearly income amount. Must be greater than zero.

submissionData.data.currency
The currency code (e.g. `USD`, `EUR`).

submissionData example
```json
{
  "data": {
    "amount": 4500.00,
    "currency": "USD"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_AUTHORISATION_ID

The identification document of one company Director. This document is required to verify authorisation to act on the account on behalf of the organisation. It is only asked for if the Business Representative (the account creator) is not listed as a Director of the company.

Request Fields
files
Upload the identification document.

submissionData example
```json
{
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_AUTHORISATION_LETTER

A document authorising the Business Representative to act on the account on behalf of the organisation. When the Business Representative is also a Director, they are automatically authorised and this document is not needed.

The document must include:

- Business name, legal type, registration number, country of incorporation and registered address.
- Legal Representative's (the Director) name, date of birth, function in the company (such as Director), permission to act on behalf of the organisation and signature.
- Authorised Representative's (the Business Representative) name, date of birth, authority to act on the account and signature.
- Date of issue.


Request Fields
files
Upload the authorisation letter.

submissionData example
```json
{
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_CONTROLLING_PERSON

Declare exactly one shareholder as the person who controls the business and provide their business title.

Request Fields
files
Not required

submissionData.data.shareholderId
The ID of the shareholder declared as the controlling person. Required. Use the `id` returned by the [List UBOs](/api-reference/profile/profileubolist) endpoint.

submissionData.data.businessTitle
The controlling person's title or role in the business. Required.

Accepted values:

- `GENERAL_PARTNER`
- `FOUNDER`
- `CEO`
- `PRESIDENT`
- `MANAGING_DIRECTOR`
- `COO`
- `CFO`
- `TREASURER`
- `EXECUTIVE_DIRECTOR`
- `VICE_PRESIDENT`


submissionData example
```json
{
  "data": {
    "shareholderId": "7ff6c4998a59d71ad9834041727017d2",
    "businessTitle": "CEO"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_DIRECTORS_CHECK

Confirm the directors of the business. Directors can be members of the board of directors, general partners or part of executive management. If a director is another business, a document identifying the individuals directing that business is needed.

Request Fields
files
Upload the relevant documents.

submissionData example
```json
{
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_INCOME_CLASSIFICATION

Under the Common Reporting Standard (CRS), we are required to collect your business's tax classification based on how it earns income.

Depending on your selection, we may need to ask for additional information (such as tax details on controlling persons).

Request Fields
files
Not required

submissionData.data.classificationType
The business's CRS classification. Required.

Accepted values:

- `ACTIVE_NFE` - Active non-financial entity: more than 50% of the business's income comes from sales, services, donations, or grants.
- `PASSIVE_NFE` - Passive non-financial entity: more than 50% of the business's income comes from dividends, interest, rent, or royalties.
- `FI_INVESTMENT_ENTITY` - Financial institution (FI) that manages investment, hedge, or private equity funds, or is a foundation funded by investments.
- `FI_NON_INVESTMENT_ENTITY` - FI such as a bank, credit union, custodial institution, or similar.


submissionData example
```json
{
  "data": {
    "classificationType": "ACTIVE_NFE"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_MONTHLY_VOLUME

A rough estimate of the monthly volumes the business intends to send or receive and the main currency routes they will use.

Request Fields
files
Not required

submissionData.data.amount
The estimated monthly volume. Must be greater than zero.

submissionData.data.currency
The currency code (e.g. `USD`, `EUR`).

submissionData example
```json
{
  "data": {
    "amount": 4500.00,
    "currency": "USD"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_REGISTRATION_DOCS

Proof of Business Registration, such as a certificate of incorporation, articles of association, or an official registry excerpt. It should be the document on record with the local business or tax authority. It must show:

- The business name, identification number and full registered address.
- The directors, managers, partners, trustees or members of the executive board.
- The owners, members or shareholders and their respective holdings.


If any of the above information has changed since formation, upload a document showing the most up to date details.

Request Fields
files
Upload the registration documents.

submissionData example
```json
{
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_SHAREHOLDER_CONTACT_DETAILS

Provide contact details, including email addresses for all current shareholders of the business. Submit all contact details in a single request, requests that omit any shareholders are rejected.

Request Fields
files
Not required

submissionData.data.businessShareholderContactDetails
Provide each current shareholder exactly once.

submissionData.data.businessShareholderContactDetails[].shareholderId
The shareholder ID. Required. Use the `id` returned by the [List UBOs](/api-reference/profile/profileubolist) endpoint.

submissionData.data.businessShareholderContactDetails[].email
The shareholder's email address. Required. It must be a valid email address with no more than 255 characters.

submissionData example
```json
{
  "data": {
    "businessShareholderContactDetails": [
      {
        "shareholderId": "7ff6c4998a59d71ad9834041727017d2",
        "email": "shareholder-one@example.com"
      },
      {
        "shareholderId": "a9578a5a0544d06fd737566c627518a4",
        "email": "shareholder-two@example.com"
      }
    ]
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_SHAREHOLDERS_CHECK

Documents showing who ultimately owns and controls the company (e.g. a recent shareholder register, operating agreement, or partnership deed). If an owner is another business, a document identifying the individuals who are the ultimate beneficial owners of that business is needed.

Request Fields
files
Upload the relevant documents.

submissionData example
```json
{
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_SOURCE_OF_WEALTH

The source of the business's wealth. `otherSourceOfWealthDescription` should be provided if `OTHER` is provided as a source of wealth.

Request Fields
files
Not required

submissionData.data.sourceOfWealthList
Accepted values:

- `BUSINESS_ACTIVITIES`
- `INVESTMENTS`
- `LOAN_OR_OTHER_FINANCING`
- `DONATION`
- `GRANTS`
- `OTHER`


submissionData.data.otherSourceOfWealthDescription
Required if `OTHER` is provided in `sourceOfWealthList`.

submissionData example
```json
{
  "data": {
    "sourceOfWealthList": ["BUSINESS_ACTIVITIES", "OTHER"],
    "otherSourceOfWealthDescription": "Loan from friends"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_SOURCE_OF_WEALTH_INFO

The source of the business's wealth and whether it is used to fund the action.

Request Fields
files
Not required

submissionData.data.sourceOfWealthList[].businessSourceOfWealthInfo
Accepted values:

- `REVENUE`
- `PERSONAL_FUNDING`
- `BUSINESS_LOAN`
- `FUNDING_AND_SHAREHOLDER_INVESTMENTS`
- `INVESTMENT_INCOME`
- `DONATIONS`
- `GRANTS`
- `LEGAL`


submissionData.data.sourceOfWealthList[].isSourceOfFund
Whether this source of wealth is used to fund the action.

submissionData example
```json
{
  "data": {
    "sourceOfWealthList": [
      {"businessSourceOfWealthInfo": "BUSINESS_LOAN", "isSourceOfFund": false},
      {"businessSourceOfWealthInfo": "GRANTS", "isSourceOfFund": true}
    ]
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_SOURCE_OF_WEALTH_PROOF

A high-quality photo or PDF of a document proving the source of the business's wealth. The required documentation varies depending on the selected source category. Examples include the most recent 3-6 months worth of bank statements, latest audited financials, latest tax returns, loan agreements, or investment contracts that are less than 12 months old. The document should display the business income amount (if you have more than one type of income, you will have to upload documents for each of them), the business name, the issue date and signatures, if applicable.

Request Fields
files
Upload the proof document.

submissionData.data.sourceOfWealthType
Accepted values:

- `REVENUE`
- `PERSONAL_FUNDING`
- `BUSINESS_LOAN`
- `FUNDING_AND_SHAREHOLDER_INVESTMENTS`
- `INVESTMENT_INCOME`
- `DONATIONS`
- `GRANTS`
- `LEGAL`


submissionData.data.documentType
Accepted values:

- `PAYSLIP`
- `INVOICES`
- `CONTRACTS`
- `TAX_DOCUMENTS`
- `AUDITED_FINANCIAL_STATEMENTS`
- `E_COMMERCE_STATEMENTS`
- `PERSONAL_INVESTMENT`
- `PERSONAL_LOAN_AGREEMENT`
- `PERSONAL_TAX_DECLARATION`
- `LOAN_AGREEMENT`
- `EQUITY_AGREEMENT`
- `SUBSCRIPTION_AGREEMENT`
- `SAVINGS_STATEMENT`
- `ASSET_SALE_AGREEMENT`
- `SHARE_SALE_CERTIFICATE`
- `DONATION_RECEIPTS`
- `GRANT_APPROVAL_LETTER`
- `WRITTEN_CONFIRMATION`
- `BANK_STATEMENT`


submissionData example
```json
{
  "data": {
    "sourceOfWealthType": "REVENUE",
    "documentType": "SAVINGS_STATEMENT"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_ULTIMATE_BENEFICIAL_OWNER_ID

The Ultimate Beneficial Owner (UBO) ID document should be submitted for all UBOs that have more than 25% share. The `shareholderId` is the `id` returned by the [Create UBO](/api-reference/profile/profileubocreate) or [List UBOs](/api-reference/profile/profileubolist) endpoints.

Provide a clear copy of the ID document. The full document needs to be in frame and all information on the document needs to be visible. If the document has information on the backside, both sides are needed. Expired documents and documents issued over 15 years ago cannot be accepted.

Accepted document types vary by the region the business is located in.

### Attributes

Feature in BETA
Attributes for this requirement type are currently in beta. The structure and keys described below may change.

When this requirement has a `state` of `NOT_PROVIDED`, the `attributes` object may include the following:

Attributes
attributes.requiredUbos
A list of shareholder IDs that require UBO ID submission. These correspond to the `id` values returned by the [List UBOs](/api-reference/profile/profileubolist) endpoint. Only shareholders with outstanding UBO ID requirements are included.

**Example:**

```json
{
  "key": "BUSINESS_ULTIMATE_BENEFICIAL_OWNER_ID",
  "state": "NOT_PROVIDED",
  "apiCollectionSupported": true,
  "versions": [{"version": "V1"}],
  "attributes": {
    "requiredUbos": [
      "7ff6c4998a59d71ad9834041727017d2",
      "a9578a5a0544d06fd73756dc627518a4",
      "f6b9391769b3ee29704ecd40c59c0ca3"
    ]
  }
}
```

Request Fields
files
Upload the ID document.

submissionData.data.documentType
**US business address** (United States, American Samoa, Guam, North Mariana Islands, Puerto Rico, United States Virgin Islands, United States Minor Outlying Islands):

- `SSN`
- `NON_US_DRIVING_LICENSE`
- `NON_US_NATIONAL_ID`
- `NON_US_PASSPORT`


**EEA business address:**

- `NATIONAL_ID`
- `PASSPORT`


**Other regions:**

- `DRIVING_LICENSE`
- `NATIONAL_ID`
- `PASSPORT`


submissionData.data.shareholderId
The UBO's shareholder ID.

submissionData.data.frontSideFileName
Filename of the front side image. Required for document types with front and back.

submissionData.data.backSideFileName
Filename of the back side image. Required for document types with front and back.

submissionData.data.ssn
The SSN value. Required when `documentType` is `SSN`.

submissionData example
```json
{
  "data": {
    "documentType": "NATIONAL_ID",
    "shareholderId": "489209",
    "frontSideFileName": "image1.jpeg",
    "backSideFileName": "image2.jpeg",
    "ssn": null
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

submissionData example (SSN)
```json
{
  "data": {
    "documentType": "SSN",
    "shareholderId": "489209",
    "frontSideFileName": null,
    "backSideFileName": null,
    "ssn": "555501234"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## BUSINESS_USE_CASE

How the business intends to use the Wise Account.

Request Fields
files
Not required

submissionData.data.useCases
Accepted values:

- `INVESTING_IN_FUNDS_STOCKS_BONDS_OR_SIMILAR`
- `DISTRIBUTING_COMPANY_PROFITS_OR_PAYING_DIVIDENDS`
- `PAYING_MORTGAGE_BANK_LOAN_INSURANCE_OR_CREDIT`
- `PAYING_FOR_GOODS_PROPERTIES_OR_SERVICES_ABROAD`
- `PAYING_RENT_OR_UTILITIES`
- `PAYING_SUPPLIERS_CONTRACTORS_OR_EMPLOYEES`
- `PAYING_TAX_ON_PROFIT_OR_PROPERTY`
- `TRANSFER_WITHIN_COMPANY_OR_GROUP`
- `RECEIVE_INVESTMENTS_OR_FUNDS`
- `RECEIVE_PAYMENTS_FROM_CLIENTS`
- `DONATION`
- `OTHER`


submissionData example
```json
{
  "data": {
    "useCases": ["DONATION", "PAYING_RENT_OR_UTILITIES"]
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## ID_DOCUMENT

Provide a clear copy of the ID document. The full document needs to be in frame and all information on the document needs to be visible. If the document has information on the backside, both sides are needed. Expired documents and documents issued over 15 years ago cannot be accepted.

Request Fields
files
Upload the ID document.

submissionData.data.issuingCountry
ISO 3166-1 alpha-2 country code.

submissionData.data.documentType
Accepted values:

- `PASSPORT`
- `ID_CARD`
- `DRIVERS_LICENSE`
- `TAX_ID`
- `RESIDENCE_PERMIT`


submissionData.data.frontSideFileName
Filename of the front side image. Required for `ID_CARD`, `DRIVERS_LICENSE`, `TAX_ID`, `RESIDENCE_PERMIT`.

submissionData.data.backSideFileName
Filename of the back side image. Required for `ID_CARD`, `DRIVERS_LICENSE`, `TAX_ID`, `RESIDENCE_PERMIT`.

submissionData example
```json
{
  "data": {
    "issuingCountry": "UK",
    "documentType": "DRIVERS_LICENSE",
    "frontSideFileName": "front_side.jpg",
    "backSideFileName": "back_side.jpg"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## INCOME

Approximate gross yearly income.

Request Fields
files
Not required

submissionData.data.amount
The gross yearly income amount. Must be greater than zero.

submissionData.data.currency
The currency code (e.g. `USD`, `EUR`).

submissionData.data.incomeType
Accepted values:

- `SALARY`
- `INVESTMENTS`
- `PENSION`
- `INHERITANCE`
- `LOAN`
- `PROPERTY_SALE`
- `FREELANCER`
- `FAMILY`
- `STUDENT`
- `GOVERNMENT_BENEFITS`


submissionData.data.incomeExplanation
Optional. A free-text description of the income source.

submissionData example
```json
{
  "data": {
	"amount": 50000.00,
	"currency": "USD",
	"incomeType": "SALARY",
	"incomeExplanation": null
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## INDIA_TRANSFER_PURPOSE

The code representing the purpose of the profile's transfer, along with supporting documents based on the code provided. This only appears for transfers from INR to one of GBP, USD, EUR, AUD, CAD, SGD.

Request Fields
files
Supporting documents with names matching the submitted fileName fields.

submissionData.data.code
Required field. Represents the purpose of the profile's transfer.

- `OVERSEAS_EDUCATION`
- `EDUCATION_EXPENSES`
- `BUSINESS_TRAVEL`
- `VACATION`
- `MEDICAL_TREATMENT`


submissionData.data.tcsTaxApplies
Required field. Must be set to true if the profile has remitted more than INR 10 lakhs (including the current transaction) in the current financial year.

submissionData.data.passportFileName
Required field. Filename for the profile's passport image.

submissionData.data.additionalDocumentFileName
Required field. Filename for additional document provided. The type of file supplied as additional document must be based on the code, these must be in the profile's name.

- For `OVERSEAS_EDUCATION` or `EDUCATION_EXPENSES` this can be a visa or university admission letter.
- For `BUSINESS_TRAVEL` or `VACATION` this can be a visa or travel ticket.
- For `MEDICAL_TREATMENT` this can be a hospital invoice, doctor's confirmation, or appointment letter.


submissionData.data.educationPaidWithLoan
Required field. If code is set to `OVERSEAS_EDUCATION` or `EDUCATION_EXPENSES` set to true if the profile is paying for this transfer with a loan from a financial institution. For other codes set to false.

submissionData.data.loanDocumentFileName
Required when 'educationPaidWithLoan' has been set to true. Filename for the loan sanction letter including sanctioned amount and borrower details.

submissionData example
```json
{
  "data": {
    "code": "OVERSEAS_EDUCATION",
    "tcsTaxApplies": false,
    "educationPaidWithLoan": true,
    "passportFileName": "file1.png",
    "additionalDocumentFileName": "file2.png",
    "loanDocumentFileName": "file3.png"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## JPN_BUSINESS_CERT

Certificate of Registered Matters for the business. Required for corporations only in Japan. The document verifies: business name, registered address, registration date, business activities, directors, and must be issued within 6 months.

Request Fields
files
Upload the Business Document.

submissionData example
```json
{
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## JPN_PERSONAL_MYNUMBER

Proof of My Number for the customer. My Number is a 12-digit ID number issued to all Japan citizens and residents, including resident foreigners living in Japan for over 90 days. We are required to collect a My Number document by Japanese regulations and can't verify customers without it.

We accept 3 different My Number documents:

- My Number card
- My Number notification card (due to the lack of face photo, this can only be accepted as a My Number document)
- Residence Certificate (Juminhyo) issued in the last 6 months with the customer's My Number (個人番号) on it


All the information (name, DOB, address) on a My Number document has to match the information on the profile and on the ID document.

Request Fields
files
Upload the supporting documents. The required number of files depends on the selected document type:

| Document Type | File Requirements |
|  --- | --- |
| `MY_NUMBER_CARD` | 2 files required (Upload front and back) |
| `MY_NUMBER_NOTIFICATION_CARD` | 2 files required (Upload front and back) |
| `RESIDENCE_CERTIFICATE` | 1 or more files (Upload all pages) |


submissionData.data.documentType
The type of My Number document being submitted.
Accepted values:

- `MY_NUMBER_CARD`
- `MY_NUMBER_NOTIFICATION_CARD`
- `RESIDENCE_CERTIFICATE`


submissionData.data.frontSideFileName
The file name of the front-side image. Must match the name of one of the uploaded files.

- Required for `MY_NUMBER_CARD` and `MY_NUMBER_NOTIFICATION_CARD`.
- Not Required for `RESIDENCE_CERTIFICATE`.


submissionData.data.backSideFileName
The file name of the back-side image. Must match the name of one of the uploaded files.

- Required for `MY_NUMBER_CARD` and `MY_NUMBER_NOTIFICATION_CARD`.
- Not Required for `RESIDENCE_CERTIFICATE`.


submissionData example
```json
{
  "data": {
    "documentType": "MY_NUMBER_CARD",
    "frontSideFileName": "front.jpg",
    "backSideFileName": "back.jpg"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## LEGAL_ENTITY_SHAREHOLDER

A legal entity shareholder is another business or organisation that directly or indirectly owns part or all of the business being onboarded. Provide the name, registered country and ownership percentage of every legal entity shareholder that owns 25% or more, directly or indirectly. Do not include individual shareholders or the business being onboarded. If there are no qualifying legal entity shareholders, submit an empty list.

Request Fields
files
Not required

submissionData.data.legalEntityShareholders
The legal entity shareholders of the business. Required.

submissionData.data.legalEntityShareholders[].name
The shareholder's name. Required and must not match the business name.

submissionData.data.legalEntityShareholders[].country
The shareholder's country as an uppercase ISO 3166-1 alpha-2 country code. Required.

submissionData.data.legalEntityShareholders[].ownershipPercentage
The shareholder's ownership percentage. Required and must be between 1 and 100 inclusive. The combined total may exceed 100. This is expected behavior for multi-layered corporate structures.

submissionData example
```json
{
  "data": {
    "legalEntityShareholders": [
      {
        "name": "Example Holdings Inc",
        "country": "US",
        "ownershipPercentage": 40
      }
    ]
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## PROOF_OF_TRADING_ADDRESS

High-quality image or PDF of a document verifying the physical location of the business operations. The document must clearly display the business name (or owner's name), the full trading address, an issue date, and the issuer's identity (e.g. bank or utility logo). Utility bills and bank statements must be less than 3 months old. Other documents (like tax bills, insurance policies, or licences) must be less than 12 months old. The document must be in PDF, JPEG, or PNG format.

The `tradingAddressId` can be retrieved from the business profile endpoint under addresses.

Request Fields
files
Upload the proof document.

submissionData.data.documentType
Accepted values:

- `ID_DOCUMENT`
- `UTILITY_BILL`
- `PHONE_BILL`
- `LEASE_AGREEMENT`
- `BANK_STATEMENT`
- `BUSINESS_REGISTRATION`
- `TAX_BILL`
- `TAX_DOCUMENT`
- `INSURANCE_POLICY`
- `OTHER`


submissionData.data.tradingAddressId
The trading address ID from the business profile.

submissionData example
```json
{
  "data": {
    "documentType": "UTILITY_BILL",
    "tradingAddressId": 4711
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## SOURCE_OF_FUNDS

Provide the origin category of the money used to finance a specific transaction or operation. `explanation` is required when `category` is `OTHER`.

Request Fields
files
Not required

submissionData.data.category
Accepted values:

- `SALARY`
- `INVESTMENT`
- `INHERITANCE`
- `LOAN`
- `PROPERTY_SALE`
- `FROM_FAMILY`
- `OTHER`


Accepted values for business profiles:

- `BUSINESS_OPERATING`
- `BUSINESS_INVESTING`
- `BUSINESS_FINANCING`
- `OTHER`


submissionData.data.explanation
Required if `category` is `OTHER`.

submissionData example
```json
{
  "data": {
	"category": "SALARY",
	"explanation": null
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## SOURCE_OF_WEALTH

Source of wealth document upload.

Request Fields
files
Upload the source of wealth document.

submissionData example
```json
{
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## SOURCE_OF_WEALTH_INFO

Whether there is a secondary source of income, and if so its type and amount. When `hasSecondaryIncome` is `false`, no other fields are required.

Request Fields
files
Not required

submissionData.data.hasSecondaryIncome
Required. Set to `true` if there's a secondary source of income.

submissionData.data.secondaryIncomeType
Required when `hasSecondaryIncome` is `true`. Accepted values for personal profiles:

- `SALARY`
- `PENSION`
- `INHERITANCE`
- `PROPERTY_SALE`
- `LOAN`
- `INVESTMENTS`
- `OTHER`


submissionData.data.secondaryIncomeDescription
Optional. A free-text description of the secondary income source.

submissionData.data.amount
Required when `hasSecondaryIncome` is `true`. The secondary income amount. Must be greater than zero.

submissionData.data.currency
Required when `hasSecondaryIncome` is `true`. The currency code (e.g. `USD`, `EUR`).

submissionData example
```json
{
  "data": {
	"hasSecondaryIncome": true,
	"secondaryIncomeType": "SALARY",
	"secondaryIncomeDescription": null,
	"amount": 20000.00,
	"currency": "USD"
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## SOURCE_OF_WEALTH_PROOF

A document proving the secondary source of wealth income. The accepted document types depend on the `secondaryIncomeType` provided.

Request Fields
files
Upload the proof document.

submissionData.data.secondaryIncomeType
Accepted values for personal profiles:

- `SALARY`
- `PENSION`
- `INHERITANCE`
- `PROPERTY_SALE`
- `LOAN`
- `INVESTMENTS`
- `OTHER`


submissionData.data.secondaryIncomeDocumentType
Accepted values:

- `PAYSLIP`
- `BANK_STATEMENT`
- `TAX_RETURN`
- `EMPLOYMENT_CONTRACT`
- `PROOF_OF_EMPLOYMENT`
- `STOCK_PLAN_EXERCISE_CONFIRMATION`
- `PORTFOLIO_STATEMENT`
- `DIVIDEND_VOUCHER`
- `PENSION_STATEMENT`
- `GRANT_OF_PROBATE`
- `WILL`
- `TRUST_DEED`
- `LOAN_AGREEMENT`
- `SALE_CONTRACT`
- `SETTLEMENT_STATEMENT`
- `GIFT_LETTER`
- `SCHOLARSHIP`
- `GRANT_LETTER`
- `LEASE_AGREEMENT`
- `OTHER`


Valid document types per `secondaryIncomeType`:

- `SALARY`:
  - `PAYSLIP`
  - `TAX_RETURN`
  - `EMPLOYMENT_CONTRACT`
  - `PROOF_OF_EMPLOYMENT`
  - `BANK_STATEMENT`
- `INVESTMENTS`:
  - `TAX_RETURN`
  - `STOCK_PLAN_EXERCISE_CONFIRMATION`
  - `PORTFOLIO_STATEMENT`
  - `DIVIDEND_VOUCHER`
  - `BANK_STATEMENT`
- `INHERITANCE`:
  - `TAX_RETURN`
  - `GRANT_OF_PROBATE`
  - `WILL`
  - `TRUST_DEED`
- `PENSION`:
  - `TAX_RETURN`
  - `PENSION_STATEMENT`
  - `BANK_STATEMENT`
- `PROPERTY_SALE`:
  - `TAX_RETURN`
  - `SALE_CONTRACT`
  - `SETTLEMENT_STATEMENT`
  - `BANK_STATEMENT`
- `LOAN`:
  - `LOAN_AGREEMENT`
  - `BANK_STATEMENT`
- `OTHER`:
  - `GIFT_LETTER`
  - `SCHOLARSHIP`
  - `LEASE_AGREEMENT`
  - `BANK_STATEMENT`
  - `OTHER`


submissionData.data.secondaryIncomeDescription
Optional. A free-text description of the secondary income source.

submissionData example
```json
{
  "data": {
	"secondaryIncomeType": "SALARY",
	"secondaryIncomeDocumentType": "PAYSLIP",
	"secondaryIncomeDescription": null
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

## TAX_RESIDENCY

Users must declare all countries where they hold tax residency. While this is usually where a user lives and works, those with more complex setups (e.g. digital nomads) must list all applicable jurisdictions.

Depending on the user's situation and the Wise entity they are onboarded to, there are three distinct submission scenarios for tax residency. Files are not required for any scenario.

Local Entity TIN Exemptions
If a customer is onboarded to a local Wise entity, providing a TIN for that specific country is not required. View the full list of Wise Group Entities [here](https://wise.com/help/articles/2974131/what-are-the-wise-group-entities). If you are unsure which entity your customers are onboarded to, please contact your Account Manager.

Request Fields
submissionData.data.taxInfoList
A list of tax residency objects for every country where the user is a tax resident.

submissionData.data.taxInfoList[].taxCountry
ISO 3166-1 alpha-2 country code of the tax residency.

submissionData example
```json
{
  "data": {
    "taxInfoList": [
      {
        "taxCountry": "SG"
      }
    ]
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

Standard CRS Collection
For customers not onboarded to a local Wise entity, a Tax Identification Number (TIN) is mandatory for all declared tax residencies. If a TIN cannot be provided, a `skipReason` must be given instead.

Request Fields
submissionData.data.taxInfoList
A list of tax residency objects for every country where the user is a tax resident.

submissionData.data.taxInfoList[].taxCountry
ISO 3166-1 alpha-2 country code of the tax residency.

submissionData.data.taxInfoList[].taxId
An object containing tax identification details.

submissionData.data.taxInfoList[].taxId.type
The specific TIN identifier type for that country. See the [TIN types reference](#tin-types-reference) below.

submissionData.data.taxInfoList[].taxId.number
The actual tax identification number.

submissionData.data.taxInfoList[].skipReason
Justification for not providing a TIN. Accepted values:

- `TAX_EXEMPT` — the customer's income is exempt from taxation.
- `RETIRED_OR_UNEMPLOYED` — the customer is currently retired or unemployed.
- `NO_TAXABLE_INCOME` — the customer does not have any taxable income.
- `WAITING_FOR_TAX_ID` — the customer is waiting to receive their TIN.
- `WITHIN_TIME_FRAME` — the customer is within the time frame for obtaining a TIN.
- `DID_NOT_FILE_INCOME` — the customer did not file a tax return.


submissionData example
```json
{
  "data": {
    "taxInfoList": [
      {
        "taxCountry": "SG",
        "taxId": {
          "type": "SG_NRIC",
          "number": "S1234567A"
        }
      },
      {
        "taxCountry": "BR",
        "skipReason": "WAITING_FOR_TAX_ID"
      }
    ]
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

Golden Visa Declarations
For customers whose only tax residency is in a Golden Visa sponsor country, a mandatory Golden Visa Declaration must be completed. All fields within the `goldenVisaDeclaration` object must be set to `true`. Refer to the [full list of Golden Visa countries](https://wise.com/us/blog/golden-visa-countries#which-countries-have-golden-visa-programs) to identify applicable jurisdictions. If any declaration value is `false`, the customer defaults to Standard CRS Collection and must provide a TIN.

Request Fields
submissionData.data.taxInfoList
A list of tax residency objects for every country where the user is a tax resident.

submissionData.data.taxInfoList[].taxCountry
ISO 3166-1 alpha-2 country code of the tax residency.

submissionData.data.taxInfoList[].skipReason
Justification for not providing a TIN. Accepted values:

- `NO_TAXABLE_INCOME` — the customer does not have any taxable income.
- `WITHIN_TIME_FRAME` — the customer is within the time frame for obtaining a TIN.
- `DID_NOT_FILE_INCOME` — the customer did not file a tax return.


submissionData.data.goldenVisaDeclaration
A set of affirmations required for users holding specific residency-by-investment visas. All values must be set to `true`. Accepted keys:

- `NO_OTHER_RESIDENCE` — customer does not hold residency rights in any other jurisdiction.
- `WITHIN_TIME_FRAME` — customer did not spend more than 90 days in any other jurisdiction in the previous year.
- `DID_NOT_FILE_INCOME` — customer did not file a tax return in any other jurisdiction during the previous year.


submissionData example
```json
{
  "data": {
    "taxInfoList": [
      {
        "taxCountry": "AE",
        "skipReason": "NO_TAXABLE_INCOME"
      },
      {
        "taxCountry": "AG",
        "skipReason": "WITHIN_TIME_FRAME"
      },
      {
        "taxCountry": "BS",
        "skipReason": "DID_NOT_FILE_INCOME"
      }
    ],
    "goldenVisaDeclaration": {
      "NO_OTHER_RESIDENCE": true,
      "WITHIN_TIME_FRAME": true,
      "DID_NOT_FILE_INCOME": true
    }
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```

### TIN types reference

The table below lists the accepted TIN types per country, with format (regex) and an example.

| Country | Type | Format | Example |
|  --- | --- | --- | --- |
| Albania | `AL_NATIONAL_ID` | `[A-Z][0-9]{8}[A-Z]` | A12345678B |
| Albania | `AL_TIN` | `[A-Z][0-9]{8}[A-Z]` | A12345678B |
| Andorra | `AD_NUMERO_DE_REGISTRE` | `[FE][0-9]{6}[A-Z]` | F123456A |
| Anguilla | `AI_INDIVIDUAL_TIN` | `1[0-9]{9}` | 1012345678 |
| Antigua and Barbuda | `AG_TIN` | `[0-9]{8}` | 12345678 |
| Argentina | `AR_CUIT` | `(20|23|24|25|26|27)[0-9]{9}` | 20123456789 |
| Argentina | `AR_CUIL` | `[0-9]{11}` | 27123456789 |
| Argentina | `AR_CDI` | `[0-9]{11}` | 20987654321 |
| Armenia | `AM_TIN` | `[0-9]{8}` | 12345678 |
| Aruba | `AW_PERSOONSNUMMER` | `[0-9]{8}` | 12345678 |
| Australia | `AU_TAX_FILE_NUMBER` | [OECD Guide](https://www.oecd.org/content/dam/oecd/en/topics/policy-issue-focus/aeoi/australia-tin.pdf) | 123456789 |
| Austria | `AT_STEUERNR` | `[0-9]{9}` | 123456789 |
| Azerbaijan | `AZ_TIN` | `[0-9]{10}` | 1234567890 |
| Azerbaijan | `AZ_PIN` | `[A-NP-Z0-9]{7}` | 1A2B3C4 |
| Belgium | `BE_NUMERO_NATIONAL` | `[0-9]{11}` | 12345678901 |
| Belize | `BZ_TIN` | `([0-9]{6}|[0-9]{8})` | 123456 |
| Brazil | `BR_CPF` | `[0-9]{11}` | 12345678901 |
| Brunei Darussalam | `BN_NRIC` | `[0-9]{8}` | 12345678 |
| Bulgaria | `BG_UCN` | `[0-9]{10}` | 1234567890 |
| Bulgaria | `BG_PERSONAL_FOREIGN_NUMBER` | `[0-9]{10}` | 1234567890 |
| Bulgaria | `BG_OFFICIAL_NUMBER` | `[0-9]{10}` | 1234567890 |
| Canada | `CA_SOCIAL_INSURANCE_NUMBER` | `[0-9]{9}` | 123456789 |
| Chile | `CL_RUT` | `[0-9]{2}[.][0-9]{3}[.][0-9]{3}-([0-9]|[K])` | 12.345.678-K |
| China | `CN_ID_NUMBER` | `[0-9]{17}([0-9]|[A-Z])` | 11010119900101123X |
| China | `CN_PASSPORT_ID` | `[CWHMT][0-9]{16}([0-9]|[A-Z])` | G12345678901234567 |
| China | `CN_SOLDIER_CARD` | `J[0-9]{14}` | J12345678901234 |
| Colombia | `CO_NIT` | `[0-9]{8,10}` | 123456789 |
| Cook Islands | `CK_RMD` | `[0-9]{5}` | 12345 |
| Costa Rica | `CR_PIN` | `[0-9]{9}` | 123456789 |
| Costa Rica | `CR_DIMEX` | `[0-9]{11,12}` | 12345678901 |
| Costa Rica | `CR_NITE` | `[0-9]{10}` | 1234567890 |
| Croatia | `HR_OIB` | `[0-9]{11}` | 12345678901 |
| Curacao | `CW_TIN` | `[0-9]{9}` | 123456789 |
| Cyprus | `CY_TIC` | `[0-9]{8}[A-Za-z]` | 12345678A |
| Czech Republic | `CZ_PERSONAL_NUMBER` | `[0-9]{9,10}` | 1234567890 |
| Denmark | `DK_CPR` | `[0-9]{10}` | 1234567890 |
| Dominica | `DM_TAX_PAYER_NUMBER` | `[0-9]{6}` | 123456 |
| Ecuador | `EC_RUC` | `[0-9]{13}` | 1234567890123 |
| Estonia | `EE_ISIKUKOOD` | `[0-9]{11}` | 12345678901 |
| Faroe Islands | `FO_PTAL` | `[0-9]{9}` | 123456789 |
| Finland | `FI_SSN` | `[0-9]{6}[+-A][0-9]{3}([A-Z]|[0-9])` | 010101-123A |
| France | `FR_NUMERO_SPI` | `[0-3]{1}[0-9]{12}` | 1234567890123 |
| Georgia | `GE_TIN` | `([0-9]{9}|[0-9]{11})` | 123456789 |
| Germany | `DE_IDNR` | `[0-9]{11}` | 12345678901 |
| Ghana | `GH_GHANACARD_PIN` | `[A-Z]{3}-[0-9]{8,9}-[A-Z0-9]` | GHA-123456789-A |
| Ghana | `GH_GRA_TIN` | `[A-Z]00[0-9]{8}` | P0012345678 |
| Gibraltar | `GI_TAXPAYER_REFERENCE_NUMBER` | `[0-9]{1,6}` | 123456 |
| Greece | `GR_CPR` | `[0-9]{9}` | 123456789 |
| Greenland | `GL_CPR` | `[0-9]{10}` | 1234567890 |
| Grenada | `GD_TIN` | `[0-9]{6}` | 123456 |
| Guernsey | `GG_SSN` | `GY[0-9]{6}` | GY123456 |
| Guernsey | `GG_NATIONAL_INSURANCE_NUMBER` | `[A-Z]{2}[0-9]{6}[ABCD]` | AB123456C |
| Guernsey | `GG_JERSEY_SSN` | `JY[0-9]{6}[A-Z]` | JY123456A |
| Hong Kong | `HK_TIN` | `[A-Z]{1,2}[0-9]{6}\(([0-9]|A)\)` | A123456(7) |
| Hungary | `HU_TIN` | `[0-9]{10}` | 8123456789 |
| Iceland | `IS_KENNITALA` | `[0-9]{10}` | 1234567890 |
| India | `IN_PAN` | `[A-Z]{5}[0-9]{4}[A-Z]{1}` | ABCDE1234F |
| Indonesia | `ID_NIK` | `[0-9]{16}` | 1234567890123456 |
| Indonesia | `ID_NPWP` | `[0-9]{15,16}` | 123456789012345 |
| Ireland | `IE_PPSN` | `[0-9]{7}[A-Z]{1,2}` | 1234567FA |
| Isle of Man | `IM_TAX_REFERENCE_NUMBER` | `(H|C|X)[0-9]{6}-[0-9]{2}` | H123456-01 |
| Isle of Man | `IM_NATIONAL_INSURANCE_NUMBER` | `[A-Z]{2}[0-9]{6}[ABCD]` | AB123456C |
| Israel | `IL_IDENTITY_NUMBER` | `[0-9]{9}` | 123456789 |
| Italy | `IT_CODICE_FISCALE` | `[A-Z]{6}[0-9LMNPQRSTUV]{2}[A-Z][0-9LMNPQRSTUV]{2}[A-Z]?[0-9LMNPQRSTUV]{3}[A-Z]` | RSSMRA80A01H501U |
| Japan | `JP_INDIVIDUAL_NUMBER` | `[0-9]{12}` | 123456789012 |
| Jersey | `JE_SSN` | `[A-Z]{2}[0-9]{6}[A-Z]` | AB123456C |
| Jersey | `JE_TIN` | `[0-9]{10}` | 1234567890 |
| Kenya | `KE_PERSONAL_IDENTIFICATION_NUMBER` | `[A-Z][0-9]{9}[A-Z]` | A123456789B |
| Kuwait | `KW_CIVIL_NUMBER` | `[0-9]{12}` | 123456789012 |
| Latvia | `LV_PERSONAL_CODE` | `[0-9]{11}` | 12345678901 |
| Lebanon | `LB_TIN` | `[0-9]{9}` | 123456789 |
| Liechtenstein | `LI_PEID_NUMBER` | `([0-9]{12}|[0-9]{4,7})` | 1234567 |
| Lithuania | `LT_PERSONAL_CODE` | `[0-9]{10,11}` | 1234567890 |
| Luxembourg | `LU_NIN` | `[0-9]{13}` | 1234567890123 |
| Macao | `MO_ID_NUMBER` | `[0-9]{8}` | 12345678 |
| Malaysia | `MY_INCOME_TAX_NUMBER` | `(SG|OG|IG) [0-9]{11}` | SG 12345678901 |
| Malaysia | `MY_NATIONAL_REGISTRATION_NUMBER` | `[0-9]{6}-[0-9]{2}-[0-9]{4}` | 900101-01-1234 |
| Maldives | `MV_TIN` | `[0-9]{7}[A-Z]{3}[0-9]{3}` | 1234567ABC001 |
| Malta | `MT_IDENTITY_CARD_NUMBER` | `[0-9]{3,7}[A-Z]` | 1234567M |
| Malta | `MT_TAXPAYER_REFERENCE_NUMBER` | `[0-9]{9}` | 123456789 |
| Marshall Islands | `MH_SSN` | `04-[0-9]{6}` | 04-123456 |
| Mauritius | `MU_TAN` | `[0-9]{8}` | 12345678 |
| Mexico | `MX_RFC` | `[A-Z]{4}[0-9]{6}[A-Z0-9]{3}` | ABCD123456E12 |
| Netherlands | `NL_FIN` | `[0-9]{9}` | 123456789 |
| New Zealand | `NZ_IRD_NUMBER` | `[0-9]{8,9}` | 123456789 |
| Nigeria | `NG_JTB_TIN` | `[0-9]{10}|[0-9]{13}` | 1234567890 |
| Nigeria | `NG_FIRS` | `[0-9]{8}-0001` | 12345678-0001 |
| Norway | `NO_NIN` | `[0-9]{11}` | 12345678901 |
| Norway | `NO_D_NUMBER` | `[0-9]{11}` | 12345678901 |
| Pakistan | `PK_CNIC` | `[0-9]{13}` | 1234567890123 |
| Poland | `PL_PESEL` | `[0-9]{11}` | 12345678901 |
| Poland | `PL_NIP` | `[0-9]{10}` | 1234567890 |
| Portugal | `PT_NIF` | `[1234][0-9]{8}` | 123456789 |
| Qatar | `QA_TIN` | `5[0-9]{9}` | 5123456789 |
| Romania | `RO_CNP` | `[0-9]{13}` | 1234567890123 |
| Romania | `RO_CIF` | `9000[0-9]{9}` | 9000123456789 |
| Romania | `RO_NIF` | `9000[0-9]{9}` | 9000123456789 |
| Saudi Arabia | `SA_TIN` | `[0-9]{10}` | 1234567890 |
| Saudi Arabia | `SA_RESIDENCY_ID` | `[0-9]{10}` | 1234567890 |
| Singapore | `SG_NRIC` | `(S|T)[0-9]{7}[A-Z]` | S1234567A |
| Singapore | `SG_FIN` | `(F|G|M)[0-9]{7}[A-Z]` | F1234567A |
| Slovakia | `SK_TIN` | `[0-9]{10}` | 1234567890 |
| Slovakia | `SK_BIRTH_IDENTIFICATION_NUMBER` | `[0-9]{9,10}` | 1234567890 |
| South Korea | `KR_RRN` | `[0-9]{13}` | 1234567890123 |
| Spain | `ES_DNI` | `[0-9]{8}[A-Z]` | 12345678A |
| Spain | `ES_NIE` | `[LKMXYZ][0-9]{7}[A-Z]` | X1234567L |
| Sweden | `SE_PERSONAL_IDENTITY_NUMBER` | `[0-9]{6}(-|+)[0-9]{4}` | 900101-1234 |
| Sweden | `SE_COORDINATION_NUMBER` | `[0-9]{6}-[0-9]{4}` | 900101-1234 |
| Turkey | `TR_NATIONAL_IDENTITY_NUMBER` | `[0-9]{11}` | 12345678901 |
| Turkey | `TR_FOREIGN_IDENTITY_NUMBER` | `[0-9]{10}` | 1234567890 |
| United Kingdom | `GB_NATIONAL_INSURANCE_NUMBER` | `[A-Z]{2}[0-9]{6}[ABCD]` | AB123456C |
| United Kingdom | `GB_UNIQUE_TAXPAYER_REFERENCE` | `[0-9]{10}` | 1234567890 |
| United States | `US_SSN` | `(?!000)(?!666)\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}` | 123-45-6789 |
| United States | `US_ITIN` | `9\d{2}-?(5\d|6[0-5]|7\d|8[0-8]|9[0-2,4-9])-?\d{4}` | 912-70-1234 |
| Uruguay | `UY_CI_NUMBER` | `[0-9]{8}` | 12345678 |
| Uruguay | `UY_FOREIGN_IDENTIFICATION_NUMBER` | `[0-9]{9}` | 123456789 |
| Uruguay | `UY_RUT` | `[0-9]{12}` | 123456789012 |


## USE_CASE_COUNTRIES

Country codes where the business intends to send money. If unsure, select the country codes that correspond with the target currencies.

Request Fields
files
Not required

submissionData.data.useCaseCountries
Country codes in ISO 3166-1 alpha-3 standard.

submissionData example
```json
{
  "data": {
    "useCaseCountries": ["usa", "gbr", "deu"]
  },
  "version": "V1",
  "kycReviewId": "93a903ea-636c-4c86-a25c-cf6d2bd00e81"
}
```