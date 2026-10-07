# 

CPF, CNPJ, and Financial Capacity are key components in the Brazilian financial system, each serving distinct roles in personal and business contexts.

## CPF/CNPJ 

CPF, or Cadastro de Pessoas Físicas, is an individual taxpayer identification number in Brazil. It is crucial for personal financial transactions, government services, and employment documentation. CPF is unique to each individual and is used to track their financial activities, ensuring transparency and compliance with tax regulations.

CNPJ, or Cadastro Nacional da Pessoa Jurídica, is the CPF equivalent for businesses. It is a unique registration number assigned to legal entities operating in Brazil. CNPJ is essential for business-related transactions, tax filings, and regulatory compliance. This number is crucial for establishing the legal identity of a company and is used by financial institutions, government agencies, and business partners for various purposes.

Wise is required to report multiple details in order to ensure transparency and compliance with tax regulations. Wise does this by ensuirng the CPF/CNPJ on the profile is validated. If your integration allows us to rely on your CPF/CNPJ validation, you will be able to upload this during profile creation via the API.

## Using Financial Capacity 

Financial Capacity, in the Brazilian context, refers to an individual or business entity's ability to meet financial obligations. Lenders and financial institutions often assess financial capacity when evaluating creditworthiness. This assessment includes factors such as income, assets, liabilities, and credit history. Understanding an entity's financial capacity is vital for making informed lending and investment decisions, promoting responsible financial practices in the Brazilian economic landscape.

Wise requires the assessment of the financial capacity of each customer profile. We do this internally when needed, but also can rely on the evaluation by partners in certain situations. If your integration allows us to rely on your financial capacity, you will be able to upload this during profile creation via the API.

## Uploading CPF/CNPJ/Financial Capacity 

During the creation of a profile, partners must provide the CPF/CNPJ and the financial Capacity assessed by them to that entity. During the upload, Wise verifies the CPF and CNPJ against a bureau database. The name and date of birth of the user must match exactly to that held with the bureau.

To complete the upload, please refer to the [Create an identification document for a profile API](/api-reference/profile/profileverificationdocumentcreate). Examples of the specific payloads that should be sent for each type are available.

### Testing CPF/CNPJ

When testing the above API in Sandbox, Wise mimics the checks completed in production, while also allowing you to test specific error codes. In order to pass the verification of the uploaded CPF, the following must be set correctly on the profile:

- firstName = 'Test'
- lastName = 'User'
- dob = 01/01/2000
- CPF must start with 6, 7, 8, or 9


If this is not set for the profile, the CPF upload will fail in the sandbox environment with an error. The error will either correspond to `NAME_MISMATCH` if firstName or lastName are incorrect or `DOB_MISMATCH` if DOB is incorrect.

#### CPF/CNPJ Errors in Sandbox

Alternate errors will be given in Sandbox based on the initial digit of the CPF. This facilitates testing of specific error handling flows as required in your integration. CPF/CNPJs that begin with the below digits will produce the corresponding error in Sandbox.

- 0 - `NOT_ASSIGNED`
- 1 - `NAME_MISMATCH`
- 2 - `DOB_MISMATCH`
- 3 - `IRREGULAR`
- 4 - `NOT_CHECKED`
- 5 - `BELONG_TO_MINOR`


Please ensure that you use the right test CPF when testing in sandbox. Also note that a CPF can only be used once per client key, so you should generate this as you create the test accounts. Never use real CPFs in Sandbox.