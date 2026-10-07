# Card kiosk collection

We provide a `KIOSK_COLLECTION` delivery method. With this option, your card order is sent directly to a kiosk machine that encrypts the chip and prints card information. Please note that this method requires a complete customized hardware setup with our card manufacturer.

Please reach out to your Implementation Manager for more information

#### Order a card

In order to produce a card to collect at a kiosk, you have to explicitly set the `deliveryOption` to `KIOSK_COLLECTION` when [ordering a new physical card](/api-reference/card-order/cardordercreate). The limit of physical cards per profile applies regardless of the delivery method selected.

Once the card order requirements are fulfilled, the card order status will be set to `CARD_DETAILS_CREATED`.
We recommend to not show these card details until the physical card is successfully produced and collected. If the card production fails, this ensures the card can't be tokenised yet by the customer.

#### Produce a card

Subscribe to the [card-production-status-change](/api-reference/webhook-event/eventcardscardproductionstatuschange) webhook to get notified.

Please wait for the event with the status `READY` before producing the card. This ensures that all the card details are available as this step is asynchronous.

To produce the card, use the [produce card endpoint](/api-reference/card-kiosk-collection/cardkioskcollectionproduce) and include the mandatory `kioskId` field in the payload. In case multiple `kioskId` values have been configured, use the one you wish to send the card to.

Once the card has been successfully sent to the kiosk machine, you will receive an event with the status `IN_PROGRESS`, indicating that the card is currently being produced.

The card production process includes chip encryption and printing of card information (cardholder name, PAN, CVV, expiry date). The layout can be customized to include additional information.

Cards that were created over 60 days ago will result in a 422 error code and cannot be retried, this is due to the data being obfuscated on our side. In this case a new card order has to be created.

Production transition flow
Card production statuses transition state diagram
#### Get card production result

Once the card is produced, you will receive an event with the status `PRODUCED`. This means that the card has been successfully produced and collected from a kiosk machine. If the card is not collected, the system will return a `PRODUCTION_ERROR` status and the card will be redirected to a rejection hopper inside the machine.

If you receive an event with the status `PRODUCTION_ERROR`, it indicates that an issue occured during the production process. You can check the `errorCode` and `description` fields to determine the root cause of the problem.

Please consult the escalation process outlined for the project to troubleshoot the error. If the error can be manually solved (e.g., the hopper door is open), you can retry producing the same card by calling the [produce card endpoint](/api-reference/card-kiosk-collection/cardkioskcollectionproduce) after fixing the issue.

#### Get production result over api

We offer a [synchronous endpoint](/api-reference/card-kiosk-collection/cardkioskcollectionproductionget) that allows you to retrieve the latest production data that we received from the card manufacturer.

#### Simulate production status

To test out your integration, we provide an [API](/api-reference/simulation/simulationcardproduction) in the sandbox environment to simulate production statuses. This will assist you in simulating success or any potential errors that may occur on the kiosk machine.