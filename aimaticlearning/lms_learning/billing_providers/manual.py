from aimaticlearning.lms_learning.billing_providers.base import PaymentProvider


class ManualProvider(PaymentProvider):
	"""Bank transfer or Pay with Wise. The student reports the payment, staff confirm it."""

	name = "Manual"
