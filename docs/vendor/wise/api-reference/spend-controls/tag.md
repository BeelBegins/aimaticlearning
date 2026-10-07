Control which card transactions are permitted by creating rules based on merchant category code (MCC) or transaction currency.

An authorisation rule dictates whether transactions should be declined or approved based on a pre-determined set of rules. A transaction can only pass if it satisfies all the applied rules.

Creating a rule has no practical implication until it is [applied](/api-reference/spend-controls/spendcontrolsruleapply). Applying a rule results in the authorisation rule being evaluated against every incoming card authorisation request.

Rules are scoped at the application level. Use a [client credentials token](/api-reference/oauth-token/oauthtokencreate) to call these endpoints.