import unittest

from aimaticlearning.lms_learning.revision import (
	_build_quiz_summary,
	_empty_mock_exam,
	apply_rating_filter,
	encode_recall_tags,
	latest_ratings_from_attempts,
	parse_recall_rating,
)


class TestRevisionRatings(unittest.TestCase):
	def test_encode_and_parse_explicit_rating(self):
		tags = encode_recall_tags("Hard", "Contract formation")
		self.assertTrue(tags.startswith("recall:hard"))
		self.assertEqual(parse_recall_rating(tags, correct=1), "hard")

	def test_legacy_correct_flag(self):
		self.assertEqual(parse_recall_rating("Offer and acceptance", 0), "hard")
		self.assertEqual(parse_recall_rating("Offer and acceptance", 1), "good")
		self.assertIsNone(parse_recall_rating("Offer and acceptance"))

	def test_latest_attempt_wins(self):
		ratings = latest_ratings_from_attempts(
			[
				{"learning_flashcard": "FC-1", "concept_tags": "recall:easy", "correct": 1},
				{"learning_flashcard": "FC-1", "concept_tags": "recall:hard", "correct": 0},
				{"learning_flashcard": "FC-2", "concept_tags": "recall:good", "correct": 1},
			]
		)
		self.assertEqual(ratings, {"FC-1": "easy", "FC-2": "good"})

	def test_filter_hard_and_unreviewed(self):
		cards = [{"name": "FC-1"}, {"name": "FC-2"}, {"name": "FC-3"}]
		ratings = {"FC-1": "hard", "FC-2": "easy"}
		hard = apply_rating_filter(cards, ratings, "hard")
		self.assertEqual([card["name"] for card in hard], ["FC-1"])
		unreviewed = apply_rating_filter(list(cards), ratings, "unreviewed")
		self.assertEqual([card["name"] for card in unreviewed], ["FC-3"])


class TestRevisionAssessments(unittest.TestCase):
	def test_quiz_summary_separates_chapter_and_mock_attempts(self):
		history = [
			{"percentage": 80, "passed": True, "kind": "mock_exam"},
			{"percentage": 50, "passed": False, "kind": "chapter_mcq"},
		]
		self.assertEqual(
			_build_quiz_summary(history),
			{
				"attempts": 2,
				"passed": 1,
				"failed": 1,
				"pass_rate_pct": 50.0,
				"average_pct": 65.0,
				"chapter_mcq_attempts": 1,
				"mock_exam_attempts": 1,
				"latest": history[0],
			},
		)

	def test_empty_mock_exam_is_explicitly_unavailable(self):
		self.assertFalse(_empty_mock_exam()["available"])
		self.assertIsNone(_empty_mock_exam()["url"])
