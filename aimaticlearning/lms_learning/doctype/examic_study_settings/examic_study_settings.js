frappe.ui.form.on("Examic Study Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Test OpenRouter"), function () {
			frm.call("test_openrouter").then(function (r) {
				const message = (r.message && r.message.message) || __("OpenRouter did not answer.");
				frappe.msgprint(message);
			});
		});
		frm.add_custom_button(__("Send test alert"), function () {
			frm.call("send_test_alert").then(function (r) {
				const message = (r.message && r.message.message) || __("Discord did not accept the alert.");
				frappe.msgprint(message);
			});
		});
	},
});
