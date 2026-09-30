"""Keep mock sittings off the student course catalogue.

QLTS and Barbri treat mocks as timed exam sittings inside a prep package, not as
syllabus subjects. Examic stores papers as LMS Course `sqe1-hard-mocks` so Frappe
LMS can run the quizzes, but learners enter at `/learning-mock-exam`.
"""

from __future__ import annotations

import json

import frappe

from aimaticlearning.lms_learning.sqe1_hard_mocks import COURSE_NAME

EXAM_COURSES = frozenset({COURSE_NAME})
STAFF_ROLES = frozenset(
	{
		"Administrator",
		"System Manager",
		"Course Creator",
		"Moderator",
		"Batch Evaluator",
		"LMS Content Reviewer",
		"LMS Administrator",
		"LMS Moderator",
		"LMS Instructor",
	}
)


def is_exam_course(name: str | None) -> bool:
	return bool(name) and name in EXAM_COURSES


def hide_exam_courses_for_session() -> bool:
	if frappe.session.user in (None, "Guest"):
		return True
	return not STAFF_ROLES.intersection(frappe.get_roles())


def without_exam_courses(rows: list) -> list:
	cleaned = []
	for row in rows or []:
		name = row.get("name") if isinstance(row, dict) else row
		if not is_exam_course(name):
			cleaned.append(row)
	return cleaned


def parsed_filters(filters: dict | str | None) -> dict:
	if not filters:
		return {}
	if isinstance(filters, str):
		filters = json.loads(filters)
	if not isinstance(filters, dict):
		return {}
	return dict(filters)


def catalog_filters(filters: dict | str | None) -> dict:
	filters = parsed_filters(filters)
	name = filters.get("name")
	if isinstance(name, (list, tuple)) and len(name) >= 2 and str(name[0]).lower() == "in":
		kept = [item for item in (name[1] or []) if not is_exam_course(item)]
		filters["name"] = ["in", kept]
		return filters
	if "name" not in filters:
		filters["name"] = ["not in", list(EXAM_COURSES)]
	return filters


def exam_courses_in_query(filters: dict | str | None) -> int:
	from lms.lms.utils import update_course_filters

	resolved = parsed_filters(filters)
	resolved, or_filters, _show_featured = update_course_filters(resolved)
	exam_names = list(EXAM_COURSES)
	name_filter = resolved.get("name")
	if isinstance(name_filter, (list, tuple)) and len(name_filter) >= 2:
		op, values = str(name_filter[0]).lower(), name_filter[1] or []
		if op == "in":
			exam_names = [name for name in exam_names if name in values]
		elif op == "not in":
			exam_names = [name for name in exam_names if name not in values]
	if not exam_names:
		return 0
	query = dict(resolved)
	query["name"] = ["in", exam_names]
	return len(frappe.get_all("LMS Course", filters=query, or_filters=or_filters or None, pluck="name"))


@frappe.whitelist(allow_guest=True)
def get_courses(filters: dict | None = None, start: int = 0, limit_page_length: int | str | None = None):
	from lms.lms.utils import get_courses as native_get_courses

	hide = hide_exam_courses_for_session()
	if hide:
		filters = catalog_filters(filters)
	rows = native_get_courses(filters=filters, start=start, limit_page_length=limit_page_length)
	return without_exam_courses(rows) if hide else rows


@frappe.whitelist(allow_guest=True)
def get_course_count(filters: dict | None = None):
	from lms.lms.utils import get_course_count as native_get_course_count

	hide = hide_exam_courses_for_session()
	parsed = catalog_filters(filters) if hide else parsed_filters(filters)
	count = native_get_course_count(filters=parsed)
	if hide:
		count = max(0, int(count or 0) - exam_courses_in_query(parsed))
	return count


@frappe.whitelist()
def get_my_courses():
	from lms.lms.api import get_my_courses as native_get_my_courses

	rows = native_get_my_courses()
	if hide_exam_courses_for_session():
		return without_exam_courses(rows)
	return rows


@frappe.whitelist(allow_guest=True)
def get_related_courses(course: str):
	from lms.lms.utils import get_related_courses as native_get_related_courses

	rows = native_get_related_courses(course)
	if hide_exam_courses_for_session():
		return without_exam_courses(rows)
	return rows
