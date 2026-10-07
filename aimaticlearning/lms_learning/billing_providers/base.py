"""Payment provider interface. Providers only talk to a payment service; access and
dates are decided in billing.py so every provider ends in `billing.apply_payment`."""

from __future__ import annotations


class PaymentProvider:
	name = "Manual"

	def is_ready(self, cfg: dict) -> bool:
		return True

	def start_payment(self, user: str, email: str, plan: str, cfg: dict, subscription: dict) -> dict:
		"""Return {"url": ...} to send the student to a hosted page, or {} for manual instructions."""
		return {}
