# JSON Web Encryption (JWE)

Learn how JOSE JWE works with Wise Platform.

JSON Web Encryption (JWE) is the JOSE standard that provides a framework for secure encryption of JSON content.

Implementing JWE ensures that only the intended recipient can read the JSON request, providing confidentiality for sensitive data exchanged with the Wise API.

Summary of the encryption process:

1. Create a key pair and deliver the public key to Wise, for use in response encryption.
2. Request Wise's public key for use in request encryption.
3. Encrypt a request body using the Wise public encryption key and make a call to the Wise API.
4. Wise decrypts the encrypted request using its private key and then performs additional checks.
5. Wise returns the response encrypted with the provided public key.
6. Your system decrypts the payload from the returned JWE.


## Providing public keys 

You can upload your public JWE key in [Developer Hub](https://wise.com/developer-hub). If you do not yet have access to Developer Hub, contact your implementation team for access.

Alternatively, you can [upload public keys via API](/api-reference/jose/joserequestpublickeyscreate).

Never share or upload your **private** key to Wise. Only upload the **public** key.

### JWE key properties

| Property  | Required? | Description |
|  --- | --- | --- |
| `keyId` | Yes | The unique public key identifier, in UUID format. JWE requests must supply the `UUID` of the key to use for response encryption for Wise to disambiguate their keys. |
| `scope` | Yes | Value for JWE is always `PAYLOAD_ENCRYPTION` when uploading via API. When uploading in Developer Hub, this is set automatically in our system when you choose the upload JWE key option (rather than the JWS key option) |
| `validFrom` | Yes | The date and time when the key will become valid. Date cannot be in the past, but you can set a future date, if desired. |
| `validTill` | Yes | The date and time the key will expire. Must be later than the `validFrom` timestamp.

Be sure to [rotate your key](/guides/developer/auth-and-security/jose/jose-jwe-key-rotation) before the expiration. |
| `publicKeyMaterial.algorithm` | Yes | The algorithm used to generate your key. For JWE, the value is always `RSA_OAEP_256`. |
| `publicKeyMaterial.keyMaterial` | Yes | Public key material.

When pasting into Developer Hub, use JWK or PEM format. When uploading via API, use DER (Distinguished Encoding Rules) format, base64 encoded. |


### Upload JWE via Developer Hub

1. Log in to Developer Hub:
  - **Sandbox testing**: Log in to the [Developer Hub sandbox](https://wise-sandbox.com/developer-hub/) with your sandbox credentials.
  - **Production**: Log in to the [Developer Hub (production)](https://wise.com/developer-hub) with your production credentials.
2. Go to **Authentication → JOSE**.
3. Make sure you are on the **JWE (Encryption)** tab and then click **Upload new JWE key**.
4. Enter your public key details:
  - Paste your public key material.
  - Enter the unique **Key ID** (`kid` in UUID format).
  - Set the **Valid From** and **Valid Until** fields. The Valid Until field determines when the key expires.


After upload, the new key appears in the JWE list alongside any existing keys.

## Encrypting a request 

Here is a step-by-step workflow for successful request encryption.

Wise uses a standard implementation of JOSE JWE and employs the "Key Encryption" key management mode for request encryption using JWE compact serialization.

For more information on constructing, encrypting, and decrypting JWE, go to [JSON Web Encryption (JWE)](https://www.rfc-editor.org/rfc/rfc7516).

Currently, we only support the **RSA-OAEP-256** algorithm and the **A256GCM** content encryption algorithm. For further support of other algorithms and encryption methods, contact your implementation manager.

### Create request headers & body

Create the required request body for the REST endpoint you wish to call, as well as the [JOSE header](https://datatracker.ietf.org/doc/html/rfc7516#section-4) with required parameters. These will be encrypted in the next stage.

Required JOSE headers for JWE:

| Header | RFC |
|  --- | --- |
| alg | [RFC-7516 section-4.1.1](https://www.rfc-editor.org/rfc/rfc7516#section-4.1.1) |
| enc | [RFC-7516 section-4.1.2](https://www.rfc-editor.org/rfc/rfc7516#section-4.1.2) |


Example header and payload:

JOSE headers for JWE
```json
{
  "alg": "RSA-OAEP-256",
  "enc": "A256GCM"
}
```

Payload to be encrypted
```json
{
  "type": "GENERAL_ENQUIRY",
  "subject": "Inquiry about Transfer 12345",
  "details": {
    "transferId": 58114690,
    "profileId": 14556049,
    "userId": 1234
  },
  "externalId": "partner_external_id_12345",
  "description": "Initial summary of the issue"
}
```

### Encrypt the message

Wise supports JWE using Key Encryption as the [Key Management Mode](https://www.rfc-editor.org/info/rfc7516/#section-2).

Content must be encrypted using [JWE Compact serialization](https://www.rfc-editor.org/info/rfc7516/#section-3.1).

#### Supported cryptographic algorithms

| Name | RFC |
|  --- | --- |
| RSA-OAEP-256 | [RFC-7518 section-4.1](https://www.rfc-editor.org/rfc/rfc7518#section-4.1) |


#### Supported content encryption algorithms

| Name | RFC |
|  --- | --- |
| A256GCM | [RFC-7518 section-5.1](https://www.rfc-editor.org/rfc/rfc7518#section-5.1) |


For instructions on encrypting messages, please refer to [RFC-7516 section-5.1](https://www.rfc-editor.org/rfc/rfc7516#section-5.1).

Example HTTP request body using JWE Compact Serialization
```sh
eyJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0
.nzXdYfoI1X-4RVKuPp4U1b7oRGjz8zp5mqU-Otag0GUczxmifX3OqxBqMirfvdZXLdV6GgIyxZxlFeuF9C94cuFaIkA1frZy6bp-gY6dNrXTWebka34SWFwCNL8hfyzDRcWs6mQ0BNL5ALUfA3NO8Xh98yUSk1dnIMSHZvLd0feIP-1rYYDJsacIMnWA9zUjzY-rTsQbrzziGKtCvmRyzJAaCYfiYOAh-UjkmAhc5-xd3XPzqKeF-QaIGd0KTrr_Wucdq9CZsuEjXhKWfU27hacDtKaG_khUOKWfWTwoThRjfO9ckuO2oeB4UGLZ36IFSlMQ48p9s4PgnMg2YDCOrg
.fx2-MHbRsutByyOm
.d8MhWJo5Ih_fvTAmBGjfUMR5wc1V74ZS65Xy7Xx5MEAU8DEPbu1cQBu9U9l4BUZ2iR637C_JSo44EqDE26dDiow6LM-GIM-WWsR5f50A1_7vf89fJR4zfH6hob6g9YC-gMMTJ50x6fhspI1vBmXWvt4uXPmO4HTs06Rl3gs1jXyoA5_3A58IsFV1POMX3DUVPhKEVQwtlUtXgfEdyXXHnO854wWNbi7_pyn2vPABS_CyZy74JJGjDWovONRFZ81OkLGmyb2jQcQxlfetZz5wTbcQ86m-AGcf3nw41y4xXn8hODjGwnYY1BiSvZOt2kOmEGRaMHr2s3kTlhZ6rPJoLjodBkbUBM_W0g
.Sewt5vM_AClXhdCBVNbWyQ
```

### Submit authenticated API request

The Wise public API supports using JWE for all HTTP request methods, including those without an expected HTTP request body, such as GET requests.

Upon receiving an HTTP request without a body, the Wise API still performs payload encryption if `X-TW-JOSE-Method: jwe` is specified.

The request must include the following headers:

- `Content-Type: application/jose+json`
- `Accept: application/jose+json`
- `X-TW-JOSE-Method: jwe`
- `X-TW-JOSE-Encryption-kid`: Encryption Key ID (UUID)


The value of `X-TW-JOSE-Encryption-kid` must correspond to the ID of one of the public keys held by Wise. This header is **not** required if you are using the [direct response encryption strategy](#4b-direct-encryption-response-encryption).

Important
You must be able to decrypt responses encrypted using any of the public keys uploaded to Wise.

Use the ['kid' JWE header parameter](https://www.rfc-editor.org/info/rfc7516/#section-4.1.6) to identify which public key was used for encryption.

Complete POST request
```bash
curl -X POST 'https://api.transferwise.com/v1/cases' \
     -H 'Authorization: Bearer XXXXXXX' \
     -H 'Content-Type: application/jose+json' \
     -H 'Accept: application/jose+json' \
     -H 'X-TW-JOSE-Method: jwe' \
     -H 'X-TW-JOSE-Encryption-kid: 2333836d-2e1c-4acd-8b52-234d379260aa' \
     -H 'Accept-Encoding: identity' \
     -d 'eyJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAtMjU2IiwidXJsIjoiL3YxL2Nhc2VzIn0.B9g-Z3eJrKFK7eALNjL363ZXHn_us_axnfIJqB4GH8ayvL2QvK8OVlrONI3HGlq80zNzaFGSugzMzptJeQxa3jz92QK3Ks-JVRUH9vEMe99fDEuvvIWHKRA-yuCs1UBRSYjt1NxskX9Vo97xmjzLyy5ysOrz5SJYJj2okKnZ7DZuNNfZ7m6wKqxFJDJ2S_y6uJQXGiv5isip1WGd54qagiK5L_9pACZNBAG9IBErojY8L0xruCjkt1-2jktyDa6t1euER_CSstiYM55Lie2EZKnDKVIJ1zOuOEqMPOFEbwNhZaJyspNiWeu0l87zo7K8_Vu6VCeSaVo0fvH7Fm6Dtg.yenUpQ_KISjo0JMk.nk5h-UKewy4wJsCk2prAK5bmUbc-PQEPHW3YtxUMBk8u5X59bHXOsol5H4foKPeRvUIw8lx-yOLck2pvh7QESUoiWSwVguuKn3w-V3AdhhTXm6Bzij_6wndusILAHThBHlwRrUuU1amG69nNxDsLNv_zmZ1ZSZfwJz01sy6dcKEolD4xH72hPIBYKrNk5ihkiV8DgzTVF-rAcBODTQ10PTd4ZWIDsvTGL49neD9WcLMVpaUwG8NMOARY4w_pr0ikTlcjFUP2vOFhq6I1KwxrRJFRNb60ifY2w-_-2Dmab4kWtwTFrkFCj2T8hUV0vZQcYldxUGCDPnSIPaHk_x9O-y66lMwyyi70ug.AMyL0XyQJ6roHeGAc_Du1Q'
```

Complete GET request
```bash
curl -X GET 'https://api.transferwise.com/v1/cases/123456789' \
     -H 'Authorization: Bearer XXXXXXX' \
     -H 'Content-Type: application/jose+json' \
     -H 'Accept: application/jose+json' \
     -H 'X-TW-JOSE-Method: jwe' \
     -H 'X-TW-JOSE-Encryption-kid: 2333836d-2e1c-4acd-8b52-234d379260aa' \
     -H 'Accept-Encoding: identity'
```

### Decrypt the response

The Wise API is designed to enhance security by encrypting HTTP responses. When JWE is used in an HTTP request, Wise responds with a body encrypted using JWE.

The Wise API does not apply encryption or modify HTTP headers for empty responses.

Wise supports two response encryption strategies: **Same as Request** and **Direct Encryption**.

#### 'Same as Request' response encryption

For this strategy, the response encryption algorithm and the content encryption algorithm are matched with those used in the initial HTTP request. Wise generates a new CEK and respond using JWE compact serialization.

Wise includes the public key ID, which was used for encrypting the response payload, as part of the `kid` (Key Identifier) in the JOSE header.

Response JOSE headers
```json
{
  "alg": "RSA-OAEP-256",
  "enc": "A256GCM",
  "kid": "663a0e44-aa4a-4ff0-a9f8-cd99f5fbad71"
}
```

For instructions on decrypting messages, please refer to [RFC-7516 section-5.2](https://www.rfc-editor.org/rfc/rfc7516#section-5.2).

#### "Direct Encryption" response encryption

The Wise API supports end-to-end application-level encryption, which can be used for securing requests between mobile clients and Wise.

In this scenario, the encrypted CEK in the original request body is used for response encryption. The response body will be in JWE compact serialization form with no CEK in the body.

Response JOSE headers
```json
{
  "enc":"A256GCM",
  "alg":"dir"
}
```

For more information about direct encryption, refer to [RFC-7518 section-4.5](https://www.rfc-editor.org/rfc/rfc7518.html#section-4.5).

## Rotating JWE keys

We recommend rotating your keys at least once every 12 months. However, you can rotate your keys as often as your security protocols required.

For steps to rotate your JWE keys, see the [Rotate JWE keys guide](/guides/developer/auth-and-security/jose/jose-jwe-key-rotation).

Use this section to diagnose common JWE failures. If your issue is related to key rotation, also refer to [Rotate JWE keys](/guides/developer/auth-and-security/jose/jose-jwe-key-rotation).

## Troubleshooting

Use this section to diagnose common JWE failures.

### Encryption or decryption failure

Wise cannot decrypt your encrypted request. You receive a `500 Internal Server Error` with a generic error message.

Common causes:

| Cause  | How to diagnose | Solution |
|  --- | --- | --- |
| **Wrong encryption key** | You encrypted the request with a key other than Wise's current public encryption key — for example, your own public key or a key from another environment. | Fetch Wise's current public key using `GET /v1/auth/jose/response/public-keys?algorithm=RSA_OAEP_256&scope=PAYLOAD_ENCRYPTION` and re-encrypt. |
| **Wrong environment** | Wise's public encryption key differs between sandbox and production. | Fetch the public key from the same environment you are sending requests to. |
| **Missing `X-TW-JOSE-Encryption-kid`** | This header tells Wise which of your uploaded public keys to use for encrypting the response. If it is missing or incorrect, response encryption may fail. | Set it to the UUID of an active encryption key you have uploaded to Developer Hub. |
| **Revoked or expired key** | The encryption key referenced by `X-TW-JOSE-Encryption-kid` has been revoked or has passed its expiration date. | Check your key status in Developer Hub under **Authentication → JOSE →  JWE (Encryption)** and switch to an active key. |


Improving error responses
Wise is working to make errors currently handled under the generic `500` error type more specific and descriptive.

In the meantime, use the diagnostic checklist below and include the `x-trace-id` response header when contacting support.

### Response decryption failure

You receive an encrypted response from Wise but your system cannot decrypt it.

| Cause  | How to diagnose | Solution |
|  --- | --- | --- |
| **Wrong private key** | Check the `kid` in the JWE response header. This identifies which of your public keys Wise used to encrypt the response. | Decrypt using the private key that corresponds to the public key identified by `kid`. |
| **Old private key discarded** | If you recently rotated keys and deleted the old private key, responses encrypted with the old key will fail to decrypt. | During key rotation, keep both private keys available until all traffic uses the new key. See [Rotate JWE keys](/guides/developer/auth-and-security/jose/jose-jwe-key-rotation). |
| **Algorithm mismatch** | Your decryption library is configured with an algorithm that doesn't match what Wise used. | Wise uses **RSA-OAEP-256** (key encryption) and **A256GCM** (content encryption). Ensure your decryption configuration matches. |


### Malformed request error

You receive a `400` or `422` response indicating a malformed or invalid request body.

**Cause**: The required JWE HTTP headers are missing or incorrect. Without these headers, Wise does not detect the request as an encrypted JWE.

**Solution**: Ensure all required headers are present:

```
Content-Type: application/jose+json
Accept: application/jose+json
X-TW-JOSE-Method: jwe
X-TW-JOSE-Encryption-kid: <your-encryption-key-uuid>
```

When is X-TW-JOSE-Encryption-kid required?
The `X-TW-JOSE-Encryption-kid` header is required unless you are using the [direct response encryption strategy](#direct-response-encryption). It tells Wise which of your public keys to use when encrypting the response.

### Empty or null response body

The API call appears to succeed but the response body is empty or null.

**Cause**: The `Accept-Encoding` HTTP header is set to `gzip`. Wise does not currently support compressed encoding for JOSE responses.

**Solution**: Set the `Accept-Encoding` header to `identity`:

```
Accept-Encoding: identity
```

### Wrong environment

Encryption or decryption fails even though everything works in another environment.

**Cause**: Both Wise's public encryption keys and your uploaded keys are environment-specific. Sandbox keys do not exist in production and vice versa.

- **Sandbox:** Upload keys via [Developer Hub sandbox](https://wise-sandbox.com/developer-hub/), and fetch Wise's public key from `api.wise-sandbox.com`.
- **Production:** Upload keys via [Developer Hub](https://wise.com/developer-hub), and fetch Wise's public key from `api.wise.com`.


### Diagnostic checklist

1. **HTTP headers**: Confirm `Content-Type: application/jose+json`, `Accept: application/jose+json`, `X-TW-JOSE-Method: jwe`, and `X-TW-JOSE-Encryption-kid` are all present and correct.
2. `Accept-Encoding`: Set to `identity`, not `gzip`.
3. **Wise's public key**: You encrypted the request using Wise's current public encryption key for the correct environment.
4. `X-TW-JOSE-Encryption-kid`: Matches the UUID of an active encryption key you uploaded to Developer Hub.
5. **Response decryption**: Use the `kid` in the JWE response header to select the correct private key for decryption.
6. **Algorithm**: You are using **RSA-OAEP-256** for key encryption and **A256GCM** for content encryption.
7. **Environment**: You are using keys and endpoints from the same environment (sandbox or production).


### Contacting support

When contacting Wise about a JWE issue, include:

- The `x-trace-id` from the response headers.
- The HTTP status code and full response body.
- The environment (sandbox or production).
- The `X-TW-JOSE-Encryption-kid` value you are using.


Contact [api@wise.com](mailto:api@wise.com).