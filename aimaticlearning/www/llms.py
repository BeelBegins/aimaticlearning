import frappe

from aimaticlearning.lms_learning.sqe_pathway import FLK1_SUBJECTS, FLK2_SUBJECTS

no_cache = 1
base_template_path = "www/llms.txt"

SITE_URL = "https://examic.study"


def get_context(context):
	context.site_url = SITE_URL
	context.flk1_courses = _published_courses(FLK1_SUBJECTS)
	context.flk2_courses = _published_courses(FLK2_SUBJECTS)
	return context


def _published_courses(subjects) -> list[dict]:
	courses = []
	for subject in subjects:
		if not frappe.db.get_value("LMS Course", subject["course"], "published"):
			continue
		courses.append(
			{
				"title": subject["title"],
				"summary": subject["summary"],
				"url": f"{SITE_URL}/lms/courses/{subject['course']}",
			}
		)
	return courses
