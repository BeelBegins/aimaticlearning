// Public Examic website: mobile menu, About submenu, cookie choice and the contact form.
// Loaded only by templates/examic_site/base.html. No tracking is loaded here or anywhere
// on the public site; examicCookieChoice() exists so any future optional tool can check it.
(function () {
	"use strict";

	var COOKIE = "examic_cookie_choice";
	var MAX_AGE = 60 * 60 * 24 * 180;

	function $(selector, root) { return (root || document).querySelector(selector); }
	function $all(selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); }

	// Menu
	function setupMenu() {
		var header = $(".ex-header");
		var toggle = $(".ex-menu-toggle");
		if (!header || !toggle) return;
		toggle.addEventListener("click", function () {
			var open = !header.classList.contains("is-menu-open");
			header.classList.toggle("is-menu-open", open);
			toggle.setAttribute("aria-expanded", String(open));
		});
		$all(".ex-sub-toggle").forEach(function (button) {
			button.addEventListener("click", function () {
				var item = button.closest(".ex-has-sub");
				var open = !item.classList.contains("is-open");
				item.classList.toggle("is-open", open);
				button.setAttribute("aria-expanded", String(open));
			});
		});
		document.addEventListener("keydown", function (event) {
			if (event.key !== "Escape") return;
			$all(".ex-has-sub.is-open").forEach(function (item) {
				item.classList.remove("is-open");
				var button = $(".ex-sub-toggle", item);
				if (button) button.setAttribute("aria-expanded", "false");
			});
			if (header.classList.contains("is-menu-open")) {
				header.classList.remove("is-menu-open");
				toggle.setAttribute("aria-expanded", "false");
				toggle.focus();
			}
		});
	}

	// Cookie choice: "essential" (optional rejected) or "optional" (optional accepted).
	function readChoice() {
		var match = document.cookie.match(new RegExp("(?:^|; )" + COOKIE + "=(essential|optional)"));
		return match ? match[1] : "";
	}
	function writeChoice(value) {
		var secure = window.location.protocol === "https:" ? "; Secure" : "";
		document.cookie = COOKIE + "=" + value + "; Max-Age=" + MAX_AGE + "; Path=/; SameSite=Lax" + secure;
		document.dispatchEvent(new CustomEvent("examic:cookie-choice", { detail: { choice: value } }));
	}
	window.examicCookieChoice = function () { return readChoice() === "optional"; };

	function setupCookies() {
		var banner = $("#ex-cookie-banner");
		var dialog = $("#ex-cookie-dialog");
		var optional = $("#ex-cookie-optional");
		var status = $("#ex-cookie-status");
		if (!banner) return;

		function sync(message) {
			var choice = readChoice();
			banner.hidden = Boolean(choice);
			if (optional) optional.checked = choice === "optional";
			if (status) status.textContent = message || (choice ? "Current choice: optional cookies " + (choice === "optional" ? "allowed." : "rejected.") : "No choice saved yet.");
			$all("[data-ex-cookie-current]").forEach(function (el) {
				el.textContent = choice ? (choice === "optional" ? "Optional cookies allowed" : "Optional cookies rejected") : "No choice saved yet";
			});
		}
		function choose(value) {
			writeChoice(value);
			sync("Saved: optional cookies " + (value === "optional" ? "allowed." : "rejected."));
		}
		function openSettings(event) {
			if (event) event.preventDefault();
			sync();
			if (dialog && typeof dialog.showModal === "function") dialog.showModal();
			else window.location.href = "/cookies#cookie-settings";
		}

		$all("[data-ex-cookie]").forEach(function (button) {
			button.addEventListener("click", function () {
				choose(button.getAttribute("data-ex-cookie"));
				if (dialog && dialog.open && button.closest("dialog")) dialog.close();
			});
		});
		$all("[data-ex-cookie-settings]").forEach(function (el) { el.addEventListener("click", openSettings); });
		var save = $("[data-ex-cookie-save]");
		if (save) save.addEventListener("click", function () {
			choose(optional && optional.checked ? "optional" : "essential");
			dialog.close();
		});
		sync();
		if (window.location.hash === "#cookie-settings") openSettings();
	}

	// Contact form
	function csrfToken() {
		return window.csrf_token || (window.frappe && window.frappe.csrf_token) || "";
	}
	function setupContact() {
		var form = $("#ex-contact-form");
		if (!form) return;
		var status = $("#ex-contact-status");
		var button = $("button[type=submit]", form);

		function say(text, ok) {
			status.textContent = text;
			status.classList.toggle("is-error", !ok);
			status.classList.toggle("is-ok", Boolean(ok));
		}
		form.addEventListener("submit", function (event) {
			event.preventDefault();
			if (!form.reportValidity()) return;
			var data = {};
			["name", "email", "enquiry_type", "message", "reference", "website"].forEach(function (key) {
				var field = form.elements[key];
				data[key] = field ? field.value.trim() : "";
			});
			button.disabled = true;
			say("Sending your message.", true);
			fetch("/api/method/aimaticlearning.lms_learning.contact.submit_enquiry", {
				method: "POST",
				credentials: "same-origin",
				headers: { Accept: "application/json", "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrfToken() },
				body: JSON.stringify(data)
			}).then(function (response) {
				return response.json().catch(function () { return {}; }).then(function (body) { return { ok: response.ok, status: response.status, body: body }; });
			}).then(function (result) {
				if (result.ok && result.body.message && result.body.message.ok) {
					form.reset();
					say("Thank you. Your message has been sent to hello@examic.study and we will reply by email.", true);
					return;
				}
				var text = result.status === 429
					? "Too many messages from this connection. Please wait an hour or email hello@examic.study."
					: serverMessage(result.body) || "We could not send your message. Please email hello@examic.study.";
				say(text, false);
			}).catch(function () {
				say("We could not send your message. Please email hello@examic.study.", false);
			}).then(function () { button.disabled = false; });
		});
	}
	function serverMessage(body) {
		try {
			var messages = JSON.parse(body._server_messages || "[]");
			if (messages.length) return JSON.parse(messages[0]).message;
		} catch (error) { return ""; }
		return "";
	}

	function start() { setupMenu(); setupCookies(); setupContact(); }
	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
	else start();
})();
