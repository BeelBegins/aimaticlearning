import unittest
from datetime import date

from aimaticlearning.lms_learning.student_dashboard import (
	first_name,
	hours_from_seconds,
	lesson_kind,
	mix_ratio,
	pace_status,
	pick_next_action,
	plain_title,
	quiz_kind,
	score_change,
	score_percent,
	sitting_is_complete,
	study_start_date,
	week_start,
	weekly_progress,
)


class TestDashboardHelpers(unittest.TestCase):
	def test_hours_are_omitted_when_nothing_was_timed(self):
		self.assertIsNone(hours_from_seconds(0))
		self.assertIsNone(hours_from_seconds(None))
		self.assertEqual(hours_from_seconds(3600), 1.0)
		self.assertEqual(hours_from_seconds(5400), 1.5)

	def test_lesson_kind_from_title_and_quiz(self):
		self.assertEqual(lesson_kind("Study notes — Directors", None), "notes")
		self.assertEqual(lesson_kind("Chapter 1 Practice MCQ", "QZ-1"), "mcq")
		self.assertEqual(lesson_kind("Module Assessment — 150 MCQs", "QZ-MA"), "module")
		self.assertEqual(lesson_kind("Flashcards — Directors", None), "flashcard")
		self.assertEqual(lesson_kind("Flashcards — Directors", "QZ-F"), "flashcard")

	def test_quiz_kind_classifies_exam_and_module(self):
		self.assertEqual(quiz_kind("mock-1", "sqe1-hard-mocks", "Mock 1", set()), "mock")
		self.assertEqual(quiz_kind("MA-1", "contract-law", "Contract", {"MA-1"}), "module")
		self.assertEqual(quiz_kind("CH-1", "contract-law", "Chapter 1 MCQ", set()), "practice")

	def test_mix_and_score_math(self):
		self.assertEqual(mix_ratio(46, 123), 37.4)
		self.assertEqual(mix_ratio(0, 0), 0.0)
		self.assertEqual(score_percent(3, 4), 75.0)
		self.assertEqual(score_percent(0, 0), 0.0)
		self.assertEqual(score_change(80, 60), 20.0)
		self.assertIsNone(score_change(80, None))

	def test_first_name_prefers_given_name(self):
		self.assertEqual(first_name("Ada Lovelace", "Ada"), "Ada")
		self.assertEqual(first_name("Ada Lovelace"), "Ada")
		self.assertEqual(first_name("Nabeel Ahmed", "Nabeel Ahmed"), "Nabeel")
		self.assertEqual(first_name(""), "there")

	def test_partial_paper_is_not_a_completed_sitting(self):
		self.assertFalse(sitting_is_complete(85, 7))
		self.assertFalse(sitting_is_complete(85, 44))
		self.assertTrue(sitting_is_complete(85, 85))
		self.assertFalse(sitting_is_complete(0, 0))

	def test_weekly_progress_does_not_invent_hours(self):
		series = weekly_progress(
			[date(2026, 5, 4), date(2026, 5, 5), date(2026, 6, 1)],
			start=date(2026, 5, 1),
			sitting=date(2026, 6, 15),
			today=date(2026, 6, 1),
			target=100,
		)
		self.assertEqual(series["unit"], "items")
		self.assertEqual(series["actual"][-1]["value"], 3)
		self.assertTrue(any(point["value"] >= 2 for point in series["actual"]))
		self.assertEqual(series["planned"][-1]["value"], 100)
		self.assertIn(series["pace"], {"behind", "on_track", "ahead", "unstarted"})

	def test_pace_thresholds(self):
		self.assertEqual(pace_status(0, 10), "unstarted")
		self.assertEqual(pace_status(11, 10), "ahead")
		self.assertEqual(pace_status(10, 10), "on_track")
		self.assertEqual(pace_status(8, 10), "behind")

	def test_study_start_uses_first_observed_date(self):
		start = study_start_date(
			[date(2026, 9, 10), date(2026, 9, 21)],
			today=date(2026, 9, 25),
			sitting=date(2027, 1, 31),
		)
		self.assertEqual(start, date(2026, 9, 10))

	def test_plain_title_drops_generated_dashes(self):
		self.assertEqual(plain_title("Chapter MCQ — Chapter 5: Directors"), "Chapter 5: Directors")
		self.assertEqual(plain_title("Flashcards — Chapter 4: Intestacy"), "Chapter 4: Intestacy")
		self.assertEqual(
			plain_title("Quick Revision Notes — Key Concepts & Glossary"),
			"Quick Revision Notes: Key Concepts & Glossary",
		)
		self.assertEqual(plain_title("Chapter 11: Damages"), "Chapter 11: Damages")
		self.assertNotIn("—", plain_title("One --- two"))

	def test_week_start_is_monday(self):
		self.assertEqual(week_start(date(2026, 9, 25)), date(2026, 9, 21))

	def test_next_action_prefers_hard_cards_then_continue(self):
		mix = {
			"notes": {"done": 1, "total": 10},
			"mcq": {"done": 1, "total": 10},
		}
		hard = pick_next_action(mix, {"title": "Notes", "href": "/lms/x", "detail": "d"}, 4)
		self.assertEqual(hard["href"], "/learning-revision")
		self.assertNotIn("another pass", hard["detail"])
		cont = pick_next_action(mix, {"title": "Notes", "href": "/lms/x", "detail": "d"}, 0)
		self.assertEqual(cont["href"], "/lms/x")
		empty = pick_next_action(
			{"notes": {"done": 10, "total": 10}, "mcq": {"done": 10, "total": 10}},
			None,
			0,
		)
		self.assertEqual(empty["href"], "/learning-mock-exam")
