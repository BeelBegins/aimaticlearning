# Security expiry notifications

Expiry notifications for mTLS certificates, JOSE JWS and JWE keys 

Wise sends security credentials expiry email reminders for:

- **mTLS client certificates** used to authenticate to Wise APIs
- **JOSE JWS & JWE keys** used for request signing and encrypting (based on the expiry date you provide when uploading the key)


This helps remind you to rotate certificates/keys before they expire and avoid interruptions to your integration.

## Who receives these emails

Notifications are sent to the **technical contact email address** we have on file for your organisation.

To ensure you receive expiry notifications we recommend you:

- Keep your **technical contact details up to date**
- Use a **shared mailbox**  rather than an individual address
- Ensure your email security tools allow receipt from Wise email domains


## When we send notifications

We send reminders ahead of the expiry date so you can rotate in time.

**Reminder schedule:** we currently send notifications **28, 14, 7, 3, 1, and 0 days** before the expiry date.

Notifications continue on the schedule until the expiring credential is no longer active (for example, revoked / replaced).

## What you need to do

When you receive an expiry notice, rotate the relevant credential before the expiry date:

- [mTLS setup & certificate rotation](/guides/developer/auth-and-security/mtls)
- [JWS setup & key rotation](/guides/developer/auth-and-security/jose/jose-jws-key-rotation)
- [JWE setup & key rotation](/guides/developer/auth-and-security/jose/jose-jwe-key-rotation)


If an mTLS certificate or JOSE key expires and is still being used, your integration may fail (for example, authentication or signature/encryption validation may no longer succeed). To avoid disruption, rotate credentials as soon as you receive an expiry reminder.