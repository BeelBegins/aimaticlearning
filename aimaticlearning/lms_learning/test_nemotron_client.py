import inspect
import json
import unittest
from unittest.mock import patch

import requests

from aimaticlearning.lms_learning import study_buddy
from aimaticlearning.lms_learning.nemotron_client import (
	STUDY_BUDDY_MODEL,
	NemotronError,
	get_chat_completion,
	get_study_buddy_model,
)


class TestNemotronClient(unittest.TestCase):
	def test_study_buddy_does_not_import_aimatic_erp(self):
		from aimaticlearning.lms_learning import nemotron_client as nc

		source = inspect.getsource(study_buddy)
		self.assertNotIn("aimatic.ai", source)
		self.assertIn("aimaticlearning.lms_learning.nemotron_client", source)
		self.assertNotIn("get_cached_doc", inspect.getsource(nc))
		self.assertNotIn("aimatic.ai", inspect.getsource(nc))

	@patch("aimaticlearning.lms_learning.nemotron_client.requests.post")
	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_get_chat_completion_returns_message(self, frappe, post):
		frappe.conf.get.side_effect = lambda key, default=None: {
			"openrouter_api_key": "sk-test",
			"openrouter_nemotron_model": "nvidia/test",
		}.get(key, default)
		post.return_value.status_code = 200
		post.return_value.json.return_value = {
			"choices": [{"message": {"role": "assistant", "content": "from the lesson"}}]
		}
		message = get_chat_completion([{"role": "user", "content": "hi"}], timeout=45)
		self.assertEqual(message["content"], "from the lesson")
		headers = post.call_args.kwargs["headers"]
		self.assertEqual(headers["Authorization"], "Bearer sk-test")
		payload = json.loads(post.call_args.kwargs["data"])
		self.assertEqual(payload["model"], "nvidia/test")

	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_study_buddy_defaults_to_paid_lightning(self, frappe):
		frappe.conf.get.return_value = None
		self.assertEqual(STUDY_BUDDY_MODEL, "nvidia/nemotron-3.5-lightning")
		self.assertEqual(get_study_buddy_model(), STUDY_BUDDY_MODEL)
		self.assertNotIn(":free", get_study_buddy_model())

	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_current_paid_model_is_allowed_only_during_rollout(self, frappe):
		frappe.conf.get.return_value = "deepseek/deepseek-v4-flash"
		self.assertEqual(get_study_buddy_model(), "deepseek/deepseek-v4-flash")

	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_free_or_unknown_model_configuration_is_rejected(self, frappe):
		for configured in (
			"nvidia/nemotron-3.5-lightning:free",
			"nvidia/nemotron-3-ultra-550b-a55b",
		):
			with self.subTest(configured=configured):
				frappe.conf.get.return_value = configured
				with self.assertRaises(NemotronError) as raised:
					get_study_buddy_model()
				self.assertEqual(raised.exception.code, "configuration")

	@patch("aimaticlearning.lms_learning.nemotron_client.requests.post")
	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_completion_metadata_is_sanitized_and_available(self, frappe, post):
		frappe.conf.get.return_value = "sk-test"
		post.return_value.status_code = 200
		post.return_value.json.return_value = {
			"id": "request-1",
			"provider": "NVIDIA",
			"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "Answer"}}],
			"usage": {"prompt_tokens": 100, "completion_tokens": 20},
		}
		result = get_chat_completion(
			[{"role": "user", "content": "hi"}],
			model=STUDY_BUDDY_MODEL,
			return_metadata=True,
		)
		self.assertEqual(result["message"]["content"], "Answer")
		self.assertEqual(result["finish_reason"], "stop")
		self.assertEqual(result["usage"]["completion_tokens"], 20)

	@patch("aimaticlearning.lms_learning.nemotron_client.requests.post")
	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_provider_error_does_not_leak_response_body(self, frappe, post):
		frappe.conf.get.return_value = "sk-test"
		post.return_value.status_code = 502
		post.return_value.text = "private upstream details"
		with self.assertRaises(NemotronError) as raised:
			get_chat_completion([{"role": "user", "content": "hi"}])
		self.assertTrue(raised.exception.retryable)
		self.assertEqual(raised.exception.code, "provider_unavailable")
		self.assertNotIn("private upstream details", str(raised.exception))

	@patch("aimaticlearning.lms_learning.nemotron_client.requests.post")
	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_timeout_is_retryable_and_sanitized(self, frappe, post):
		frappe.conf.get.return_value = "sk-test"
		post.side_effect = requests.Timeout("private network details")
		with self.assertRaises(NemotronError) as raised:
			get_chat_completion([{"role": "user", "content": "hi"}])
		self.assertEqual(raised.exception.code, "timeout")
		self.assertTrue(raised.exception.retryable)
		self.assertNotIn("private network details", str(raised.exception))

	@patch("aimaticlearning.lms_learning.nemotron_client.requests.post")
	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_rate_limit_is_retryable_but_client_error_is_not(self, frappe, post):
		frappe.conf.get.return_value = "sk-test"
		post.return_value.status_code = 429
		with self.assertRaises(NemotronError) as limited:
			get_chat_completion([{"role": "user", "content": "hi"}])
		self.assertEqual(limited.exception.code, "rate_limited")
		self.assertTrue(limited.exception.retryable)

		post.return_value.status_code = 400
		with self.assertRaises(NemotronError) as rejected:
			get_chat_completion([{"role": "user", "content": "hi"}])
		self.assertEqual(rejected.exception.code, "provider_rejected")
		self.assertFalse(rejected.exception.retryable)

	@patch("aimaticlearning.lms_learning.nemotron_client.requests.post")
	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_malformed_success_response_is_retryable(self, frappe, post):
		frappe.conf.get.return_value = "sk-test"
		post.return_value.status_code = 200
		post.return_value.json.side_effect = ValueError("private invalid body")
		with self.assertRaises(NemotronError) as raised:
			get_chat_completion([{"role": "user", "content": "hi"}])
		self.assertEqual(raised.exception.code, "invalid_response")
		self.assertTrue(raised.exception.retryable)
		self.assertNotIn("private invalid body", str(raised.exception))

	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_missing_key_raises(self, frappe):
		frappe.conf.get.return_value = None
		with self.assertRaises(NemotronError):
			get_chat_completion([{"role": "user", "content": "hi"}])
