# Raise dispute with dynamic flow

Customers can raise disputes to recover funds from fraudulent transactions or problematic products and services.

For the dispute submission process, Wise offers Dynamic Flow, a way to easily build embeddable forms into your application.
There are 2 ways you can implement our dynamic flow for disputes:

- Customer Initiated
- Partner Customer Support Initiated


## Customer Initiated 

![Dispute Flow Customer Initiated](/assets/dispute-flow-customer.3915bb973887d5b9546ec6b6ac61828c465852c71bc63465383ceaa5945a466c.28b10c14.png)

The customer initiated flow is used when you would like to show the dynamic flow on your customer facing app.

## Partner Customer Support Initiated 

![Dispute Flow Partner Customer Support Initiated](/assets/dispute-flow-partner.ca830cd92d1da4fb1f5616d8471a0257d601faae351dcdfacc2231aa022ad7a2.28b10c14.png)

The partner customer support initiated flow is used when you would like to show the dynamic flow to your internal app used only accessible to your employees.

If you think that a card has been compromised, [block or freeze the card](/api-reference/card/cardstatusupdate).

After submission of the dispute, Wise's agents will get in contact with your support team should they need anymore information.

## Retrieve dispute reasons 

Retrieve the list of possible reasons for submitting a dispute. If a reason code has `subOptions`, those should be used for submitting disputes.

```shell curl
curl -i -X GET \
  https://api.wise.com/2026Q4/spend/profiles/14547572/dispute-form/reasons \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479'
```

Example Response
```json
[
  {
    "code": "ATM_DISPENSED_NO_FUNDS",
    "description": "I didn't receive the money from the ATM or cash machine",
    "isFraud": false,
    "supportsMultipleTransactions": false,
    "tooltip": "Choose this if the ATM did not dispense the money or gave you less than expected"
  },
  {
    "code": "UNAUTHORIZED",
    "description": "I did not make, authorize, or participate in this transaction",
    "tooltip": "Choose this if you don't know the merchant or have never purchased anything from them",
    "subOptions": [
      {
        "code": "CARD_POSSESSION",
        "description": "I don't recognise a transaction",
        "isFraud": true,
        "supportsMultipleTransactions": true,
        "tooltip": "Choose this if you had your card at the time of the transactions, or if you think your card details have been compromised"
      },
      {
        "code": "CARD_NO_POSSESSION",
        "description": "My card was lost or stolen",
        "isFraud": true,
        "supportsMultipleTransactions": true,
        "tooltip": "Choose this if you didn't have your card at the time of the transactions"
      }
    ]
  }
]
```

For request/response details, see the [API reference](/api-reference/disputes/disputereasonsget).

## Setting up the submit dispute API for Dynamic Forms

You will need to implement a POST API with the following format:
**`POST https://{{yourApiUrl}}/spend/profiles/{{profileId}}/dispute-form/flows/{{scheme}}/{{reason}}`**

This API should forward the call to
**`POST https://{{wiseUrl}}/spend/profiles/{{profileId}}/dispute-form/flows/{{scheme}}/{{reason}}`** along with the request body.
This is required as the dynamic form returned by us will automatically be configured to call your POST API.
In order to redirect the Dynamic Flow JavaScript library to your domain please use `baseUrl` or `fetcher` as part of the dynamic flows setup.

