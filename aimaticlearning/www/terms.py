from aimaticlearning.lms_learning.public_site import page_context


def get_context(context):
	page_context(context)
	context.title = "Terms and Conditions | Examic"
	context.meta_description = "The learner terms and conditions for Examic.study, operated by EXAMIC LTD."
	return context
