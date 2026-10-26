"""Free month to paid month, driven through the real webhook handler with an in-memory student.

No database and no Stripe: the subscription row is a plain object, and every event has the shape the live
account sends (a free-month Checkout is `payment_status: paid` with `amount_total: 0`).
"""

import unittest
from datetime import date
from unittest import mock

from aimaticlearning.lms_learning import billing

USER = "student@example.com"
TRIAL_END = date(2026, 11, 25)
FIRST_CHARGE = date(2026, 11, 26)
CFG = {"monthly_price": 49, "three_month_price": 99, "trial_days": 30, "free_mock_count": 2,
	"active_provider": "Stripe", "enabled": 1}


class FakeSubscription:
	def __init__(self):
		self.user = USER
		self.trial_ends_on = TRIAL_END
		self.paid_until = None
		self.plan = ""
		self.pending_plan = None
		self.pending_reference = None
		self.pending_requested_on = None
		self.stripe_customer = None
		self.stripe_subscription = None
		self.last_payment_error = None
		self.last_payment_on = None
		self.card_required = 1
		self.status = "Trial"
		self.payments = []

	def append(self, table, row):
		getattr(self, table).append(row)

	def save(self, **_):
		pass


class FakeProvider:
	name = "Stripe"

	def __init__(self):
		self.ended = []

	def uses_subscription(self, plan, cfg):
		return True

	def schedule_end(self, subscription_id, cancel_at, cfg):
		self.ended.append((subscription_id, cancel_at))


def checkout(plan, event_id="evt_co"):
	return {"id": event_id, "type": "checkout.session.completed", "data": {"object": {
		"mode": "subscription", "payment_status": "paid", "amount_total": 0, "client_reference_id": USER,
		"metadata": {"plan": plan, "user": USER}, "customer": "cus_1", "subscription": "sub_1"}}}


def invoice(paid_pence, reason, plan, event_id):
	return {"id": event_id, "type": "invoice.paid", "data": {"object": {
		"id": "in_" + event_id, "amount_paid": paid_pence, "customer": "cus_1", "subscription": "sub_1",
		"billing_reason": reason, "subscription_details": {"metadata": {"user": USER, "plan": plan}}}}}


