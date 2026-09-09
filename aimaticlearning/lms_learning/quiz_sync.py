from __future__ import annotations

import frappe


def sync_quiz_submission_event(doc: frappe.Document, method: str | None = None) -> dict:
	"""Mirror one native LMS submission into the learner analytics model."""
	return sync_quiz_submission(doc.name)


def sync_quiz_submission(submission_name: str) -> dict:
	"""Store explicit MCQ results once, preserving the native submission as source."""
	submission = frappe.get_doc("LMS Quiz Submission", submission_name)
	module = _module_for_submission(submission)
	if not module:
		return {
			"submission": submission_name,
			"created": 0,
			"skipped": 0,
			"unresolved": 0,
			"reason": "no_learning_module",
		}

	chapter_for_quiz = _chapter_for_quiz(module, submission.quiz)
	created = 0
	skipped = 0
	unresolved = 0
	for result in submission.get("result") or []:
		question_name = result.get("question_name")
		if not question_name or result.get("is_correct") is None:
			unresolved += 1
			continue
		if _question_type(submission.quiz, question_name) == "Open Ended":
			skipped += 1
			continue

		meta = frappe.db.get_value(
			"Learning Question Meta",
			{"lms_question": question_name},
			["learning_module", "course_chapter", "concept", "revision"],
			as_dict=True,
		)
		if meta and meta.learning_module and meta.learning_module != module.name:
			unresolved += 1
			continue

		course_chapter = (meta and meta.course_chapter) or chapter_for_quiz
		filters = {
			"user": submission.member,
			"learning_module": module.name,
			"lms_question": question_name,
			"quiz_submission": submission.name,
		}
		if frappe.db.exists("Learning Attempt Detail", filters):
			skipped += 1
			continue

		frappe.get_doc(
			{
				"doctype": "Learning Attempt Detail",
				"user": submission.member,
				"learning_module": module.name,
				"course_chapter": course_chapter,
				"lms_question": question_name,
				"quiz_submission": submission.name,
				"correct": int(bool(result.get("is_correct"))),
				"attempt_order": int(result.get("idx") or 0),
				"concept_tags": meta and meta.concept,
				"question_revision": meta and meta.revision,
			}
		).insert(ignore_permissions=True)
		created += 1

	return {
		"submission": submission_name,
		"created": created,
		"skipped": skipped,
		"unresolved": unresolved,
	}


def sync_existing_quiz_submissions(limit: int | None = None) -> dict:
	"""Backfill old submissions; intended for an authorized maintenance run."""
	frappe.only_for(("System Manager", "Course Creator", "LMS Content Reviewer"))
	page_length = max(min(int(limit or 10000), 10000), 1)
	rows = frappe.get_all(
		"LMS Quiz Submission",
		fields=["name"],
		order_by="creation asc",
		limit_page_length=page_length,
	)
	totals = {"processed": 0, "created": 0, "skipped": 0, "unresolved": 0}
	for row in rows:
		result = sync_quiz_submission(row.name)
		totals["processed"] += 1
		for key in ("created", "skipped", "unresolved"):
			totals[key] += int(result.get(key) or 0)
	frappe.db.commit()
	return totals


def _module_for_submission(submission: frappe.Document):
	course = submission.course or frappe.db.get_value("LMS Quiz", submission.quiz, "course")
	if not course:
		return None
	return frappe.db.get_value(
		"Learning Module Config",
		{"lms_course": course},
		["name", "lms_course", "module_assessment_quiz"],
		as_dict=True,
	)


def _chapter_for_quiz(module: frappe._dict, quiz: str | None) -> str | None:
	if not quiz or quiz == module.module_assessment_quiz:
		return None
	return frappe.db.get_value(
		"Learning Chapter Profile",
		{"learning_module": module.name, "chapter_quiz": quiz},
		"course_chapter",
	)


def _question_type(quiz: str, question_name: str) -> str | None:
	return frappe.db.get_value(
		"LMS Quiz Question",
		{"parent": quiz, "question": question_name},
		"type",
	)
