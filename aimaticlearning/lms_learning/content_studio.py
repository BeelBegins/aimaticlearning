from __future__ import annotations

import json
import re
from html import escape, unescape

import frappe
from frappe import _
from frappe.utils import cint

from aimaticlearning.lms_learning.content_generation import (
	_link_question_to_quiz,
	_validate_flashcard_source,
)
from aimaticlearning.lms_learning.course_presentation import _ensure_flashcard_lesson, _profile_sort_key
from aimaticlearning.lms_learning.import_pipeline import _ensure_chapter_quiz
from aimaticlearning.lms_learning.exam_surface import is_exam_course
from aimaticlearning.lms_learning.outline_sync import (
	ensure_quiz_lesson,
	link_chapter_to_course,
	link_lesson_to_chapter,
)
from aimaticlearning.lms_learning.sqe_pathway import FLK1_SUBJECTS, FLK2_SUBJECTS

CONTENT_ROLES = ("System Manager", "LMS Content Reviewer", "Course Creator")
MAX_OPTIONS = 10
MIN_OPTIONS = 2
DEFAULT_MCQ_OPTIONS = 5
CHAPTER_TITLE_MAX = 140
FIRST_HEADING_RE = re.compile(r"(<(h[1-6])(?:\s[^>]*)?>)(.*?)(</\2>)", re.I | re.S)
QL_EDITOR_WRAP_RE = re.compile(
	r'^\s*<div class="ql-editor(?:\s[^"]*)?"[^>]*>(.*)</div>\s*$',
	re.I | re.S,
)
EMPTY_QUILL_MARKUP_RE = re.compile(r"(?i)</?p>|<br\s*/?>|&nbsp;")
TITLE_PREFIXES = (
	"Notes — ",
	"Notes – ",
	"Notes - ",
	"Draft notes — ",
	"Draft notes – ",
	"Draft notes - ",
	"Chapter MCQ — ",
	"Chapter MCQ – ",
	"Chapter MCQ - ",
	"Flashcards — ",
	"Flashcards – ",
	"Flashcards - ",
	"Chapter — ",
	"Chapter – ",
	"Chapter - ",
)
FLASHCARD_STATUSES = ("Draft", "Under Review", "Published", "Retired")
FLASHCARD_STUDIO_FIELDS = [
	"name",
	"front",
	"back",
	"concept",
	"difficulty",
	"source_reference",
	"source_quote",
	"status",
	"revision",
]
DUPLICATE_STEM_SUFFIX = " (copy)"


class ContentStudioError(Exception):
	pass


def require_content_role() -> None:
	frappe.only_for(CONTENT_ROLES)


def default_mcq_options() -> list[dict]:
	return [{"text": "", "is_correct": 0, "explanation": ""} for _ in range(DEFAULT_MCQ_OPTIONS)]


def annotate_studio_modules(rows: list) -> list:
	flk1 = {item["course"] for item in FLK1_SUBJECTS}
	flk2 = {item["course"] for item in FLK2_SUBJECTS}
	cleaned = []
	for row in rows or []:
		item = dict(row)
		course = item.get("lms_course")
		if is_exam_course(course):
			continue
		if course in flk1:
			item["pathway"] = "FLK1"
		elif course in flk2:
			item["pathway"] = "FLK2"
		else:
			item["pathway"] = "Other"
		cleaned.append(item)
	rank = {"FLK1": 0, "FLK2": 1, "Other": 2}
	cleaned.sort(key=lambda item: (rank.get(item.get("pathway"), 9), (item.get("title") or "").lower()))
	return cleaned


def notes_write_values(html: str | None) -> dict:
	"""Learner notes lesson payload. Never put EditorJS in `content`."""
	return {"body": sanitize_studio_notes_html(html), "content": ""}


def sanitize_studio_notes_html(html: str | None) -> str:
	"""Strip Quill's editor wrapper and treat empty Quill chrome as blank notes."""
	text = html or ""
	match = QL_EDITOR_WRAP_RE.match(text)
	if match:
		text = (match.group(1) or "").strip()
	else:
		text = text.strip()
	if not EMPTY_QUILL_MARKUP_RE.sub(" ", text).strip():
		return ""
	return text


def notes_compare_key(html: str | None) -> str:
	"""Stable compare for Studio working copy vs learner body (ignore Quill chrome / whitespace)."""
	text = sanitize_studio_notes_html(html)
	text = re.sub(r"\s+", " ", text)
	return text.strip()


def flashcard_status_counts(learning_module: str, course_chapter: str | None) -> dict:
	"""Published / Under Review / Draft / Retired counts for chapter list chips."""
	counts = {status: 0 for status in FLASHCARD_STATUSES}
	if not course_chapter:
		return counts
	for row in frappe.get_all(
		"Learning Flashcard",
		filters={"learning_module": learning_module, "course_chapter": course_chapter},
		fields=["status"],
		limit_page_length=5000,
	):
		status = row.status or "Draft"
		if status in counts:
			counts[status] += 1
	return counts


def notes_publish_state(
	notes_html: str | None,
	learner_body: str | None,
	*,
	notes_lesson: str | None = None,
) -> dict:
	"""Describe Studio notes_html vs learner Course Lesson.body publish/sync state."""
	studio = sanitize_studio_notes_html(notes_html)
	learner = sanitize_studio_notes_html(learner_body)
	studio_chars = len(studio)
	learner_chars = len(learner)
	if not (notes_lesson or "").strip():
		status = "missing_lesson"
		label = "No notes lesson"
	elif not studio and not learner:
		status = "empty"
		label = "Empty notes"
	elif notes_compare_key(studio) == notes_compare_key(learner):
		status = "in_sync"
		label = "Notes published"
	else:
		status = "out_of_sync"
		label = "Out of sync"
	return {
		"status": status,
		"label": label,
		"in_sync": status == "in_sync",
		"studio_chars": studio_chars,
		"learner_chars": learner_chars,
		"has_notes_lesson": bool((notes_lesson or "").strip()),
	}


def _learner_notes_body(notes_lesson: str | None) -> str:
	if not (notes_lesson or "").strip():
		return ""
	return frappe.db.get_value("Course Lesson", notes_lesson, "body") or ""


