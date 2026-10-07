# Fund transfers

Once a transfer is created, it must be funded. The method you use to fund transfers depends on two factors:

- **Funding model**: Determines *when* the settlement funds reach Wise relative to the payout. Wise supports **pre-funding** (funds arrive before payout) and **post-funding** (payout executes first, settlement happens later).
- **Funding method**: Determines *how* the funds are sent. Options include funding from a pre-loaded Wise balance, sending a bank payment per transfer, or settling multiple transfers in a single payment.


You can use a single approach for all transfers, or combine methods depending on the currency, corridor, or transfer volume. You’ll work with your implementation team during onboarding to determine your model and method.

Once a transfer is funded, the exchange rate is locked and the transfer status changes from `incoming_payment_waiting` to `processing`. At this point, the transfer cannot be cancelled via API.

Fund the correct amount
Be sure to fund the exact amount specified in the final quote object. Under- or over-funding may cause a reconciliation failure or delay the transfer. Also note that if the rate expires before the transfer is funded, the target amount may change or the transfer may be automatically cancelled after 14 days.

## Pre-funding

With pre-funding, settlement funds must reach Wise *before* the payout is initiated to the recipient. Pre-funding is the default for most correspondent partners and supports the funding from balance and direct deposit methods.

### Fund from balance

The fund from balance method debits your Wise multi-currency account (MCA) balance immediately upon the fund request and is the fastest option for transfer processing.

**Requirements**:

- Your MCA must hold a sufficient balance in the source currency of the transfer.
- The balance currency must match the transfer source currency. Cross-currency balance funding is not currently supported.


**How it works**:

1. After creating the transfer, call the [Fund a transfer endpoint](/api-reference/transfer/transferfund) with `type` set to `BALANCE` in the request body.
2. Wise debits your balance and begins processing the payout.


#### Sample request

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/profiles/123456789/transfers/16521632/payments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "type": "BALANCE",
    "balanceId": 45678901
  }'
```

Not all currencies supported
Funding from a balance requires the currency supports carrying a balance in the MCA. Not all currencies are currently supported for MCA (for example, Wise does not currently support holding a balance for IDR).

### Direct deposit

Direct deposit means sending a bank payment directly from your institution's bank account to Wise's collection account. Each transfer is funded individually and identified with a unique payment reference. This is often referred to as **transfer-by-transfer**, as it funds one payout transfer with a single transfer to fund it (that is, in a 1-to-1 relationship).

This method is suitable for partners on instant or fast domestic payment rails (such as FPS for GBP), where per-transfer bank payments can be initiated quickly and at low cost.

**To fund via direct deposit after creating a transfer**:

1. Call the [Get pay-in deposit details endpoint](/api-reference/payin-deposit-detail/payindepositdetailget) to retrieve Wise's bank account details and the payment reference for the transfer.
2. Use the details from the response to initiate a bank payment from your account to the Wise bank account provided. 
In the **payment reference** field of your bank transfer, include the transfer id value prefixed with the letter `T`. For example, if the transfer ID is `80106743`, enter `T80106743` in the payment reference field. Wise uses this reference to automatically link the incoming payment to the correct transfer.


When Wise receives the funds and matches the payment reference to the transfer, the transfer moves to `processing`.

Match account and profile names
The sender name on the incoming bank payment must match the business name on the Wise business profile that created the transfer. Mismatches may delay linking and require manual intervention.

## Post-funding

Post-funding allows you to fund multiple transfers with a single payment. With Post-Funding, you separate payment confirmation and settlement, allowing you to defer settlement after payment execution.

Instead of pre-loading your balance or sending a bank payment before each payout, Wise will fund the transfers upon receiving transfer instructions. You then settle the total for all executed transfers with us on a pre-agreed schedule, for example daily T+1.

### Availability

Post-funding is currently available to correspondent partners contracted with Wise Platform Ltd (WPL, UK entity), with other entities coming soon. Contact your implementation team to discuss eligibility if you are interested.

### How post-funding works

Once Wise enables post-funding for your integration, we assign a post-funding limit to your profile, denominated in a single currency.

1. Create a quote and a transfer and fund the transfer using the [Fund a transfer endpoint](/api-reference/transfer/transferfund) with `type` set to `BALANCE`. This is the same endpoint and type used for standard funding from balance.
2. Where it is not possible to pre-fund based on your available balance, Wise funds the transfer and reflects the debit for the transfer in your balance. Wise then updates the balance to reflect the *total unsettled amount* based on all executed transfers that are pending settlement.
3. You then settle multiple transfers with a single settlement payment by sending funds to your Wise account (per currency) by the agreed settlement deadline (for example, T+1).
4. Wise recognises these funds are to settle the unsettled transfers and updates your balance to reflect settlement (for example, update the balance to $0 USD).


**Key details**:

- If a transfer would cause you to exceed your limit, the funding request is rejected. The transfer remains in `incoming_payment_waiting` until you settle and have the remaining limit available or available funds.
- Post-funding can only be used for transfers. Other balance operations (such as balance conversions or card payments) cannot draw on the post-funding limit.
- Wise charges a fee for the operational cost of this method. Pricing details are agreed upon when post-funding is set up for the account.


### Monitoring your available usage

- Use the [Get Total Funds endpoint](/api-reference/balance/totalfunds) to check your current available post-funding product usage limit across all currencies.
- Subscribe to the balance update webhook (`”event_type”: “balances#update”`) to receive notifications when your balance is debited or credited.
- Subscribe to the limit threshold webhook (`"event_type": "profiles#overdraft-limit-threshold"`) to receive alerts when your post-funding usage approaches or exceeds a configured threshold (default is 70%).


## Bulk settlement

Bulk settlement allows you to fund multiple transfers with a single payment. Rather than sending individual bank payments per transfer, you submit a *settlement journal* that lists the transfer IDs to be funded, and then send one aggregated bank payment to cover all listed transfers.

No longer available for new integrations
The bulk settlement method is no longer available for new correspondent partner integrations.

**To fund via bulk settlement**:

1. Create transfers as usual. Transfers remain in `incoming_payment_waiting` status.
2. Call the [send a settlement journal endpoint](/api-reference/bulk-settlement/bulksettlementjournalcreate) and in the request body include an array of transfer IDs to be funded.
3. Send a single bank payment to Wise for the total amount of the transfers listed in the settlement journal.


Once Wise receives and links the payment, all transfers in the journal move to `processing`.

### Sample settlement journal request

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