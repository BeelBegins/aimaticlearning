# Refunding transfers

A refund is when money that a sender paid for a transfer is returned to them (or to the partner's balance) instead of being delivered to the recipient.

## Refund reasons

Refunds can be triggered by a few scenarios:

- **Bounce backs**: This is the most common reason for a refund. A bounce back occurs when a recipient's bank rejects the payment, often because the account number is wrong, the account is closed, or the name doesn't match the transfer request. Bounce backs automatically trigger cancellation of the transfer and a refund to the sender.
- **Transfer cancellations**: Partners can [cancel a transfer](/api-reference/transfer/transfercancel) before it's been fully processed, for example if the customer changed their mind or entered incorrect details.
- **Compliance reasons**: Certain compliance or regulatory checks can prevent transfers from being completed, resulting in a refund.


## Refund methods

The refund method Wise uses depends on your [funding/settlement model](/guides/product/send-money/funding):

| Funding/settlement model | Refund method |
|  --- | --- |
| Direct bank transfer (push) | Refund to bank account |
| Fund from balance | Refund to balance |
| Bulk settlement | Net settlement |


Refund method and funding model
In most cases, the funding/settlement model determines the refund method. However, in some cases the **refund to bank account** method can be configured for partners using the **fund from balance** model.

Select the refund method that applies to your funding model to learn more about how it works.

Refund to bank account
Wise refunds directly to sender bank account.

Refund to balance
Wise refunds the partner's multi-currency balance account.

Net settlement
Bulk refunds to partners who use bulk settlement.

## Partial refunds

A partial refund means the amount refunded is less than the amount of the original transfer. A partial refund usually occurs due to one of the following reasons:

- **Intermediary bank fees**: For payments that used the Swift network, intermediary banks may deduct fees, resulting in less than the full amount being refunded.
  - For example, you send a $1,000 transfer, but only $975 is returned due to intermediary bank fees.
- **Recipient account limitations**: If the recipient’s bank imposes a limit on the account, or the recipient can’t accept the full amount, any excess amount will be refunded.
  - For example, you send $1,000, but only $800 is accepted by the recipient’s bank, leading to a $200 refund.


Swift network intermediary bank fees are the most common cause of partial refunds. Any transfer sent via a Swift rail is potentially subject to these fees, though it also depends on the intermediary banks involved in the specific transaction. Read our help article about [Swift correspondent fees](https://wise.com/help/articles/3KEJruODkhi59TZbSxO2xn/what-are-swift-correspondent-fees-when-sending-and-receiving-money) to learn more about how this works.

Partners who support global currencies that may be affected by Swift partial refunds must have this capability enabled for their integration.

Consult with your Wise Platform Implementation team for details and testing prior to going live in production.

### Identifying partial refunds

To identify a partial refund, compare the refunded amount in the refund webhook payload to the original transfer amount. If the refunded amount is less than the original transfer amount, then it is a partial refund.

How you handle partial refunds depends on the refund method. Review the refund method guide that applies to your integration (linked above) for more details.