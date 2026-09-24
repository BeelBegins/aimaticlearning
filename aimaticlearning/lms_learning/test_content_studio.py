import unittest

from aimaticlearning.lms_learning.content_studio import (
	ContentStudioError,
	lms_question_fields,
	normalize_chapter_title,
	normalize_mcq_options,
	notes_write_values,
	question_signature,
	replace_matching_first_heading,
	retitle_display,
	validate_chapter_title,
	validate_mcq_payload,
)
from aimaticlearning.lms_learning.outline_sync import new_quiz_lesson_values


class TestContentStudio(unittest.TestCase):
	def test_notes_write_values_clear_editorjs(self):
		values = notes_write_values("<p>Offer and acceptance</p>")
		self.assertEqual(values["body"], "<p>Offer and acceptance</p>")
		self.assertEqual(values["content"], "")

	def test_notes_write_values_empty_still_clears_content(self):
		values = notes_write_values(None)
		self.assertEqual(values["body"], "")
		self.assertEqual(values["content"], "")

	def test_sanitize_strips_quill_editor_wrapper(self):
		from aimaticlearning.lms_learning.content_studio import sanitize_studio_notes_html

		wrapped = '<div class="ql-editor read-mode"><h2>Offer</h2><p>Acceptance</p></div>'
		self.assertEqual(sanitize_studio_notes_html(wrapped), "<h2>Offer</h2><p>Acceptance</p>")
		values = notes_write_values(wrapped)
		self.assertEqual(values["body"], "<h2>Offer</h2><p>Acceptance</p>")
		self.assertEqual(values["content"], "")

	def test_sanitize_treats_empty_quill_as_blank(self):
		from aimaticlearning.lms_learning.content_studio import sanitize_studio_notes_html

		self.assertEqual(sanitize_studio_notes_html("<p><br></p>"), "")
		self.assertEqual(sanitize_studio_notes_html('<div class="ql-editor read-mode"><p><br></p></div>'), "")
		self.assertEqual(sanitize_studio_notes_html('<div class="ql-editor"><p></p></div>'), "")
		self.assertEqual(sanitize_studio_notes_html("  "), "")
		self.assertEqual(sanitize_studio_notes_html('<div class="ql-editor read-mode"><p>Offer</p></div>'), "<p>Offer</p>")
		self.assertEqual(notes_write_values("<p><br></p>")["body"], "")

	def test_validate_mcq_requires_explicit_correct_option(self):
		options = normalize_mcq_options(
			[
				{"text": "Offer", "is_correct": 0},
				{"text": "Acceptance", "is_correct": 0},
			]
		)
		with self.assertRaises(ContentStudioError) as raised:
			validate_mcq_payload("What completes a contract?", options)
		self.assertIn("exactly one", str(raised.exception).lower())
		self.assertIn("option a", str(raised.exception).lower())

	def test_validate_mcq_rejects_first_option_as_implicit_answer(self):
		options = normalize_mcq_options(
			[
				{"text": "A is listed first", "is_correct": False},
				{"text": "B is actually correct", "is_correct": True},
			]
		)
		validate_mcq_payload("Pick the rule", options)
		fields = lms_question_fields("Pick the rule", options)
		self.assertEqual(fields["is_correct_1"], 0)
		self.assertEqual(fields["is_correct_2"], 1)
		self.assertEqual(fields["option_2"], "B is actually correct")

	def test_validate_mcq_rejects_two_correct_options(self):
		options = normalize_mcq_options(
			[
				{"text": "One", "is_correct": 1},
				{"text": "Two", "is_correct": 1},
			]
		)
		with self.assertRaises(ContentStudioError):
			validate_mcq_payload("Ambiguous", options)

	def test_blank_options_are_dropped(self):
		options = normalize_mcq_options(
			[
				{"text": "  Keep  ", "is_correct": 1, "explanation": " Because statute. "},
				{"text": "   "},
				{"text": "Also keep", "is_correct": 0},
			]
		)
		self.assertEqual(len(options), 2)
		self.assertEqual(options[0]["text"], "Keep")
		self.assertEqual(options[0]["explanation"], "Because statute.")

	def test_question_signature_changes_when_correct_option_moves(self):
		first = question_signature(
			"Stem",
			[{"text": "A", "is_correct": True, "explanation": ""}, {"text": "B", "is_correct": False, "explanation": ""}],
		)
		second = question_signature(
			"Stem",
			[{"text": "A", "is_correct": False, "explanation": ""}, {"text": "B", "is_correct": True, "explanation": ""}],
		)
		self.assertNotEqual(first, second)

	def test_quiz_lesson_factory_stays_empty_content(self):
		values = new_quiz_lesson_values(
			title="Chapter MCQ — Formation",
			course="contract-law",
			chapter="CH-1",
			quiz_id="formation-chapter-mcq",
		)
		self.assertEqual(values["content"], "")
		self.assertTrue((values["body"] or "").strip())

	def test_flashcard_lesson_values_leave_content_empty(self):
		from aimaticlearning.lms_learning.course_presentation import flashcard_lesson_values

		values = flashcard_lesson_values(
			"Chapter 1: Forms of Business Organisations", "LMOD-00017", "CH-1"
		)
		self.assertEqual(values["content"], "")
		self.assertEqual(values["title"], "Flashcards \u2014 Chapter 1: Forms of Business Organisations")
		self.assertIn("data-aimatic-flashcard-deck", values["body"])
		self.assertIn('data-learning-module="LMOD-00017"', values["body"])
		self.assertIn('data-course-chapter="CH-1"', values["body"])
		self.assertNotIn("/learning-flashcards?", values["body"])


	def test_validate_chapter_title_rejects_blank(self):
		with self.assertRaises(ContentStudioError):
			validate_chapter_title(normalize_chapter_title("   "))


	def test_retitle_display_updates_derived_lesson_and_quiz_labels(self):
		old = ["Registration for VAT", "Chapter 22: Registration for VAT"]
		self.assertEqual(retitle_display("Notes — Registration for VAT", old, "VAT Registration"), "Notes — VAT Registration")
		self.assertEqual(
			retitle_display("Chapter 22: Registration for VAT", old, "Chapter 22: VAT Registration"),
			"Chapter 22: VAT Registration",
		)
		self.assertEqual(
			retitle_display("Registration for VAT — Chapter MCQ", old, "VAT Registration"),
			"VAT Registration — Chapter MCQ",
		)
		self.assertIsNone(retitle_display("Unrelated lesson", old, "VAT Registration"))


	def test_replace_matching_first_heading_only_when_title_matches(self):
		html = '<article class="aimatic-notes"><h2>Registration for VAT</h2><p>Body</p></article>'
		updated, changed = replace_matching_first_heading(
			html, ["Registration for VAT"], "VAT Registration"
		)
		self.assertTrue(changed)
		self.assertIn("<h2>VAT Registration</h2>", updated)
		self.assertIn("<p>Body</p>", updated)
		untouched, skipped = replace_matching_first_heading(
			html, ["Some other chapter"], "VAT Registration"
		)
		self.assertFalse(skipped)
		self.assertEqual(untouched, html)

	def test_validate_flashcard_payload_requires_front_and_back(self):
		from aimaticlearning.lms_learning.content_studio import validate_flashcard_payload

		with self.assertRaises(ContentStudioError):
			validate_flashcard_payload("", "back", "Draft")
		validate_flashcard_payload("front", "back", "Draft")

	def test_default_mcq_options_are_five_for_sqe(self):
		from aimaticlearning.lms_learning.content_studio import DEFAULT_MCQ_OPTIONS, default_mcq_options

		options = default_mcq_options()
		self.assertEqual(DEFAULT_MCQ_OPTIONS, 5)
		self.assertEqual(len(options), 5)
		self.assertEqual(sum(1 for option in options if option["is_correct"]), 0)

	def test_annotate_studio_modules_hides_exam_course_and_labels_pathways(self):
		from aimaticlearning.lms_learning.content_studio import annotate_studio_modules

		rows = annotate_studio_modules(
			[
				{"name": "c", "title": "Contract Law", "lms_course": "contract-law"},
				{"name": "m", "title": "SQE1 Hard Mocks", "lms_course": "sqe1-hard-mocks"},
				{"name": "w", "title": "Wills", "lms_course": "wills-and-administration-of-estates"},
				{"name": "x", "title": "Extra", "lms_course": "ad-hoc-course"},
			]
		)
		names = [row["lms_course"] for row in rows]
		self.assertNotIn("sqe1-hard-mocks", names)
		self.assertEqual(rows[0]["pathway"], "FLK1")
		self.assertEqual(rows[0]["lms_course"], "contract-law")
		self.assertEqual(rows[1]["pathway"], "FLK2")
		self.assertEqual(rows[2]["pathway"], "Other")

	def test_flashcard_studio_fields_include_source_quote(self):
		from aimaticlearning.lms_learning.content_studio import FLASHCARD_STUDIO_FIELDS

		self.assertIn("source_quote", FLASHCARD_STUDIO_FIELDS)
		self.assertIn("source_reference", FLASHCARD_STUDIO_FIELDS)

	def test_reorder_question_names_swaps_neighbours_only(self):
		from aimaticlearning.lms_learning.content_studio import ContentStudioError, reorder_question_names

		names = ["q1", "q2", "q3"]
		self.assertEqual(reorder_question_names(names, "q2", "up"), ["q2", "q1", "q3"])
		self.assertEqual(reorder_question_names(names, "q2", "down"), ["q1", "q3", "q2"])
		self.assertEqual(reorder_question_names(names, "q1", "up"), ["q1", "q2", "q3"])
		self.assertEqual(reorder_question_names(names, "q3", "down"), ["q1", "q2", "q3"])
		with self.assertRaises(ContentStudioError):
			reorder_question_names(names, "missing", "up")
		with self.assertRaises(ContentStudioError):
			reorder_question_names(names, "q1", "sideways")

	def test_insert_and_reorder_outline_names(self):
		from aimaticlearning.lms_learning.content_studio import insert_outline_name, reorder_outline_names

		names = ["a", "b", "c"]
		self.assertEqual(insert_outline_name(names, "new", 1), ["new", "a", "b", "c"])
		self.assertEqual(insert_outline_name(names, "new", 2), ["a", "new", "b", "c"])
		self.assertEqual(insert_outline_name(names, "new", None), ["a", "b", "c", "new"])
		self.assertEqual(reorder_outline_names(["a", "b", "c"], "c", "up"), ["a", "c", "b"])

	def test_duplicate_question_stem_marks_copy_once(self):
		from aimaticlearning.lms_learning.content_studio import DUPLICATE_STEM_SUFFIX, duplicate_question_stem

		self.assertEqual(duplicate_question_stem("Offer and acceptance"), f"Offer and acceptance{DUPLICATE_STEM_SUFFIX}")
		self.assertEqual(
			duplicate_question_stem(f"Offer and acceptance{DUPLICATE_STEM_SUFFIX}"),
			f"Offer and acceptance{DUPLICATE_STEM_SUFFIX}",
		)
		with self.assertRaises(ContentStudioError):
			duplicate_question_stem("   ")

	def test_notes_publish_state_detects_sync_and_drift(self):
		from aimaticlearning.lms_learning.content_studio import notes_compare_key, notes_publish_state

		studio = '<div class="ql-editor"><h2>Offer</h2><p>Acceptance</p></div>'
		learner = "<h2>Offer</h2><p>Acceptance</p>"
		self.assertEqual(notes_compare_key(studio), notes_compare_key(learner))
		synced = notes_publish_state(studio, learner, notes_lesson="lesson-1")
		self.assertEqual(synced["status"], "in_sync")
		self.assertTrue(synced["in_sync"])
		self.assertEqual(synced["label"], "Notes published")

		drift = notes_publish_state(
			"<h2>Offer</h2><p>Acceptance</p><h3>CHAPTER SUMMARY AND KEY CONCEPTS</h3>",
			"<h2>Offer</h2><p>Acceptance</p>",
			notes_lesson="lesson-1",
		)
		self.assertEqual(drift["status"], "out_of_sync")
		self.assertFalse(drift["in_sync"])
		self.assertGreater(drift["studio_chars"], drift["learner_chars"])

		missing = notes_publish_state("<p>x</p>", "", notes_lesson="")
		self.assertEqual(missing["status"], "missing_lesson")
		empty = notes_publish_state("<p><br></p>", "", notes_lesson="lesson-1")
		self.assertEqual(empty["status"], "empty")

	def test_flashcard_status_counts_shape(self):
		from aimaticlearning.lms_learning.content_studio import FLASHCARD_STATUSES, flashcard_status_counts

		counts = flashcard_status_counts("LMOD-MISSING", None)
		self.assertEqual(set(counts), set(FLASHCARD_STATUSES))
		self.assertEqual(sum(counts.values()), 0)

	def test_chapter_removal_requires_exact_heading(self):
		from aimaticlearning.lms_learning.content_studio import (
			ContentStudioError,
			validate_chapter_removal_confirm,
		)

		validate_chapter_removal_confirm("VAT Registration", "  VAT Registration  ")
		with self.assertRaises(ContentStudioError) as raised:
			validate_chapter_removal_confirm("VAT Registration", "VAT")
		self.assertIn("exact chapter heading", str(raised.exception).lower())

