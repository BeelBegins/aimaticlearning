import unittest

from aimaticlearning.lms_learning.study_buddy import (
	_system_prompt,
	format_attempt_context,
	format_history_turns,
	parse_attempt_context,
	study_buddy_log_values,
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
		self.assertIn("**double asterisks**", prompt)


class TestStudyBuddyChatLog(unittest.TestCase):
	def test_log_values_keep_question_and_omit_lesson_body(self):
		values = study_buddy_log_values(
			user="student@example.com",
			course="business-law-practice-blp",
			lesson_row={
				"name": "0062 Chapter MCQ",
				"title": "Chapter MCQ",
				"chapter": "CH-1",
				"body": "SECRET LESSON BODY",
			},
			chapter=1,
			lesson=4,
			question="What is VAT?",
			answer="VAT is a consumption tax.",
			model="deepseek/deepseek-v4-flash",
			grounded=True,
			has_attempt_context=True,
			status="Answered",
		)
		self.assertEqual(values["doctype"], "Study Buddy Chat Log")
		self.assertEqual(values["question"], "What is VAT?")
		self.assertEqual(values["preview"], "What is VAT?")
		self.assertEqual(values["model"], "deepseek/deepseek-v4-flash")
		self.assertEqual(values["status"], "Answered")
		self.assertEqual(values["grounded"], 1)
		self.assertNotIn("body", values)
		self.assertNotIn("SECRET LESSON BODY", str(values))
		self.assertNotIn("system", str(values).lower())

	def test_history_turns_drop_empty_and_keep_pairs(self):
		turns = format_history_turns(
			[
				{"question": "What is VAT?", "answer": "A consumption tax.", "user": "other@example.com"},
				{"question": "Skipped fail", "answer": ""},
				{"question": "", "answer": "No question"},
				{"question": "Second?", "answer": "Yes."},
			]
		)
		self.assertEqual(
			turns,
			[
				{"question": "What is VAT?", "answer": "A consumption tax."},
				{"question": "Second?", "answer": "Yes."},
			],
		)
		self.assertNotIn("other@example.com", str(turns))
