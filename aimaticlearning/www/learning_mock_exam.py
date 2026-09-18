from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import get_url


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote("/learning-mock-exam", safe="")
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = False
	context.title = _("Mock exams")
	context.canonical_url = get_url("/learning-mock-exam")
