# Partner pooled funding

Partner pooled funding allows partners to hold liquidity in their Enterprise Account and transfer funds to the Business Account only when a card transaction occurs. The main benefit is the ability for partners to manage and control liquidity centrally in a single Enterprise Account, eliminating the need to pre-fund individual Business Accounts.

Partner pooled funding model
In a Partner pooled funding setup, the following resources are created:

- An Enterprise Account with one or more pre-funded balances.
- Business Accounts linked to the Enterprise Account. Each Business Account automatically creates empty balances to mirror currencies supported by the Enterprise Account.
- Cards linked to a Business Account.


When a card transaction is initiated, Partner pooled funding determines the required fund movements from the Enterprise Account to the Business Account to ensure the transaction can be authorized and fulfilled.

#### Capabilities

Partner pooled funding is built on top of existing Wise capabilities, allowing partners to support more currencies while benefiting from automated and most cost-effective exchange rates.

- **Multi-Currency Account (MCA)**
The Enterprise Account is created and managed directly by partners on the Wise business user interface. Like any other Wise Account, it includes a Wise Multi-Currency Account (MCA), enabling partners to open and hold balances in any supported currency within their region.
- **Smart Conversion**
The Multi-Currency Account also supports Smart Conversion. When the transaction currency has insufficient funds or the currency is not supported, Smart Conversion automatically funds the card transaction from the most cost-effective available balance. This enables partners to support a wider range of spending currencies without needing to pre-fund every currency balance.


## Wise Terminology

- [Enterprise Account](/guides#enterprise-partners): Partner main account
- [Business Account](/guides#embedded-partners): Customer account
- [Multi-Currency Account](/guides/product/accounts): Wise product that lets customers and businesses hold and manage multiple currency balances within a single account.
- **Smart Conversion**: Wise feature that automatically selects the balance with the lowest conversion fee to fund a card transaction when the transaction currency has insufficient funds.
- **Card Authorisation**: Real-time process in which the card issuer approves or declines a payment request based on a list of application checks (sufficient funds, fraud).
- **Card Capture**: Process of confirming a previously authorised card transaction so that the reserved funds can be collected and settled.


## User Flow

This is a high level diagram to illustrate the current setup for Partner pooled funding.

#### Same-currency transaction

Partner pooled funding same currency flow
1. A cardholder from business A is spending 20 SGD with their card.
2. Wise looks up the corresponding SGD balance on the Enterprise Account and verifies that there are sufficient funds available.
3. A reservation of 20 SGD is placed on the business profile's SGD balance.
4. The card transaction is authorised and the payment will go through.


#### Transactions in other currencies

If the transaction currency is not supported (i.e. no balance has been opened), or if the Enterprise Account does not have sufficient funds in the transaction currency, Wise will apply Smart Conversion to identify the currency with the lowest conversion fee. Funds will then be reserved and debited from that balance to settle the card transaction.

## Balance management

#### Top-up Enterprise Account balances

Partners can open balances in any currencies they choose to support. These balances are opened on the partner's Wise account via Wise web platform.

Partners should maintain sufficient funds based on the expected transaction volumes. To fund balances, please refer to [this guide](/guides/product/send-money/funding) that lists the available pay-in methods.

#### Balance operations

Partners can view balances in any currencies through their Wise business user interface. We also provide endpoints such as [list balances](/api-reference/balance/balancelist) in case partners want to build their own dashboard and tooling. Partners will also be provided alerts on low balances in currencies which can be used to trigger operational processes for topping up balances.

Partners can also use the user interface or APIs to make [balance to balance transfers](/guides/product/accounts/convert-from-balance-to-balance) to convert the balance from one currency to another. In order to withdraw a balance to an external account, please refer to this guide on our [send money product](/guides/product/send-money/use-cases/enterprise/send-money). Fees associated with conversion at time of withdrawal can be transparently viewed by the partner.

## Tracking spend by businesses

Partners can use the [balance statement endpoint](/api-reference/balance-statement) to generate statements, track business spend by currency for any time period, and invoice their business customers.

## Accounts Setup

#### Enterprise Account Setup

To set up your Enterprise Account:

1. Create an account on the Wise website to serve as your Enterprise Account and complete the required onboarding steps.
2. Contact the Wise implementation team, who will internally register your Enterprise Account.
3. Open currencies on your Enterprise Account that you want to hold funds in. Funds held in these currencies can then be used for transactions on the cards of individual Business Accounts.


#### Business Account Setup

Next, you can proceed to set up the business profiles for your business end customers over API. After creating a Business Account, you must link it to your Enterprise Account before any cards can be ordered. To set up individual business profiles:

1. [Create a Business Profile](/guides/product/kyc/partner-kyc/profile-creation#create-a-business-profile).
2. Link the Business Profile to your Enterprise Account. This is required so that all cards ordered under the Business Profile are configured to pull funds from the Enterprise Account for card transactions. This step must be completed before any cards are ordered under the Business Profile.


Wise validates that Partner pooled funding is enabled on your partner configuration and that your partner credentials are authorised to use the specified Enterprise Account. Once validated, Wise will also automatically open currency balances on the Business Account to mirror the currencies open on the Enterprise Account.

Once the association has been created, all cards subsequently ordered under the Business Profile are automatically configured to be Partner pooled funded from the associated Enterprise Account. The Enterprise Account associated with the card is used at authorisation and capture to perform Partner pooled funding.