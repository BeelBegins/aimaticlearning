(function () {
	"use strict";

	// Mock sittings run on the stock LMS quiz page. Learners should see "mock exam"
	// wording and have an on-screen calculator, as in the real SQE1 sitting.
	const WORDS = [
		[/\bQuizzes\b/g, "Mock Exams"],
		[/\bquizzes\b/g, "mock exams"],
		[/\bQuiz\b/g, "Mock Exam"],
		[/\bquiz\b/g, "mock exam"],
	];
	const SKIP = "script, style, textarea, input, [contenteditable], .aimatic-calc";

	function isMockPage() {
		return document.body.classList.contains("aimatic-exam-sitting")
			|| /^\/lms\/quiz\/mock-/.test(window.location.pathname);
	}

	function relabel(root) {
		const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
		const nodes = [];
		while (walker.nextNode()) nodes.push(walker.currentNode);
		nodes.forEach(function (node) {
			const parent = node.parentElement;
			if (!parent || parent.closest(SKIP)) return;
			let text = node.nodeValue;
			if (!/quiz/i.test(text)) return;
			WORDS.forEach(function (pair) { text = text.replace(pair[0], pair[1]); });
			if (text !== node.nodeValue) node.nodeValue = text;
		});
	}

	// Immediate-execution calculator. No eval.
	const OPS = {
		"+": function (a, b) { return a + b; },
		"-": function (a, b) { return a - b; },
		"*": function (a, b) { return a * b; },
		"/": function (a, b) { return b === 0 ? NaN : a / b; },
	};
	const SYMBOL = { "+": "+", "-": "−", "*": "×", "/": "÷" };

	function createCalculator() {
		const state = { entry: "0", acc: null, op: null, fresh: true, error: false };
		const root = document.createElement("div");
		root.className = "aimatic-calc";
		root.hidden = true;
		root.setAttribute("role", "dialog");
		root.setAttribute("aria-label", "Calculator");
		root.tabIndex = -1;

		const head = document.createElement("div");
		head.className = "aimatic-calc-head";
		const title = document.createElement("span");
		title.textContent = "Calculator";
		const close = document.createElement("button");
		close.type = "button";
		close.className = "aimatic-calc-close";
		close.setAttribute("aria-label", "Close calculator");
		close.textContent = "×";
		head.append(title, close);

		const trail = document.createElement("div");
		trail.className = "aimatic-calc-trail";
		const screen = document.createElement("div");
		screen.className = "aimatic-calc-screen";
		screen.setAttribute("aria-live", "polite");

		const keys = document.createElement("div");
		keys.className = "aimatic-calc-keys";
		const layout = [
			["C", "clear"], ["⌫", "back"], ["%", "pct"], ["÷", "/"],
			["7", "7"], ["8", "8"], ["9", "9"], ["×", "*"],
			["4", "4"], ["5", "5"], ["6", "6"], ["−", "-"],
			["1", "1"], ["2", "2"], ["3", "3"], ["+", "+"],
			["±", "sign"], ["0", "0"], [".", "."], ["=", "="],
		];
		layout.forEach(function (item) {
			const button = document.createElement("button");
			button.type = "button";
			button.textContent = item[0];
			button.dataset.calcKey = item[1];
			if (OPS[item[1]] || item[1] === "=") button.className = "is-op";
			keys.append(button);
		});
		root.append(head, trail, screen, keys);

		function show() {
			screen.textContent = state.entry;
			trail.textContent = state.op ? format(state.acc) + " " + SYMBOL[state.op] : " ";
		}

		function format(value) {
			if (!isFinite(value)) return "Error";
			return String(parseFloat(value.toPrecision(12)));
		}

		function reset() {
			state.entry = "0"; state.acc = null; state.op = null; state.fresh = true; state.error = false;
		}

		function commit() {
			if (state.op === null) return;
			const result = OPS[state.op](state.acc, parseFloat(state.entry));
			state.entry = format(result);
			state.error = state.entry === "Error";
			state.acc = null; state.op = null; state.fresh = true;
		}

		function press(key) {
			if (state.error && key !== "clear") return;
			if (/^[0-9]$/.test(key)) {
				if (state.fresh) { state.entry = key; state.fresh = false; }
				else if (state.entry.replace(/[-.]/g, "").length < 14) {
					state.entry = state.entry === "0" ? key : state.entry + key;
				}
			} else if (key === ".") {
				if (state.fresh) { state.entry = "0."; state.fresh = false; }
				else if (state.entry.indexOf(".") === -1) state.entry += ".";
			} else if (OPS[key]) {
				if (state.op && !state.fresh) commit();
				if (state.error) return show();
				state.acc = parseFloat(state.entry);
				state.op = key;
				state.fresh = true;
			} else if (key === "=" || key === "Enter") {
				commit();
			} else if (key === "pct") {
				const value = parseFloat(state.entry);
				// 50 + 10% -> 10% of 50; otherwise plain value / 100.
				const next = state.op && state.acc !== null && (state.op === "+" || state.op === "-")
					? state.acc * value / 100 : value / 100;
				state.entry = format(next);
				state.fresh = true;
			} else if (key === "sign") {
				if (state.entry !== "0") {
					state.entry = state.entry.charAt(0) === "-" ? state.entry.slice(1) : "-" + state.entry;
				}
			} else if (key === "back") {
				if (!state.fresh) {
					state.entry = state.entry.length > 1 && state.entry !== "-0"
						? state.entry.slice(0, -1) : "0";
					if (state.entry === "-") state.entry = "0";
				}
			} else if (key === "clear") {
				reset();
			}
			show();
		}

		keys.addEventListener("click", function (event) {
			const button = event.target.closest("[data-calc-key]");
			if (button) press(button.dataset.calcKey);
		});
		root.addEventListener("keydown", function (event) {
			// Only while the calculator itself has focus, so answer keys are untouched.
			if (event.key === "Escape") { setOpen(false); return; }
			let key = event.key;
			if (key === "Backspace") key = "back";
			else if (key === "Delete" || key === "c" || key === "C") key = "clear";
			else if (key === "%") key = "pct";
			if (/^[0-9.]$/.test(key) || OPS[key] || key === "Enter" || key === "=" || key === "back" || key === "clear" || key === "pct") {
				if (event.target.closest("[data-calc-key]") && key === "Enter") return;
				event.preventDefault();
				press(key === "=" ? "=" : key);
			}
		});

		const toggle = document.createElement("button");
		toggle.type = "button";
		toggle.className = "aimatic-calc-toggle";
		toggle.textContent = "Calculator";
		toggle.setAttribute("aria-expanded", "false");

		function setOpen(open) {
			root.hidden = !open;
			toggle.setAttribute("aria-expanded", open ? "true" : "false");
			if (open) root.focus(); else toggle.focus();
		}
		toggle.addEventListener("click", function () { setOpen(root.hidden); });
		close.addEventListener("click", function () { setOpen(false); });

		show();
		return { root: root, toggle: toggle };
	}

	function ensureCalculator() {
		if (document.querySelector(".aimatic-calc-toggle")) return;
		const calc = createCalculator();
		document.body.append(calc.toggle, calc.root);
	}

	function apply() {
		if (!isMockPage()) return;
		relabel(document.body);
		if (/^\/lms\/quiz\//.test(window.location.pathname)) ensureCalculator();
	}

	function start() {
		if (window.AimaticLmsDom) {
			window.AimaticLmsDom.observe(apply).run();
		} else {
			apply();
		}
	}
	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
	else start();
})();