class TestFreeMonthToPaid(unittest.TestCase):
	def setUp(self):
		self.sub = FakeSubscription()
		self.provider = FakeProvider()
		self.logged = []
		self.seen = set()
		self.today = FIRST_CHARGE
		patches = [
			mock.patch.object(billing, "nowdate", lambda: self.today.isoformat()),
			mock.patch.object(billing, "settings", lambda: CFG),
			mock.patch.object(billing, "provider", lambda: self.provider),
			mock.patch.object(billing, "_send_template", lambda *a, **k: None),
			mock.patch.object(billing, "_discord", lambda *a, **k: None),
			mock.patch.object(billing, "get_url", lambda path="": path),
			mock.patch.object(billing, "_log_event", self._log),
			mock.patch.object(billing, "frappe", self._fake_frappe()),
		]
		for p in patches:
			p.start()
			self.addCleanup(p.stop)

	def _fake_frappe(self):
		fake = mock.MagicMock()
		fake.get_doc = lambda *a, **k: self.sub
		fake.db.exists = self._exists
		fake.db.get_value = self._get_value
		fake.utils.formatdate = lambda d: str(d)
		return fake

	def _log(self, event_id, provider_name, event_type, status, **fields):
		self.seen.add(event_id)
		self.logged.append((event_type, status))

	def _exists(self, doctype, name=None):
		if doctype == "Examic Payment Event":
			return name in self.seen
		return doctype == billing.SUBSCRIPTION and name == USER

	def _get_value(self, doctype, filters, fieldname=None, **_):
		if isinstance(filters, dict):
			for field, value in filters.items():
				if getattr(self.sub, field, None) == value:
					return USER
		return None

	def access(self, today):
		sub = self.sub
		status = billing.status_for(sub.trial_ends_on, sub.paid_until, sub.pending_plan, today)
		state = billing.state_for(status, False, True)
		early = billing.monthly_checkout_paid(state, sub.plan, sub.stripe_subscription, sub.card_required)
		return status, state, billing.mocks_unlocked(state) or early

	def test_monthly_signup_stays_in_the_free_month_until_the_first_invoice(self):
		# Card saved: nothing paid, so no plan, no paid date, and the mocks stay locked.
		self.assertEqual(billing.process_stripe_event(checkout("Monthly")), "Matched")
		self.assertEqual((self.sub.plan, self.sub.pending_plan, self.sub.paid_until), ("", "Monthly", None))
		self.assertEqual(self.sub.stripe_subscription, "sub_1")
		self.assertEqual(self.access(date(2026, 10, 27)), ("Trial", "trial", False))
		self.assertEqual(self.access(TRIAL_END), ("Trial", "trial", False))

		# Stripe's own 0.00 first invoice and a repeated delivery change nothing.
		self.assertEqual(billing.process_stripe_event(invoice(0, "subscription_create", "Monthly", "evt_i0")), "Ignored")
		self.assertEqual(billing.process_stripe_event(checkout("Monthly")), "Ignored")
		self.assertEqual((self.sub.plan, self.sub.paid_until), ("", None))

		# First charge day, before the webhook arrives: locked, never open.
		self.assertEqual(self.access(FIRST_CHARGE), ("Awaiting Payment", "locked", False))

		# The charge succeeds: one paid month, starting after the free month, all mocks open.
		self.assertEqual(billing.process_stripe_event(invoice(4900, "subscription_cycle", "Monthly", "evt_i1")), "Matched")
		self.assertEqual((self.sub.plan, self.sub.pending_plan), ("Monthly", None))
		self.assertEqual(self.sub.paid_until, date(2026, 12, 26))
		self.assertEqual(len(self.sub.payments), 1)
		self.assertEqual(self.access(FIRST_CHARGE), ("Active", "paid", True))

		# The same invoice delivered again must not extend the period or add a payment.
		self.assertEqual(billing.process_stripe_event(invoice(4900, "subscription_cycle", "Monthly", "evt_i1")), "Ignored")
		self.assertEqual((self.sub.paid_until, len(self.sub.payments)), (date(2026, 12, 26), 1))

		# The next monthly invoice adds exactly one more month.
		billing.process_stripe_event(invoice(4900, "subscription_cycle", "Monthly", "evt_i2"))
		self.assertEqual(self.sub.paid_until, date(2027, 1, 26))

	def test_three_month_signup_ends_after_one_term_and_opens_only_on_payment(self):
		billing.process_stripe_event(checkout("3-Month", "evt_co3"))
		self.assertEqual((self.sub.plan, self.sub.pending_plan), ("", "3-Month"))
		self.assertEqual(len(self.provider.ended), 1, "the fixed term must be scheduled to stop renewing")
		self.assertEqual(self.access(date(2026, 11, 10))[2], False)
		billing.process_stripe_event(invoice(9900, "subscription_cycle", "3-Month", "evt_i3"))
		self.assertEqual(self.sub.paid_until, date(2027, 2, 26))
		self.assertEqual(self.access(FIRST_CHARGE), ("Active", "paid", True))

	def test_failed_first_charge_keeps_everything_locked_and_flags_the_student(self):
		billing.process_stripe_event(checkout("Monthly"))
		failed = {"id": "evt_f", "type": "invoice.payment_failed", "data": {"object": {
			"customer": "cus_1", "subscription_details": {"metadata": {"user": USER}}}}}
		self.assertEqual(billing.process_stripe_event(failed), "Matched")
		self.assertTrue(self.sub.last_payment_error)
		self.assertEqual(self.access(FIRST_CHARGE)[2], False)

	def test_cancelling_during_the_free_month_returns_to_card_setup_without_paid_access(self):
		billing.process_stripe_event(checkout("Monthly"))
		gone = {"id": "evt_d", "type": "customer.subscription.deleted", "data": {"object": {
			"id": "sub_1", "customer": "cus_1", "metadata": {"user": USER}}}}
		billing.process_stripe_event(gone)
		self.assertEqual((self.sub.stripe_subscription, self.sub.pending_plan, self.sub.paid_until), (None, None, None))
		self.assertEqual(self.access(date(2026, 11, 10))[2], False)

	def test_event_for_an_unknown_student_is_flagged_not_applied(self):
		event = checkout("Monthly", "evt_x")
		event["data"]["object"]["client_reference_id"] = "nobody@example.com"
		event["data"]["object"]["metadata"]["user"] = "nobody@example.com"
		event["data"]["object"]["customer"] = "cus_other"
		event["data"]["object"]["subscription"] = "sub_other"
		self.assertEqual(billing.process_stripe_event(event), "Needs review")
		self.assertEqual((self.sub.plan, self.sub.pending_plan), ("", None))

	def test_old_paid_at_checkout_monthly_still_opens_the_mocks_at_once(self):
		# A student with no card requirement who pays 49 GBP at checkout keeps the original behaviour.
		self.sub.card_required = 0
		self.today = date(2026, 10, 27)
		event = checkout("Monthly", "evt_old")
		event["data"]["object"]["amount_total"] = 4900
		billing.process_stripe_event(event)
		self.assertEqual(self.sub.plan, "Monthly")
		self.assertEqual(self.access(date(2026, 10, 27))[2], True)


if __name__ == "__main__":
	unittest.main()
