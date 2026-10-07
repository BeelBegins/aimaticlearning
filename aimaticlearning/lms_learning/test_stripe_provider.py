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
