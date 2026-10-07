from aimaticlearning.lms_learning import billing


def get_context(context):
	context.no_cache = 1
	cfg = billing.settings()
	context.monthly_price = billing.price_text(cfg["monthly_price"])
	context.three_month_price = billing.price_text(cfg["three_month_price"])
	context.three_month_each = billing.price_text(round(cfg["three_month_price"] / 3, 2))
	context.title = "Pricing | Examic Study"
	context.meta_description = (
		f"First month free, then {context.monthly_price} per month or {context.three_month_price} for 3 months. "
		"All mock exams, full preparation resources and performance analytics."
	)
	return context
