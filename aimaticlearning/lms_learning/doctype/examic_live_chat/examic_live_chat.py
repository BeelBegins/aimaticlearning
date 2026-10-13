import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

from aimaticlearning.lms_learning.live_chat import is_staff


class ExamicLiveChat(Document):
	def validate(self):
		if not self.is_new():
			previous = self.get_doc_before_save()
			if previous and previous.student and previous.student != self.student:
				frappe.throw(_("The student on a live chat cannot be changed."))
		if self.messages:
			last = self.messages[-1]
			self.last_message = str(last.body or "")[:140]
			if not last.sent_at:
				last.sent_at = now_datetime()
			if not last.sender:
				last.sender = frappe.session.user
			if not last.role and is_staff():
				last.role = "Staff"

	@frappe.whitelist()
	def send_reply(self, body: str):
		from aimaticlearning.lms_learning.live_chat import staff_reply

		return staff_reply(self, body)
