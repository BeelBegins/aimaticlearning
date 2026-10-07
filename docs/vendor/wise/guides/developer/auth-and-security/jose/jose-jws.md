# JSON Web Signature (JWS)

Learn how JOSE JWS works with Wise Platform.

JSON Web Signature (JWS) is the JOSE standard that provides a framework to digitally sign JSON content.

Implementing JWS in your system ensures the sender's identity and message haven't been altered, providing non-repudiation for your interactions with the Wise API.

Summary of the signing process:

1. Create a key pair and deliver the public key to Wise.
2. Wise installs the public key to be consumed by the Wise API.
3. Once installed, you can call JWS enabled endpoint with signed request bodies.
4. Wise verifies the signature using the public key provided and performs additional checks, including the validity of the URL.
5. Wise returns the response encoded and signed.
6. Your system verifies and decodes the header and payload from the returned JWS.


## Providing public keys 

You can upload your public JWS key in [Developer Hub](https://wise.com/developer-hub). If you do not yet have access to Developer Hub, contact your implementation team for access.

Alternatively, you can [upload public keys via API](/api-reference/jose/joserequestpublickeyscreate).

Never share or upload your **private** key to Wise. Only upload the **public** key.

### JWS key properties

| Property  | Required? | Description |
|  --- | --- | --- |
| `keyId` | Yes | The unique public key identifier, in UUID format. The public Key ID of the private key you are signing with is set as the JWS `kid` header, indicating which key to use to validate the signature. |
| `scope` | Yes | Value for JWS is always `PAYLOAD_SIGNING` when uploading via API. When uploading in Developer Hub, this is set automatically in our system when you choose the upload JWS key option (rather than the JWE key option) |
| `validFrom` | Yes | The date and time when the key will become valid. Date cannot be in the past, but you can set a future date, if desired. |
| `validTill` | Yes | The date and time the key will expire. Must be later than the `validFrom` timestamp.

Be sure to [rotate your key](/guides/developer/auth-and-security/jose/jose-jws-key-rotation) before the expiration. |
| `publicKeyMaterial.algorithm` | Yes | The algorithm used to generate your key. Available values: `ES256`, `ES384`, `ES512`, `PS256`, `PS384`, `PS512` |
| `publicKeyMaterial.keyMaterial` | Yes | Public key material.

When pasting into Developer Hub, use JWK or PEM format. When uploading via API, use DER (Distinguished Encoding Rules) format, base64 encoded. |


### Upload JWS via Developer Hub

1. Log in to Developer Hub:
  - **Sandbox testing**: Log in to the [Developer Hub sandbox](https://wise-sandbox.com/developer-hub/) with your sandbox credentials.
  - **Production**: Log in to the [Developer Hub (production)](https://wise.com/developer-hub) with your production credentials.
2. Go to **Authentication → JOSE**.
3. Make sure you are on the **JWS (Signing)** tab and then click **Upload new JWS key**.
4. Enter your public key details:
  - Paste your public key material.
  - Choose the algorithm that matches your key type.
  - Enter the unique **Key ID** (`kid` in UUID format).
  - Set the **Valid From** and **Valid Until** fields. The Valid Until field determines when the key expires.


After upload, the new key appears in the JWS list alongside any existing keys.

## Manually signing a request 

Here is a step-by-step workflow, with example commands, to manually sign a request.

Wise uses a standard implementation of JOSE JWS. For more information on constructing, signing, and validating JWS, go to [JSON Web Signature (JWS)](https://openid.net/specs/draft-jones-json-web-signature-04.html).

### Create request headers & body

Create the required request body for the REST endpoint you wish to call, as well as the [JWS header](https://datatracker.ietf.org/doc/html/rfc7515#page-8) with required parameters. These will be signed in the next stage.

Required JOSE header parameters for JWS:

| Header | RFC |
|  --- | --- |
| alg | [RFC-7515 section-4.1.1](https://www.rfc-editor.org/info/rfc7515/#section-4.1.1) |
| kid | [RFC-7515 section-4.1.4](https://www.rfc-editor.org/info/rfc7515/#section-4.1.4) |
| url | Private Header Parameter |


Important!
The `url` custom parameter must be included since Wise uses this to verify the request path has not been tampered with. Both the headers and payload are signed and verified against the actual call.

JOSE header for JWS
```json
{
  "alg": "ES512",
  "typ": "JWT",
  "kid": "663a0e44-aa4a-4ff0-a9f8-cd99f5fbad71",
  "url": "/v3/profiles/12345/transfers/12345/payments"
}
```

Payload to be signed
```json
{
  "type": "BALANCE"
}
```

### Sign with private key

We accept JWS requests as JWTs using JWS compact serialization as defined in the [JOSE standard for JWS](https://datatracker.ietf.org/doc/html/rfc7515#section-3.3).

We recommend you use an [established library](https://jwt.io/libraries) to complete this process to avoid difficulties and errors in the encoding and signing process.

Here is an example of the previous payload and header block signed using JWS compact serialization:

Signed example
```shell
ewogICJhbGciOiAiRVM1MTIiLAogICJ0eXAiOiAiSldUIiwKICAia2lkIjogIjY2M2EwZTQ0LWFhNGEtNGZmMC1hOWY4LWNkOTlmNWZiYWQ3MSIsCiAgInVybCI6ICIvdjMvcHJvZmlsZXMvMTIzNDUvdHJhbnNmZXJzLzEyMzQ1L3BheW1lbnRzIgp9
.ewogICJ0eXBlIjogIkJBTEFOQ0UiCn0=
.Z-B7ScaZ37U_0CKrv03LTi0O0GWR2Hm5shzoEj8xRmM
```

### Submit authenticated API request

The request must include the following headers:

- `Content-Type: application/jose+json`
- `Accept: application/jose+json`
- `X-TW-JOSE-Method: jws`


Complete API request example
```bash
curl -X POST 'https://api.transferwise.com/v3/profiles/12345/transfers/12345/payments' \
     -H 'Authorization: Bearer XXXXXXX' \
     -H 'Content-Type: application/jose+json' \
     -H 'Accept: application/jose+json' \
     -H 'X-TW-JOSE-Method: jws' \
     -H 'Accept-Encoding: identity' \
     -d 'ewogICJhbGciOiAiRVM1MTIiLAogICJ0eXAiOiAiSldUIiwKICAia2lkIjogIjY2M2EwZTQ0LWFhNGEtNGZmMC1hOWY4LWNkOTlmNWZiYWQ3MSIsCiAgInVybCI6ICIvdjMvcHJvZmlsZXMvMTIzNDUvdHJhbnNmZXJzLzEyMzQ1L3BheW1lbnRzIgp9.ewogICJ0eXBlIjogIkJBTEFOQ0UiCn0=.Z-B7ScaZ37U_0CKrv03LTi0O0GWR2Hm5shzoEj8xRmM'
```

### Verify the response

The response is a fully formed JWT using compact serialization.

Verify the response by fetching the latest Wise public key and checking the signature. See [Get Wise JWT public key](/api-reference/jose/joseresponsepublickeysget) for details.

Wise signs the response using the same algorithm used to sign the request body.

If there is no body in the original request, the ES512 algorithm will be used to sign the response.

Request
```bash
  $ curl -i -X GET 'https://api.wise-sandbox.com/v1/auth/jwt-public-key?algorithm=ES512&scope=PAYLOAD_SIGNING' \
         -H 'Content-Type: application/json' \
         -H 'Authorization: Bearer <your api token>'
```

## Rotating JWS keys

We recommend rotating your keys at least once every 12 months. However, you can rotate your keys as often as your security protocols require.

For steps to rotate your JWS keys, see the [Rotate JWS keys guide](/guides/developer/auth-and-security/jose/jose-jws-key-rotation).

## Troubleshooting

Use this section to diagnose common JWS failures.

### Signature verification failure

`400 Bad Request` response:

```json
{
  "error": "jws_error",
  "error_description": "Unable to verify the request signature"
}
```

This means Wise received your JWS but could not verify the signature.

Common causes:

| Cause  | How to diagnose | Solution |
|  --- | --- | --- |
| **Mismatched `kid`** | Check that the `kid` in your JWT header exactly matches the Key ID you received when uploading your public key. | Copy the `kid` from Developer Hub (in **Authentication → JOSE → JWS (Signing)**) and set it in your JWS header. |
| **Wrong private key** | Confirm you are signing with the private key from the same key pair whose public key you uploaded to Wise. | Re-sign using the correct private key. If you've lost it, revoke the old key, generate a new key pair and upload the new public key. |
| **Algorithm mismatch** | Verify that the `alg` in your JWS header (for example, `ES512`) matches the algorithm used to generate your key pair and the algorithm registered with Wise. | Regenerate the key pair using the correct algorithm, or update the `alg` header to match. |
| **`url` mismatch** | Compare the `url` in your JWS protected header with the actual endpoint path. Wise verifies these match. | Set `url` to the exact request path. |


### Malformed request error

A `400` or `422` response indicating a malformed or invalid request body, even though your payload JSON is correct.

**Cause**: The required JOSE HTTP headers are missing or incorrect. Without these headers, Wise does not detect the request as a signed JWS and attempts to parse the JWS compact serialization as plain JSON, which fails.

**Solution**: Ensure all three required headers are present on every JWS request:

```
Content-Type: application/jose+json
Accept: application/jose+json
X-TW-JOSE-Method: jws
```

### Unexpected server error

`500 Internal Server Error` with a generic message:

```json
{
  "message": "An unexpected error occurred",
  "request_id": "..."
}
```

Common causes:

| Cause  | How to diagnose | Solution |
|  --- | --- | --- |
| **Missing `kid` header** | Check your JWS protected header for the `kid` field. If you have multiple active signing keys, `kid` is required so Wise can identify which key to use. | Add `kid` to your JWS protected header, set to the Key ID of the signing key you are using. |
| **Revoked key** | Check your key status in Developer Hub under **Authentication → JOSE → JWS (Signing)**. If the key shows as revoked, it can no longer be used for verification. | Switch to signing with an active key. If you need to re-upload the old key, see [Rotate JWS keys](/guides/developer/auth-and-security/jose/jose-jws-key-rotation). |
| **Expired key** | Check the `validTill` timestamp for your key in Developer Hub. If it has passed, the key is no longer valid. | Upload a new key pair and update your signing configuration. |
| **Non-existent key** | The `kid` does not match any key in Wise's system. This could be a typo or a copy-paste error. | Verify the UUID is correct and matches a Key ID from Developer Hub. |


Improving error responses
Wise is working to make errors currently handled under the generic `500` error type more specific and descriptive.

In the meantime, use the diagnostic checklist below and include the `x-trace-id` response header when contacting support.

### Empty or null response body

The request appears to succeed but the response body is empty or null.

**Cause**: The `Accept-Encoding` HTTP header is set to `gzip`. Wise does not currently support compressed encoding for JOSE responses, which can result in the response body being silently dropped.

**Solution**: Set the `Accept-Encoding` header to `identity`:

```
Accept-Encoding: identity
```

### Wrong environment

Requests fail with verification errors even though signing works in another environment.

**Cause**: Signing keys are environment-specific. Keys uploaded in sandbox are not available in production, and vice versa.

- **Sandbox:** Upload keys via [Developer Hub sandbox](https://wise-sandbox.com/developer-hub/) and send requests to `api.wise-sandbox.com`.
- **Production:** Upload keys via [Developer Hub](https://wise.com/developer-hub) and send requests to `api.wise.com`.


### Diagnostic checklist

1. **HTTP headers**: Confirm `Content-Type: application/jose+json`, `Accept: application/jose+json`, and `X-TW-JOSE-Method: jws` are all present.
2. `Accept-Encoding`: Set to `identity`, not `gzip`.
3. **`kid` header**: Present in the JWS protected header and matches the Key ID of an active key in Developer Hub for the correct environment.
4. **`url` header**: Matches the actual API endpoint path in the request.
5. **Algorithm**: The `alg` in your JWS header matches the algorithm your key pair was generated with.
6. **Key pair**: You are signing with the private key that corresponds to the public key uploaded to Wise.
7. **Environment**: You are using keys and endpoints from the same environment (sandbox or production).


### Contacting support

When contacting Wise about a JWS issue, include:

- The `x-trace-id` from the response headers.
- The HTTP status code and full response body.
- The environment (sandbox or production).
- The `kid` you are using.


This helps the support team diagnose the issue quickly. Contact [api@wise.com](mailto:api@wise.com).