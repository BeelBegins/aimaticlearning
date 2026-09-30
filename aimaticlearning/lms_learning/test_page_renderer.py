import unittest

from aimaticlearning.lms_learning.page_renderer import ASSET_TAGS, mark_exam_sitting_body, mark_student_body


class TestMarkStudentBody(unittest.TestCase):
	def test_keeps_body_tag_and_appends_class(self):
		html = '<html><body class="sm:overscroll-y-none no-scrollbar"><div>ok</div></body></html>'
		out = mark_student_body(html)
		self.assertIn('<body class="sm:overscroll-y-none no-scrollbar aimatic-lms-student">', out)
		self.assertNotIn('\nclass="sm:overscroll-y-none', out)
		self.assertTrue(out.startswith("<html><body "))

	def test_does_not_duplicate_class(self):
		html = '<body class="no-scrollbar aimatic-lms-student">'
		self.assertEqual(mark_student_body(html), html)

	def test_exam_sitting_class_appends_without_breaking_body(self):
		html = '<body class="sm:overscroll-y-none no-scrollbar">'
		out = mark_exam_sitting_body(html)
		self.assertIn("aimatic-exam-sitting", out)
		self.assertTrue(out.startswith("<body class="))
		self.assertEqual(mark_exam_sitting_body(out), out)

	def test_learning_assets_include_student_dashboard(self):
		self.assertIn("lms_student_dashboard.css", ASSET_TAGS)
		self.assertIn("lms_student_dashboard.js", ASSET_TAGS)