def _write_profile_notes_html(profile, html: str, *, bump_revision: bool = True) -> int:
	"""Persist notes_html despite DocType read_only=1 (Document.save skips it)."""
	html = sanitize_studio_notes_html(html)
	current = profile.notes_html or ""
	revision = cint(profile.source_revision)
	if bump_revision and current != html:
		revision += 1
	frappe.db.set_value(
		"Learning Chapter Profile",
		profile.name,
		{"notes_html": html, "source_revision": revision},
		update_modified=True,
	)
	profile.notes_html = html
	profile.source_revision = revision
	return revision


def normalize_chapter_title(title: str | None) -> str:
	return re.sub(r"\s+", " ", (title or "").strip())


def validate_chapter_title(title: str) -> None:
	if not title:
		raise ContentStudioError("Chapter heading cannot be empty.")
	if len(title) > CHAPTER_TITLE_MAX:
		raise ContentStudioError("Chapter heading is too long (140 characters).")


def validate_chapter_removal_confirm(chapter_title: str, typed: str | None) -> None:
	wanted = normalize_chapter_title(chapter_title)
	if not wanted:
		raise ContentStudioError("Chapter heading cannot be empty.")
	if normalize_chapter_title(typed) != wanted:
		raise ContentStudioError("Type the exact chapter heading to remove it.")


def heading_inner_text(html_fragment: str) -> str:
	return unescape(re.sub(r"<[^>]+>", "", html_fragment or "")).strip()


def replace_matching_first_heading(
	html: str | None, old_titles: list[str], new_title: str
) -> tuple[str, bool]:
	text = html or ""
	match = FIRST_HEADING_RE.search(text)
	if not match:
		return text, False
	current = heading_inner_text(match.group(3))
	wanted = {normalize_chapter_title(value) for value in old_titles if normalize_chapter_title(value)}
	if normalize_chapter_title(current) not in wanted:
		return text, False
	updated = (
		text[: match.start()]
		+ match.group(1)
		+ escape(new_title)
		+ match.group(4)
		+ text[match.end() :]
	)
	return updated, True


def retitle_display(current: str | None, old_titles: list[str], new_title: str) -> str | None:
	current = (current or "").strip()
	new_title = normalize_chapter_title(new_title)
	if not current or not new_title:
		return None
	for old in old_titles:
		old = normalize_chapter_title(old)
		if not old or old == new_title:
			continue
		if current == old:
			return new_title
		for prefix in TITLE_PREFIXES:
			if current == f"{prefix}{old}":
				return f"{prefix}{new_title}"
		if current == f"{old} — Chapter MCQ":
			return f"{new_title} — Chapter MCQ"
		if current == f"{old} – Chapter MCQ":
			return f"{new_title} – Chapter MCQ"
		if current == f"{old} - Chapter MCQ":
			return f"{new_title} - Chapter MCQ"
	return None


def validate_flashcard_payload(front: str | None, back: str | None, status: str | None) -> None:
	if not (front or "").strip() or not (back or "").strip():
		raise ContentStudioError("Each flashcard needs a front and a back.")
	if (status or "Draft") not in FLASHCARD_STATUSES:
		raise ContentStudioError("Unknown flashcard status.")


def normalize_mcq_options(options: list | None) -> list[dict]:
	cleaned: list[dict] = []
	for option in options or []:
		if not isinstance(option, dict):
			continue
		text = (option.get("text") or "").strip()
		if not text:
			continue
		cleaned.append(
			{
				"text": text,
				"is_correct": bool(cint(option.get("is_correct"))),
				"explanation": (option.get("explanation") or "").strip(),
			}
		)
	return cleaned


def validate_mcq_payload(question: str | None, options: list[dict]) -> None:
	if not (question or "").strip():
		raise ContentStudioError("Each MCQ needs a question stem.")
	if len(options) < MIN_OPTIONS:
		raise ContentStudioError(f"Each MCQ needs at least {MIN_OPTIONS} options.")
	if len(options) > MAX_OPTIONS:
		raise ContentStudioError(f"Each MCQ can have at most {MAX_OPTIONS} options.")
	correct = sum(1 for option in options if option.get("is_correct"))
	if correct != 1:
		raise ContentStudioError(
			"Mark exactly one option as correct. Do not assume option A is the answer."
		)


def reorder_question_names(names: list[str], target: str, direction: str) -> list[str]:
	ordered = [name for name in names if name]
	if target not in ordered:
		raise ContentStudioError("That question is not on this chapter quiz.")
	move = (direction or "").strip().lower()
	if move not in ("up", "down"):
		raise ContentStudioError("Move direction must be up or down.")
	idx = ordered.index(target)
	swap_with = idx - 1 if move == "up" else idx + 1
	if swap_with < 0 or swap_with >= len(ordered):
		return ordered
	ordered[idx], ordered[swap_with] = ordered[swap_with], ordered[idx]
	return ordered


def reorder_outline_names(names: list[str], target: str, direction: str) -> list[str]:
	ordered = [name for name in names if name]
	if target not in ordered:
		raise ContentStudioError("That chapter is not on this subject's outline.")
	move = (direction or "").strip().lower()
	if move not in ("up", "down"):
		raise ContentStudioError("Move direction must be up or down.")
	idx = ordered.index(target)
	swap_with = idx - 1 if move == "up" else idx + 1
	if swap_with < 0 or swap_with >= len(ordered):
		return ordered
	ordered[idx], ordered[swap_with] = ordered[swap_with], ordered[idx]
	return ordered


def insert_outline_name(names: list[str], new_name: str, outline_idx: int | None) -> list[str]:
	ordered = [name for name in names if name and name != new_name]
	if not new_name:
		return ordered
	if outline_idx is None or outline_idx == "":
		ordered.append(new_name)
		return ordered
	idx = cint(outline_idx)
	if idx < 1:
		idx = 1
	if idx > len(ordered) + 1:
		idx = len(ordered) + 1
	ordered.insert(idx - 1, new_name)
	return ordered


def duplicate_question_stem(question: str | None) -> str:
	stem = (question or "").strip()
	if not stem:
		raise ContentStudioError("Cannot duplicate an empty question.")
	if stem.endswith(DUPLICATE_STEM_SUFFIX):
		return stem
	return f"{stem}{DUPLICATE_STEM_SUFFIX}"


