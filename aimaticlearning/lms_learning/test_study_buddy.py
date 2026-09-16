import unittest

from aimaticlearning.lms_learning.study_buddy import (
	_system_prompt,
	format_attempt_context,
	parse_attempt_context,
)


class TestStudyBuddyAttemptContext(unittest.TestCase):
	def test_keeps_live_question_and_options(self):
		context = parse_attempt_context(
			{
				"question": "<p>Which tax applies?</p>",
				"options": ["VAT", "Income tax", "CGT"],
				"selected_options": ["VAT"],
				"question_index": 3,
				"quiz_title": "Directors — Practice MCQs",
				"correct_answer": "B",
				"explanation": "Do not leak this",
			}
		)
		self.assertEqual(context["question"], "Which tax applies?")
		self.assertEqual(context["options"], ["VAT", "Income tax", "CGT"])
		self.assertEqual(context["selected_options"], ["VAT"])
		self.assertEqual(context["question_index"], 3)
		self.assertNotIn("correct_answer", context)
		self.assertNotIn("explanation", context)
		text = format_attempt_context(context)
		self.assertIn("Question: Which tax applies?", text)
		self.assertIn("Option A: VAT", text)
		self.assertNotIn("Do not leak this", text)

	def test_rejects_empty_or_invalid_payloads(self):
		self.assertIsNone(parse_attempt_context(""))
		self.assertIsNone(parse_attempt_context("not-json"))
		self.assertIsNone(parse_attempt_context({"correct_answer": "A"}))
		self.assertIsNone(parse_attempt_context({"options": "A"}))

	def test_system_prompt_includes_live_mcq_block(self):
		prompt = _system_prompt("Practice MCQs", "Approved notes.", "Question: Which tax applies?")
		self.assertIn("Live MCQ the learner is looking at", prompt)
		self.assertIn("Question: Which tax applies?", prompt)
		self.assertIn("Approved notes.", prompt)
