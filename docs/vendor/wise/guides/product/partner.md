# Wise Platform partner support

As a Wise Platform partner, you have access to a global technical support team 24/7 for any technical issues you may experience with the Wise Platform API once your integration is live.

Our Enterprise support team also provides operational assistance for partners managing transactions for their customers.

Wise business accounts using personal API tokens
If you access the Wise API using a [personal API token](/guides/developer/auth-and-security/personal-api-token), please see the [Support for business accounts guide](/guides/product/partner/business-account-support) to learn about your support options.

## API status page

Wise reports all incidents and maintenance notifications to our public status page, [status.wise.com](https://status.wise.com/). Always check the status page first when any issues arise with your integration.

You can subscribe to the page via email, Slack, or webhook. You can also integrate with the [Wise status page via API](https://status.wise.com/api).

## Enterprise support

Partner accounts are issued a partner-specific email address to contact the Wise Enterprise support team for assistance managing [customer operations issues](/guides/product/partner/operations). Examples of customer operations issues include rejected payment inquiries, payment recall requests, and [payment status](/guides/product/partner/operations#payment-status-or-money-hasnt-reached-recipient) or [proof of payout](/guides/product/partner/operations#receipt-or-proof-of-payout) requests.

Responses are sent to the sender email, but we can also designate a CC email for all cases and updates, which you arrange as part of your contracted SLA.

As all responses are delivered via email, we cannot guarantee the structure or how various email clients will represent the emails. If you plan to automate or otherwise rely on the structure of the support responses, we recommend you use our case handling service instead.

## Case handling

Wise may need more information before a transfer or account-related process can continue. You may also have questions for us. Use the [cases service](/guides/product/partner/case-handling) to resolve cases faster, reduce delays for you and your customer, and improve customer experience.

Cases can be created automatically by us, manually by our support team, or by you through the Wise Platform API.

## Technical support

For technical questions about the Wise Platform API, send an email to [api@wise.com](mailto:api@wise.com).

To help our support team resolve your issue efficiently, include in your request:

- API endpoint(s) affected
- Business impact of errors
- `x-trace-id` examples of failing requests
- The environment (production or sandbox)
- API request and response body
- Timestamps and duration of issues
- User or profile IDs, if applicable


The team adheres to the response and resolution times set out in your commercial agreements with Wise Platform. However, we make every effort to handle all incoming cases as soon as we can, according to the severity of your issue.

## Emergency support

For urgent requests that occur outside of normal working hours, Wise provides an emergency phone support option to partner accounts. The emergency phone number is provided by your CSM and is monitored 24/7 by our team.

Examples of high-severity issues include:

- Complete payment processing outages affecting all users.
- Critical system failures preventing any form of integration functionality.
- Major security incidents needing urgent resolution.


If you think you need to escalate a critical issue by phone, please check the [Wise status page](https://status.wise.com) first. If an incident has been reported there, the on-call team will be unable to provide you with more detailed updates.

Non-critical support requests made to the emergency channels may be redirected to our standard support channels, which can result in delays and affect our ability to respond to the most severe incidents. Frequent misuse may result in restrictions to these enhanced escalation methods.

**When you call the emergency number**:

- You’ll hear an automated greeting informing you that you’ve reached Wise Platform on-call.
- You’ll then be connected directly to an engineer on the team.
- If you’re not successfully connected to an engineer, we’ll try to connect you to one of the other engineers on the team. This could happen in the unlikely event of a major outage across the API, causing many partners to attempt to contact the team at the same time.
- If no engineers are currently available, you’ll be prompted to leave a voicemail. When you leave a voicemail, provide an email address or phone number so the team knows how to follow up with you.


**When you reach an engineer, they will**:

- Capture basic information about your integration and the issue.
- Ensure an incident is raised internally and mobilise the appropriate teams.
- Follow up with you to coordinate further steps over email.
- Ask you to email [api@wise.com](mailto:api@wise.com) with more information (for example, trace ids) so we can work with you to resolve the issue. Note: The purpose of the phone number is to alert us to critical issues. We won’t keep you on the line while we troubleshoot (though we will set up a Zoom call over email if needed).


Please only use the phone number to report the first instance if an issue. We’ll provide updates via email and via the Wise Public Status page. The team cannot provide updates over phone for ongoing incidents.

## Support for Open Banking APIs

For support with our Open Banking APIs, see our [Open Banking guide](/guides/developer/open-banking).