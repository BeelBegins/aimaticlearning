from __future__ import annotations

import json
import re
from html import unescape

import frappe
from frappe.utils import now_datetime


def build_editorjs_content(
	title: str,
	paragraphs: list[str],
	profile_name: str | None = None,
) -> str:
	blocks: list[dict] = [
		{
			"type": "header",
			"data": {"text": title, "level": 2},
		}
	]
	for paragraph in paragraphs:
		text = (paragraph or "").strip()
		if not text:
			continue
		blocks.append({"type": "paragraph", "data": {"text": text}})

	if profile_name:
		blocks.append(
			{
				"type": "paragraph",
				"data": {
					"text": (
						f'<a href="/learning-notes/{profile_name}" target="_blank" rel="noopener">'
						"Open protected notes viewer</a>"
					),
				},
			}
		)

	return json.dumps(
		{
			"time": int(now_datetime().timestamp() * 1000),
			"blocks": blocks,
			"version": "2.29.1",
		}
	)


def paragraphs_from_notes_html(notes_html: str) -> list[str]:
	if not notes_html:
		return []
	parts = re.findall(r"<p>(.*?)</p>", notes_html, flags=re.DOTALL)
	return [unescape(part.strip()) for part in parts if part.strip()]


def link_chapter_to_course(course_name: str, chapter_name: str) -> None:
	course = frappe.get_doc("LMS Course", course_name)
	if any(row.chapter == chapter_name for row in course.get("chapters") or []):
		return
	course.append("chapters", {"chapter": chapter_name})
	course.save(ignore_permissions=True)


def link_lesson_to_chapter(chapter_name: str, lesson_name: str) -> None:
	chapter = frappe.get_doc("Course Chapter", chapter_name)
	if any(row.lesson == lesson_name for row in chapter.get("lessons") or []):
		return
	chapter.append("lessons", {"lesson": lesson_name})
	chapter.save(ignore_permissions=True)


def populate_notes_lesson(profile_name: str) -> str | None:
	profile = frappe.get_doc("Learning Chapter Profile", profile_name)
	if not profile.notes_lesson:
		return None

	paragraphs = paragraphs_from_notes_html(profile.notes_html or "")
	preview = _notes_preview_paragraphs(paragraphs)
	viewer_link = f"/learning-notes/{profile.name}"

	markdown_lines = [
		f"## {profile.chapter_title}",
		"",
		"### Study notes",
		"",
		"Read the full chapter in the **protected notes viewer** (no download). "
		"Use **Practice MCQs** and **Flashcards** lessons in this chapter after reading.",
		"",
	]
	for paragraph in preview:
		markdown_lines.append(paragraph)
		markdown_lines.append("")
	markdown_lines.append(f"[Open full protected notes →]({viewer_link})")

	lesson = frappe.get_doc("Course Lesson", profile.notes_lesson)
	lesson.content = build_editorjs_content(
		f"Study notes — {profile.chapter_title}",
		[
			f"Preview for {profile.chapter_title}. Open the protected viewer for the full chapter."
		],
		profile_name=profile.name,
	)
	lesson.body = "\n".join(markdown_lines).strip()
	lesson.save(ignore_permissions=True)
	return lesson.name


def _notes_preview_paragraphs(paragraphs: list[str], max_paragraphs: int = 2, max_chars: int = 600) -> list[str]:
	preview: list[str] = []
	total = 0
	for paragraph in paragraphs:
		text = (paragraph or "").strip()
		if not text or len(text) < 30:
			continue
		if total + len(text) > max_chars and preview:
			break
		preview.append(text)
		total += len(text)
		if len(preview) >= max_paragraphs:
			break
	return preview


def new_quiz_lesson_values(
	*,
	title: str,
	course: str,
	chapter: str,
	quiz_id: str,
	body: str | None = None,
) -> dict:
	"""Quiz-wired lessons must keep EditorJS `content` empty.

	Frappe LMS Lesson.vue renders the CodeX editor whenever `content` is
	truthy, and only then falls through to `body` + `quiz_id`. A paragraph
	blob hides the quiz widget. `body` still has to be non-empty: the
	`quiz_id` widget is only mounted inside that body fallback.
	"""
	return {
		"doctype": "Course Lesson",
		"title": title,
		"course": course,
		"chapter": chapter,
		"quiz_id": quiz_id,
		"content": "",
		"body": (body or "").strip()
		or "<p>Complete this quiz, then submit your attempt to review the results.</p>",
	}


def quiz_lessons_with_editorjs(rows: list[dict]) -> list[dict]:
	blocked = []
	for row in rows:
		quiz_id = (row.get("quiz_id") or "").strip()
		content = (row.get("content") or "").strip()
		if quiz_id and content:
			blocked.append(row)
	return blocked


def _empty_quiz_lesson_content(lesson_name: str) -> bool:
	content = frappe.db.get_value("Course Lesson", lesson_name, "content")
	if not (content or "").strip():
		return False
	frappe.db.set_value("Course Lesson", lesson_name, "content", "")
	return True


