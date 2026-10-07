# Onboarding your customers

Creating profiles and customer verification for embedded partners

Embedded Solutions partners must create a unique profile for each end customer that uses the Wise financial services built into the partner applications.

Each profile is also subject KYC verification checks. How the KYC verification occurs depends on whether you are licensed to perform your own KYC verification or not.

- Partners that are **qualified and licensed** to perform their own KYC checks can do so when they meet certain conditions and when contractually agreed upon with Wise. With this approach, you still create unique profiles for each of your customers, but you do not need to send your customers through the Wise-performed customer onboarding flow. See the [Partner-performed customer onboarding](#partner-performed-customer-onboarding) section below for details.
- Partners **not licensed** to perform their own customer identity checks must use the Wise-performed customer onboarding flows. Wise-performed onboarding gathers your customers' personal and/or business details and performs the KYC/KYB checks your customers must pass. See the [Wise-performed customer onboarding](#wise-performed-customer-onboarding) section below for details.


## Partner-performed customer onboarding

With this approach, Wise Platform relies on you to perform customer verification according to your established process.

To allow for this, you must meet the following requirements and preconditions. If any of the preconditions change, you must notify Wise Platform in a timely manner.

- You are a regulated entity.
- You perform customer due diligence (“CDD” and “KYC”) and CDD record keeping in compliance with your verification procedure.
- You have regular internal quality assurance processes to check procedures are compliant with the AML/CTF Program and have been adhered to. This must occur annually, at minimum.
- You have an appointed AML/CTF Compliance Officer.
- You perform on-going ML/TF risk awareness training and training on CDD and record keeping for employees.
- You don’t allow customers who are onboarded through simplified due diligence or a lower KYC standard than the Wise AML/CTF Program to access Wise through your application.


You must inform us if you rely on a third-party or other financial institutions to perform customer identification or verification. When this is the case, our Compliance team must to audit both your business and that of the third-party conducting the checks.

## Wise-performed customer onboarding

Wise provides multiple methods that allow you to build a branded customer onboarding experience directly into your application.

Compare the customisation levels, integration effort, and maintenance needs to help determine which method best suits your business needs.

|  | Hosted | API | Hybrid |
|  --- | --- | --- | --- |
| **Description** | Redirect your customers into fully Wise-hosted flow | Build your own customized flow using the API | Combine API-led onboarding with hosted onboarding |
| **Customisation** | Platform logo and theme | Full control | Full control to your preferred level |
| **Customer journey** | Limited control | Full control | Full control to your preferred level |
| **Integration effort** | Minimal | High | Moderate |
| **Maintenance*** | Out of box, supported immediately | Requires updates when new compliance requirements emerge | Out of box, supported immediately |


**Maintenance in this context means supporting compliance changes and expanding to new regions*.

Select a tab for a more detailed description of each Wise-performed onboarding method.

Hosted
In the hosted onboarding method, Wise provides you with the hosted link, which you then direct your customer to at the point in the journey you decide to initiate the hosted onboarding process. The forms are branded with your company logo and theme colors. Wise manages the portal logo and theme based on files and specifications you provide to your onboarding team.

Once directed to the hosted page, your customer is guided through steps to enter the required KYC/KYB details. They may also be required to perform liveness checks or instructed to upload documents, like an image of a government-issued ID.

With hosted customer onboarding, you don't build the verification screens or collect the KYC requirements yourself, since your customers are entering their information into Wise-created and managed forms.

API
In the API method, your customers remain in your application for the onboarding process using a flow you design and control. You then send the gathered information through the Wise Platform API for verification.

With API-only onboarding, you are responsible for collecting all current and future information to verify your customer. As new compliance requirements are introduced, you are responsible for updating your integration to support them. Failure to do so can result in customers being unable to complete onboarding.

Hybrid
The hybrid method enables you to own your customer onboarding experience, while using Wise-hosted flows to handle requirements that cannot be collected via API. The hybrid method also ensures you can handle changing requirements without breaking your onboarding flow.

Wise recommends the hybrid method for most integrations as it allows you to customise your onboarding experience while ensuring you meet all compliance requirements as they evolve. Using a hosted fallback also enables you to expand to new regions more quickly, as new or region-specific requirements can be handled without requiring changes to your integration.

### Initiating the onboarding process

Before a customer can send their first transfer, they must have a [profile](/guides/product/account-setup/customer-onboarding/create-customer-profiles) and complete the customer onboarding process.

You can initiate onboarding for a customer at any moment before submitting their first transfer request by using **proactive KYC** (available for business accounts in **EU, UK, United States, Canada, Singapore, Japan, and Australia** markets). For partners outside of these regions, the KYC Review process is initiated automatically when you submit the customer's first transfer request.

### Prerequisites

Before sending your customers through the onboarding process, be sure to note the following:

- Your customer must have a [profile resource created](/guides/product/account-setup/customer-onboarding/create-customer-profiles) before you can initiate the onboarding flow for them.
- You must subscribe to the [KYC review state change webhook](/guides/product/account-setup/customer-onboarding/kyc-statechange-webhook) for status updates, as much of the workflow relies on the data these webhook event payloads provide.
- If customer onboarding is initiated when the customer attempts their first transfer (as opposed to proactive KYC), the transfer must be in a [funded state](/guides/product/send-money/funding) to ensure review by a Wise agent.
- The proactive KYC option is available for business accounts in **EU, UK, United States, Canada, Singapore, Japan, and Australia** markets only.


### Data requirements

The data requirements for any specific customer depends on factors such as their:

- Country of residence
- Customer type (personal or business)
- Action being taken (for example, creating a transfer)


Certain scenarios may cause Wise to ask for additional information after the customer onboarding process, for example if the customer address or risk level changes.

### Next steps

Select a step to view the how-to guide:

Create customer profile
Create a personal or business profile for the customer.

Subscribe to webhook
Subscribe to the KYC state change webhook to receive event notifications.

Initiate Wise-performed onboarding
Send your customer through a branded onboarding experience. Choose either a full [hosted experience](/guides/product/account-setup/customer-onboarding/hosted-kyc) or the [API & Hybrid experience](/guides/product/account-setup/customer-onboarding/api-hybrid-kyc).