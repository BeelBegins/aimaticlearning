import unittest
from datetime import date

from aimaticlearning.lms_learning import billing


class TestStatus(unittest.TestCase):
	today = date(2026, 11, 1)

	def test_status_follows_dates(self):
		s = billing.status_for
		self.assertEqual(s(date(2026, 11, 5), None, None, self.today), "Trial")
		self.assertEqual(s(date(2026, 11, 1), None, None, self.today), "Trial")
		self.assertEqual(s(date(2026, 10, 31), None, None, self.today), "Expired")
		self.assertEqual(s(date(2026, 10, 31), None, "Monthly", self.today), "Awaiting Payment")
		self.assertEqual(s(date(2026, 10, 31), date(2026, 12, 1), None, self.today), "Active")
		self.assertEqual(s(date(2026, 10, 31), date(2026, 10, 31), None, self.today), "Expired")

	def test_state_mapping(self):
		f = billing.state_for
		self.assertEqual(f("Expired", True, True), "staff")
		self.assertEqual(f("Expired", False, False), "full")
		self.assertEqual(f("Trial", False, True), "trial")
		self.assertEqual(f("Active", False, True), "paid")
		self.assertEqual(f("Expired", False, True), "locked")
		self.assertEqual(f("Awaiting Payment", False, True), "locked")

	def test_mocks_open_only_for_staff_and_paid(self):
		self.assertTrue(billing.mocks_unlocked("staff"))
		self.assertTrue(billing.mocks_unlocked("paid"))
		for state in ("full", "trial", "locked"):
			self.assertFalse(billing.mocks_unlocked(state))


class TestPeriods(unittest.TestCase):
	def test_paid_period_starts_after_the_free_month(self):
		# Paying on day 5 of the free month: monthly runs from the end of the free month.
		got = billing.extend_paid_until("Monthly", date(2026, 11, 9), None, today=date(2026, 10, 14))
		self.assertEqual(got, date(2026, 12, 9))
		got = billing.extend_paid_until("3-Month", date(2026, 11, 9), None, today=date(2026, 10, 14))
		self.assertEqual(got, date(2027, 2, 9))

	def test_late_payment_counts_from_today(self):
		got = billing.extend_paid_until("Monthly", date(2026, 11, 9), None, today=date(2026, 11, 20))
		self.assertEqual(got, date(2026, 12, 20))

	def test_paying_again_early_extends(self):
		got = billing.extend_paid_until("Monthly", date(2026, 11, 9), date(2026, 12, 9), today=date(2026, 12, 1))
		self.assertEqual(got, date(2027, 1, 9))


class TestCardSetup(unittest.TestCase):
	def test_new_signup_without_a_card_must_set_up_first(self):
		self.assertTrue(billing.needs_card_setup("trial", 1, None))

	def test_card_on_file_or_older_signup_or_other_state_does_not(self):
		self.assertFalse(billing.needs_card_setup("trial", 1, "sub_1"))
		self.assertFalse(billing.needs_card_setup("trial", 0, None))
		self.assertFalse(billing.needs_card_setup("paid", 1, None))
		self.assertFalse(billing.needs_card_setup("locked", 1, None))


class TestEnforcementPaths(unittest.TestCase):
	def test_locked_surfaces_and_allowed_pages(self):
		for path in ("/lms", "/lms/courses/tort-law", "/learning-mock-exam", "/api/method/lms.lms.utils.get_courses",
				"/api/method/aimaticlearning.lms_learning.api.get_flashcards"):
			self.assertTrue(billing.is_locked_path(path), path)
		for path in ("/billing", "/pricing", "/sqe", "/terms", "/login", "/logout", "/assets/x.css",
				"/api/method/aimaticlearning.lms_learning.billing.get_billing_state"):
			self.assertFalse(billing.is_locked_path(path), path)
		self.assertFalse(billing.is_locked_path("/"))


if __name__ == "__main__":
	unittest.main()
