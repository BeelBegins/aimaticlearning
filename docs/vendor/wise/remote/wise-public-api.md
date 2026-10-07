# WisePublicApi


## Security

### BasicAuth

[object Object]

Type: http
Scheme: Basic

### ClientCredentialsToken

[object Object]

Type: oauth2
Token URL: /oauth/token
Scopes:

### PersonalToken

[object Object]

Type: http
Scheme: Bearer
Bearer Format: JWT

### UserToken

[object Object],[object Object],[object Object],[object Object]

Type: oauth2
Authorization URL: /oauth/authorize
Token URL: /oauth/token
Scopes:

## Download OpenAPI description

 - [WisePublicApi](https://docs.wise.com/_bundle/remote/wise-public-api.yaml)

## payment-methods

 - [POST /funding/payment-methods/balance/payins](https://docs.wise.com/remote/wise-public-api/payment-methods/createbalancepayin.md): This endpoint is SCA protected when it applies. If your profile is registered within the UK and/or EEA, SCA most likely applies to you. Please read more about [implementing SCA](/guides/developer/auth
 - [POST /funding/payment-methods/paynow/payins](https://docs.wise.com/remote/wise-public-api/payment-methods/createpaynowpayin.md): Creates a PayNow payment instruction for a payin session. PayNow is an SGD push payment method. A payin session is the unit of funding. It is returned when you create the object you want to fund, suc
 - [POST /funding/payment-methods/trusted-pre-fund/payins](https://docs.wise.com/remote/wise-public-api/payment-methods/createtrustedprefundpayin.md): Creates a trusted pre-fund payment for a payin session. Wise processes the funded object before receiving the settlement funds. You settle multiple trusted pre-fund payments later through one bulk pay
## gpi-tracking

 - [POST /v1/gpi-tracking](https://docs.wise.com/remote/wise-public-api/gpi-tracking/lookupgpitracking.md): Looks up GPI tracking data for a transfer identified by `identifierType` and `identifier`.
## incoming-transfer

 - [GET /v1/incoming-transfers/{incomingTransferId}](https://docs.wise.com/remote/wise-public-api/incoming-transfer/getincomingtransfer.md): Retrieves an incoming transfer by id. You can pull the incoming-transfer ID from the webhook payload.
## direct-debit-payments

 - [GET /v1/profiles/{profileId}/direct-debit/payments/{paymentId}](https://docs.wise.com/remote/wise-public-api/direct-debit-payments/getdirectdebitpaymentbyid.md): Retrieves a direct debit payment belonging to a profile by payment ID.
 - [GET /v1/profiles/{profileId}/direct-debit/payments/{paymentId}/refunds](https://docs.wise.com/remote/wise-public-api/direct-debit-payments/getdirectdebitrefundbypaymentid.md): Retrieves the refund associated with a direct debit payment. Returns the current state of the refund, enabling partners to track whether funds have been returned to the payer.
## direct-debit-mandates

 - [DELETE /v1/profiles/{profileId}/direct-debits/mandates/{mandateId}](https://docs.wise.com/remote/wise-public-api/direct-debit-mandates/cancelmandatebyid.md): Permanently cancels a direct debit mandate. Once cancelled, no new transactions will be processed against the mandate and the cancellation cannot be reversed via the API.
 - [GET /v1/profiles/{profileId}/direct-debits/mandates/{mandateId}](https://docs.wise.com/remote/wise-public-api/direct-debit-mandates/getmandatebyid.md): Retrieves a direct debit mandate belonging to a profile by mandate ID.
## settlement

 - [GET /v1/settlement/allocations/{allocation_id}](https://docs.wise.com/remote/wise-public-api/settlement/getsettlementallocation.md): Retrieves the details of a settlement allocation by its ID. Optionally includes paginated payment intents associated with the allocation.
 - [GET /v1/settlement/allocations/{allocation_id}/payment-intents/{payment_intent_id}](https://docs.wise.com/remote/wise-public-api/settlement/getpaymentintent.md): Retrieves the details of a specific payment intent within a settlement allocation.
## simulation

 - [POST /v1/simulation/settlement/funds](https://docs.wise.com/remote/wise-public-api/simulation/simulatesettlementallocationsfunds.md): Simulates the receipt of funds for a specific settlement allocation. This endpoint allows you to simulate the receipt of funds associated with a given allocation, which can be useful for testi
## bank-account-details

 - [GET /v2/balances/account-details/{id}](https://docs.wise.com/remote/wise-public-api/bank-account-details/getaccountdetails.md): Retrieves account details by ID. Account details identify an account that can receive funds (e.g. an IBAN, or a sort code and account number). GB, US and BE account details are supported. Requesting a
## third-party-transfer

 - [POST /v2/profiles/{profileId}/third-party-transfers](https://docs.wise.com/remote/wise-public-api/third-party-transfer/createthirdpartytransfer.md): When creating a transfer on behalf of a third party, you must take note that: * The `originator` datablock is **required**. This details the ultimate sender of funds in the transfer. * Depending on th
 - [GET /v2/profiles/{profileId}/third-party-transfers/{transferId}](https://docs.wise.com/remote/wise-public-api/third-party-transfer/getthirdpartytransfer.md): Get third party transfer info by ID. To receive dynamic updates as the state of the transfer changes, see the [webhooks documentation](https://docs.wise.com/api-reference/webhook).
## quote

 - [POST /v3/profiles/{profileId}/quotes](https://docs.wise.com/remote/wise-public-api/quote/quotecreate.md): You must use a user access token to authenticate this call and supply the profile with which the quote should be associated. This ensures that quote can be used to create a transfer. If you are fundin
 - [GET /v3/profiles/{profileId}/quotes/{quoteId}](https://docs.wise.com/remote/wise-public-api/quote/quoteget.md): Get quote info by Profile and ID. If the quote has expired (not used to create a transfer within 30 minutes of quote creation), it will only be accessible for approximately 48 hours via this endpoint.
 - [PATCH /v3/profiles/{profileId}/quotes/{quoteId}](https://docs.wise.com/remote/wise-public-api/quote/quoteupdate.md): You should update a quote using a `PATCH` call to add a recipient. This will update the saved quote's data based on who and where the money will be sent to. Updating the quote with a recipient may cau
## transfer

 - [POST /v3/profiles/{profileId}/transfers/{transferId}/payments](https://docs.wise.com/remote/wise-public-api/transfer/transferfund.md): This endpoint is SCA protected when it applies. If your profile is registered within the UK and/or EEA, SCA most likely applies to you. Please read more about [implementing SCA](/guides/developer/auth
