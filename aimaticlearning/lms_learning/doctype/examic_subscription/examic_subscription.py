from frappe.model.document import Document

from aimaticlearning.lms_learning import billing


class ExamicSubscription(Document):
	def validate(self):
		self.status = billing.status_for(self.trial_ends_on, self.paid_until, self.pending_plan)
