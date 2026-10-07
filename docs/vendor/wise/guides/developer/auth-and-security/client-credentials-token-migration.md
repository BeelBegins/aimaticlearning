# Client credentials token format migration

Learn about the Wise migration from UUID tokens to JWT tokens.

API integrations receive an `access_token` when using the Client Credentials OAuth flow. Wise is migrating these access tokens from opaque UUID tokens to JWT tokens (encrypted JWT/JWE).

This guide explains what's changing, who is impacted and what you need to do to remain compatible.

## Timelines

- Transition period from **mid June 2026** (Sandbox): JWT token formats will be returned
- Transition period from **end July 2026** (Production): UUID and JWT token formats may both be returned
- Deadline to migrate:
  - Sandbox: **31 July 2026**
  - Production: **7 January 2027**


After the deadline: only JWT tokens will be issued, and UUID tokens will no longer be supported.

## What's changing

Only the format of the `access_token` value is changing. The way you use it does not change and you can continue sending tokens as `Authorization: Bearer <access_token>`.

### Old format: UUID (opaque)

Example Response with UUID token (200 - OK)
```json
{
 "access_token": "ca44a17e-9b28-4fb7-bcf7-9ba09340c26f",
 "token_type": "bearer",
 "expires_in": 43199,
 "scope": "transfers",
 "expires_at": "2026-05-06T00:57:28.213Z"
}
```

### New format: JWT/JWE

Example Response with JWT (200 - OK)
```json
{
 "access_token": "eyJhbGciOiJSUzI1NiIsImVuYyI6IkEyNTZHQ00iLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiIzIiwiaXNzIjo...",
 "token_type": "bearer",
 "expires_in": 43199,
 "scope": "transfers",
 "expires_at": "2026-05-06T00:57:28.213Z"
}
```

**JWT token characteristics**

- Typically 500-800+ characters (length varies)
- Dot-separated sections (JWE commonly has 5 parts)
- Should be treated as an opaque string (do not parse or enforce UUID rules)


## Who is impacted

You are impacted if your integration does any of the following with `access_token`:

- Stores tokens in a UUID-typed database column
- Validates tokens with UUID regex checks or UUID parsers
- Assumes tokens are always 36 characters and include hyphens
- Performs UUID-specific conversions (for example, converting to a binary UUID type)


If you store the token as a string and only use it as a bearer token in the Authorization header, you are likely unaffected.

## What you need to do

### Step 1: Update database storage

Store access tokens in a string field that can hold long values.

**Recommended**

- TEXT, or a sufficiently large VARCHAR (for example, VARCHAR(2048) or larger)


**Avoid**

- UUID column types for access tokens
- Length limits that could truncate tokens


### Step 2: Update application code

- Handle `access_token` as an opaque string.


**Do**

- Store and pass the token as a string
- Use minimal validation (for example: non-empty string)


**Don't**

- Parse/cast to UUID
- Apply UUID regex validation
- Enforce fixed length (36 chars)


### Step 3: Test in sandbox

Before deploying to production:

1. Request Client Credentials tokens in sandbox
2. Confirm tokens can be stored without truncation
3. Confirm API calls succeed using: `Authorization: Bearer <access_token>`
4. Confirm no UUID validation/parsing paths reject the new format


## Frequently asked questions

### Do I need to decode the JWT?

No, treat the token as an opaque bearer token. Your integration should not depend on decoding token contents.

### Does the OAuth flow change?

No, only the `access_token` format changes.

Contact your Customer Success Manager if you have questions about operational queries. Otherwise, reach out to [api@wise.com](mailto:api@wise.com) for technical queries.