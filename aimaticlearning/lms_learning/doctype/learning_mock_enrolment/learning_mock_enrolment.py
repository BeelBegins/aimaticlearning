import frappe
from frappe.model.document import Document


class LearningMockEnrolment(Document):
	def validate(self):
		if not self.exam or not self.member:
			return
		filters = {"exam": self.exam, "member": self.member}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Learning Mock Enrolment", filters):
			frappe.throw("This member is already enrolled on the mock exam.")
