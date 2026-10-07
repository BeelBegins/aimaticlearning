The quote resource defines the currencies involved in a transfer, the amount to send, and the profile sending the money.

The quote resource is one of the resources required when creating a transfer, along with the recipient account that is receiving the funds.

### Types of quotes

With the Wise API you can create either **unauthenticated** or **authenticated** quotes.

**Unauthenticated quotes** are for illustrative purposes only. Use this option to display example rates before a user has created or linked an account. This endpoint does not require an auth token and the response has no ID, so it cannot be used to create a transfer.

**Authenticated quotes** require an auth token and provide a quote ID in the response, which you then use when creating a transfer.

Upon creating an authenticated quote, the current mid-market exchange rate is locked and will be used for the transfer created from the quote. The rate is locked for 30 minutes to give a user time to submit the transfer.

The quote response contains details like the exchange rate, the estimated delivery time, applicable fees, methods for the user to pay for the transfer, and quote expiration time. *Not all fields are applicable to all use cases*.