(function () {
	"use strict";

	var storageKey = "examic-frappe-theme";
	var legacyStorageKey = "examic-soft-theme";
	var legacyThemeAliases = { "blue-red": "blue" };

	/* Single source of truth for labels and colours. Add a theme here and the
	 * picker, persistence, and every CSS consumer will use it automatically. */
	var themeDefinitions = {
		frappe: {
			label: "Black & White",
			tokens: {
				ink: "var(--ink-gray-9, #171717)", muted: "var(--ink-gray-7, #5b656e)",
				surface: "var(--surface-white, #fff)", subtle: "var(--surface-gray-2, #f4f5f6)",
				subtleStrong: "var(--surface-gray-3, #e9ebed)", line: "var(--outline-gray-2, #e2e6eb)",
				primary: "var(--ink-gray-9, #171717)", primaryHover: "var(--ink-gray-8, #2c3338)",
				cardEnd: "var(--ink-gray-8, #2c3338)", secondary: "var(--ink-gray-7, #5b656e)",
				danger: "var(--red-500, #e24c4b)", dangerSoft: "var(--surface-red-2, #fff5f5)",
				shadow: "0 14px 40px var(--black-overlay-100, rgba(0, 0, 0, 0.08))"
			}
		},
		blue: {
			label: "Blue",
			tokens: {
				ink: "#0B1F41", muted: "#526179", surface: "#FFFFFF", subtle: "#F3F6FA",
				subtleStrong: "#E3EAF3", line: "#D6DEE9", primary: "#0B1F41",
				primaryHover: "#08152D", cardEnd: "#0B1F41", secondary: "#163A70",
				danger: "var(--red-500, #e24c4b)", dangerSoft: "#FFF5F5",
				shadow: "0 14px 40px rgba(11, 31, 65, 0.14)"
			}
		}
	};
	var allowedThemes = Object.keys(themeDefinitions);

	function isLmsHost() {
		var host = window.location.hostname;
		return host === "lms.aimatic.tech" || host === "examic.study" || host === "www.examic.study";
	}

	function polishLogin() {
		if (!/\/login\/?$/.test(window.location.pathname)) return;
		document.querySelectorAll(".page-card-head h4").forEach(function (heading) {
			if (/create a\s+examic/i.test(heading.textContent)) {
				heading.textContent = "Create your student account";
			}
		});
		document.querySelectorAll(".page-card-head .app-logo").forEach(function (logo) {
			logo.alt = "Examic Study";
			logo.src = "/assets/aimaticlearning/images/examic-study-mark.svg?v=20260902-6";
		});
	}

	function selectedTheme() {
		var saved = window.localStorage.getItem(storageKey);
		if (legacyThemeAliases[saved]) saved = legacyThemeAliases[saved];
		if (allowedThemes.indexOf(saved) !== -1) return saved;
		/* Never carry a custom sage/sky/lilac choice into the new palette. */
		window.localStorage.removeItem(legacyStorageKey);
		return "frappe";
	}

	function applyTheme(theme) {
		if (legacyThemeAliases[theme]) theme = legacyThemeAliases[theme];
		if (allowedThemes.indexOf(theme) === -1) theme = "frappe";
		var tokens = themeDefinitions[theme].tokens;
		document.documentElement.setAttribute("data-theme", "light");
		document.documentElement.setAttribute("data-examic-theme", theme);
		Object.keys(tokens).forEach(function (name) {
			document.documentElement.style.setProperty("--examic-theme-" + name.replace(/[A-Z]/g, function (letter) { return "-" + letter.toLowerCase(); }), tokens[name]);
		});
		window.localStorage.setItem(storageKey, theme);
	}

	function addPicker() {
		if (!/^\/lms(?:\/|$)/.test(window.location.pathname)) return;
		var rail = document.querySelector(".aimatic-lms-chapter-rail");
		var sidebar = document.querySelector(".bg-surface-sidebar");
		var existing = (rail && rail.querySelector(".aimatic-theme-picker")) ||
			(sidebar && sidebar.querySelector(".aimatic-theme-picker"));
		if (existing) return;
		if (!rail && !sidebar) return;
		var picker = document.createElement("label");
		picker.className = "aimatic-theme-picker";
		var options = allowedThemes.map(function (theme) {
			return "<option value=\"" + theme + "\">" + themeDefinitions[theme].label + "</option>";
		}).join("");
		picker.innerHTML = "<span>Theme</span><select aria-label=\"Choose a colour theme\">" + options + "</select>";
		var select = picker.querySelector("select");
		select.value = selectedTheme();
		select.addEventListener("change", function () { applyTheme(select.value); });
		if (rail) {
			rail.querySelector("[class~='bg-surface-gray-1']")?.appendChild(picker) || rail.prepend(picker);
		} else {
			var sidebarBody = sidebar.querySelector(".overflow-y-auto") || sidebar;
			sidebarBody.prepend(picker);
		}
	}

	function boot() {
		if (!isLmsHost()) return;
		applyTheme(selectedTheme());
		addPicker();
		polishLogin();
	}

	function apply() {
		if (!isLmsHost()) return;
		applyTheme(selectedTheme());
		addPicker();
		polishLogin();
	}

	const observer = window.AimaticLmsDom && window.AimaticLmsDom.observe(apply);
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", function () {
			boot();
			if (observer) observer.run();
		});
	} else {
		boot();
		if (observer) observer.run();
	}
})();
