import unittest

from aimaticlearning.lms_learning.revision import (
	apply_rating_filter,
	encode_recall_tags,
	latest_mcq_results_from_attempts,
	latest_ratings_from_attempts,
	lesson_title_matches_activity,
	parse_recall_rating,
	rank_revision_recommendations,
	summarise_mcq_results,
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

	def test_strong_mastery_chapters_without_work_are_hidden(self):
		from aimaticlearning.lms_learning.revision import include_chapter_on_revision_board

		self.assertFalse(include_chapter_on_revision_board("strong", hard_cards=0, incorrect_mcqs=0))
		self.assertTrue(include_chapter_on_revision_board("strong", hard_cards=2, incorrect_mcqs=0))
		self.assertTrue(include_chapter_on_revision_board("needs_work", hard_cards=0, incorrect_mcqs=0))
		self.assertTrue(include_chapter_on_revision_board("not_started"))


class TestRevisionMcqAttempts(unittest.TestCase):
	def test_mcq_attempts_are_included_and_flashcards_are_skipped(self):
		results = latest_mcq_results_from_attempts(
			[
				{
					"lms_question": "Q-1",
					"learning_flashcard": None,
					"correct": 0,
					"course_chapter": "CH-1",
					"concept_tags": "Directors",
				},
				{
					"lms_question": "Q-1",
					"learning_flashcard": None,
					"correct": 1,
					"course_chapter": "CH-1",
					"concept_tags": "Directors",
				},
				{
					"lms_question": "Q-2",
					"learning_flashcard": None,
					"correct": 1,
					"course_chapter": "CH-2",
					"concept_tags": "VAT",
				},
				{
					"lms_question": None,
					"learning_flashcard": "FC-1",
					"correct": 0,
					"course_chapter": "CH-1",
					"concept_tags": "recall:hard",
				},
			]
		)
		self.assertEqual(set(results), {"Q-1", "Q-2"})
		self.assertEqual(results["Q-1"]["correct"], 0)
		self.assertEqual(results["Q-2"]["correct"], 1)

	def test_mcq_summary_counts_incorrect_and_quiz_history(self):
		results = {
			"Q-1": {"correct": 0, "course_chapter": "CH-1"},
			"Q-2": {"correct": 1, "course_chapter": "CH-1"},
			"Q-3": {"correct": 0, "course_chapter": "CH-2"},
		}
		summary = summarise_mcq_results(results, [{"percentage": 40}, {"percentage": 80}])
		self.assertEqual(summary["attempted"], 3)
		self.assertEqual(summary["correct"], 1)
		self.assertEqual(summary["incorrect"], 2)
		self.assertEqual(summary["quizzes"], 2)


class TestRevisionLessonTitles(unittest.TestCase):
	def test_flashcard_and_mcq_title_patterns(self):
		self.assertTrue(lesson_title_matches_activity("Flashcards", "flashcard"))
		self.assertTrue(lesson_title_matches_activity("Flashcards — Directors", "flashcard"))
		self.assertTrue(lesson_title_matches_activity("Practice MCQs", "mcq"))
		self.assertTrue(lesson_title_matches_activity("Chapter 1 — Practice MCQs", "mcq"))
		self.assertTrue(lesson_title_matches_activity("SQE1 Practice Questions", "mcq"))
		self.assertTrue(lesson_title_matches_activity("MCQ Practice", "mcq"))
		self.assertFalse(lesson_title_matches_activity("Flashcards", "mcq"))
		self.assertFalse(lesson_title_matches_activity("Forms of Business Organisations", "mcq"))
		self.assertFalse(lesson_title_matches_activity("Practice MCQs", "flashcard"))


class TestRevisionRecommendationRanking(unittest.TestCase):
	def test_hard_cards_outrank_weak_concepts_and_incorrect_mcqs(self):
		recs = rank_revision_recommendations(
			flashcards={"published": 40, "hard": 5, "good": 2, "easy": 1, "unreviewed": 32},
			has_ratings=True,
			weaknesses=[{"concept": "VAT", "mastery_pct": 40, "attempts": 4}],
			chapters=[
				{"chapter_title": "Directors", "group": "needs_work", "mcq_url": "/lms/mcq"},
			],
			mcqs={"attempted": 6, "correct": 2, "incorrect": 4, "quizzes": 1},
			quiz_history=[{"quiz_title": "Directors — Practice MCQs", "percentage": 35}],
		)
		self.assertEqual(recs[0], "Revise 5 flashcards you rated Hard.")
		self.assertIn("Revisit Directors — mastery is below 50% after chapter attempts.", recs)
		self.assertIn("Review concept 'VAT' (40% over 4 attempts).", recs)
		self.assertIn("Retry 4 MCQs you answered incorrectly.", recs)
		self.assertTrue(any("Retake Directors — Practice MCQs" in item for item in recs))

	def test_incorrect_mcqs_rank_when_no_hard_cards(self):
		recs = rank_revision_recommendations(
			flashcards={"published": 10, "hard": 0, "good": 4, "easy": 3, "unreviewed": 3},
			has_ratings=True,
			weaknesses=[],
			chapters=[{"chapter_title": "LLPs", "group": "strong"}],
			mcqs={"attempted": 8, "correct": 5, "incorrect": 3, "quizzes": 1},
			quiz_history=[],
		)
		self.assertEqual(recs[0], "Retry 3 MCQs you answered incorrectly.")

	def test_empty_signals_point_to_mcqs_and_flashcards(self):
		recs = rank_revision_recommendations(
			flashcards={"published": 0, "hard": 0, "good": 0, "easy": 0, "unreviewed": 0},
			has_ratings=False,
			weaknesses=[],
			chapters=[],
			mcqs={"attempted": 0, "correct": 0, "incorrect": 0, "quizzes": 0},
			quiz_history=[],
		)
		self.assertTrue(any("chapter MCQs" in item for item in recs))