def question_signature(question: str, options: list[dict]) -> str:
	parts = [(question or "").strip()]
	for option in options:
		correct = "1" if option.get("is_correct") else "0"
		parts.append(f"{option.get('text') or ''}|{correct}|{option.get('explanation') or ''}")
	return "\n".join(parts)


def lms_question_fields(question: str, options: list[dict]) -> dict:
	fields = {
		"question": question.strip(),
		"type": "Choices",
		"multiple": 0,
	}
	for idx in range(1, MAX_OPTIONS + 1):
		fields[f"option_{idx}"] = ""
		fields[f"is_correct_{idx}"] = 0
		fields[f"explanation_{idx}"] = ""
	for idx, option in enumerate(options, start=1):
		fields[f"option_{idx}"] = option["text"]
		fields[f"is_correct_{idx}"] = 1 if option.get("is_correct") else 0
		fields[f"explanation_{idx}"] = option.get("explanation") or ""
	return fields


def options_from_lms_question(doc) -> list[dict]:
	options: list[dict] = []
	for idx in range(1, MAX_OPTIONS + 1):
		text = (doc.get(f"option_{idx}") or "").strip()
		if not text:
			continue
		options.append(
			{
				"text": text,
				"is_correct": bool(cint(doc.get(f"is_correct_{idx}"))),
				"explanation": doc.get(f"explanation_{idx}") or "",
			}
		)
	return options


def _parse_json(value):
	if value is None or value == "":
		return None
	if isinstance(value, (dict, list)):
		return value
	return json.loads(value)


def _throw(error: ContentStudioError) -> None:
	frappe.throw(_(str(error)))


@frappe.whitelist()
def get_studio_tree(learning_module: str | None = None):
	require_content_role()
	if not learning_module:
		modules = annotate_studio_modules(
			frappe.get_all(
				"Learning Module Config",
				fields=[
					"name",
					"title",
					"lms_course",
					"target_chapter_mcq_count",
					"chapter_count",
					"import_status",
				],
				order_by="title asc",
				limit_page_length=200,
			)
		)
		return {"modules": modules}

	module = frappe.get_doc("Learning Module Config", learning_module)
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": learning_module},
		fields=[
			"name",
			"chapter_title",
			"course_chapter",
			"notes_lesson",
			"chapter_quiz",
			"notes_html",
			"mcq_count",
			"source_revision",
		],
		limit_page_length=500,
	)
	outline_by_chapter = {}
	if module.lms_course:
		for rec in frappe.get_all(
			"Chapter Reference",
			filters={"parent": module.lms_course},
			fields=["chapter", "idx"],
			limit_page_length=500,
		):
			outline_by_chapter[rec.chapter] = rec.idx
	profiles.sort(
		key=lambda row: (
			0 if outline_by_chapter.get(row.course_chapter) else 1,
			outline_by_chapter.get(row.course_chapter) or 0,
			_profile_sort_key(row),
		)
	)
	chapter_names = [row.course_chapter for row in profiles if row.course_chapter]
	lms_titles = {}
	if chapter_names:
		for rec in frappe.get_all(
			"Course Chapter",
			filters={"name": ["in", chapter_names]},
			fields=["name", "title"],
			limit_page_length=500,
		):
			lms_titles[rec.name] = rec.title
	chapters = []
	for row in profiles:
		quiz_count = _quiz_question_count(row.chapter_quiz)
		fc_counts = flashcard_status_counts(learning_module, row.course_chapter)
		flashcard_count = sum(fc_counts.get(status, 0) for status in ("Draft", "Under Review", "Published"))
		learner_body = _learner_notes_body(row.notes_lesson)
		notes_state = notes_publish_state(
			row.notes_html, learner_body, notes_lesson=row.notes_lesson
		)
		chapters.append(
			{
				"name": row.name,
				"chapter_title": lms_titles.get(row.course_chapter) or row.chapter_title,
				"course_chapter": row.course_chapter,
				"notes_lesson": row.notes_lesson,
				"chapter_quiz": row.chapter_quiz,
				"notes_chars": len(row.notes_html or ""),
				"learner_notes_chars": notes_state["learner_chars"],
				"notes_status": notes_state["status"],
				"notes_status_label": notes_state["label"],
				"notes_in_sync": notes_state["in_sync"],
				"mcq_count": quiz_count if row.chapter_quiz else cint(row.mcq_count),
				"flashcard_count": flashcard_count,
				"flashcard_published": fc_counts.get("Published", 0),
				"flashcard_under_review": fc_counts.get("Under Review", 0),
				"flashcard_draft": fc_counts.get("Draft", 0),
				"flashcard_retired": fc_counts.get("Retired", 0),
				"source_revision": row.source_revision,
				"outline_idx": outline_by_chapter.get(row.course_chapter),
			}
		)
	return {
		"learning_module": module.name,
		"title": module.title,
		"lms_course": module.lms_course,
		"target_chapter_mcq_count": cint(module.target_chapter_mcq_count) or 20,
		"import_status": module.import_status,
		"chapters": chapters,
	}


@frappe.whitelist()
def get_chapter_bundle(chapter_profile: str):
	require_content_role()
	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	module = frappe.get_doc("Learning Module Config", profile.learning_module)
	questions = _chapter_questions(profile)
	course_chapter_title = (
		frappe.db.get_value("Course Chapter", profile.course_chapter, "title")
		if profile.course_chapter
		else None
	)
	learner_body = _learner_notes_body(profile.notes_lesson)
	notes_state = notes_publish_state(
		profile.notes_html, learner_body, notes_lesson=profile.notes_lesson
	)
	fc_counts = flashcard_status_counts(profile.learning_module, profile.course_chapter)
	return {
		"name": profile.name,
		"chapter_title": course_chapter_title or profile.chapter_title,
		"profile_chapter_title": profile.chapter_title,
		"learning_module": profile.learning_module,
		"module_title": module.title,
		"lms_course": module.lms_course,
		"course_chapter": profile.course_chapter,
		"notes_lesson": profile.notes_lesson,
		"chapter_quiz": profile.chapter_quiz,
		"notes_html": profile.notes_html or "",
		"learner_notes_html": learner_body,
		"notes_status": notes_state["status"],
		"notes_status_label": notes_state["label"],
		"notes_in_sync": notes_state["in_sync"],
		"notes_studio_chars": notes_state["studio_chars"],
		"notes_learner_chars": notes_state["learner_chars"],
		"source_revision": profile.source_revision,
		"mcq_count": len(questions),
		"target_chapter_mcq_count": cint(module.target_chapter_mcq_count) or 20,
		"flashcard_published": fc_counts.get("Published", 0),
		"flashcard_under_review": fc_counts.get("Under Review", 0),
		"flashcard_draft": fc_counts.get("Draft", 0),
		"flashcard_retired": fc_counts.get("Retired", 0),
		"preview_url": f"/learning-notes/{profile.name}",
		"flashcards_url": f"/learning-flashcards?chapter_profile={profile.name}",
		"questions": questions,
		"flashcards": _chapter_flashcards(profile),
	}


