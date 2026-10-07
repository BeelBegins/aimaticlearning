# Correlation ID

Trace your API requests with a client-generated correlation ID.

The Wise API supports an optional correlation ID header for basic client-side tracing.

- **If provided:** It will echo back the correlation ID in the response header
- **If not provided:** No correlation ID returned in the header response


Important:
This is a simple echo. Wise does not log or store this value, all tracking must be done on your side. Do not share PII data.

## Specification

| Attribute | Value |
|  --- | --- |
| Header Name | `X-External-Correlation-Id` |
| Format | String (UUID recommended) |
| Example | `550e8400-e29b-41d4-a716-446655440000` |
| Max Length | 36 characters *If exceeded, the header will be ignored.* |
| Required | No |


## Example Request

```http
GET /v1/transfers/123 HTTP/1.1
Host: api.wise.com
Authorization: Bearer <token>
X-External-Correlation-Id: 550e8400-e29b-41d4-a716-446655440000
```