# Student signup flow

One continuous flow: details and plan, an emailed code, then the Stripe card page. Code: `aimaticlearning/lms_learning/signup.py`, form `templates/lms_learning/examic_signup_form.html`, browser check `scripts/signup-harness/run.js`. Card details are only ever typed on Stripe's hosted page.

## Steps

1. **Form** (`/login#signup`). Plan (Monthly or 3-Month), full name, email, password (8+ characters, show/hide), terms. Copy states pay £0 today and the first charge date.
2. **Request the code** (`request_signup_code`). The server checks every field, refuses an address that already has an account, then emails a 6-digit code immediately (not queued, so a mail failure is known). The pending signup waits in the cache for 15 minutes: password encrypted with the site key, code stored only as a hash. No User exists yet.
3. **Notice below the Sign up button.** It says the code was emailed to the exact address, to check the inbox and the spam or junk folder, that it can take a few minutes, and that it works for 15 minutes. The code box, "Confirm and add card", a resend countdown (60 s) and "Use a different email" sit in the same block. The form fields lock while a code is pending.
4. **Verify** (`verify_signup_code`). Right code: the student is created (the existing `start_student_signup` job then enrols them and sends the welcome email), the subscription row is created at once with `card_required` and the chosen `signup_plan`, the student is signed in, and `billing.start_checkout` returns the Stripe address.
5. **Card on Stripe.** Nothing is charged until the first charge date. Stripe returns to `/billing?paid=1`, which waits for the webhook and opens `/lms`.
6. **Closed the tab after step 4?** The student is a normal `setup` student: log in with the password, `/billing` offers the card again with their plan first.

## Limits and safety

- Code: 10 wrong tries, then the pending signup is deleted and a new code is needed. Expires after 15 minutes. Works once. Compared in constant time.
- Sending: 60 s between codes, 5 codes per email per hour, plus a per-IP limit on both endpoints.
- Existing enabled account: told to log in, no code. Disabled account: told it is registered but disabled.
- Stripe unreachable at step 4: the student still exists and is signed in; the page sends them to `/billing`.
- Mail failure at step 2: nothing is kept and the student is told it was not sent.
- The stock `lms.lms.user.sign_up` and `frappe.core.doctype.user.user.sign_up` are overridden (`hooks.py`) to refuse, so no unverified account can be created around the code.
- Cache loss only means the student asks for a new code.

## Checks

`python -m unittest aimaticlearning.lms_learning.test_signup` covers the server rules with an in-memory cache. `scripts/signup-harness/run.js` drives the real form in Chromium against stubbed answers (notice placement, inbox and spam wording, lock, countdown, wrong code, redirect, existing account, errors, 420 px width). Neither proves mail delivery or Stripe: do one real signup with a throwaway address after a deploy.

## Deploying

Restart web and workers, then run `bench --site examic.study clear-cache`. Frappe caches hooks in Redis, so without it the `override_whitelisted_methods` entries are not read and the stock `sign_up` stays open. Check with `frappe.get_hooks("override_whitelisted_methods")`, and probe with an address that already exists so a failed check creates nothing.
