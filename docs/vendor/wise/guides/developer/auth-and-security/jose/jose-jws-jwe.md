# JWS + JWE

Learn how to sign and encrypt with a single call.

For the highest level of API security for your integration, implement both JSON Web Signature (JWS) and JSON Web Encryption (JWE) together.

Signatures verify the sender's identity and prevent tampering, and encryption ensures that only intended recipients can read the message content, providing complete protection.

The signing and encryption is completed via a combined JWS and JWE mechanism, supported by JOSE, providing both authenticity (through signing) and confidentiality (through encryption).

Here's a summary of the process:

1. Create two key pairs, one for signing and one for encryption, and deliver both public keys to Wise.
2. Wise installs both public keys to be consumed by the Wise API.
3. Once installed, you can call JWS+JWE enabled endpoints with signed and encrypted request bodies.
4. Wise first decrypts the request using Wise's private encryption key, then verifies the signature using your public signing key and performs additional checks.
5. Wise returns the response signed and encrypted — first signing the response, then encrypting the signed JWT. Your system must accept the media type provided (see details below).
6. Your system decrypts the response using your private encryption key, then verifies and decodes the signature using Wise's public signing key.


## Providing public keys 

You can upload both public JWS and JWE keys in [Developer Hub](https://wise.com/developer-hub). If you do not yet have access to Developer Hub, contact your implementation team for access.

See the [JSON Web Signing Key guide](/guides/developer/auth-and-security/jose/jose-jws) and [JSON Web Encryption Key guide](/guides/developer/auth-and-security/jose/jose-jwe) for instructions on uploading your keys to Developer Hub.

Alternatively, you can [upload public keys via API](/api-reference/jose/joserequestpublickeyscreate).

## Using JWS+JWE endpoints workflow 

Here is a step-by-step workflow, with example commands, to manually sign and encrypt a request.

Wise uses a standard implementation of the JOSE JWS and JWE standards.

### Create request header and body

Create a request body (according to the usual API reference) and sign it with the request URL in the header block (see example).

JWS header to be signed
```json
  {                                                                             
    "alg": "ES512",                                                             
    "typ": "JWT",                                                               
    "kid": "663a0e44-aa4a-4ff0-a9f8-cd99f5fbad71",                              
    "url": "/auth/jose/playground/jwsjwe"
  }
```

Payload to be signed
```json
  {    
    "message": "This is an example from docs.wise.com"                          
  }
```

Important!
The `url` must be included since Wise uses this to verify the request path has not been tampered with. Both the headers and payload are signed and verified against the actual call.

### Sign with private signing Key

The header and body should then be base64url encoded and signed, with the signature appended as per the [JOSE standard for JWS](https://jose.readthedocs.io/en/latest/#jws).

Wise recommends you use an [established library](https://jwt.io/libraries) to complete this process to avoid difficulties and errors in the encoding and signing process.

This example uses the header and body as shown above and signs it with a private signing key.

The three parts of this JWS are:

- Base64(base64url) Encoded Header
- Base64(base64url) Encoded Body
- Signed header + Body


Signed JWT example
```shell
  eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjY2M2EwZTQ0LWFhNGEtNGZmMC1hOWY4LW
  NkOTlmNWZiYWQ3MSIsInVybCI6Ii92MS9hdXRoL2pvc2UvcGxheWdyb3VuZC9qd3Nqd2UifQ.eyJtZ
  XNzYWdlIjoiVGhpcyBpcyBhbiBleGFtcGxlIGZyb20gZG9jcy53aXNlLmNvbSJ9.AS9QHdkWvUEn0L
  xQEMPRBzlceN78J-Le-Qm1XIkkSBpsGdc0WM0MZTIGFEAJEcWeUR2M-abtd5DRdar4hLzs9apPAQ-G
  T70SIDV6pX9-4UKfIfzJ4g305zCoHflTfn-ijvI7XrVR_yr7xO9GJo86bfBqAX_m5uuxyU7Jy9gM1e
  pd8HcC
```

### Encrypt the signed JWT with Wise's public encryption key

The signed JWT must now be encrypted using Wise's public encryption key.

First, [retrieve Wise's public encryption key](/api-reference/jose/joseresponsepublickeysget) via the endpoint. Then, encrypt the entire signed JWT string using the `RSA-OAEP-256` algorithm with Wise's public key.

The result will be a JWE token with five parts separated by dots:

- JWE Protected Header (Base64url encoded)
- JWE Encrypted Key (Base64url encoded)
- JWE Initialization Vector (Base64url encoded)
- JWE Ciphertext (Base64url encoded)
- JWE Authentication Tag (Base64url encoded)


Encrypted JWT (JWE) example
```shell
  eyJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.W0fuxaZOoyaBcxWwgtjEPkOnLd
  VNyH9ncZi5Y9xQbjD4sYJn8vEQmxKHDw5s14sWhdexSNAPTVMSyzwJaA-LRL0tZTEuQ.ohD4LLjImi
  KOV4Tu.Rgp9mc2JD6m9Zm5htSqrejwWYy0_hIylYdLD39ZCR-VnQ2VX-Tot8kKGeNncnv7hJ_ApANW
  iJpKJbiM.5hNt-uaxuOkOraGGZSmsig
```

### Submit authenticated API request

The request must include the following headers:

- `Content-Type: application/jose+json`
- `Accept: application/jose+json`
- `X-TW-JOSE-Method: jws+jwe`
- `Accept-Encoding: identity`
- `X-TW-JOSE-Encryption-kid`: Encryption Key ID (UUID)


The value of `X-TW-JOSE-Encryption-kid` must correspond to the ID of one of the public JWE keys you uploaded to Wise.

Complete API request example
```bash
  curl -X POST 'https://api.wise-sandbox.com/auth/jose/playground/jwsjwe' \  
       -H 'Authorization: Bearer XXXXXXX' \ 
       -H 'Content-Type: application/jose+json' \ 
       -H 'Accept: application/jose+json' \
       -H 'X-TW-JOSE-Method: jws+jwe' \
       -H 'Accept-Encoding: identity' \
       -H 'X-TW-JOSE-Encryption-kid: 2333836d-2e1c-4acd-8b52-234d379260aa' \
       -d 'eyJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.W0fuxaZOoyaBcxWwg
  tjEPkOnLdVNyH9ncZi5Y9xQbjD4sYJn8vEQmxKHDw5s14sWhdexSNAPTVMSyzwJaA-LRL0tZTEuQ.o
  hD4LLjImiKOV4Tu.Rgp9mc2JD6m9Zm5htSqrejwWYy0_hIylYdLD39ZCR-VnQ2VX-Tot8kKGeNncnv
  7hJ_ApANWiJpKJbiM.5hNt-uaxuOkOraGGZSmsig'
```

### Decrypt and verify the response

The response from Wise will be encrypted and signed. To process it you must first decrypt the response, then verify the signature.

#### Decrypt the response

Decrypt the response using your private encryption key. The response is a JWE token that must be decrypted using the RSA-OAEP-256 algorithm with your private encryption key.

Encrypted response from Wise
```shell
  eyJraWQiOiJiMzc0ODE1MC0xNGQ0LTRlMDAtYjM5NC03YWUwYzkzYmUyNDUiLCJlbmMiOiJBMjU2R0
  NNIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.VGhpcyBpcyB0aGUgZW5jcnlwdGVkIENFSw.aXZfdmFsd
  WU.ZW5jcnlwdGVkX3BheWxvYWQ.YXV0aF90YWc
```

After decryption, you will have a signed JWT (JWS) from Wise.

#### Verify the signature

Verify the signature of the decrypted JWT using Wise's public signing key. See [Get Wise's public key](/api-reference/jose/joseresponsepublickeysget) for details.

**Get Wise's public signing key**

```shell curl
curl -i -X GET \
  'https://api.wise-sandbox.com/v1/auth/jose/response/public-keys?version=0&algorithm=ES512&scope=PAYLOAD_SIGNING' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Use Wise's public signing key to verify the signature and decode the payload.

Wise signs the response using the same algorithm that was used to sign the request body.

If there is no body in the original request, the ES512 algorithm is used for signing the response.

Final decoded response
```json
  {                                                                             
    "message": "jose-playground-response-This is an example from docs.wise.com",
    "method": "POST"
  }
```

Note on algorithm selection
Wise matches the signing algorithm specified in your request header. If no algorithm is specified, Wise uses the algorithm associated with your currently active public key.

## Flow summary 

**Request Flow**

1. **Sign**: Create and sign your payload using your private signing key (JWS).
2. **Encrypt**: Encrypt the signed JWT using Wise's public encryption key (JWE).
3. **Send**: Submit the encrypted token to Wise with required headers.


**Response Flow**

1. **Decrypt**: Decrypt Wise's response using your private encryption key (JWE).
2. **Verify**: Verify the signature using Wise's public signing key (JWS).
3. **Process**: Extract and use the verified payload.


This approach ensures:

- **Authenticity**: The signature proves the message came from the claimed sender.
- **Integrity**: The signature ensures the message hasn't been tampered with.
- **Confidentiality**: The encryption ensures only the intended recipient can read the message.
- **Non-repudiation**: The signature provides proof of origin that cannot be denied.


## Testing

Use the [Playground JWS+JWE endpoint](/api-reference/jose/joseplaygroundjwsjweget) to test your JWS+JWE implementation in a safe environment before production use.

## Troubleshooting

Because JWS+JWE combines signing and encryption, failures can originate from either layer. Use the guidance below to identify which layer is affected, then refer to the detailed troubleshooting in the corresponding JWS or JWE guides.

### Identifying the failure layer

When Wise processes a JWS+JWE request, it first **decrypts** (JWE layer), then **verifies the signature** (JWS layer). This means:

- If decryption fails (wrong encryption key, wrong environment), Wise cannot read the payload at all. You will typically receive a `500 Internal Server Error`.
- If decryption succeeds but signature verification fails, you will receive a `400 Bad Request` with error code `jws_error`:


```json
{
  "error": "jws_error",
  "error_description": "Unable to verify the request signature"
}
```

Use the error response to determine which layer to troubleshoot:

| Error response | Likely layer | Refer to |
|  --- | --- | --- |
| `400` with `jws_error` | Signing (JWS) | [JWS troubleshooting](/guides/developer/auth-and-security/jose/jose-jws#troubleshooting) |
| `500 Internal Server Error` | Can apply to either layer | [JWE troubleshooting](/guides/developer/auth-and-security/jose/jose-jwe#troubleshooting) and [JWS troubleshooting](/guides/developer/auth-and-security/jose/jose-jws#troubleshooting) |
| `400` / `422` malformed request | Missing HTTP headers | Check all required headers below. |


### Required headers

Ensure all required headers are present for JWS+JWE requests:

```
Authorization: Bearer XXXXXXX
Content-Type: application/jose+json
Accept: application/jose+json
X-TW-JOSE-Method: jws+jwe
Accept-Encoding: identity
X-TW-JOSE-Encryption-kid: <your-encryption-key-uuid>
```

### Response processing

When processing responses from Wise, remember the order is reversed: **decrypt first**, then **verify the signature**.

If you cannot decrypt the response, see [JWE response decryption failure](/guides/developer/auth-and-security/jose/jose-jwe#response-decryption-failure).

If you decrypt successfully but signature verification fails, see [JWS signature verification failure](/guides/developer/auth-and-security/jose/jose-jws#signature-verification-failure).

### Contacting support

When contacting Wise about a JWS+JWE issue, include:

- The `x-trace-id` from the response headers.
- The HTTP status code and full response body.
- The environment (sandbox or production).
- The `kid` from your JWS header and the `X-TW-JOSE-Encryption-kid` value.


Contact [api@wise.com](mailto:api@wise.com).