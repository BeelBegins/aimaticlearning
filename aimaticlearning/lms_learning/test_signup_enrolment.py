import unittest
from types import SimpleNamespace
from unittest import mock

from aimaticlearning.lms_learning import billing, enrollment


def _user(roles=("LMS Student",), user_type="Website User", skip_welcome=False):
	return SimpleNamespace(
		name="new@example.com",
		user_type=user_type,
		flags=SimpleNamespace(skip_lms_welcome_email=skip_welcome),
		get=lambda key: [SimpleNamespace(role=r) for r in roles] if key == "roles" else None,
	)


class TestSignupEnrolment(unittest.TestCase):
	def test_free_period_is_one_month_and_two_mocks(self):
		self.assertEqual(enrollment.PRODUCT_SETTINGS["free_days"], 30)
		self.assertEqual(enrollment.PRODUCT_SETTINGS["free_mocks"], 2)
		self.assertEqual(str(enrollment.free_until("2026-10-10")), "2026-11-09")

	@mock.patch.object(enrollment, "is_lms_site", return_value=True)
	def test_only_self_service_student_signups_are_enrolled(self, _site):
		self.assertTrue(enrollment.is_new_student_signup(_user()))
		self.assertFalse(enrollment.is_new_student_signup(_user(skip_welcome=True)))
		self.assertFalse(enrollment.is_new_student_signup(_user(user_type="System User")))
		self.assertFalse(enrollment.is_new_student_signup(_user(roles=("Guest",))))

	@mock.patch.object(enrollment.frappe, "enqueue")
	@mock.patch.object(enrollment, "is_lms_site", return_value=True)
	def test_signup_queues_one_job_after_commit(self, _site, enqueue):
		enrollment.start_student_signup(_user())
		self.assertEqual(enqueue.call_count, 1)
		self.assertTrue(enqueue.call_args.kwargs["enqueue_after_commit"])
		enqueue.reset_mock()
		enrollment.start_student_signup(_user(skip_welcome=True))
		enqueue.assert_not_called()

	def _run(self, existing=(), failing=()):
		doc = SimpleNamespace(full_name="New Student", email="new@example.com", name="new@example.com", get=lambda k: None)

		def enroll(member, course, skip_email=False, **kw):
			if course in failing:
				raise RuntimeError("boom")
			return "ENR-" + course

		patches = [
			mock.patch.object(enrollment.frappe, "session", SimpleNamespace(user="Guest")),
			mock.patch.object(enrollment.frappe, "set_user"),
			mock.patch.object(enrollment.frappe, "get_doc", return_value=doc),
			mock.patch.object(enrollment, "signup_courses", return_value=["tort", "land", "wills"]),
			mock.patch.object(enrollment, "enroll_member_in_course", side_effect=enroll),
			mock.patch.object(enrollment.frappe, "get_meta", return_value=SimpleNamespace(has_field=lambda f: True)),
			mock.patch.object(enrollment.frappe, "log_error"),
			mock.patch.object(enrollment, "_render_template", return_value=("subject", "body")),
			mock.patch.object(enrollment, "_queue_email"),
			mock.patch.object(enrollment, "free_until", return_value="2026-11-09"),
			mock.patch.object(billing, "settings", return_value={"trial_days": 30}),
			mock.patch.object(billing, "create_subscription"),
			mock.patch.object(enrollment, "get_url", side_effect=lambda path: "https://lms.example" + path),
			mock.patch.object(enrollment.frappe.utils, "formatdate", side_effect=lambda d: str(d)),
		]
		db = SimpleNamespace(
			exists=lambda dt, filters=None: bool(filters and filters.get("course") in existing),
			get_value=lambda dt, name, field=None: name.title(),
			set_value=mock.Mock(),
		)
		patches.append(mock.patch.object(enrollment.frappe, "db", db))
		for p in patches:
			p.start()
		self.addCleanup(mock.patch.stopall)
		return enrollment.complete_student_signup("new@example.com"), db

	def test_new_student_gets_every_course_and_one_welcome_email(self):
		result, db = self._run()
		self.assertEqual(result, {"user": "new@example.com", "courses": 3, "new_enrolments": 3})
		self.assertEqual(enrollment._queue_email.call_count, 1)
		context = enrollment._render_template.call_args.args[1]
		self.assertEqual(context["course_titles"], ["Tort", "Land", "Wills"])
		self.assertEqual(context["free_days"], 30)
		billing.create_subscription.assert_called_once_with("new@example.com")
		db.set_value.assert_called_once()
		self.assertEqual(db.set_value.call_args.args[:3], ("User", "new@example.com", "examic_free_until"))

	def test_rerun_is_idempotent_and_sends_no_second_email(self):
		result, _db = self._run(existing=("tort", "land", "wills"))
		self.assertEqual(result["new_enrolments"], 0)
		enrollment._queue_email.assert_not_called()

	def test_one_failing_course_does_not_stop_the_rest(self):
		result, _db = self._run(failing=("land",))
		self.assertEqual(result["courses"], 2)
		self.assertEqual(result["new_enrolments"], 2)
		enrollment.frappe.log_error.assert_called_once()


class TestSignupEmail(unittest.TestCase):
	def test_plain_addresses_pass_and_probes_fail(self):
		from aimaticlearning.lms_learning.enrollment import is_plausible_email

		for good in ("a.b+c@example.com", "student@mail.co.uk"):
			self.assertTrue(is_plausible_email(good), good)
		for bad in ("", "x@y", "sample@email.tst' and 2*3*8=6*8", "a b@x.com", 'a"b@x.com', "a@x.com;drop", "<a@x.com>"):
			self.assertFalse(is_plausible_email(bad), bad)


if __name__ == "__main__":
	unittest.main()
