# Strong Customer Authentication & 2FA

Strong customer authentication (SCA) is a security measure that requires customers to provide multiple forms of identification to verify their identity before accessing sensitive information or performing high-risk transactions.

The goal of SCA is to prevent fraud and protect sensitive information by ensuring that only authorized users can access it.

You can think of SCA as a form of multi-factor authentication (MFA) designed specifically for financial services. However, MFA is a broader technical concept while SCA defines the business feature.

## European regulatory requirement

SCA is a European regulatory requirement as part of the second
[Payment Services Directive (PSD2)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L2366) for authenticating online payments and making them more secure.

Some actions require SCA in the UK and EEA, such as funding a transfer from your multi-currency account or retrieving a statement.

Please note that Wise may enforce SCA on endpoints based on our risk assessment as part of our best efforts for consumer protection.

## SCA-protected endpoints

At Wise, when an endpoint performs an action that requires strong customer authentication, the initial request to that endpoint is rejected with a response status of `403 (Forbidden)` to inform you that stronger authentication is needed. The endpoint can be retried again with stronger authentication.

When an endpoint requires a stronger authentication, we've indicated so by adding an alert banner like this to the endpoint reference:

SCA protected endpoint
This endpoint is SCA protected. SCA requirements apply to profiles registered outside of the following regions: US, AU, NZ, SG, CA, MY.

For more information on how to build a stronger authentication request call, review our [One Time Token guide](/guides/developer/auth-and-security/one-time-token).

## Implementing SCA

How you implement SCA will depend on your [integration use case](/guides#use-cases). Before implementing SCA, be sure to discuss it with your implementation team to ensure you use the method appropriate for your use case.

The following table provides the recommended SCA guide based on integration use case:

| Integration use case | Recommended SCA guide |
|  --- | --- |
| [Embedded finance using partner KYC](/guides/product/account-setup/customer-onboarding) | [SCA over API](/guides/developer/auth-and-security/sca-over-api) |
| [Embedded finance using Wise KYC](/guides/product/account-setup/customer-onboarding/api-hybrid-kyc) | [Embedded SCA component](/guides/developer/auth-and-security/embedded-sca-component) |
| [Open banking](/guides/developer/open-banking) | [Open banking guide](/guides/developer/open-banking) |