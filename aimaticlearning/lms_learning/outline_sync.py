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

	markdown_lines = [
		f"## {profile.chapter_title}",
		"",
		"### Study notes",
		"",
		"Work through the chapter notes across the lesson pages. "
		"Then complete the **Practice MCQs** and **Flashcards** lessons in this chapter.",
		"",
	]
	for paragraph in preview:
		markdown_lines.append(paragraph)
		markdown_lines.append("")

	lesson = frappe.get_doc("Course Lesson", profile.notes_lesson)
	lesson.content = build_editorjs_content(
		f"Study notes — {profile.chapter_title}",
		[
			"Study the chapter notes across the lesson pages, then complete the Practice MCQs and Flashcards."
		],
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
		lesson = frappe.get_doc("Course Lesson", existing)
	else:
		lesson = frappe.get_doc(
			{
				"doctype": "Course Lesson",
				"title": title,
				"course": course,
				"chapter": profile.course_chapter,
			}
		)
		lesson.insert(ignore_permissions=True)

	# Keep quiz lessons on the body path: Lesson.vue passes quiz_id to
	# LessonContent only when content is empty. EditorJS-only content therefore
	# renders the heading but silently omits the actual quiz.
	lesson.title = title
	lesson.body = (
		"<p>Complete this chapter quiz (up to 20 MCQs). "
		"Review the explanations after each attempt.</p>"
	)
	lesson.content = ""
	lesson.quiz_id = profile.chapter_quiz
	lesson.save(ignore_permissions=True)

	link_lesson_to_chapter(profile.course_chapter, lesson.name)
	return lesson.name


def repair_quiz_lesson_rendering() -> dict:
	"""Migrate linked MCQ lessons to the body + quiz_id rendering path."""
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters={"chapter_quiz": ["is", "set"]},
		fields=["name"],
		order_by="creation asc",
	)
	updated = []
	for row in profiles:
		lesson_name = ensure_quiz_lesson(row.name)
		if lesson_name:
			updated.append(lesson_name)
	frappe.db.commit()
	return {"updated": len(updated), "lessons": updated}


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
	else:
		lesson = frappe.get_doc(
			{
				"doctype": "Course Lesson",
				"title": title,
				"course": course_name,
				"chapter": chapter_name,
				"quiz_id": quiz_name,
				"content": build_editorjs_content(
					title,
					[
						"Complete the full module assessment (150 MCQs). "
						"This draws from chapter topics across the course."
					],
				),
			}
		)
		lesson.insert(ignore_permissions=True)
		lesson_name = lesson.name

	link_chapter_to_course(course_name, chapter_name)
	link_lesson_to_chapter(chapter_name, lesson_name)
	return lesson_name



def ensure_module_assessments_for_existing_mcqs() -> dict:
	modules = frappe.get_all("Learning Module Config", filters={"module_assessment_quiz": ["is", "not set"]}, fields=["name", "lms_course"], order_by="name asc")
	created = []
	for module_row in modules:
		profiles = frappe.get_all("Learning Chapter Profile", filters={"learning_module": module_row.name, "chapter_quiz": ["is", "set"]}, fields=["name", "course_chapter", "chapter_title"], order_by="creation asc")
		by_chapter = []
		for profile in profiles:
			quiz_name = frappe.db.get_value("Learning Chapter Profile", profile.name, "chapter_quiz")
			if not quiz_name:
				continue
			questions = [row.question for row in frappe.get_doc("LMS Quiz", quiz_name).questions or [] if row.question]
			if questions:
				by_chapter.append((profile, list(dict.fromkeys(questions))))
		pool = []
		chapter_index = 0
		while by_chapter and len(pool) < 150:
			profile, questions = by_chapter[chapter_index % len(by_chapter)]
			if questions:
				question = questions.pop(0)
				if question not in pool:
					pool.append(question)
			if not any(questions for _, questions in by_chapter):
				break
			chapter_index += 1
		if not pool:
			continue
		target = len(pool)
		course = frappe.get_doc("LMS Course", module_row.lms_course)
		quiz = frappe.get_doc({"doctype": "LMS Quiz", "title": f"{course.title} — Module Assessment ({target} MCQs)", "course": course.name, "max_attempts": 0, "show_answers": 1, "passing_percentage": 60})
		for question in pool:
			quiz.append("questions", {"question": question, "marks": 1})
		quiz.total_marks = target
		quiz.insert(ignore_permissions=True)
		for question in pool:
			meta_name = frappe.db.get_value("Learning Question Meta", {"lms_question": question})
			if meta_name:
				frappe.db.set_value("Learning Question Meta", meta_name, "question_role", "Both")
		last_profile = profiles[-1]
		lesson = frappe.get_doc({"doctype": "Course Lesson", "title": f"Module Assessment — {target} MCQs", "course": course.name, "chapter": last_profile.course_chapter, "quiz_id": quiz.name, "body": f"<p>Complete the full module assessment ({target} MCQs) covering the course chapters.</p>", "content": ""})
		lesson.insert(ignore_permissions=True)
		link_chapter_to_course(course.name, last_profile.course_chapter)
		link_lesson_to_chapter(last_profile.course_chapter, lesson.name)
		module = frappe.get_doc("Learning Module Config", module_row.name)
		module.module_assessment_quiz = quiz.name
		module.module_assessment_count = target
		module.module_mcq_count = target
		module.import_status = "Content Ready"
		module.save(ignore_permissions=True)
		created.append({"module": module.name, "course": course.name, "quiz": quiz.name, "questions": target})
	frappe.db.commit()
	return {"created": created, "count": len(created)}



