# Subscribe to notifications about incoming transfers

This guide explains how to subscribe to webhook notifications for incoming transfers. Wise Platform uses a **notification + fetch** integration pattern: the webhook event signals that funds have been credited and provides the `incoming_transfer_id`, which you then use to retrieve the full transfer record — including debtor details, clearing identifiers, and the account details that received the payment — via the [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer).

This pattern applies uniformly across all supported payment rails, including SEPA, Faster Payments, ACH, domestic wire, and international Swift transfers received via your connected BIC.

## Incoming transfer credited event 

Subscribe to the `incoming-transfer#credited` event type to receive a notification when a transfer is credited to either your customer's [Local Account Details](/guides/product/accounts/bank-account-details) or your connected BIC. This is the recommended event type for all new integrations, regardless of the originating payment rail or currency.

### What this event tells you

This webhook signals that funds have been credited and provides you with the identifiers you need to fetch full transfer details in a follow-up API call

The payload contains:

- `data.incoming_transfer_id`: the `incoming_transfer_id` you use to fetch the complete incoming transfer resource from the [Incoming Transfer API endpoint](/api-reference/incoming-transfer/getincomingtransfer).
- `data.occurred_at`: the timestamp at which the transfer was credited to your balance.


For the full payload schema and field-level descriptions, see the [incoming transfer credited event](/api-reference/webhook-event/eventincomingtransfercredited) in the API reference.

### Fetch the full transfer record

After receiving an `incoming-transfer#credited` event, use the `incoming_transfer_id` from the payload to call the Incoming Transfers API and retrieve the complete transfer details:

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/incoming-transfers/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

The response includes:

- The credited amount, currency, and value date.
- Debtor details: name, address, and originating account identifiers.
- Debtor bank details: bank name, address, and BIC.
- Clearing and regulatory identifiers: LEI and Clearing System Member ID, where available.
- The specific account details that received the payment (IBAN, sort code and account number, routing and account number, etc.), enabling you to identify and reconcile the transfer against the correct customer.


Refer to the [Incoming Transfers API reference](/api-reference/incoming-transfer/getincomingtransfer) for the full response schema, field descriptions, and worked examples.

## Create a webhook subscription 

To subscribe to any of the event types described in this guide, create an application webhook subscription using the following endpoint. Pass the event type you want to subscribe to in the `trigger_on` field.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/applications/{clientKey}/subscriptions' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "name": "Webhook Subscription #1",
    "trigger_on": "transfers#state-change",
    "delivery": {
      "version": "4.0.0",
      "url": "https://your.webhook.url/12345"
    }
  }'
```

For request/response details, see the [API reference](/api-reference/webhook/webhookapplicationsubscriptioncreate).

## Rail-specific and auxiliary webhook events 

The following webhook event types provide rail-specific or auxiliary signals for incoming payments. They remain functional and may be appropriate in certain integration contexts, but they are narrower in scope than `incoming-transfer#credited`. New integrations should use `incoming-transfer#credited` as the primary notification mechanism, as it provides a unified, rail-agnostic signal and a consistent resource model across all payment types.

If your integration already uses any of the events described below, the sections below describe their behaviour and the data they provide. Consider whether `incoming-transfer#credited` in combination with the [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer) can cover your use case before relying on these events exclusively.

### `swift-in#credit` 

The `swift-in#credit` event was used to notify partners of incoming Swift transfers received via a connected BIC. It fires when a Swift payment is matched to a profile and credited to the corresponding balance.

The payload includes:

- The credited amount and currency.
- The Swift transaction reference and BIC of the sending institution.
- The matched profile ID, used to identify the receiving customer.
- A subset of debtor details extracted from the underlying Swift message.


`swift-in#credit` only covers transfers received via your connected BIC. It does not fire for local scheme payments (SEPA, Faster Payments, ACH). Integrations relying solely on this event will not be notified of pay-ins to Local Account Details. Migrate to `incoming-transfer#credited` to receive a unified signal across all payment rails.

