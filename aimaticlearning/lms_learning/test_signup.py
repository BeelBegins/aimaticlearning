"""Emailed-code signup, driven with an in-memory cache and no database, mail or Stripe."""

import unittest
from types import SimpleNamespace
from unittest import mock

from aimaticlearning.lms_learning import signup

EMAIL = "new.student@example.com"
GOOD = {"email": EMAIL, "full_name": "Jane Doe", "password": "correct horse", "plan": "Monthly", "verify_terms": 1}


class FakeCache:
	def __init__(self):
		self.data = {}

	def get_value(self, key):
		return self.data.get(key)

	def set_value(self, key, value, expires_in_sec=None):
		self.data[key] = value

	def delete_value(self, key):
		self.data.pop(key, None)


class SignupCase(unittest.TestCase):
	def setUp(self):
		self.cache = FakeCache()
		self.mail = []
		self.created = []
		self.logged_in = []
		self.existing = None
		self.fake_frappe = mock.MagicMock()
		self.fake_frappe.cache = self.cache
		self.fake_frappe.DuplicateEntryError = type("DuplicateEntryError", (Exception,), {})
		self.fake_frappe.sendmail = lambda **kw: self.mail.append(kw)
		self.fake_frappe.db.get_value = lambda *a, **k: self.existing
		self.fake_frappe.session.user = "Guest"
		patches = [
			mock.patch.object(signup, "frappe", self.fake_frappe),
			mock.patch.object(signup, "_", lambda text: text),
			mock.patch.object(signup, "is_signup_disabled", lambda: False),
			mock.patch.object(signup, "_support_email", lambda: "help@example.com"),
			mock.patch.object(signup.enrollment, "is_plausible_email", lambda e: "@" in e),
			mock.patch.object(signup, "_create_student", self._create),
			mock.patch.object(signup, "_log_in", lambda user: self.logged_in.append(user)),
			mock.patch.object(signup.billing, "create_subscription", lambda user: None),
			mock.patch.object(signup.billing, "signup_plan_field", lambda: True),
			mock.patch.object(signup.billing, "start_checkout", self._checkout),
		]
		for patch in patches:
			patch.start()
			self.addCleanup(patch.stop)
		self.checkout_error = None
		self.encrypt = mock.patch("frappe.utils.password.encrypt", lambda text: "enc:" + text)
		self.encrypt.start()
		self.addCleanup(self.encrypt.stop)

	def _create(self, email, pending):
		self.created.append((email, pending))
		return email

	def _checkout(self, plan):
		if self.checkout_error:
			raise self.checkout_error
		return {"url": f"https://checkout.example/{plan}"}

	def request(self, **changes):
		args = {**GOOD, **changes}
		return signup.request_signup_code.__wrapped__(**args)

	def verify(self, code, email=EMAIL):
		return signup.verify_signup_code.__wrapped__(email, code)

	def sent_code(self):
		import re

		return re.search(r">(\d{6})</p>", self.mail[-1]["message"]).group(1)


class TestRequestCode(SignupCase):
	def test_valid_form_emails_a_code_and_creates_nothing(self):
		answer = self.request()
		self.assertEqual((answer["status"], answer["email"]), ("sent", EMAIL))
		self.assertEqual(len(self.mail), 1)
		self.assertTrue(self.mail[0]["now"])
		self.assertEqual(self.mail[0]["recipients"], [EMAIL])
		self.assertEqual(len(self.sent_code()), 6)
		self.assertEqual(self.created, [])

	def test_pending_entry_holds_no_plain_password_or_code(self):
		self.request()
		pending = self.cache.get_value(signup.PENDING_KEY.format(EMAIL))
		self.assertEqual(pending["password"], "enc:correct horse")
		self.assertNotIn(self.sent_code(), str(pending))

	def test_email_is_lowercased_and_trimmed(self):
		self.assertEqual(self.request(email="  New.Student@Example.com ")["email"], EMAIL)

	def test_bad_fields_are_reported_by_field(self):
		self.assertEqual(self.request(full_name=" ")["field"], "signup_fullname")
		self.assertEqual(self.request(email="nonsense")["field"], "signup_email")
		self.assertEqual(self.request(plan="Free")["field"], "signup_plan")
		self.assertEqual(self.request(password="short")["field"], "signup_password")
		self.assertEqual(self.request(password=EMAIL)["field"], "signup_password")
		self.assertEqual(self.request(verify_terms=0)["field"], "signup-terms")
		self.assertEqual(self.mail, [])

	def test_existing_and_disabled_accounts_get_no_code(self):
		self.existing = SimpleNamespace(name=EMAIL, enabled=1)
		self.assertEqual(self.request()["status"], "exists")
		self.existing = SimpleNamespace(name=EMAIL, enabled=0)
		self.assertEqual(self.request()["status"], "disabled")
		self.assertEqual(self.mail, [])

	def test_resend_waits_a_minute_then_is_allowed(self):
		self.request()
		again = self.request()
		self.assertEqual(again["status"], "wait")
		self.assertGreater(again["wait"], 0)
		self.assertEqual(len(self.mail), 1)
		self.cache.data[signup.SENDS_KEY.format(EMAIL)] = [signup.time.time() - 61]
		self.assertEqual(self.request()["status"], "sent")

	def test_five_codes_an_hour_is_the_limit(self):
		now = signup.time.time()
		self.cache.data[signup.SENDS_KEY.format(EMAIL)] = [now - 3000 + i for i in range(5)]
		self.assertEqual(self.request()["status"], "limit")
		self.assertEqual(self.mail, [])

	def test_mail_failure_leaves_nothing_pending_and_does_not_say_sent(self):
		self.fake_frappe.sendmail = mock.Mock(side_effect=OSError("smtp down"))
		answer = self.request()
		self.assertEqual(answer["status"], "mail_failed")
		self.assertIsNone(self.cache.get_value(signup.PENDING_KEY.format(EMAIL)))
		self.assertIsNone(self.cache.get_value(signup.SENDS_KEY.format(EMAIL)))

	def test_name_is_escaped_in_the_email(self):
		self.request(full_name="<b>Eve</b>")
		self.assertNotIn("<b>Eve</b>", self.mail[0]["message"])


