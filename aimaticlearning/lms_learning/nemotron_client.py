"""OpenRouter chat client for Examic Study Buddy.

Uses only frappe.conf (site_config / common_site_config). Does not import
the SZL `aimatic` app or any of its DocTypes.

	bench set-config -g openrouter_api_key "sk-or-..."
	bench --site lms.aimatic.tech set-config openrouter_study_buddy_model \
		"nvidia/nemotron-3.5-lightning"
"""

from __future__ import annotations

import json

import frappe
import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"
STUDY_BUDDY_MODEL = "nvidia/nemotron-3.5-lightning"
STUDY_BUDDY_LEGACY_MODEL = "deepseek/deepseek-v4-flash"
DEFAULT_TIMEOUT = 60


class NemotronError(Exception):
	def __init__(
		self,
		message: str,
		*,
		code: str = "provider",
		retryable: bool = False,
		http_status: int | None = None,
	):
		super().__init__(message)
		self.code = code
		self.retryable = retryable
		self.http_status = http_status


def _get_api_key() -> str:
	api_key = frappe.conf.get("openrouter_api_key")
	if not api_key:
		raise NemotronError(
			"OpenRouter is not configured.",
			code="configuration",
		)
	return api_key


def _get_model() -> str:
	return frappe.conf.get("openrouter_nemotron_model") or DEFAULT_MODEL


def get_study_buddy_model() -> str:
	"""Return one paid model, allowing only the current model during rollout."""
	configured = str(frappe.conf.get("openrouter_study_buddy_model") or "").strip()
	if not configured:
		return STUDY_BUDDY_MODEL
	if configured.endswith(":free") or configured not in {
		STUDY_BUDDY_MODEL,
		STUDY_BUDDY_LEGACY_MODEL,
	}:
		raise NemotronError(
			"Study Buddy has an unsupported model configuration.", code="configuration"
		)
	return configured


def get_chat_completion(
	messages: list[dict],
	temperature: float = 0.2,
	max_tokens: int = 1024,
	model: str | None = None,
	timeout: int = DEFAULT_TIMEOUT,
	return_metadata: bool = False,
) -> dict:
	"""Return the assistant message, optionally with sanitized response metadata."""
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
	except requests.Timeout as exc:
		raise NemotronError(
			"OpenRouter timed out.", code="timeout", retryable=True
		) from exc
	except requests.RequestException as exc:
		raise NemotronError(
			"OpenRouter could not be reached.", code="network", retryable=True
		) from exc

	if response.status_code != 200:
		status = int(response.status_code)
		if status == 429:
			code = "rate_limited"
		elif status >= 500:
			code = "provider_unavailable"
		else:
			code = "provider_rejected"
		raise NemotronError(
			f"OpenRouter request failed with HTTP {status}.",
			code=code,
			retryable=status == 429 or status >= 500,
			http_status=status,
		)

	try:
		data = response.json()
	except ValueError as exc:
		raise NemotronError(
			"OpenRouter returned invalid JSON.", code="invalid_response", retryable=True
		) from exc
	try:
		choice = data["choices"][0]
		message = choice["message"]
	except (KeyError, IndexError, TypeError) as exc:
		raise NemotronError(
			"OpenRouter returned an unexpected response.",
			code="invalid_response",
			retryable=True,
		) from exc
	if not return_metadata:
		return message
	return {
		"message": message,
		"finish_reason": str(choice.get("finish_reason") or "")[:80],
		"usage": data.get("usage") if isinstance(data.get("usage"), dict) else {},
		"provider": str(data.get("provider") or "")[:140],
	}
