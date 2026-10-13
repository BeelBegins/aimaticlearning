from aimaticlearning.lms_learning.public_site import page_context


def get_context(context):
	page_context(context)
	context.title = "How It Works | Examic"
	context.meta_description = (
		"Create an account, use the free month, explore your subjects and study, practise and review "
		"for SQE1 on Examic.study."
	)
	return context
