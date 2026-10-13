"""Staff Discord alerts. Failures are logged and never shown to students."""

from __future__ import annotations

import requests

import frappe
from aimaticlearning.lms_learning.study_settings import flag, load_settings, webhook_url

ALERT_FIELDS = {
	"signup": "alert_signup",
	"payment_confirmed": "alert_payment_confirmed",
	"payment_needs_review": "alert_payment_review",
	"access_locked": "alert_access_locked",
	"study_buddy_failure": "alert_study_buddy_failure",
	"live_chat": "alert_live_chat",
}
DEDUPE_SECONDS = 600


def build_payload(title: str, description: str) -> dict:
	clean_title = " ".join(str(title or "").split())[:200] or "Examic Study"
	clean_description = str(description or "").strip()[:1500]
	return {
		"content": clean_title,
		"embeds": [{"title": clean_title, "description": clean_description, "color": 2061820}],
	}


def notify(event: str, *, title: str, description: str, dedupe_key: str) -> None:
	try:
		_notify(event, title=title, description=description, dedupe_key=dedupe_key)
	except Exception:
		frappe.log_error(title="Discord alert failed")


def send_test_alert() -> dict:
	if "System Manager" not in set(frappe.get_roles()):
		frappe.throw(frappe._("Not permitted."), frappe.PermissionError)
	doc = load_settings()
	url = webhook_url(doc)
	if not url:
		return {"ok": False, "message": "Add a Discord webhook first."}
	if not _post(url, build_payload("Examic Study", "Test alert from Examic Study Settings.")):
		return {"ok": False, "message": "Discord did not accept the alert."}
	return {"ok": True, "message": "Test alert sent."}


def _notify(event: str, *, title: str, description: str, dedupe_key: str) -> None:
	field = ALERT_FIELDS.get(event)
	if not field:
		return
	doc = load_settings()
	if doc is None or not flag(doc, "discord_alerts_enabled", False) or not flag(doc, field, False):
		return
	url = webhook_url(doc)
	if not url:
		return
	cache_key = f"examic_discord:{dedupe_key}"
	if _seen(cache_key):
		return
	if _post(url, build_payload(title, description)):
		_mark(cache_key)


def _post(url: str, payload: dict) -> bool:
	try:
		response = requests.post(url, json=payload, timeout=5, allow_redirects=False)
	except requests.RequestException:
		frappe.log_error(title="Discord alert failed")
		return False
	if response.status_code >= 300:
		frappe.log_error(title="Discord alert failed", message=f"HTTP {response.status_code}")
		return False
	return True


def _cache():
	getter = getattr(frappe, "cache", None)
	if not callable(getter):
		return None
	try:
		return getter()
	except Exception:
		return None


def _seen(key: str) -> bool:
	cache = _cache()
	if cache is None:
		return False
	try:
		return bool(cache.get_value(key))
	except Exception:
		return False


def _mark(key: str) -> None:
	cache = _cache()
	if cache is None:
		return
	try:
		cache.set_value(key, "1", expires_in_sec=DEDUPE_SECONDS)
	except Exception:
		return
