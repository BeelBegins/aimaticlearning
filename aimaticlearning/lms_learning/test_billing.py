import unittest
from datetime import date, datetime, timedelta
from unittest import mock

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


class TestMonthlyEarlyUnlock(unittest.TestCase):
	def test_card_at_signup_student_never_unlocks_on_the_plan_label(self):
		paid_checkout = billing.monthly_checkout_paid
		self.assertTrue(paid_checkout("trial", "Monthly", "sub_1", 0))
		self.assertFalse(paid_checkout("trial", "Monthly", "sub_1", 1))
		self.assertFalse(paid_checkout("trial", "Monthly", None, 0))
		self.assertFalse(paid_checkout("trial", "3-Month", "sub_1", 0))
		self.assertFalse(paid_checkout("locked", "Monthly", "sub_1", 0))


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


class TestSignupPlan(unittest.TestCase):
	now = datetime(2026, 11, 1, 12, 0)

	def run_record(self, plan="3-Month", user=None, field=True):
		from unittest import mock

		db = mock.MagicMock()
		row = {"name": "a@b.com", "creation": self.now, "last_login": None, **(user or {})}
		with (
			mock.patch.object(billing, "signup_plan_field", return_value=field),
			mock.patch.object(billing.frappe, "db", db),
			mock.patch("frappe.utils.now_datetime", return_value=self.now + timedelta(minutes=1)),
			mock.patch.object(billing, "create_subscription"),
		):
			db.get_value.return_value = billing.frappe._dict(row)
			billing.record_signup_plan.__wrapped__("a@b.com", plan)
		return db.set_value

	def test_new_student_plan_is_saved(self):
		set_value = self.run_record()
		set_value.assert_called_once()
		self.assertEqual(set_value.call_args.args[2:], ("signup_plan", "3-Month"))

	def test_unknown_plan_or_old_schema_is_ignored(self):
		self.assertFalse(self.run_record(plan="Gold").called)
		self.assertFalse(self.run_record(field=False).called)

	def test_existing_student_is_not_touched(self):
		self.assertFalse(self.run_record(user={"last_login": self.now}).called)
		self.assertFalse(self.run_record(user={"creation": self.now - timedelta(hours=2)}).called)


class TestBillingHealth(unittest.TestCase):
	def row(self, **over):
		base = {"name": "a@b.com", "plan": "", "pending_plan": "Monthly", "trial_ends_on": date(2026, 11, 25),
			"paid_until": None, "stripe_subscription": "sub_1", "card_required": 1}
		base.update(over)
		return base

	def kinds(self, rows, now):
		return [i["kind"] for i in billing.billing_health_issues(rows, now)]

	def test_unrecorded_first_charge_alerts_only_after_the_grace_period(self):
		before_due = datetime(2026, 11, 26, 2, 59)
		after_due = datetime(2026, 11, 26, 3, 0)
		self.assertEqual(self.kinds([self.row()], datetime(2026, 11, 25, 23, 0)), [])
		self.assertEqual(self.kinds([self.row()], before_due), [])
		self.assertEqual(self.kinds([self.row()], after_due), ["charge_not_recorded"])

	def test_a_recorded_payment_clears_the_first_charge_alert(self):
		paid = self.row(plan="Monthly", pending_plan=None, paid_until=date(2026, 12, 26))
		self.assertEqual(self.kinds([paid], datetime(2026, 11, 27, 12, 0)), [])

	def test_free_month_student_with_a_saved_card_is_healthy(self):
		self.assertEqual(self.kinds([self.row()], datetime(2026, 11, 10, 12, 0)), [])

	def test_no_card_student_waiting_for_a_manual_payment_is_not_flagged(self):
		manual = self.row(stripe_subscription=None, card_required=0)
		self.assertEqual(self.kinds([manual], datetime(2026, 12, 1, 12, 0)), [])

	def test_plan_label_without_a_payment_is_flagged_for_card_at_signup_students(self):
		bad = self.row(plan="Monthly", pending_plan=None)
		self.assertEqual(self.kinds([bad], datetime(2026, 10, 27, 12, 0)), ["plan_without_payment"])
		self.assertEqual(self.kinds([dict(bad, card_required=0)], datetime(2026, 10, 27, 12, 0)), [])

	def test_live_subscription_with_an_ended_paid_period_is_flagged_after_a_day(self):
		lapsed = self.row(plan="Monthly", pending_plan=None, paid_until=date(2026, 12, 26))
		self.assertEqual(self.kinds([lapsed], datetime(2026, 12, 27, 12, 0)), [])
		self.assertEqual(self.kinds([lapsed], datetime(2026, 12, 28, 12, 0)), ["renewal_not_recorded"])
		cancelled = dict(lapsed, stripe_subscription=None)
		self.assertEqual(self.kinds([cancelled], datetime(2026, 12, 28, 12, 0)), [])

	def test_job_alerts_staff_once_a_day_per_issue(self):
		rows = [self.row(), self.row(name="ok@b.com", paid_until=date(2099, 1, 1), plan="Monthly", pending_plan=None)]
		sent = []
		real = billing.billing_health_issues
		with (
			mock.patch.object(billing, "frappe") as fake,
			mock.patch.object(billing, "card_required_field", lambda: True),
			mock.patch.object(billing, "billing_health_issues", lambda r: real(r, datetime(2026, 11, 27, 9, 0))),
			mock.patch.object(billing, "_discord", lambda *a: sent.append(a)),
		):
			fake.get_all.return_value = rows
			result = billing.billing_health_job()
		self.assertEqual(result, {"issues": 1})
		event, title, text, key, seconds = sent[0]
		self.assertEqual((event, title, key, seconds), ("payment_needs_review", "Charge not recorded", "health:charge_not_recorded:a@b.com", 23 * 3600))
		self.assertIn("a@b.com", text)
		self.assertIn("2026-11-26", text)

