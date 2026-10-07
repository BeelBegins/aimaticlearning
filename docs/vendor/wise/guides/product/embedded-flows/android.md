# Embed on Android

Use this guide after your backend has created an Embedded Flow URL with the create recipient embedded link request endpoint.

On Android, load the returned `url` in a `WebView`. If you want to react to flow events in native code, inject a small bridge that forwards window messages from the flow to your app.

## Load the flow

WebView setup
```kotlin
val webView: WebView = findViewById(R.id.wiseEmbeddedFlow)

webView.settings.javaScriptEnabled = true
webView.settings.domStorageEnabled = true
webView.loadUrl("<EMBEDDED_FLOW_URL>")
```

Some flows may need camera or microphone permissions for verification steps. Make sure your app handles Android runtime permissions when using flows that need device capabilities.

## Optional flow messages

Embedded Flows can emit `ready`, `resize`, `done`, and `error` messages. In a native WebView, forward those messages to Kotlin with a JavaScript interface. If the user cancels the flow, Wise emits an `error` message with `code` set to `cancelled`.

Bridge flow messages
```kotlin
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONObject

class FlowBridge {
  @JavascriptInterface
  fun postMessage(payload: String) {
    val event = JSONObject(payload)

    when (event.optString("type")) {
      "ready" -> {
        // Hide loading UI.
      }
      "resize" -> {
        // Read event.optInt("height") if you need to resize the WebView.
      }
      "done" -> {
        // Continue your app flow.
      }
      "error" -> {
        if (event.optString("code") == "cancelled") {
          // The user closed or cancelled the flow.
          return
        }

        // Show a fallback state.
      }
    }
  }
}

val webView: WebView = findViewById(R.id.wiseEmbeddedFlow)

webView.settings.javaScriptEnabled = true
webView.settings.domStorageEnabled = true
webView.addJavascriptInterface(FlowBridge(), "WiseFlow")

webView.webViewClient = object : WebViewClient() {
  override fun onPageFinished(view: WebView, url: String) {
    view.evaluateJavascript(
      """
      window.addEventListener('message', function(event) {
        window.WiseFlow.postMessage(JSON.stringify(event.data));
      });
      """.trimIndent(),
      null
    )
  }
}

webView.loadUrl("<EMBEDDED_FLOW_URL>")
```

## Redirect instead of embedding

If a WebView is not the right fit for your app, open the returned `url` with the browser component you normally use for external flows. When the flow finishes, Wise returns the user to the redirect URL you provided when creating the embedded link request.

Wise appends `status=success`, `status=cancelled`, or `status=error` when returning the user to your redirect URL.