# Embedded SCA component

By default, your customers are expected to authenticate themselves by entering their Wise password as well as an OTP code sent to their phone.

If you prefer your customers to use a different authentication method, please contact your implementation manager.

## JavaScript library 

We have created a library, available on [npmjs.com](https://www.npmjs.com/package/@transferwise/approve-api-action-helpers), that allows you to embed the Wise SCA flow into your application as a UI component, making it easier to integrate strong customer authentication (SCA) into your application.

We have also provided also a sample app on [GitHub](https://github.com/transferwise/wise-platform-samples/tree/main/strong-customer-authentication) showcasing how to use that library.

## Detailed workflow 

Here is a step-by-step workflow with example commands to process a payment (which may vary slightly depending on the exact versions of utilities used).

A similar example is also available in our [code samples repository](https://github.com/transferwise/wise-platform-samples/tree/main/strong-customer-authentication).

Your customer makes a request which requires strong authentication. The call is made using our [SCA helper library](https://www.npmjs.com/package/@transferwise/approve-api-action-helpers) from your frontend.

SCA helper library
```code
import { create, Mode } from '@transferwise/approve-api-action-helpers';
const request = create({ mode: Mode.PRODUCTION });
const res = await request('/tw-fund-payment', { method: 'POST', data: { ... } });
```

Your server forwards the request to Wise Platform API.

**Request**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/transfers/16521632/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "BALANCE"
  }'
```

The request is declined with HTTP status `403 / Forbidden` with the following response headers:

- `X-2FA-Approval-Result`: `REJECTED`
- `X-2FA-Approval` containing the one-time token (OTT) value, which is what needs to be signed.


Response
```http
HTTP/1.1 403 Forbidden
Date: Fri, 03 Jan 2020 12:34:56 GMT
Content-Type: application/json;charset=UTF-8
x-2fa-approval-result: REJECTED
x-2fa-approval: be2f6579-9426-480b-9cb7-d8f1116cc8b9
...
{
    "timestamp": "2020-01-03T12:34:56.789+0000",
    "status": 403,
    "error": "Forbidden",
    "message": "You are forbidden to send this request",
    "path": "/profiles/{profileId}/transfers/{transferId}/payments"
}
```

* Your server reflects the response status and the header `x-2fa-approval` back to your frontend.
* Our frontend library now understands that SCA is required and asks the customer to pass challenges (such as password).
* When customer has completed challenges, our frontend library automatically triggers the initial call (1) again, but this time it includes the OTT (`x-2fa-approval` header) and sends it to your backend.


**Request after implementing SCA**

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/transfers/16521632/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "BALANCE"
  }'
```

Your server repeats the initial request above with the addition of the one-time token.

Response after implementing SCA
```code
HTTP/1.1 200 OK
Date: Fri, 03 Jan 2020 12:34:56 GMT
Content-Type: application/json;charset=UTF-8
x-2fa-approval-result: APPROVED

{
  "type": "BALANCE",
  "status": "COMPLETED",
  "errorCode": null
}
```

Customer has authenticated and the action is completed. You will receive a response with `x-2fa-approval-result` status `APPROVED` in headers.