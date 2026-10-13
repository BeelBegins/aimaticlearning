"""Public contact form for the Examic website (/contact).

Enquiries are emailed to the support mailbox in Examic Billing Settings
(hello@examic.study). Nothing is stored beyond the Email Queue record, and no marketing
consent is asked for or recorded.
"""

from __future__ import annotations

import re

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import escape_html

ENQUIRY_TYPES = (
	"Account Support",
	"Content Issue",
	"Subscription & Cancellation",
	"Privacy",
	"Accessibility",
	"Complaint",
	"Business Enquiry",
)
MAX_LENGTH = {"name": 140, "email": 140, "reference": 140, "message": 5000}
_EMAIL = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")


def clean_enquiry(name, email, enquiry_type, message, reference=None) -> dict:
	"""Validate one enquiry. Raises ValueError with a learner-facing message."""
	values = {
		"name": " ".join(str(name or "").split()),
		"email": str(email or "").strip(),
		"enquiry_type": str(enquiry_type or "").strip(),
		"message": str(message or "").strip(),
		"reference": " ".join(str(reference or "").split()),
	}
	if not values["name"]:
		raise ValueError("Please enter your name.")
	if not _EMAIL.match(values["email"]):
		raise ValueError("Please enter a valid email address.")
	if values["enquiry_type"] not in ENQUIRY_TYPES:
		raise ValueError("Please choose an enquiry type.")
	if len(values["message"]) < 5:
		raise ValueError("Please write your message.")
	for key, limit in MAX_LENGTH.items():
		if len(values[key]) > limit:
			raise ValueError(f"The {key} field is too long (maximum {limit} characters).")
	return values


def email_body(values: dict) -> str:
	rows = [
		("Name", values["name"]),
		("Email", values["email"]),
		("Enquiry type", values["enquiry_type"]),
		("Lesson or order reference", values["reference"] or "Not given"),
	]
	table = "".join(f"<tr><th align='left'>{label}</th><td>{escape_html(value)}</td></tr>" for label, value in rows)
	text = escape_html(values["message"]).replace("\n", "<br>")
	return f"<p>New enquiry from the examic.study contact form.</p><table>{table}</table><p>{text}</p>"


def support_email() -> str:
	try:
		from aimaticlearning.lms_learning.billing import settings

		return settings().get("support_email") or "hello@examic.study"
	except Exception:
		return "hello@examic.study"


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60 * 60)
def submit_enquiry(name=None, email=None, enquiry_type=None, message=None, reference=None, website=None):
	if website:
		# Honeypot field that people never see; answer as if sent.
		return {"ok": True}
	try:
		values = clean_enquiry(name, email, enquiry_type, message, reference)
	except ValueError as error:
		frappe.throw(_(str(error)), title=_("Check your message"))
	frappe.sendmail(
		recipients=[support_email()],
		reply_to=values["email"],
		subject=f"[Examic contact] {values['enquiry_type']}: {values['name']}",
		message=email_body(values),
		delayed=True,
	)
	return {"ok": True}