def ensure_quiz_lesson(profile_name: str) -> str | None:
	profile = frappe.get_doc("Learning Chapter Profile", profile_name)
	if not profile.chapter_quiz or not profile.course_chapter:
		return None

	course = frappe.db.get_value("Course Chapter", profile.course_chapter, "course")
	title = f"Chapter MCQ — {profile.chapter_title}"
	existing = frappe.db.get_value(
		"Course Lesson",
		{"course": course, "chapter": profile.course_chapter, "quiz_id": profile.chapter_quiz},
		"name",
	)
	if existing:
		lesson_name = existing
		_empty_quiz_lesson_content(lesson_name)
	else:
		lesson = frappe.get_doc(
			new_quiz_lesson_values(
				title=title,
				course=course,
				chapter=profile.course_chapter,
				quiz_id=profile.chapter_quiz,
			)
		)
		lesson.insert(ignore_permissions=True)
		lesson_name = lesson.name

	link_lesson_to_chapter(profile.course_chapter, lesson_name)
	return lesson_name


def sync_profile_outline(profile_name: str) -> dict:
	profile = frappe.get_doc("Learning Chapter Profile", profile_name)
	module = frappe.get_doc("Learning Module Config", profile.learning_module)
	course_name = module.lms_course

	if profile.course_chapter:
		link_chapter_to_course(course_name, profile.course_chapter)
	if profile.notes_lesson and profile.course_chapter:
		link_lesson_to_chapter(profile.course_chapter, profile.notes_lesson)
		populate_notes_lesson(profile_name)

	quiz_lesson = ensure_quiz_lesson(profile_name)
	return {
		"profile": profile_name,
		"notes_lesson": profile.notes_lesson,
		"quiz_lesson": quiz_lesson,
	}


def repair_course_content(course_name: str | None = None) -> dict:
	if not course_name:
		course_name = frappe.db.get_value(
			"Learning Module Config",
			{"title": "Business Law & Practice (BLP)"},
			"lms_course",
		)
	if not course_name:
		frappe.throw("BLP course not found.")

	module_name = frappe.db.get_value("Learning Module Config", {"lms_course": course_name}, "name")
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": module_name},
		pluck="name",
		order_by="creation asc",
	)

	synced = []
	for profile_name in profiles:
		synced.append(sync_profile_outline(profile_name))

	# Module assessment lesson on last chapter or course-level - add to last chapter
	module = frappe.get_doc("Learning Module Config", module_name)
	if module.module_assessment_quiz and profiles:
		last_profile = frappe.get_doc("Learning Chapter Profile", profiles[-1])
		assessment_lesson = _ensure_module_assessment_lesson(
			course_name,
			last_profile.course_chapter,
			module.module_assessment_quiz,
		)
	else:
		assessment_lesson = None

	frappe.db.commit()
	return {
		"course": course_name,
		"learning_module": module_name,
		"synced_chapters": len(synced),
		"details": synced,
		"module_assessment_lesson": assessment_lesson,
	}


def _ensure_module_assessment_lesson(
	course_name: str, chapter_name: str, quiz_name: str
) -> str | None:
	title = "Module Assessment — 150 MCQs"
	existing = frappe.db.get_value(
		"Course Lesson",
		{"course": course_name, "quiz_id": quiz_name},
		"name",
	)
	if existing:
		lesson_name = existing
		_empty_quiz_lesson_content(lesson_name)
	else:
		lesson = frappe.get_doc(
			new_quiz_lesson_values(
				title=title,
				course=course_name,
				chapter=chapter_name,
				quiz_id=quiz_name,
			)
		)
		lesson.insert(ignore_permissions=True)
		lesson_name = lesson.name

	link_chapter_to_course(course_name, chapter_name)
	link_lesson_to_chapter(chapter_name, lesson_name)
	return lesson_name


def clear_quiz_lesson_editorjs(course_name: str | None = None, dry_run: bool = True) -> dict:
	"""Empty EditorJS `content` on quiz-wired lessons so the LMS widget mounts."""
	sql = """
		SELECT name, course, title, quiz_id, content
		FROM `tabCourse Lesson`
		WHERE quiz_id IS NOT NULL AND quiz_id != ''
		  AND TRIM(IFNULL(content, '')) != ''
	"""
	params: list = []
	if course_name:
		sql += " AND course = %s"
		params.append(course_name)
	rows = frappe.db.sql(sql, tuple(params), as_dict=True)
	blocked = quiz_lessons_with_editorjs(rows)
	if not dry_run:
		for row in blocked:
			frappe.db.set_value("Course Lesson", row["name"], "content", "")
		if blocked:
			frappe.db.commit()
	return {
		"dry_run": dry_run,
		"count": len(blocked),
		"cleared": [
			{"name": row["name"], "course": row["course"], "title": row["title"]}
			for row in blocked
		],
	}


@frappe.whitelist(allow_guest=True)
def get_course_details(course: str):
	"""Native get_course_details() reports quiz_count by scanning each lesson's
	EditorJS content for an embedded 'quiz' block. Every chapter MCQ on this
	platform is instead wired via Course Lesson.quiz_id (see ensure_quiz_lesson
	above), so the native count is always 0 and the frontend's CourseCardOverlay
	hides its "Quiz topics" row entirely, even on courses with dozens of working
	quizzes. Patch the count in rather than duplicating the whole function."""
	from lms.lms.utils import get_course_details as native_get_course_details

	details = native_get_course_details(course)
	if not details:
		return details

	quiz_id_count = frappe.db.sql(
		"""
		SELECT COUNT(DISTINCT quiz_id) FROM `tabCourse Lesson`
		WHERE course=%s AND quiz_id IS NOT NULL AND quiz_id != ''
		""",
		(course,),
	)[0][0]
	if quiz_id_count:
		details["quiz_count"] = (details.get("quiz_count") or 0) + quiz_id_count
	return details