@frappe.whitelist()
def save_chapter_notes(chapter_profile: str, notes_html: str | None = None):
	require_content_role()
	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	html = sanitize_studio_notes_html(notes_html)
	revision = _write_profile_notes_html(profile, html)

	lesson_written = False
	skipped_quiz_lesson = False
	if profile.notes_lesson:
		quiz_id = frappe.db.get_value("Course Lesson", profile.notes_lesson, "quiz_id") or ""
		if (quiz_id or "").strip():
			skipped_quiz_lesson = True
		else:
			values = notes_write_values(html)
			frappe.db.set_value(
				"Course Lesson",
				profile.notes_lesson,
				{"body": values["body"], "content": values["content"]},
			)
			lesson_written = True

	learner_body = html if lesson_written else _learner_notes_body(profile.notes_lesson)
	notes_state = notes_publish_state(html, learner_body, notes_lesson=profile.notes_lesson)
	return {
		"ok": True,
		"source_revision": revision,
		"lesson_written": lesson_written,
		"skipped_quiz_lesson": skipped_quiz_lesson,
		"notes_status": notes_state["status"],
		"notes_status_label": notes_state["label"],
		"notes_in_sync": notes_state["in_sync"],
	}


@frappe.whitelist()
def sync_notes_to_learner(chapter_profile: str):
	"""Push Studio working copy (notes_html) onto the learner notes lesson body."""
	require_content_role()
	try:
		profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
		if not profile.notes_lesson:
			raise ContentStudioError("This chapter has no notes lesson to publish into.")
		quiz_id = frappe.db.get_value("Course Lesson", profile.notes_lesson, "quiz_id") or ""
		if (quiz_id or "").strip():
			raise ContentStudioError("Cannot publish notes onto a quiz-wired lesson.")
		html = sanitize_studio_notes_html(profile.notes_html)
		values = notes_write_values(html)
		frappe.db.set_value(
			"Course Lesson",
			profile.notes_lesson,
			{"body": values["body"], "content": values["content"]},
		)
		notes_state = notes_publish_state(html, values["body"], notes_lesson=profile.notes_lesson)
		return {
			"ok": True,
			"notes_status": notes_state["status"],
			"notes_status_label": notes_state["label"],
			"notes_in_sync": notes_state["in_sync"],
			"learner_notes_html": values["body"],
		}
	except ContentStudioError as error:
		_throw(error)


@frappe.whitelist()
def pull_learner_notes_to_studio(chapter_profile: str):
	"""Replace Studio working copy with the current learner-published body."""
	require_content_role()
	try:
		profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
		if not profile.notes_lesson:
			raise ContentStudioError("This chapter has no notes lesson to pull from.")
		learner_body = sanitize_studio_notes_html(_learner_notes_body(profile.notes_lesson))
		revision = _write_profile_notes_html(profile, learner_body)
		# Re-read learner body so status reflects DB truth, not the in-memory copy.
		db_studio = frappe.db.get_value("Learning Chapter Profile", profile.name, "notes_html") or ""
		db_learner = _learner_notes_body(profile.notes_lesson)
		notes_state = notes_publish_state(
			db_studio, db_learner, notes_lesson=profile.notes_lesson
		)
		return {
			"ok": True,
			"notes_html": sanitize_studio_notes_html(db_studio),
			"source_revision": revision,
			"notes_status": notes_state["status"],
			"notes_status_label": notes_state["label"],
			"notes_in_sync": notes_state["in_sync"],
		}
	except ContentStudioError as error:
		_throw(error)


@frappe.whitelist()
def save_chapter_heading(chapter_profile: str, chapter_title: str):
	require_content_role()
	new_title = normalize_chapter_title(chapter_title)
	try:
		validate_chapter_title(new_title)
	except ContentStudioError as error:
		_throw(error)

	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	course_chapter_title = (
		frappe.db.get_value("Course Chapter", profile.course_chapter, "title")
		if profile.course_chapter
		else None
	)
	old_titles = [
		value
		for value in (profile.chapter_title, course_chapter_title)
		if normalize_chapter_title(value)
	]
	if new_title == normalize_chapter_title(course_chapter_title or profile.chapter_title) and new_title == normalize_chapter_title(
		profile.chapter_title
	):
		return {
			"ok": True,
			"chapter_title": new_title,
			"changed": False,
			"notes_heading_updated": False,
			"retitled": [],
		}

	_assert_heading_available(profile, new_title)

	html, notes_heading_updated = replace_matching_first_heading(
		profile.notes_html, old_titles, new_title
	)
	if notes_heading_updated:
		_write_profile_notes_html(profile, html)
		if profile.notes_lesson:
			quiz_id = frappe.db.get_value("Course Lesson", profile.notes_lesson, "quiz_id") or ""
			if not (quiz_id or "").strip():
				values = notes_write_values(html)
				frappe.db.set_value(
					"Course Lesson",
					profile.notes_lesson,
					{"body": values["body"], "content": values["content"]},
				)

	profile.chapter_title = new_title
	profile.save(ignore_permissions=True)

	if profile.course_chapter:
		frappe.db.set_value("Course Chapter", profile.course_chapter, "title", new_title)

	retitled = _retitle_chapter_surfaces(profile, old_titles, new_title)
	return {
		"ok": True,
		"chapter_title": new_title,
		"changed": True,
		"notes_heading_updated": notes_heading_updated,
		"retitled": retitled,
		"source_revision": profile.source_revision,
	}


