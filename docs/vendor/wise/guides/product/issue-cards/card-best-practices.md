# Best practices

As these cards are issued by Wise, Wise's own fraud monitoring controls are running in the background 24/7, ensuring that customers' funds are safe. Throughout the lifetime of the product, you might experience situations where transactions would get declined due to our fraud controls. Here are some scenarios to keep in mind during your implementation so as to handle them promptly:

* **Customers should fund their balance before attempting to tokenise the card on their mobile wallets**
  * Wise strictly prevents zero balance tokenisations. While some merchants might send an ASI (Account Status Inquiry) for these card checks, some merchants will attempt to tokenise the card without an ASI, resulting in a failure. Ensuring that the balance is funded before tokenising the card will prevent these errors. We recommend implementing a flow to ensure that the customer funds their balance before they create their card.