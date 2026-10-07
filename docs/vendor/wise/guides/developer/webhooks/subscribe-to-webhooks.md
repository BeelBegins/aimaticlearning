# Subscribe to webhooks

Wise offers many event types and each event type triggers specific notifications. You must subscribe to each event for which you want to receive notifications.

You can subscribe to webhooks in the following ways:

- On the Wise [Developer Hub](https://wise.com/developer-hub).
- Programmatically via API.


## Requirements

Whether you subscribe via Developer Hub or via API, you must provide the following information:

- A name for the subscription.
- The event type to subscribe to (when subscribing via API, this value goes into the `trigger_on` field).
- Your webhook URL that will receive the event notification (IP addresses not allowed).
- The schema version for the event type. We always recommend using the latest supported schema version for the event type.
  - `4.0.0` and later provides consistent millisecond-precision timestamps, which helps with correct [event ordering](/guides/developer/webhooks/event-ordering).


If subscribing via API, you must also have:

- Your client key from Developer Hub.
- Your client credentials access token.


## Subscribe via Developer Hub

With Wise [Developer Hub](https://wise.com/developer-hub), you can view the details of active subscriptions, create and delete webhook subscriptions, and see the event history.

Webhooks in the Developer Hub are application-level only and require access  permissions. Speak with your implementation team if you don’t yet have access.

### View active subscriptions

Go to the **Webhooks > Subscriptions** section in Developer Hub.

The page displays a list of all subscriptions for the currently selected application with the following information:

| Column  | Description |
|  --- | --- |
| **Name** | The human-readable name you gave the subscription. |
| **Listening for** | The event type and schema version.

Ex: `transfers#state-change · 4.0.0` |
| **URL** | The callback URL where events are delivered. |


Click any row to go to that subscription's detail page.

Developer hub webhook subscriptions page
### Create a subscription

On the Webhook Subscriptions page, click the **Create Subscription** button.

The Create Subscription form appears and includes four **required** sections:

- Subscription name
- Notification URL
- Listen for
- Schema version


Developer hub create subscription form page
| Section | Description |
|  --- | --- |
| **Subscription name** | This is your label to identify this subscription. The name pre-fills with a default value based on how many subscriptions already exist (for example, `Subscription 3`). 

Change this value to anything you prefer, just make sure it is unique. |
| **Notification URL** | This is the HTTPS endpoint that will receive webhook payloads. The URL is validated in real time. 

The URL must meet **all** of the following requirements:- Must start with `https://` (related error: `The URL must be valid and start with 'https://'`)
- Must not include an explicit port number (related error: `The URL must not include a port number`)
- Must not include query parameters (related error: `The URL must not include any query parameters`)
- Must not include user credentials (related error: `The URL must not include user credentials`) 

Example of a valid URL: `https://my-webhook-domain.com/callback`

 |
| **Listen for** | This is a grouped, collapsible list of available event types.

At this time, you can select *exactly one event type per subscription*. |
| **Schema version** | This section appears after you select an event type. A dropdown lists all available schema versions for the selected event type, most recent first. |


When you have completed the form, click the **Create Subscription** button.

Creating a subscription automatically sends a test event to your callback URL so you can verify your endpoint is reachable.

### View subscription detail

Click any row in the subscriptions table to open the detail page for that subscription.

The detail page shows:

| Field | Description |
|  --- | --- |
| **Listening for** | The event type and schema version. |
| **Subscription ID** | The unique identifier for this subscription (useful for API calls). |
| **URL** | The callback URL. |
| **Created at** | The date the subscription was created. |
| **Recent events table** | The delivery history scoped to this subscription. See the [Event Delivery Details](/guides/developer/webhooks/view-retry-events#event-delivery-details) for how to use it. |


Developer hub subscription details page
### Delete a subscription

On the subscription's detail page, click the **Delete subscription** button. A confirmation modal appears with the message:

`Any events in flight at the time of deletion are still delivered but no webhook will be sent for them as the subscription no longer exists.`

## Subscribe via API

To subscribe to a webhook event via API, send a [create application webhook subscription request](/api-reference/webhook/webhookapplicationsubscriptioncreate).

Each request creates a subscription for a specific event. You must create a subscription for every event for which you want to receive notifications.

### Request body

All of the following fields are required in the request body:

| Field  | Type | Description |
|  --- | --- | --- |
| `name` | string | Your custom name for the subscription. Names should be unique and descriptive. |
| `trigger_on` | string | The event type value of the webhook you are subscribing to. See the [list of available webhook events](/api-reference/webhook-event) along with their details and example payloads.

Examples: `transfers#state-change`, `transfers#refund`, `balances#update`, `profiles#state-change` |
| `delivery` | object | Contains the schema `version` and your callback `url` where notification payloads are sent. |
| `delivery.version` | string | The schema version of the event. We recommend always using the latest version. |
| `delivery.url` | string | The URL where your server will be listening for events. |


### Example request and response

The following examples show a request and response for a subscription to the transfer state change event (`transfers#state-change`).

Request
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

Response
```json 200 application/json
{
  "id": "72195556-e5cb-495e-a010-b37a4f2a3043",
  "name": "Webhook Subscription #1",
  "trigger_on": "transfers#state-change",
  "delivery": {
    "version": "4.0.0",
    "url": "https://your.webhook.url/12345"
  },
  "scope": {
    "domain": "application",
    "id": "<your client key>"
  },
  "created_by": {
    "type": "application",
    "id": "<your client ID>"
  },
  "created_at": "2019-10-10T13:55:57Z"
}
```

```json 429 application/json
{}
```

Creating a subscription automatically sends a test event to your callback URL so you can verify your endpoint is reachable.

### Profile-level webhooks

Profile-level webhooks send notifications when events occur for resources created under a specific Wise profile. *In most cases, Wise partners should subscribe at the application level rather than profile level.*

If you wish to subscribe to a webhook at the profile level, use the [create profile webhook subscription endpoint](/api-reference/webhook/webhookprofilesubscriptioncreate).

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/profiles/{profileId}/subscriptions' \
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

Instead of the `CLIENT_CREDENTIALS_TOKEN` use a `USER_TOKEN` for authorization. Instead of the `clientKey` in the endpoint path, use the `profileId`.

The request body and response are the same as application-level webhook subscriptions.

Only certain event types support profile-level subscriptions. Check the [webhook event list](/api-reference/webhook-event) to see if your desired event is supported at the profile level.