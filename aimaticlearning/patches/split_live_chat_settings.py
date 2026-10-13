import frappe

LIVE_CHAT_FIELDS = (
	"live_chat_enabled",
	"live_chat_greeting",
	"live_chat_offline_message",
	"live_chat_schedule_enabled",
	"live_chat_timezone",
	"live_chat_start",
	"live_chat_end",
	"live_chat_monday",
	"live_chat_tuesday",
	"live_chat_wednesday",
	"live_chat_thursday",
	"live_chat_friday",
	"live_chat_saturday",
	"live_chat_sunday",
)


def execute():
	"""Copy live chat onto its own record and show the original Study Buddy prompt."""
	from aimaticlearning.lms_learning.study_settings import (
		DEFAULT_HELPFUL_TEXT,
		DEFAULT_HELPFUL_WRAPPER,
		DEFAULT_TUTOR_PROMPT,
	)

	if frappe.db.exists("DocType", "Examic Study Settings"):
		study = frappe.get_single("Examic Study Settings")
		changed = False
		if not (study.get("system_prompt") or "").strip():
			study.system_prompt = DEFAULT_TUTOR_PROMPT
			changed = True
		if not (study.get("helpful_wrapper") or "").strip():
			study.helpful_wrapper = DEFAULT_HELPFUL_WRAPPER
			changed = True
		if not (study.get("helpful_text") or "").strip():
			study.helpful_text = DEFAULT_HELPFUL_TEXT
			changed = True
		if changed:
			study.save(ignore_permissions=True)
	else:
		study = None

	if not frappe.db.exists("DocType", "Examic Live Chat Settings") or study is None:
		return
	chat = frappe.get_single("Examic Live Chat Settings")
	for field in LIVE_CHAT_FIELDS:
		chat.set(field, study.get(field))
	chat.save(ignore_permissions=True)
