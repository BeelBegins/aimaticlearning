import re

import frappe
from frappe.website.page_renderers.redirect_page import RedirectPage
from frappe.website.page_renderers.template_page import TemplatePage

from aimaticlearning.lms_learning.statistics import can_view_statistics

ASSET_MARKER = "examic-study-learning-assets"
ASSET_TAGS = f'''<!-- {ASSET_MARKER} -->
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_learning.css?v=20260917-studentmeta2">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_kinnu.css?v=20260917-railfix1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_student_experience.css?v=20261002-flag2">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_student_dashboard.css?v=20260925-dash4">
<link rel="stylesheet" href="/assets/aimaticlearning/css/examic_sessions.css?v=20260917-flash1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_exam_tools.css?v=20261001-calc1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lesson_audio.css?v=20260907-1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_soft_themes.css?v=20260917-railfix2">
<script defer src="/assets/aimaticlearning/js/lms_dom_observe.js?v=20260902-1"></script>
<script defer src="/assets/aimaticlearning/js/lms_learning.js?v=20260917-buddy4"></script>
<script defer src="/assets/aimaticlearning/js/lms_soft_themes.js?v=20260917-frappe8"></script>
<script defer src="/assets/aimaticlearning/js/lms_kinnu.js?v=20260902-1"></script>
<script defer src="/assets/aimaticlearning/js/lms_student_experience.js?v=20261001-flag1"></script>
<script defer src="/assets/aimaticlearning/js/lms_student_dashboard.js?v=20260925-dash4"></script>
<script defer src="/assets/aimaticlearning/js/examic_sessions.js?v=20260925-flashcard1"></script>
<script defer src="/assets/aimaticlearning/js/lms_exam_tools.js?v=20261001-calc1"></script>
<script defer src="/assets/aimaticlearning/js/lesson_audio.js?v=20260909-1"></script>'''


class AimaticLMSPageRenderer(TemplatePage):
	"""Decorate the LMS-owned SPA shell with Examic Study learner experience assets."""

	def can_render(self):
		return self.path == "_lms" and super().can_render()

	def render(self):
		path = frappe.local.request.path.rstrip("/")
		if path == "/lms/statistics" and not can_view_statistics():
			frappe.flags.redirect_location = "/lms/courses"
			return RedirectPage("/lms/courses", 302).render()
		if path == "/lms/courses/sqe1-hard-mocks":
			frappe.flags.redirect_location = "/learning-mock-exam"
			return RedirectPage("/learning-mock-exam", 302).render()

		response = super().render()
		html = response.get_data(as_text=True)
		if _is_student_view():
			html = mark_student_body(html)
		if _is_exam_sitting_path(path):
			html = mark_exam_sitting_body(html)
		if ASSET_MARKER not in html:
			html = html.replace("</head>", f"{ASSET_TAGS}\n</head>", 1)
		response.set_data(html)
		return response


def mark_student_body(html: str) -> str:
	"""Keep the LMS body tag intact while adding the student chrome class."""
	if "aimatic-lms-student" in html:
		return html
	return re.sub(
		r'(<body\s+class="[^"]*)"',
		lambda match: f'{match.group(1)} aimatic-lms-student"',
		html,
		count=1,
	)


def mark_exam_sitting_body(html: str) -> str:
	"""Mark timed mock sittings so learner chrome can hide course UI."""
	if "aimatic-exam-sitting" in html:
		return html
	return re.sub(
		r'(<body\s+class="[^"]*)"',
		lambda match: f'{match.group(1)} aimatic-exam-sitting"',
		html,
		count=1,
	)



def _is_student_view() -> bool:
	"""Mark only ordinary LMS students; keep staff/admin views unchanged."""
	roles = set(frappe.get_roles())
	privileged_roles = {
		"Administrator",
		"System Manager",
		"LMS Administrator",
		"LMS Moderator",
		"LMS Instructor",
	}
	return "LMS Student" in roles and not roles.intersection(privileged_roles)


def _is_exam_sitting_path(path: str) -> bool:
	if path.startswith("/lms/courses/sqe1-hard-mocks/learn/"):
		return True
	if not path.startswith("/lms/quiz/"):
		return False
	quiz = path.rsplit("/", 1)[-1]
	if not quiz:
		return False
	from aimaticlearning.lms_learning.exam_product import is_exam_quiz

	return is_exam_quiz(quiz)
