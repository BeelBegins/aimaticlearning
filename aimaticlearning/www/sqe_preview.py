from aimaticlearning.lms_learning.preview import require_preview_access
from aimaticlearning.www.sqe import get_context as get_sqe_context


def get_context(context):
	require_preview_access()
	context = get_sqe_context(context, preview_mode=True)
	context.no_cache = 1
	context.preview_mode = True
	context.body_class = "sqe-public-page sqe-preview-page"
	context.title = "Examic Study Preview | Focused SQE Preparation"
	context.canonical_url = "https://examic.study/sqe-preview"
	return context
