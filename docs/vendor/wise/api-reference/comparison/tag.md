The comparison API can be used to request price and speed information about various money transfer providers. This includes not only Wise but other providers in the market.

Important
All requests to the Comparison API require authentication. Comparison data is provided for informational purposes and must not be used for critical flows.

Price Estimation 

The quotes (price and speed) provided by this API are based off of real quotes collected from 3rd party websites. We collect both the advertised exchange rate and fee for each provider for various amounts. When a comparison is requested, we calculate the markup percentage of the collected exchange rate on the mid-market rate at the time of collection. We then apply this markup to the current mid-market rate to provide a realistic estimate of what each provider offers. We collect data for all providers around once per hour to ensure we provide as accurate and up-to-date information as possible.

Note: Today, we only provide estimations for FX transactions with a Bank Transfer pay-in and pay-out option. This is important to stress as many providers offer significantly different fees and exchange rates when used debit/credit card, cash etc.

For more details on the data collection process please see the following page:
[https://wise.com/gb/compare/disclaimer](https://wise.com/gb/compare/disclaimer)

If you have questions or suspect any data to be inaccurate or incomplete please contact us at: [comparison@wise.com](mailto:comparison@wise.com)

Delivery Estimation 

Similar to price, we collect speed data for most (if not all) providers which we have price information for. Many providers display speed estimates to their customers in a number of different ways.

Some examples:

- "The transfer should be complete within 2-5 days"
- "The money should arrive in your account within 48 hours"
- "Should arrive by 26th Aug"
- "Could take up to 4 working days"


The below API intends to model these in a consistent format by providing a minimum and maximum range for all delivery estimations. An estimate that states "up to X" will have "max" set to a duration but "min" as null; "from X" will have "min" set to a duration and "max" as null. Finally, for those providers who offer a specific, point in time estimation (like Wise), the API will surface a duration where "min" and "max" are equal.

Quotes structure 

In order to provide the most flexible and accurate data for clients, we surface a denormalized list of quotes per provider where each quote represents a unique collection of comparison "dimensions".

A single given provider may expose multiple quotes for the same currency route. The most common example is where a provider offers different pricing for two different countries which use the same currency, e.g.:

Provider X:

- GBP EUR 1000 [GB -> ES] fee: 10, rate: 1.5
- GBP EUR 1000 [GB -> DE] fee: 8, rate: 1.5
- GBP EUR 1000 [GB -> FR] fee: 10, rate: 1.35


The same principle applies for speed, i.e. a provider may have different speed estimates for different target countries. Hence, we expose these as discrete quotes, where a quote is a unique combination of route, country, speed and price factors.

A client may choose to reduce this set of quotes down to a single or several quotes in order to display a relevant quote to a given user. An example where we take the cheapest quote for a given currency route (and also surface the target country) can be seen at the below link:

[https://wise.com/gb/compare/?sourceCurrency=GBP&targetCurrency=EUR&sendAmount=1000](https://wise.com/gb/compare/?sourceCurrency=GBP&targetCurrency=EUR&sendAmount=1000)