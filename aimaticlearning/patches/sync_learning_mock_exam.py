import frappe


def execute():
	if "lms" not in frappe.get_installed_apps():
		return
	if not frappe.db.exists("DocType", "Learning Mock Exam"):
		return
	from aimaticlearning.lms_learning.exam_product import sync_from_hard_mock_course

	sync_from_hard_mock_course()
