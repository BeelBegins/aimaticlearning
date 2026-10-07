# Versioning

Wise Platform APIs evolve over time as we add features and expand coverage. This guide explains how Wise Platform versions its APIs, what types of changes you can expect within a version, and how to choose which version to use.

Versioning scope
This versioning policy does not currently apply to **webhooks** or **sensitive card details** endpoints. We will update this policy once these endpoints have been migrated to this versioning scheme.

## How versioning works at Wise Platform

Wise Platform uses global, calendar-based versioning (CalVer). Versions are shared across the API (rather than versioning each endpoint independently) and released on a quarterly basis.

Versions are named by year and quarter, for example:

- `2026Q3`
- `2026Q4`


Wise Platform versioning is URL-based, meaning you select the version by including it in the endpoint request path.

For example:

```
/2026Q3/auth/jose/response/public-keys
```

## Version types

Documentation for each version is accessible in the [API reference](/api-reference) via the **Versions** drop-down.

| Version type | Description |
|  --- | --- |
| **Latest** | The most recently released version. |
| **Active** | Prior released versions with continuous support until they are sunset (see [Deprecation and sunset policy](#deprecation-and-sunset-policy) for details). |
| **Preview** | A preview of the upcoming quarter's version. May include breaking or other changes without notice.
Use with caution and in a test environment, or when specifically instructed (for stable releases, continue to use *Latest* or *Active* versions). |
| **Legacy** | Endpoints that use the older endpoint-based versioning (released prior to CalVer). These endpoints are still supported and continue to work as originally intended. |


## Release cadence

Wise releases new API versions **quarterly**.

Each quarter, the *Preview* version is promoted to the *Latest* version and the prior *Latest* version moves into *Active* status.

For example, on 1 October 2026:

- The *Latest* version becomes `2026Q4` and the `2026Q3` version becomes an *Active* version.
- The new *Latest* version includes any major and breaking changes that have been added up to that point.
- Changes are documented in the [changelog](/changelog) along with any necessary migration guidance.
- The new *Preview* version is then `2027Q1`.


## Changes

Wise classifies changes as either **breaking** or **non-breaking**.

API integration requirements
To ensure long-term stability, your integration must adhere strictly to all documented API specifications and standards. Unenforced requirements may be enabled at any time without a new API version release; as long as your implementation follows the documentation, it will not be affected.

### Breaking changes

A breaking change is any change that requires you to modify your integration to keep it working as originally intended.

Examples include:

- Removing or renaming a field.
- Changing a field’s type or meaning.
- Introducing new required parameters.
- Removing or fundamentally changing an endpoint.
- Behavioural changes that alter expected outcomes for the same request.


Breaking changes are added to the upcoming (preview) version only, except when security or compliance concerns require adding the breaking change to the latest version. You only need to update your request URL to the new version if you wish to use the updated endpoint.

### Non-breaking changes

Wise may introduce additive, backward-compatible changes within the *Latest* version at any time. These changes will *not* increment the API version number.

Examples include:

- Adding new fields to responses.
- Adding new optional request parameters.
- Adding new endpoints/resources.


Integration best practice
Design to be resilient to additive changes so that newly-added fields do not break parsing or validation.

## Deprecation and sunset policy

Wise supports each active version until such time as we determine it needs to be deprecated.

Currently, Wise has no set time frame for how long a version remains active. However, we have no plans right now to sunset any currently supported versions.

To avoid disruption to your integration, any plans to sunset versions will be communicated well in advance.

### Communication policy

Ahead of sunsetting a version, Wise will provide notice at least 6 months in advance via:

- Email to partner contacts.
- The [developer changelog](https://docs.wise.com/changelog).


## Policy review

Wise Platform is continuously evolving as we offer new features and coverage to our API customers.

It's important to us that our partner integrations are not adversely affected by changes and we endeavor to uphold these standards as part of our company's mission of transparency. We regularly review our policies to make sure we're delivering the best possible developer experience.