@frappe.whitelist()
def save_chapter_mcq(
	chapter_profile: str,
	question: str,
	options: str | list | None = None,
	lms_question: str | None = None,
	concept: str | None = None,
	difficulty: str | None = None,
	source_reference: str | None = None,
	learning_objective: str | None = None,
	question_role: str | None = None,
):
	require_content_role()
	try:
		normalized = normalize_mcq_options(_parse_json(options) or [])
		validate_mcq_payload(question, normalized)
	except ContentStudioError as error:
		_throw(error)

	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	quiz_name = _ensure_profile_quiz(profile)
	fields = lms_question_fields(question, normalized)

	created = False
	if lms_question:
		doc = frappe.get_doc("LMS Question", lms_question)
		previous = question_signature(doc.question, options_from_lms_question(doc))
		doc.update(fields)
		doc.save(ignore_permissions=True)
		question_name = doc.name
	else:
		doc = frappe.get_doc({"doctype": "LMS Question", **fields})
		doc.insert(ignore_permissions=True)
		question_name = doc.name
		created = True
		previous = ""

	current = question_signature(question, normalized)
	meta = _upsert_question_meta(
		profile,
		question_name,
		{
			"concept": concept,
			"difficulty": difficulty or "Medium",
			"source_reference": source_reference,
			"learning_objective": learning_objective,
			"question_role": question_role or "Chapter MCQ",
			"bump_revision": bool(previous) and previous != current,
		},
	)
	_link_question_to_quiz(quiz_name, question_name)
	ensure_quiz_lesson(profile.name)
	_refresh_profile_mcq_count(profile)

	return {
		"ok": True,
		"created": created,
		"lms_question": question_name,
		"meta": meta,
		"chapter_quiz": quiz_name,
		"mcq_count": cint(profile.mcq_count),
		"revision": meta.get("revision"),
	}


@frappe.whitelist()
def unlink_chapter_mcq(chapter_profile: str, lms_question: str):
	require_content_role()
	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	if not profile.chapter_quiz:
		frappe.throw(_("This chapter has no quiz to unlink from."))

	quiz = frappe.get_doc("LMS Quiz", profile.chapter_quiz)
	kept = [row for row in (quiz.questions or []) if row.question != lms_question]
	if len(kept) == len(quiz.questions or []):
		frappe.throw(_("That question is not on this chapter quiz."))
	quiz.set("questions", [])
	for row in kept:
		quiz.append("questions", {"question": row.question, "marks": row.marks or 1})
	quiz.total_marks = len(quiz.questions or [])
	quiz.save(ignore_permissions=True)
	_refresh_profile_mcq_count(profile)
	return {"ok": True, "mcq_count": cint(profile.mcq_count)}


@frappe.whitelist()
def reorder_chapter_mcq(chapter_profile: str, lms_question: str, direction: str):
	require_content_role()
	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	if not profile.chapter_quiz:
		frappe.throw(_("This chapter has no quiz to reorder."))
	quiz = frappe.get_doc("LMS Quiz", profile.chapter_quiz)
	names = [row.question for row in (quiz.questions or []) if row.question]
	try:
		ordered = reorder_question_names(names, lms_question, direction)
	except ContentStudioError as error:
		_throw(error)
	if ordered == names:
		return {"ok": True, "changed": False, "order": ordered}
	marks = {row.question: row.marks or 1 for row in (quiz.questions or [])}
	quiz.set("questions", [])
	for question_name in ordered:
		quiz.append("questions", {"question": question_name, "marks": marks.get(question_name, 1)})
	quiz.save(ignore_permissions=True)
	return {"ok": True, "changed": True, "order": ordered}


@frappe.whitelist()
def duplicate_chapter_mcq(chapter_profile: str, lms_question: str):
	require_content_role()
	source = frappe.get_doc("LMS Question", lms_question)
	options = options_from_lms_question(source)
	try:
		stem = duplicate_question_stem(source.question)
		validate_mcq_payload(stem, options)
	except ContentStudioError as error:
		_throw(error)

	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	quiz_name = _ensure_profile_quiz(profile)
	fields = lms_question_fields(stem, options)
	doc = frappe.get_doc({"doctype": "LMS Question", **fields})
	doc.insert(ignore_permissions=True)

	source_meta = frappe.db.get_value(
		"Learning Question Meta",
		{"lms_question": lms_question},
		["concept", "difficulty", "source_reference", "learning_objective", "question_role"],
		as_dict=True,
	) or {}
	meta = _upsert_question_meta(
		profile,
		doc.name,
		{
			"concept": source_meta.get("concept"),
			"difficulty": source_meta.get("difficulty") or "Medium",
			"source_reference": source_meta.get("source_reference"),
			"learning_objective": source_meta.get("learning_objective"),
			"question_role": source_meta.get("question_role") or "Chapter MCQ",
			"bump_revision": False,
		},
	)
	_link_question_to_quiz(quiz_name, doc.name)
	ensure_quiz_lesson(profile.name)
	_refresh_profile_mcq_count(profile)
	return {
		"ok": True,
		"created": True,
		"lms_question": doc.name,
		"meta": meta,
		"chapter_quiz": quiz_name,
		"mcq_count": cint(profile.mcq_count),
	}


@frappe.whitelist()
def add_studio_course(title: str, short_introduction: str | None = None):
	require_content_role()
	title = normalize_chapter_title(title)
	try:
		validate_chapter_title(title)
	except ContentStudioError as error:
		_throw(error)
	if frappe.db.exists("LMS Course", {"title": title}):
		frappe.throw(_("A course with that title already exists."))
	if frappe.db.exists("Learning Module Config", {"title": title}):
		frappe.throw(_("A learning module with that title already exists."))

	intro = (short_introduction or "").strip() or f"{title} study notes, chapter MCQs, and flashcards."
	course = frappe.get_doc(
		{
			"doctype": "LMS Course",
			"title": title,
			"short_introduction": intro,
			"description": intro,
			"published": 0,
			"upcoming": 0,
			"disable_self_learning": 0,
		}
	)
	course.append("instructors", {"instructor": frappe.session.user})
	course.insert(ignore_permissions=True)

	module = frappe.get_doc(
		{
			"doctype": "Learning Module Config",
			"title": title,
			"lms_course": course.name,
			"target_chapter_mcq_count": 20,
			"module_assessment_count": 150,
			"flashcard_target": 200,
			"import_status": "Not Started",
		}
	)
	module.insert(ignore_permissions=True)
	return {
		"ok": True,
		"learning_module": module.name,
		"lms_course": course.name,
		"published": 0,
	}


