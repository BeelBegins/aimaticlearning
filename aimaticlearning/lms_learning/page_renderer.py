import json
import re

import frappe
from frappe.website.page_renderers.redirect_page import RedirectPage
from frappe.website.page_renderers.template_page import TemplatePage

from aimaticlearning.lms_learning.statistics import can_view_statistics

ASSET_MARKER = "examic-study-learning-assets"
# Runs before the LMS Vue bundle. Quiz.vue's production setup() returns only a
# render function, so activeQuestion is not on the component instance. Capture
# Vue refs as they are created, then the chapter MCQ arrows can move that ref.
QUIZ_NAV_BOOT = """<script>
(function () {
	if (window.__examicRefBoot) return;
	window.__examicRefBoot = true;
	window.__examicRefs = [];
	window.__examicArrays = [];
	Object.defineProperty(Object.prototype, "__v_isRef", {
		configurable: true,
		enumerable: false,
		get: function () { return false; },
		set: function (value) {
			Object.defineProperty(this, "__v_isRef", {
				value: !!value,
				writable: true,
				configurable: true,
				enumerable: false
			});
			if (value) window.__examicRefs.push(this);
		}
	});
	var OrigProxy = window.Proxy;
	function ExamicProxy(target, handler) {
		var obj = new OrigProxy(target, handler);
		if (Array.isArray(target)) window.__examicArrays.push(obj);
		return obj;
	}
	ExamicProxy.revocable = function (target, handler) {
		var boxed = OrigProxy.revocable(target, handler);
		if (Array.isArray(target)) window.__examicArrays.push(boxed.proxy);
		return boxed;
	};
	window.Proxy = ExamicProxy;
})();
</script>
"""
ASSET_TAGS = f'''<!-- {ASSET_MARKER} -->
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_learning.css?v=20261009-split1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_kinnu.css?v=20260917-railfix1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_student_experience.css?v=20261008-themelock1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_student_dashboard.css?v=20261005-dash6">
<link rel="stylesheet" href="/assets/aimaticlearning/css/examic_sessions.css?v=20260917-flash1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_exam_tools.css?v=20261026-pearson7">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lesson_audio.css?v=20260907-1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/lms_soft_themes.css?v=20261008-themelock5">
<script defer src="/assets/aimaticlearning/js/lms_dom_observe.js?v=20260902-1"></script>
<script defer src="/assets/aimaticlearning/js/course_content_navigation.js?v=20261013-1"></script>
<script defer src="/assets/aimaticlearning/js/lms_learning.js?v=20261009-split1"></script>
<script defer src="/assets/aimaticlearning/js/lms_soft_themes.js?v=20261008-themelock5"></script>
<script defer src="/assets/aimaticlearning/js/lms_kinnu.js?v=20260902-1"></script>
<script defer src="/assets/aimaticlearning/js/lms_student_experience.js?v=20261027-collapse3"></script>
<script defer src="/assets/aimaticlearning/js/lms_student_dashboard.js?v=20261005-dash6"></script>
<script defer src="/assets/aimaticlearning/js/examic_sessions.js?v=20260925-flashcard1"></script>
<script defer src="/assets/aimaticlearning/js/lms_exam_tools.js?v=20261026-pearson7"></script>
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

		if path.startswith("/lms/quiz/"):
			from aimaticlearning.lms_learning.exam_product import can_unlock_all_mocks, is_quiz_locked

			if is_quiz_locked(path.rsplit("/", 1)[-1], can_unlock_all_mocks()):
				frappe.flags.redirect_location = "/learning-mock-exam"
				return RedirectPage("/learning-mock-exam", 302).render()

		response = super().render()
		html = response.get_data(as_text=True)
		if _is_student_view():
			html = mark_student_body(html)
		if _is_exam_sitting_path(path):
			html = mark_exam_sitting_body(html)
		if ASSET_MARKER not in html:
			html = html.replace("</head>", f"{_study_features_script()}{ASSET_TAGS}\n</head>", 1)
		if "__examicRefBoot" not in html:
			html = html.replace("<script type=\"module\"", QUIZ_NAV_BOOT + "<script type=\"module\"", 1)
		response.set_data(html)
		return response


def _study_features_script() -> str:
	"""Flags for the learner script so Study Buddy and live chat do not flash on."""
	fallback = {
		"study_buddy_enabled": True,
		"helpful_text": "Approved chapter context is selected automatically.",
		"live_chat_enabled": False,
		"live_chat_open": False,
		"live_chat_greeting": "",
		"live_chat_offline_message": "",
		"live_chat_hours": "",
		"starter_prompts": [],
	}
	try:
		from aimaticlearning.lms_learning.study_settings import public_features

		payload = public_features()
	except Exception:
		payload = fallback
	encoded = json.dumps(payload, ensure_ascii=True).replace("<", "\\u003c")
	return f"<script>window.examicStudyFeatures = {encoded};</script>\n"


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
