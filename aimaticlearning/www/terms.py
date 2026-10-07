from aimaticlearning.lms_learning import billing


def get_context(context):
	cfg = billing.settings()
	context.monthly_price = billing.price_text(cfg["monthly_price"])
	context.three_month_price = billing.price_text(cfg["three_month_price"])
	return context
