Find discoverable Wise profiles and add them to your recipient list using an identifier — such as a Wisetag, email, or phone number — without needing bank details.

Creating a transfer with a contact 

1. [Create a Quote](/api-reference/quote/quotecreate), passing `contactId` instead of `targetAccount` in the request body.
2. Extract the `targetAccount` value from the Quote response — Wise resolves the contact into a recipient account.
3. [Create a Transfer](/api-reference/standard-transfer/transfercreate) using the `targetAccount` from the Quote response.