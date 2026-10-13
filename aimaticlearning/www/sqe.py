import frappe

from aimaticlearning.lms_learning.public_site import flk_catalogue, mock_facts, page_context


def get_context(context):
	page_context(context, **flk_catalogue(), **mock_facts())
	context.title = "Examic | SQE1 Preparation for England and Wales"
	context.meta_description = (
		"Prepare for SQE1 with structured notes, chapter practice questions, flashcards and timed "
		"mock exams. First month free, no payment card needed."
	)
	context.body_class = "sqe-public-page"
	# Hardcoded, not frappe.utils.get_url(): examic.study is the public brand and must be
	# the one canonical/OG host everywhere (matches the JSON-LD provider URL below and
	# aimaticlearning/www/sitemap.py).
	context.canonical_url = "https://examic.study/"
	context.og_image = "https://examic.study/assets/aimaticlearning/images/examic-study-header-uk.png"
	context.login_url = "/login"
	context.signup_url = "/login#signup"
	context.courses_url = "/lms/courses"
	context.viewer = _get_viewer_state()
	context.course_schema = _get_course_schema(context.flk1_courses + context.flk2_courses)
	return context


def _get_course_schema(courses: list[dict]) -> str:
	"""JSON-LD ItemList of Course entries so AI/search crawlers can read course
	facts directly, without executing the course-detail SPA's JavaScript."""
	site_url = "https://examic.study"
	provider = {"@type": "EducationalOrganization", "name": "Examic", "legalName": "EXAMIC LTD", "url": site_url}
	items = [
		{
			"@type": "ListItem",
			"position": idx,
			"item": {
				"@type": "Course",
				"name": course["title"],
				"description": course["summary"],
				"url": f"{site_url}{course['course_url']}",
				"provider": provider,
			},
		}
		for idx, course in enumerate(courses, start=1)
	]
	schema = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": items}
	return frappe.as_json(schema)


def _get_viewer_state() -> dict:
	user = frappe.session.user
	if user == "Guest":
		return {"mode": "visitor"}

	enrolments = frappe.get_all(
		"LMS Enrollment",
		filters={"member": user, "docstatus": 0},
		fields=["course", "modified"],
		order_by="modified desc",
		limit_page_length=1,
	)
	if not enrolments:
		return {"mode": "new"}

	course_name = enrolments[0].course
	if not frappe.db.get_value("LMS Course", course_name, "published"):
		return {"mode": "new"}

	course = frappe.get_doc("LMS Course", course_name)
	total_lessons = sum(
		len(frappe.get_doc("Course Chapter", row.chapter).lessons or [])
		for row in course.chapters or []
	)
	completed = frappe.db.count(
		"LMS Course Progress",
		{"member": user, "course": course.name, "status": "Complete"},
	)
	completed = min(completed, total_lessons)
	progress = round((completed / total_lessons) * 100) if total_lessons else 0
	return {
		"mode": "student",
		"course_name": course.name,
		"course_title": course.title,
		"completed": completed,
		"total_lessons": total_lessons,
		"progress": progress,
		"course_url": f"/lms/courses/{course.name}",
	}
