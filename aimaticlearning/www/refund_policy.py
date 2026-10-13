from aimaticlearning.lms_learning.public_site import page_context


def get_context(context):
	page_context(context)
	context.title = "Cancellation and Refund Policy | Examic"
	context.meta_description = "How to cancel an Examic plan, how renewal works and how refunds are handled."
	return context
