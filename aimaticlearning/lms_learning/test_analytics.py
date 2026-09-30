import unittest

from aimaticlearning.lms_learning.analytics import _mastery_group


class TestMasteryGroup(unittest.TestCase):
	def test_flashcard_only_never_strong(self):
		# No MCQ attempts / coverage → not started even at 100%.
		self.assertEqual(_mastery_group(100, 0, covered=False), "not_started")

	def test_partial_mcq_high_score_is_developing_not_strong(self):
		self.assertEqual(_mastery_group(100, 1, covered=False), "developing")
		self.assertEqual(_mastery_group(80, 5, covered=False), "developing")

	def test_full_cover_good_marks_is_strong(self):
		self.assertEqual(_mastery_group(75, 20, covered=True), "strong")
		self.assertEqual(_mastery_group(90, 20, covered=True), "strong")

	def test_full_cover_weak_marks_is_needs_work(self):
		self.assertEqual(_mastery_group(40, 20, covered=True), "needs_work")
		self.assertEqual(_mastery_group(55, 20, covered=True), "developing")

	def test_quiz_submission_cover_without_detail_rows(self):
		# Submission exists (covered) with good % and zero detail rows still strong.
		self.assertEqual(_mastery_group(85, 0, covered=True), "strong")
