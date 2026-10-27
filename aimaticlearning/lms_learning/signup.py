"""One-sitting student signup: details and plan, an emailed code, then straight to the card.

Nothing is created until the emailed code is entered. The pending signup lives in the cache
for `PENDING_SECONDS`, the password is stored encrypted with the site key and the code only as
a hash. Verifying creates the student, signs them in and returns the Stripe Checkout address.
See docs/signup-flow.md.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, escape_html
from frappe.website.utils import is_signup_disabled

from aimaticlearning.lms_learning import billing, enrollment

CODE_DIGITS = 6
PENDING_SECONDS = 15 * 60
RESEND_SECONDS = 60
MAX_SENDS_PER_HOUR = 5
MAX_CODE_TRIES = 10
MIN_PASSWORD_LENGTH = 8
PENDING_KEY = "examic_signup_pending:{}"
SENDS_KEY = "examic_signup_sends:{}"


def normalise_email(email: str | None) -> str:
	return (email or "").strip().lower()


def new_code() -> str:
	return f"{secrets.randbelow(10**CODE_DIGITS):0{CODE_DIGITS}d}"


def hash_code(email: str, code: str) -> str:
	return hashlib.sha256(f"{normalise_email(email)}:{(code or '').strip()}".encode()).hexdigest()


def code_matches(pending: dict, email: str, code: str) -> bool:
	entered = (code or "").strip()
	if len(entered) != CODE_DIGITS or not entered.isdigit():
		return False
	return hmac.compare_digest(pending.get("code_hash", ""), hash_code(email, entered))


def password_problem(password: str | None, email: str, full_name: str) -> str | None:
	"""The reason a password is not accepted, or None."""
	password = password or ""
	if len(password) < MIN_PASSWORD_LENGTH:
		return _("Choose a password of at least {0} characters.").format(MIN_PASSWORD_LENGTH)
	if len(password) > 100:
		return _("That password is too long.")
	if password.lower() in {email, (full_name or "").strip().lower()}:
		return _("Your password cannot be your name or email.")
	return None


def recent_sends(email: str, now: float | None = None) -> list[float]:
	cutoff = (now if now is not None else time.time()) - 3600
	return [stamp for stamp in (frappe.cache.get_value(SENDS_KEY.format(email)) or []) if stamp > cutoff]


def seconds_until_resend(email: str, now: float | None = None) -> int:
	sends = recent_sends(email, now)
	if not sends:
		return 0
	wait = RESEND_SECONDS - ((now if now is not None else time.time()) - max(sends))
	return max(0, int(wait + 0.999))


def _send_code_email(email: str, full_name: str, code: str) -> None:
	"""Sent now, not queued, so a failure is known before the student is told it was sent."""
	minutes = PENDING_SECONDS // 60
	frappe.sendmail(
		recipients=[email],
		subject=_("Your Examic Study code: {0}").format(code),
		message=(
			f"<p>Hi {escape_html(full_name)},</p>"
			f"<p>Your Examic Study verification code is:</p>"
			f"<p style=\"font-size:28px;letter-spacing:6px;font-weight:700\">{code}</p>"
			f"<p>Enter it on the signup page within {minutes} minutes. "
			"If you did not ask for this, ignore this email and nothing will be created.</p>"
		),
		now=True,
	)


def _existing_account_answer(email: str) -> dict | None:
	row = frappe.db.get_value("User", {"email": email}, ["name", "enabled"], as_dict=True)
	if not row:
		return None
	if row.enabled:
		return {"status": "exists", "message": _("Already Registered")}
	return {"status": "disabled", "message": _("Registered but disabled")}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60 * 60)
def request_signup_code(
	email: str,
	full_name: str,
	password: str,
	plan: str,
	verify_terms: int = 0,
	user_category: str = "",
) -> dict:
	"""Check the form, keep it pending and email the code. Creates no user."""
	if is_signup_disabled():
		frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))
	email = normalise_email(email)
	full_name = (full_name or "").strip()
	if not full_name:
		return {"status": "invalid", "field": "signup_fullname", "message": _("Full name is required.")}
	if not enrollment.is_plausible_email(email):
		return {"status": "invalid", "field": "signup_email", "message": _("Please enter a valid email.")}
	if plan not in billing.PLANS:
		return {"status": "invalid", "field": "signup_plan", "message": _("Choose a plan.")}
	problem = password_problem(password, email, full_name)
	if problem:
		return {"status": "invalid", "field": "signup_password", "message": problem}
	if not cint(verify_terms):
		return {"status": "invalid", "field": "signup-terms", "message": _("Please accept the terms to continue.")}
	existing = _existing_account_answer(email)
	if existing:
		return existing

	wait = seconds_until_resend(email)
	if wait:
		return {"status": "wait", "wait": wait, "message": _("A code was just sent. You can ask for another in {0} seconds.").format(wait)}
	if len(recent_sends(email)) >= MAX_SENDS_PER_HOUR:
		return {"status": "limit", "message": _("Too many codes were requested for this email. Please try again in an hour.")}

	from frappe.utils.password import encrypt

	code = new_code()
	pending = {
		"full_name": full_name,
		"plan": plan,
		"password": encrypt(password),
		"user_category": (user_category or "")[:140],
		"code_hash": hash_code(email, code),
		"tries": 0,
	}
	try:
		_send_code_email(email, full_name, code)
	except Exception:
		frappe.log_error(title="Signup code email failed", message=email)
		return {"status": "mail_failed", "message": _("We could not send the email. Please try again or contact {0}.").format(_support_email())}
	frappe.cache.set_value(PENDING_KEY.format(email), pending, expires_in_sec=PENDING_SECONDS)
	frappe.cache.set_value(SENDS_KEY.format(email), [*recent_sends(email), time.time()], expires_in_sec=3600)
	return {"status": "sent", "email": email, "wait": RESEND_SECONDS, "expires_in": PENDING_SECONDS}


def _support_email() -> str:
	return frappe.db.get_single_value("LMS Settings", "contact_us_email") or "hello@examic.study"


def _create_student(email: str, pending: dict) -> str:
	from frappe.utils.password import decrypt

	default_role = frappe.db.get_single_value("Portal Settings", "default_role")
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": escape_html(pending["full_name"]),
			"verify_terms": 1,
			"user_category": pending.get("user_category") or "",
			"country": "",
			"enabled": 1,
			"send_welcome_email": 0,
			"new_password": decrypt(pending["password"]),
			"user_type": "Website User",
		}
	)
	user.flags.ignore_permissions = True
	user.flags.ignore_password_policy = True
	user.flags.no_welcome_mail = True
	if default_role:
		user.append_roles(default_role)
	user.insert()
	return user.name


def _log_in(user: str) -> None:
	frappe.local.login_manager.login_as(user)


def _checkout_url(plan: str) -> str:
	"""None when Stripe cannot be reached: the student then lands on /billing to add the card."""
	try:
		return billing.start_checkout(plan).get("url") or ""
	except Exception:
		frappe.log_error(title="Signup checkout not opened", message=frappe.session.user)
		return ""


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=60, seconds=60 * 60)
def verify_signup_code(email: str, code: str) -> dict:
	"""Check the code, create and sign in the student, open the card page."""
	email = normalise_email(email)
	key = PENDING_KEY.format(email)
	pending = frappe.cache.get_value(key)
	if not pending:
		return {"status": "expired", "message": _("This code has expired. Ask for a new one.")}
	if not code_matches(pending, email, code):
		pending["tries"] = cint(pending.get("tries")) + 1
		if pending["tries"] >= MAX_CODE_TRIES:
			frappe.cache.delete_value(key)
			return {"status": "locked", "message": _("Too many wrong codes. Ask for a new one.")}
		frappe.cache.set_value(key, pending, expires_in_sec=PENDING_SECONDS)
		left = MAX_CODE_TRIES - pending["tries"]
		return {"status": "wrong", "left": left, "message": _("That code is not right. {0} tries left.").format(left)}

	frappe.cache.delete_value(key)
	existing = _existing_account_answer(email)
	if existing:
		return existing
	try:
		user = _create_student(email, pending)
	except frappe.DuplicateEntryError:
		frappe.db.rollback()
		return {"status": "exists", "message": _("Already Registered")}

	# The card step needs the card-required subscription row now, not after the background job.
	billing.create_subscription(user)
	if billing.signup_plan_field():
		frappe.db.set_value(billing.SUBSCRIPTION, user, "signup_plan", pending["plan"], update_modified=False)
	frappe.db.commit()
	_log_in(user)
	return {"status": "ok", "url": _checkout_url(pending["plan"]), "billing": "/billing"}


@frappe.whitelist(allow_guest=True)
def refuse_direct_signup(email: str | None = None, full_name: str | None = None, **kwargs):
	"""Stands in for the stock sign_up endpoints, so no account can skip the emailed code."""
	frappe.throw(_("Please sign up from the Examic Study signup page."), title=_("Not Allowed"))
