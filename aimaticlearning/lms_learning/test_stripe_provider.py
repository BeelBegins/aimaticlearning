import hashlib
import hmac
import unittest

from aimaticlearning.lms_learning.billing_providers import stripe as sp

SECRET = "whsec_test_secret"
BODY = b'{"id":"evt_1","type":"invoice.paid"}'


def _header(body=BODY, secret=SECRET, ts=1_800_000_000, extra=""):
	sig = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
	return f"t={ts},v1={sig}{extra}"


class TestSignature(unittest.TestCase):
	def test_valid_signature_passes(self):
		self.assertTrue(sp.verify_signature(BODY, _header(), SECRET, now=1_800_000_100))

	def test_tampered_body_fails(self):
		self.assertFalse(sp.verify_signature(BODY + b" ", _header(), SECRET, now=1_800_000_100))

	def test_wrong_secret_or_missing_header_fails(self):
		self.assertFalse(sp.verify_signature(BODY, _header(secret="other"), SECRET, now=1_800_000_100))
		self.assertFalse(sp.verify_signature(BODY, "", SECRET, now=1_800_000_100))
		self.assertFalse(sp.verify_signature(BODY, _header(), "", now=1_800_000_100))

	def test_old_timestamp_fails(self):
		self.assertFalse(sp.verify_signature(BODY, _header(), SECRET, now=1_800_000_000 + 301))

	def test_any_matching_v1_signature_passes(self):
		self.assertTrue(sp.verify_signature(BODY, _header(extra=",v1=deadbeef"), SECRET, now=1_800_000_000))


class TestInterpretEvent(unittest.TestCase):
	def test_one_off_checkout_pays(self):
		event = {"type": "checkout.session.completed", "data": {"object": {
			"mode": "payment", "payment_status": "paid", "amount_total": 9900, "client_reference_id": "a@b.com",
			"metadata": {"plan": "3-Month"}, "payment_intent": "pi_1", "customer": "cus_1"}}}
		action = sp.interpret_event(event)
		self.assertEqual((action["action"], action["plan"], action["amount"], action["user"]), ("pay", "3-Month", 99.0, "a@b.com"))
		self.assertEqual(action["reference"], "pi_1")

	def test_subscription_checkout_only_links(self):
		event = {"type": "checkout.session.completed", "data": {"object": {
			"mode": "subscription", "payment_status": "paid", "amount_total": 4900, "client_reference_id": "a@b.com",
			"metadata": {"plan": "Monthly"}, "customer": "cus_1", "subscription": "sub_1"}}}
		action = sp.interpret_event(event)
		self.assertEqual(action["action"], "link")
		self.assertEqual((action["customer"], action["subscription"]), ("cus_1", "sub_1"))

	def test_invoice_paid_extends_monthly_and_zero_invoice_is_ignored(self):
		paid = {"type": "invoice.paid", "data": {"object": {"id": "in_1", "amount_paid": 4900, "customer": "cus_1",
			"subscription": "sub_1", "subscription_details": {"metadata": {"user": "a@b.com"}}}}}
		action = sp.interpret_event(paid)
		self.assertEqual((action["action"], action["plan"], action["amount"], action["user"]), ("pay", "Monthly", 49.0, "a@b.com"))
		paid["data"]["object"]["amount_paid"] = 0
		self.assertEqual(sp.interpret_event(paid)["action"], "ignore")

	def test_trial_checkout_links_the_card_and_waits_for_the_first_invoice(self):
		event = {"type": "checkout.session.completed", "data": {"object": {
			"mode": "subscription", "payment_status": "no_payment_required", "amount_total": 0,
			"client_reference_id": "a@b.com", "metadata": {"plan": "3-Month"}, "customer": "cus_1", "subscription": "sub_1"}}}
		action = sp.interpret_event(event)
		self.assertEqual((action["action"], action["plan"], action["user"]), ("trial", "3-Month", "a@b.com"))
		self.assertEqual((action["customer"], action["subscription"]), ("cus_1", "sub_1"))

	def test_invoice_paid_takes_the_plan_from_subscription_metadata(self):
		paid = {"type": "invoice.paid", "data": {"object": {"id": "in_2", "amount_paid": 9900, "customer": "cus_1",
			"subscription": "sub_1", "billing_reason": "subscription_cycle",
			"subscription_details": {"metadata": {"user": "a@b.com", "plan": "3-Month"}}}}}
		action = sp.interpret_event(paid)
		self.assertEqual((action["plan"], action["amount"], action["starts_now"]), ("3-Month", 99.0, False))

	def test_failed_cancelled_and_unknown(self):
		failed = sp.interpret_event({"type": "invoice.payment_failed", "data": {"object": {"customer": "cus_1"}}})
		self.assertEqual(failed["action"], "failed")
		gone = sp.interpret_event({"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_1", "customer": "cus_1"}}})
		self.assertEqual(gone["action"], "cancelled")
		self.assertEqual(sp.interpret_event({"type": "charge.refunded", "data": {"object": {}}})["action"], "ignore")


