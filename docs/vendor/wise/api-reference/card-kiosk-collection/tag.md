These APIs are designed to allow you to print and encrypt your card directly from a kiosk machine. The card information will be sent to our card manufacturer to configure and print the card on-site on a kiosk machine.

The card printing process will automatically begin once the request is received by our card manufacturer.

During the printing process, you will be notified via webhook about any [card production status change](/api-reference/webhook-event/eventcardscardproductionstatuschange).

Before using these APIs, make sure to read the guide on [kiosk collection](/guides/product/issue-cards/card-kiosk-collection#card-kiosk-collection).

Please reach out to your Implementation Manager for more information on these APIs.

**Testing**: In the sandbox environment, use the [card production simulation API](/api-reference/simulation/simulationcardproduction) to test your integration with various production statuses and error scenarios.

Production status flow 

These statuses represent the lifecycle of a card production:

- `READY` - Card is ready for production. The [produce card endpoint](/api-reference/card-kiosk-collection/cardkioskcollectionproduce) can be called.
- `IN_PROGRESS` - Card is being produced at the kiosk machine (chip encryption and printing in progress).
- `PRODUCED` - Card has been successfully produced and collected from the kiosk. This is a final state.
- `PRODUCTION_ERROR` - Card production failed. Check the errorCode to identify the issue, resolve it, then retry using the [produce card endpoint](/api-reference/card-kiosk-collection/cardkioskcollectionproduce).


A card with production status `PRODUCED` will trigger an asynchronous call to update the associated card order to `PRODUCED` status.

![Card production status flow](/assets/card-production-status-flow.d5febc132f8e8c7d98835174afa64aa4ef9182140a5494f0f6df4167ed116f50.28b10c14.png)