For the full payload schema, see the [swift-in#credit event](/api-reference/webhook-event/eventswiftincredit) in the API reference.

### `swift#message-received` 

The `swift#message-received` event delivers the raw Swift message payload in PACS format for incoming Swift transfers. Unlike `swift-in#credit`, this event is not strictly a credit notification — it fires when the message is received and processed, and provides the underlying ISO 20022 message content for integrations that require structured access to the original Swift data.

The payload includes:

- `data.resource.content`: the raw Swift message, Base64-encoded.
- `data.resource.message_type`: the ISO 20022 message type identifier, for example:
  - `pacs.008.001.08` for customer credit transfers (FI-to-customer).
  - `pacs.009.001.08` for financial institution credit transfers (FI-to-FI).
- `data.action.profile_id`: the ID of the destination profile receiving the funds. This can be used to reconcile the payment against a specific customer profile.


This event is useful when your downstream systems require direct access to the structured Swift message — for example, to extract regulatory fields, intermediary bank details, or remittance information not exposed in higher-level Wise API responses.

`swift#message-received` is a supplementary event and does not replace a credit notification. For credit confirmation and reconciliation, use `incoming-transfer#credited` in combination with the [Incoming Transfer API](/api-reference/incoming-transfer/getincomingtransfer). Use `swift#message-received` only when access to the raw PACS message is specifically required.

### Example pacs.008 message content

For a pacs.008 (Customer Credit Transfer), the structure will look similar to the following:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<envelope:Envelope xmlns:envelope="urn:swift:xsd:envelope">
  <head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
    <head:Fr>
      <head:FIId>
        <head:FinInstnId>
          <head:BICFI>TRWIBEB3XXX</head:BICFI>
        </head:FinInstnId>
      </head:FIId>
    </head:Fr>
    <head:To>
      <head:FIId>
        <head:FinInstnId>
          <head:BICFI>RECEIVERBIC</head:BICFI>
        </head:FinInstnId>
      </head:FIId>
    </head:To>
    <head:BizMsgIdr>TRWIMCBPR2025092500000113262046HV0</head:BizMsgIdr>
    <head:MsgDefIdr>pacs.008.001.08</head:MsgDefIdr>
    <head:BizSvc>swift.cbprplus.02</head:BizSvc>
    <head:CreDt>2025-09-25T14:10:20.713+00:00</head:CreDt>
  </head:AppHdr>
  <pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
    <pacs:FIToFICstmrCdtTrf>
      <pacs:GrpHdr>
        <pacs:MsgId>TRWIMCBPR2025092500000113262046HV0</pacs:MsgId>
        <pacs:CreDtTm>2025-09-25T14:10:20.689+00:00</pacs:CreDtTm>
        <pacs:NbOfTxs>1</pacs:NbOfTxs>
        <pacs:SttlmInf>
          <pacs:SttlmMtd>INGA</pacs:SttlmMtd>
        </pacs:SttlmInf>
      </pacs:GrpHdr>
      <pacs:CdtTrfTxInf>
        <pacs:PmtId>
          <pacs:InstrId>1321370   80131</pacs:InstrId>
          <pacs:EndToEndId>NOTPROVIDED</pacs:EndToEndId>
          <pacs:UETR>e34242e5-631b-4c58-a37a-3f5c451239e6</pacs:UETR>
        </pacs:PmtId>
        <pacs:PmtTpInf>
          <pacs:InstrPrty>NORM</pacs:InstrPrty>
          <pacs:SvcLvl>
            <pacs:Cd>G001</pacs:Cd>
          </pacs:SvcLvl>
        </pacs:PmtTpInf>
        <pacs:IntrBkSttlmAmt Ccy="GBP">390</pacs:IntrBkSttlmAmt>
        <pacs:IntrBkSttlmDt>2025-09-25</pacs:IntrBkSttlmDt>
        <pacs:InstdAmt Ccy="EUR">640</pacs:InstdAmt>
        <pacs:XchgRate>0.871234</pacs:XchgRate>
        <pacs:ChrgBr>SHAR</pacs:ChrgBr>
        <pacs:ChrgsInf>
				<pacs:Amt Ccy="EUR">0</pacs:Amt>
				<pacs:Agt>
					<pacs:FinInstnId>
						<pacs:BICFI>CHASDEFXXXX</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:Agt>
			</pacs:ChrgsInf>        
        <pacs:ChrgsInf>
				<pacs:Amt Ccy="GBP">10</pacs:Amt>
				<pacs:Agt>
					<pacs:FinInstnId>
						<pacs:BICFI>TRWIBEB3XXX</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:Agt>
			</pacs:ChrgsInf>
        <pacs:PrvsInstgAgt1>
          <pacs:FinInstnId>
            <pacs:BICFI>CMCIFRPAXXX</pacs:BICFI>
          </pacs:FinInstnId>
        </pacs:PrvsInstgAgt1>
        <pacs:PrvsInstgAgt2>
          <pacs:FinInstnId>
            <pacs:BICFI>CHASDEFXXXX</pacs:BICFI>
          </pacs:FinInstnId>
        </pacs:PrvsInstgAgt2>
        <pacs:InstgAgt>
          <pacs:FinInstnId>
            <pacs:BICFI>TRWIBEB3XXX</pacs:BICFI>
          </pacs:FinInstnId>
        </pacs:InstgAgt>
        <pacs:InstdAgt>
          <pacs:FinInstnId>
            <pacs:BICFI>RECEIVERBIC</pacs:BICFI>
          </pacs:FinInstnId>
        </pacs:InstdAgt>
        <pacs:Dbtr>
          <pacs:Nm>DEBTOR NAME</pacs:Nm>
          <pacs:PstlAdr>
            <pacs:AdrLine>ADDRESS LINE 1</pacs:AdrLine>
            <pacs:AdrLine>ADDRESS LINE 2</pacs:AdrLine>
          </pacs:PstlAdr>
          <pacs:CtryOfRes>COUNTRY</pacs:CtryOfRes>
        </pacs:Dbtr>
        <pacs:DbtrAcct>
          <pacs:Id>
            <pacs:IBAN>GB09IFXS11111111111111</pacs:IBAN>
          </pacs:Id>
        </pacs:DbtrAcct>
        <pacs:DbtrAgt>
          <pacs:FinInstnId>
            <pacs:BICFI>CMCIFRPPXXX</pacs:BICFI>
          </pacs:FinInstnId>
        </pacs:DbtrAgt>
        <pacs:CdtrAgt>
          <pacs:FinInstnId>
            <pacs:BICFI>SWNBFR22XXX</pacs:BICFI>
          </pacs:FinInstnId>
        </pacs:CdtrAgt>
        <pacs:Cdtr>
          <pacs:Nm>CREDITOR NAME</pacs:Nm>
          <pacs:PstlAdr>
            <pacs:TwnNm>NOTPROVIDED</pacs:TwnNm>
            <pacs:Ctry>CREDITOR COUNTRY</pacs:Ctry>
          </pacs:PstlAdr>
        </pacs:Cdtr>
        <pacs:CdtrAcct>
          <pacs:Id>
            <pacs:IBAN>GB09IFXS11111111111112</pacs:IBAN>
          </pacs:Id>
        </pacs:CdtrAcct>
        <pacs:RgltryRptg>
          <pacs:Dtls>
            <pacs:Inf>/ORDERRES/FR</pacs:Inf>
            <pacs:Inf>/BENEFRES/FR</pacs:Inf>
          </pacs:Dtls>
        </pacs:RgltryRptg>
        <pacs:RmtInf>
          <pacs:Ustrd>EXAMPLE REFERENCE</pacs:Ustrd>
        </pacs:RmtInf>
      </pacs:CdtTrfTxInf>
    </pacs:FIToFICstmrCdtTrf>
  </pacs:Document>
</envelope:Envelope>
```

For the full event payload schema and examples, see the [swift#message-received event](/api-reference/webhook-event/eventswiftmessagereceived) in the API reference.

### Balance-related events 

Earlier integrations used balance and transfer state events as indirect signals for incoming payment detection. These events are general-purpose notifications not specific to incoming transfers, and their use for receive-flow processing is not recommended.

#### `balances#update`

The `balances#update` event fires whenever a balance changes, including credits from incoming transfers, debits from outbound payments, and any other balance-affecting operation. Because it is not scoped to incoming transfers specifically, it provides no debtor or payment rail context and requires additional API calls to determine the source of the balance change.

#### `transfers#state-change`

The `transfers#state-change` event covers state transitions for outbound transfer objects created via the Wise Platform transfers API.

Do not use `balances#update` or `transfers#state-change` as the primary mechanism for detecting incoming transfers. These events do not carry incoming transfer context and will not provide the `incoming_transfer_id` required to retrieve full transfer details. Migrate to `incoming-transfer#credited` for accurate and complete incoming transfer detection.