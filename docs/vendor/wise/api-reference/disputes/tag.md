Raise and manage card transaction disputes, including submission via Dynamic Flow or direct API, file uploads, and dispute lifecycle tracking.

For implementation details, see:

- [Disputes via Dynamic Flow](/guides/product/issue-cards/card-disputes-dynamic-flow) — build a dispute UI using the Dynamic Flow framework
- [Disputes via API](/guides/product/issue-cards/card-disputes-api) — submit disputes directly, with per-reason request body details
- [Dispute management](/guides/product/issue-cards/card-disputes-management) — track and withdraw disputes


Dispute sub-statuses 

The possible `subStatus` values are:

- `SUBMITTED` — Initial status
- `IN_REVIEW` — The dispute is under review or requires additional information
- `REFUNDED` — The refund has been processed
- `REJECTED` — The dispute is invalid
- `WITHDRAWN` — The customer has withdrawn the dispute
- `CONFIRMED` — The dispute has been reviewed but a refund is not applicable
- `REFUND_IN_PROGRESS` — A refund is being processed
- `ATTEMPTING_RECOVERY` — A chargeback request has been submitted
- `RECOVERY_UNSUCCESSFUL` — The chargeback attempt was unsuccessful


The status transition diagram may undergo modifications in the future and only covers regular pathways.

Dispute statuses transition diagram