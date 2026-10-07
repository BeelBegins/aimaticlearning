# Webhooks and notifications

Listen for events to trigger actions in your workflow.

Webhooks are user-defined callbacks triggered by certain events in Wise's system.

Use webhook notifications to keep your application informed about Wise events and use the details in a webhook payload to trigger specific actions and workflows.

Common webhook events include (but are not limited to):

| Event  | Description |
|  --- | --- |
| [Transfer state changes](/api-reference/webhook-event/eventtransfersstatechange) | Notifies you when a transfer changes from one state to another. See the [Tracking transfers guide](/guides/product/send-money/tracking/transfer-statuses) to learn about each possible state of a transfer. |
| [Transfer payout failures](/api-reference/webhook-event/eventtransferspayoutfailure) | Notifies you when a [transfer payout fails](/guides/product/send-money/tracking/payout-failures) and includes a reason code and description. |
| [Profile state changes](/api-reference/webhook-event/eventprofilesstatechange) | Notifies you when a profile changes from one state to another. |
| [Verification state changes](/api-reference/webhook-event/eventprofilesverificationstatechange) | Notifies you when the verification of a profile changes from one state to another. |
| [Balance updates](/api-reference/webhook-event/eventbalancesupdate) | Notifies you every time a multi-currency account is credited or debited. |
| [Card status changes](/api-reference/webhook-event/eventcardscardstatuschange) | Notifies you when a [card status changes](/guides/product/issue-cards/card-transaction), including the initial card status. |
| [Card order status changes](/api-reference/webhook-event/eventcardscardorderstatuschange) | Notifies you every time a card order status updates. |
| [SWIFT message receipt](/api-reference/webhook-event/eventswiftmessagereceived) | Notifies you when a SWIFT message is received and processed by Wise on your behalf. |
| [Bulk settlement payment receipt](/api-reference/webhook-event/eventbulksettlementpaymentreceived) | Notifies you when a bulk settlement fund is received. |


## Webhook subscriptions

The Wise API supports two subscription types:

- **Application-level webhooks**: Sends notifications for events related to resources created by your application.
- **Profile-level webhooks**: Sends notifications when events occur for resources created under a specific Wise profile.


In most cases, you should subscribe to the **application-level** webhook.

You can subscribe to specific webhook events either programmatically or via [Developer Hub](https://wise.com/developer-hub). Review the [Subscribe to webhooks guide](/guides/developer/webhooks/subscribe-to-webhooks) for details about both options.

## Webhook delivery

All webhook callbacks use HTTP `POST` requests. When a business event occurs and a webhook is created, Wise sends an HTTP `POST` request.

The webhook is considered successfully processed only when we receive a `200` response.

### Retry policy

In the event that an HTTP request fails, we retry according to the following policy:

#### Exponential backoff

By default, we retry HTTP failure responses using an exponential backoff algorithm.

We start with an initial delay of 1 minute, with a growth factor of two and  a maximum delay of 24 hours. This results in the following retry sequence:

- First retry with a 1-min delay.
- Second retry with a 2-min delay.
- Third retry with a 4-min delay.
- ...
- After the eleventh retry, there are 14 more retries once a day.


#### Retry-after headers

Wise respects [retry-after](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After) headers.

We can handle both `http-date` and `delay-seconds` responses.

For example:

- If you return `Retry-After: Wed, 22 Oct 2025 07:28:00 GMT` we  wait until that time to retry, or retry immediately if the date is in the past.
- If you return `Retry-After: 180` we wait 180 seconds until we retry.


#### Non-recoverable client errors

The following HTTP statuses almost always fail on retry. We will attempt to deliver them up to three times only.

| Status code | Name |
|  --- | --- |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 409 | Conflict |
| 410 | Gone |
| 417 | Expectation Failed |
| 422 | Unprocessable Content |


While Wise has a robust retry mechanism, webhook delivery is done on a **best-effort** guarantee. Please contact us if you believe you missed any webhook events.

## Webhook URLs

Before proceeding, make sure the endpoint where you intend to receive webhooks satisfies the following requirements:

- Has a valid domain name (IPs are disallowed).
- Listens to HTTPS requests on port 443.
- Has a valid HTTPS certificate signed by a trusted Certificate Authority (CA). Self-signed or expired certificates are not accepted.
- Does not include any query arguments in the URL.
- Responds directly with a 2xx status code. Redirects are not supported. Any 3xx status code (301, 302, 307, etc) is recognized as a delivery error and the redirect will not be followed.


### Examples

- Valid URL: `https://webhooks.example.com/balance-change`
- Invalid URL: `http://webhooks.example.com:8080/hook.php?type=balance`


You can have multiple subscriptions per event type, but be mindful that you will receive duplicate callbacks, one for each subscription.

### IP allowlisting (optional)

If your webhook endpoint sits behind a firewall, WAF, or API gateway that blocks unknown source IPs, you must allowlist Wise’s webhook sender IPs. If you don’t, Wise can still generate events, but your network can drop the webhook requests before they reach your application.

- **Prefer CIDR ranges in production**:
To maximise availability (including scaling and disaster recovery), allowlist the full CIDR ranges where possible. Individual IPs can change and have a lower reliability SLO.
- **Don’t use IP allowlisting as your only security control**:
IP allowlisting is a network control. You should still use HTTPS and implement the webhook security controls described in this guide (for example, mTLS and/or [payload verification](/guides/developer/webhooks/event-handling) where applicable).


#### Production

Allowlist both CIDR blocks to support regional failover:

- `45.129.54.0/24` (Frankfurt, eu-central-1)
- `45.129.55.0/24` (Paris, eu-west-3)


If you can’t allowlist a `/24`, allowlist these individual IPs instead:

- `45.129.54.176/32`
- `45.129.54.183/32`
- `45.129.54.106/32`
- `45.129.55.0/32`
- `45.129.55.1/32`
- `45.129.55.2/32`


In both cases, you'll also need to add these individual IPs:

- `18.184.162.75/32`
- `18.184.251.153/32`
- `52.58.50.91/32`


#### Sandbox

Allowlist these IPs for webhook delivery in Sandbox:

- `3.67.109.66/32`
- `3.78.113.13/32`
- `18.199.110.249/32`
- `45.129.55.64/32`
- `45.129.55.65/32`
- `45.129.55.66/32`