@frappe.whitelist()
def add_studio_chapter(learning_module: str, chapter_title: str, outline_idx: int | None = None):
	require_content_role()
	new_title = normalize_chapter_title(chapter_title)
	try:
		validate_chapter_title(new_title)
	except ContentStudioError as error:
		_throw(error)

	module = frappe.get_doc("Learning Module Config", learning_module)
	if not module.lms_course:
		frappe.throw(_("This module is not linked to an LMS Course."))
	course = frappe.get_doc("LMS Course", module.lms_course)
	stub = frappe._dict(
		{
			"name": "new",
			"learning_module": module.name,
			"course_chapter": None,
		}
	)
	_assert_heading_available(stub, new_title)
	if frappe.db.exists("Course Chapter", {"course": course.name, "title": new_title}):
		frappe.throw(_("Another chapter in this course already uses that heading."))

	chapter = frappe.get_doc(
		{
			"doctype": "Course Chapter",
			"title": new_title,
			"course": course.name,
		}
	)
	chapter.insert(ignore_permissions=True)
	link_chapter_to_course(course.name, chapter.name)
	ordered = insert_outline_name(_course_outline_names(course.name), chapter.name, outline_idx)
	_write_course_outline(course.name, ordered)

	notes_html = f'<article class="aimatic-notes"><h2>{escape(new_title)}</h2><p></p></article>'
	values = notes_write_values(notes_html)
	lesson = frappe.get_doc(
		{
			"doctype": "Course Lesson",
			"title": f"Notes — {new_title}",
			"course": course.name,
			"chapter": chapter.name,
			"body": values["body"],
			"content": values["content"],
		}
	)
	lesson.insert(ignore_permissions=True)
	link_lesson_to_chapter(chapter.name, lesson.name)

	quiz_name = _ensure_chapter_quiz(course, chapter.name, new_title)
	profile = frappe.get_doc(
		{
			"doctype": "Learning Chapter Profile",
			"learning_module": module.name,
			"chapter_title": new_title,
			"course_chapter": chapter.name,
			"notes_lesson": lesson.name,
			"chapter_quiz": quiz_name,
			"notes_html": notes_html,
			"source_revision": 1,
			"mcq_count": 0,
		}
	)
	profile.insert(ignore_permissions=True)
	ensure_quiz_lesson(profile.name)
	module.reload()
	module.refresh_counts()
	module.save(ignore_permissions=True)
	return {
		"ok": True,
		"chapter_profile": profile.name,
		"course_chapter": chapter.name,
		"notes_lesson": lesson.name,
		"chapter_quiz": quiz_name,
		"outline_idx": ordered.index(chapter.name) + 1 if chapter.name in ordered else None,
	}


@frappe.whitelist()
def reorder_studio_chapter(chapter_profile: str, direction: str):
	require_content_role()
	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	module = frappe.get_doc("Learning Module Config", profile.learning_module)
	if is_exam_course(module.lms_course):
		frappe.throw(_("Exam sittings cannot be reordered from Content Studio."))
	if not module.lms_course or not profile.course_chapter:
		frappe.throw(_("This chapter is not on a course outline yet."))
	names = _course_outline_names(module.lms_course)
	if profile.course_chapter not in names:
		names.append(profile.course_chapter)
	try:
		ordered = reorder_outline_names(names, profile.course_chapter, direction)
	except ContentStudioError as error:
		_throw(error)
	if ordered == names:
		return {"ok": True, "changed": False, "order": ordered, "outline_idx": names.index(profile.course_chapter) + 1}
	_write_course_outline(module.lms_course, ordered)
	return {
		"ok": True,
		"changed": True,
		"order": ordered,
		"outline_idx": ordered.index(profile.course_chapter) + 1,
	}


@frappe.whitelist()
def remove_studio_chapter(chapter_profile: str, confirm_title: str | None = None):
	require_content_role()
	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	module = frappe.get_doc("Learning Module Config", profile.learning_module)
	if is_exam_course(module.lms_course):
		frappe.throw(_("Exam sittings cannot be removed from Content Studio."))

	course_chapter_title = (
		frappe.db.get_value("Course Chapter", profile.course_chapter, "title")
		if profile.course_chapter
		else None
	)
	heading = course_chapter_title or profile.chapter_title
	try:
		validate_chapter_removal_confirm(heading, confirm_title)
		moved_assessment = _rehome_module_assessment(profile, module)
	except ContentStudioError as error:
		_throw(error)
	chapter_name = profile.course_chapter
	quiz_name = profile.chapter_quiz
	retired_cards = 0
	deleted_lessons = 0

	if chapter_name and module.lms_course:
		_unlink_chapter_from_course(module.lms_course, chapter_name)

	if chapter_name:
		retired_cards = _retire_chapter_flashcards(profile.learning_module, chapter_name)
		_clear_question_meta_chapter(profile.learning_module, chapter_name)

	if quiz_name and quiz_name != module.module_assessment_quiz:
		_empty_chapter_quiz(quiz_name)

	if chapter_name:
		deleted_lessons = _delete_chapter_lessons(chapter_name, keep={moved_assessment} if moved_assessment else None)
		_delete_chapter_progress(chapter_name)

	profile.notes_lesson = None
	profile.chapter_quiz = None
	profile.course_chapter = None
	profile.save(ignore_permissions=True)
	frappe.delete_doc("Learning Chapter Profile", profile.name, ignore_permissions=True, force=True)

	if chapter_name and frappe.db.exists("Course Chapter", chapter_name):
		frappe.delete_doc("Course Chapter", chapter_name, ignore_permissions=True, force=True)

	module.reload()
	module.refresh_counts()
	module.save(ignore_permissions=True)
	return {
		"ok": True,
		"removed": profile.name,
		"chapter_title": heading,
		"retired_flashcards": retired_cards,
		"deleted_lessons": deleted_lessons,
		"moved_assessment": moved_assessment,
		"questions_kept": True,
	}


