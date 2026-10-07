# Language Support

See our translation and language support

Internationalisation support for translation of strings returned by the API is supported for endpoints on the right.

When calling these endpoints, you can include an `Accept-Language` header or a query string parameter of `statementLocale` with a supported language code as the value then strings will be returned in the requested language. The languages supported by Wise are:

| Language | Code |
|  --- | --- |
| American English | en_US |
| Arabic | ar |
| British English | en |
| Chinese | zh |
| Czech | cs |
| Danish | da |
| Dutch | nl |
| French | fr |
| German | de |
| Hebrew | he |
| Hungarian | hu |
| Italian | it |
| Japanese | ja |
| Korean | ko |
| Norwegian | nb |
| Polish | pl |
| Portuguese | pt |
| Romanian | ro |
| Russian | ru |
| Spanish | es |
| Swedish | sv |
| Turkish | tr |
| Ukrainian | uk |


If you request an unsupported language then British English will be returned by default.

Language Supported Endpoints - Header
* `/currencies`
* `/quotes`
* `/quotes/<quoteId/quoteUuid>/account-requirements`
* `/accounts`
* `/transfers`
* `/transfer-requirements`
* `/profiles/<profileId>/transfers/<transferId>/deposit-details/bank-transfer`


Language Supported Endpoints - Query String
* `/profiles/<profileId>/balance-statements/<balanceId>/statement`