import frappe
from frappe import _
from frappe.utils import get_url
from urllib.parse import quote


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote("/learning-dashboard", safe="")
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = False
	context.title = _("Dashboard")
	context.canonical_url = get_url("/learning-dashboard")
