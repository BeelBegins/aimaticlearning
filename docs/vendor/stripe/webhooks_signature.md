# Manage webhook endpoints

Handle delivery failures, signature errors, and event-generation failures for your webhook endpoints.

Diagnose and resolve issues with your webhook endpoints. If you haven’t set up an endpoint yet, start with [Set up events](https://docs.stripe.com/events/set-up-events.md).

## Find the right section

Use the table below to jump to the guidance you need.

| Situation | Where to go |
| --- | --- |
| Your endpoint was unavailable and missed events | [Process undelivered events](https://docs.stripe.com/events/manage-webhook-endpoints.md#process-undelivered-events) |
| You’re seeing `Webhook signature verification failed` errors | [Resolve signature verification errors](https://docs.stripe.com/events/manage-webhook-endpoints.md#signature-errors) |
| Events are failing to deliver or returning error status codes | [Debug webhook deliveries](https://docs.stripe.com/events/manage-webhook-endpoints.md#debugging) |
| Stripe failed to generate an event and you need to recover | [Handle event-generation failures](https://docs.stripe.com/events/manage-webhook-endpoints.md#event-generation-failures) |
| You want to route events to typed handler functions without writing manual parsing code | [Use event notification handlers](https://docs.stripe.com/events/manage-webhook-endpoints.md#event-notification-handlers) |
| You’re building a webhook to respond to payment events | [Set up events](https://docs.stripe.com/events/set-up-events.md) |
| You want to follow security and operational best practices | [Best practices](https://docs.stripe.com/events/manage-webhook-endpoints.md#best-practices) |

## Process undelivered events 

If your webhook endpoint was temporarily unavailable, Stripe [automatically retries](https://docs.stripe.com/events/how-events-work.md#automatic-retries) undelivered events for up to three days. To speed up recovery, manually process the backlog.

### List webhook events 

Call the [List Events](https://docs.stripe.com/api/events/list.md) API with the following parameters:

- `ending_before`: An event ID that was successfully delivered immediately before the outage. This anchors the list to the window of events you missed.
- `types`: The event types your endpoint listens for.
- `delivery_success`: Set to `false` to return only events that failed delivery to at least one of your endpoints.

Stripe only returns events created in the last 30 days.

```curl
curl -G https://api.stripe.com/v1/events \
  -u "<<YOUR_SECRET_KEY>>:" \
  -d ending_before=evt_001 \
  -d "types[]=payment_intent.succeeded" \
  -d "types[]=payment_intent.payment_failed" \
  -d delivery_success=false
```

By default, the response returns up to 10 events. To retrieve all events, use [auto-pagination](https://docs.stripe.com/api/pagination/auto.md).

#### Ruby

```ruby

# Don't put any keys in code. See https://docs.stripe.com/keys-best-practices.
# Find your keys at https://dashboard.stripe.com/apikeys.
client = Stripe::StripeClient.new('<<YOUR_SECRET_KEY>>')
events = client.v1.events.list({
  ending_before: 'evt_001',
  types: ['payment_intent.succeeded', 'payment_intent.payment_failed'],
  delivery_success: false,
})

events.auto_paging_each do |event|
  # This function is defined in the next section
  process_event(event)
end
```

Using `ending_before` with auto-pagination returns events in chronological order, so you process them in the order they were created.

### Process the events 

Guard against processing the same event twice. Your manual recovery script might run more than once, and Stripe’s automatic retries might deliver some events while your script is running.

#### Ruby

```ruby
def process_event(event)
  if is_processing_or_processed(event)
    puts "skipping event #{event.id}"
  else
    puts "processing event #{event.id}"
    mark_as_processing(event)

    # Process the event
    # ...

    mark_as_processed(event)
  end
end
```

Implement the following functions against your own data store:

- `is_processing_or_processed`: Returns true if the event is already being handled or has been handled.
- `mark_as_processing`: Marks the event as in-progress before you begin.
- `mark_as_processed`: Marks the event as complete after you finish.

### Respond to automatic retries 

Stripe still considers manually processed events as undelivered and continues its automatic retry schedule. When your endpoint receives an event you’ve already processed, skip it and return a `200` response to stop further retries.

#### Ruby

```ruby
require 'json'
require 'stripe'

client = Stripe::StripeClient.new(ENV.fetch('STRIPE_API_KEY'))

# Using Sinatra
post '/webhook' do
  payload = request.body.read
  event = nil

  begin
    event = Stripe::Event.construct_from(
      JSON.parse(payload, symbolize_names: true)
    )
  rescue JSON::ParserError => e
    status 400
    return
  end

  if is_processing_or_processed(event)
    puts "skipping event #{event.id}"
  else
    puts "processing event #{event.id}"
    mark_as_processing(event)

    # Process the event
    # ...

    mark_as_processed(event)
  end

  status 200
end
```

## Resolve signature verification errors 

When processing webhook events, verify that each request came from Stripe using the `Stripe-Signature` header. Call `constructEvent()` (for snapshot events) or `parseEventNotification()` (for thin events) with three parameters:

- `requestBody`: The raw request body string Stripe sent.
- `signature`: The `Stripe-Signature` header value.
- `endpointSecret`: The secret associated with your endpoint.

#### Ruby

```ruby
Stripe::Webhook.construct_event(request_body, signature, endpoint_secret)
```

If you see this error, at least one of the three parameters you passed is incorrect:

```
Webhook signature verification failed. Err: No signatures found matching the expected signature for payload.
```

### Check the endpoint secret 

The most common cause is using the wrong endpoint secret. The secret for a CLI-forwarded endpoint is different from the secret for a Dashboard-managed endpoint—don’t mix them up.

- **Dashboard endpoint**: Open the endpoint in [Workbench](https://dashboard.stripe.com/test/webhooks) and click **Reveal secret**.
- **CLI**: The secret is printed in the terminal when you run `stripe listen`.

Both secrets start with `whsec_`. Print the `endpointSecret` value your code uses and confirm it matches what you find above.

### Check the request body 

The request body must be the exact UTF-8 string Stripe sent, without any modifications. When printed, it looks similar to this:

```
{
  "id": "evt_xxx",
  "object": "event",
  "data": {
      ...
  }
}
```

Some frameworks parse or mutate the request body before your code sees it—by reordering keys, stripping whitespace, converting to JSON, or changing encoding—which causes signature verification to fail.

| Framework | Retrieval method |
| --- | --- |
| stripe-node library with Express | Follow the [Set up events](https://docs.stripe.com/events/set-up-events.md) guide. |
| stripe-node library with Body Parser | Try solutions in this [GitHub issue](https://github.com/stripe/stripe-node/issues/341). |
| stripe-node library with Next.js [App Router](https://nextjs.org/docs/app/building-your-application/routing/route-handlers) | See this [working example](https://github.com/stripe/stripe-node/blob/master/examples/webhook-signing/nextjs/app/api/webhooks/route.ts). |
| stripe-node library with Next.js [Pages Router](https://nextjs.org/docs/pages/building-your-application/routing/api-routes) | Disable `bodyParser` and use `buffer(request)`, as in [this example](https://github.com/stripe/stripe-node/blob/master/examples/webhook-signing/nextjs/pages/api/webhooks.ts). |

If you use stripe-node with Express, make sure `app.use(express.json())` appears *after* your webhook route. Express applies middleware in order; if `express.json()` runs first, it parses the body before signature verification.

```javascript
// Webhook route must come before the JSON middleware
app.post('/webhook', ...);

// JSON middleware for other routes
app.use(express.json());

app.post('/another-route', ...);
```

#### AWS API Gateway with Lambda

To retrieve the raw request body, configure a **Body Mapping Template** of content type `application/json` in the API Gateway:

```
{
  "method": "$context.httpMethod",
  "body": $input.json('$'),
  "rawBody": "$util.escapeJavaScript($input.body).replaceAll("\\'", "'")",
  "headers": {
    #foreach($param in $input.params().header.keySet())
    "$param": "$util.escapeJavaScript($input.params().header.get($param))"
    #if($foreach.hasNext),#end
    #end
  }
}
```

In your Lambda function, access the raw body from `event.rawBody` and the headers from `event.headers`.

### Check the signature header 

Print the `signature` parameter and confirm it matches this format:

```
t=xxx,v1=yyy,v0=zzz
```

If not, check how your code extracts the `Stripe-Signature` header value.

> For complete signature verification instructions, see [Check webhook signatures](https://docs.stripe.com/events/set-up-events.md#signature-checking). In addition to signature verification, configure your server to only accept webhook requests from Stripe’s [IP addresses](https://docs.stripe.com/ips.md).

## Debug webhook deliveries 

Multiple types of issues can prevent successful event delivery to your webhook endpoint. This section helps you identify and fix them.

### View event deliveries 

To view event deliveries, open [Workbench](https://docs.stripe.com/workbench.md), select the webhook endpoint under **Webhooks**, then select the **Event deliveries** tab. The **Event deliveries** tab provides a list of events and whether they’re `Delivered`, `Pending`, or `Failed`. Click an event to view metadata, including the HTTP status code of the delivery attempt and the time of pending future deliveries.

You can also use the [Stripe CLI](https://docs.stripe.com/cli.md) to [listen for events](https://docs.stripe.com/webhooks.md#test-webhook) directly in your terminal.

### Fix HTTP status codes

When an event displays a status code of `200`, it indicates successful delivery to the webhook endpoint. You might also receive a status code other than `200`. View the table below for a list of common HTTP status codes and recommended solutions.

| Pending webhook status | Description | Fix |
| --- | --- | --- |
| (Unable to connect) ERR | We’re unable to establish a connection to the destination server. | Make sure that your host domain is publicly accessible to the internet. |
| (`302`) ERR (or other `3xx` status) | The destination server attempted to redirect the request to another location. We consider redirect responses to webhook requests as failures. | Set the webhook endpoint destination to the URL resolved by the redirect. |
| (`400`) ERR (or other `4xx` status) | The destination server can’t or won’t process the request. This might occur when the server detects an error (`400`), when the destination URL has access restrictions, (`401`, `403`, `405`), or when the destination URL doesn’t exist (`404`). | Make sure that your endpoint is publicly accessible to the internet and accepts a POST HTTP method. |
| (`500`) ERR (or other `5xx` status) | The destination server encountered an error while processing the request. | Review your application’s logs to understand why it’s returning a `500` error. |
| (TLS error) ERR | We couldn’t establish a secure connection to the destination server. Issues with the SSL/TLS certificate or an intermediate certificate in the destination server’s certificate chain usually cause these errors. Stripe requires *TLS* (TLS refers to the process of securely transmitting data between the client—the app or browser that your customer is using—and your server. This was originally performed using the SSL (Secure Sockets Layer) protocol) version `v1.2` or higher. | Perform an [SSL server test](https://www.ssllabs.com/ssltest/) to find issues that might cause this error. |
| (Timed out) ERR | The destination server took too long to respond to the webhook request. | Make sure you defer complex logic and return a successful response immediately in your webhook handling code. |

## Handle event-generation failures  (Public preview)

In rare cases, Stripe can fail to generate an `Event` object. When this happens, the event is irrecoverable—Stripe can’t deliver it to your destinations or surface it in the Dashboard or the [List Events API](https://docs.stripe.com/api/v2/core/events/list.md). Instead, Stripe creates a [`v2.core.health.event_generation_failure.resolved`](https://docs.stripe.com/api/v2/core/events/event-types.md#v2_event_types-v2.core.health.event_generation_failure.resolved) event to notify you of the failure.

### Where these events appear

Stripe delivers `v2.core.health.event_generation_failure.resolved` events to:

- The [Events](https://docs.stripe.com/workbench/overview.md#events) tab in Workbench
- The [Health](https://docs.stripe.com/workbench/health.md) tab in Workbench
- Any webhook endpoint you configure to listen for this event type

To receive these alerts using a webhook, [register a webhook endpoint](https://docs.stripe.com/events/set-up-events.md) that listens for `v2.core.health.event_generation_failure.resolved` events.

### How to use the health event

Process the event notification to retrieve the `v2.core.health.event_generation_failure.resolved` object:

```json
{
  "alert_id": "halert_61RFBMa6o6H87usts16RFBM10hSQlYfddqcFoEMR6CPY",
  "grouping_key": "_grouping_s8PgTvizbkORV9z5PhaJSvc4dUcAMmfRpEHKm4EeJ1glsQ5XMf",
  "impact": {
    "event_type": "payment_intent.requires_action",
    "related_object_id": "pi_1QA8PKDTvO5jCVb3TVDZP75a",
    "related_object": {
      "id": "pi_1QA8PKDTvO5jCVb3TVDZP75a",
      "type": "payment_intent",
      "url": "https://dashboard.stripe.com/payment_intents/pi_1QA8PKDTvO5jCVb3TVDZP75a"
    }
  },
  "resolved_at": "2025-10-30T16:05:44.000Z",
  "summary": "We have failed to create a notification for your Stripe account."
}
```

The payload tells you:

- **Failed event type**: `payment_intent.requires_action`
- **Affected resource**: PaymentIntent `pi_1QA8PKDTvO5jCVb3TVDZP75a`
- **Timestamp**: `2025-10-30T16:05:44.000Z`
- **Account scope**: The `impact` object doesn’t include a `context` property, so the failure occurred on your platform account, not a connected account.

### Recover after a failure

If your integration relies on receiving the failed event type, poll the relevant API to get the current state of the affected resource. For the example above, retrieve the PaymentIntent directly:

```curl
curl https://api.stripe.com/v1/payment_intents/pi_1QA8PKDTvO5jCVb3TVDZP75a \
  -u "<<YOUR_SECRET_KEY>>:"
```

## Use event notification handlers 

> Event notification handlers are available in [public preview](https://docs.stripe.com/sdks/versioning.md#public-preview-release-channel). This feature doesn’t support event destinations that use [EventBridge](https://docs.stripe.com/event-destinations/eventbridge.md) in public preview.

Event notification handlers are the preferred approach to process thin events in production. They replace manual `switch` statements with typed callback functions and handle signature verification automatically.

Each Stripe SDK provides an `EventNotificationHandler` class that handles parsing, validating, and routing incoming webhook events to typed callback functions. You write one function per event type instead of a large `switch` statement, and the handler takes care of signature verification.

## Before you begin

You must use one of the following SDK versions or higher.

| Language | GA | Public preview | Private preview |
| --- | --- | --- | --- |
| Python | `v15.6.0` | `v14.2.0b1` | `v15.2.0a3` |
| Ruby | `v19.6.0` | `v18.2.0-beta.1` | `v19.2.0-alpha.3` |
| PHP | `v21.3.0` | `v19.2.0-beta.1` | `v20.2.0-alpha.4` |
| Go | `v86.4.0` | `v84.2.0-beta.1` | `v85.2.0-alpha.3` |
| Node | `v22.6.0` | `v20.2.0-beta.1` | `v22.2.0-alpha.4` |
| .NET | `v52.4.0` | `v50.2.0-beta.1` | `v51.2.0-alpha.3` |
| Java | `v33.4.0` | `v31.2.0-beta.1` | `v32.2.0-alpha.3` |

### Write a fallback callback 

Write a function that runs when no dedicated callback is registered for an incoming event type. This function receives the `EventNotification` object, the `StripeClient`, and details about why no handler was matched.

As a migration strategy, consider moving your existing webhook endpoint code into this function first, then migrating individual event types to their own callbacks over time.

#### Python

```python
def fallback_callback(notif: EventNotification, client: StripeClient, details: UnhandledNotificationDetails):
    print(f'Got an unhandled event of type {notif.type}!')
```

### Initialize the handler 

In your webhook endpoint, initialize an `EventNotificationHandler` by calling the convenience method on `StripeClient`. Pass it your fallback callback.

#### Webhook endpoint

If you’re writing a traditional webhook endpoint, pass your webhook secret to the handler constructor so the SDK can verify the request.

#### Python

```python
client = StripeClient(api_key)
handler = client.notification_handler(webhook_secret, fallback_callback)
```

#### Cloud provider

If you use a cloud provider such as [Azure Event Grid](https://docs.stripe.com/event-destinations/eventgrid.md), verification isn’t needed. Use the `*WithoutVerification` handler constructor to get the correct method signatures.

#### Python

```python
client = StripeClient(api_key)
handler = client.notification_handler_without_verification(fallback_callback)
```

### Register a callback for an event type 

Write a typed function for each event type you want to handle. Your callback receives the event notification cast to the correct SDK class, plus a `StripeClient` bound to the context of the notification. You can register zero or more callbacks—any event type without a registered callback routes to the fallback.

#### Python

```python
@handler.on_v1_billing_meter_error_report_triggered
def handle_meter_error(
    notif: V1BillingMeterErrorReportTriggeredEventNotification,
    client: StripeClient,
):
    event = notif.fetch_event()
    print(f"Err! No meter found: {event.data.developer_message_summary}")
```

### Process incoming events 

Pass incoming `POST` bodies to the handler. The handler parses the payload and routes to the matching callback.

#### Webhook endpoint

Pass the `Stripe-Signature` header to `.handle()` so the SDK can verify the request.

#### Python

```python
@app.route("/webhook", methods=["POST"])
def webhook():
    webhook_body = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        handler.handle(webhook_body, sig_header)
        return jsonify(success=True), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
```

#### Cloud provider

If you’re using a cloud provider such as [Amazon EventBridge](https://docs.stripe.com/event-destinations/eventbridge.md) or [Azure Event Grid](https://docs.stripe.com/event-destinations/eventgrid.md), verification isn’t needed. The handler’s `.handle()` method accepts only the payload and unwraps the inner `Event` from the cloud provider’s envelope.

Event notification handlers don’t support EventBridge destinations on the [public preview release channel](https://docs.stripe.com/sdks/versioning.md#public-preview-release-channel).

#### Python

```python
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        handler.handle(request.data)
        return jsonify(success=True), 200
    except Exception as e:
        return jsonify(error=str(e)), 400
```

### How it works 

A diagram explaining the flow of events through an event notification handler (See full diagram at https://docs.stripe.com/events/manage-webhook-endpoints)

```text
[.handle(event, …)] --> [preHandle registered?]
[preHandle registered?] -- yes --> [run preHandle]
[run preHandle] -- return false --> [Stop (without error)]
[run preHandle] -- return true --> [Known SDK event?]
[preHandle registered?] -- no --> [Known SDK event?]
[Known SDK event?] -- yes --> [Callback Registered?]
[Known SDK event?] -- no --> [Run fallbackCallback]
[Callback Registered?] -- yes --> [Run registered callback]
[Callback Registered?] -- no --> [Run fallbackCallback]
```

Internally, handling an event follows these steps:

1. Parse and validate the incoming event.
2. Determine which callback to invoke.
3. Run that callback with the correctly typed `EventNotification` class.

### The preHandle method 

Event notification handlers have a `preHandle` method designed around two main use cases:

1. Calling a function before invoking any callbacks (such as a logger).
2. Halting the processing of an event based on the content of that event. Use this for [deduplicating events](https://docs.stripe.com/events/manage-webhook-endpoints.md#handle-duplicate-events).

You register the pre-handle callback in the same way as event-specific callbacks. The handler invokes it with the parsed `EventNotification` class and a `StripeClient` instance bound to the event’s context.

#### Python

```python
# example for testing; use something more durable for production
processed_event_ids = set()

@handler.pre_handle
def log_and_dedup(notif: EventNotification, client: StripeClient) -> bool:
    # log every incoming event
    print(f'Starting {notif.id}')

    # ignore duplicates...
    if notif.id in processed_event_ids:
        print(f"Already processed {notif.id}, skipping.")
        return False
    processed_event_ids.add(notif.id)

    # ... or event types you don't care about
    if notif.type == 'some.ignored.event':
        return False

    return True
```

The .NET SDK uses the `.Cancel` property of its native `event` object to control whether to continue event handling. It defaults to false, which invokes an event-specific callback (or your fallback) as normal. If you set `e.Cancel = true;` it stops execution without returning an error.

### Error handling 

The event notification handler does no additional error handling or suppressing. Any SDK error (such as each language’s `SignatureVerificationError`) or error from your callbacks comes from the `.handle(...)` function.

## Best practices 

Review these best practices to make sure your webhook endpoints remain secure and function well with your integration.

### Handle duplicate events 

Webhook endpoints might occasionally receive the same event more than once. Guard against duplicated event receipts by logging the [event IDs](https://docs.stripe.com/api/events/object.md#event_object-id) you’ve processed, and then not processing already-logged events.

In some cases, two separate Event objects are generated and sent. To identify these duplicates, use the ID of the object in `data.object` along with the `event.type`.

### Only listen to event types your integration requires

Configure your webhook endpoints to receive only the types of events required by your integration. Listening for extra events (or all events) puts undue strain on your server and we don’t recommend it.

You can [change the events](https://docs.stripe.com/api/webhook_endpoints/update.md#update_webhook_endpoint-enabled_events) that a webhook endpoint receives in the Dashboard or with the API.

### Handle events asynchronously

Configure your handler to process incoming events with an asynchronous queue. You might encounter scalability issues if you choose to process events synchronously. Any large spike in webhook deliveries (for example, during the beginning of the month when all subscriptions renew) might overwhelm your endpoint hosts.

Asynchronous queues allow you to process the concurrent events at a rate your system can support.

### Quickly return a 2xx response 

Your endpoint must quickly return a successful status code (`2xx`) before any complex logic that could cause a timeout. For example, you must return a `200` response before updating a customer’s invoice as paid in your accounting system.

### Exempt webhook route from CSRF protection 

If you’re using Rails, Django, or another web framework, your site might automatically check that every POST request contains a *CSRF token*. This is an important security feature that helps protect you and your users from [cross-site request forgery](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_\(CSRF\)) attempts. However, this security measure might also prevent your site from processing legitimate events. If so, you might need to exempt the webhooks route from CSRF protection.

#### Rails

```ruby
class StripeController < ApplicationController
  # If your controller accepts requests other than Stripe webhooks,
  # you'll probably want to use `protect_from_forgery` to add CSRF
  # protection for your application. But don't forget to exempt
  # your webhook route!
  protect_from_forgery except: :webhook

  def webhook
    # Process webhook data in `params`
  end
end
```

### Receive events with an HTTPS server

If you use an HTTPS URL for your webhook endpoint (required in live mode), Stripe validates that the connection to your server is secure before sending your webhook data. For this to work, your server must be correctly configured to support HTTPS with a valid server certificate. Stripe webhooks support only *TLS* (TLS refers to the process of securely transmitting data between the client—the app or browser that your customer is using—and your server. This was originally performed using the SSL (Secure Sockets Layer) protocol) versions v1.2 and v1.3.

### Roll endpoint signing secrets periodically 

The secret used for verifying that events come from Stripe is modifiable in the [Webhooks](https://dashboard.stripe.com/webhooks) tab in Workbench. To keep them safe, we recommend that you roll (change) secrets periodically, or when you suspect a compromised secret.

To roll a secret:

1. Click each endpoint in the Workbench [Webhooks](https://dashboard.stripe.com/webhooks) tab that you want to roll the secret for.
2. Navigate to the overflow menu (⋯) and click **Roll secret**. You can choose to immediately expire the current secret or delay its expiration for up to 24 hours to allow yourself time to update the verification code on your server. During this time, multiple secrets are active for the endpoint. Stripe generates one signature per secret until expiration.

### Verify events are sent from Stripe 

Without verification, an attacker could send fake webhook events to your endpoint to trigger actions like fulfilling orders, granting account access, or modifying records. Always verify that webhook events originate from Stripe before acting on them.

Use both of these protections:

- **IP allowlisting**: Stripe sends webhook events from a set list of [IP addresses](https://docs.stripe.com/ips.md). Configure your server or firewall to only accept webhook requests from these addresses.
- **Signature verification**: Stripe signs every webhook event by including a signature in the `Stripe-Signature` header. Verify this signature using the [official libraries](https://docs.stripe.com/events/set-up-events.md#signature-checking) to confirm the event wasn’t sent or modified by a third party.

## See also

- [How events work](https://docs.stripe.com/events/how-events-work.md)
- [Set up events](https://docs.stripe.com/events/set-up-events.md)
- [Migrate to thin events](https://docs.stripe.com/webhooks/migrate-snapshot-to-thin-events.md)
