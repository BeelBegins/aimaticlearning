import inspect
import json
import unittest
from unittest.mock import patch

from aimaticlearning.lms_learning import study_buddy
from aimaticlearning.lms_learning.nemotron_client import (
	NemotronError,
	get_chat_completion,
	get_study_buddy_model,
	paid_model_id,
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
	def test_study_buddy_model_uses_explicit_flash_not_shared_free_helper(self, frappe):
		frappe.conf.get.side_effect = lambda key, default=None: {
			"openrouter_study_buddy_model": "deepseek/deepseek-v4-flash",
			"openrouter_nemotron_model": "nvidia/nemotron-3-ultra-550b-a55b:free",
		}.get(key, default)
		self.assertEqual(get_study_buddy_model(), "deepseek/deepseek-v4-flash")

	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_study_buddy_model_defaults_to_flash(self, frappe):
		frappe.conf.get.side_effect = lambda key, default=None: {
			"openrouter_study_buddy_model": None,
			"openrouter_nemotron_model": "nvidia/nemotron-3-ultra-550b-a55b:free",
		}.get(key, default)
		self.assertEqual(get_study_buddy_model(), "deepseek/deepseek-v4-flash")

	def test_paid_model_id_strips_free_suffix(self):
		self.assertEqual(paid_model_id("nvidia/nemotron-3-ultra-550b-a55b:free"), "nvidia/nemotron-3-ultra-550b-a55b")
		self.assertEqual(paid_model_id("deepseek/deepseek-v4-flash"), "deepseek/deepseek-v4-flash")

	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_missing_key_raises(self, frappe):
		frappe.conf.get.return_value = None
		with self.assertRaises(NemotronError):
			get_chat_completion([{"role": "user", "content": "hi"}])
