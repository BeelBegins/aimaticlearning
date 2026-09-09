from __future__ import annotations

import re

import frappe
from frappe import _

from aimaticlearning.lms_learning.outline_sync import (
	build_editorjs_content,
	link_chapter_to_course,
	link_lesson_to_chapter,
)
from aimaticlearning.lms_learning.protected_notes import render_notes_html

CHAPTER_NUM_RE = re.compile(r"Chapter\s+(\d+)\s*:", re.I)
INTRO_MAX_PARAGRAPHS = 8
INTRO_MAX_BYTES = 12000
MEGA_NOTES_BYTES = 50000


def repair_course_presentation(course_name: str | None = None) -> dict:
	"""Fix chapter order, trim broken intro blob, short lesson bodies, flashcard lessons."""
	if not course_name:
		course_name = frappe.db.get_value(
			"Learning Module Config",
			{"title": "Business Law & Practice (BLP)"},
			"lms_course",
		)
	if not course_name:
		frappe.throw(_("BLP course not found."))

	module_name = frappe.db.get_value("Learning Module Config", {"lms_course": course_name}, "name")
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": module_name},
		fields=["name", "chapter_title", "course_chapter", "notes_lesson", "chapter_quiz", "notes_html"],
		order_by="creation asc",
	)

	fixed_intro = _repair_introduction_blob(profiles)
	reordered = _reorder_course_chapters(course_name, profiles)
	hub_lessons = 0

	for profile in profiles:
		doc = frappe.get_doc("Learning Chapter Profile", profile.name)
		if _consolidate_chapter_hub_lesson(doc, course_name):
			hub_lessons += 1

	flashcards_seeded = _seed_chapter_flashcards(module_name, limit_chapters=8, per_chapter=6)

	_course = frappe.get_doc("LMS Course", course_name)
	_course.short_introduction = (
		"SQE Business Law & Practice — study notes, chapter MCQs, flashcards, and module assessment."
	)
	_course.description = (
		"<p>One lesson per chapter with tabs: <strong>Study notes</strong>, "
		"<strong>Practice MCQs</strong>, and <strong>Flashcards</strong>. "
		"Module assessment is in the final chapter.</p>"
	)
	_course.save(ignore_permissions=True)

	frappe.db.commit()
	return {
		"course": course_name,
		"fixed_intro": fixed_intro,
		"reordered_chapters": reordered,
		"hub_lessons": hub_lessons,
		"flashcards_seeded": flashcards_seeded,
	}


def _repair_introduction_blob(profiles: list[dict]) -> bool:
	for row in profiles:
		if row.chapter_title.strip().lower() != "introduction":
			continue
		html = row.notes_html or ""
		if len(html) <= MEGA_NOTES_BYTES:
			return False
		welcome = render_notes_html(
			[
				"Welcome to Business Law & Practice (BLP) on Examic Study.",
				"This module covers UK tax and VAT topics aligned to your SQE study path.",
				"Open each chapter in order: read the chapter notes, complete practice MCQs, "
				"then review flashcards before moving on.",
				"The full company-law question bank is linked separately in MCQ sections — "
				"it is not part of this introductory chapter.",
			]
		)
		frappe.db.set_value("Learning Chapter Profile", row.name, "notes_html", welcome)
		return True
	return False


def _profile_sort_key(profile: dict) -> tuple[int, str]:
	title = profile.get("chapter_title") or ""
	chapter_name = profile.get("course_chapter")
	if chapter_name:
		chapter_title = frappe.db.get_value("Course Chapter", chapter_name, "title") or title
		match = CHAPTER_NUM_RE.search(chapter_title)
		if match:
			return (int(match.group(1)), chapter_title.lower())
	return _chapter_sort_key(profile)


def _chapter_sort_key(profile: dict) -> tuple[int, str]:
	title = profile.get("chapter_title") or ""
	match = CHAPTER_NUM_RE.search(title)
	if match:
		return (int(match.group(1)), title.lower())
	if title.lower() == "introduction":
		return (0, title.lower())
	return (999, title.lower())


def _reorder_course_chapters(course_name: str, profiles: list[dict]) -> int:
	ordered_profiles = sorted(profiles, key=_profile_sort_key)
	course = frappe.get_doc("LMS Course", course_name)
	course.set("chapters", [])

	for idx, profile in enumerate(ordered_profiles, start=1):
		chapter_name = profile.course_chapter
		if not chapter_name:
			continue
		frappe.db.set_value("Course Chapter", chapter_name, "idx", idx)
		link_chapter_to_course(course_name, chapter_name)
		course.append("chapters", {"chapter": chapter_name, "idx": idx})

	course.save(ignore_permissions=True)
	return len(ordered_profiles)


