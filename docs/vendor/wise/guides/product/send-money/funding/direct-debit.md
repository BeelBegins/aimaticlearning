# Fund transfers with direct debit

Pull funds from a bank account to fund your transfers.

To fund a transfer using direct debit, you must work with two primary resources: **Payment Instruments** and **Payins**.

- A **Payment Instrument** is a saved pre-authorised funding source, such as a bank account, from which you can pull funds.
- A **Payin** is the request you initiate to pull a specific payment from that instrument.


## Supported schemes

| Scheme | Currency | Region | Status |
|  --- | --- | --- | --- |
| BACS | GBP | United Kingdom | Live |
| SEPA | EUR | Europe | Live |
| ACH | USD | United States | Beta |
| EFT | CAD | Canada | Beta |


**ACH** and **EFT** support is currently in beta. While fully functional and supported, the API may undergo changes based on partner feedback.

## How direct debit payin funds transfers  

The Direct Debit API uses the `paymentInstrumentId` and the `payinSessionId` from a new transfer to create a new Payin.

Once the direct debit payin is received, the associated transfer is funded.
The funds are never shown as a credit on your balance and are used immediately.

### Summary of requests 

Follow these steps to implement direct debits via the API:

1. **Create the Payment Instrument**: Send a request to `POST /profiles/{{profileId}}/payment-instruments` to initiate the authorization flow for a new funding source.
2. **Connect the Payment Instrument**: Send a request to `POST /profiles/{{profileId}}/payment-instruments/{{paymentInstrumentId}}/manual-confirmation` to confirm the payment instrument's details are correct.
  * This leads to a `CONNECTED` Payment Instrument, which then supports the submission of new Payins.
3. **Create a transfer**: As with any process to send money on Wise Platform, you must create a quote and then create a transfer using `POST /transfers`.
  * Capture the `payinSessionId` from the response.
4. **Create a Payin**: Send a request, including the `payinSessionId`, to `POST /profiles/{{profileId}}/payment-instruments/{{paymentInstrumentId}}/payins`.
  * Once this payin is complete, the transfer is funded and your money is sent to the transfer recipient.
5. **Check status**: Send a `GET` request for either a payment instrument or a payin to retrieve its status at any time.


## Next steps

- [Create and connect a payment instrument](/guides/product/send-money/funding/direct-debit/create-payment-instrument).
- [Create and track payins](/guides/product/send-money/funding/direct-debit/create-payin).
- [Learn more about sending money](/guides/product/send-money).
- Review the authorization and compliance requirements for your region:
  - [UK and Europe: Direct Debit mandates](/guides/product/send-money/funding/direct-debit/mandates-standards)
  - [United States: ACH authorization requirements](/guides/product/send-money/funding/direct-debit/ach-debits-us)
  - [Canada: EFT debit requirements](/guides/product/send-money/funding/direct-debit/eft-debits-ca)