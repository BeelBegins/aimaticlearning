# Embed on web

Use this guide after your backend has created an Embedded Flow URL with the create recipient embedded link request endpoint.

On web, load the returned `url` in an iframe. You can either let the iframe render with a fixed size, or listen for optional messages from the flow to update the frame and react to completion or errors.

## Add the iframe

Iframe
```html
<iframe
  id="wise-embedded-flow"
  title="Wise Platform Embedded Flow"
  src="<EMBEDDED_FLOW_URL>"
  sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
  allow="camera; microphone;"
  style="width: 100%; min-height: 600px; border: 0;"
></iframe>
```

The iframe should allow scripts, same-origin access, popups, and forms. Some flows may also need camera or microphone permissions for verification steps.

## Optional flow messages

Embedded Flows can post messages to the parent window. Listen for these messages if you want to resize the iframe, show loading states, or move the user to the next step when the flow finishes.

| Message | When it is sent | Typical use |
|  --- | --- | --- |
| `ready` | The flow is ready to be shown. | Hide a loading state or make the iframe visible. |
| `resize` | The flow content height changes. | Update the iframe height. |
| `done` | The user completes the flow. | Close the iframe or continue your product flow. |
| `error` | The flow cannot continue, or the user cancels. | Show a fallback state, ask the user to try again, or return them to the previous step. |


Listen for messages
```js
const iframe = document.querySelector('#wise-embedded-flow');

window.addEventListener('message', (event) => {
  if (event.source !== iframe.contentWindow) return;

  const message = event.data;

  if (message.type === 'ready') {
    iframe.style.visibility = 'visible';
  }

  if (message.type === 'resize') {
    iframe.style.height = `${message.height}px`;
  }

  if (message.type === 'done') {
    // Continue your product flow.
  }

  if (message.type === 'error') {
    if (message.code === 'cancelled') {
      // The user closed or cancelled the flow.
      return;
    }

    // Show a fallback state.
  }
});
```

## Redirect instead of embedding

If you do not want to embed the flow, redirect the user to the returned `url`. When the flow finishes, Wise returns the user to the redirect URL you provided when creating the embedded link request.

Wise appends a `status` query parameter when returning the user to your redirect URL:

| Status | Meaning |
|  --- | --- |
| `success` | The user completed the flow. |
| `cancelled` | The user closed or cancelled the flow. |
| `error` | The flow could not continue. |