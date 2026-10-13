(function () {
	"use strict";

	/* Single source of truth: the public website's palette, defined in
	 * public/css/sqe_frappe_theme.css. The student portal has no theme choice
	 * of its own; it always renders these colours. Keep this object's values in
	 * sync with sqe_frappe_theme.css if the brand palette ever changes. */
	var EXAMIC_THEME = {
		ink: "#0E1B3D", muted: "#4A5878", surface: "#FFFFFF", subtle: "#F5F7FB",
		subtleStrong: "#EAEFFA", line: "#DDE3F0", primary: "#00247D",
		primaryHover: "#1A3A94", cardEnd: "#001A5C", secondary: "#CF142B",
		danger: "#CF142B", dangerSoft: "#FDECEE",
		shadow: "0 14px 40px rgba(0, 36, 125, 0.12)"
	};

	/* The portal is colour-locked, so the only theme control left is upstream
	 * LMS's own light/dark/system toggle, which the forced data-theme below
	 * makes non-functional on student routes. Hide it by its rendered label
	 * rather than leave a dead control visible. Staff/Administrator views never
	 * carry aimatic-lms-student, so their toggle keeps working. Keep this label
	 * in sync with apps/lms/frontend/src/components/Sidebar/UserDropdown.vue
	 * ("Toggle Theme"); do not edit that upstream file. */
	var HIDDEN_DROPDOWN_ITEM_LABEL = "Toggle Theme";

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
			logo.src = "/assets/aimaticlearning/images/examic-study-mark-uk.svg?v=20261005-uk";
		});
	}

	function applyTheme() {
		document.documentElement.setAttribute("data-theme", "light");
		document.documentElement.setAttribute("data-examic-theme", "uk");
		Object.keys(EXAMIC_THEME).forEach(function (name) {
			document.documentElement.style.setProperty("--examic-theme-" + name.replace(/[A-Z]/g, function (letter) { return "-" + letter.toLowerCase(); }), EXAMIC_THEME[name]);
		});
	}

	/* Scoped to [data-slot="item"], the attribute frappe-ui's Menu component
	 * puts on every dropdown row, so this never scans the whole document. */
	function hideUpstreamThemeToggle() {
		if (!document.body.classList.contains("aimatic-lms-student")) return;
		document.querySelectorAll('[data-slot="item"]:not([data-aimatic-theme-hidden])').forEach(function (item) {
			if (item.textContent.trim() !== HIDDEN_DROPDOWN_ITEM_LABEL) return;
			item.style.display = "none";
			item.setAttribute("data-aimatic-theme-hidden", "true");
		});
	}

	function boot() {
		if (!isLmsHost()) return;
		applyTheme();
		hideUpstreamThemeToggle();
		polishLogin();
	}

	function apply() {
		if (!isLmsHost()) return;
		applyTheme();
		hideUpstreamThemeToggle();
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
