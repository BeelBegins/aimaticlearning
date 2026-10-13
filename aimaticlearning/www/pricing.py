from aimaticlearning.lms_learning.public_site import page_context


def get_context(context):
	page_context(context)
	context.title = "Pricing | Examic"
	context.meta_description = (
		f"First month free with every published course and {context.free_mock_names}, no payment card needed. "
		f"Then {context.monthly_price} per month or {context.three_month_price} once for 3 months."
	)
	return context
