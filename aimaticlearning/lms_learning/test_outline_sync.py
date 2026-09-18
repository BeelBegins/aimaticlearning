import unittest

from aimaticlearning.lms_learning.outline_sync import (
	new_quiz_lesson_values,
	quiz_lessons_with_editorjs,
)


class TestQuizLessonContent(unittest.TestCase):
	def test_new_quiz_lesson_values_leave_content_empty(self):
		values = new_quiz_lesson_values(
			title="Chapter MCQ — Formation",
			course="business-law-practice-blp",
			chapter="CH-1",
			quiz_id="introduction-chapter-mcq-20",
		)
		self.assertEqual(values["content"], "")
		self.assertTrue((values["body"] or "").strip())
		self.assertEqual(values["quiz_id"], "introduction-chapter-mcq-20")
		self.assertNotIn("blocks", values)

	def test_quiz_lessons_with_editorjs_only_flags_quiz_id_plus_content(self):
		rows = [
			{
				"name": "blocked",
				"quiz_id": "q1",
				"content": '{"time":1,"blocks":[{"type":"paragraph","data":{"text":"x"}}]}',
			},
			{"name": "empty-content", "quiz_id": "q2", "content": ""},
			{"name": "whitespace-content", "quiz_id": "q3", "content": "   "},
			{"name": "notes-blob", "quiz_id": "", "content": '{"blocks":[]}'},
			{"name": "no-quiz", "quiz_id": None, "content": '{"blocks":[]}'},
		]
		blocked = quiz_lessons_with_editorjs(rows)
		self.assertEqual([row["name"] for row in blocked], ["blocked"])
