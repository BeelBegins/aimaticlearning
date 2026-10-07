# Mutual TLS

Learn how to set up mTLS with Wise.

Mutual certificate validation is a security process between two parties, such as with Wise and a client. Once both parties have successfully validated each other's certificates, they proceed to establish a secure, encrypted communication channel.

## Generating a certificate 

Generating a certificate involves the following:

1. Generating a CSR.
2. Uploading the CSR to Developer Hub.
3. Downloading the Wise certificate.
4. Testing the certificate.


### Step 1: Generate a CSR 

Use the following command as an example to generate a Certificate Signing Request (CSR), replacing `<name of your organisation>`.

Sample private key and CSR generation command
```
openssl req -nodes -newkey rsa:4096 -keyout sandbox-PRIVATE-KEY.key -out sandbox-certificate-request.csr -subj "/C=EU/O=<name of your organisation>"
```

The command outputs a private key called `sandbox-PRIVATE-KEY.key` and a certificate signing request called `sandbox-certificate-request.csr`.

*Do not share your private key with anyone — including us.*

#### CSR requirements

- The key algorithm should be RSA or ECC.
  - For an RSA key, the length should be at minimum 2048 bits (we support 2048, 3072, and 4096 bits).
  - For an ECC key, the length should be either 256 or 384 bits.
- You must set an organisation name, as in the example command above.
- Wise sets a Common Name (CN) for you, which will be your Client ID. If you put anything else in, it will be overridden to be your Client ID.
- The CSR should be in PEM format.
- We do not allow any comments or plain text metadata in the CSR.


### Step 2: Upload the CSR

Once you have generated your CSR:

1. Log into Developer Hub and go to the **Authentication** section.
  - If testing in the sandbox: use [Developer Hub Sandbox](https://wise-sandbox.com/developer-hub/) and log in with the sandbox account that you shared when you requested client credentials.
  - If implementing in production: use [Developer Hub](https://wise.com/developer-hub) and log in with the production account that you shared when you requested client credentials.
2. Go to the **Generate certificate** screen, give the certificate a unique name, and paste in the content of your CSR.
  - After you submit the form, the **Certificate Details** screen opens displaying the client certificate.
3. Copy the client certificate content into a file with `.pem` extension (for example, `sandbox-CERTIFICATE.pem` in the sandbox). Securely store that certificate in your key store.


### Step 3: Download the certificate

Go back to the Developer Hub **Authentication** section and click the **Get Wise Certificate** button.

This will download a Wise certificate for the environment you are in (sandbox or production).

Securely store the certificate in your trust store.

### Step 4: Test the certificate

Open a terminal/cmd window and go to the newly created cert folder.

To test the integrity of the private key and generated certificate, try executing:

Example command
```
openssl rsa -in sandbox-PRIVATE-KEY.key -noout -modulus
openssl x509 -in sandbox-CERTIFICATE.pem -noout -modulus
```

Compare that the outputs are the same.

To test an example request, try executing:

Example command
```shell
curl --key sandbox-PRIVATE-KEY.key \
     --cert sandbox-CERTIFICATE.pem \
     --cacert wise.ca-certificate.sandbox.pem \
    https://api-mtls.wise-sandbox.com/v1/authenticated/playground \
    -H 'Authorization: Bearer <access_token>'
```

- **Sandbox**: Once you have obtained the OAuth credentials and your certificate, you can test mTLS right away by changing the host to: `https://api-mtls.wise-sandbox.com`
- **Production**: Once you have completed your integration to the sandbox, follow the same process for production. You can use mTLS right away by changing the host to: `https://api-mtls.transferwise.com`.


## Renewing certificates

Your client certificate is valid for **12 months** from the date it was issued. Wise notifies you approximately 4 weeks before your certificate expires, but we
recommend you also set up your own internal monitoring.

If your certificate expires before you renew it, **all API calls to the mTLS endpoint will fail immediately**. The TLS handshake is rejected before the HTTP request is processed, so you will not receive an API response body.

Depending on your client library, you may see errors such as:

- A `403 Forbidden` response
- A TLS handshake failure (connection reset)
- An SSL error from your client library, for example `SSL_ERROR_HANDSHAKE_FAILURE_ALERT` or `CERTIFICATE_VERIFY_FAILED`


This affects **every** API call routed through the mTLS hostname (`api-mtls.transferwise.com` in production, `api-mtls.wise-sandbox.com` in sandbox).

### Certificate lifecycle

1. **Wise sends expiry alerts** at 28, 14, 7, 3, and 1 day(s) before your certificate expires.
2. **You generate a new CSR** and upload it via [Developer Hub](https://wise.com/developer-hub) (or [Developer Hub Sandbox](https://wise-sandbox.com/developer-hub/)) before the current certificate expires.
3. **You receive a new certificate** and update your integration to use it.
4. **You revoke the old certificate** once you have confirmed the new one is working.


### Renew before expiry

To avoid downtime, always renew your certificate **before** the current one expires. Wise allows up to 10 active certificates at a time, so you can have both the old and new certificates active simultaneously.

1. Generate a new CSR using the same process described above.
2. Upload the new CSR in Developer Hub and receive your new certificate.
3. Deploy the new certificate and private key to your integration.
4. Verify the new certificate works by making a test API call to the mTLS endpoint.
5. Once confirmed, revoke the old certificate in Developer Hub.


Start the renewal process at least **2 weeks** before expiry. This gives you time to generate, deploy, and test the new certificate without pressure.

### Monitor for certificate expiry

Do not rely solely on Wise notifications. Set up your own monitoring to track certificate expiry.

Without monitoring, an expired certificate can cause a complete integration outage that lasts until a new certificate is generated, uploaded, and deployed. Set up at least one of the suggested monitoring approaches.

#### Option 1: Scheduled expiry check

Use `openssl` to check whether your certificate will expire within a given window. The following command exits with code `1` if the certificate expires within 30 days:

```bash
openssl x509 -in your-CERTIFICATE.pem -checkend 2592000 -noout
# 2592000 = 30 days in seconds
# Exit code 0 = still valid
# Exit code 1 = expires within 30 days
```

Run this as a daily cron job or scheduled task and pipe the exit code into your alerting system (for example, Datadog, PagerDuty, Prometheus, or CloudWatch).

#### Option 2: Extract and track the expiry date

Extract the expiry date and store it in your monitoring system:

```bash
openssl x509 -in your-CERTIFICATE.pem -noout -enddate
# Example output: notAfter=Jul  8 12:00:00 2027 GMT
```

Set alerts at the **60-day** and **30-day** marks to begin the renewal process.

#### Option 3: Use your secrets manager

If you store certificates in a secrets manager or certificate store (such as HashiCorp Vault, AWS Certificate Manager, or Azure Key Vault), configure the built-in expiry alerting when you import the certificate.

## Additional resources

If you'd like to learn more about mutual certificate validation, visit the following resources:

- [Cloudflare: What is mutual TLS (mTLS)?](https://www.cloudflare.com/en-gb/learning/access-management/what-is-mutual-tls/)
- [SSL.com: Generate and secure your private keys](https://www.ssl.com/guide/ssl-best-practices/#ftoc-heading-3)
- [SSL.com: Private and public keys](https://www.ssl.com/article/private-and-public-keys/)