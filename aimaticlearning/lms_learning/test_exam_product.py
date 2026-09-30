import unittest

from aimaticlearning.lms_learning.exam_product import FORMAT_NOTE, group_lobby_sessions, quiz_sitting_url
from aimaticlearning.lms_learning.sqe1_hard_mocks import LOBBY_URL


class TestExamProduct(unittest.TestCase):
	def test_quiz_sitting_url_is_quiz_page_not_course_outline(self):
		self.assertEqual(quiz_sitting_url("mock-1-flk1-s1"), "/lms/quiz/mock-1-flk1-s1?fromLesson=1")
		self.assertEqual(quiz_sitting_url(""), LOBBY_URL)
		self.assertNotIn("/lms/courses/", quiz_sitting_url("mock-1-flk1-s1"))

	def test_group_lobby_sessions_keeps_sitting_order(self):
		rows = [
			{
				"sitting_index": 2,
				"sitting_title": "Mock 2",
				"session_index": 1,
				"session_title": "FLK1 Session 1",
				"lms_quiz": "q-2-1",
				"duration_minutes": 153,
				"question_count": 85,
			},
			{
				"sitting_index": 2,
				"sitting_title": "Mock 2",
				"session_index": 2,
				"session_title": "FLK1 Session 2",
				"lms_quiz": "q-2-2",
			},
			{
				"sitting_index": 1,
				"sitting_title": "Mock 1",
				"session_index": 1,
				"session_title": "FLK1 Session 1",
				"lms_quiz": "q-1-1",
			},
		]
		mocks = group_lobby_sessions(rows, {"q-2-1": 1}, max_attempts=3)
		self.assertEqual([item["title"] for item in mocks], ["Mock 2", "Mock 1"])
		self.assertEqual(mocks[0]["sessions"][0]["start_url"], "/lms/quiz/q-2-1?fromLesson=1")
		self.assertEqual(mocks[0]["sessions"][0]["attempts"], 1)
		self.assertEqual(mocks[0]["sessions"][1]["attempts"], 0)
		self.assertIn("153 minutes", FORMAT_NOTE)

	def test_enroll_helper_accepts_bypass_flag(self):
		import inspect

		from aimaticlearning.lms_learning.enrollment import enroll_member_in_course

		params = inspect.signature(enroll_member_in_course).parameters
		self.assertIn("bypass_self_learning_gate", params)
