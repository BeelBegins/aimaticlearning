"""Free month, paid plans and access gating for Examic Study.

Stripe Checkout and its signed webhooks handle student card payments. Staff can still
confirm a payment directly through the restricted manual confirmation method.

Access states:
  staff   staff roles: everything
  full    an account with no subscription row (existing students): all courses, mocks 1 and 2
  trial   free month: all courses, Mock 1 and Mock 2
  paid    paid period: everything including every mock
  locked  free month over and not paid: only the billing page
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import add_days, add_months, get_url, getdate, nowdate

SETTINGS = "Examic Billing Settings"
SUBSCRIPTION = "Examic Subscription"
PLANS = {
	"Monthly": {"months": 1, "price_field": "monthly_price", "default_price": 49, "label": "Monthly"},
	"3-Month": {"months": 3, "price_field": "three_month_price", "default_price": 99, "label": "3-Month"},
}
DEFAULT_TRIAL_DAYS = 30
FREE_MOCKS = 2
REMIND_DAYS_BEFORE = 3
PAYMENT_REMINDER_TEMPLATE = "Examic Study Payment Reminder"
PAYMENT_RECEIPT_TEMPLATE = "Examic Study Payment Receipt"
PAYMENT_PROBLEM_TEMPLATE = "Examic Study Payment Problem"
STAFF_ROLES = {
	"Administrator", "System Manager", "LMS Administrator", "LMS Moderator",
	"LMS Instructor", "Course Creator", "LMS Content Reviewer",
}

# Paths a locked student can still open.
ALLOWED_PREFIXES = (
	"/billing", "/pricing", "/sqe", "/terms", "/privacy", "/refund-policy", "/login",
	"/logout", "/assets", "/files", "/api/method/ping", "/api/method/logout",
	"/api/method/login", "/api/method/frappe.auth", "/api/method/frappe.core.doctype.user.user",
	"/api/method/aimaticlearning.lms_learning.billing.", "/api/method/aimaticlearning.lms_learning.contact.",
	"/api/method/frappe.client.get_value",
	"/api/method/frappe.desk.form.", "/favicon", "/robots.txt", "/sitemap.xml", "/sw.js",
)
# App surfaces that are locked when the free month is over.
LOCKED_PREFIXES = (
	"/lms", "/learning-", "/api/method/lms.", "/api/method/aimaticlearning.", "/api/resource/LMS ",
	"/api/resource/Course", "/api/resource/Learning",
)


def status_for(trial_ends_on, paid_until, pending_plan=None, today=None) -> str:
	today = getdate(today or nowdate())
	if paid_until and getdate(paid_until) >= today:
		return "Active"
	if trial_ends_on and getdate(trial_ends_on) >= today:
		return "Trial"
	return "Awaiting Payment" if pending_plan else "Expired"


def state_for(status: str, is_staff: bool, has_subscription: bool) -> str:
	if is_staff:
		return "staff"
	if not has_subscription:
		return "full"
	return {"Active": "paid", "Trial": "trial"}.get(status, "locked")


def extend_paid_until(plan: str, trial_ends_on, paid_until, today=None):
	"""First paid day follows the free month. Paying again early extends, never shortens."""
	months = PLANS[plan]["months"]
	base = max(
		getdate(today or nowdate()),
		getdate(trial_ends_on) if trial_ends_on else getdate(today or nowdate()),
		getdate(paid_until) if paid_until else getdate(today or nowdate()),
	)
	return getdate(add_months(base, months))


def mocks_unlocked(state: str) -> bool:
	return state in ("staff", "paid")


def settings() -> dict:
	"""Billing settings with safe defaults. Secrets are decrypted here and never logged."""
	defaults = {
		"enabled": 1, "active_provider": "Manual", "support_email": "hello@examic.study",
		"trial_days": DEFAULT_TRIAL_DAYS, "free_mock_count": FREE_MOCKS, "reminder_days": REMIND_DAYS_BEFORE,
		"monthly_price": PLANS["Monthly"]["default_price"], "three_month_price": PLANS["3-Month"]["default_price"],
		"account_holder": "", "sort_code": "", "account_number": "", "payment_instructions": "",
		"stripe_mode": "Test", "stripe_publishable_key": "", "stripe_monthly_price_id": "",
		"stripe_three_month_price_id": "", "stripe_secret_key": "", "stripe_webhook_secret": "",
		"stripe_automatic_tax": 0,
	}
	if not frappe.db.exists("DocType", SETTINGS):
		return defaults
	doc = frappe.get_cached_doc(SETTINGS)
	cfg = dict(defaults)
	for key, default in defaults.items():
		if key in ("stripe_secret_key", "stripe_webhook_secret"):
			cfg[key] = doc.get_password(key, raise_exception=False) or ""
		elif doc.get(key) not in (None, ""):
			cfg[key] = doc.get(key)
	for key in ("trial_days", "free_mock_count", "reminder_days"):
		cfg[key] = int(cfg[key])
	for key in ("monthly_price", "three_month_price"):
		cfg[key] = float(cfg[key])
	return cfg


def plan_price(plan: str) -> float:
	return settings()[PLANS[plan]["price_field"]]


def price_text(value: float) -> str:
	return f"\u00a3{value:g}"


def trial_end(start=None):
	return add_days(start or nowdate(), settings()["trial_days"])


def provider():
	"""The active provider. Stripe only counts as active once its keys are filled in."""
	from aimaticlearning.lms_learning.billing_providers.manual import ManualProvider
	from aimaticlearning.lms_learning.billing_providers.stripe import StripeProvider

	cfg = settings()
	if cfg["active_provider"] == "Stripe":
		stripe = StripeProvider()
		if stripe.is_ready(cfg):
			return stripe
	return ManualProvider()


def _is_staff(user: str) -> bool:
	return bool(STAFF_ROLES & set(frappe.get_roles(user)))


def access_state(user: str | None = None) -> dict:
	user = user or frappe.session.user
	cache = getattr(frappe.local, "examic_access", None)
	if cache is None:
		cache = frappe.local.examic_access = {}
	if user in cache:
		return cache[user]
	if user == "Guest":
		result = {"state": "guest"}
	elif _is_staff(user):
		result = {"state": "staff"}
	elif not frappe.db.exists("DocType", SUBSCRIPTION) or not settings()["enabled"]:
		result = {"state": "full"}
	else:
		row = frappe.db.get_value(
			SUBSCRIPTION, user,
			["status", "plan", "trial_ends_on", "paid_until", "pending_plan", "pending_reference", "stripe_subscription"],
			as_dict=True,
		)
		if not row:
			result = {"state": "unsubscribed"}
		else:
			status = status_for(row.trial_ends_on, row.paid_until, row.pending_plan)
			state = state_for(status, False, True)
			if status == "Awaiting Payment" and not row.trial_ends_on and not row.paid_until:
				state = "unsubscribed"
			end = row.paid_until if state == "paid" else row.trial_ends_on
			monthly_subscription_active = bool(
				state in ("trial", "unsubscribed") and row.plan == "Monthly" and row.stripe_subscription
			)
			result = {
				"state": state,
				"status": status,
				"plan": row.plan,
				"trial_ends_on": row.trial_ends_on,
				"paid_until": row.paid_until,
				"pending_plan": row.pending_plan,
				"pending_reference": row.pending_reference,
				"monthly_subscription_active": monthly_subscription_active,
				"days_left": (getdate(end) - getdate(nowdate())).days if end else 0,
			}
	cache[user] = result
	return result


def can_open_mock(user: str | None = None) -> bool:
	state = access_state(user)
	return mocks_unlocked(state["state"]) or bool(state.get("monthly_subscription_active"))


def is_locked_path(path: str) -> bool:
	path = path or ""
	if path.startswith(ALLOWED_PREFIXES):
		return False
	return path.startswith(LOCKED_PREFIXES)


class PaymentRequired(frappe.ValidationError):
	http_status_code = 402


def _found(location: str):
	from werkzeug.exceptions import HTTPException
	from werkzeug.utils import redirect

	class Found(HTTPException):
		code = 302

		def get_response(self, environ=None, scope=None):
			return redirect(location, 302)

	return Found()


def enforce_access():
	"""before_request: a student whose free month is over sees only the billing page."""
	request = getattr(frappe.local, "request", None)
	if not request or frappe.session.user == "Guest":
		return
	path = request.path or ""
	if not is_locked_path(path):
		return
	if access_state()["state"] != "locked":
		return
	if path.startswith("/api/"):
		raise PaymentRequired(_("Your free month has ended. Choose a plan on the billing page."))
	raise _found("/billing")


def create_subscription(user: str, start=None):
	"""Idempotent: one subscription per new student, started at signup."""
	if frappe.db.exists(SUBSCRIPTION, user):
		return frappe.get_doc(SUBSCRIPTION, user)
	end = trial_end(start)
	doc = frappe.get_doc({"doctype": SUBSCRIPTION, "user": user, "trial_ends_on": end, "status": "Trial"})
	doc.insert(ignore_permissions=True)
	return doc


def _reference(user: str) -> str:
	import hashlib

	return "EXM-" + hashlib.sha1(user.lower().encode()).hexdigest()[:6].upper()


@frappe.whitelist()
def get_billing_state() -> dict:
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("Please sign in."), frappe.PermissionError)
	cfg = settings()
	prov = provider()
	info = dict(access_state(user))
	sub = frappe.db.get_value(SUBSCRIPTION, user, ["stripe_customer", "last_payment_error"], as_dict=True) or {}
	info.update(
		{
			"provider": prov.name,
			"reference": _reference(user),
			"can_manage": bool(sub.get("stripe_customer")) and prov.name == "Stripe",
			"payment_problem": sub.get("last_payment_error") or "",
			"plans": [
				{"name": "Monthly", "price": cfg["monthly_price"], "detail": "per month, starts today"},
				{
					"name": "3-Month",
					"price": cfg["three_month_price"],
					"detail": (
						"for 3 months after your free month, paid once today"
						if info.get("state") == "trial"
						else "for 3 months, paid once, starts today"
					),
				},
			],
			"account_holder": cfg["account_holder"],
			"sort_code": cfg["sort_code"],
			"account_number": cfg["account_number"],
			"instructions": cfg["payment_instructions"],
			"support_email": cfg["support_email"],
		}
	)
	return json.loads(frappe.as_json(info))


@frappe.whitelist()
def start_checkout(plan: str) -> dict:
	"""Stripe: create a hosted Checkout page for this student and plan."""
	user = frappe.session.user
	if user == "Guest" or plan not in PLANS:
		frappe.throw(_("Choose a plan."), frappe.ValidationError)
	prov = provider()
	if prov.name != "Stripe":
		frappe.throw(_("Card payment is not available yet."), frappe.ValidationError)
	sub = frappe.db.get_value(SUBSCRIPTION, user, ["trial_ends_on", "stripe_customer"], as_dict=True)
	if not sub:
		user_doc = frappe.db.get_value("User", user, ["enabled", "user_type"], as_dict=True)
		if not user_doc or not user_doc.enabled or user_doc.user_type != "Website User":
			frappe.throw(_("This account cannot start a student plan."), frappe.PermissionError)
		doc = frappe.get_doc({
			"doctype": SUBSCRIPTION,
			"user": user,
			"pending_plan": plan,
			"pending_reference": _reference(user),
			"pending_requested_on": frappe.utils.now_datetime(),
		})
		doc.insert(ignore_permissions=True)
		sub = {"trial_ends_on": None, "stripe_customer": None}
	email = frappe.db.get_value("User", user, "email") or user
	return prov.start_payment(user, email, plan, settings(), dict(sub))


@frappe.whitelist()
def open_portal() -> dict:
	"""Stripe customer portal: update card, see invoices, cancel."""
	user = frappe.session.user
	customer = frappe.db.get_value(SUBSCRIPTION, user, "stripe_customer") if user != "Guest" else None
	prov = provider()
	if prov.name != "Stripe" or not customer:
		frappe.throw(_("No card billing found for this account."), frappe.ValidationError)
	return {"url": prov.portal_url(customer, settings())}


@frappe.whitelist()
def request_payment(plan: str) -> dict:
	"""Manual provider: the student says they paid. Access stays as it is until staff confirm."""
	user = frappe.session.user
	if user == "Guest" or plan not in PLANS:
		frappe.throw(_("Choose a plan."), frappe.ValidationError)
	if not frappe.db.exists(SUBSCRIPTION, user):
		frappe.throw(_("No subscription found for this account."), frappe.ValidationError)
	reference = _reference(user)
	frappe.db.set_value(
		SUBSCRIPTION, user,
		{"pending_plan": plan, "pending_reference": reference, "pending_requested_on": frappe.utils.now_datetime()},
	)
	cfg = settings()
	frappe.sendmail(
		recipients=[cfg["support_email"]],
		subject=f"Payment to confirm: {user} ({plan})",
		message=(
			f"<p>{frappe.utils.escape_html(user)} says they paid for the {plan} plan "
			f"({price_text(plan_price(plan))}). Reference: <strong>{reference}</strong>.</p>"
			f"<p>Check the bank balance, then open the subscription and choose Confirm payment.</p>"
			f"<p><a href=\"{get_url('/desk/examic-subscription/' + user)}\">Open subscription</a></p>"
		),
		now=False,
	)
	frappe.db.commit()
	return {"ok": True, "reference": reference}


def apply_payment(doc, plan: str, amount: float | None, paid_on, reference: str | None,
		method: str, note: str | None = None, confirmed_by: str | None = None,
		starts_now: bool = False) -> dict:
	"""The one place that opens a paid period. `starts_now` lets Monthly begin on checkout day."""
	paid_on = getdate(paid_on or nowdate())
	trial_end = None if starts_now else doc.trial_ends_on
	doc.paid_until = extend_paid_until(plan, trial_end, doc.paid_until, paid_on)
	doc.plan = plan
	doc.last_payment_on = paid_on
	doc.last_payment_error = None
	reference = reference or doc.pending_reference or _reference(doc.user)
	doc.pending_plan = None
	doc.pending_reference = None
	doc.pending_requested_on = None
	value = float(amount) if amount not in (None, "") else plan_price(plan)
	doc.append(
		"payments",
		{"payment_date": paid_on, "plan": plan, "amount": value, "method": method,
		 "reference": reference, "confirmed_by": confirmed_by, "note": note},
	)
	doc.save(ignore_permissions=True)
	_send_template(
		PAYMENT_RECEIPT_TEMPLATE, doc.user,
		{"plan": plan, "amount": price_text(value),
		 "paid_until": frappe.utils.formatdate(doc.paid_until), "portal_url": get_url("/lms")},
	)
	_discord(
		"payment_confirmed",
		"Payment confirmed",
		f"{doc.user} paid {price_text(value)} ({plan}). Paid until {doc.paid_until}.",
		f"payment:{doc.user}:{reference}",
	)
	return {"status": doc.status, "paid_until": str(doc.paid_until)}


@frappe.whitelist()
def confirm_payment(subscription: str, plan: str, amount: float | None = None, payment_date=None,
		reference: str | None = None, method: str = "Wise bank transfer", note: str | None = None) -> dict:
	"""Staff only (manual provider): record a payment and open the paid period."""
	if not ({"System Manager", "LMS Administrator", "Administrator"} & set(frappe.get_roles())):
		frappe.throw(_("Not permitted."), frappe.PermissionError)
	if plan not in PLANS:
		frappe.throw(_("Unknown plan."), frappe.ValidationError)
	doc = frappe.get_doc(SUBSCRIPTION, subscription)
	return apply_payment(doc, plan, amount, payment_date, reference, method, note, frappe.session.user)


def _log_event(event_id: str, provider_name: str, event_type: str, status: str, **fields) -> None:
	if frappe.db.exists("Examic Payment Event", event_id):
		return
	frappe.get_doc(
		{"doctype": "Examic Payment Event", "event_id": event_id, "provider": provider_name,
		 "event_type": event_type, "status": status, **fields}
	).insert(ignore_permissions=True)


def _find_subscription(action: dict) -> str | None:
	"""Match by the user we put in Stripe metadata, else by the saved Stripe customer."""
	user = action.get("user")
	if user and frappe.db.exists(SUBSCRIPTION, user):
		return user
	for field in ("stripe_customer", "stripe_subscription"):
		key = "customer" if field == "stripe_customer" else "subscription"
		if action.get(key):
			found = frappe.db.get_value(SUBSCRIPTION, {field: action[key]}, "name")
			if found:
				return found
	return None


def process_stripe_event(event: dict) -> str:
	"""Apply one verified Stripe event. Idempotent by event id. Returns the log status."""
	from aimaticlearning.lms_learning.billing_providers import stripe as stripe_mod

	event_id, event_type = event.get("id") or "", event.get("type") or ""
	if not event_id or frappe.db.exists("Examic Payment Event", event_id):
		return "Ignored"
	action = stripe_mod.interpret_event(event)
	if action["action"] == "ignore":
		_log_event(event_id, "Stripe", event_type, "Ignored")
		return "Ignored"
	name = _find_subscription(action)
	if not name:
		_log_event(event_id, "Stripe", event_type, "Needs review", reference=action.get("reference"),
			amount=action.get("amount"), error="No matching student for this payment event.")
		_discord(
			"payment_needs_review",
			"Payment needs review",
			"No matching student for this payment event.",
			f"review:{event_id}",
		)
		return "Needs review"
	doc = frappe.get_doc(SUBSCRIPTION, name)
	if action.get("customer") and not doc.stripe_customer:
		doc.stripe_customer = action["customer"]
	if action.get("subscription"):
		doc.stripe_subscription = action["subscription"]
	kind = action["action"]
	if kind == "pay":
		plan = action.get("plan")
		if plan not in PLANS:
			doc.save(ignore_permissions=True)
			_log_event(event_id, "Stripe", event_type, "Needs review", user=name, reference=action.get("reference"),
				amount=action.get("amount"), error="Plan missing on the payment.")
			_discord(
				"payment_needs_review",
				"Payment needs review",
				f"{name}: plan missing on the payment.",
				f"review:{event_id}",
			)
			return "Needs review"
		apply_payment(
			doc, plan, action.get("amount"), nowdate(), action.get("reference"), "Stripe card",
			None, None, starts_now=bool(action.get("starts_now")),
		)
	elif kind == "failed":
		doc.last_payment_error = action["message"]
		doc.save(ignore_permissions=True)
		_send_template(PAYMENT_PROBLEM_TEMPLATE, name, {})
	elif kind == "cancelled":
		doc.stripe_subscription = None
		doc.save(ignore_permissions=True)
	else:  # link
		if action.get("plan") in PLANS:
			doc.plan = action["plan"]
		doc.save(ignore_permissions=True)
	_log_event(event_id, "Stripe", event_type, "Matched", user=name, plan=action.get("plan"),
		amount=action.get("amount"), reference=action.get("reference"))
	return "Matched"


@frappe.whitelist(allow_guest=True, methods=["POST"])
def stripe_webhook():
	"""Stripe calls this. The signature, not a login, proves the request is genuine."""
	from aimaticlearning.lms_learning.billing_providers import stripe as stripe_mod

	cfg = settings()
	payload = frappe.request.get_data()
	header = frappe.get_request_header("Stripe-Signature") or ""
	if not stripe_mod.verify_signature(payload, header, cfg["stripe_webhook_secret"]):
		frappe.local.response["http_status_code"] = 400
		return {"error": "invalid signature"}
	try:
		event = json.loads(payload.decode("utf-8"))
		status = process_stripe_event(event)
	except Exception:
		frappe.db.rollback()
		frappe.log_error(title="Stripe webhook failed", message=frappe.get_traceback())
		frappe.local.response["http_status_code"] = 500
		return {"error": "processing failed"}
	frappe.db.set_single_value(SETTINGS, "stripe_last_event", frappe.utils.now_datetime())
	frappe.db.commit()
	return {"status": status}


def _discord(event: str, title: str, description: str, dedupe_key: str) -> None:
	try:
		from aimaticlearning.lms_learning.discord_alerts import notify

		notify(event, title=title, description=description, dedupe_key=dedupe_key)
	except Exception:
		frappe.log_error(title="Discord alert failed")


def _send_template(template: str, user: str, extra: dict) -> None:
	from aimaticlearning.lms_learning.enrollment import _queue_email, _render_template

	if not frappe.db.exists("Email Template", template):
		return
	cfg = settings()
	name = frappe.db.get_value("User", user, "full_name") or user
	context = {"student_name": name, "billing_url": get_url("/billing"),
		"monthly_price": price_text(cfg["monthly_price"]), "three_month_price": price_text(cfg["three_month_price"]), **extra}
	subject, message = _render_template(template, context)
	_queue_email(user, subject, message, SUBSCRIPTION, user)


def daily_billing_job() -> dict:
	"""Refresh statuses and send reminders before and on the day access ends."""
	counts = {"updated": 0, "reminded": 0}
	today = getdate(nowdate())
	for row in frappe.get_all(
		SUBSCRIPTION, fields=["name", "status", "trial_ends_on", "paid_until", "pending_plan"]
	):
		end = row.paid_until if row.paid_until and getdate(row.paid_until) >= today else row.trial_ends_on
		new_status = status_for(row.trial_ends_on, row.paid_until, row.pending_plan, today)
		if new_status != row.status:
			frappe.db.set_value(SUBSCRIPTION, row.name, "status", new_status, update_modified=False)
			counts["updated"] += 1
			if row.status in ("Trial", "Active") and new_status in ("Expired", "Awaiting Payment"):
				_discord(
					"access_locked",
					"Access locked",
					f"{row.name} is now {new_status}.",
					f"locked:{row.name}:{today}",
				)
		if end and new_status in ("Trial", "Active"):
			days_left = (getdate(end) - today).days
			if days_left in (settings()["reminder_days"], 0):
				_send_template(
					PAYMENT_REMINDER_TEMPLATE, row.name,
					{"days_left": days_left, "end_date": frappe.utils.formatdate(end),
					 "ending": "free month" if new_status == "Trial" else "plan"},
				)
				counts["reminded"] += 1
	frappe.db.commit()
	return counts
