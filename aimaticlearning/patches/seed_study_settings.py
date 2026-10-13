import frappe

MODEL = "nvidia/nemotron-3.5-lightning"


def execute():
	if not frappe.db.exists("DocType", "Examic Study Settings"):
		return
	doc = frappe.get_single("Examic Study Settings")
	if doc.get("models"):
		return
	doc.append(
		"models",
		{"model_id": MODEL, "label": "Nemotron 3.5 Lightning", "enabled": 1},
	)
	doc.default_model = MODEL
	doc.study_buddy_enabled = 1
	doc.save(ignore_permissions=True)
