# Migrating to the new Sandbox

To improve the testing experience with Wise Platform, we are releasing a new version of our Sandbox environment. We require you to migrate from the current Sandbox version (V1) to our new Sandbox version (V2) by **June 30, 2026**. This guide will explain why you need to migrate and what actions you will need to take.

Any profiles, transactions or activities that have been created in the current version (V1) after **April 1, 2025**, will unfortunately not be transferred to the new version (V2).

The rest of this document refers to the two sandbox environments as **V1** and **V2**.

| Term | Description |
|  --- | --- |
| **V1** | [https://sandbox.transferwise.tech](https://sandbox.transferwise.tech) / [https://sandbox.wise.tech](https://sandbox.wise.tech) |
| **V2** | [https://wise-sandbox.com](https://wise-sandbox.com) |
| **CSM** | Customer Success Manager |


## Why Are We Migrating?

We're introducing an improved Sandbox environment to offer closer parity with our production environment allowing more features to be tested while also enhancing the stability.

To focus our resources on this improved experience, the current Sandbox (V1) will be deprecated on **June 30, 2026**.

Key Dates
- V1 environment data cut-off: **April 1, 2025**
- V1 environment deprecation: **June 30, 2026**


## How to migrate to the V2 sandbox environment

You **will need to complete the following actions** before the migration deadline:

1. **Update environment configuration**
  - **Action Needed:** Switch base URLs / credentials to V2
2. **[Applicable for partners onboarded after 1 April 2025] Request new V2 sandbox credentials**
  - **Action Needed:** Contact Wise Team (api@wise.com) or your delivery contact.
3. **[Applicable for some] Update security configuration**
  - If you use mTLS, JWS, JWE or SCA with Wise, please refer to the **[Security](#security)** section for guidance.
4. **Recreate test data**
  - Transactions, users, profiles or other test entities created after **April 1, 2025** will need to be re-seeded.
5. **Run validation tests**
  - Ensure existing test flows of your integration behave as expected in V2.


## Environment Configuration

API documentation has been updated and points to Sandbox V2. Please update the base URL and use the portal address for V2:

|  | **Sandbox V1 (Old)** | **Sandbox V2** |
|  --- | --- | --- |
| **API Host/ Base URL** | `api.sandbox.transferwise.tech`  `api.sandbox.wise.tech` | `api.wise-sandbox.com` |
| **Wise Portal** | `sandbox.transferwise.tech`  `sandbox.wise.tech` | `wise-sandbox.com` |


**V1 tokens and credentials created after 1 April 2025 will not work in V2.** Request new credentials via your delivery team or api@wise.com.

- For clients, users and profiles created before **April 1, 2025**, the profile ID, client ID, client secret and refresh token will remain the same as they were migrated over to V2. However, you will still need to generate a new access token every 12 hours on expiry and you can continue using APIs as per usual.
- Otherwise, create user accounts and profiles from scratch, either via API or through Wise.com using OAuth Linking. After setup, generate your refresh and access tokens.
  - See [Setting up a Wise Account](/guides/developer/account-creation) for the detailed setup guide.


Upon obtaining your tokens and setting up your account and profiles, you’re good to go.

## API Endpoint and Webhook Behaviours

All endpoints and webhooks available in V1 work in V2. No code logic changes are required. For any doubts, refer to the API Docs for details.

- IDs (e.g. user ID, profile ID, transfer ID, balance ID, webhook subscription ID) and passwords created before **April 1, 2025** will remain the same for both V1 and V2.


## Recreating Test Data

Due to differences in infrastructure and data models between Sandbox V1 and V2, existing test data cannot be migrated. To continue testing, please recreate required entities such as users, profiles, and transactions in V2.

## Security

If you have implemented mTLS, JWE, JWS or SCA with Wise, actions are outlined below accordingly.

### mTLS for APIs

**Change required**

- You will need to generate and download new certificates for V2 to configuring mTLS from scratch. See [Mutual TLS](/guides/developer/auth-and-security/mtls).


### mTLS for Webhooks

**No change required**

- The public keys listed in API Docs work for V1 and V2. No config updates between environments will be required. See [Test notification header](/guides/developer/webhooks/event-handling#test-notification-header-x-test-notification).


### JOSE: JWE and JWS

**Change required**

- You will need to retrieve new public keys from [Get Wise public signing key](/api-reference/jose/joseresponsepublickeysget).
- Use these to verify signed payloads and/or encrypt in V2.


### SCA

**Change potentially required**

If you are not using any of the APIs that require SCA (for example balance funding and account statement access) then **no action is required**.

If you have an agreed exemption from SCA (for example for secure corporate payments) then **no action is required**.

If you are using the [embedded SCA component](/guides/developer/auth-and-security/embedded-sca-component) or one of our [SCA over API](/guides/developer/auth-and-security/sca-over-api#authentication-methods) strategies, please contact your CSM to discuss any integration changes that might be required for those more customised solutions.

## What Happens If No Action Is Taken?

If you do not migrate:

- V1 environment will eventually be disabled
- Test integrations relying on V1 will fail
- New features and fixes will not be available
- Support for V1-specific issues will be limited


## Next Steps

- Share this guide with your development team
- Begin migration early
- Contact your Customer Success Manager (if you have one), Wise Delivery Team (if you are in the process of build and test) or [api@wise.com](mailto:api@wise.com) for support


## Frequently Asked Questions (FAQ)

### 1. Is production affected?

No. This migration impacts **testing environments only**. Production systems are not affected.

### 2. What is the difference between v1 and v2?

V2 is a newer testing environment with stronger infrastructural stability that more closely mirrors production. V1 is being deprecated and will no longer receive updates.

### 3. Will my existing V1 test data be available in v2?

Data from V1 created up until **April 1, 2025** will be available. Beyond this date, the environments have diverged. V1 data cannot be migrated or recovered into V2 beyond the cut-off date of **April 1, 2025**.

### 4. Can we keep using V1 alongside V2?

No. V1 will be fully deprecated after the migration window.

### 5. Do we need to change our code?

Possibly. While many integrations will work with minimal changes, you should:

- Verify API compatibility
- Re-seed required test data
- Validate critical test flows


Most changes should be configuration-related as your team switches over to using V2.

### 6. What happens if we don’t migrate in time?

We will stop support for V1 on **June 30, 2026** and will deprecate the environment shortly after. Your testing workflows will no longer work once the environment is deprecated.

### 7. How do we validate that we’re ready?

We recommend:

- Running your full test suite in V2
- Verifying key user and transaction flows
- Confirming expected error handling


### 8. Where can we get help?

If you encounter issues during migration, reach out to your delivery team or support contact with:

- Environment details
- Affected endpoints
- Example request / response payloads


Contact your Customer Success Manager if you have one for operational queries. Otherwise, reach out to [api@wise.com](mailto:api@wise.com) for technical queries.