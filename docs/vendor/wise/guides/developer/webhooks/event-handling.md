# Event handling

How to create a webhook event handler.

To receive events, you must set up a publicly accessible HTTPS endpoint and create a subscription that uses this endpoint. Our system sends HTTP POST requests to this endpoint with events encoded using JSON.

Your system must respond with a `2xx`-series HTTP status code within 5 seconds of receiving a request to acknowledge successful delivery of a webhook notification.

If this "success" response is not received by us within this time period, we consider the delivery attempt as failed and will later try to resend the message. We attempt to redeliver messages, up to 25 times, at increasing intervals over a two week period.

A recommended strategy for handling notifications is to do some basic validation and then store the notification for processing by a separate server process. This prevents our delivery system from considering delivery attempts as failed if your handler does not respond in time due to a long handling process.

Since events may arrive out of order due to retries or network conditions, you should use the event's ordering fields rather than the delivery order to determine the correct sequence. See the [Event ordering guide](/guides/developer/webhooks/event-ordering) for details.

## Event HTTP requests 

Event HTTP requests contain custom headers and the bodies have a type-specific structure.

Events using version 2 of our type schema contain a common base structure with additional event-specific details.

### Signature header `X-Signature-SHA256`

Each outgoing webhook request is signed.

You should verify that any request you handle was sent by Wise and has not been forged or tampered with. You should not process any requests with signatures that fail verification.

Signatures are generated using an RSA key and SHA256 digest of the message body. They are transmitted using the `X-Signature-SHA256` request header and are Base64 encoded.

In this [repository](https://github.com/transferwise/digital-signatures-examples/tree/main/verify-webhook-signature), you can see some reference implementations in Java, Node and Ruby.

### Delivery ID header `X-Delivery-Id`

Each outgoing notification is assigned a unique delivery UUID.

### Test notification header `X-Test-Notification`

This header is present with the value `true` if the notification is a test message.

Test messages can be sent to verify callback URLs when subscriptions are being set up.

Production public key
```bash
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvO8vXV+JksBzZAY6GhSO
XdoTCfhXaaiZ+qAbtaDBiu2AGkGVpmEygFmWP4Li9m5+Ni85BhVvZOodM9epgW3F
bA5Q1SexvAF1PPjX4JpMstak/QhAgl1qMSqEevL8cmUeTgcMuVWCJmlge9h7B1CS
D4rtlimGZozG39rUBDg6Qt2K+P4wBfLblL0k4C4YUdLnpGYEDIth+i8XsRpFlogx
CAFyH9+knYsDbR43UJ9shtc42Ybd40Afihj8KnYKXzchyQ42aC8aZ/h5hyZ28yVy
Oj3Vos0VdBIs/gAyJ/4yyQFCXYte64I7ssrlbGRaco4nKF3HmaNhxwyKyJafz19e
HwIDAQAB
-----END PUBLIC KEY-----
```

Sandbox public key
```bash
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwpb91cEYuyJNQepZAVfP
ZIlPZfNUefH+n6w9SW3fykqKu938cR7WadQv87oF2VuT+fDt7kqeRziTmPSUhqPU
ys/V2Q1rlfJuXbE+Gga37t7zwd0egQ+KyOEHQOpcTwKmtZ81ieGHynAQzsn1We3j
wt760MsCPJ7GMT141ByQM+yW1Bx+4SG3IGjXWyqOWrcXsxAvIXkpUD/jK/L958Cg
nZEgz0BSEh0QxYLITnW1lLokSx/dTianWPFEhMC9BgijempgNXHNfcVirg1lPSyg
z7KqoKUN0oHqWLr2U1A+7kqrl6O2nx3CKs1bj1hToT1+p4kcMoHXA7kA+VBLUpEs
VwIDAQAB
-----END PUBLIC KEY-----
```

## Event payload 

All event notification payloads have the same high-level structure.

Top-level properties are common to all events. The `data` property is an object that can contain various properties.
The exact properties that the `data` object contains depends on the event type and schema version of the event.

Common Properties
data
Event type and schema version-specific details.

subscription_id
ID of the webhook subscription that triggered the event notification.

event_type
Event type (what event happened in our system).

schema_version
Schema version (the notification structure used to model the event).

sent_at
When the event notification was sent from our system.

Basic event payload
```json
{
  "data": {},
  "subscription_id": "01234567-89ab-cdef-0123-456789abcdef",
  "event_type": "event#type",
  "schema_version": "2.0.0",
  "sent_at": "2026-01-01T12:34:56Z"
}
```