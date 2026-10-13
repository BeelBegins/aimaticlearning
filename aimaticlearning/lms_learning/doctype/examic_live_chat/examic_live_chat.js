frappe.ui.form.on("Examic Live Chat", {
	refresh(frm) {
		if (frm.is_new()) return;
		hideRawFields(frm);
		bindLiveRefresh(frm);
		renderStaffChat(frm);
	},
});

function hideRawFields(frm) {
	[
		"student",
		"status",
		"column_break_context",
		"course",
		"lesson_title",
		"section_break_preview",
		"last_message",
		"last_message_at",
		"section_break_messages",
		"messages",
	].forEach(function (fieldname) {
		frm.set_df_property(fieldname, "hidden", 1);
	});
	frm.page.clear_inner_toolbar();
}

function bindLiveRefresh(frm) {
	if (frm._examic_live_chat_bound) return;
	frm._examic_live_chat_bound = true;
	frappe.realtime.on("examic_live_chat", function (data) {
		if (data && data.thread === frm.doc.name && !frm._examic_chat_draft) {
			frm.reload_doc();
		}
	});
}

function renderStaffChat(frm) {
	const host = frm.layout && frm.layout.wrapper;
	if (!host) return;
	const previous = host.find(".examic-staff-chat textarea");
	const draft = previous.length ? previous.val() : frm._examic_chat_draft || "";
	frm._examic_chat_draft = draft || null;
	host.find(".examic-staff-chat").remove();

	const panel = $(
		'<section class="examic-staff-chat">' +
			'<header class="examic-staff-chat-head"></header>' +
			'<div class="examic-staff-chat-log" role="log"></div>' +
			'<div class="examic-staff-chat-compose">' +
				'<textarea rows="3" placeholder="Reply to the student"></textarea>' +
				'<button type="button">Send reply</button>' +
			"</div>" +
		"</section>"
	);
	host.append(panel);

	const head = panel.find(".examic-staff-chat-head");
	$("<p>").addClass("examic-staff-chat-kicker").text("Student").appendTo(head);
	$("<h2>").text(frm.doc.student || "Student").appendTo(head);
	const context = [frm.doc.course, frm.doc.lesson_title].filter(Boolean).join(" · ");
	if (context) {
		$("<p>").addClass("examic-staff-chat-context").text(context).appendTo(head);
	}
	const statusRow = $("<div>").addClass("examic-staff-chat-status").appendTo(head);
	const status = $("<select>").attr("aria-label", "Status");
	["Open", "Waiting", "Closed"].forEach(function (option) {
		$("<option>").val(option).text(option).appendTo(status);
	});
	status.val(frm.doc.status || "Open");
	status.on("change", function () {
		frm.set_value("status", status.val());
		frm.save();
	});
	status.appendTo(statusRow);
	if (frm.doc.status === "Waiting") {
		$("<span>").text("Waiting for a reply").appendTo(statusRow);
	}

	const log = panel.find(".examic-staff-chat-log");
	const messages = frm.doc.messages || [];
	if (!messages.length) {
		$("<p>").addClass("examic-staff-chat-empty").text("No messages yet.").appendTo(log);
	}
	messages.forEach(function (row) {
		const mine = row.role === "Staff";
		const bubble = $("<article>")
			.addClass("examic-staff-chat-bubble")
			.toggleClass("is-staff", mine)
			.appendTo(log);
		const who = mine ? (row.sender === frappe.session.user ? "You" : row.sender || "Staff") : "Student";
		const meta = $("<p>").addClass("examic-staff-chat-meta").appendTo(bubble);
		$("<span>").text(who).appendTo(meta);
		if (row.sent_at) {
			$("<time>").text(chatTime(row.sent_at)).appendTo(meta);
		}
		$("<p>").addClass("examic-staff-chat-body").text(row.body || "").appendTo(bubble);
	});
	log.scrollTop(log.prop("scrollHeight"));

	const input = panel.find("textarea");
	const button = panel.find("button");
	if (draft) input.val(draft);
	input.on("input", function () {
		frm._examic_chat_draft = input.val();
	});
	input.on("keydown", function (event) {
		if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
			event.preventDefault();
			sendStaffReply(frm, input, button);
		}
	});
	button.on("click", function () {
		sendStaffReply(frm, input, button);
	});
}

function chatTime(value) {
	const pretty = frappe.datetime.prettyDate ? String(frappe.datetime.prettyDate(value) || "") : "";
	const parsed = frappe.datetime.str_to_obj ? frappe.datetime.str_to_obj(value) : null;
	const date = parsed && typeof parsed.toDate === "function" ? parsed.toDate() : parsed;
	let clock = "";
	if (date instanceof Date && !Number.isNaN(date.getTime())) {
		clock = String(date.getHours()).padStart(2, "0") + ":" + String(date.getMinutes()).padStart(2, "0");
	}
	const plain = [pretty, clock].filter(Boolean).join(" · ").replace(/<[^>]*>/g, "");
	return plain || String(frappe.datetime.str_to_user(value) || "").replace(/<[^>]*>/g, "");
}

function sendStaffReply(frm, input, button) {
	const body = (input.val() || "").trim();
	if (!body) {
		input.focus();
		return;
	}
	button.prop("disabled", true);
	frm._examic_chat_draft = null;
	frm.call("send_reply", { body: body })
		.then(function () {
			input.val("");
			frm.reload_doc();
		})
		.fail(function () {
			frm._examic_chat_draft = body;
			button.prop("disabled", false);
		});
}