class TestTrialEnd(unittest.TestCase):
	def test_first_charge_is_the_day_after_the_free_month_if_far_enough(self):
		import calendar, datetime
		now = calendar.timegm(datetime.datetime(2026, 10, 10).timetuple())
		stamp = sp.trial_end_timestamp("2026-11-09", now=now)
		self.assertEqual(datetime.datetime.utcfromtimestamp(stamp).date().isoformat(), "2026-11-10")

	def test_too_close_means_charge_now(self):
		import calendar, datetime
		now = calendar.timegm(datetime.datetime(2026, 11, 8).timetuple())
		self.assertIsNone(sp.trial_end_timestamp("2026-11-09", now=now))
		self.assertIsNone(sp.trial_end_timestamp(None))


if __name__ == "__main__":
	unittest.main()


class TestFixedTerm(unittest.TestCase):
	def _day(self, stamp):
		import datetime
		return datetime.datetime.fromtimestamp(stamp, datetime.UTC).date().isoformat()

	def test_first_charge_is_the_day_after_the_free_month(self):
		self.assertEqual(str(sp.first_charge_date("2026-11-09")), "2026-11-10")

	def test_three_month_plan_stops_three_months_after_the_first_charge(self):
		self.assertEqual(self._day(sp.plan_end_timestamp("3-Month", "2026-11-09", deferred=True)), "2027-02-10")

	def test_three_month_plan_paid_now_stops_three_months_from_today(self):
		self.assertEqual(self._day(sp.plan_end_timestamp("3-Month", None, deferred=False, today="2026-10-24")), "2027-01-24")


class TestStartPayment(unittest.TestCase):
	CFG = {"stripe_secret_key": "sk_test", "stripe_monthly_price_id": "price_m", "stripe_three_month_price_id": "price_once",
		"stripe_three_month_recurring_price_id": "price_3m", "stripe_automatic_tax": 0}

	def _start(self, plan, cfg=None, sub=None):
		from unittest import mock

		sent = {}

		def fake_post(path, data, secret):
			sent.update(data)
			return {"url": "https://checkout.example/session"}

		with mock.patch.object(sp, "_post", fake_post), mock.patch.object(sp.frappe.utils, "get_url", lambda *a: "https://x.test"):
			result = sp.StripeProvider().start_payment("a@b.com", "a@b.com", plan, cfg or self.CFG, sub or {})
		return result, sent

	def test_deferred_monthly_collects_a_card_and_sets_the_trial_end(self):
		from unittest import mock

		with mock.patch.object(sp, "trial_end_timestamp", lambda day: 1_900_000_000):
			result, sent = self._start("Monthly", sub={"defer_charge": True, "trial_ends_on": "2026-11-09"})
		self.assertTrue(result["deferred"])
		self.assertEqual((sent["mode"], sent["line_items[0][price]"]), ("subscription", "price_m"))
		self.assertEqual(sent["subscription_data[trial_end]"], 1_900_000_000)
		self.assertEqual(sent["payment_method_collection"], "always")
		self.assertEqual(sent["subscription_data[metadata][plan]"], "Monthly")

	def test_deferred_three_month_uses_the_recurring_price(self):
		from unittest import mock

		with mock.patch.object(sp, "trial_end_timestamp", lambda day: 1_900_000_000):
			_, sent = self._start("3-Month", sub={"defer_charge": True, "trial_ends_on": "2026-11-09"})
		self.assertEqual((sent["mode"], sent["line_items[0][price]"]), ("subscription", "price_3m"))

	def test_three_month_without_recurring_price_cannot_be_deferred(self):
		cfg = {**self.CFG, "stripe_three_month_recurring_price_id": ""}
		with self.assertRaises(Exception):
			self._start("3-Month", cfg=cfg, sub={"defer_charge": True, "trial_ends_on": "2026-11-09"})

	def test_without_defer_the_old_one_off_payment_is_unchanged(self):
		cfg = {**self.CFG, "stripe_three_month_recurring_price_id": ""}
		result, sent = self._start("3-Month", cfg=cfg)
		self.assertFalse(result["deferred"])
		self.assertEqual((sent["mode"], sent["line_items[0][price]"]), ("payment", "price_once"))
		self.assertNotIn("subscription_data[trial_end]", sent)
