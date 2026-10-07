"""Free month, paid plans and access gating for Examic Study.

Payments are confirmed by staff (Wise bank transfer or Pay with Wise), so this module
only decides what a student may open. It never talks to a payment provider. A future
gateway can call `confirm_payment` and nothing else changes.

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
STAFF_ROLES = {
	"Administrator", "System Manager", "LMS Administrator", "LMS Moderator",
	"LMS Instructor", "Course Creator", "LMS Content Reviewer",
}

# Paths a locked student can still open.
ALLOWED_PREFIXES = (
	"/billing", "/pricing", "/sqe", "/terms", "/privacy", "/refund-policy", "/login",
	"/logout", "/assets", "/files", "/api/method/ping", "/api/method/logout",
	"/api/method/login", "/api/method/frappe.auth", "/api/method/frappe.core.doctype.user.user",
	"/api/method/aimaticlearning.lms_learning.billing.", "/api/method/frappe.client.get_value",
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
	doc = frappe.get_cached_doc(SETTINGS) if frappe.db.exists("DocType", SETTINGS) else None
	get = (lambda key, default=None: doc.get(key) if doc and doc.get(key) not in (None, "") else default)
	return {
		"trial_days": int(get("trial_days", DEFAULT_TRIAL_DAYS)),
		"monthly_price": float(get("monthly_price", PLANS["Monthly"]["default_price"])),
		"three_month_price": float(get("three_month_price", PLANS["3-Month"]["default_price"])),
		"account_holder": get("account_holder", ""),
		"sort_code": get("sort_code", ""),
		"account_number": get("account_number", ""),
		"payment_instructions": get("payment_instructions", ""),
		"support_email": get("support_email", "hello@aimatic.tech"),
	}


def plan_price(plan: str) -> float:
	return settings()[PLANS[plan]["price_field"]]


def trial_end(start=None):
	return add_days(start or nowdate(), settings()["trial_days"])


def _is_staff(user: str) -> bool:
	return bool(STAFF_ROLES & set(frappe.get_roles(user)))


def access_state(user: str | None = None) -> dict:
	user = user or frappe.session.user
	cache = frappe.local.__dict__.setdefault("_examic_access", {})
	if user in cache:
		return cache[user]
	if user == "Guest":
		result = {"state": "guest"}
	elif _is_staff(user):
		result = {"state": "staff"}
	elif not frappe.db.exists("DocType", SUBSCRIPTION):
		result = {"state": "full"}
	else:
		row = frappe.db.get_value(
			SUBSCRIPTION, user,
			["status", "plan", "trial_ends_on", "paid_until", "pending_plan", "pending_reference"],
			as_dict=True,
		)
		if not row:
			result = {"state": "full"}
		else:
			status = status_for(row.trial_ends_on, row.paid_until, row.pending_plan)
			state = state_for(status, False, True)
			end = row.paid_until if state == "paid" else row.trial_ends_on
			result = {
				"state": state,
				"status": status,
				"plan": row.plan,
				"trial_ends_on": row.trial_ends_on,
				"paid_until": row.paid_until,
				"pending_plan": row.pending_plan,
				"pending_reference": row.pending_reference,
				"days_left": (getdate(end) - getdate(nowdate())).days if end else 0,
			}
	cache[user] = result
	return result


def can_open_mock(user: str | None = None) -> bool:
	return mocks_unlocked(access_state(user)["state"])


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
	info = dict(access_state(user))
	info.update(
		{
			"reference": _reference(user),
			"plans": [
				{"name": "Monthly", "price": cfg["monthly_price"], "detail": "per month after your free month"},
				{"name": "3-Month", "price": cfg["three_month_price"], "detail": "for 3 months, paid once (months 2 to 4)"},
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
def request_payment(plan: str) -> dict:
	"""Student says they paid. Access stays as it is until staff confirm."""
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
			f"(£{plan_price(plan):g}). Reference: <strong>{reference}</strong>.</p>"
			f"<p>Check the Wise balance, then open the subscription and choose Confirm payment.</p>"
			f"<p><a href=\"{get_url('/desk/examic-subscription/' + user)}\">Open subscription</a></p>"
		),
		now=False,
	)
	frappe.db.commit()
	return {"ok": True, "reference": reference}


@frappe.whitelist()
def confirm_payment(subscription: str, plan: str, amount: float | None = None, payment_date=None,
		reference: str | None = None, method: str = "Wise bank transfer", note: str | None = None) -> dict:
	"""Staff only: record a payment and open the paid period."""
	if not (STAFF_ROLES - {"Course Creator", "LMS Content Reviewer", "LMS Instructor"}) & set(frappe.get_roles()):
		frappe.throw(_("Not permitted."), frappe.PermissionError)
	if plan not in PLANS:
		frappe.throw(_("Unknown plan."), frappe.ValidationError)
	doc = frappe.get_doc(SUBSCRIPTION, subscription)
	paid_on = getdate(payment_date or nowdate())
	doc.paid_until = extend_paid_until(plan, doc.trial_ends_on, doc.paid_until, paid_on)
	doc.plan = plan
	doc.last_payment_on = paid_on
	doc.pending_plan = None
	doc.pending_reference = None
	doc.pending_requested_on = None
	doc.append(
		"payments",
		{
			"payment_date": paid_on,
			"plan": plan,
			"amount": amount if amount not in (None, "") else plan_price(plan),
			"method": method,
			"reference": reference or doc.pending_reference or _reference(doc.user),
			"confirmed_by": frappe.session.user,
			"note": note,
		},
	)
	doc.save(ignore_permissions=True)
	_send_template(
		PAYMENT_RECEIPT_TEMPLATE, doc.user,
		{"plan": plan, "amount": f"£{float(amount or plan_price(plan)):g}",
		 "paid_until": frappe.utils.formatdate(doc.paid_until), "portal_url": get_url("/lms")},
	)
	return {"status": doc.status, "paid_until": str(doc.paid_until)}


def _send_template(template: str, user: str, extra: dict) -> None:
	from aimaticlearning.lms_learning.enrollment import _queue_email, _render_template

	if not frappe.db.exists("Email Template", template):
		return
	name = frappe.db.get_value("User", user, "full_name") or user
	subject, message = _render_template(template, {"student_name": name, "billing_url": get_url("/billing"), **extra})
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
		if end and new_status in ("Trial", "Active"):
			days_left = (getdate(end) - today).days
			if days_left in (REMIND_DAYS_BEFORE, 0):
				_send_template(
					PAYMENT_REMINDER_TEMPLATE, row.name,
					{"days_left": days_left, "end_date": frappe.utils.formatdate(end),
					 "ending": "free month" if new_status == "Trial" else "plan"},
				)
				counts["reminded"] += 1
	frappe.db.commit()
	return counts