See [example backend implementation](#example)

The response to the submit call of the dynamic flow will include the `x-df-exit: true` HTTP header. This header is used by the JavaScript framework to add an option to exit the dynamic flow and redirect the user to a different page (or exit a WebView depending on the client's implementation). In order to intercept the last page on the frontend, an `onClose` function should be added to JavaScript, for example:

```js
const onClose = () => {
  console.log("DF is exiting");
  window.location.href = "https://www.example.com/";
};
```

## Retrieve the dynamic flow for disputes 

Retrieve the JSON for initiating the dispute flow. This endpoint should be used in conjunction with Wise's
[Dynamic Flow framework](https://www.npmjs.com/package/@transferwise/dynamic-flows).

The JSON data in the response must be passed into the Dynamic Flow Framework which handles the rest of the multi-step dispute submission including the generation of the subsequent pages (if needed) and the creation of the dispute, along with all the required documents.

```shell curl
curl -i -X POST \
  'https://api.wise.com/2026Q4/spend/profiles/14547572/dispute-form/flows/step/VISA/TROUBLE_WITH_GOODS_SERVICES?transactionId=6789' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "email": "support@partner.com"
  }'
```

For request/response details, see the [API reference](/api-reference/disputes/disputedynamicflowstep).

A sample implementation of the dynamic flow for Disputes can be found [here](https://codesandbox.io/s/transaction-dispute-jp4k89?file=/src/App.js).

## Submit dispute 

Submit the dispute. The request body varies depending on the dispute reason — see the [API reference](/api-reference/disputes/disputesubmit) for details on each reason's required fields.

```shell curl
curl -i -X POST \
  https://api.wise.com/2026Q4/spend/profiles/14547572/dispute-form/flows/VISA/WRONG_AMOUNT \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -H 'X-External-Correlation-Id: f47ac10b-58cc-4372-a567-0e02b2c3d479' \
  -d '{
    "transaction": {
      "transactionId": "12345",
      "email": "support@partner.com"
    },
    "form": {
      "charged": {
        "value": 50,
        "currency": "EUR"
      },
      "expected": {
        "value": 5,
        "currency": "EUR"
      },
      "agreedDetails": {
        "agreed": true,
        "agreedReason": "some reason"
      },
      "goods": "something",
      "details": "wrong amount dispute"
    },
    "disclaimer": {
      "allAnswered": true,
      "filesUploaded": true
    }
  }'
```

For request/response details, see the [API reference](/api-reference/disputes/disputesubmit).

## Example backend implementation for dynamic flow disputes (Java) 

Partner Implementation
```java
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import javax.validation.Valid;

@Slf4j
@RestController
@RequestMapping(value = "/spend/profiles/{profileId}/dispute-form", produces = MediaType.APPLICATION_JSON_VALUE)
public class MyPartnerProxy {
    private static String CAL_VERSION = "2026Q3";
    private static String TARGET_BASE_URL = String.format("https://api.wise-sandbox.com/%s", CAL_VERSION);
    private static String ACCESS_TOKEN = "Bearer 492b992e-85dd-4671-8095-b0d1d2235d07";

    private static String STEP_URL = "/spend/profiles/{profileId}/dispute-form/flows/step/{scheme}/{reason}";
    private static String SUBMIT_URL = "/spend/profiles/{profileId}/dispute-form/flows/{scheme}/{reason}";

    private WebClient webClient;

    public MyPartnerProxy() {
        this.webClient = WebClient.builder()
                .baseUrl(TARGET_BASE_URL)
                .defaultHeader("Authorization", ACCESS_TOKEN)
                .build();
    }

    @GetMapping("/flows/step/{scheme}/{reason}")
    public ResponseEntity<Object> getStep(final @Valid @PathVariable("profileId") Long profileId,
                                          final @PathVariable("scheme") String scheme,
                                          final @PathVariable("reason") String reason,
                                          final @RequestParam("transactionId") String transactionId) {
        ObjectNode data = JsonNodeFactory.instance.objectNode();
        data.put("email", "support@partner.com");

        Object stepResponse = webClient.post()
                .uri(STEP_URL, uriBuilder -> uriBuilder
                        .queryParam("transactionId", transactionId)
                        .build(profileId, scheme, reason)
                )
                .body(Mono.just(data), ObjectNode.class)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .bodyToMono(Object.class)
                .block();
        return ResponseEntity.ok(stepResponse);
    }

    @PostMapping("/flows/{scheme}/{reason}")
    public ResponseEntity<Object> submit(final @Valid @PathVariable("profileId") Long profileId,
                                         final @PathVariable("scheme") String scheme,
                                         final @PathVariable("reason") String reason,
                                         @RequestBody final Object payload) {
        Object submitResponse = webClient.post()
                .uri(SUBMIT_URL, uriBuilder -> uriBuilder
                        .build(profileId, scheme, reason)
                )
                .body(Mono.just(payload), Object.class)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .bodyToMono(Object.class)
                .block();
        return ResponseEntity.ok(submitResponse);
    }

}
```

## Customizing your Dynamic Flow 

Wise's Dynamic Flow uses Bootstrap for responsive UI, based on a 12-grid column layout. The defaults for currency selection, amount and file upload are `col-xs-12`, `col-sm-6`, and `col-xs-12` for the rest. The CSS classes used are listed below. These class selectors can be used to override existing CSS

To override the existing CSS, add a new stylesheet and place the reference to that file after a Bootstrap CSS reference (if any), so that it will override any previous style properties. Alternatively, add !important to a property/value to override ALL previous styling rules for that property. Avoid using this for all properties, as the stylesheet will be large and more difficult to debug. In this code example, modify the CSS file imports in App.js to view the different overriding style sheets.

Please note that some of the form elements also use core Bootstrap classes, so be careful when you modify the styles.

An interactive demo can be found [here](https://codesandbox.io/s/transaction-dispute-css-example-1poqmi?file=/overriding.md).

#### Input labels 

| **class** | **description** |
|  --- | --- |
| `.control-label.d-inline` | All input labels |
| `.d-inline` | Text, selection and file upload input labels |
| `.d-inline-block` | Text input labels |
| `.np-checkbox__text` | Checkbox text |


#### Input 

| **class** | **elements** |
|  --- | --- |
| `.form-group` | Form input and labels |
| `.form-control` | Text input |
| `.d-inline-flex` | Text in dropdown selection |
| `.form-control-placeholder` | Dropdown selection placeholder text |
| `.tw-form-control` | `textarea` input |
| `.droppable`, `.tw-droppable-md` or `.droppable-md` | File upload |
| `.droppable-default-card` or `.droppable-card-content` | Content for file upload |
| `.droppable-complete-card` | Completed file upload |
| `.m-b-3` | Text in file upload block |


#### Button 

| **class** | **elements** |
|  --- | --- |
| `.btn.np-dropdown-toggle` | Dropdown selection |
| `.sr-only` | Radio buttons |
| `.promoted-selection` | To select names |
| `.tw-radio-button.checked .tw-radio-check` | For checked buttons |
| `.tw-radio-check` | All radio buttons |
| `.np-radio__text` | Text for radio buttons |
| `.btn.btn-primary.btn-sm` | File upload buttons |
| `.btn.btn-sm.btn-accent` | Cancel button during file upload |
| `.np-checkbox`, `.checkbox` | Checkbox button |
| `.btn.btn-md.np-btn-block.btn-priority-2` | "Continue" button |


#### Icon 

| **class** | **elements** |
|  --- | --- |
| `.chevron-color`, or `tw-icon-chevron-up` | Arrow icon for dropdown selection |
| `.circle`, `.circle-sm` , `.circle-inverse` or ` .tw-icon-upload` | File upload icon |
| `.tw-icon-info-circle` | Information icon for alert |
| `.np-checkbox-button` | Checkbox selection icon |


#### Alert 

| **class** | **elements** |
|  --- | --- |
| `.alert-detach.alert-danger` | Alert for form validation |
| `.d-flex.alert-neutral` | "You may be responsible for dispute administration fees" alert |


#### Others 

| **class** | **elements** |
|  --- | --- |
| `.text-xs-center.m-b-3` | "I was charged the wrong amount or currency" |
| `.np-drawer-header--title` | "Search ..." title in currency selection |
| `.np-select-filter` | Search bar in currency selection |
| `legend` | "Please upload" above file upload |
| `.np-popover__content` or `.np-bottom-sheet--content` | Popover content upon clicking information icon beside "Confirmation of the correct price" |