def _consolidate_chapter_hub_lesson(profile: frappe.Document, course_name: str) -> bool:
	"""Keep chapter notes as a normal lesson; MCQs and flashcards stay separate lessons."""
	if not profile.course_chapter or not profile.notes_lesson:
		return False

	chapter_title = frappe.db.get_value("Course Chapter", profile.course_chapter, "title") or profile.chapter_title
	lesson = frappe.get_doc("Course Lesson", profile.notes_lesson)
	lesson.title = chapter_title if chapter_title.lower().startswith("chapter") else f"Chapter — {profile.chapter_title}"
	lesson.body = profile.notes_html or "<p>No study notes are available for this chapter yet.</p>"
	lesson.content = ""
	lesson.quiz_id = ""
	lesson.save(ignore_permissions=True)

	chapter = frappe.get_doc("Course Chapter", profile.course_chapter)
	lesson_rows = [{"lesson": lesson.name, "idx": 1}]
	other_lessons = frappe.get_all(
		"Course Lesson",
		filters={"course": course_name, "chapter": profile.course_chapter, "name": ["!=", lesson.name]},
		fields=["name", "title", "quiz_id", "body", "creation"],
	)
	def lesson_bucket(row: dict) -> tuple[int, str]:
		title = (row.title or "").lower()
		if "module assessment" in title:
			return (3, title)
		if row.quiz_id:
			return (1, title)
		if "flashcard" in title:
			return (2, title)
		return (1, title)
	for idx, row in enumerate(sorted(other_lessons, key=lesson_bucket), start=2):
		lesson_rows.append({"lesson": row.name, "idx": idx})
	chapter.set("lessons", lesson_rows)
	chapter.save(ignore_permissions=True)
	for row in lesson_rows:
		frappe.db.set_value("Course Lesson", row["lesson"], "idx", row["idx"])
	return True

def _lesson_rename(lesson_name: str, title: str) -> None:
	frappe.db.set_value("Course Lesson", lesson_name, "title", title)


def _find_quiz_lesson(course_name: str, chapter_name: str, quiz_id: str) -> str | None:
	return frappe.db.get_value(
		"Course Lesson",
		{"course": course_name, "chapter": chapter_name, "quiz_id": quiz_id},
		"name",
	)


def _ensure_flashcard_lesson(profile: frappe.Document, course_name: str) -> str | None:
	"""Create or refresh one canonical, API-backed Flashcards lesson for a chapter."""
	if not profile.course_chapter:
		return None

	candidates = frappe.get_all(
		"Course Lesson",
		filters={"course": course_name, "chapter": profile.course_chapter},
		fields=["name", "title", "body", "creation"],
		order_by="creation asc",
	)
	canonical = next((row for row in candidates if "data-aimatic-flashcard-deck" in (row.body or "")), None)
	if not canonical:
		canonical = next((row for row in candidates if row.title == "Flashcards"), None)
	if not canonical:
		canonical = next((row for row in candidates if "flashcard" in (row.title or "").lower()), None)

	if canonical:
		lesson = frappe.get_doc("Course Lesson", canonical.name)
	else:
		lesson = frappe.get_doc(
			{
				"doctype": "Course Lesson",
				"title": "Flashcards",
				"course": course_name,
				"chapter": profile.course_chapter,
			}
		)
		lesson.insert(ignore_permissions=True)

	from aimaticlearning.lms_learning.kinnu_course import _flashcard_lesson_html
	lesson.title = "Flashcards"
	lesson.body = _flashcard_lesson_html(profile)
	lesson.content = ""
	lesson.quiz_id = ""
	lesson.save(ignore_permissions=True)
	link_lesson_to_chapter(profile.course_chapter, lesson.name)
	return lesson.name

def repair_flashcard_lesson_rendering(learning_module: str | None = None) -> dict:
	"""Clear stale EditorJS payloads so Flashcard deck hosts render."""
	filters = {}
	if learning_module:
		filters["learning_module"] = learning_module
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters=filters,
		fields=["name", "course_chapter"],
		order_by="creation asc",
	)
	updated = []
	for row in profiles:
		profile = frappe.get_doc("Learning Chapter Profile", row.name)
		course = frappe.db.get_value("Course Chapter", profile.course_chapter, "course")
		lesson_name = _ensure_flashcard_lesson(profile, course)
		if lesson_name:
			updated.append(lesson_name)
	frappe.db.commit()
	return {"updated": len(updated), "lessons": updated}


