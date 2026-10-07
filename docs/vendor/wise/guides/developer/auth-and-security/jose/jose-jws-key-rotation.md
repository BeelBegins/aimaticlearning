# Rotate JWS keys

How to rotate JWS keys in the Developer Hub.

To limit the impact of a compromised key and avoid verification failures when keys expire, you should regularly rotate your JWS keys. Wise recommends rotating at least every 12 months, but you can rotate as frequently as your security protocols require.

Rotating your JWS keys means:

1. Generating a new key pair.
2. Uploading the **public** key to Wise in Developer Hub.
3. Switching your system to sign with the matching **private** key.


## Before you start

Plan a short **overlap window** where both the old and new public keys are present in Developer Hub. This lets you switch signing keys safely before revoking any keys.

## Step 1: Generate a new key pair

Generate a new key pair and store your **private** key securely (for example in an HSM or a secrets manager).

Never share or upload your **private** key to Wise. Only upload the **public** key.

## Step 2: Upload the new public key

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

## Step 3: Switch your signing system to the new private key

Update your signing configuration so newly created JWS/JWTs are signed with the **new private key**, and set the JWT/JWS header `kid` to the new Key ID.

- Test by [sending signed payloads with the new JWS key](/guides/developer/auth-and-security/jose/jose-jws#flow).
- Ensure the `kid` in your JWT header **exactly matches** the Key ID in Developer Hub.


Important
Keep the old public key available during the cutover. Don’t revoke it until you are confident all signing traffic is using the new `kid`.

## Step 4: Revoke the old public key

Once you’ve confirmed your integration is successfully signing with the new key, and requests are verifying as expected:

1. Return to **Authentication → JOSE → JWS (Signing)**.
2. Delete the **old** key and confirm when prompted.


## Troubleshooting key rotation

- **Verification failures after rotation**: Confirm your system is signing using the new private key *and* the JWT header `kid` matches the new Key ID in Developer Hub.
- **Wrong environment**: Keys uploaded in **sandbox** won’t work in **production** (and vice versa).
- **Revoked too early**: If you deleted the old key before all services switched, re-upload the old public key (if you still have it) and repeat the cutover more gradually.