class TestVerifyCode(SignupCase):
	def test_right_code_creates_signs_in_and_returns_the_card_page(self):
		self.request(plan="3-Month")
		answer = self.verify(self.sent_code())
		self.assertEqual(answer["status"], "ok")
		self.assertEqual(answer["url"], "https://checkout.example/3-Month")
		self.assertEqual([c[0] for c in self.created], [EMAIL])
		self.assertEqual(self.logged_in, [EMAIL])
		self.fake_frappe.db.set_value.assert_called_with("Examic Subscription", EMAIL, "signup_plan", "3-Month", update_modified=False)

	def test_a_code_works_once(self):
		self.request()
		code = self.sent_code()
		self.verify(code)
		self.assertEqual(self.verify(code)["status"], "expired")
		self.assertEqual(len(self.created), 1)

	def test_wrong_code_counts_down_and_ten_failures_lock(self):
		self.request()
		code = self.sent_code()
		wrong = "000000" if code != "000000" else "111111"
		for left in range(signup.MAX_CODE_TRIES - 1, 0, -1):
			answer = self.verify(wrong)
			self.assertEqual((answer["status"], answer["left"]), ("wrong", left))
		self.assertEqual(self.verify(wrong)["status"], "locked")
		self.assertEqual(self.verify(code)["status"], "expired")
		self.assertEqual(self.created, [])

	def test_malformed_codes_are_wrong_not_errors(self):
		self.request()
		for bad in ("", "12345", "abcdef", None):
			self.assertEqual(self.verify(bad)["status"], "wrong")

	def test_code_for_another_email_does_not_work(self):
		self.request()
		code = self.sent_code()
		self.assertEqual(self.verify(code, email="other@example.com")["status"], "expired")

	def test_no_pending_signup_is_expired(self):
		self.assertEqual(self.verify("123456")["status"], "expired")

	def test_account_created_meanwhile_is_reported_not_duplicated(self):
		self.request()
		code = self.sent_code()
		self.existing = SimpleNamespace(name=EMAIL, enabled=1)
		self.assertEqual(self.verify(code)["status"], "exists")
		self.assertEqual(self.created, [])

	def test_stripe_failure_still_creates_and_signs_in_and_falls_back_to_billing(self):
		self.request()
		self.checkout_error = RuntimeError("stripe down")
		answer = self.verify(self.sent_code())
		self.assertEqual((answer["status"], answer["url"], answer["billing"]), ("ok", "", "/billing"))
		self.assertEqual(self.logged_in, [EMAIL])

	def test_duplicate_insert_is_reported_as_registered(self):
		self.request()

		def clash(email, pending):
			raise self.fake_frappe.DuplicateEntryError()

		with mock.patch.object(signup, "_create_student", clash):
			self.assertEqual(self.verify(self.sent_code())["status"], "exists")
		self.assertEqual(self.logged_in, [])


class TestHelpers(unittest.TestCase):
	def test_codes_are_six_digits(self):
		for _ in range(200):
			code = signup.new_code()
			self.assertEqual(len(code), 6)
			self.assertTrue(code.isdigit())

	def test_direct_signup_endpoints_are_refused(self):
		with mock.patch.object(signup, "frappe") as fake, mock.patch.object(signup, "_", lambda text: text):
			signup.refuse_direct_signup("a@b.com", "A B", redirect_to="/x", verify_terms=1)
			fake.throw.assert_called_once()


if __name__ == "__main__":
	unittest.main()
