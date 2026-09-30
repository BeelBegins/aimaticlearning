"""SQE1 mocks as an exam product. LMS Quiz stays the paper engine."""

from __future__ import annotations

import frappe

from aimaticlearning.lms_learning.sqe1_hard_mocks import (
	COURSE_NAME,
	COURSE_TITLE,
	DURATION_MINUTES,
	LOBBY_URL,
	MAX_ATTEMPTS,
	REPORT_CHAPTER_TITLE,
)

EXAM_KEY = COURSE_NAME
FORMAT_NOTE = (
	"January 2027 sitting: 85 questions, 153 minutes, closed book, "
	f"{MAX_ATTEMPTS} attempts per session."
)


def quiz_sitting_url(quiz: str | None) -> str:
	if not quiz:
		return LOBBY_URL
	return f"/lms/quiz/{quiz}?fromLesson=1"


def is_exam_quiz(quiz: str | None) -> bool:
	if not quiz:
		return False
	course = frappe.db.get_value("LMS Quiz", quiz, "course")
	if course == COURSE_NAME:
		return True
	if not frappe.db.exists("DocType", "Learning Mock Session"):
		return False
	return bool(frappe.db.exists("Learning Mock Session", {"lms_quiz": quiz}))


def feedback_pdf_url(submission: str | None) -> str | None:
	if not submission:
		return None
	from urllib.parse import quote

	return (
		"/api/method/aimaticlearning.lms_learning.api.download_mock_feedback_pdf?submission="
		+ quote(submission, safe="")
	)


def group_lobby_sessions(
	rows: list,
	attempts_by_quiz: dict | None = None,
	max_attempts: int = MAX_ATTEMPTS,
	latest_submission_by_quiz: dict | None = None,
) -> list:
	attempts_by_quiz = attempts_by_quiz or {}
	latest_submission_by_quiz = latest_submission_by_quiz or {}
	sittings: dict[int, dict] = {}
	order: list[int] = []
	for row in rows or []:
		if hasattr(row, "as_dict"):
			row = row.as_dict()
		key = int(row.get("sitting_index") or 0)
		if key not in sittings:
			sittings[key] = {
				"title": row.get("sitting_title") or f"Mock {key}",
				"sessions": [],
			}
			order.append(key)
		quiz = row.get("lms_quiz")
		sittings[key]["sessions"].append(
			{
				"title": row.get("session_title") or "Session",
				"duration": int(row.get("duration_minutes") or DURATION_MINUTES),
				"questions": int(row.get("question_count") or 85),
				"attempts": int(attempts_by_quiz.get(quiz, 0) or 0),
				"max_attempts": int(max_attempts or MAX_ATTEMPTS),
				"start_url": quiz_sitting_url(quiz),
				"feedback_url": feedback_pdf_url(latest_submission_by_quiz.get(quiz)),
			}
		)
	return [sittings[key] for key in order]


def _course_session_rows() -> list[dict]:
	if not frappe.db.exists("LMS Course", COURSE_NAME):
		return []
	course = frappe.get_doc("LMS Course", COURSE_NAME)
	rows = []
	sitting_idx = 0
	for crow in course.get("chapters") or []:
		chapter = frappe.get_doc("Course Chapter", crow.chapter)
		title = chapter.title or ""
		if title == REPORT_CHAPTER_TITLE:
			continue
		sitting_idx += 1
		session_idx = 0
		for lrow in chapter.get("lessons") or []:
			lesson = frappe.get_doc("Course Lesson", lrow.lesson)
			quiz = (lesson.quiz_id or "").strip()
			if not quiz:
				continue
			session_idx += 1
			question_count = frappe.db.count("LMS Quiz Question", {"parent": quiz}) or 85
			rows.append(
				{
					"sitting_index": sitting_idx,
					"sitting_title": title,
					"session_index": session_idx,
					"session_title": lesson.title,
					"lms_quiz": quiz,
					"duration_minutes": DURATION_MINUTES,
					"question_count": int(question_count),
				}
			)
	return rows


def sync_from_hard_mock_course() -> dict:
	"""Idempotent: copy the live hard-mock outline into Learning Mock Exam."""
	if not frappe.db.exists("DocType", "Learning Mock Exam"):
		return {"ok": False, "reason": "doctype-missing"}
	if not frappe.db.exists("LMS Course", COURSE_NAME):
		return {"ok": False, "reason": "course-missing"}

	rows = _course_session_rows()
	if frappe.db.exists("Learning Mock Exam", EXAM_KEY):
		exam = frappe.get_doc("Learning Mock Exam", EXAM_KEY)
	else:
		exam = frappe.get_doc(
			{
				"doctype": "Learning Mock Exam",
				"exam_key": EXAM_KEY,
				"title": COURSE_TITLE,
				"acl_course": COURSE_NAME,
			}
		)

	exam.title = COURSE_TITLE
	exam.acl_course = COURSE_NAME
	exam.duration_minutes = DURATION_MINUTES
	exam.max_attempts = MAX_ATTEMPTS
	exam.format_note = FORMAT_NOTE
	exam.set("sessions", [])
	for row in rows:
		exam.append("sessions", row)
	if exam.is_new():
		exam.insert(ignore_permissions=True)
	else:
		exam.save(ignore_permissions=True)

	backfilled = backfill_enrolments_from_course(exam.name)
	return {
		"ok": True,
		"exam": exam.name,
		"sessions": len(rows),
		"enrolments": backfilled,
	}


