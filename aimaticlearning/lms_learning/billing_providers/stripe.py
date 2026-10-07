"""Stripe: hosted Checkout, customer portal and signed webhooks, over plain HTTPS.

Docs saved in docs/vendor/stripe/. Card details never reach this server. Keys come from
Examic Billing Settings (Password fields), never from code.
"""

from __future__ import annotations

import hashlib
import hmac
import time

import frappe
import requests

from aimaticlearning.lms_learning.billing_providers.base import PaymentProvider

API = "https://api.stripe.com/v1"
TOLERANCE_SECONDS = 300
MIN_TRIAL_END_SECONDS = 49 * 3600  # Checkout needs trial_end at least 48 hours ahead
PLAN_MODE = {"Monthly": "subscription", "3-Month": "payment"}


def parse_signature_header(header: str) -> tuple[int | None, list[str]]:
	timestamp, signatures = None, []
	for part in (header or "").split(","):
		key, _, value = part.strip().partition("=")
		if key == "t" and value.isdigit():
			timestamp = int(value)
		elif key == "v1" and value:
			signatures.append(value)
	return timestamp, signatures


def verify_signature(payload: bytes, header: str, secret: str, now: float | None = None,
		tolerance: int = TOLERANCE_SECONDS) -> bool:
	"""Stripe signs `{timestamp}.{raw body}` with HMAC SHA-256 using the endpoint secret."""
	timestamp, signatures = parse_signature_header(header)
	if not secret or timestamp is None or not signatures:
		return False
	if abs((now if now is not None else time.time()) - timestamp) > tolerance:
		return False
	expected = hmac.new(secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256).hexdigest()
	return any(hmac.compare_digest(expected, sig) for sig in signatures)


def interpret_event(event: dict) -> dict:
	"""Turn a Stripe event into one action. Pure, so it is easy to test.

	Only `invoice.paid` extends a subscription and only a paid Checkout in payment mode
	extends a one-off plan, so a first invoice is never counted twice.
	"""
	kind = event.get("type", "")
	obj = (event.get("data") or {}).get("object") or {}
	if kind == "checkout.session.completed":
		meta = obj.get("metadata") or {}
		base = {"user": obj.get("client_reference_id") or meta.get("user"), "plan": meta.get("plan"),
			"customer": obj.get("customer"), "subscription": obj.get("subscription")}
		if obj.get("mode") == "payment" and obj.get("payment_status") == "paid":
			return {**base, "action": "pay", "amount": (obj.get("amount_total") or 0) / 100,
				"reference": obj.get("payment_intent") or obj.get("id")}
		if obj.get("mode") == "subscription":
			return {**base, "action": "link"}
		return {"action": "ignore"}
	if kind == "invoice.paid":
		amount = (obj.get("amount_paid") or 0) / 100
		meta = (obj.get("subscription_details") or {}).get("metadata") or {}
		if amount <= 0:
			return {"action": "ignore"}
		return {"action": "pay", "plan": "Monthly", "user": meta.get("user"), "customer": obj.get("customer"),
			"subscription": obj.get("subscription"), "amount": amount, "reference": obj.get("id")}
	if kind == "invoice.payment_failed":
		meta = (obj.get("subscription_details") or {}).get("metadata") or {}
		return {"action": "failed", "user": meta.get("user"), "customer": obj.get("customer"),
			"message": "Your card payment did not go through. Update your card to keep your access."}
	if kind == "customer.subscription.deleted":
		return {"action": "cancelled", "customer": obj.get("customer"), "subscription": obj.get("id"),
			"user": (obj.get("metadata") or {}).get("user")}
	return {"action": "ignore"}


def _post(path: str, data: dict, secret: str) -> dict:
	try:
		response = requests.post(f"{API}{path}", data=data, auth=(secret, ""), timeout=20)
		body = response.json()
	except Exception:
		frappe.log_error(title="Stripe request failed", message=path)
		frappe.throw("The payment service could not be reached. Try again shortly.")
	if response.status_code >= 400:
		frappe.log_error(title="Stripe error", message=f"{path} {response.status_code} {body.get('error', {}).get('message')}")
		frappe.throw("The payment service refused the request. Please email support.")
	return body


def trial_end_timestamp(trial_ends_on, now: float | None = None) -> int | None:
	"""First charge the day after the free month ends, if Stripe allows it (>= 48h ahead)."""
	if not trial_ends_on:
		return None
	from frappe.utils import add_days, getdate
	import calendar
	first_charge = getdate(add_days(trial_ends_on, 1))
	stamp = calendar.timegm(first_charge.timetuple())
	return stamp if stamp - (now if now is not None else time.time()) >= MIN_TRIAL_END_SECONDS else None


class StripeProvider(PaymentProvider):
	name = "Stripe"

	def is_ready(self, cfg: dict) -> bool:
		return bool(cfg.get("stripe_secret_key") and cfg.get("stripe_monthly_price_id") and cfg.get("stripe_three_month_price_id"))

	def start_payment(self, user: str, email: str, plan: str, cfg: dict, subscription: dict) -> dict:
		price = cfg["stripe_monthly_price_id"] if plan == "Monthly" else cfg["stripe_three_month_price_id"]
		site = frappe.utils.get_url()
		data = {
			"mode": PLAN_MODE[plan],
			"line_items[0][price]": price,
			"line_items[0][quantity]": 1,
			"client_reference_id": user,
			"metadata[user]": user,
			"metadata[plan]": plan,
			"success_url": f"{site}/billing?paid=1",
			"cancel_url": f"{site}/billing",
		}
		if subscription.get("stripe_customer"):
			data["customer"] = subscription["stripe_customer"]
		else:
			data["customer_email"] = email
		if cfg.get("stripe_automatic_tax"):
			data["automatic_tax[enabled]"] = "true"
			data["billing_address_collection"] = "required"
			if subscription.get("stripe_customer"):
				data["customer_update[address]"] = "auto"
		if plan == "Monthly":
			data["subscription_data[metadata][user]"] = user
			trial_end = trial_end_timestamp(subscription.get("trial_ends_on"))
			if trial_end:
				data["subscription_data[trial_end]"] = trial_end
		else:
			data["payment_intent_data[metadata][user]"] = user
		session = _post("/checkout/sessions", data, cfg["stripe_secret_key"])
		return {"url": session["url"]}

	def portal_url(self, customer: str, cfg: dict) -> str:
		session = _post("/billing_portal/sessions", {"customer": customer, "return_url": f"{frappe.utils.get_url()}/billing"}, cfg["stripe_secret_key"])
		return session["url"]
