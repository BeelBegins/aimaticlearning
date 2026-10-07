# Migrating to industry categories

Replace legacy business categories when you create or update business profiles

Wise is moving business profile classification from the legacy `firstLevelCategory` and `secondLevelCategory` fields to `industryCategories`. This is a **field change, not an endpoint change**, keep using the create and update business profile endpoints you already integrate with.

## Why you need to migrate

This compliance-driven change helps Wise meet regulatory expectations. It replaces the broad, hardcoded legacy categories with a more granular list aligned with the latest industry-classification standards. It also allows a business to provide more than one industry category.

For the values accepted by the API, see the [Wise business categories list](/guides/product/account-setup/customer-onboarding/business-categories).

Submit values from the Wise business categories list. External NACE and SIC codes are not Wise API values.

## Before you start

- Identify any interface that collects a business's industry information.
- Make sure you can test your changes in the sandbox.


## 1. No endpoint change is required

`industryCategories` is accepted on every current create and update business profile endpoint, including the existing V2 and V3 flows. Keep using the endpoint you already call:

| If you currently use | Keep using it |
|  --- | --- |
| `POST /v2/profiles/business-profile` | [Create a business profile](/api-reference/legacy/profile/profilebusinesscreate) |
| `POST /v3/profiles/business-profile` | [Create a business profile (V3)](/api-reference/legacy/profile/profilebusinesscreatev3) |
| `POST /2026Q3/profiles/business-profile` | [Create a business profile](/api-reference/profile/profilebusinesscreatev3) |
| `PUT /v2/profiles/{profileId}/business-profile` | [Update a business profile](/api-reference/legacy/profile/profilebusinessupdate) |
| `PUT /2026Q3/profiles/{profileId}/business-profile` | [Update a business profile](/api-reference/profile/profilebusinessupdate) |


## 2. Replace the legacy category fields

Replace a single `firstLevelCategory` and `secondLevelCategory` pair with an array containing one or more `industryCategories` values that best describe the business:

```json
{
  "industryCategories": [
    "SOFTWARE_DEVELOPMENT_PUBLISHING",
    "IT_CONSULTANCY_TECHNICAL_SUPPORT_SERVICES"
  ]
}
```

Update your data-collection interface so that a business can select more than one value where applicable.

Do not send duplicate values in the array.

### The two formats are mutually exclusive

Send **either** `industryCategories` **or** the `firstLevelCategory`/`secondLevelCategory` pair in a request, never both. A request containing both formats is rejected with a `400` HTTP error.

This applies on both create and update. On update, it means you cannot change from the legacy pair to `industryCategories` by sending the new field alongside the old ones: drop `firstLevelCategory` and `secondLevelCategory` from the request entirely and send only `industryCategories`.

Only the format you send is stored. Submitting `industryCategories` on an existing profile clears its legacy category values, and vice versa.

## 3. Update your response handling

Create and update responses return **only the format you sent**. The other format comes back as `null`:

- If you send `industryCategories`, the response contains your values and `firstLevelCategory`, `secondLevelCategory` and `descriptionOfBusiness` are `null`.
- If you send the legacy pair, the response contains those values and `industryCategories` is `null`.


If you read any of the legacy fields from a create or update response, switch to reading `industryCategories`.

`businessFreeFormDescription` is a separate free-form request field and is not affected by this migration.

## 4. Handle existing profiles

You do not need to backfill or re-submit categories for existing profiles.

Unlike create and update, [Retrieve a profile by ID](/api-reference/profile/profileget) derives the missing format and returns both:

- Profiles classified with `firstLevelCategory` and `secondLevelCategory` also return `industryCategories`.
- Profiles classified with `industryCategories` also return `firstLevelCategory`, `secondLevelCategory` and `descriptionOfBusiness` for backwards compatibility.


Where an `industryCategories` combination has no legacy equivalent, the derived `secondLevelCategory` is returned as `UNMAPPED`. Do not build logic that depends on the derived legacy values.

To change an existing profile's categories, submit `industryCategories` through the update business profile endpoint you already use.

## 5. Test your migration

In the sandbox:

1. Create a business profile with one `industryCategories` value.
2. Create a business profile with more than one `industryCategories` value.
3. Update an existing business profile to use `industryCategories`.
4. Send `industryCategories` **and** `firstLevelCategory`/`secondLevelCategory` in the same request and confirm you handle the resulting `400`.
5. Confirm that your requests omit `firstLevelCategory` and `secondLevelCategory`.
6. Confirm that your response handling does not require the deprecated fields.