def repair_module_assessment_lesson_rendering() -> dict:
	updated = []
	modules = frappe.get_all("Learning Module Config", filters={"module_assessment_quiz": ["is", "set"]}, fields=["name", "lms_course", "module_assessment_quiz"])
	for module_row in modules:
		quiz = frappe.get_doc("LMS Quiz", module_row.module_assessment_quiz)
		count = len(quiz.questions or [])
		lesson_name = frappe.db.get_value("Course Lesson", {"course": module_row.lms_course, "quiz_id": module_row.module_assessment_quiz}, "name")
		if lesson_name:
			lesson = frappe.get_doc("Course Lesson", lesson_name)
		else:
			profile_name = frappe.db.get_value("Learning Chapter Profile", {"learning_module": module_row.name}, "name", order_by="creation desc")
			profile = frappe.get_doc("Learning Chapter Profile", profile_name)
			lesson = frappe.get_doc({"doctype": "Course Lesson", "course": module_row.lms_course, "chapter": profile.course_chapter, "quiz_id": module_row.module_assessment_quiz})
		lesson.title = f"Module Assessment — {count} MCQs"
		lesson.body = f"<p>Complete the full module assessment ({count} MCQs) covering the course chapters.</p>"
		lesson.content = ""
		lesson.quiz_id = module_row.module_assessment_quiz
		if lesson.is_new():
			lesson.insert(ignore_permissions=True)
			link_lesson_to_chapter(lesson.chapter, lesson.name)
		else:
			lesson.save(ignore_permissions=True)
		module = frappe.get_doc("Learning Module Config", module_row.name)
		module.module_assessment_count = count
		module.module_mcq_count = count
		module.import_status = "Content Ready"
		module.save(ignore_permissions=True)
		updated.append({"module": module.name, "lesson": lesson.name, "questions": count})
	frappe.db.commit()
	return {"updated": updated, "count": len(updated)}



def consolidate_duplicate_module_assessments() -> dict:
	removed = []
	for module in frappe.get_all("Learning Module Config", filters={"module_assessment_quiz": ["is", "set"]}, fields=["name", "lms_course", "module_assessment_quiz"]):
		lessons = frappe.get_all("Course Lesson", filters={"course": module.lms_course, "quiz_id": module.module_assessment_quiz}, fields=["name", "chapter", "body", "creation"], order_by="creation asc")
		canonical = next((row for row in lessons if row.body), lessons[-1] if lessons else None)
		for row in lessons:
			if not canonical or row.name == canonical.name:
				continue
			chapter = frappe.get_doc("Course Chapter", row.chapter)
			chapter.set("lessons", [ref for ref in chapter.lessons if ref.lesson != row.name])
			chapter.save(ignore_permissions=True)
			removed.append(row.name)
	frappe.db.commit()
	return {"detached": removed, "count": len(removed)}
