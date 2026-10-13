from aimaticlearning.lms_learning.public_site import flk_catalogue, mock_facts, page_context


def get_context(context):
	page_context(context, **flk_catalogue(), **mock_facts())
	context.title = "Resources | Examic"
	context.meta_description = "The SQE1 FLK1 and FLK2 subjects published on Examic.study and the study tools in each."
	return context
