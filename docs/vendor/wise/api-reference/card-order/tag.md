With this set of APIs, you will be able to create cards for your customers. You can also retrieve and view the status of your current card orders, as well as the list of available card programs for the user.

On production, each personal profile can order at most 1 physical card and 3 virtual cards. On sandbox, we allow up to 10 physical cards and 30 virtual cards for testing purpose. However, no more than 3 virtual cards can be ordered per day. This limit includes cards and card orders.

Card order status flow 

The card order response will contain the `status` field. The initial status is `PLACED` or `REQUIREMENTS_FULFILLED` depending on the requirement fulfillment state:

- `PLACED` - The card order is created. The card will be generated once it has fulfilled all the requirements
- `REQUIREMENTS_FULFILLED` - The card order has fulfilled all the requirements and the card should be generated in a short while
- `CARD_DETAILS_CREATED` - The card has been generated
- `PRODUCED` - The physical card has been produced and waiting to be picked up by delivery vendor (physical card only)
- `COMPLETED` - The card has been activated and is ready to use. The card order is completed
- `CANCELLED` - The card order has been cancelled. This can happen if you reach out to Wise Support to cancel a card order
- `RETURNED` - Delivery failed, the physical card has been returned and will be blocked (physical card only)


![Card order status state machine](/assets/card-order-status-flow.5dc3cd6580ca9beb1217ee786ebbd65a439ee722e9168a86b2b47b440ed09060.28b10c14.png)