# Creating an account

Getting started as a Correspondent or Enterprise partner

All Wise Platform partners must have an account with a business profile. How these accounts get created differs depending on your integration model.

- Correspondent and Enterprise partners start by creating an account and adding a business profile.
- For Embedded Solution partners, accounts are provisioned internally due to their unique configuration needs.


## Methods

You can create your Wise account and related profiles either **via API** or **via the Wise.com interface**. Each method has a specific OAuth grant flow for obtaining user tokens.

- **API method**: Uses the **registration code grant flow** to obtain user tokens. This method is best for fully automated, headless integrations where you programmatically obtain credentials and tokens, providing the best level of security overall.
- **Wise.com method**: Uses the **authorisation code grant flow** to obtain user tokens. This method is best for partners who prefer to create their account interactively through the Wise web interface.


Your implementation team will help you decide which path best fits your business and integration needs.

Select your preferred method below for step-by-step instructions:

API method 
For the registration code OAuth grant flow.

Wise.com method
For the authorisation code OAuth grant flow.

## Requirements

- Client credentials are required for both account setup methods.
- A redirect URI, if using the authorisation code grant flow.
- Multiple pieces of data about the business and its representatives to create the profile.


Review this section thoroughly to ensure you have the necessary information before you begin.

### Client credentials

Your `client_id` and `client_secret` are issued by your implementation team and are scoped to your specific integration. Visit the [Developer Hub](https://wise.com/developer-hub) to access your client credentials at any time.

*If you are currently testing with sandbox credentials, be sure to access the [sandbox Developer Hub](https://wise-sandbox.com/developer-hub) instead*.

### Redirect URI

The **redirect URI** is the registered callback URL for the authorisation code flow (not necessary if using the registration code flow).

For Correspondent partners, Wise issues a dummy redirect URI solely for the purpose of providing the authorisation code during the redirect step.

### Business profile details

All partner integrations require, at minimum, the following data points to create a business profile:

**Business representative (authorised signatory)**:

- Full legal name (first name, last name)
- Date of birth
- Residential address (state code required for US, CA, BR, and AU addresses)
- Contact email address
- Phone number (with international prefix)


The person your organization designates as the business representative should be someone considered an **authorised signatory**. This could be a director, executive officer, or other senior leader in your organization. Your implementation team can help you determine the appropriate individual.

The representative's details are submitted as part of the business profile creation request, rather than as a separate personal profile.

**Business profile**:

- Legal business name
- Business registration number
- Company type (from an [enumerated list](/api-reference/profile/profilebusinesscreatev3))
- Company role of the person creating the profile (`OWNER`, `DIRECTOR`, or `OTHER`)
- Registered business address
- Business industry categories (see [Business categories](/guides/product/account-setup/customer-onboarding/business-categories))
- Operational address(es)
- Business webpage
- An actively monitored email address for handling Requests for Information (RFIs)


**Business directors and ultimate beneficial owners (UBOs)**:

- Full name, date of birth, and country of residence (ISO3 code) for each director
- Full name, date of birth, country of residence (ISO3 code), address, and ownership percentage for each UBO


If you are uncertain about who to identify as business directors or UBOs, consult with your implementation team for assistance.

Additional information may be required
Depending on the region the business is located in and the type of organization, Wise may require additional details and documentation beyond what is listed here to perform enhanced due diligence (EDD). The Wise KYC team will review all details submitted and notify you of any additional requirements, if any.

Your implementation team can also assist with submitting the additional details and documents.

## Environments

For each environment, sandbox and production, we offer an endpoint that requires mutual TLS (mTLS) and a separate endpoint for non-mTLS. For most situations we recommend using mTLS, which requires some [additional setup](/guides/developer/auth-and-security/mtls).

| Environment | Base URL | mTLS enabled |
|  --- | --- | --- |
| Sandbox | `https://api.wise-sandbox.com` | `https://api-mtls.wise-sandbox.com` |
| Production | `https://api.wise.com` | `https://api-mtls.transferwise.com` |


During development, you’ll follow the setup steps in the sandbox environment with your sandbox credentials. Once ready to move into production, you’ll follow the same steps in the production environment.

The sandbox environment may be made available prior to an executed partnership agreement, and your onboarding team will issue sandbox-specific credentials to you.

## Postman collection

Postman collection: Partner access tokens