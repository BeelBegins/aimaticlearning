# Manage disputes

These APIs allow you to manage disputes raised via either API or dynamic flow.

## List disputes 

List disputes for a profile.

```shell curl
curl -i -X GET \
  'https://api.wise.com/2026Q4/spend/profiles/16605997/disputes?status=ACTIVE&transactionId=2040&pageSize=10&pageNumber=1' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/disputes/disputelist).

## Get dispute 

Retrieve a single dispute by its ID.

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/spend/profiles/16605997/disputes/51e2dc60-9e4b-4ff5-b917-b90cc5e1ecfb \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

For request/response details, see the [API reference](/api-reference/disputes/disputeget).

## Withdraw dispute 

You can withdraw a dispute only when the `canWithdraw` field is `true`.

```shell curl
curl -i -X PUT \
  https://api.wise.com/2026Q4/spend/profiles/16605997/disputes/51e2dc60-9e4b-4ff5-b917-b90cc5e1ecfb/status \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "status": "CLOSED"
  }'
```

For request/response details, see the [API reference](/api-reference/disputes/disputewithdraw).