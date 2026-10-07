# 15 Jan Detailed Changelog

Multiple ID fields are now explicitly documented as `int64` (64-bit integer). Please ensure your integration stores these IDs using the appropriate 64-bit type (e.g., Long in Java, BIGINT in SQL).

Key fields to note:

- transfer ID - approaching the `int32` upper bound
- recipient ID - approaching the `int32` upper bound
- card transaction ID - past the `int32` upper bound
- user ID
- profile ID
- balance ID


The detailed changelog of data type updates across API endpoints is listed below. Review to confirm your integration uses 64-bit data types where required.

| Endpoint | Updated fields |
|  --- | --- |
| [Address](/api-reference/address) | `profile`, `id` |
| [Balance](/api-reference/balance) | `id` |
| [Balance Conversion](/api-reference/balance/balancemovement) | `profileId`, `sourceBalanceId`, `targetBalanceId` |
| [Balance - Excess Money Account](/api-reference/balance/excessmoneyaccount) | `profileId`, `recipientId`, `userProfileId` |
| [Balance Statement](/api-reference/balance-statement) | `balanceId`, `query.accountId` |
| [Bank Account Details](/api-reference/bank-account-details) | `profileId`, `targetAccountId`, `id` |
| [Batch Group](/api-reference/batch-group) | `profileId`, `version`, `shortId`, `userId`, `accountId`, `id`, `paymentInitiationId` |
| [Card](/api-reference/card) | `profileId`, `pageSize`, `pageNumber` |
| [Card Order](/api-reference/card-order) | `lifetimeLimit`, `cardHolderProfileId`, `id`, `profileId` |
| [Card Transaction](/api-reference/card-transaction) | `balanceTransactionId`, `balanceId` |
| [Case](/api-reference/case) | `id` |
| [Comparison](/api-reference/comparison) | `id` |
| [Disputes](/api-reference/disputes) | `profileId`, `transactionId` |
| [Direct Debit Account](/api-reference/direct-debit-account) | `id` |
| [Multi-Currency Account](/api-reference/multi-currency-account) | `id`, `profileId`, `recipientId` |
| [One Time Token](/api-reference/sca-ott) | `validity`, `userId` |
| [Profile](/api-reference/profile) | `id`, `address.id`, `operationalAddresses[n].id` |
| [Quote Object](/api-reference/quote) | `user`, `profile`, `option.price.priceSetId` |
| [Quote - Update a quote](/api-reference/quote/quoteupdate) | `targetAccount` |
| [Quote - Create authenticated quote](/api-reference/quote/quotecreate) | `profileId`, `targetAccount` |
| [Recipient](/api-reference/recipient) | `id`, `creatorId`, `profileId`, `seekPosition` |
| [Recipient - Create Recipient Account](/api-reference/recipient/recipientcreate) | `profile` |
| [Recipient - List Recipient Accounts](/api-reference/recipient/recipientlist) | `profileId`, `creatorId` |
| [Spend Controls](/api-reference/spend-controls) | `id` |
| [Transfer](/api-reference/transfer) | `profile` |
| [Transfer - Standard Transfer](/api-reference/standard-transfer) | `id`, `user`, `targetAccount`, `sourceAccount`, `quote`, `business` |
| [Transfer - Originator Transfer](/api-reference/third-party-transfer/getthirdpartytransfer) | `id`, `user`, `targetAccount`, `sourceAccount`, `business` |
| [Transfer - Create a Transfer](/api-reference/standard-transfer/transfercreate) | `targetAccount`, `sourceAccount` |
| [Transfer - Create Third Party](/api-reference/third-party-transfer/createthirdpartytransfer) | `targetAccount` |
| [Transfer - Partner License Transfer](/api-reference/transfer/transferpartnerlicencecreate) | `targetAccount`, `sourceAccount` |
| [Transfer - List of completed payments](/api-reference/transfer/transferpaymentslist) | `id` |
| [User](/api-reference/user/usergetbytoken) | `id`, `details.primaryAddress` |
| [User Security](/api-reference/user-security/usersecurityphonenumberlist) | `id` |
| [3DS challenge events](/api-reference/webhook-event/eventcards3dschallenge) (webhook event type) | `data.resource.profile_id`, `data.challenge_expires_after` |
| [Account details order state change event](/api-reference/webhook-event/eventaccountdetailsorderstatechange) (webhook event type) | `data.profile_id` |
| [Account details payment state change event](/api-reference/webhook-event/eventaccountdetailspaymentstatechange) (webhook event type) | `data.transfer.id` |
| [Additional verification state change event](/api-reference/webhook-event/eventprofilescddcheckstatechange) (webhook event type) | `data.resource.id` |
| [Balance account state change event](/api-reference/webhook-event/eventbalancesaccountstatechange) (webhook event type) | `data.resource.id`, `data.resource.profile_id` |
| [Balance credit events](/api-reference/webhook-event/eventbalancescredit) (webhook event type) | `data.resource.id`, `data.resource.profile_id` |
| [Balance update event](/api-reference/webhook-event/eventbalancesupdate) (webhook event type) | `data.resource.id`, `data.resource.profile_id`, `data.balance_id` |
| [Card order status change events](/api-reference/webhook-event/eventcardscardorderstatuschange) (webhook event type) | `data.resource.profile_id` |
| [Card production status change events](/api-reference/webhook-event/eventcardscardproductionstatuschange) (webhook event type) | `data.resource.profile_id` |
| [Card status change events](/api-reference/webhook-event/eventcardscardstatuschange) (webhook event type) | `data.resource.profile_id` |
| [Card transaction state change events](/api-reference/webhook-event/eventcardstransactionstatechange) (webhook event type) | `data.resource.profile_id`, `data.transaction_id`, `data.balance_transaction_id` , `data.debits[0].balance_id` , `data.credit.balance_id` |
| [KYC review state change event](/api-reference/webhook-event/eventkycreviewsstatechange) (webhook event type) | `data.resource.profileId` |
| [Overdraft limit threshold event](/api-reference/webhook-event/eventprofilesoverdraftlimitthreshold) (webhook event type) | `data.resource.id` |
| [Profile state change event](/api-reference/webhook-event/eventprofilesstatechange) (webhook event type) | `data.resource.id` |
| [Swift receive credit events](/api-reference/webhook-event/eventswiftincredit) (webhook event type) | `data.action.id`, `data.action.profile_id`, `data.action.account_id` |
| [Transaction disputes update events](/api-reference/webhook-event/eventtransactiondisputesupdate) (webhook event type) | `data.resource.profile_id`, `data.resource.transaction_id` |
| [Transfer active cases event](/api-reference/webhook-event/eventtransfersactivecases) (webhook event type) | `data.resource.id`, `data.resource.profile_id`, `data.resource.account_id` |
| [Transfer payout failure event](/api-reference/webhook-event/eventtransferspayoutfailure) (webhook event type) | `data.transfer_id`, `data.profile_id` |
| [Transfer refund event](/api-reference/webhook-event/eventtransfersrefund) (webhook event type) | `data.resource.id`, `data.resource.profile_id`,`data.resource.account_id` |
| [Transfer state change event](/api-reference/webhook-event/eventtransfersstatechange) (webhook event type) | `data.resource.id`, `data.resource.profile_id`,`data.resource.account_id` |
| [User state change events](/api-reference/webhook-event/eventusersstatechange) (webhook event type) | `data.resource.id` |
| [Verification state change event](/api-reference/webhook-event/eventprofilesverificationstatechange) (webhook event type) | `data.resource.id` |