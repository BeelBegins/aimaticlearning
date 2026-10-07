# Personal API tokens

Create and use a personal token with a Wise business account.

A personal API token authenticates requests to the Wise API for your own Wise business account, allowing you to [automate certain actions in your payouts workflow](/guides/product/send-money/use-cases/payouts-smbs).

By generating a personal API token for your business account, you can authorize your application to programmatically generate quotes, collect and store recipient account details, prepare payments by drafting transfers, and track transfer statuses.

## Limitations

Personal API tokens are limited to the endpoints for [creating quotes](/api-reference/quote/quotecreate), [retrieving](/api-reference/recipient/recipientlist) and [creating recipients](/api-reference/recipient/recipientcreate), [creating transfers](/api-reference/standard-transfer/transfercreate) and [batch groups](/api-reference/batch-group/batchgroupcreate), and tracking transfer events.

[Funding transfers](/guides/product/send-money/funding) and [retrieving balance statements](/api-reference/balance-statement/balancestatementget) via API are not supported except for accounts based in the US, Canada, Australia, New Zealand, Singapore, and Malaysia.

If you need more advanced access to the Wise API, [contact our team](https://wise.com/platform/contact) to discuss a partnership agreement.

## Create a personal API token

1. Log into your [Wise.com](https://wise.com) business account.
2. Go to **Your Account** -> **Connect and manage apps** -> **API tokens**.
3. Click **Add new token**.
4. Complete 2-step verification when prompted.
5. Copy and securely store your token (it will only be shown once).


Keep your token secure!
* Store your token in a secrets manager, never in code or version control.
* Don't log your token or expose it in URLs.
* Revoke and regenerate if you suspect a token is compromised.
* Use separate tokens for different applications if needed.


## Using a personal API token

Include the token in the `Authorization` header of every API request.

**Example**:

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/profiles \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Personal API tokens remain active until revoked.

## Revoking a token

If your token is compromised or no longer needed:

1. Log into your [Wise.com](https://wise.com) business account.
2. Go to **Your Account** -> **Connect and manage apps** -> **API tokens**.
3. Find the token and choose **Revoke**.


The token will stop working immediately.