def backfill_enrolments_from_course(exam: str | None = None) -> int:
	exam = exam or EXAM_KEY
	if not frappe.db.exists("Learning Mock Exam", exam):
		return 0
	created = 0
	for member in frappe.get_all("LMS Enrollment", {"course": COURSE_NAME}, pluck="member"):
		result = enrol_member_on_exam(member, exam)
		if result.get("created"):
			created += 1
	return created


def enrol_member_on_exam(user: str, exam: str | None = None) -> dict:
	from aimaticlearning.lms_learning.enrollment import enroll_member_in_course

	exam = exam or EXAM_KEY
	acl_course = COURSE_NAME
	if frappe.db.exists("DocType", "Learning Mock Exam") and frappe.db.exists("Learning Mock Exam", exam):
		acl_course = frappe.db.get_value("Learning Mock Exam", exam, "acl_course") or COURSE_NAME

	# ACL course is unpublished + disable_self_learning so it never appears as a
	# normal subject. Start-session enrolment must still succeed for students.
	lms_enrollment = enroll_member_in_course(
		user,
		acl_course,
		skip_email=True,
		bypass_self_learning_gate=True,
	)
	if not frappe.db.exists("DocType", "Learning Mock Enrolment"):
		return {"enrolment": None, "lms_enrollment": lms_enrollment, "created": False}
	if not frappe.db.exists("Learning Mock Exam", exam):
		return {"enrolment": None, "lms_enrollment": lms_enrollment, "created": False}

	existing = frappe.db.get_value("Learning Mock Enrolment", {"exam": exam, "member": user})
	if existing:
		if lms_enrollment:
			frappe.db.set_value("Learning Mock Enrolment", existing, "lms_enrollment", lms_enrollment)
		return {"enrolment": existing, "lms_enrollment": lms_enrollment, "created": False}

	doc = frappe.get_doc(
		{
			"doctype": "Learning Mock Enrolment",
			"exam": exam,
			"member": user,
			"lms_enrollment": lms_enrollment,
		}
	)
	doc.insert(ignore_permissions=True)
	return {"enrolment": doc.name, "lms_enrollment": lms_enrollment, "created": True}


def is_enrolled(user: str, exam: str | None = None) -> bool:
	exam = exam or EXAM_KEY
	if user in (None, "Guest"):
		return False
	if frappe.db.exists("DocType", "Learning Mock Enrolment") and frappe.db.exists(
		"Learning Mock Enrolment", {"exam": exam, "member": user}
	):
		return True
	return bool(frappe.db.exists("LMS Enrollment", {"member": user, "course": COURSE_NAME}))


def student_lobby(user: str | None = None) -> dict:
	"""Logged-in lobby. Enrolment happens on Start, not as a course card."""
	from aimaticlearning.lms_learning.utils import throw_access_denied

	user = user or frappe.session.user
	if not user or user == "Guest":
		throw_access_denied()

	max_attempts = MAX_ATTEMPTS
	format_note = FORMAT_NOTE
	session_rows = []
	if frappe.db.exists("DocType", "Learning Mock Exam") and frappe.db.exists("Learning Mock Exam", EXAM_KEY):
		exam = frappe.get_doc("Learning Mock Exam", EXAM_KEY)
		max_attempts = int(exam.max_attempts or MAX_ATTEMPTS)
		format_note = exam.format_note or FORMAT_NOTE
		session_rows = list(exam.get("sessions") or [])
	else:
		session_rows = _course_session_rows()

	quizzes = [
		(row.get("lms_quiz") if isinstance(row, dict) else row.lms_quiz)
		for row in session_rows
		if (row.get("lms_quiz") if isinstance(row, dict) else row.lms_quiz)
	]
	attempts_by_quiz = {}
	latest_submission_by_quiz = {}
	for quiz in quizzes:
		attempts_by_quiz[quiz] = frappe.db.count("LMS Quiz Submission", {"quiz": quiz, "member": user})
		latest_submission_by_quiz[quiz] = frappe.db.get_value(
			"LMS Quiz Submission",
			{"quiz": quiz, "member": user},
			"name",
			order_by="creation desc",
		)

	return {
		"title": COURSE_TITLE,
		"format": format_note,
		"exam": EXAM_KEY,
		"lobby_url": LOBBY_URL,
		"enrolled": is_enrolled(user, EXAM_KEY),
		"mocks": group_lobby_sessions(session_rows, attempts_by_quiz, max_attempts, latest_submission_by_quiz),
	}


def unpublish_acl_course() -> dict:
	if not frappe.db.exists("LMS Course", COURSE_NAME):
		return {"ok": False, "reason": "course-missing"}
	frappe.db.set_value(
		"LMS Course",
		COURSE_NAME,
		{
			"published": 0,
			"disable_self_learning": 1,
		},
	)
	return {
		"ok": True,
		"course": COURSE_NAME,
		"published": 0,
		"disable_self_learning": 1,
	}
