# Multi currency accounts

This document provides guidelines for the implementation of multi-currency accounts for all partners.

Wise Platform image
br
## What is a multi-currency account? 

A multi-currency account is a single account that lets a profile hold, send, receive, and convert money across multiple currencies. Each multi-currency account can contain one or more balances, and each balance can be issued local bank account details (e.g. a GBP sort code and account number, or a EUR IBAN and BIC) so the user can be paid like a local in that country.

This guide describes the logic to:

1. Determine a user's eligibility for multi-currency accounts.
2. Determine which balance account currencies are supported.
3. Create balance accounts for personal and business profiles.
4. Add bank account details to eligible balance accounts.
5. Top up a balance account from an external source.
6. Send money from a balance account.
7. Convert funds between two balances in different currencies.
8. View the transaction history for a balance account.


Multi Currency Accounts Postman Collection
## Multi-currency account structure 

The structure of a multi-currency account is as follows:

1. A **user** has a profile (personal or business).
2. A **profile** has the ability to open a **multi-currency account**.
3. A **multi-currency account** has the ability to have one or multiple **balance accounts** in different currencies.
4. A **balance account** has a specific currency and can contain a set of **bank account details**.
5. **Bank account details** are a set of local account details that allow the account holder, or their customer, to receive funds like a local in that country's currency (for example, an IBAN + BIC for EUR, or account number + sort code for GBP).


The diagram below illustrates the relationships between each of the components highlighted above.

Multi-Currency Accounts Structure Diagram
Bank account details
Account details for a specific currency balance account are optional and not issued by default when opening a balance. Go to the [Bank account details guide](/guides/product/accounts/bank-account-details) to learn about creating, viewing, and managing bank account details.