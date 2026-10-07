# 

### BIC/SWIFT numbers for Sandbox testing

Sandbox requires a valid recipient BIC (Business Identifier Code) when processing test payments to the EU,
failure to do this can result in an error when simulating the fund action of a transfer.

Use the following BIC/IBAN combinations in sandbox to simulate a successful payment:

* **IBAN:** "BE57 9677 4768 2935", **BIC:** "TRWIBEB1"


We recommend you use a confirmed supported BIC when testing, but if your test data does not specify one of the above examples
then please be prepared to re-attempt with different test data in the event a BIC is not accepted and the simulation fails.