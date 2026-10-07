# Address Requirements

Address requirements vary by country. Use the address requirements endpoints to dynamically discover which fields are needed before creating an address. You can use this to build a dynamic UI that adapts to each country's requirements.

## How it works

### Step 1: Get initial requirements and render fields

Call [GET /address-requirements](/api-reference/address/addressrequirementsget) to retrieve the initial list of required fields, then render them in your UI.

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/address-requirements \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

The response contains four base fields:

- `country` (select field with list of values)
- `city` (text field)
- `postCode` (text field)
- `firstLine` (text field)


```json 200 application/json
[
  {
    "type": "address",
    "fields": [
      {
        "name": "Country",
        "group": [
          {
            "key": "country",
            "type": "select",
            "refreshRequirementsOnChange": true,
            "required": true,
            "displayFormat": null,
            "example": "Germany",
            "minLength": null,
            "maxLength": null,
            "validationRegexp": null,
            "validationAsync": null,
            "valuesAllowed": [
              {
                "key": "US",
                "name": "United States"
              },
              {
                "key": "GB",
                "name": "United Kingdom"
              }
            ]
          }
        ]
      }
    ]
  }
]
```

```json 429 application/json
{}
```

### Step 2: Check for dynamic fields

When the user selects a value, check if that field has `refreshRequirementsOnChange: true`. The `country` field has this set to `true`, meaning additional fields may be required depending on the selected country.

### Step 3: Get context-specific requirements and update UI

Call [POST /address-requirements](/api-reference/address/addressrequirementspost) with the current form state to discover additional fields, then update your UI with any new fields returned.

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/address-requirements \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "details": {
      "country": "US"
    }
  }'
```

For example, posting `{"details": {"country": "US"}}` adds `state` to the list of required fields. Posting `{"details": {"country": "GB"}}` does not add any additional fields.

### Step 4: Repeat until complete

Continue calling POST with updated values whenever a field with `refreshRequirementsOnChange: true` changes.

For example, posting `{"details": {"country": "CA"}}` adds `occupations` to the list of fields. Posting `{"details": {"country": "US", "state": "AL"}}` does not.

Once all dynamic fields are resolved, you have the complete set of fields needed to create a valid address.

For full endpoint details, see the [Address API Reference](/api-reference/address).