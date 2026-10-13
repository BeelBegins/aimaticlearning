"""Student live chat. One thread per student. Staff reply from Desk."""

from __future__ import annotations

from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import get_url, now_datetime, strip_html

from aimaticlearning.lms_learning.study_settings import live_chat_enabled, live_chat_open, public_features
from aimaticlearning.lms_learning.utils import throw_access_denied

THREAD = "Examic Live Chat"
MAX_MESSAGE_LENGTH = 2_000
STAFF_ROLES = {"System Manager", "LMS Moderator", "LMS Administrator", "Administrator"}


def is_staff(user: str | None = None) -> bool:
	roles = set(frappe.get_roles(user) if user else frappe.get_roles())
	return bool(roles & STAFF_ROLES)


def clean_message(value: str) -> str:
	return " ".join(strip_html(str(value or "")).split())[:MAX_MESSAGE_LENGTH].strip()


def chat_state(doc=None) -> dict:
	features = public_features()
	messages = _public_messages(doc) if doc is not None and features["live_chat_enabled"] else []
	return {
		"enabled": features["live_chat_enabled"],
		"open": features["live_chat_open"],
		"greeting": features["live_chat_greeting"],
		"offline_message": features["live_chat_offline_message"],
		"hours": features["live_chat_hours"],
		"messages": messages,
	}


@frappe.whitelist()
def get_live_chat() -> dict:
	if frappe.session.user == "Guest":
		throw_access_denied()
	return chat_state(_own_thread())


@frappe.whitelist()
def post_live_chat_message(message: str, course: str | None = None, lesson_title: str | None = None) -> dict:
	if frappe.session.user == "Guest":
		throw_access_denied()
	if not live_chat_enabled():
		frappe.throw(_("Live chat is turned off."), frappe.ValidationError)
	if not live_chat_open():
		frappe.throw(_("Live chat is closed right now."), frappe.ValidationError)
	body = clean_message(message)
	if not body:
		frappe.throw(_("Enter a message first."), frappe.ValidationError)
	user = frappe.session.user
	doc, was_waiting = _thread_for_post(user)
	if doc.student != user:
		throw_access_denied()
	doc.append(
		"messages",
		{"sender": user, "role": "Student", "body": body, "sent_at": now_datetime()},
	)
	doc.status = "Waiting"
	doc.course = clean_message(course or "")[:140]
	doc.lesson_title = clean_message(lesson_title or "")[:140]
	doc.last_message = body[:140]
	doc.last_message_at = now_datetime()
	_save_thread(doc)
	publish_thread(doc.name, doc.student)
	if not was_waiting:
		_alert_waiting(user)
	return chat_state(doc)


def staff_reply(doc, body: str) -> dict:
	if not is_staff():
		frappe.throw(_("Not permitted."), frappe.PermissionError)
	text = clean_message(body)
	if not text:
		frappe.throw(_("Enter a reply first."), frappe.ValidationError)
	doc.append(
		"messages",
		{"sender": frappe.session.user, "role": "Staff", "body": text, "sent_at": now_datetime()},
	)
	doc.status = "Open"
	doc.last_message = text[:140]
	doc.last_message_at = now_datetime()
	doc.save(ignore_permissions=True)
	publish_thread(doc.name, doc.student)
	return {"ok": True}


def publish_thread(name: str, student: str) -> None:
	payload = {"thread": name}
	try:
		frappe.publish_realtime("examic_live_chat", payload, user=student)
		frappe.publish_realtime("examic_live_chat", payload, room="examic_support")
	except Exception:
		frappe.log_error(title="Live chat realtime failed")


def _own_thread():
	user = frappe.session.user
	try:
		found = frappe.db.exists(THREAD, user)
	except Exception:
		return None
	if not found:
		return None
	doc = frappe.get_doc(THREAD, user)
	if doc.student != user:
		throw_access_denied()
	return doc


def _thread_for_post(user: str):
	try:
		found = frappe.db.exists(THREAD, user)
	except Exception:
		frappe.log_error(title="Live chat save failed")
		frappe.throw(_("Live chat is unavailable right now."), frappe.ValidationError)
	if found:
		doc = frappe.get_doc(THREAD, user)
		return doc, doc.status == "Waiting"
	return frappe.get_doc({"doctype": THREAD, "student": user, "status": "Open"}), False


def _save_thread(doc) -> None:
	try:
		if doc.is_new():
			doc.insert(ignore_permissions=True)
		else:
			doc.save(ignore_permissions=True)
	except Exception:
		frappe.log_error(title="Live chat save failed")
		frappe.throw(_("Live chat is unavailable right now."), frappe.ValidationError)


def _alert_waiting(student: str) -> None:
	try:
		from aimaticlearning.lms_learning.discord_alerts import notify

		link = get_url("/app/examic-live-chat/" + quote(student, safe=""))
		notify(
			"live_chat",
			title="New live chat message",
			description=f"{student} is waiting for a reply. {link}",
			dedupe_key=f"live_chat:{student}",
		)
	except Exception:
		frappe.log_error(title="Discord alert failed")


def _public_messages(doc) -> list[dict]:
	rows = []
	for row in getattr(doc, "messages", None) or []:
		body = str(getattr(row, "body", "") or "").strip()
		role = getattr(row, "role", "") or ""
		if not body or role not in ("Student", "Staff"):
			continue
		rows.append({"role": role, "body": body[:MAX_MESSAGE_LENGTH], "sent_at": str(getattr(row, "sent_at", "") or "")})
	return rows
