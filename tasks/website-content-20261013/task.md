# Task: website-content-20261013

Goal: publish EXAMIC LTD's website content handover (Examic_Website_Content_Updated.docx)
on the public site without overwriting live product facts: shared header/footer, Home and
Pricing rewrite, SQE1, How It Works, Resources, About (+4), Contact, Introductory Offer,
Complaints, Accessibility, Educational Disclaimer, Cookie Notice and settings, updated
Terms, Refunds and Privacy, and email wording.

Environment (site `examic.study`; local-only or live): local code only. Not deployed.

Files / allowed edit paths: `aimaticlearning/www/` public pages, `templates/examic_site/`,
`public/css/examic_site.css`, `public/js/examic_site.js`, `lms_learning/public_site.py`,
`lms_learning/contact.py`, email template text in `enrollment.py`, billing allow-list.

Acceptance criteria: see the route table in the handover plan; no 30-mock, 5,000-card,
2,500-question, 1,000-page or "all content validated" claim anywhere; prices, trial days and
free mocks read from Examic Billing Settings; Monthly immediate-charge sentence kept.

Constraints (no core edits, no auto-enrol, live approval, API compatibility): no change to
prices, trial_days, checkout, access rules, portal pages or content. No VAT wording.

Base commit and existing local changes: `0d61bd1` (student-journey-review-20261008 snapshot),
work on branch `claude/eager-bardeen-0d1xts`.

Skills used: lms-learning, lms-billing.

Verification (commands, expected results):
- Done locally 2026-10-13: `test_contact`, `test_billing`, `test_signup_enrolment` pass
  (run against a frappe stub, no bench in that container). All 20 pages render through a
  Jinja harness; Playwright at 1366px and 375px: every route 200, one h1, no horizontal
  overflow, no unknown internal links, mobile menu with Log In/Create Account, About submenu,
  cookie Reject/Accept/Manage/Settings round trip, contact form validation and send.
- Not done: the real Frappe `web.html`/Bootstrap shell, the live site (blocked from that
  container), a real email from the contact form, logged-in `/lms` and `/billing` checks.

Status (defined / working / review / blocked / done): review (awaiting deploy approval).

Remaining issues / next step:
1. Deploy (approval): pull, `bench build --app aimaticlearning`, clear website cache, restart
   web. No migrate needed (no DocType change).
2. Run `enrollment.create_email_templates()` on the site so Welcome/Reminder wording updates (approval).
3. Live checks from the plan: `/` and `/sqe`, every menu/footer link, `/pricing` prices,
   contact form email reaches hello@examic.study, cookie banner, `/lms` and `/billing` for a
   student, one lesson and one mock entry.
4. Owner/legal: review Terms, Refunds, Privacy, Cookies; supply the processor list, locations,
   transfer safeguards and retention periods (privacy gaps are marked on the page). Note that
   `discord_alerts.notify` sends new students' email addresses to a Discord webhook; include it
   in the data map. Checkout still does not show cooling-off/early-supply wording or a model
   cancellation form (handover sections 11 and 17).