@frappe.whitelist()
def save_flashcard(
	chapter_profile: str,
	front: str,
	back: str,
	name: str | None = None,
	concept: str | None = None,
	difficulty: str | None = None,
	source_reference: str | None = None,
	source_quote: str | None = None,
	status: str | None = None,
):
	require_content_role()
	status = (status or "Draft").strip() or "Draft"
	try:
		validate_flashcard_payload(front, back, status)
	except ContentStudioError as error:
		_throw(error)

	profile = frappe.get_doc("Learning Chapter Profile", chapter_profile)
	if not profile.course_chapter:
		frappe.throw(_("This chapter is not linked to an LMS Course Chapter yet."))
	if status in ("Under Review", "Published"):
		_validate_flashcard_source(
			profile,
			(source_reference or "").strip(),
			(source_quote or "").strip(),
		)

	fields = {
		"learning_module": profile.learning_module,
		"course_chapter": profile.course_chapter,
		"front": front.strip(),
		"back": back.strip(),
		"concept": (concept or "").strip(),
		"difficulty": difficulty or "Medium",
		"source_reference": (source_reference or "").strip(),
		"source_quote": (source_quote or "").strip(),
		"status": status,
		"ai_generated": 0,
	}
	created = False
	if name:
		doc = frappe.get_doc("Learning Flashcard", name)
		if doc.learning_module != profile.learning_module:
			frappe.throw(_("That flashcard does not belong to this subject."))
		if (doc.front or "") != fields["front"] or (doc.back or "") != fields["back"]:
			fields["revision"] = cint(doc.revision) + 1
		doc.update(fields)
		doc.save(ignore_permissions=True)
	else:
		fields["doctype"] = "Learning Flashcard"
		fields["revision"] = 1
		doc = frappe.get_doc(fields)
		doc.insert(ignore_permissions=True)
		created = True

	if status == "Published":
		module = frappe.get_doc("Learning Module Config", profile.learning_module)
		_ensure_flashcard_lesson(profile, module.lms_course)

	return {
		"ok": True,
		"created": created,
		"name": doc.name,
		"status": doc.status,
		"revision": cint(doc.revision),
	}


def _chapter_questions(profile) -> list[dict]:
	quiz_order: list[str] = []
	if profile.chapter_quiz:
		quiz_order = [
			row.question
			for row in frappe.get_all(
				"LMS Quiz Question",
				filters={"parent": profile.chapter_quiz},
				fields=["question", "idx"],
				order_by="idx asc",
			)
			if row.question
		]

	meta_rows = frappe.get_all(
		"Learning Question Meta",
		filters={
			"learning_module": profile.learning_module,
			"course_chapter": profile.course_chapter,
		},
		fields=[
			"name",
			"lms_question",
			"concept",
			"difficulty",
			"source_reference",
			"learning_objective",
			"question_role",
			"revision",
			"ai_generated",
		],
		limit_page_length=500,
	)
	meta_by_question = {row.lms_question: row for row in meta_rows if row.lms_question}

	ordered = list(quiz_order)
	for row in meta_rows:
		if row.lms_question and row.lms_question not in ordered:
			ordered.append(row.lms_question)

	questions = []
	for question_name in ordered:
		doc = frappe.get_doc("LMS Question", question_name)
		meta = meta_by_question.get(question_name)
		questions.append(
			{
				"lms_question": doc.name,
				"question": doc.question,
				"options": options_from_lms_question(doc),
				"meta": meta.name if meta else None,
				"concept": meta.concept if meta else "",
				"difficulty": meta.difficulty if meta else "Medium",
				"source_reference": meta.source_reference if meta else "",
				"learning_objective": meta.learning_objective if meta else "",
				"question_role": meta.question_role if meta else "Chapter MCQ",
				"revision": meta.revision if meta else 1,
				"ai_generated": cint(meta.ai_generated) if meta else 0,
				"on_chapter_quiz": question_name in quiz_order,
			}
		)
	return questions


def _ensure_profile_quiz(profile) -> str:
	if profile.chapter_quiz:
		return profile.chapter_quiz
	if not profile.course_chapter:
		frappe.throw(_("This chapter is not linked to an LMS Course Chapter yet."))
	course_name = frappe.db.get_value("Course Chapter", profile.course_chapter, "course")
	course = frappe.get_doc("LMS Course", course_name)
	quiz_name = _ensure_chapter_quiz(course, profile.course_chapter, profile.chapter_title)
	profile.chapter_quiz = quiz_name
	profile.save(ignore_permissions=True)
	return quiz_name


def _upsert_question_meta(profile, question_name: str, values: dict) -> dict:
	meta_name = frappe.db.get_value("Learning Question Meta", {"lms_question": question_name})
	revision = 1
	fields = {
		"doctype": "Learning Question Meta",
		"lms_question": question_name,
		"learning_module": profile.learning_module,
		"course_chapter": profile.course_chapter,
		"concept": values.get("concept"),
		"learning_objective": values.get("learning_objective"),
		"difficulty": values.get("difficulty") or "Medium",
		"question_role": values.get("question_role") or "Chapter MCQ",
		"source_reference": values.get("source_reference"),
	}
	if meta_name:
		meta = frappe.get_doc("Learning Question Meta", meta_name)
		revision = cint(meta.revision) or 1
		if values.get("bump_revision"):
			revision += 1
		fields["revision"] = revision
		meta.update(fields)
		meta.save(ignore_permissions=True)
	else:
		fields["revision"] = 1
		fields["ai_generated"] = 0
		meta = frappe.get_doc(fields)
		meta.insert(ignore_permissions=True)
	return {"name": meta.name, "revision": cint(meta.revision)}


def _refresh_profile_mcq_count(profile) -> None:
	count = _quiz_question_count(profile.chapter_quiz)
	profile.mcq_count = count
	frappe.db.set_value("Learning Chapter Profile", profile.name, "mcq_count", count)


def _quiz_question_count(quiz_name: str | None) -> int:
	if not quiz_name:
		return 0
	return frappe.db.count("LMS Quiz Question", {"parent": quiz_name})


