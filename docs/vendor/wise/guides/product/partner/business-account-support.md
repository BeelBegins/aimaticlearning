# Support for business accounts

Wise business accounts that access the Wise API using a personal API token can contact the Wise support team for technical support issues and questions.

Send an email to [api@wise.com](mailto:api@wise.com). Our support team handles tickets in the order they are received and by severity of the issue. Our team aims to respond to all business account requests within 60 minutes.

To help our support team resolve your issue efficiently, please include as much of the following information in your request as possible:

- API endpoint(s) affected.
- Business impact of errors.
- `x-trace-id` examples of failing requests.
- The environment: production or sandbox.
- API request and response body.
- Timestamps, and duration of issues.
- User or profile IDs if applicable.


## API status page

Wise reports all incidents and maintenance notifications to our public status page, [status.wise.com](https://status.wise.com/), so be sure to check the API status before submitting a support ticket.

You can subscribe to the page via email, Slack, or webhook. You can also integrate with the [Wise status page via API](https://status.wise.com/api).

## Frequently asked questions

Before submitting your support ticket, review the following FAQs as they may provide an answer to your question.

### How do I get a client ID and client secret?

Wise provides client IDs and client secrets for [Wise Platform](https://platform.wise.com/) partner integrations only.

For business accounts accessing the API using a [personal API token](/guides/developer/auth-and-security/personal-api-token), **no client ID or secret is required or provided**.

### How can I start testing the API?

Create a new account in the [Wise sandbox](https://wise-sandbox.com/) to get started testing the API (your existing Wise account won't work for the sandbox). Note that logging in or registering with your Facebook or Google account is not supported.

### Does it cost anything to use the Wise API?

For business accounts accessing the Wise API with a personal token, there are no additional charges to use the available API features. For these accounts, Wise applies the [regular pricing system for customers](https://wise.com/gb/pricing/).

### What currencies can I send to and from?

See our [What currencies can I send to help article](https://wise.com/help/articles/2571907/what-currencies-can-i-send-to-and-from?origin=search-currencies) for more info on which currencies you can send to and from.

See our [Which currencies can I receive and keep help article](https://wise.com/help/articles/2897238/which-currencies-can-i-add-keep-and-receive-in-my-wise-account?origin=related-article-2897226) to learn about which currencies you can add, keep, and receive into your Wise account.

### Can I use Wise API to receive money in my online checkout?

We don't offer the option to build Wise into your checkout flow as a payment option to receive money, as the main use for the Wise API is to automate payouts.

The good news is that you can use the local bank details that come with your Wise account (USD, EUR, GBP, AUD, NZD and PLN) and reconcile the incoming payments via the API.

### How do I create a payment link on the API?

Unfortunately this isn't a feature that is supported by our public API. Please continue to create these links using the Wise.com interface.

### I have a question about my Wise.com account. Can you help?

For questions about your Wise.com account, go to the [Wise Help Centre](https://wise.com/help). The help centre provides multiple help articles to answer your questions as well as a contact form to get your question to the right team.