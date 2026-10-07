# Provide a customer portal to your customers

Allow your customers to manage their own accounts and subscriptions.

Give your customers the ability to manage their account by setting up a customer portal. Configure the portal in the Dashboard, or use the API to implement advanced features, such as setting up unique configurations for different customers or for *connected accounts* (A person or business accepting payments or receiving payouts on a Connect platform).

Automate many of your customer interactions by combining a customer portal with customer communications controlled by [Stripe Billing automations](https://docs.stripe.com/billing/automations.md). Building custom, automated workflows can help streamline your business processes, enhance customer communication, and improve revenue recovery efforts.

[Explore demo](https://billing.stripe.com/customer-portal-demo)

## Create a customer portal

Create a customer portal to enable your customers to manage their account such as updating their billing information, payment methods, and subscription status.
[Get started](https://docs.stripe.com/customer-management/activate-no-code-customer-portal.md)
## Get started

[Activate the customer portal](https://docs.stripe.com/customer-management/activate-no-code-customer-portal.md): Use the Dashboard to activate the customer portal and optionally customize branding and prefill customer email addresses.

[Configure the customer portal](https://docs.stripe.com/customer-management/configure-portal.md): Configure settings for the customer portal in the Dashboard.

[Integrate the customer portal](https://docs.stripe.com/customer-management/integrate-customer-portal.md): Customize and integrate a customer portal into your application using the Stripe API.

[Create deep links to the customer portal](https://docs.stripe.com/customer-management/portal-deep-links.md): Set up custom links to specific actions by coding customer portal flows.

[Add a cancellation page](https://docs.stripe.com/customer-management/cancellation-page.md): Allow your customers to cancel their subscriptions in the customer portal. You can optionally collect cancellation reasons and offer coupons to discourage cancellation.

## Features 

A customer portal allows your customers to manage their payment details, invoices, and subscriptions in one place.

| Feature | Description |
| --- | --- |
| Customer management | Offer your customers the ability to:

- Update billing information, including their tax IDs
- Update payment methods
- Update subscriptions
- Cancel subscriptions immediately or at the end of the current billing period
- Pay, download, and view current and past invoices |
| Cancellation deflection | Reduce churn by offering your customers a coupon when they try to cancel their subscription. Customers who cancel anyway can share why. You can collect those reasons through [webhooks](https://docs.stripe.com/webhooks.md) or [Stripe Sigma](https://docs.stripe.com/data/sigma.md). |
| Interoperability | Use the portal with other Stripe products:

- [Checkout](https://docs.stripe.com/payments/checkout.md) and the [embeddable pricing table](https://docs.stripe.com/payments/checkout/pricing-table.md)
- [Payment Links](https://docs.stripe.com/payment-links.md)
- [Managed Payments](https://docs.stripe.com/payments/managed-payments.md)
- [Connect](https://docs.stripe.com/connect.md)
- [Invoices](https://docs.stripe.com/invoicing.md)
- [Billing](https://docs.stripe.com/billing.md)
- [Stripe Tax](https://docs.stripe.com/tax.md) |
| Localization support | Automatically localize the portal based on your customers’ preferred language. To view a localized version of the portal, set your browser’s default language to the language you want to preview. See the full list of [supported languages](https://docs.stripe.com/customer-management.md#language-support). |
| Customized branding | Configure the portal to [match your branding](https://docs.stripe.com/customer-management/configure-portal.md#branding), including your icon, logo, colors, and business information. |
| Payment methods | Manage payment methods to make it convenient for your customers to pay you. See the full list of [supported payment methods](https://docs.stripe.com/customer-management.md#supported-payment-methods). Read the  [payment methods](https://docs.stripe.com/payments/payment-methods/integration-options.md) guide to learn more. |
| Invoice-only support | You can use the customer portal for standalone invoices. See [Preview invoicing management](https://docs.stripe.com/customer-management/configure-portal.md#preview-invoicing-management) for details. |
| Stripe Connect compatibility | The customer portal works with Stripe Connect. If you’re using the customer portal with Stripe Connect, configure the customer portal for the platform instead of a connected account. |
| Ephemeral sessions | Portal sessions are temporary. New portal sessions expire after a 5 minute period. If a customer uses it within that time period, the session expires within 1 hour of the most recent activity. |

## Limitations 

The customer portal has the following limitations:

### Limitations to modifying subscriptions

- If a subscription uses any of the following, the customer can cancel it in the portal, but can’t update it:
  - [Multiple products](https://docs.stripe.com/billing/subscriptions/quantities.md#multiple-product-sub).
  - [Usage-based billing](https://docs.stripe.com/products-prices/pricing-models.md#usage-based-pricing).
  - [Trial offers](https://docs.stripe.com/billing/subscriptions/trials.md).
  - Sending invoices for collection. Read more about the `collection_method` [parameter](https://docs.stripe.com/api/subscriptions/object.md#subscription_object-collection_method). If you use the [Dashboard](https://dashboard.stripe.com/subscriptions) to create the subscription, you make this selection in the **Payment method** section.
  - Unsupported payment methods.
- Customers can’t update or cancel subscriptions that currently have an update scheduled with a [subscription schedule](https://docs.stripe.com/billing/subscriptions/subscription-schedules.md).
- Tax behavior requirements for customer portal subscription changes depend on when the change takes effect: the portal uses the Subscriptions API for changes that take effect immediately, and Subscription Schedules for changes that take effect at the end of the billing period. See [tax behavior](https://docs.stripe.com/tax/products-prices-tax-codes-tax-behavior.md), [updating subscriptions](https://docs.stripe.com/api/subscriptions/update.md), and [updating subscription schedules](https://docs.stripe.com/api/subscription_schedules/update.md).
- By default, customer modifications to a `trialing` subscription end the free trial and create an invoice for immediate payment. To keep the trial active, when you configure the customer portal, set [features.subscription_update.trial_update_behavior](https://docs.stripe.com/api/customer_portal/configurations/create.md#create_portal_configuration-features-subscription_update-trial_update_behavior) to `continue_trial`.
- When you [allow customers to switch plans](https://docs.stripe.com/customer-management/configure-portal.md#configure-subscription-management), you can specify a maximum of 10 products for them to choose from.

### Technical limitations

- If the session allows for payment method management, the portal displays the payment method section, even if the portal doesn’t support the customer’s default payment method. See the list of [supported payment methods](https://docs.stripe.com/customer-management.md#supported-payment-methods).
- You can’t define multiple [Prices](https://docs.stripe.com/api/prices.md) with the same `product` and `recurring.interval` values. For example, to offer a magazine for a regular price of 4 USD per month and a student price of 3 USD per month, create a separate student magazine [Product](https://docs.stripe.com/api/products.md) version.
- You can’t display the customer portal inside an iframe.

## Supported payment methods 

| [Payment method](https://docs.stripe.com/api/payment_methods/object.md#payment_method_object-type) | Description | Presentment currencies | Business locations | Limitations |
| --- | --- | --- | --- | --- |
| ACH Direct Debit (`us_bank_account`) | Stripe users can receive bank transfers directly from customers. | USD | Most locations | Customers can’t manually enter a new bank account in the portal. |
| Affirm (`affirm`) | Affirm is a buy now, pay later payment method that allows customers to split purchases into installments. | CAD, USD | CA, US | None |
| Afterpay / Clearpay (`afterpay_clearpay`) | Afterpay (Clearpay in the UK) is a buy now, pay later payment method that allows customers to split purchases into installments. | AUD, CAD, NZD, GBP, USD | AU, CA, NZ, UK, US | None |
| Alipay (`alipay`) | Alipay is a digital wallet payment method popular with customers in China. | AUD, CAD, CNY, EUR, GBP, HKD, JPY, MYR, NZD, SGD, USD | Most locations | None |
| Amazon Pay (`amazon_pay`) | Amazon Pay is a wallet payment method that lets your customers check out the same way as on Amazon.com. | AUD, CHF, DKK, EUR, GBP, HKD, JPY, NOK, NZD, SEK, USD, ZAR | US and Europe | None |
| AU BECS Debit (`au_becs_debit`) | Bulk Electronic Clearing System (BECS) Direct Debit payments from customers with an Australian bank account. | AUD | AU | None |
| BLIK (`blik`) | [BLIK](https://docs.stripe.com/payments/blik/recurring-payments.md) is an authenticated bank debit payment method in Poland where customers authorize payments with a code from their banking app. | PLN | PL | None |
| Boleto (`boleto`) | Boleto is a popular payment method in Brazil where customers pay by using a Boleto voucher with a generated number. | BRL | BR | You must have a Brazilian Stripe account to accept Boleto from your customers. |
| Cards (`card`) | Cards, including Apple Pay and Google Pay, are one of the most popular ways to pay online, with broad global reach. There are different types of cards and several steps in the process. | Most currencies | Most locations | None |
| Cash App Pay (`cashapp`) | Cash App is a popular consumer app in the US that allows customers to bank, invest, send, and receive money using their digital wallet. | USD | US | You can’t use Cash App Pay if your account is in US territories. |
| Crypto (`crypto`) | Crypto allows customers to pay with stablecoins and other supported cryptocurrencies. | USDC, USDG, USDP | US | None |
| Custom payment methods (`custom`) | Custom payment methods allow you to extend your payment and billing integrations with payment methods processed outside of Stripe. | Most currencies | Most locations | None |
| GoPay (`gopay`)
(Private preview) | GoPay is a popular digital wallet payment method in Indonesia.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | IDR | ID | None |
| Kakao Pay (`kakao_pay`) | Kakao Pay is a popular digital wallet payment method in South Korea. | KRW | Most locations | None |
| Klarna (`klarna`) | Klarna is a buy now, pay later payment method that allows customers to pay in installments or defer payment. | AUD, CAD, CHF, CZK, DKK, EUR, GBP, NOK, NZD, PLN, RON, SEK, USD | Most locations | None |
| Korean cards (`kr_card`) | Korean cards allow customers to pay with domestic Korean cards. | KRW | Most locations | None |
| Korea Market (`kr_market`)
(Private preview) | Korea Market allows customers to pay through domestic Korean payment methods.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | KRW | Most locations | None |
| Link (`link`) | Link saves and autofills payment and shipping information for your customers so they don’t need to enter payment details manually. | Most currencies | Most locations | None |
| Naira Bank Transfer (`ng_bank_transfer`) (Private preview) | Naira Bank Transfer allows customers to pay via bank transfer in Nigeria.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | NGN | US | None |
| Naira card (`ng_card`)
(Private preview) | Naira card allows customers to pay with domestic Nigerian cards.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | NGN | US | None |
| Naira Wallet (`ng_wallet`)
(Private preview) | Naira Wallet allows customers to pay using Nigerian digital wallets.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | NGN | US | None |
| Naver Pay (`naver_pay`) | Naver Pay is a popular digital wallet payment method in South Korea. | KRW | Most locations | None |
| Nigeria Market (`ng_market`)
(Private preview) | Nigeria Market allows customers to pay through domestic Nigerian payment methods.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | NGN | US | None |
| NZ BECS Debit (`nz_bank_account`) | Bulk Electronic Clearing System (BECS) Direct Debit payments from customers with a New Zealand bank account. | NZD | NZ | None |
| Pay by Bank (`pay_by_bank`) | Pay by Bank allows customers to make payments directly from their bank account. | EUR, GBP | DE, FI, FR, IE, UK | None |
| PayPal (`paypal`) | PayPal is a payment method that enables customers in any country to pay using their PayPal account. | AUD, CAD, CHF, CZK, DKK, EUR, GBP, HKD, NOK, NZD, PLN, SEK, SGD, USD | Europe, UK | [Requires approval](https://docs.stripe.com/payments/paypal/set-up-future-payments.md#enable-recurring-payments) |
| PayTo (`payto`) | PayTo is a real-time payment method in Australia for accepting one-time and recurring payments. | AUD | AU | Customers can’t add a new PayTo payment method in the portal. |
| Pix (`pix`) | Pix is a real-time payment method in Brazil regulated by the Central Bank of Brazil. | BRL | Most locations | None |
| Pre-authorized debits (`acss_debit`) | PADs are a low-cost, high volume batch processing network for financial transactions in Canada. | CAD, USD | CA, US | None |
| Revolut Pay (`revolut_pay`) | Revolut Pay is a digital wallet payment method that allows Revolut users to pay directly from their Revolut account. | DKK, EUR, GBP, HUF, PLN, RON | Europe, UK | None |
| Satispay (`satispay`) | Satispay is a digital wallet payment method popular in Italy. | EUR | Europe | None |
| SEPA Direct Debit (`sepa_debit`) | The Single Euro Payments Area (SEPA) is an initiative of the European Union to simplify payments within and across member countries. | EUR | Most locations | None |
| TrueMoney (`truemoney`)
(Private preview) | TrueMoney is a popular digital wallet payment method in Thailand.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | THB | US, TH | None |
| TWINT (`twint`) | TWINT is a popular mobile payment method in Switzerland. | CHF | Europe, UK | None |
| UK BACS Debit (`bacs_debit`) | Bacs Direct Debit is a reusable, delayed notification payment method available to bank account holders from the United Kingdom. | GBP | UK | Your Stripe account must be in a [supported business location](https://docs.stripe.com/payments/bacs-debit.md#bacs_debit-business-locations) to accept Bacs Direct Debit payments from customers with a UK bank account. |
| UPI (`upi`) | UPI is a real-time payment system developed by the National Payments Corporation of India. | INR | US | None |
| WeChat Pay (`wechat_pay`)
(Private preview) | WeChat Pay is a digital wallet payment method popular with customers in China.

Contact [Stripe Support](https://support.stripe.com/) for more information about this private preview. | AUD, CAD, CHF, CNY, DKK, EUR, GBP, HKD, JPY, NOK, SEK, SGD, USD | Most locations | None |

## Language support

The customer portal supports the following languages:

- Bulgarian (bg)
- Chinese Simplified (zh)
- Chinese Traditional—Hong Kong (zh-Hant-HK)
- Chinese Traditional—Taiwan (zh-Hant-TW)
- Croatian (hr)
- Czech (cs)
- Danish (da)
- Dutch (nl)
- English, US (en)
- English, UK (en-GB)
- Estonian (et)
- Filipino (fil)
- Finnish (fi)
- French, France (fr)
- French, Canada (fr-CA)
- German (de)
- Greek (el)
- Hungarian (hu)
- Indonesian (id)
- Italian (it)
- Japanese (ja)
- Korean (ko)
- Latvian (lv)
- Lithuanian (lt)
- Malay (ms)
- Maltese (mt)
- Norwegian Bokmål (nb-NO)
- Polish (pl)
- Portuguese, Portugal (pt)
- Portuguese, Brazil (pt-BR)
- Romanian (ro)
- Russian (ru)
- Slovak (sk)
- Slovenian (sl)
- Spanish, Spain (es)
- Spanish, Latin America (es-419)
- Swedish (sv)
- Thai (th)
- Turkish (tr)
- Vietnamese (vi)
