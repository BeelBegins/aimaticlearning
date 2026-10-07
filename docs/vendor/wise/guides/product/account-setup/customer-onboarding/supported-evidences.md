# List of supported evidences

"Evidences" are pieces of data Wise requires to successfully review and verify your customers.

When Wise requires additional verification evidence, use the following Additional Verification endpoints to send the required data:

- [POST Upload evidences](/api-reference/verification/verificationuploadevidences): To submit non-document, text-based identity details in a structured format (for example, SSN, registration numbers, tax identifiers).
- [POST Upload document](/api-reference/verification/verificationuploaddocument): To upload supporting files like source of wealth documents and proof of identity/address.


## Supported evidences for personal profiles

Upload evidences
| Field  | Description |
|  --- | --- |
| `accountPurpose` | Indicates the primary purpose for using Wise account. Selected from a list of enum values. |
| `accountPurposeExplanation` | A free-text field to supply additional reasons and specific examples for using the Wise account. |
| `yearlyAnticipatedVolume` | The customer's yearly anticipated transaction volume in their local currency. Select from a list of enum values. |
| `annualIncome` | Expected annual income in the customer's local currency. Must be submitted with `mainSourceOfIncome`. |
| `mainSourceOfIncome` | The customer's primary source of income. Must be submitted with `annualIncome`. |
| `incomeExplanation` | A free-text field to include additional ways the customer earns money that was not identified in the provided documents. |
| `intendedCountries` | List of ISO 3166-1 alpha-3 country codes that the customer intends to send and receive money from.

Check the [lists of countries you can send money to with Wise](https://wise.com/help/articles/2571942/what-countries-can-i-send-to). |


Upload documents
| Document type  | Description |
|  --- | --- |
| `SOURCE_OF_WEALTH` | A document detailing source of wealth according to specified main source of income.

The [Additional customer verification guide](/guides/product/account-setup/customer-onboarding/additional-verification#source-of-wealth-document) provides a list of acceptable documents. |
| `ID_PROOF` | A document detailing proof of identification for the profile.

See the [How does Wise verify my identity? help article](https://wise.com/help/articles/2949801/how-does-wise-verify-my-identity?origin=search-ID+coument+) for a list of acceptable documents. |
| `ADDRESS_PROOF` | A document detailing proof of residential address of the profile owner.

See the [How does Wise verify my identity? help article](https://wise.com/help/articles/2949804/how-does-wise-verify-my-address?origin=search-proof+of+address+) for a list of acceptable documents. |


## Supported evidences for business profiles

Upload evidences
| Field  | Description |
|  --- | --- |
| `mainSourceOfFunding` | The main source of wealth for the business. Selected from a list of enum values. |
| `monthlyAnticipatedVolume` | The monthly anticipated volume of your business. Selected from a list of enum values. |
| `businessUseCase` | The main use case for which the business wants to use Wise. Selected from a list of enum values. |
| `intendedCountries` | List of ISO 3166-1 alpha-3 country codes that the customer intends to send and receive money from.

Check the [lists of countries you can send money to with Wise](https://wise.com/help/articles/2571942/what-countries-can-i-send-to). |


Upload documents
| Document type  | Description |
|  --- | --- |
| `SOURCE_OF_WEALTH` | A source of wealth document that aligns with the source of funding provided.

The [Additional customer verification guide](/guides/product/account-setup/customer-onboarding/additional-verification#source-of-wealth-document) provides a list of acceptable documents. |
| `TRADING_ADDRESS_PROOF` | A document detailing proof of operational address.

The [Additional customer verification guide](/guides/product/account-setup/customer-onboarding/additional-verification#proof-of-trading-address-document) provides a list of acceptable documents. |