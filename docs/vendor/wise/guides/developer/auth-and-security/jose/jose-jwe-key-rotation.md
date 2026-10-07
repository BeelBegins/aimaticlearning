# Rotate JWE keys

How to rotate JWE keys in the Developer Hub.

To limit the impact of a compromised key and avoid encryption failures when keys expire, you should regularly rotate your JWE keys. Wise recommends rotating at least every 12 months, but you can rotate as frequently as your security protocols require.

Rotating your JWE keys means:

1. Generating a new key pair.
2. Ensuring your system can decrypt using both the new and old key.
3. Uploading the **public** key to Wise in Developer Hub.
4. Changing the requested encryption key to the new **public** key.
5. Revoking the old key.


We recommend a strategy of **progressive key rotation**, where the new encryption is switched over to gradually. This strategy mitigates risk during rotation, but it's also possible to switch all traffic over to the new encryption key, if preferred.

## Step 1: Generate a new key pair

Generate a new key pair and store your **private** key securely (for example in an HSM or a secrets manager).

Remember to generate a UUID key ID for the new JWE key.

Never share or upload your **private** key to Wise. Only upload the **public** key.

## Step 2: Add new private key to your system

Update your decryption configuration to ensure that you can decrypt responses encrypted using the new public key you will upload to Wise.

Important
You must be able to decrypt responses encrypted using any of the public keys uploaded to Wise.

Use the ['kid' JWE header parameter](https://www.rfc-editor.org/info/rfc7516/#section-4.1.6) to identify which public key was used for encryption.

## Step 3: Upload the new public key

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

## Step 4: Starting the progressive rotation

Change the `X-TW-JOSE-Encryption-kid` HTTP header to the UUID of your new key for a subset of requests. You can also send some separate test requests using the new key for response encryption to gain confidence before starting this stage.

If you can successfully decrypt all responses encrypted using your new public key, move on to the next stage.

Feel free to switch traffic over to the new key using any preferred rotation strategy. A hard switchover is possible, but is more risky than a progressive rotation.

## Step 5: Complete the progressive rotation

Once you are satisfied the new key is working appropriately, start using the new encryption key for all requests.

When you are certain no requests are being sent with the `X-TW-JOSE-Encryption-kid` HTTP header set to the old key UUID, you can progress to the next step.

## Step 6: Revoke the old public key

Important!
Do not revoke the old key until you are confident all encryption traffic is using the new `kid`.

Once you've confirmed Wise is encrypting with the new key and your system is successfully decrypting responses:

1. Return to **Authentication → JOSE → JWE (Encryption)**.
2. Delete the **old** key and confirm when prompted.


## Troubleshooting key rotation

- **Decryption failures after rotation**: Confirm your system is decrypting using the new private key *and* the JWE header `kid` matches the new Key ID in Developer Hub.
- **Wrong environment**: Keys uploaded in **sandbox** won't work in **production** (and vice versa).
- **Revoked too early**: If you deleted the old key before all services switched, re-upload the old public key (if you still have it and do not suspect it has been compromised) and repeat the cutover more gradually.