# Card Address Validation

To create a card order, make sure to follow country-specific address fields and validation. If your country is not listed below, use the [Other countries](#other-countries) format.

For card creation, the `address` requirement depends on the card type:

- **Physical Cards (Required)**: Used as the delivery address to ship the card and for AVS checks in countries where required.
- **Virtual Cards (Optional)**: If provided, this acts as the billing address. If omitted, the profile address is used as the fallback. In either scenario, the address is used for AVS checks in countries where required.


We do not support PO BOX addresses.

**Supported countries:**

- [Brazil](#brazil) — uses different address fields (`addressNumber`, `address`, `district`, `complement`)
- [Australia](#australia) — requires `state` field with specific state codes
- [Other countries](#other-countries) — default format using `firstLine`, `secondLine`, `thirdLine`


## Brazil

### Address fields

| Field | Type | Max length | Required | Description |
|  --- | --- | --- | --- | --- |
| `addressNumber` | String | 6 | Yes | Card holder's address number |
| `address` | String | 100 | Yes | Card holder's address |
| `district` | String | 80 | Yes | Card holder's district |
| `complement` | String | 28 | No | Card holder's complement |
| `postCode` | String | 8 | Yes | Card holder's postal code |
| `city` | String | 30 | Yes | Card holder's city |
| `state` | String | 10 | Yes | Card holder's state (see state codes below) |
| `country` | String | 2 | Yes | `BR` |


### State codes

| Code | State |
|  --- | --- |
| `AC` | Acre |
| `AL` | Alagoas |
| `AP` | Amapá |
| `AM` | Amazonas |
| `BA` | Bahia |
| `CE` | Ceará |
| `DF` | Distrito Federal |
| `ES` | Espírito Santo |
| `GO` | Goiás |
| `MA` | Maranhão |
| `MT` | Mato Grosso |
| `MS` | Mato Grosso do Sul |
| `MG` | Minas Gerais |
| `PA` | Pará |
| `PB` | Paraíba |
| `PR` | Paraná |
| `PE` | Pernambuco |
| `PI` | Piauí |
| `RJ` | Rio de Janeiro |
| `RN` | Rio Grande do Norte |
| `RS` | Rio Grande do Sul |
| `RO` | Rondônia |
| `RR` | Roraima |
| `SC` | Santa Catarina |
| `SP` | São Paulo |
| `SE` | Sergipe |
| `TO` | Tocantins |


### Example address

```json
{
    "address": {
        "addressNumber": "134",
        "address": "Rua Moacir da Silva Mota",
        "district": "Tancredo Neves",
        "complement": null,
        "state": "RR",
        "city": "Boa Vista",
        "postCode": "69313488",
        "country": "BR"
    }
}
```

### Validation

Field validation is performed on the following criteria:

- value is required
- value length
- valid postCode for a country
- valid state


Use the [validate address endpoint](/api-reference/card-order/cardordervalidateaddress) to check your address before creating a card order.

## Australia

### Address fields

| Field | Type | Max length | Required | Description |
|  --- | --- | --- | --- | --- |
| `firstLine` | String | 30 | Yes | Card holder's address |
| `secondLine` | String | 30 | No | Card holder's address |
| `thirdLine` | String | 30 | No | Card holder's address |
| `postCode` | String | 10 | Yes | Card holder's postal code |
| `city` | String | 30 | Yes | Card holder's city |
| `state` | String | 30 | Yes | Card holder's state (see state codes below) |
| `country` | String | 2 | Yes | `AU` |


### State codes

| Code | State |
|  --- | --- |
| `ACT` | Australian Capital Territory |
| `NSW` | New South Wales |
| `NT` | Northern Territory |
| `QLD` | Queensland |
| `SA` | South Australia |
| `TAS` | Tasmania |
| `VIC` | Victoria |
| `WA` | Western Australia |


### Example address

```json
{
    "address": {
        "firstLine": "72 Botany Rd",
        "secondLine": "New South Wales",
        "thirdLine": null,
        "postCode": "2017",
        "city": "Sydney",
        "state": "NSW",
        "country": "AU"
    }
}
```

### Validation

Field validation is performed on the following criteria:

- value is required
- value length
- valid postCode for a country
- valid state


Use the [validate address endpoint](/api-reference/card-order/cardordervalidateaddress) to check your address before creating a card order.

## Other countries

### Address fields

| Field | Type | Max length | Required | Description |
|  --- | --- | --- | --- | --- |
| `firstLine` | String | 30 | Yes | Card holder's address |
| `secondLine` | String | 30 | No | Card holder's address |
| `thirdLine` | String | 30 | No | Card holder's address |
| `postCode` | String | 10 | Yes | Card holder's postal code |
| `city` | String | 30 | Yes | Card holder's city |
| `state` | String | 30 | No | Card holder's state |
| `country` | String | 2 | Yes | ISO 3166-1 alpha-2 country code |


### Example address

```json
{
    "address": {
        "firstLine": "1 Paya Lebar Link",
        "secondLine": "#13-06 PLQ 2",
        "thirdLine": "Paya Lebar Quarter",
        "postCode": "408533",
        "city": "Singapore",
        "state": null,
        "country": "SG"
    }
}
```

### Validation

Field validation is performed on the following criteria:

- value is required
- value length
- valid postCode for a country


Use the [validate address endpoint](/api-reference/card-order/cardordervalidateaddress) to check your address before creating a card order.

## Validation response

The [validate address endpoint](/api-reference/card-order/cardordervalidateaddress) returns a collection of errors on fields that did not pass the format validation. A successful address validation will return an empty errors collection.

```json
{
    "errors": [
        {
            "field": "city",
            "message": "Required Field"
        },
        {
            "field": "postCode",
            "message": "Please enter a valid postcode"
        },
        {
            "field": "firstLine",
            "message": "Must be less than 30 characters"
        }
    ]
}
```