"""Import offline Contract flashcard JSON (no OpenRouter)."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import frappe

MODULE = "LMOD-00526"


def _norm(text: str, strip_tags: bool = False) -> str:
	value = html.unescape(text or "")
	if strip_tags:
		value = re.sub(r"<[^>]*>", " ", value)
	return re.sub(r"\s+", " ", value).strip()


def import_chapter_json(path: str, chapter_profile: str, publish: int = 1) -> dict:
	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	plain = _norm(profile.notes_html or "", strip_tags=True)
	items = json.loads(Path(path).read_text(encoding="utf-8"))
	accepted = []
	rejected = []
	for item in items:
		front = (item.get("front") or "").strip()
		back = (item.get("back") or "").strip()
		quote = _norm(item.get("source_quote") or "")
		if not front or not back or not quote or quote not in plain:
			rejected.append(
				{
					"front": front[:100],
					"quote": quote[:120],
					"reason": "missing or quote not in notes",
				}
			)
			continue
		accepted.append(item)

	status = "Published" if int(publish) else "Under Review"
	created = 0
	for item in accepted:
		doc = frappe.get_doc(
			{
				"doctype": "Learning Flashcard",
				"learning_module": MODULE,
				"course_chapter": profile.course_chapter,
				"concept": (item.get("concept") or "").strip(),
				"front": item["front"].strip(),
				"back": item["back"].strip(),
				"difficulty": item.get("difficulty") or "Medium",
				"source_reference": (item.get("source_reference") or f"{profile.chapter_title} notes").strip(),
				"source_quote": _norm(item["source_quote"]),
				"revision": 1,
				"ai_generated": 0,
				"status": status,
			}
		)
		doc.insert(ignore_permissions=True)
		created += 1

	from aimaticlearning.lms_learning.course_presentation import _ensure_flashcard_lesson

	_ensure_flashcard_lesson(profile, "contract-law")
	module = frappe.get_doc("Learning Module Config", MODULE)
	module.refresh_counts()
	module.save(ignore_permissions=True)
	frappe.db.commit()
	return {
		"chapter": profile.chapter_title,
		"created": created,
		"rejected": rejected,
		"status": status,
	}
