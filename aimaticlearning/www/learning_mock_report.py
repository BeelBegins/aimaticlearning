from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import get_url

from aimaticlearning.lms_learning.statistics import can_view_statistics


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote("/learning-mock-report", safe="")
		raise frappe.Redirect
	if not can_view_statistics():
		frappe.local.flags.redirect_location = "/learning-mock-exam"
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = False
	context.title = _("Mock coverage")
	context.canonical_url = get_url("/learning-mock-report")
