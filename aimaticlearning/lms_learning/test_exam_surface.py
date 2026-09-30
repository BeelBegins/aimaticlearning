import json
import unittest

from aimaticlearning.lms_learning.exam_surface import (
	catalog_filters,
	is_exam_course,
	parsed_filters,
	without_exam_courses,
)


class TestExamSurface(unittest.TestCase):
	def test_hard_mocks_are_exam_courses_not_subjects(self):
		self.assertTrue(is_exam_course("sqe1-hard-mocks"))
		self.assertFalse(is_exam_course("contract-law"))
		self.assertFalse(is_exam_course(""))

	def test_catalog_filters_exclude_exam_course(self):
		filters = catalog_filters({"published": 1})
		self.assertEqual(filters["name"], ["not in", ["sqe1-hard-mocks"]])
		self.assertEqual(filters["published"], 1)

	def test_catalog_filters_strips_exam_from_enrolled_list(self):
		filters = catalog_filters({"name": ["in", ["contract-law", "sqe1-hard-mocks"]]})
		self.assertEqual(filters["name"], ["in", ["contract-law"]])

	def test_parsed_filters_accepts_json(self):
		self.assertEqual(parsed_filters(json.dumps({"live": 1})), {"live": 1})
		self.assertEqual(parsed_filters(None), {})

	def test_without_exam_courses_drops_mock_cards(self):
		rows = [{"name": "contract-law"}, {"name": "sqe1-hard-mocks"}, {"name": "tort-law"}]
		self.assertEqual(
			[row["name"] for row in without_exam_courses(rows)],
			["contract-law", "tort-law"],
		)
