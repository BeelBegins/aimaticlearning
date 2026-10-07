# Settlement cycle

After funding multiple transfers over a settlement period, you should then settle for those transfers in bulk. How you do this depends on how refunds are processed for the integration you are building.

There are two steps involved in the settlement process:

1. Sending the settlement journal request to Wise.
2. Sending the actual funds to Wise via bank transfer.


Throughout the settlement period you will have called the funding endpoint multiple times to fund transfers. At the end of each settlement period (usually daily), you must make a request that sends a journal containing all transfers you wish to settle, and then send the total amount of funds to the pre-agreed deposit bank account.

## Settlement flow summary 

Run a process to perform settlement. This can be ad hoc or scheduled to run at the same time daily.

The process should:

- Query for all transfers that are yet to be settled with Wise (all transfers you have called the funding endpoint for since the previous run of the settlement process)
- Query for all completed refunds that are yet to be notified to Wise (all refunded transfers you have been notified using one of the refund methods since the previous run of the settlement process. *Note: This is only applicable for the Net Settlement model.*)


Once you have performed these queries:

1. Calculate the `balanceTransfer` amount based on the logic described above.
2. Get the **Client Credentials Token** in order to call the settlement journal endpoint.
3. Call the settlement journal endpoint first, to submit the settlement journal.
4. Deposit the exact total amount of funds in the settlement journal to the pre-agreed deposit bank account with Wise, using the same settlement reference used in the settlement journal.


Total settlement amount calculation
`totalSettlementAmount` = Sum of (`sourceAmount` * `exchangeRate`)

The settlement journal endpoint receives the settlement and performs basic verification, such as JSON format checks. Additional verification will be performed asynchronously when the transfers are actually settled.

## Send a settlement journal 

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/settlements \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "TRUSTED_BULK_SETTLEMENT",
    "settlementReference": "TPFB190322",
    "settlementDate": "2019-03-22T23:59:59-05:00",
    "transfers": [
      {
        "id": 125678,
        "date": "2019-03-22T10:00:12-05:00",
        "sourceAmount": 23.24,
        "sourceCurrency": "USD",
        "customerName": "Joe Bloggs",
        "partnerReference": "11111",
        "comment": "Extra Data"
      },
      {
        "id": 178889,
        "date": "2019-03-23T12:40:05-05:00",
        "sourceAmount": 125.67,
        "sourceCurrency": "USD",
        "customerName": "Mat Newman",
        "partnerReference": "11112",
        "comment": "Extra Data"
      }
    ],
    "refundedTransfers": [
      {
        "id": 178880,
        "partnerReference": "11108"
      }
    ],
    "balanceTransfer": 0
  }'
```

For full request/response details, see the [bulk settlement reference](/api-reference/bulk-settlement/bulksettlementjournalcreate).