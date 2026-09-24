import unittest
from unittest.mock import patch

from aimaticlearning.lms_learning import study_buddy as study_buddy_module
from aimaticlearning.lms_learning.nemotron_client import NemotronError
from aimaticlearning.lms_learning.study_buddy import (
	_system_prompt,
	assemble_source_context,
	format_attempt_context,
	format_history_turns,
	history_messages_from_turns,
	normalise_conversation_id,
	parse_attempt_context,
	request_study_buddy_completion,
	study_buddy_log_values,
	validate_source_citations,
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
		self.assertIn("Answer the question directly", prompt)
		self.assertIn("material in this chapter", prompt)


class TestStudyBuddyGrounding(unittest.TestCase):
	def test_context_uses_open_lesson_then_approved_chapter_notes(self):
		context, sources = assemble_source_context(
			lesson_title="Practice MCQs",
			lesson_body="<p>Use the chapter rules to answer.</p>",
			chapter_title="Value Added Tax",
			chapter_notes="<h2>VAT</h2><p>VAT is charged on taxable supplies.</p>",
			question="When is VAT charged?",
		)
		self.assertIn("[S1] Open lesson: Practice MCQs", context)
		self.assertIn("[S2] Chapter notes: Value Added Tax", context)
		self.assertEqual([source["id"] for source in sources], ["S1", "S2"])

	def test_context_deduplicates_notes_lesson_and_stays_bounded(self):
		body = "VAT is charged on taxable supplies. " * 1000
		context, sources = assemble_source_context(
			lesson_title="VAT Notes",
			lesson_body=body,
			chapter_title="VAT",
			chapter_notes=body,
			question="What is VAT?",
		)
		self.assertEqual(len(sources), 1)
		self.assertLessEqual(len(context), 8100)

	def test_invalid_model_citations_are_removed(self):
		answer, sources = validate_source_citations(
			"VAT applies [S1], not [S9] or [Q2].",
			[{"id": "S1", "label": "VAT notes", "scope": "Chapter"}],
		)
		self.assertEqual(answer, "VAT applies [S1], not  or .")
		self.assertEqual([source["id"] for source in sources], ["S1"])


class TestStudyBuddyConversation(unittest.TestCase):
	def test_conversation_ids_are_normalized_and_invalid_values_rejected(self):
		value = normalise_conversation_id("550e8400-e29b-41d4-a716-446655440000")
		self.assertEqual(value, "550e8400-e29b-41d4-a716-446655440000")
		with self.assertRaises(ValueError):
			normalise_conversation_id("not-a-conversation")

	def test_server_history_keeps_complete_recent_pairs(self):
		messages = history_messages_from_turns(
			[
				{"question": "First?", "answer": "First answer."},
				{"question": "Failed", "answer": ""},
				{"question": "Second?", "answer": "Second answer."},
			]
		)
		self.assertEqual([message["role"] for message in messages], ["user", "assistant", "user", "assistant"])
		self.assertEqual(messages[-1]["content"], "Second answer.")

	@patch("aimaticlearning.lms_learning.study_buddy.get_chat_completion")
	def test_empty_answer_retries_once_on_the_same_paid_model(self, completion):
		completion.side_effect = [
			{
				"message": {"role": "assistant", "content": ""},
				"finish_reason": "length",
				"usage": {"prompt_tokens": 100, "completion_tokens": 0},
			},
			{
				"message": {"role": "assistant", "content": "Grounded answer [S1]."},
				"finish_reason": "stop",
				"usage": {"prompt_tokens": 80, "completion_tokens": 12},
			},
		]
		result = request_study_buddy_completion(
			system_message={"role": "system", "content": "[S1] Approved notes"},
			history_messages=[
				{"role": "user", "content": "Earlier question"},
				{"role": "assistant", "content": "Earlier answer"},
				{"role": "user", "content": "Latest question"},
				{"role": "assistant", "content": "Latest answer"},
			],
			question="Current question",
			model="nvidia/nemotron-3.5-lightning",
		)
		self.assertEqual(result["answer"], "Grounded answer [S1].")
		self.assertEqual(result["retry_count"], 1)
		self.assertEqual(completion.call_count, 2)
		for call in completion.call_args_list:
			self.assertEqual(call.kwargs["model"], "nvidia/nemotron-3.5-lightning")
		self.assertEqual(len(completion.call_args_list[0].args[0]), 6)
		self.assertEqual(len(completion.call_args_list[1].args[0]), 4)

	@patch("aimaticlearning.lms_learning.study_buddy.get_chat_completion")
	def test_non_retryable_provider_error_stops_after_one_attempt(self, completion):
		completion.side_effect = NemotronError(
			"configuration error", code="configuration", retryable=False
		)
		result = request_study_buddy_completion(
			system_message={"role": "system", "content": "Approved notes"},
			history_messages=[],
			question="Question",
			model="nvidia/nemotron-3.5-lightning",
		)
		self.assertEqual(result["error"].code, "configuration")
		self.assertEqual(result["retry_count"], 0)
		completion.assert_called_once()


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
			model="nvidia/nemotron-3.5-lightning",
			conversation_id="550e8400-e29b-41d4-a716-446655440000",
			source_scope="S1, S2",
			latency_ms=1234,
			finish_reason="stop",
			prompt_tokens=500,
			completion_tokens=80,
			retry_count=1,
			grounded=True,
			has_attempt_context=True,
			status="Answered",
		)
		self.assertEqual(values["doctype"], "Study Buddy Chat Log")
		self.assertEqual(values["question"], "What is VAT?")
		self.assertEqual(values["preview"], "What is VAT?")
		self.assertEqual(values["model"], "nvidia/nemotron-3.5-lightning")
		self.assertEqual(values["conversation_id"], "550e8400-e29b-41d4-a716-446655440000")
		self.assertEqual(values["source_scope"], "S1, S2")
		self.assertEqual(values["latency_ms"], 1234)
		self.assertEqual(values["finish_reason"], "stop")
		self.assertEqual(values["completion_tokens"], 80)
		self.assertEqual(values["retry_count"], 1)
		self.assertEqual(values["status"], "Answered")
		self.assertEqual(values["grounded"], 1)
		self.assertNotIn("body", values)
		self.assertNotIn("SECRET LESSON BODY", str(values))
		self.assertNotIn("system", str(values).lower())

	@patch("aimaticlearning.lms_learning.study_buddy._diagnostic_schema_ready", return_value=False)
	@patch("aimaticlearning.lms_learning.study_buddy.frappe")
	def test_pre_migration_log_strips_additive_fields(self, frappe, _schema_ready):
		values = {
			"doctype": "Study Buddy Chat Log",
			"question": "What is VAT?",
			"conversation_id": "550e8400-e29b-41d4-a716-446655440000",
			"source_scope": "S1",
			"latency_ms": 321,
			"retry_count": 1,
		}
		study_buddy_module._save_study_buddy_log(values)
		saved = frappe.get_doc.call_args.args[0]
		self.assertEqual(saved["doctype"], "Study Buddy Chat Log")
		self.assertEqual(saved["question"], "What is VAT?")
		for fieldname in study_buddy_module.ADDITIVE_LOG_FIELDS:
			self.assertNotIn(fieldname, saved)
		frappe.get_doc.return_value.insert.assert_called_once_with(ignore_permissions=True)

	@patch("aimaticlearning.lms_learning.study_buddy._diagnostic_schema_ready", return_value=False)
	@patch("aimaticlearning.lms_learning.study_buddy.frappe")
	def test_pre_migration_history_uses_legacy_lesson_filter(self, frappe, _schema_ready):
		frappe.get_all.return_value = []
		study_buddy_module._conversation_rows(
			user="student@example.com",
			course="business-law-practice-blp",
			chapter=1,
			lesson=4,
			conversation_id="550e8400-e29b-41d4-a716-446655440000",
		)
		filters = frappe.get_all.call_args.kwargs["filters"]
		self.assertEqual(filters["lesson_number"], 4)
		self.assertNotIn("conversation_id", filters)

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