def _seed_chapter_flashcards(
	learning_module: str, limit_chapters: int = 8, per_chapter: int = 6, only_empty: bool = False
) -> int:
	"""Seed published flashcards from chapter note paragraphs (skip mega intro)."""
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": learning_module},
		fields=["name", "chapter_title", "course_chapter", "notes_html"],
		order_by="creation asc",
	)
	created = 0
	used_chapters = 0

	for profile in profiles:
		if used_chapters >= limit_chapters:
			break
		html = profile.notes_html or ""
		if only_empty and frappe.db.count("Learning Flashcard", {"learning_module": learning_module, "course_chapter": profile.course_chapter, "status": "Published"}):
			continue
		if len(html) < 200:
			continue

		paragraphs = _flashcard_source_segments(html)[:per_chapter]
		if not paragraphs:
			continue

		for i, paragraph in enumerate(paragraphs, start=1):
			front = paragraph[:120].rsplit(" ", 1)[0] + "…" if len(paragraph) > 120 else paragraph
			back = paragraph
			source = f"{profile.chapter_title} para {i}"
			existing = frappe.db.exists(
				"Learning Flashcard",
				{
					"learning_module": learning_module,
					"course_chapter": profile.course_chapter,
					"source_reference": source,
				},
			)
			if existing:
				continue
			frappe.get_doc(
				{
					"doctype": "Learning Flashcard",
					"learning_module": learning_module,
					"course_chapter": profile.course_chapter,
					"concept": profile.chapter_title,
					"front": front,
					"back": back,
					"difficulty": "Medium",
					"source_reference": source,
					"status": "Published",
					"ai_generated": 0,
				}
			).insert(ignore_permissions=True)
			created += 1

		used_chapters += 1

	return created


def _flashcard_source_segments(notes_html: str) -> list[str]:
	"""Extract readable, source-grounded blocks from imported chapter HTML."""
	blocks = re.findall(
		r"<(?:p|li|h[1-6]|td|th|div)[^>]*>(.*?)</(?:p|li|h[1-6]|td|th|div)>",
		notes_html or "",
		flags=re.DOTALL | re.IGNORECASE,
	)
	if not blocks:
		blocks = re.split(r"<br\s*/?>|\n+", notes_html or "", flags=re.IGNORECASE)
	segments = []
	seen = set()
	for block in blocks:
		text = re.sub(r"<[^>]+>", " ", block)
		text = re.sub(r"&(?:nbsp|amp|quot|#39);", " ", text)
		text = re.sub(r"\s+", " ", text).strip()
		if len(text) < 40 or text in seen:
			continue
		seen.add(text)
		segments.append(text)
	return segments


def _reorder_chapter_lessons(chapter_name: str, course_name: str) -> None:
	"""Notes → MCQs → Flashcards within each chapter."""
	if not chapter_name:
		return
	lessons = frappe.get_all(
		"Course Lesson",
		filters={"course": course_name, "chapter": chapter_name},
		fields=["name", "title", "quiz_id", "body", "creation"],
	)
	flashcard_lessons = [lesson for lesson in lessons if "flashcard" in (lesson.title or "").lower()]
	canonical_flashcard = next(
		(lesson for lesson in flashcard_lessons if "data-aimatic-flashcard-deck" in (lesson.body or "")),
		next((lesson for lesson in flashcard_lessons if lesson.title == "Flashcards"), None),
	)
	if not canonical_flashcard and flashcard_lessons:
		canonical_flashcard = sorted(flashcard_lessons, key=lambda lesson: (lesson.creation or "", lesson.name))[0]
	order = {0: [], 1: [], 2: []}
	for lesson in lessons:
		title = (lesson.title or "").lower()
		if lesson.quiz_id:
			order[1].append(lesson.name)
		elif "flashcard" in title:
			if canonical_flashcard and lesson.name != canonical_flashcard.name:
				continue
			order[2].append(lesson.name)
		else:
			order[0].append(lesson.name)

	chapter = frappe.get_doc("Course Chapter", chapter_name)
	chapter.set("lessons", [])
	idx = 1
	for bucket in (0, 1, 2):
		for lesson_name in order[bucket]:
			chapter.append("lessons", {"lesson": lesson_name, "idx": idx})
			frappe.db.set_value("Course Lesson", lesson_name, "idx", idx)
			idx += 1
	chapter.save(ignore_permissions=True)
