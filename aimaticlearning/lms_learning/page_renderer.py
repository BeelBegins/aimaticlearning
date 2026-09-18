import re

import frappe
from frappe.website.page_renderers.redirect_page import RedirectPage
from frappe.website.page_renderers.template_page import TemplatePage

from aimaticlearning.lms_learning.statistics import can_view_statistics

ASSET_MARKER = "examic-study-learning-assets"
ASSET_TAGS = f'''<!-- {ASSET_MARKER} -->
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_learning.css?v=20260917-studentmeta2">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_kinnu.css?v=20260917-railfix1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_student_experience.css?v=20260917-exam1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/examic_sessions.css?v=20260917-flash1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lesson_audio.css?v=20260907-1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_soft_themes.css?v=20260917-railfix2">
<script defer src="/assets/aimaticlearning/js/lms_dom_observe.js?v=20260902-1"></script>
<script defer src="/assets/aimaticlearning/js/lms_learning.js?v=20260917-buddy4"></script>
<script defer src="/assets/aimaticlearning/js/lms_soft_themes.js?v=20260917-frappe8"></script>
<script defer src="/assets/aimaticlearning/js/lms_kinnu.js?v=20260902-1"></script>
<script defer src="/assets/aimaticlearning/js/lms_student_experience.js?v=20260917-exam1"></script>
<script defer src="/assets/aimaticlearning/js/examic_sessions.js?v=20260917-flash2"></script>
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
