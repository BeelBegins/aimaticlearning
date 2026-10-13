"""Facts shown on the public Examic website, read from settings and live course data.

Prices, the free period and the free mock count come from Examic Billing Settings.
Subjects come from published LMS Courses in the SQE1 pathway. Nothing here is a
hard-coded marketing figure.
"""

from __future__ import annotations

import frappe

from aimaticlearning.lms_learning import billing
from aimaticlearning.lms_learning.sqe_pathway import FLK1_SUBJECTS, FLK2_SUBJECTS

# The SQE1 mock product (sqe1_hard_mocks.py): each mock has two FLK1 and two FLK2 sessions.
MOCK_SESSIONS_PER_FLK = 2


def offer_facts() -> dict:
	"""Plan facts for page copy. Prices are formatted the same way as /pricing."""
	cfg = billing.settings()
	free_mocks = cfg["free_mock_count"]
	return {
		"monthly_price": billing.price_text(cfg["monthly_price"]),
		"three_month_price": billing.price_text(cfg["three_month_price"]),
		"three_month_each": billing.price_text(round(cfg["three_month_price"] / 3, 2)),
		"trial_days": cfg["trial_days"],
		"free_mock_count": free_mocks,
		"free_mock_names": " and ".join(f"Mock {n}" for n in range(1, free_mocks + 1)),
		"free_sessions_per_flk": free_mocks * MOCK_SESSIONS_PER_FLK,
		"support_email": cfg.get("support_email") or "hello@examic.study",
	}


def mock_facts() -> dict:
	"""The SQE1 mock set as built on this site, counted from the exam product."""
	from aimaticlearning.lms_learning import sqe1_hard_mocks

	sittings = 0
	try:
		sittings = frappe.db.count(
			"Course Chapter", {"course": sqe1_hard_mocks.COURSE_NAME, "title": ["like", "Mock %"]}
		)
	except Exception:
		sittings = 0
	return {
		"mock_count": sittings,
		"session_count": sittings * MOCK_SESSIONS_PER_FLK * 2,
		"questions_per_session": 85,
		"minutes_per_session": sqe1_hard_mocks.DURATION_MINUTES,
	}


def published_subjects(subjects) -> list[dict]:
	"""Published subjects in the pathway's assessment order, with what is live for each."""
	courses = []
	for subject in subjects:
		if not frappe.db.get_value("LMS Course", subject["course"], "published"):
			continue
		course = frappe.get_doc("LMS Course", subject["course"])
		courses.append(
			{
				"name": course.name,
				"title": course.title,
				"summary": course.short_introduction or subject["summary"],
				"course_url": f"/lms/courses/{course.name}",
				"chapter_count": len(course.chapters or []),
				"activity_label": activity_label(course.name),
			}
		)
	return courses


def flk_catalogue() -> dict:
	return {"flk1_courses": published_subjects(FLK1_SUBJECTS), "flk2_courses": published_subjects(FLK2_SUBJECTS)}


def activity_label(course_name: str) -> str:
	"""Reflect what is actually live for this course, not a hardcoded guess."""
	has_mcqs = bool(
		frappe.db.sql(
			"""
			SELECT 1
			FROM `tabChapter Reference` cr
			JOIN `tabLesson Reference` lr ON lr.parent = cr.chapter
			JOIN `tabCourse Lesson` cl ON cl.name = lr.lesson
			WHERE cr.parent=%s AND cl.quiz_id IS NOT NULL AND cl.quiz_id != ''
			LIMIT 1
			""",
			(course_name,),
		)
	)
	learning_module = frappe.db.get_value("Learning Module Config", {"lms_course": course_name}, "name")
	has_flashcards = bool(
		learning_module
		and frappe.db.exists("Learning Flashcard", {"learning_module": learning_module, "status": "Published"})
	)
	if has_mcqs and has_flashcards:
		return "Notes, practice questions and flashcards"
	if has_mcqs:
		return "Notes and chapter practice questions"
	return "Structured study notes"


def page_context(context, **extra):
	"""Shared context for a public page: offer facts plus any page-specific values."""
	context.no_cache = 1
	context.update(offer_facts())
	context.update(extra)
	return context
