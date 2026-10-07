Cases enable you to open, retrieve, and respond to support and operations queries through direct API.

The Cases API allows you to integrate your back-end tooling, enabling:

- Faster responses through automated workflows
- Structured data via typed messages and submissions
- Operational efficiencies with programmatic case management


**Case statuses**

- cases can move through different statuses.


| Status | Description | Partner Action |
|  --- | --- | --- |
| `CREATING` | Case being created | Wait |
| `IN_REVIEW` | Case being actioned | No action needed |
| `WAITING_CUSTOMER_INPUT` | Information required | Respond |
| `RESOLVED` | Case solved and closed | None |
| `FAILED` | Case creation failed | Contact support |


**Message types**

- Messages are typed and structured:


Request messages:

- `DEPOSIT_SANCTION_HIT_REQUEST`
- `RECIPIENT_SANCTION_HIT_REQUEST`
- `REFERENCE_SANCTION_HIT_REQUEST`
- `RECIPIENT_LOCATION_HIT_REQUEST`
- `REFERENCE_LOCATION_HIT_REQUEST`
- `FREEFORM` - Free text communication


Submission messages (from partner):

- `*_SUBMISSION` - Structured response to requests
- `FREEFORM` - Free text communication