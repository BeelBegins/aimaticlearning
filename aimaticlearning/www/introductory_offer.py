from aimaticlearning.lms_learning.public_site import page_context


def get_context(context):
	page_context(context)
	context.title = "Introductory Offer Terms | Examic"
	context.meta_description = (
		f"Your first {context.trial_days} days on Examic are free, with every published course and "
		f"{context.free_mock_names}. No payment card and no automatic charge."
	)
	return context
