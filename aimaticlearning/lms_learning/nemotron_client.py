"""OpenRouter chat client for Examic Study Buddy.

Uses only frappe.conf (site_config / common_site_config). Does not import
the SZL `aimatic` app or any of its DocTypes.

	bench set-config -g openrouter_api_key "sk-or-..."
	bench --site lms.aimatic.tech set-config openrouter_study_buddy_model "deepseek/deepseek-v4-flash"
"""

from __future__ import annotations

import json

import frappe
import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"
STUDY_BUDDY_DEFAULT_MODEL = "deepseek/deepseek-v4-flash"
DEFAULT_TIMEOUT = 60


class NemotronError(Exception):
	pass


def _get_api_key() -> str:
	api_key = frappe.conf.get("openrouter_api_key")
	if not api_key:
		raise NemotronError(
			"openrouter_api_key is not configured. Set it with: "
			"bench set-config -g openrouter_api_key <your-key>"
		)
	return api_key


def _get_model() -> str:
	return frappe.conf.get("openrouter_nemotron_model") or DEFAULT_MODEL


def paid_model_id(model: str | None) -> str:
	value = str(model or "").strip()
	if value.endswith(":free"):
		value = value[: -len(":free")]
	return value or STUDY_BUDDY_DEFAULT_MODEL


def get_study_buddy_model() -> str:
	"""Paid OpenRouter model for learner Study Buddy (never the :free helper)."""
	explicit = frappe.conf.get("openrouter_study_buddy_model")
	if explicit:
		return paid_model_id(explicit)
	return STUDY_BUDDY_DEFAULT_MODEL


def get_chat_completion(
	messages: list[dict],
	temperature: float = 0.2,
	max_tokens: int = 1024,
	model: str | None = None,
	timeout: int = DEFAULT_TIMEOUT,
) -> dict:
	"""Return the assistant message dict. Raises NemotronError on failure."""
	payload = {
		"model": model or _get_model(),
		"messages": messages,
		"temperature": temperature,
		"max_tokens": max_tokens,
	}

	try:
		response = requests.post(
			OPENROUTER_API_URL,
			headers={
				"Authorization": f"Bearer {_get_api_key()}",
				"Content-Type": "application/json",
			},
			data=json.dumps(payload),
			timeout=timeout,
		)
	except requests.RequestException as exc:
		raise NemotronError(f"OpenRouter request failed: {exc}") from exc

	if response.status_code != 200:
		raise NemotronError(f"OpenRouter returned {response.status_code}: {response.text}")

	data = response.json()
	try:
		return data["choices"][0]["message"]
	except (KeyError, IndexError, TypeError) as exc:
		raise NemotronError(f"Unexpected OpenRouter response shape: {data}") from exc
