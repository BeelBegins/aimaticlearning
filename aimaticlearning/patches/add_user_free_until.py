import frappe

FIELD = "examic_free_until"


def execute():
	"""Add the read-only User date that records the end of a student's free period."""
	if "lms" not in frappe.get_installed_apps():
		return
	if frappe.db.exists("Custom Field", {"dt": "User", "fieldname": FIELD}):
		return
	frappe.get_doc(
		{
			"doctype": "Custom Field",
			"dt": "User",
			"fieldname": FIELD,
			"label": "Examic free until",
			"fieldtype": "Date",
			"read_only": 1,
			"no_copy": 1,
			"description": "Recorded at signup. Nothing locks access when it passes.",
		}
	).insert(ignore_permissions=True)