def _assert_heading_available(profile, new_title: str) -> None:
	clash = frappe.db.exists(
		"Learning Chapter Profile",
		{
			"learning_module": profile.learning_module,
			"chapter_title": new_title,
			"name": ("!=", profile.name),
		},
	)
	if clash:
		frappe.throw(_("Another chapter in this subject already uses that heading."))
	if not profile.course_chapter:
		return
	course = frappe.db.get_value("Course Chapter", profile.course_chapter, "course")
	lms_clash = frappe.db.exists(
		"Course Chapter",
		{
			"course": course,
			"title": new_title,
			"name": ("!=", profile.course_chapter),
		},
	)
	if lms_clash:
		frappe.throw(_("Another chapter in this course already uses that heading."))


def _retitle_chapter_surfaces(profile, old_titles: list[str], new_title: str) -> list[dict]:
	changed: list[dict] = []
	if profile.course_chapter:
		for lesson in frappe.get_all(
			"Course Lesson",
			filters={"chapter": profile.course_chapter},
			fields=["name", "title"],
			limit_page_length=50,
		):
			updated = retitle_display(lesson.title, old_titles, new_title)
			if updated:
				frappe.db.set_value("Course Lesson", lesson.name, "title", updated)
				changed.append({"doctype": "Course Lesson", "name": lesson.name, "title": updated})
	if profile.chapter_quiz:
		quiz_title = frappe.db.get_value("LMS Quiz", profile.chapter_quiz, "title")
		updated = retitle_display(quiz_title, old_titles, new_title)
		if updated:
			frappe.db.set_value("LMS Quiz", profile.chapter_quiz, "title", updated)
			changed.append({"doctype": "LMS Quiz", "name": profile.chapter_quiz, "title": updated})
	return changed


def _chapter_flashcards(profile) -> list[dict]:
	if not profile.course_chapter:
		return []
	return frappe.get_all(
		"Learning Flashcard",
		filters={
			"learning_module": profile.learning_module,
			"course_chapter": profile.course_chapter,
			"status": ["!=", "Retired"],
		},
		fields=FLASHCARD_STUDIO_FIELDS,
		order_by="creation asc",
		limit_page_length=500,
	)


def _unlink_chapter_from_course(course_name: str, chapter_name: str) -> None:
	course = frappe.get_doc("LMS Course", course_name)
	kept = [row.chapter for row in (course.get("chapters") or []) if row.chapter != chapter_name]
	if len(kept) == len(course.get("chapters") or []):
		return
	course.set("chapters", [])
	for name in kept:
		course.append("chapters", {"chapter": name})
	course.save(ignore_permissions=True)


def _rehome_module_assessment(profile, module) -> str | None:
	quiz = module.module_assessment_quiz
	if not quiz or not profile.course_chapter:
		return None
	lesson = frappe.db.get_value(
		"Course Lesson",
		{"chapter": profile.course_chapter, "quiz_id": quiz},
		"name",
	)
	if not lesson:
		return None
	other = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": profile.learning_module, "name": ["!=", profile.name]},
		fields=["name", "course_chapter"],
		limit_page_length=20,
	)
	dest = next((row.course_chapter for row in other if row.course_chapter), None)
	if not dest:
		raise ContentStudioError(
			"Cannot remove the last chapter while a module assessment is attached. Add another chapter first."
		)
	chapter = frappe.get_doc("Course Chapter", profile.course_chapter)
	kept = [row.lesson for row in (chapter.get("lessons") or []) if row.lesson != lesson]
	chapter.set("lessons", [])
	for name in kept:
		chapter.append("lessons", {"lesson": name})
	chapter.save(ignore_permissions=True)
	frappe.db.set_value("Course Lesson", lesson, "chapter", dest)
	link_lesson_to_chapter(dest, lesson)
	return lesson


def _retire_chapter_flashcards(learning_module: str, course_chapter: str) -> int:
	names = frappe.get_all(
		"Learning Flashcard",
		filters={"learning_module": learning_module, "course_chapter": course_chapter},
		pluck="name",
		limit_page_length=500,
	)
	for name in names:
		frappe.db.set_value("Learning Flashcard", name, {"status": "Retired", "course_chapter": None})
	return len(names)


def _clear_question_meta_chapter(learning_module: str, course_chapter: str) -> None:
	for name in frappe.get_all(
		"Learning Question Meta",
		filters={"learning_module": learning_module, "course_chapter": course_chapter},
		pluck="name",
		limit_page_length=500,
	):
		frappe.db.set_value("Learning Question Meta", name, "course_chapter", None)


def _empty_chapter_quiz(quiz_name: str) -> None:
	if not frappe.db.exists("LMS Quiz", quiz_name):
		return
	quiz = frappe.get_doc("LMS Quiz", quiz_name)
	quiz.set("questions", [])
	quiz.total_marks = 0
	quiz.save(ignore_permissions=True)


def _delete_chapter_lessons(chapter_name: str, keep: set[str] | None = None) -> int:
	keep = keep or set()
	names = [
		name
		for name in frappe.get_all("Course Lesson", filters={"chapter": chapter_name}, pluck="name")
		if name not in keep
	]
	for name in names:
		frappe.delete_doc("Course Lesson", name, ignore_permissions=True, force=True)
	return len(names)


def _delete_chapter_progress(chapter_name: str) -> None:
	if not frappe.db.exists("DocType", "LMS Course Progress"):
		return
	for name in frappe.get_all("LMS Course Progress", filters={"chapter": chapter_name}, pluck="name"):
		frappe.delete_doc("LMS Course Progress", name, ignore_permissions=True, force=True)


def _course_outline_names(course_name: str) -> list[str]:
	return [
		row.chapter
		for row in frappe.get_all(
			"Chapter Reference",
			filters={"parent": course_name},
			fields=["chapter", "idx"],
			order_by="idx asc",
			limit_page_length=500,
		)
		if row.chapter
	]


def _write_course_outline(course_name: str, names: list[str]) -> None:
	course = frappe.get_doc("LMS Course", course_name)
	course.set("chapters", [])
	for idx, name in enumerate(names, start=1):
		course.append("chapters", {"chapter": name, "idx": idx})
	course.save(ignore_permissions=True)

