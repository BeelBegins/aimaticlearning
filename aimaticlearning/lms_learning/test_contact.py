import unittest

from aimaticlearning.lms_learning import billing, contact


class TestContactEnquiry(unittest.TestCase):
	def valid(self, **overrides):
		data = {
			"name": "  Sam   Learner ",
			"email": "sam@example.com",
			"enquiry_type": "Content Issue",
			"message": "Question 4 in Contract Law chapter 2 has a typo.",
			"reference": "",
		}
		data.update(overrides)
		return data

	def test_accepts_required_fields_without_marketing_consent(self):
		got = contact.clean_enquiry(**self.valid())
		self.assertEqual(got["name"], "Sam Learner")
		self.assertEqual(got["reference"], "")

	def test_every_published_enquiry_type_is_accepted(self):
		for kind in contact.ENQUIRY_TYPES:
			self.assertEqual(contact.clean_enquiry(**self.valid(enquiry_type=kind))["enquiry_type"], kind)

	def test_rejects_missing_or_bad_values(self):
		for overrides in ({"name": " "}, {"email": "not an email"}, {"enquiry_type": "Sales"}, {"message": ""},
				{"message": "x" * 5001}, {"reference": "r" * 141}):
			with self.assertRaises(ValueError, msg=overrides):
				contact.clean_enquiry(**self.valid(**overrides))

	def test_email_body_escapes_learner_text(self):
		body = contact.email_body(contact.clean_enquiry(**self.valid(message="<script>x</script>")))
		self.assertNotIn("<script>", body)

	def test_locked_students_can_still_send_an_enquiry(self):
		self.assertFalse(billing.is_locked_path("/api/method/aimaticlearning.lms_learning.contact.submit_enquiry"))
		for path in ("/contact", "/complaints", "/introductory-offer", "/about/our-story"):
			self.assertFalse(billing.is_locked_path(path), path)


if __name__ == "__main__":
	unittest.main()
