import unittest

from aimaticlearning.lms_learning.page_renderer import mark_student_body


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
