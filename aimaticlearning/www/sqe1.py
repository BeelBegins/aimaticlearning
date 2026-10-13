from aimaticlearning.lms_learning.public_site import flk_catalogue, mock_facts, page_context


def get_context(context):
	page_context(context, **flk_catalogue(), **mock_facts())
	context.title = "SQE1 Preparation | Examic"
	context.meta_description = (
		"Prepare for SQE1 FLK1 and FLK2 with structured notes, chapter practice questions, flashcards "
		"and timed mock exams on Examic.study."
	)
	return context
