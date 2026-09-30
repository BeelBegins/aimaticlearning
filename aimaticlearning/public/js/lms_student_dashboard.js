(function () {
	"use strict";

	const API = "/api/method/aimaticlearning.lms_learning.api.get_student_dashboard";
	const TABS = [
		["practice", "Practice questions"],
		["module", "Module tests"],
		["mock", "Simulated exam"],
	];

	function isLmsHome() {
		return /^\/lms\/?$/.test(window.location.pathname);
	}

	function isStandalone() {
		return /^\/learning-dashboard\/?$/.test(window.location.pathname);
	}

	function text(node, value) {
		node.textContent = value == null ? "" : String(value);
	}

	function el(tag, className, value) {
		const node = document.createElement(tag);
		if (className) node.className = className;
		if (value !== undefined) text(node, value);
		return node;
	}

	function hostRoot() {
		return document.getElementById("aimatic-student-dashboard");
	}

	function findHomeRoot() {
		return document.querySelector("main .w-full.p-5") || document.querySelector("#app .w-full.p-5");
	}

	function mountOnLmsHome() {
		if (!isLmsHome() || !document.body.classList.contains("aimatic-lms-student")) return hostRoot();
		if (hostRoot()) {
			document.body.classList.add("aimatic-student-dash-mounted");
			return hostRoot();
		}
		const home = findHomeRoot();
		if (!home) return null;
		const host = el("div", "aimatic-student-dash");
		host.id = "aimatic-student-dashboard";
		home.appendChild(host);
		document.body.classList.add("aimatic-student-dash-mounted");
		return host;
	}

	function formatDate(value) {
		if (!value) return "";
		const day = new Date(value + (String(value).length === 10 ? "T00:00:00" : ""));
		if (Number.isNaN(day.getTime())) return String(value);
		return day.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
	}

	function paceLabel(pace) {
		if (pace === "ahead") return "Ahead of plan";
		if (pace === "on_track") return "On plan";
		if (pace === "behind") return "Behind plan";
		return "Not started";
	}

	function changeCell(value) {
		if (value == null || value === "") return "";
		const number = Number(value);
		if (!Number.isFinite(number)) return "";
		const prefix = number > 0 ? "+" : "";
		return prefix + number.toFixed(1);
	}

	function ringSvg(segments) {
		const ns = "http://www.w3.org/2000/svg";
		const svg = document.createElementNS(ns, "svg");
		svg.setAttribute("viewBox", "0 0 120 120");
		svg.setAttribute("role", "img");
		svg.setAttribute("aria-label", "Study mix");
		const cx = 60;
		const cy = 60;
		const radii = [48, 36, 24];
		segments.forEach(function (segment, index) {
			const r = radii[index];
			const c = 2 * Math.PI * r;
			const pct = Math.max(0, Math.min(100, Number(segment.percent) || 0));
			const bg = document.createElementNS(ns, "circle");
			bg.setAttribute("cx", String(cx));
			bg.setAttribute("cy", String(cy));
			bg.setAttribute("r", String(r));
			bg.setAttribute("fill", "none");
			bg.setAttribute("stroke", "var(--dash-line)");
			bg.setAttribute("stroke-width", "8");
			svg.appendChild(bg);
			const fg = document.createElementNS(ns, "circle");
			fg.setAttribute("cx", String(cx));
			fg.setAttribute("cy", String(cy));
			fg.setAttribute("r", String(r));
			fg.setAttribute("fill", "none");
			fg.setAttribute("stroke", "var(--dash-accent)");
			fg.setAttribute("stroke-width", "8");
			fg.setAttribute("stroke-linecap", "round");
			fg.setAttribute("stroke-dasharray", c.toFixed(2));
			fg.setAttribute("stroke-dashoffset", (c * (1 - pct / 100)).toFixed(2));
			fg.setAttribute("transform", "rotate(-90 60 60)");
			fg.setAttribute("opacity", String(1 - index * 0.22));
			svg.appendChild(fg);
		});
		return svg;
	}

	function chartSvg(progress) {
		const ns = "http://www.w3.org/2000/svg";
		const svg = document.createElementNS(ns, "svg");
		svg.setAttribute("viewBox", "0 0 640 220");
		svg.setAttribute("role", "img");
		svg.setAttribute("aria-label", "Coverage over time versus the default study plan");
		const actual = progress.actual || [];
		const planned = progress.planned || [];
		const maxVal = Math.max(progress.target || 0, 1, ...actual.map(function (p) { return p.value; }), ...planned.map(function (p) { return p.value; }));
		const all = planned.length ? planned : actual;
		function x(index, total) {
			if (total <= 1) return 36;
			return 36 + (index / (total - 1)) * 580;
		}
		function y(value) {
			return 196 - (Number(value) / maxVal) * 168;
		}
		function polyline(points, dashed) {
			const line = document.createElementNS(ns, "polyline");
			line.setAttribute("fill", "none");
			line.setAttribute("stroke", dashed ? "var(--dash-muted)" : "var(--dash-accent)");
			line.setAttribute("stroke-width", dashed ? "2" : "2.6");
			if (dashed) line.setAttribute("stroke-dasharray", "6 6");
			line.setAttribute("points", points.map(function (pt, index) {
				return x(index, points.length).toFixed(1) + "," + y(pt.value).toFixed(1);
			}).join(" "));
			svg.appendChild(line);
		}
		[0, 0.25, 0.5, 0.75, 1].forEach(function (frac) {
			const grid = document.createElementNS(ns, "line");
			grid.setAttribute("x1", "36");
			grid.setAttribute("x2", "616");
			grid.setAttribute("y1", String(y(maxVal * frac)));
			grid.setAttribute("y2", String(y(maxVal * frac)));
			grid.setAttribute("stroke", "var(--dash-line)");
			grid.setAttribute("stroke-width", "1");
			svg.appendChild(grid);
		});
		if (planned.length) polyline(planned, true);
		if (actual.length) polyline(actual, false);
		if (all.length) {
			const first = document.createElementNS(ns, "text");
			first.setAttribute("x", "36");
			first.setAttribute("y", "214");
			first.setAttribute("fill", "var(--dash-muted)");
			first.setAttribute("font-size", "11");
			first.textContent = formatDate(all[0].date);
			svg.appendChild(first);
			const last = document.createElementNS(ns, "text");
			last.setAttribute("x", "616");
			last.setAttribute("y", "214");
			last.setAttribute("fill", "var(--dash-muted)");
			last.setAttribute("font-size", "11");
			last.setAttribute("text-anchor", "end");
			last.textContent = formatDate(all[all.length - 1].date);
			svg.appendChild(last);
		}
		return svg;
	}

	function mixRow(label, bucket) {
		const row = el("div", "dash-mix-row");
		const title = el("strong");
		title.append(el("span", "", label), el("span", "", (bucket.done || 0) + " / " + (bucket.total || 0)));
		row.append(title);
		const hours = bucket.hours != null ? " · " + bucket.hours + "h timed" : "";
		row.append(el("span", "", (bucket.percent || 0) + "% coverage" + hours));
		const bar = el("div", "dash-bar");
		const fill = el("i");
		fill.style.width = Math.max(0, Math.min(100, Number(bucket.percent) || 0)) + "%";
		bar.append(fill);
		row.append(bar);
		return row;
	}

	function renderScoreboard(host, board, emptyText) {
		host.replaceChildren();
		if (!board || !(board.groups || []).length) {
			host.append(el("p", "dash-lead", emptyText || "Nothing recorded yet."));
			return;
		}
		const wrap = el("div", "dash-table-wrap");
		const table = el("table", "dash-table");
		const head = document.createElement("thead");
		const headRow = document.createElement("tr");
		["Subject", "Correct", "Attempted", "% Correct", "Change"].forEach(function (label) {
			headRow.append(el("th", "", label));
		});
		head.append(headRow);
		table.append(head);
		const body = document.createElement("tbody");
		board.groups.forEach(function (group) {
			const groupRow = document.createElement("tr");
			groupRow.className = "dash-group";
			const cell = document.createElement("td");
			cell.colSpan = 5;
			text(cell, group.title);
			groupRow.append(cell);
			body.append(groupRow);
			(group.rows || []).forEach(function (row) {
				const tr = document.createElement("tr");
				const name = document.createElement("td");
				const link = el("a", "", row.subject);
				link.href = row.href || "/lms/courses";
				name.append(link);
				tr.append(name);
				tr.append(el("td", "", String(row.correct || 0)));
				tr.append(el("td", "", String(row.attempted || 0)));
				tr.append(el("td", "", (row.attempted ? Number(row.percent || 0).toFixed(1) : "")));
				const change = el("td", "dash-change", changeCell(row.change));
				if (row.change > 0) change.classList.add("is-up");
				if (row.change < 0) change.classList.add("is-down");
				tr.append(change);
				body.append(tr);
			});
		});
		const totals = board.totals || {};
		const totalRow = document.createElement("tr");
		totalRow.append(el("td", "", "Total"));
		totalRow.append(el("td", "", String(totals.correct || 0)));
		totalRow.append(el("td", "", String(totals.attempted || 0)));
		totalRow.append(el("td", "", totals.attempted ? Number(totals.percent || 0).toFixed(1) : ""));
		totalRow.append(el("td", "", changeCell(totals.change)));
		body.append(totalRow);
		table.append(body);
		wrap.append(table);
		host.append(wrap);
	}

	function render(host, data) {
		host.classList.add("aimatic-student-dash");
		host.replaceChildren();
		if (isStandalone()) {
			const nav = el("nav", "dash-nav");
			nav.setAttribute("aria-label", "Study");
			[
				["/learning-dashboard", "Dashboard", true],
				["/lms/courses", "Subjects", false],
				["/learning-revision", "Revision", false],
				["/learning-mock-exam", "Mock exams", false],
			].forEach(function (item) {
				const link = el("a", "", item[1]);
				link.href = item[0];
				if (item[2]) link.setAttribute("aria-current", "page");
				nav.append(link);
			});
			host.append(nav);
		}

		if (data.empty_reason) {
			const empty = el("div", "dash-empty");
			empty.append(el("h2", "", "No course data yet"));
			empty.append(el("p", "dash-lead", (data.next_action && data.next_action.detail) || "Enrol on a subject to see coverage."));
			const go = el("a", "dash-btn dash-btn-primary", "Browse subjects");
			go.href = "/lms/courses";
			empty.append(go);
			host.append(empty);
			return;
		}

		const learner = data.learner || {};
		const sitting = data.sitting || {};
		const mix = data.mix || {};
		const progress = data.progress || {};
		const next = data.next_action || {};

		const hero = el("section", "dash-hero");
		const hello = el("div", "dash-hello");
		hello.append(el("p", "dash-kicker", "Examic Study · SQE1"));
		hello.append(el("h1", "", "Hello, " + (learner.first_name || "there")));
		hello.append(el("p", "dash-lead", "Notes, chapter questions and flashcards, in one place."));
		const meta = el("div", "dash-meta");
		if (sitting.days_left != null) meta.append(el("span", "dash-chip", sitting.days_left + " days to January 2027"));
		const pace = el("span", "dash-chip", paceLabel(progress.pace));
		pace.classList.add("is-" + (progress.pace || "unstarted"));
		meta.append(pace);
		hello.append(meta);
		if (next.href && next.title) {
			const cont = el("a", "dash-continue");
			cont.href = next.href;
			cont.append(el("span", "", "Continue"));
			cont.append(el("strong", "", next.title));
			hello.append(cont);
		}
		hero.append(hello);
		host.append(hero);

		const grid = el("section", "dash-grid");
		const mixCard = el("article", "dash-card");
		mixCard.append(el("h2", "", "Study mix"));
		const mixWrap = el("div", "dash-mix");
		const ring = el("div", "dash-ring");
		ring.append(ringSvg([mix.notes || {}, mix.mcq || {}, mix.review || {}]));
		mixWrap.append(ring);
		const rows = el("div", "dash-mix-rows");
		rows.append(mixRow("Notes", mix.notes || {}));
		rows.append(mixRow("Multiple choice", mix.mcq || {}));
		rows.append(mixRow("Review", mix.review || {}));
		mixWrap.append(rows);
		mixCard.append(mixWrap);
		grid.append(mixCard);

		const recentCard = el("article", "dash-card");
		recentCard.append(el("h2", "", "Recent activity"));
		const list = el("div", "dash-recent");
		const recent = data.recent || [];
		const kinds = { notes: "Notes", mcq: "MCQ", flashcard: "Cards", module: "Test", mock: "Mock" };
		if (!recent.length) {
			list.append(el("div", "dash-recent-empty", "No lessons opened yet."));
		} else {
			recent.forEach(function (item) {
				const node = el(item.href ? "a" : "div");
				if (item.href) node.href = item.href;
				node.append(el("span", "dash-kind", kinds[item.kind] || "Study"));
				const body = el("div");
				body.append(el("strong", "", item.title || "Lesson"));
				if (item.subject) body.append(el("em", "", item.subject));
				node.append(body);
				node.append(el("time", "", formatDate(item.date)));
				list.append(node);
			});
		}
		recentCard.append(list);
		grid.append(recentCard);
		host.append(grid);

		const chartCard = el("article", "dash-card dash-chart");
		chartCard.append(el("h2", "", "Coverage over time"));
		const legend = el("div", "dash-legend");
		const actualKey = el("span");
		actualKey.append(el("i"), document.createTextNode("Your coverage"));
		const planKey = el("span");
		planKey.append(el("i", "is-plan"), document.createTextNode("Plan to January 2027"));
		legend.replaceChildren(actualKey, planKey);
		chartCard.append(legend);
		chartCard.append(chartSvg(progress));
		host.append(chartCard);

		const boardCard = el("article", "dash-card");
		boardCard.append(el("h2", "", "Subject scores"));
		const tabs = el("div", "dash-tabs");
		tabs.setAttribute("role", "tablist");
		const panel = el("div");
		TABS.forEach(function (tab, index) {
			const button = el("button", "", tab[1]);
			button.type = "button";
			button.setAttribute("role", "tab");
			button.setAttribute("aria-selected", String(index === 0));
			button.dataset.tab = tab[0];
			tabs.append(button);
		});
		tabs.addEventListener("click", function (event) {
			const button = event.target.closest("button[data-tab]");
			if (!button) return;
			tabs.querySelectorAll("button").forEach(function (other) {
				other.setAttribute("aria-selected", String(other === button));
			});
			renderScoreboard(panel, (data.scoreboard || {})[button.dataset.tab], {
				practice: "No chapter questions yet.",
				module: "No module test yet.",
				mock: "No completed exam sitting yet.",
			}[button.dataset.tab]);
		});
		boardCard.append(tabs, panel);
		renderScoreboard(panel, (data.scoreboard || {}).practice, "No chapter questions yet.");
		host.append(boardCard);

		const recs = el("article", "dash-card");
		recs.append(el("h2", "", "What to do this week"));
		const ul = el("ul", "dash-recs");
		(data.recommendations || []).forEach(function (line) {
			ul.append(el("li", "", line));
		});
		recs.append(ul);
		host.append(recs);

		const subjects = data.subjects || [];
		if (subjects.length) {
			const subjectWrap = el("div", "dash-subjects");
			subjects.forEach(function (subject) {
				const card = el("a", "dash-subject");
				card.href = subject.continue_href || subject.href;
				card.append(el("small", "", subject.pathway || "SQE1"));
				card.append(el("strong", "", subject.title));
				const bar = el("div", "dash-bar");
				const fill = el("i");
				fill.style.width = Math.max(0, Math.min(100, Number(subject.progress) || 0)) + "%";
				bar.append(fill);
				card.append(bar);
				card.append(el("span", "", (subject.progress || 0) + "% lesson progress"));
				subjectWrap.append(card);
			});
			host.append(subjectWrap);
		}
	}

	function showError(host, message) {
		host.classList.add("aimatic-student-dash");
		const box = el("div", "dash-error");
		box.append(el("strong", "", message || "Dashboard could not be loaded."));
		const retry = el("button", "dash-btn", "Retry");
		retry.type = "button";
		retry.addEventListener("click", function () { load(host); });
		box.append(retry);
		host.replaceChildren(box);
	}

	function load(host) {
		if (!host) return;
		const quiet = Boolean(host.querySelector(".dash-hello, .dash-empty"));
		const requestId = String(Date.now());
		host.dataset.dashRequest = requestId;
		host.classList.add("aimatic-student-dash");
		if (!quiet) host.replaceChildren(el("div", "dash-loading", "Loading your dashboard…"));
		const controller = new AbortController();
		const timer = window.setTimeout(function () { controller.abort(); }, 14000);
		fetch(API + "?_=" + requestId, {
			credentials: "same-origin",
			cache: "no-store",
			headers: { Accept: "application/json" },
			signal: controller.signal,
		})
			.then(function (response) {
				if (!response.ok) {
					const error = new Error("HTTP " + response.status);
					error.status = response.status;
					throw error;
				}
				return response.json();
			})
			.then(function (payload) {
				if (host.dataset.dashRequest !== requestId) return;
				render(host, payload.message || {});
			})
			.catch(function (error) {
				if (host.dataset.dashRequest !== requestId) return;
				if (quiet && host.querySelector(".dash-hello, .dash-empty")) return;
				let message = "Dashboard could not be loaded. Try again.";
				if (error.name === "AbortError") message = "Dashboard is taking too long to respond.";
				else if (error.status === 401 || error.status === 403) message = "Sign in to see your dashboard.";
				showError(host, message);
			})
			.finally(function () { window.clearTimeout(timer); });
	}

	let lastPath = "";

	function syncDashboard() {
		const path = window.location.pathname;
		const active = isLmsHome() || isStandalone();
		if (!active) {
			const existing = hostRoot();
			if (existing) delete existing.dataset.dashFresh;
			lastPath = path;
			return;
		}
		const host = isStandalone() ? hostRoot() : mountOnLmsHome();
		if (!host) return;
		const openedAgain = lastPath !== path || host.dataset.dashFresh !== "1";
		lastPath = path;
		if (!openedAgain) return;
		host.dataset.dashFresh = "1";
		load(host);
	}

	function refreshDashboard() {
		if (!isLmsHome() && !isStandalone()) return;
		const host = isStandalone() ? hostRoot() : mountOnLmsHome();
		if (!host) return;
		load(host);
	}

	const observer = window.AimaticLmsDom && window.AimaticLmsDom.observe(syncDashboard);
	document.addEventListener("visibilitychange", function () {
		if (document.visibilityState === "visible") refreshDashboard();
	});
	window.addEventListener("pageshow", refreshDashboard);
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", function () {
			syncDashboard();
			if (observer) observer.run();
		});
	} else {
		syncDashboard();
		if (observer) observer.run();
	}
})();
