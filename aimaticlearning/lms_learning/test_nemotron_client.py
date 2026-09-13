import inspect
import unittest
from unittest.mock import patch

from aimaticlearning.lms_learning import study_buddy
from aimaticlearning.lms_learning.nemotron_client import (
	NemotronError,
	get_chat_completion,
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

	@patch("aimaticlearning.lms_learning.nemotron_client.frappe")
	def test_missing_key_raises(self, frappe):
		frappe.conf.get.return_value = None
		with self.assertRaises(NemotronError):
			get_chat_completion([{"role": "user", "content": "hi"}])
