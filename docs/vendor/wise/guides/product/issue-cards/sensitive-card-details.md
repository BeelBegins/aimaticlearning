# Sensitive card details

Securely handle card data with end-to-end encryption

Card details (PAN, CVV, PIN) are sensitive data that are strongly secured by RSA and AES encryption algorithms.

To minimize risks of exposure, we take the stand to set up an end to end encrypted communication between the **Client and Wise**.
The encryption should be performed on the client side to ensure data integrity. The encrypted payload should be proxied to the backend which initiate the API call to Wise with the user token.

We are using the `JWE` standard to pass encrypted data. A JWE is composed of 5 parts that ensure the payload integrity and authentication checks. Each part is required and need to be base64 encoded.

Details to generate a valid `JWE`:

- Our RSA key uses the `RSAES-OAEP-256` encryption algorithm (we still support `RSAES-PKCS1-V1_5`, however, we strongly suggest migrating to the more secure method).
- The AES key should be of length `256` and use `AES-GCM` encryption algorithm.
- The length of the Initialisation Vector should be of length `12`.


Please reach out to our team to get an implementation code example.

## Card PIN encryption  

This section explains how to set a card PIN for your customer when ordering a card.
If you don't need this feature, a PIN will be automatically generated instead.

Please contact Wise to enable this feature.

1. Fetch the `RSA key` from Wise's endpoint.
2. Generate an `AES key` directly from your client.
3. Use the `AES key` to encrypt your pin.
4. Use the `RSA Key` to encrypt your `AES key`.
5. Build an encrypted JSON (`JWE`).
The payload part encapsulate the *AES encrypted PIN* (**step 3**) and the *RSA encrypted AES key* (**step 4**).
6. Proxy the call to your backend. Call /POST set pin with a user token.


Sensitive card details encryption
## Sensitive card data decryption 

1. Fetch the `RSA key` from Wise's endpoint.
2. Generate an `AES key` directly in your client.
3. Use the `RSA Key` to encrypt your `AES key`.
4. Build an encrypted JSON (`JWE`) from **step 3**.
5. Proxy the call to your backend. Call one of sensitive card details endpoints with a user token.
6. The response is an `JWE`. Use your same key generated previously (**step 2**) to decrypt the response.


Sensitive card details decryption