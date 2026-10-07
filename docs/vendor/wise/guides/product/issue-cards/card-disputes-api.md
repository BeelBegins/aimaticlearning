# Raise dispute via API

Using [dynamic flow](/guides/product/issue-cards/card-disputes-dynamic-flow) is the preferred way of implementing dispute submission. Alternatively you can submit disputes directly using our APIs.

To submit a dispute via API:

1. Pick a dispute reason from the [list below](#reason-examples). Do not use the [get reasons API](/api-reference/disputes/disputereasonsget) for the moment with this approach.
2. Upload any supporting files (receipts, screenshots, etc.) using the [file upload endpoint](#file).
3. [Submit the dispute](#submit) with the reason code, transaction details, and any uploaded file IDs.


## Upload a file 

Upload a file for use in a dispute submission. Use the `fileId` in the response when submitting the dispute.

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/spend/profiles/14547572/dispute-form/file \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: multipart/form-data' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -F receipt=string
```

For request/response details, see the [API reference](/api-reference/disputes/disputefileupload).

## Submit dispute 

Submit the dispute. The request body varies depending on the dispute reason — see [request body by dispute reason](#reason-examples) below.

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/spend/profiles/14547572/dispute-form/flows/VISA/WRONG_AMOUNT \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "transaction": {
      "transactionId": "12345",
      "email": "support@partner.com"
    },
    "form": {
      "charged": {
        "value": 50,
        "currency": "EUR"
      },
      "expected": {
        "value": 5,
        "currency": "EUR"
      },
      "agreedDetails": {
        "agreed": true,
        "agreedReason": "some reason"
      },
      "goods": "something",
      "details": "wrong amount dispute"
    },
    "disclaimer": {
      "allAnswered": true,
      "filesUploaded": true
    }
  }'
```

For request/response details, see the [API reference](/api-reference/disputes/disputesubmit).

## Request body by dispute reason 

***View request for dispute reason:***

Dispute Reason
*I didn't receive the money from the ATM or cash machine*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

atmMoneyQuestions
Required. See [AtmMoneyQuestions](#atm-money-questions) below.

details
Detailed explanation of what happened

#### AtmMoneyQuestions 

atmPartialWithdrawal
Whether the ATM dispensed something (`true`) or nothing at all (`false`). Required.

expected
How much was the customer expecting to receive from the ATM. See [Money](#money) below. Required.

expected
How much has the customer actually received from the ATM. See [Money](#money) below. Required only if `atmPartialWithdrawal` is `true`.

#### Money 

value
Amount. Required.

currency
Three-character currency code, e.g. `USD`. Required.

#### Files 

receipt
Receipt from the cash machine or picture of the screen showing the error encountered.

ATM_DISPENSED_NO_FUNDS
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "atmMoneyQuestions": {
      "atmPartialWithdrawal": "false",
      "expected": {
        "value": 100,
        "currency": "EUR"
      }
    },
    "details": "atmDetails"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  },
  "files": {
    "receipt": "123"
  }
}
```

ATM_DISPENSED_NO_FUNDS - partial
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "atmMoneyQuestions": {
      "atmPartialWithdrawal": "true",
      "expected": {
        "value": 100,
        "currency": "EUR"
      },
      "received": {
        "value": 50,
        "currency": "EUR"
      }
    },
    "details": "atmDetails"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  },
  "files": {
    "receipt": "123"
  }
}
```

*I've been charged twice for one purchase*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

paymentMethod
Required. See [PaymentMethodWrapper](#payment-method-wrapper) below.

details
#### MerchantContact 

contactedMerchant
Whether the customer has contacted the merchant, `true` or `false`. Required.

merchantSaid
Merchant response. Required if `contactedMerchant` is `true`

reasonNoContact
Reason for not contacting the merchant. Required if `contactedMerchant` is `false`

#### PaymentMethodWrapper 

paymentMethod
Payment method for the original charge. `WISE_CARD`, `ANOTHER_CARD`, `CASH`, `CHECK`, or `BANK_TRANSFER`. Required.

#### Files 

receipt
Receipt of the purchase.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

otherDoc
Any relevant documentation the customer may have.

BILLED_TWICE
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "merchantContact": {
      "contactedMerchant": "true",
      "merchantSaid": "Merchant said this"
    },
    "paymentMethod": {
      "paymentMethod": "WISE_CARD"
    },
    "details": "billed twice dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  },
  "files": {
    "receipt": "123",
    "correspondence": "456",
    "otherDoc": "789"
  }
}
```

*The order was cancelled*

**NB:** This reason code is **Visa-only**. For MasterCard, use `NO_GOODS_OR_SERVICES`.

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
Description of the ordered item. Required.

merchantWebsite
Website where the order was made.

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

refundDetails
Required. See [RefundDetails](#refund-details) below.

cancellationDetails
Required. See [CancellationDetails](#cancellation-details) below.

orderWasForItem
Whether the order was for merchandise (`true`) or services (`false`). Required.

goodsReceivedDetails
Required. See [GoodsReceivedDetails](#goods-received-details) below.

details
Detailed explanation of what happened.

#### MerchantContact 

contactedMerchant
Whether the customer has contacted the merchant, `true` or `false`. Required.

merchantSaid
Merchant response. Required if `contactedMerchant` is `true`

reasonNoContact
Reason for not contacting the merchant. Required if `contactedMerchant` is `false`

#### CancellationDetails 

cancellationActor
Who cancelled the order. `MERCHANT` or `CUSTOMER`. Required.

cancellationPolicy
Required only if `cancellationActor` is `CUSTOMER`. See [CancellationPolicy](#cancellation-policy) below.

merchantCancelMerchandiseDate
When did the merchant cancel the order. Required only if `cancellationActor` is `MERCHANT`.

#### CancellationPolicy 

policyProvided
Whether a cancellation policy was provided to the customer by the merchant. Required.

properlyCancelled
Whether the customer cancelled the order in accordance to the policy provided. Required only if `policyProvided` is `true`.

cancelledWithinDays
How many days after the transaction the order was cancelled.

cancellationNumber
Cancellation number, if available.

#### GoodsReceivedDetails 

receivedGoods
Whether the customer received the goods or services ordered. Required.

returnDetails
Required only if `receivedGoods` is `true`. See [ReturnDetails](#return-details) below.

#### ReturnDetails 

merchantNoResponse
Whether the merchant ignored the request to return the item. Required.

dateReturned
When did the customer send back the items. Required only if `merchantNoResponse` is `false`.

dateMerchantReceived
When did the merchant receive the returned items.

returnMethod
How were the items returned. `RETURN_LABEL`, `COURIER`, or `POST`. Required only if `merchantNoResponse` is `false`.

trackingNumber
Tracking number of the return shipment, if available.

#### RefundDetails 

isPartial
Whether the customer is owed a partial (`true`) or full (`false`) refund. Required.

amountDue
How much the customer is owed. Required only if `isPartial` is `true`. See [Money](#money) below.

reason
Why is the customer owed this amount. Required only if `isPartial` is `true`. See [Money](#money) below.

#### Money 

value
Amount. Required.

currency
Three-character currency code, e.g. `USD`. Required.

#### Files 

receipt
Receipt of the purchase.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

trackingNumber
Tracking number, if provided.

otherDoc
Any relevant documentation the customer may have.

CANCELLED_ORDER - by customer
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "merchantContact": {
      "contactedMerchant": "true",
      "merchantSaid": "Merchant said this"
    },
    "refundDetails": {
      "isPartial": "true",
      "amountDue": {
        "value": 50,
        "currency": "EUR"
      },
      "reason": "reasons"
    },
    "cancellationDetails": {
      "cancellationActor": "CUSTOMER",
      "cancellationPolicy": {
        "policyProvided": "true",
        "properlyCancelled": true,
        "cancelledWithinDays": 4,
        "cancellationNumber": "XJKSK-213"
      }
    },
    "goodsReceivedDetails": {
      "receivedGoods": "true",
      "returnDetails": {
        "merchantNoResponse": "false",
        "dateReturned": "2021-05-10",
        "dateMerchantReceived": "2021-05-16",
        "returnMethod": "COURIER",
        "trackingNumber": "SDHJBGPWE32"
      }
    },
    "purchaseDescription": "some item",
    "merchantWebsite": "http://some-website.com",
    "orderWasForItem": true,
    "details": "cancelled order dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

CANCELLED_ORDER - by merchant
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "merchantContact": {
      "contactedMerchant": "true",
      "merchantSaid": "Merchant said this"
    },
    "refundDetails": {
      "isPartial": "true",
      "amountDue": {
        "value": 50,
        "currency": "EUR"
      },
      "reason": "reasons"
    },
    "cancellationDetails": {
      "cancellationActor": "MERCHANT",
      "merchantCancelMerchandiseDate":"2021-05-12"
    },
    "goodsReceivedDetails": {
      "receivedGoods": "true",
      "returnDetails": {
        "merchantNoResponse": "false",
        "dateReturned": "2021-05-10",
        "dateMerchantReceived": "2021-05-16",
        "returnMethod": "COURIER",
        "trackingNumber": "SDHJBGPWE32"
      }
    },
    "purchaseDescription": "some item",
    "merchantWebsite": "http://some-website.com",
    "orderWasForItem": true,
    "details": "cancelled order dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  },
  "files": {
    "receipt": "123",
    "correspondence": "456",
    "prrofOfReturn": "789"
  }
}
```

*My card was lost or stolen*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

#### Transaction 

transactionId
ID of the transaction. Supports multiple values, comma-separated.

email
Email of the support team that Wise should reach out to

#### Form 

noPossessionReason
Why was the card not in the customer's possession: `LOST` or `STOLEN`. Required.

lostDate
When did the customer lost the card? Required.

lostDetails
How did the customer lose the card? Required.

discoveryDate
When did the customer discover the unauthorized transaction(s)? Required.

details
Detailed explanation of what happened. Required.

cancellationOption
Whether we may immediately cancel the card: `MAY_CANCEL` or `DONT_CANCEL`. Note: Wise may still cancel the card unilaterally. Required.

CARD_NO_POSSESSION
```
{
  "transaction": {
    "transactionId": "12345,23456",
    "email": "support@partner.com"
  },
  "form": {
    "noPossessionReason": "LOST",
    "lostDetails": "description of how i lost my card",
    "lostDate": "2021-04-05",
    "discoveryDate": "2021-04-10",
    "details": "details about card no possession dispute",
    "cancellationOption": "DONT_CANCEL"
  }
}
```

*I don't recognise a transaction*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

#### Transaction 

transactionId
ID of the transaction. Supports multiple values , comma-separated.

email
Email of the support team that Wise should reach out to

#### Form 

discoveryDate
When did the customer notice the unauthorized transaction? Required.

previousBusinessDetails
Required. See [PreviousBusinessDetails](#previous-business-details) below.

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

familyConfirmation
Whether the customer's friends and family confirmed they have not used the customer's card or made any online purchases with it. Required.

details
Detailed explanation of what happened. Required.

cancellationOption
Whether we may immediately cancel the card: `MAY_CANCEL` or `DONT_CANCEL`. Note: Wise may still cancel the card unilaterally. Required.

#### PreviousBusinessDetails 

hasPreviousBusiness
Whether the customer has done any business with this merchant in the past. Required.

purchaseDate
When was the last time the customer did business with this merchant.

purchaseDescription
What was the last order (merchandise/service) from the merchant. Required only if `hasPreviousBusiness` is `true`.

details
Detailed explanation of the last order.

#### MerchantContact 

hasContacted
Has the customer tried to reach out to the merchant directly? Required.

merchantSaid
What did the merchant say when the customer reached out to them? Required only if `hasContacted` is `true`.

CARD_POSSESSION - merchant not known
```
{
  "transaction": {
    "transactionId": "12345,23456",
    "email": "support@partner.com"
  },
  "form": {
    "previousBusinessDetails": {
      "hasPreviousBusiness": "false"
    },
    "merchantContact": {
      "hasContacted": "true",
      "merchantSaid": "nothing"
    },
    "discoveryDate": "2021-06-10",
    "familyConfirmation": true,
    "details": "card possession dispute",
    "cancellationOption": "MAY_CANCEL"
  }
}
```

CARD_POSSESSION - known merchant
```
{
  "transaction": {
    "transactionId": "12345,23456",
    "email": "support@partner.com"
  },
  "form": {
    "previousBusinessDetails": {
      "hasPreviousBusiness": "true",
      "purchaseDate": "2021-02-05",
      "purchaseDescription": "something",
      "purchaseDetails": "details about the purchase"
    },
    "merchantContact": {
      "hasContacted": "true",
      "merchantSaid": "nothing"
    },
    "discoveryDate": "2021-06-10",
    "familyConfirmation": true,
    "details": "card possession dispute but known merchant",
    "cancellationOption": "MAY_CANCEL"
  }
}
```

*The goods were fake or counterfeit*

**NB:** This reason code is **Visa-only**. For MasterCard, use `SOMETHING_WRONG_WHAT_WAS_RECEIVED`.

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
What did the customer order? Required.

merchantWebsite
Merchant website, if available.

receivedDetails
Required. See [ReceivedDetails](#receiveddetails) below.

notifiedBy
Who notified the customer that the goods are fake/counterfeit: `IP_OWNER`, `CUSTOMS`, `LAW_ENFORCEMENT` or `THIRD_PARTY`. Required.

notificationDate
When was the customer notified that the goods are fake/counterfeit? Required.

currentLocation
Where are the goods now? Required.

details
Detailed explanation of what happened.

#### ReceivedDetails 

hasReceived
Has the customer received the goods? Required.

receivedDescription
What did the customer actually receive? Required only if `hasReceived` is `true`.

receivedDate
When were the items received? Required only if `hasReceived` is `true`.

whatsWrong
What is wrong with the items? Required only if `hasReceived` is `true`.

hasReturned
Has the customer sent the items back to the merchant? Required only if `hasReceived` is `true`.

#### Files 

receipt
Receipt of the purchase.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

descriptionFile
Description of what was wrong.

otherDoc
Any relevant documentation the customer may have.

FAKE_OR_COUNTERFEIT
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "receivedDetails": {
      "hasReceived": "true",
      "receivedDescription": "fake something",
      "receivedDate": "2021-06-05",
      "whatsWrong": "it's fake",
      "hasReturned": false
    },
    "purchaseDescription": "something",
    "merchantWebsite": "http://website.com",
    "notifiedBy": "THIRD_PARTY",
    "notificationDate": "2021-06-10",
    "currentLocation": "with me",
    "details": "fake dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*The order never arrived*

**NB:** This reason code is **Visa-only**. For MasterCard, use `NO_GOODS_OR_SERVICES`.

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
What was ordered? Required.

merchantWebsite
Merchant website, if available.

expectedDate
When was the order expected to arrive? Required.

cancelledOrder
Did the customer cancel the order before the delivery date? Required.

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

refundDetails
Required. See [RefundDetails](#refund-details) below.

details
Detailed explanation of what happened.

#### MerchantContact 

contactedMerchant
Did the customer contact the merchant? Required.

merchantSaid
What did the merchant say? Required only if `contactedMerchant` is `true`.

reasonNoContact
Why was the merchant not contacted? Required only if `contactedMerchant` is `false`.

deliveryDetails
Required only if `contactedMerchant` is `true`. See [DeliveryDetails](#delivery-details) below.

#### DeliveryDetails 

wasDelivered
Did the merchant claim that the order was delivered? Required.

deliveryAddress
Where is the merchant claiming the order was delivered to?

isCorrectAddress
Whether the `deliveryAddress` is the customer's correct delivery address.

#### RefundDetails 

isPartial
Whether the customer is owed a partial (`true`) or full (`false`) refund. Required.

amountDue
How much the customer is owed. Required only if `isPartial` is `true`. See [Money](#money) below.

reason
Why is the customer owed this amount. Required only if `isPartial` is `true`. See [Money](#money) below.

#### Money 

value
Amount. Required.

currency
Three-character currency code, e.g. `USD`. Required.

#### Files 

receipt
Receipt of the purchase.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

trackingNumber
Tracking number, if provided.

otherDoc
Any relevant documentation the customer may have.

NEVER_ARRIVED
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "merchantContact": {
      "contactedMerchant": "true",
      "merchantSaid": "Merchant said this",
      "deliveryDetails": {
        "wasDelivered": "true",
        "deliveryAddress": "street x, tallinn",
        "isCorrectAddress": true
      }
    },
    "refundDetails": {
      "isPartial": "true",
      "amountDue": {
        "value": 10,
        "currency": "EUR"
      },
      "reason": "reasons"
    },
    "purchaseDescription": "something",
    "merchantWebsite": "website",
    "expectedDate": "2021-06-01",
    "cancelledOrder": false,
    "details": "never arrived dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*I never got the goods or service I ordered*

**NB:** This reason code is **MasterCard-only**. For Visa, use `CANCELLED_ORDER` or `NEVER_ARRIVED`.

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
Description of what's been purchased. Required.

merchantWebsite
Merchant Website, if available.

expectedDate
By when were the goods or services expected? Required.

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

details
Detailed explanation of what happened.

#### MerchantContact 

contactedMerchant
Did the customer contact the merchant? Required.

merchantSaid
What did the merchant say? Required only if `contactedMerchant` is `true`.

reasonNoContact
Why was the merchant not contacted? Required only if `contactedMerchant` is `false`.

#### Files 

receipt
Receipt of the purchase.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

trackingNumber
Tracking number, if provided.

otherDoc
Any relevant documentation the customer may have.

NO_GOODS_OR_SERVICES
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "merchantContact": {
      "contactedMerchant": "false",
      "reasonNoContact": "they ghosted me"
    },
    "purchaseDescription": "something",
    "merchantWebsite": "website",
    "expectedDate": "2021-06-01",
    "details": "no goods dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*I haven't received the refund*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

refundReason
Why is the customer owed a refund? Required.

purchaseDescription
What did the customer purchase? Required.

confirmationMethod
How did the merchant confirm the refund: `CREDIT_VOUCHER`, `VOIDED_TRANSACTION_RECEIPT`, or `EMAIL`. Required **only for Visa**.

dateExpected
When was the refund due? Required.

isAwareOfDelay
Is the customer aware that it can take up to 10 working days to receive a refund back into their account? Required **only for Visa**.

cancellationNumber
Cancellation number, if available. **MasterCard-only**.

cancellationActor
Who cancelled the transaction: `MERCHANT` or `CUSTOMER`. Required **only for MasterCard**.

refundDetails
Required. See [RefundDetails](#refund-details) below.

merchantSaid
What did the merchant say when the customer contacted them about the issue? Required.

details
Detailed explanation of what happened.

#### RefundDetails 

isPartial
Whether the customer is owed a partial (`true`) or full (`false`) refund. Required.

amountDue
How much the customer is owed. Required only if `isPartial` is `true`. See [Money](#money) below.

reason
Why is the customer owed this amount. Required only if `isPartial` is `true`. See [Money](#money) below.

#### Money 

value
Amount. Required.

currency
Three-character currency code, e.g. `USD`. Required.

#### Files 

refundConfirmation
Confirmation that a refund is owed.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

cancellationConfirmation
Cancellation confirmation.

otherDoc
Any relevant documentation the customer may have.

NO_REFUND - MasterCard
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "refundDetails": {
      "isPartial": "false"
    },
    "refundReason": "This is why I would like a refund",
    "purchaseDescription": "something",
    "dateExpected": "2021-03-05",
    "cancellationNumber": "ABCDE-123",
    "cancellationActor": "MERCHANT",
    "merchantSaid": "Merchant said this",
    "details": "no refund mc dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

NO_REFUND - Visa
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "refundDetails": {
      "isPartial": "false"
    },
    "refundReason": "This is why I would like a refund",
    "purchaseDescription": "something",
    "confirmationMethod": "EMAIL",
    "dateExpected": "2021-05-05",
    "isAwareOfDelay": true,
    "merchantSaid": "Merchant said this",
    "details": "no refund visa dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*The goods or services were not as described or defective*

**NB:** This reason code is **Visa-only**. For MasterCard, use `SOMETHING_WRONG_WHAT_WAS_RECEIVED`.

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
What was ordered? Required.

merchantWebsite
Merchant website, if available.

receivedDescription
What was received? Required.

receivedDate
When was the order received? Required.

issue
What is the nature of the issue: `NOT_AS_DESCRIBED` or `BROKEN_OR_DEFECTIVE`. Required.

whatsWrong
Detailed explanation of what is wrong with the purchase.

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

returnDetails
Required. See [ReturnDetails](#return-details) below.

refundDetails
Required. See [RefundDetails](#refund-details) below.

details
Detailed explanation of what happened.

#### MerchantContact 

contactMethod
How did the customer reach out to the merchant: `EMAIL`, `PHONE`, `CHAT`, or `SOCIAL_MEDIA`. Required.

contactDate
When did the customer reach out to the merchant? Required.

merchantSaid
What did the merchant say? Required.

#### ReturnDetails 

merchantNoResponse
Did the merchant ignore the customer's request to return the item? Required.

dateReturned
When did the customer return the items? Required only if `merchantNoResponse` is `false`.

dateMerchantReceived
When did the merchant receive the items back?

returnMethod
How were the items returned: `RETURN_LABEL`, `COURIER`, `POST`. Required only if `merchantNoResponse` is `false`.

trackingNumber
Tracking number of the return shipment, if available.

#### RefundDetails 

isPartial
Whether the customer is owed a partial (`true`) or full (`false`) refund. Required.

amountDue
How much the customer is owed. Required only if `isPartial` is `true`. See [Money](#money) below.

reason
Why is the customer owed this amount. Required only if `isPartial` is `true`. See [Money](#money) below.

#### Money 

value
Amount. Required.

currency
Three-character currency code, e.g. `USD`. Required.

#### Files 

receipt
Receipt or confirmation of the transaction.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

descriptionFile
Description of what was wrong.

otherDoc
Any relevant documentation the customer may have.

NOT_AS_DESCRIBED
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "returnDetails": {
      "merchantNoResponse": "false",
      "dateReturned": "2021-05-06",
      "dateMerchantReceived": "2021-05-12",
      "returnMethod": "RETURN_LABEL",
      "trackingNumber": "BLEAXC-4324"
    },
    "refundDetails": {
      "isPartial": "false"
    },
    "purchaseDescription": "something",
    "merchantWebsite": "http://website",
    "receivedDescription": "something else",
    "receivedDate": "2021-06-01",
    "issue": "BROKEN_OR_DEFECTIVE",
    "whatsWrong": "it's missing a crucial piece",
    "merchantContact": {
      "merchantSaid": "that they'd refund me",
      "contactMethod": "EMAIL",
      "contactDate": "2021-05-05"
    },
    "details": "not as described dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*The goods or services have quality issues*

**NB:** This reason code is **Visa-only**. For MasterCard, use `SOMETHING_WRONG_WHAT_WAS_RECEIVED`.

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
What did the customer order? Required.

merchantWebsite
Merchant website, if available.

receivedDescription
What did the customer receive? Required.

receivedDate
When was the order received?

whatsWrong
What are the quality issues?

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

orderDetails
Required. See [OrderDetails](#order-details) below.

refundDetails
Required. See [RefundDetails](#refund-details) below.

details
Detailed explanation of what happened.

#### MerchantContact 

contactMethod
How did the customer reach out to the merchant: `EMAIL`, `PHONE`, `CHAT`, or `SOCIAL_MEDIA`. Required.

contactDate
When did the customer reach out to the merchant? Required.

merchantSaid
What did the merchant say? Required.

#### OrderDetails 

orderType
What type of order was it: `MERCHANDISE` or `SERVICE`. Required.

returnDetails
Required if `orderType` is `MERCHANDISE`. See [ReturnDetails](#return-details) below.

serviceCancellationDetails
Required if `orderType` is `SERVICE`. See [ServiceCancellationDetails](#service-cancellation-details) below.

qualityOfFoodInd
Whether the dispute is about the quality of the food served in a restaurant. Required if `orderType` is `SERVICE`.

#### ReturnDetails 

hasReturned
Has the customer already returned the items?

dateReturned
When did the customer return the items? Required only if `hasReturned` is `true`.

dateMerchantReceived
When did the merchant receive the items back?

returnMethod
How were the items returned: `RETURN_LABEL`, `COURIER`, `POST`. Required only if `hasReturned` is `false`.

trackingNumber
Tracking number of the return shipment, if available.

#### ServiceCancellationDetails 

hasCancelled
Has the customer cancelled the service? Required.

cancellationDate
When was the cancellation request done?

paidForRework
Did the customer pay to have the work redone?

#### RefundDetails 

isPartial
Whether the customer is owed a partial (`true`) or full (`false`) refund. Required.

amountDue
How much the customer is owed. Required only if `isPartial` is `true`. See [Money](#money) below.

reason
Why is the customer owed this amount. Required only if `isPartial` is `true`. See [Money](#money) below.

#### Money 

value
Amount. Required.

currency
Three-character currency code, e.g. `USD`. Required.

#### Files 

receipt
Receipt or confirmation of the transaction.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

descriptionFile
Description of what was wrong.

otherDoc
Any relevant documentation the customer may have.

QUALITY_ISSUES - did not contact merchant
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "orderDetails": {
      "orderType": "SERVICE",
      "serviceCancellationDetails": {
        "hasCancelled": "true",
        "cancellationDate": "2021-06-03",
        "paidForRework": true,
        "qualityOfFoodInd":false
      }
    },
    "refundDetails": {
      "isPartial": "false"
    },
    "purchaseDescription": "something",
    "merchantWebsite": "http://merchant",
    "receivedDescription": "something else",
    "receivedDate": "2021-06-01",
    "whatsWrong": "something is wrong",
    "merchantContact": {
      "merchantSaid": "Merchant said this",
      "contactMethod": "PHONE",
      "contactDate": "2021-06-02"
    },
    "details": "quality issues dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

QUALITY_ISSUES - contacted merchant
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "purchaseDescription": "something",
    "merchantWebsite": "http://merchant",
    "receivedDescription": "something else",
    "receivedDate": "2021-06-01",
    "whatsWrong": "somthing is wrong",
    "merchantContact": {
      "merchantSaid": "Merchant said this",
      "contactMethod": "PHONE",
      "contactDate": "2021-06-02"
    },
    "orderDetails": {
      "orderType": "MERCHANDISE",
      "returnDetails": {
        "hasReturned": "true",
        "dateReturned": "2021-06-03",
        "dateMerchantReceived": "2021-06-10",
        "returnMethod": "POST",
        "trackingNumber": "BLABLA-123"
      }
    },
    "refundDetails": {
      "isPartial": "false"
    },
    "details": "quality issues dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*I cancelled a subscription and was charged again*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

cancelledDate
When was the subscription cancelled? Required.

cancellationReason
Why did the customer cancel the subscription? Required **only for Visa**.

merchantWebsite
Merchant website, if available.

merchantConfirmation
Required **only for Visa**. See [MerchantConfirmation](#merchant-confirmation) below.

alternativePaymentMethod
Did the merchant ask for another payment method for billing the remaining subscription? Required **only for Visa**.

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

details
Detailed explanation of what happened.

#### MerchantConfirmation 

MerchantConfirmation
merchantConfirmed
Did the merchant confirm that the account was closed or the subcription was cancelled? Required.

confirmationDate
When did the customer receive the confirmation? Required if `merchantConfirmed` is `true`.

#### MerchantContact 

MerchantContact
contactMethod
How did the customer reach out to the merchant: `EMAIL`, `PHONE`, `CHAT`, or `SOCIAL_MEDIA`. Required.

contactDate
When did the customer reach out to the merchant? Required.

merchantSaid
What did the merchant say? Required.

#### Files 

files
cancellationConfirmation
Cancellation confirmation.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

otherDoc
Any relevant documentation the customer may have.

CHARGED_RECURRING_PAYMENT - MasterCard
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "cancelledDate": "2021-04-01",
    "merchantContact": {
      "merchantSaid": "Merchant said this",
      "contactMethod": "CHAT",
      "contactDate": "2021-04-05"
    },
    "details": "recurring payment mc dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

CHARGED_RECURRING_PAYMENT - Visa
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "merchantConfirmation": {
      "merchantConfirmed": "true",
      "confirmationDate": "2021-04-05"
    },
    "cancelledDate": "2021-04-01",
    "cancellationReason": "i didn't like the service",
    "alternativePaymentMethod": false,
    "merchantContact": {
      "merchantSaid": "Merchant said this",
      "contactMethod": "SOCIAL_MEDIA",
      "contactDate": "2021-05-06"
    },
    "details": "charged recurring payment visa dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*I think there might be an issue with the merchant*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
What did the customer purchase? Required.

merchantWebsite
Merchant website, if available.

expectedDate
By when did the customer expect to receive the order? Required.

websiteStillOperating
Is the merchant website still operating?

merchantSaid
What did the merchant say when contacted? Required.

investmentDetails
Required. See [InvestmentDetails](#investment-details) below.

details
Detailed explanation of what happened.

#### InvestmentDetails 

isInvestment
Is the transaction related to forex trading, investment brokers, cryptocurrencies, or gambling? Required.

acquaintanceExplanation
How did the customer know the merchant and decided to make an account or trade with them? Required if `isInvestment` is `true`.

#### Files 

receipt
Receipt or confirmation of the transaction.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

SCAM
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "investmentDetails": {
      "isInvestment": "true",
      "acquaintanceExplanation": "a friend referred me"
    },
    "purchaseDescription": "something",
    "merchantWebsite": "http://website",
    "expectedDate": "2021-06-05",
    "websiteStillOperating": true,
    "merchantSaid": "nothing",
    "details": "scam dispute"
  }
}
```

*Something is wrong with the goods or service I ordered*

**NB:** This reason code is **MasterCard-only**. For Visa, use `FAKE_OR_COUNTERFEIT`, `NOT_AS_DESCRIBED`, or `QUALITY_ISSUES`.

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

purchaseDescription
What did the customer purchase? Required.

merchantWebsite
Merchant website, if available.

received
What did the customer receive? Required.

whatsWrong
What is wrong with the received item? Required.

returnDetails
See [ReturnDetails](#return-details) below.

mechantContact
Required. See [MerchantContact](#merchant-contact) below.

details
Detailed explanation of what happened.

#### ReturnDetails 

hasReturned
Has the customer returned the items to the merchant?

trackingNumber
Tracking number of the return shipment, if available.

#### MerchantContact 

contactMethod
How did the customer reach out to the merchant: `EMAIL`, `PHONE`, `CHAT`, or `SOCIAL_MEDIA`. Required.

contactDate
When did the customer reach out to the merchant? Required.

merchantSaid
What did the merchant say? Required.

#### Files 

receipt
Receipt or confirmation of the transaction.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

descriptionFile
Description of what is wrong with the items.

otherDoc
Any relevant documentation the customer may have.

SOMETHING_WRONG_WHAT_WAS_RECEIVED
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "returnDetails": {
      "hasReturned": "true",
      "trackingNumber": "blabal-123"
    },
    "purchaseDescription": "something",
    "merchantWebsite": "http://website",
    "received": "something else",
    "whatsWrong": "it's not as described",
    "merchantContact": {
      "merchantSaid": "Merchant said this",
      "contactMethod": "SOCIAL_MEDIA",
      "contactDate": "2021-06-05"
    },
    "details": "something wrong dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*A past merchant unexpectedly charged me again*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

isRelatedToPreviousTransaction
Could the charge be related to a prior transaction with the merchant (e.g. subscriptions, rental agreements, due payments)? Required.

previousPurchase
What did you previously buy from this merchant? Required.

previousPurchaseDate
When was the last purchase done?

isAdditionalCharge
Could this charge be for additional services, fees, or damage charges (e.g. gas, tickets, tolls, late checkout, breakfast, etc.)? Required.

merchantContact
Required. See [MerchantContact](#merchant-contact) below.

details
Detailed explanation of what happened.

#### MerchantContact 

contactMethod
How did the customer reach out to the merchant: `EMAIL`, `PHONE`, `CHAT`, or `SOCIAL_MEDIA`. Required.

contactDate
When did the customer reach out to the merchant? Required.

merchantSaid
What did the merchant say? Required.

#### Files 

previousReceipt
Receipt or confirmation of the previous transaction.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

otherDoc
Any relevant documentation the customer may have.

UNEXPECTEDLY_CHARGED_AGAIN
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "previousPurchase": "something",
    "previousPurchaseDate": "2021-03-05",
    "isAdditionalCharge": "false",
    "isRelatedToPreviousTransaction": true,
    "merchantContact": {
      "merchantSaid": "Merchant said this",
      "contactMethod": "CHAT",
      "contactDate": "2021-04-05"
    },
    "details": "unexpected charge dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*I've been charged for a subscription without my permission*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

noticedDate
When did the customer notice the subscription charge? Required.

merchantWebsite
Merchant website, if available.

agreedToTerms
Did the customer check a box agreeing to terms and conditions? Required.

trialDetails
Required. See [TrialDetails](#trial-details) below.

isCardCompromised
Does the customer believe their card details have been compromised and a replacement is needed? Required.

receivedNotification
Did the customer receive a notification 7 days prior to the billing?

merchantSaid
What did the merchant say when contacted by the customer? Required.

details
Detailed explanation of what happened.

#### TrialDetails (#trial-details)

enteredTrial
Did the customer enroll in a free trial? Required.

trialDuration
How many days was the trial supposed to last? Required if `enteredTrial` is `true`.

#### Files 

cancellationConfirmation
Cancellation confirmation.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

otherDoc
Any relevant documentation the customer may have.

UNWANTED_SUBSCRIPTION
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "trialDetails": {
      "enteredTrial": "true",
      "trialDuration": 10
    },
    "noticedDate": "2021-06-05",
    "merchantWebsite": "http://merchant",
    "isCardCompromised": false,
    "agreedToTerms": true,
    "receivedNotification": false,
    "merchantSaid": "nothing",
    "details": "unwanted subscription dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```

*I was charged the wrong amount or currency*

#### Request 

transaction
[Transaction](#transaction) that is related to this dispute.

form
[Form](#form) that contain all information required to submit this dispute.
Changes according to the selected reason code.

disclaimer
[Disclaimer](#disclaimer) that keep track of acknowledgements.

files
[Files](#files) A key value pair that describe the received file of a submission.

#### Transaction 

transactionId
ID of the transaction

email
Email of the support team that Wise should reach out to

#### Disclaimer 

allAnswered
Acknowledgment that all questions have been answered. The server will reject the request if this is not true.

filesUploaded
Acknowledgment that all relevant files have been attached. The server will reject the request if this is not true.

#### Form 

charged
How much the customer was charged. See [Money](#money) below. Required.

expected
How much was the customer expecting to pay. See [Money](#money) below. Required.

goods
What did the customer buy? Required.

agreedDetails
Required. See `AgreedDetails` below.

details
Detailed explanation of what happened.

#### AgreedDetails 

agreed
Did the customer agree to paying the charged amount? Required.

agreedReason
Why did the customer agree to paying the incorrect amount? Required if `agreed` is `true`.

#### Money 

value
Amount. Required.

currency
Three-character currency code, e.g. `USD`. Required.

#### Files 

priceConfirmation
Confirmation of the correct price.

correspondence
Any correspondence between the customer and the merchant related to the dispute.

otherDoc
Any relevant documentation the customer may have.

WRONG_AMOUNT
```
{
  "transaction": {
    "transactionId": "12345",
    "email": "support@partner.com"
  },
  "form": {
    "charged": {
      "value": 50,
      "currency": "EUR"
    },
    "expected": {
      "value": 5,
      "currency": "EUR"
    },
    "agreedDetails": {
      "agreed": "true",
      "agreedReason": "some reason"
    },
    "goods": "something",
    "details": "wrong amount dispute"
  },
  "disclaimer": {
    "allAnswered": true,
    "filesUploaded": true
  }
}
```