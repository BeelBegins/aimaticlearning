import frappe
from frappe.model.document import Document

from aimaticlearning.lms_learning.study_settings import prepare_settings


class ExamicStudySettings(Document):
	def validate(self):
		message = prepare_settings(self)
		if message:
			frappe.throw(frappe._(message))

	@frappe.whitelist()
	def test_openrouter(self):
		from aimaticlearning.lms_learning.study_settings import run_openrouter_test

		return run_openrouter_test()

	@frappe.whitelist()
	def send_test_alert(self):
		from aimaticlearning.lms_learning.discord_alerts import send_test_alert

		return send_test_alert()
