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


class TestFreeMockLock(unittest.TestCase):
	def test_only_first_two_sittings_are_open(self):
		from aimaticlearning.lms_learning import exam_product as ep

		self.assertEqual([ep.is_sitting_locked(i) for i in (1, 2, 3, 4)], [False, False, True, True])

	def test_quiz_name_maps_to_sitting(self):
		from aimaticlearning.lms_learning import exam_product as ep

		self.assertEqual(ep.quiz_sitting_number("mock-3-flk1-session-1-x"), 3)
		self.assertIsNone(ep.quiz_sitting_number("blp-module-assessment-150-mcqs"))
		self.assertTrue(ep.is_quiz_locked("mock-4-flk2-session-2-x"))
		self.assertFalse(ep.is_quiz_locked("mock-4-flk2-session-2-x", unlock_all=True))
		self.assertFalse(ep.is_quiz_locked("mock-2-flk1-session-1-x"))

	def test_lobby_withholds_start_url_when_locked(self):
		from aimaticlearning.lms_learning import exam_product as ep

		rows = [
			{"sitting_index": i, "sitting_title": f"Mock {i}", "session_title": "S", "lms_quiz": f"mock-{i}-a"}
			for i in (1, 3)
		]
		mocks = ep.group_lobby_sessions(rows, free_sittings=ep.FREE_SITTINGS)
		self.assertTrue(mocks[0]["sessions"][0]["start_url"])
		self.assertEqual(mocks[1]["sessions"][0]["start_url"], "")
		self.assertTrue(mocks[1]["locked"])
