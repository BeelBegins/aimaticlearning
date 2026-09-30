app_name = "aimaticlearning"
app_title = "Aimatic Learning"
app_publisher = "Aimatic"
app_description = "Aimatic-owned LMS features"
app_email = "sthassan41@gmail.com"
app_license = "mit"
app_logo_url = "/assets/aimaticlearning/images/examic-study-mark.svg"
app_home = "/desk/lms-learning"

required_apps = ["lms"]

after_install = "aimaticlearning.setup.after_install"

doc_events = {
	"LMS Enrollment": {
		"after_insert": "aimaticlearning.lms_learning.enrollment.send_course_enrollment_email",
	},
	"User": {
		"after_insert": "aimaticlearning.lms_learning.enrollment.send_student_welcome_email",
	},
	"Course Lesson": {
		"validate": "aimaticlearning.lms_learning.outline_sync.enforce_empty_quiz_content",
	},
}

# Lesson audio generation is a manual "Generate Audio" button on the form,
# never automatic on save - see public/js/course_lesson_audio_button.js.
doctype_js = {
	"Course Lesson": "public/js/course_lesson_audio_button.js",
}

app_include_js = ["/assets/aimaticlearning/js/studio_page_cache.js?v=20260924-dirty3"]

website_route_rules = [
	{"from_route": "/learning-notes/<chapter_profile>", "to_route": "learning_notes"},
	{"from_route": "/learning-flashcards", "to_route": "learning_flashcards"},
	{"from_route": "/learning-dashboard", "to_route": "learning_dashboard"},
	{"from_route": "/learning-revision", "to_route": "learning_revision"},
	{"from_route": "/learning-mock-report", "to_route": "learning_mock_report"},
	{"from_route": "/learning-mock-exam", "to_route": "learning_mock_exam"},
]

page_renderer = [
	"aimaticlearning.lms_learning.page_renderer.AimaticLMSPageRenderer",
]

lms_markdown_macro_renderers = {
	"AimaticChapterHub": "aimaticlearning.lms_learning.lesson_macros.chapter_hub_renderer",
}

web_include_css = [
	"/assets/aimaticlearning/css/lms_learning.css?v=20260925-buddy5",
	"/assets/aimaticlearning/css/lms_soft_themes.css?v=20260917-railfix2",
]
web_include_js = [
	"/assets/aimaticlearning/js/lms_learning.js?v=20260925-buddy5",
	"/assets/aimaticlearning/js/lms_soft_themes.js?v=20260917-frappe8",
]

update_website_context = [
	"aimaticlearning.lms_learning.enrollment.update_website_context",
]

signup_form_template = "aimaticlearning.lms_learning.enrollment.show_student_signup_form"

override_whitelisted_methods = {
	"lms.lms.api.get_chart_details": "aimaticlearning.lms_learning.statistics.get_chart_details",
	"lms.lms.api.get_sidebar_settings": "aimaticlearning.lms_learning.statistics.get_sidebar_settings",
	"lms.lms.utils.get_chart_data": "aimaticlearning.lms_learning.statistics.get_chart_data",
	"lms.lms.utils.get_course_completion_data": "aimaticlearning.lms_learning.statistics.get_course_completion_data",
	"lms.lms.utils.get_course_details": "aimaticlearning.lms_learning.outline_sync.get_course_details",
	"lms.lms.utils.get_courses": "aimaticlearning.lms_learning.exam_surface.get_courses",
	"lms.lms.utils.get_course_count": "aimaticlearning.lms_learning.exam_surface.get_course_count",
	"lms.lms.api.get_my_courses": "aimaticlearning.lms_learning.exam_surface.get_my_courses",
	"lms.lms.utils.get_related_courses": "aimaticlearning.lms_learning.exam_surface.get_related_courses",
}
