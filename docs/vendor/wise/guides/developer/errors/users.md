# User errors

Handle user creation and registration code errors.

User creation errors identify invalid registration details or an email that already belongs to a Wise user. Process every item in the `errors` array and use `path` to associate the error with an input.

On this page:

- [Create a user](#create-a-user)
- [Prevent user creation errors](#prevent-user-creation-errors)
- [Handle user error messages](#handle-user-error-messages)


See the [shared handling guidance](/guides/developer/errors#choose-a-recovery-action) for choosing an action, displaying messages, and retrying safely.

## Create a user

**Endpoint:** `POST /user/signup/registration_code`

The examples below are documented for `POST /v1/user/signup/registration_code`. Match your API version when using them.

See the [create a user operation](/api-reference/user/usercreate) for the current request and response schema.

A value that must be unique is already in use. Use `path` to identify the affected field.

**HTTP status:** `409`

**What to do**

- Check the field identified by `path` before choosing a recovery action.
- If the email belongs to an existing Wise user, stop user creation and follow the account-linking or OAuth flow for your integration. Do not change the email to bypass that conflict.


**Retry conditions**

Do not retry the same request.

**Example error response (v1)**

```json
{
  "errors": [
    {
      "code": "NOT_UNIQUE",
      "message": "You're already a member. Please login",
      "path": "email",
      "arguments": [
        "email",
        "ma********************@wise.com"
      ]
    }
  ]
}
```

A required field is missing or has a null value. Use `path` to identify each affected field.

**HTTP status:** `400`

**What to do**

- Provide all fields required by the current operation schema.
- Process every item in the `errors` array.


**Retry conditions**

Retry after adding the missing fields.

**Example error response (v1)**

```json
{
  "errors": [
    {
      "code": "NotNull",
      "message": "must not be null",
      "path": "email",
      "arguments": []
    },
    {
      "code": "NotNull",
      "message": "must not be null",
      "path": "registrationCode",
      "arguments": []
    }
  ]
}
```

A field does not meet its size restrictions: its length is below the allowed minimum or above the allowed maximum. Use `path` to identify the field and check its applicable constraints.

**HTTP status:** `400`

**What to do**

- Use `path` to identify the field.
- Validate its length against the current operation schema and any limits supplied in the response.
- Treat `arguments` as error-specific context.


**Retry conditions**

Retry after correcting the field length.

**Example error response (v1)**

```json
{
  "errors": [
    {
      "code": "Size",
      "message": "size must be between 32 and 2147483647",
      "path": "registrationCode",
      "arguments": [
        "2147483647",
        "32"
      ]
    }
  ]
}
```

A field failed validation but the response uses a generic identifier. The endpoint and `path` provide the specific meaning.

**HTTP status:** `422`

**What to do**

- Associate the error with the field identified by `path`.
- Use a suitable returned message for user-correctable input, with a safe fallback.
- Do not map `ERROR` to one universal meaning.


**Retry conditions**

Retry after correcting the identified field.

**Example error response (v1)**

```json
{
  "errors": [
    {
      "code": "ERROR",
      "message": "Please provide a valid email",
      "path": "email",
      "arguments": [
        "email",
        "ma********************@w"
      ]
    }
  ]
}
```

## Prevent user creation errors

Before creating a user:

- Provide a valid email address.
- Generate and store a unique `registrationCode` with at least 32 characters.
- Protect the registration code as you would other credentials.
- Keep it because the registration-code grant uses it to obtain tokens.


Do not depend on a particular code for every malformed request. Validate against the operation schema and use `path`, where present, to locate the affected field.

## Handle user error messages

- Display a returned message only when it clearly describes user-correctable input.
- Do not parse message text or use it for programmatic branching.
- Keep email addresses and registration codes out of logs.
- Record the endpoint, HTTP status, code, and path for unknown errors.