import frappe
from frappe.model.document import Document

from aimaticlearning.lms_learning.study_settings import prepare_live_chat


class ExamicLiveChatSettings(Document):
	def validate(self):
		message = prepare_live_chat(self)
		if message:
			frappe.throw(frappe._(message))
