# Initiate a return

You can initiate returns over API for received payments.
The flow looks like this:

To implement returns:

1. Initiate a return via the [Returns endpoint](/api-reference/2026q3/bank-account-details/bankaccountdetailsreturnscreate)
2. Monitor the return status via [webhook event notifications](/guides/product/receive-money/initiate-a-return#monitor-the-return-status)
3. Check reconciliation of the return using [Balance Statement API](/api-reference/balance-statement/balancestatementget)


## Initiate a return

Once you identify the payment you wish to return, a payment return can be initiated by calling the [Returns endpoint](/api-reference/2026q3/bank-account-details/bankaccountdetailsreturnscreate) and providing the transfer ID of the payment you wish to return.

Ensure that you have sufficient funds in your balance to cover the return. The balance will be debited asynchronously so the API may return success even in cases of insufficient funds.

Webhook event notifications can be used to confirm the return was successfully initiated (as described in the next section).

## Monitor the return status

We do not require partners to monitor the return status. Returns are usually processed instantly and in the unlikely event of a failure, our operations team will reach out to the partner to resolve the issue.

There are no actions required from the partner once a payment return is initiated, hence we do not consider it necessary to monitor the return status.

However, if you wish to monitor the return status, you can subscribe to the following webhook event notification depending on how the payment was received.

### Monitor returns of payments received into account details

For returns of payments received into your customer's Wise-issued account details (including returns of Swift payments to their account details), you are notified through the same [Account details payment state change](/api-reference/webhook-event/eventaccountdetailspaymentstatechange) event subscription.

Return progress is reflected in the payment status as follows:

* `COMPLETED`: The status of a settled payment. This also indicates that the return has not been initiated yet.
* `CANCELLED`: Once the funds have been debited from the balance, the payment is set to this state. Wise then starts processing the return.
* `REFUNDED`: The return has been successfully processed and the payment is en route to the originator.


### Monitor Swift return payments received into connected BIC

To monitor returns of Swift payments received into your connected BIC, subscribe to the [Transfer State Change webhook](/api-reference/webhook-event/eventtransfersstatechange).

The transfer here will be the original inbound transfer. Transfer lifecycle extends beyond settlement, hence we use the same resource for the return.

A transfer has many states, but only the following are relevant for returns:

- `outgoing_payment_sent`: The status of a settled transfer. This also indicates that the return has not been initiated yet.
- `bounced_back`: Once the funds have been debited from the balance, the transfer will be set to this state. Wise will then start processing the return.
- `refunded`: The return has been successfully processed and the payment is en route to the originator. Since the return is also sent over Swift, it may take a while to reach.


## Reconcile the return

Once the return has been processed, you can reconcile the return by checking the [Balance Statement endpoint](/api-reference/balance-statement/balancestatementget).

Using the transfer ID of the original inbound payment, you can find the return in the balance statement and it should be reflected as a debit.