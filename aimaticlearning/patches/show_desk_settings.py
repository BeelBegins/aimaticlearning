"""Give the two desk tiles real icons and point LMS Learning at Examic settings."""

import frappe

ICONS = {
	"LMS Learning": "graduation-cap",
	"Learning": "book-open",
}


def execute():
	for name, icon in ICONS.items():
		if frappe.db.exists("Workspace", name):
			frappe.db.set_value("Workspace", name, "icon", icon, update_modified=False)
		if frappe.db.exists("Desktop Icon", name):
			frappe.db.set_value("Desktop Icon", name, "icon", icon, update_modified=False)
	frappe.clear_cache()
