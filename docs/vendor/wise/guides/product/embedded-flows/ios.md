# Embed on iOS

Use this guide after your backend has created an Embedded Flow URL with the create recipient embedded link request endpoint.

On iOS, load the returned `url` in a `WKWebView`. If you want to react to flow events in native code, inject a small bridge that forwards window messages from the flow to your app.

## Load the flow

WKWebView setup
```swift
import WebKit

let webView = WKWebView(frame: .zero)
let flowUrl = URL(string: "<EMBEDDED_FLOW_URL>")!
webView.load(URLRequest(url: flowUrl))
```

Some flows may need camera or microphone permissions for verification steps. Make sure your app includes the required iOS permission descriptions when using flows that need device capabilities.

## Optional flow messages

Embedded Flows can emit `ready`, `resize`, `done`, and `error` messages. In a native WebView, forward those messages to Swift with a `WKScriptMessageHandler`. If the user cancels the flow, Wise emits an `error` message with `code` set to `cancelled`.

Bridge flow messages
```swift
import WebKit

final class FlowMessageHandler: NSObject, WKScriptMessageHandler {
  func userContentController(
    _ userContentController: WKUserContentController,
    didReceive message: WKScriptMessage
  ) {
    guard let event = message.body as? [String: Any],
          let type = event["type"] as? String else {
      return
    }

    switch type {
    case "ready":
      // Hide loading UI.
      break
    case "resize":
      // Read event["height"] if you need to resize the web view.
      break
    case "done":
      // Continue your app flow.
      break
    case "error":
      if event["code"] as? String == "cancelled" {
        // The user closed or cancelled the flow.
        break
      }

      // Show a fallback state.
      break
    default:
      break
    }
  }
}

let contentController = WKUserContentController()
contentController.add(FlowMessageHandler(), name: "wiseFlow")

let bridgeScript = """
window.addEventListener('message', function(event) {
  window.webkit.messageHandlers.wiseFlow.postMessage(event.data);
});
"""

contentController.addUserScript(
  WKUserScript(
    source: bridgeScript,
    injectionTime: .atDocumentStart,
    forMainFrameOnly: false
  )
)

let configuration = WKWebViewConfiguration()
configuration.userContentController = contentController

let webView = WKWebView(frame: .zero, configuration: configuration)
webView.load(URLRequest(url: URL(string: "<EMBEDDED_FLOW_URL>")!))
```

## Redirect instead of embedding

If a WebView is not the right fit for your app, open the returned `url` with the browser component you normally use for external flows. When the flow finishes, Wise returns the user to the redirect URL you provided when creating the embedded link request.

Wise appends `status=success`, `status=cancelled`, or `status=error` when returning the user to your redirect URL.