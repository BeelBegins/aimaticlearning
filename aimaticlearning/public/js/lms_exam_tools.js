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
	const SKIP = "script, style, textarea, input, [contenteditable], .aimatic-calc, .aimatic-pearson";

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

	function isMockSitting() {
		return isMockPage() && /^\/lms\/quiz\//.test(window.location.pathname);
	}

	function buttonByLabel(pattern) {
		return Array.from(document.querySelectorAll("button")).find(function (button) {
			if (button.closest(".aimatic-pearson") || button.closest(".aimatic-style-choice")) return false;
			const text = (button.textContent || "").replace(/\s+/g, " ").trim();
			const aria = (button.getAttribute("aria-label") || "").replace(/\s+/g, " ").trim();
			return pattern.test(text) || pattern.test(aria);
		});
	}

	function questionCounter() {
		return Array.from(document.querySelectorAll(".text-sm.text-ink-gray-5")).find(function (node) {
			return /^Question\s+\d+\s+-/.test((node.textContent || "").trim());
		});
	}

	function currentNumber() {
		const counter = questionCounter();
		const match = counter && counter.textContent.trim().match(/^Question\s+(\d+)/);
		return match ? parseInt(match[1], 10) : 0;
	}

	function questionTotal() {
		const match = (document.body.textContent || "").match(/consists of\s+(\d+)\s+questions/i);
		if (match) return parseInt(match[1], 10);
		const session = quizSession();
		return session && session.questions ? session.questions.value.length : 0;
	}

	function quizSession() {
		const refs = window.__examicRefs || [];
		let questions = null;
		let at = -1;
		for (let i = refs.length - 1; i >= 0; i -= 1) {
			const value = refs[i] && refs[i].value;
			if (Array.isArray(value) && value.length && value[0] && value[0].question) {
				questions = refs[i];
				at = i;
				break;
			}
		}
		if (!questions) return null;
		const current = currentNumber();
		let active = null;
		let selected = null;
		for (let i = at; i >= 0 && i >= at - 8; i -= 1) {
			const ref = refs[i];
			if (!ref) continue;
			if (!active && typeof ref.value === "number" && current && ref.value === current) active = ref;
			if (
				!selected &&
				Array.isArray(ref.value) &&
				ref.value.length >= 4 &&
				ref.value.length <= 12 &&
				ref.value.every(function (item) { return item === 0 || item === 1; })
			) selected = ref;
		}
		return { activeQuestion: active, questions: questions, selectedOptions: selected };
	}

	function flagKey() {
		return "examic-review:" + window.location.pathname;
	}

	function loadFlags() {
		try {
			const rows = JSON.parse(sessionStorage.getItem(flagKey()) || "[]");
			return new Set(Array.isArray(rows) ? rows : []);
		} catch (error) {
			return new Set();
		}
	}

	function saveFlags(flags) {
		sessionStorage.setItem(flagKey(), JSON.stringify(Array.from(flags)));
	}

	function reviewLabel() {
		return Array.from(document.querySelectorAll("label")).find(function (label) {
			return /Mark for review/.test((label.textContent || "").replace(/\s+/g, " "));
		});
	}

	let flagLockUntil = 0;

	function syncCurrentFlag(flags) {
		if (Date.now() < flagLockUntil) return flags;
		const number = currentNumber();
		const input = reviewLabel() && reviewLabel().querySelector("input");
		if (!number || !input) return flags;
		if (input.checked) flags.add(number);
		else flags.delete(number);
		saveFlags(flags);
		return flags;
	}

	function savedAnswerIds() {
		const session = quizSession();
		const ids = new Set();
		if (!session) return ids;
		const known = new Set(session.questions.value.map(function (row) { return row.question; }));
		for (let i = 0; i < localStorage.length; i += 1) {
			const key = localStorage.key(i);
			let rows;
			try { rows = JSON.parse(localStorage.getItem(key)); } catch (error) { continue; }
			if (!Array.isArray(rows)) continue;
			rows.forEach(function (row) {
				if (!row || !known.has(row.question_name)) return;
				if (Array.isArray(row.answer) && row.answer.some(Boolean)) ids.add(row.question_name);
			});
		}
		return ids;
	}

	function answeredNumbers() {
		const session = quizSession();
		const answered = new Set();
		if (!session) return answered;
		const ids = savedAnswerIds();
		session.questions.value.forEach(function (row, index) {
			if (ids.has(row.question)) answered.add(index + 1);
		});
		return answered;
	}

	function pagerButton(target) {
		return Array.from(document.querySelectorAll("button")).find(function (button) {
			if (button.closest(".aimatic-pearson") || button.closest(".aimatic-style-choice")) return false;
			if ((button.textContent || "").replace(/\s+/g, " ").trim() !== String(target)) return false;
			return /\brounded-full\b/.test(button.className || "");
		});
	}

	let navToken = 0;

	function wait(ms) {
		return new Promise(function (resolve) { window.setTimeout(resolve, ms); });
	}

	async function waitForNumber(match, ms) {
		for (let tick = 0; tick < ms / 40; tick += 1) {
			if (match(currentNumber())) return true;
			await wait(40);
		}
		return match(currentNumber());
	}

	// Native Previous/Next/pager buttons run LMS switchQuestion, which saves the answer being
	// left. A far jump takes one native step so that save happens, then sets the active
	// question directly (one render instead of one per question). Selection is zeroed first
	// so the question we stepped through cannot leak its answer onto the target. If the LMS
	// refs cannot be found it falls back to stepping one question at a time.
	async function goToQuestion(target) {
		const total = questionTotal();
		if (target < 1 || (total && target > total)) return;
		const token = ++navToken;
		const nativeToward = function (from) {
			return pagerButton(target) || buttonByLabel(target > from ? /^Next question$/i : /^Previous question$/i);
		};
		const first = currentNumber();
		if (!first || first === target) return;
		const near = pagerButton(target) || (Math.abs(target - first) === 1 ? nativeToward(first) : null);
		if (near) {
			near.click();
			return;
		}
		let session = quizSession();
		if (session && session.activeQuestion && session.selectedOptions) {
			const step = nativeToward(first);
			if (step) {
				step.click();
				await waitForNumber(function (n) { return n !== first; }, 1000);
			}
			if (token !== navToken) return;
			if (currentNumber() !== target) {
				session = quizSession();
				if (session && session.activeQuestion && session.selectedOptions) {
					session.selectedOptions.value = session.selectedOptions.value.map(function () { return 0; });
					session.activeQuestion.value = target;
					if (await waitForNumber(function (n) { return n === target; }, 1500)) return;
				}
			} else {
				return;
			}
		}
		for (let guard = 0; guard < 120 && token === navToken; guard += 1) {
			const current = currentNumber();
			if (!current || current === target) return;
			const click = nativeToward(current);
			if (!click) return;
			click.click();
			if (!(await waitForNumber(function (n) { return n !== current; }, 1000))) return;
		}
	}

	function timerText() {
		const nodes = Array.from(document.querySelectorAll("span, div"));
		const label = nodes.find(function (node) {
			return (node.childNodes.length === 1) && /^\s*Time\s*:?\s*$/i.test(node.textContent || "");
		});
		const value = label && label.parentElement && label.parentElement.querySelector(".font-semibold");
		return value ? value.textContent.trim() : "";
	}

	function examTitle() {
		const heading = document.querySelector("h1");
		const text = heading && heading.textContent.trim();
		return text || "Mock exam";
	}

	const FLAG_ICON = '<svg class="aimatic-pearson-flag-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M5 21V4m0 0h11l-2 4 2 4H5" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>';

	// The DOM observer re-runs apply() on every childList change, so painting must be
	// idempotent: write only what changed or the shell repaints forever and rows detach.
	function setText(node, value) {
		if (node.textContent !== value) node.textContent = value;
	}

	function reviewScreen() {
		return document.querySelector(".aimatic-pearson-review-screen");
	}

	function openReview(filter) {
		const screen = reviewScreen();
		if (!screen) return;
		screen.hidden = false;
		paintReview(filter || "all");
	}

	function closeReview() {
		const screen = reviewScreen();
		if (screen) screen.hidden = true;
	}

	function ensureShell() {
		let shell = document.querySelector(".aimatic-pearson");
		if (shell && !shell.querySelector(".aimatic-pearson-rows")) {
			shell.remove();
			shell = null;
		}
		if (shell) return shell;
		shell = document.createElement("div");
		shell.className = "aimatic-pearson";
		shell.innerHTML = [
			'<header class="aimatic-pearson-bar">',
			'<div class="aimatic-pearson-left">',
			'<div class="aimatic-pearson-title"></div>',
			'<div class="aimatic-pearson-links"><span class="aimatic-pearson-calc-slot"></span>',
			'<a class="aimatic-pearson-exit" href="/learning-mock-exam">Exit to Mock Exams</a></div>',
			"</div>",
			'<div class="aimatic-pearson-tools">',
			'<span class="aimatic-pearson-time"></span>',
			'<span class="aimatic-pearson-progress"></span>',
			'<button type="button" class="aimatic-pearson-review" aria-pressed="false">',
			FLAG_ICON,
			"<span><u>F</u>lag for Review</span></button>",
			"</div></header>",
			'<footer class="aimatic-pearson-footer">',
			'<button type="button" class="aimatic-pearson-open-review" data-pearson="review"><u>R</u>eview Screen</button>',
			'<button type="button" data-pearson="prev">&larr; <u>P</u>revious</button>',
			'<button type="button" data-pearson="next"><u>N</u>ext &rarr;</button>',
			"</footer>",
			'<div class="aimatic-pearson-review-screen" hidden>',
			'<header class="aimatic-pearson-bar aimatic-pearson-review-bar">',
			'<div class="aimatic-pearson-left"><div class="aimatic-pearson-title"></div>',
			'<div class="aimatic-pearson-links"><a class="aimatic-pearson-exit" href="/learning-mock-exam">Exit to Mock Exams</a></div></div>',
			'<div class="aimatic-pearson-tools"><span class="aimatic-pearson-time"></span></div>',
			"</header>",
			'<div class="aimatic-pearson-review-body">',
			"<h2>Item Review Screen</h2>",
			'<div class="aimatic-pearson-section"><span>Section</span><span class="aimatic-pearson-count"></span></div>',
			'<div class="aimatic-pearson-rows"></div>',
			"</div>",
			'<footer class="aimatic-pearson-footer aimatic-pearson-review-footer">',
			'<button type="button" data-pearson="end">End Test</button>',
			'<div class="aimatic-pearson-filters">',
			'<button type="button" data-filter="all">Review <u>A</u>ll</button>',
			'<button type="button" data-filter="incomplete">Review <u>I</u>ncomplete</button>',
			'<button type="button" data-filter="flagged">Review <u>F</u>lagged</button>',
			"</div></footer></div>",
		].join("");
		document.body.append(shell);
		shell.querySelector(".aimatic-pearson-review").addEventListener("click", function () {
			const flags = loadFlags();
			const number = currentNumber();
			const want = !flags.has(number);
			const label = reviewLabel();
			const input = label && label.querySelector("input");
			if (label && input && input.checked !== want) label.click();
			if (want) flags.add(number);
			else flags.delete(number);
			flagLockUntil = Date.now() + 400;
			saveFlags(flags);
			paintShell();
		});
		shell.querySelector('[data-pearson="prev"]').addEventListener("click", function () {
			goToQuestion(currentNumber() - 1);
		});
		shell.querySelector('[data-pearson="next"]').addEventListener("click", function () {
			const total = questionTotal();
			// As in the real player, Next on the last question opens the Item Review Screen.
			if (total && currentNumber() >= total) openReview("all");
			else goToQuestion(currentNumber() + 1);
		});
		shell.querySelector('[data-pearson="review"]').addEventListener("click", function () { openReview("all"); });
		shell.querySelector('[data-pearson="end"]').addEventListener("click", endTest);
		shell.querySelectorAll("[data-filter]").forEach(function (button) {
			button.addEventListener("click", function () { paintReview(button.dataset.filter); });
		});
		return shell;
	}

	function paintReview(filter) {
		const shell = document.querySelector(".aimatic-pearson");
		if (!shell) return;
		const total = questionTotal();
		const flags = syncCurrentFlag(loadFlags());
		const answered = answeredNumbers();
		const rows = shell.querySelector(".aimatic-pearson-rows");
		shell.querySelectorAll("[data-filter]").forEach(function (button) {
			button.classList.toggle("is-active", button.dataset.filter === filter);
		});
		const signature = [filter, total, Array.from(flags).sort().join(","), Array.from(answered).sort().join(",")].join("|");
		if (rows.dataset.signature === signature) return;
		rows.dataset.signature = signature;
		rows.replaceChildren();
		let incomplete = 0;
		for (let number = 1; number <= total; number += 1) {
			const isFlagged = flags.has(number);
			const isAnswered = answered.has(number);
			if (!isAnswered) incomplete += 1;
			if (filter === "flagged" && !isFlagged) continue;
			if (filter === "incomplete" && isAnswered) continue;
			const row = document.createElement("button");
			row.type = "button";
			row.className = "aimatic-pearson-row";
			if (isFlagged) row.classList.add("is-flagged");
			row.innerHTML = FLAG_ICON + '<span class="aimatic-pearson-qname">Question ' + number + "</span>" +
				'<span class="aimatic-pearson-status ' + (isAnswered ? "is-answered" : "is-incomplete") + '">' +
				(isAnswered ? "Answered" : "Incomplete") + "</span>";
			row.addEventListener("click", function () {
				closeReview();
				goToQuestion(number);
			});
			rows.append(row);
		}
		setText(shell.querySelector(".aimatic-pearson-count"), "(" + incomplete + " Unseen/Incomplete)");
		if (!rows.childElementCount) {
			const empty = document.createElement("p");
			empty.className = "aimatic-pearson-empty";
			empty.textContent = filter === "flagged" ? "No questions flagged." : "No incomplete questions.";
			rows.append(empty);
		}
	}

	function endTest() {
		const submit = buttonByLabel(/^(Submit|End session & submit)$/);
		if (submit) submit.click();
	}

	function styleKey() {
		return "examic-mock-style:" + window.location.pathname;
	}

	function clearPearson() {
		document.body.classList.remove("aimatic-pearson-sitting");
		[
			".aimatic-pearson-native-actions",
			".aimatic-pearson-past-attempts",
			".aimatic-pearson-native-time",
			".aimatic-pearson-native-review",
			".aimatic-pearson-native-counter",
		].forEach(function (selector) {
			document.querySelectorAll(selector).forEach(function (node) {
				node.classList.remove(selector.slice(1));
			});
		});
		closeReview();
		const shell = document.querySelector(".aimatic-pearson");
		if (shell) shell.hidden = true;
	}

	let startingWithChoice = false;

	function isStartButton(button) {
		if (!button || button.closest(".aimatic-pearson") || button.closest(".aimatic-style-choice")) {
			return false;
		}
		const text = (button.textContent || "").replace(/\s+/g, " ").trim();
		return /^(Start|Start the Quiz|Start new session|Start mock exam)$/i.test(text);
	}

	function showStyleModal(onPick) {
		if (document.querySelector(".aimatic-style-choice")) return;
		const modal = document.createElement("div");
		modal.className = "aimatic-style-choice";
		modal.innerHTML = [
			'<div class="aimatic-style-choice-card" role="dialog" aria-modal="true" aria-label="Mock exam style">',
			"<p>How do you want to sit this mock?</p>",
			'<button type="button" data-style="normal">Normal</button>',
			'<button type="button" data-style="pearson">Pearson style</button>',
			"</div>",
		].join("");
		modal.addEventListener("click", function (event) {
			const button = event.target.closest("[data-style]");
			if (!button) return;
			sessionStorage.setItem(styleKey(), button.dataset.style);
			modal.remove();
			onPick(button.dataset.style);
		});
		document.body.append(modal);
	}

	function ensureStyleChoice() {
		const chosen = sessionStorage.getItem(styleKey());
		const existing = document.querySelector(".aimatic-style-choice");
		if (chosen) {
			if (existing) existing.remove();
			return chosen;
		}
		clearPearson();
		// Mid-attempt refresh with no saved choice: ask before painting Pearson chrome.
		if (questionCounter() && !existing) {
			showStyleModal(function () { apply(); });
		}
		return "";
	}

	function bindStartGate() {
		if (bindStartGate.bound) return;
		bindStartGate.bound = true;
		document.addEventListener("click", function (event) {
			if (!isMockSitting() || startingWithChoice) return;
			const button = event.target.closest("button");
			// Ask on every Start: the stored choice only keeps a mid-attempt refresh in the same style.
			if (!isStartButton(button)) return;
			// A new attempt forgets the previous choice, or ensureStyleChoice() would close the modal.
			sessionStorage.removeItem(styleKey());
			event.preventDefault();
			event.stopPropagation();
			event.stopImmediatePropagation();
			showStyleModal(function () {
				startingWithChoice = true;
				try {
					button.click();
				} finally {
					window.setTimeout(function () {
						startingWithChoice = false;
						apply();
					}, 0);
				}
			});
		}, true);
	}

	function hideNativeChrome() {
		const mark = reviewLabel();
		if (mark) {
			const wrap = mark.closest("div.inline-flex.flex-col")
				|| mark.closest("div.inline-flex")
				|| mark;
			wrap.classList.add("aimatic-pearson-native-review");
			mark.classList.add("aimatic-pearson-native-review");
		}
		document.querySelectorAll("label").forEach(function (label) {
			if (/Mark for review/i.test((label.textContent || "").replace(/\s+/g, " "))) {
				const wrap = label.closest("div.inline-flex.flex-col")
					|| label.closest("div.inline-flex")
					|| label;
				wrap.classList.add("aimatic-pearson-native-review");
			}
		});
		const counter = questionCounter();
		if (counter) counter.classList.add("aimatic-pearson-native-counter");
		const nativePrev = buttonByLabel(/^Previous question$/i);
		const nativeNext = buttonByLabel(/^Next question$/i);
		const nativeSubmit = buttonByLabel(/^(Submit|End session & submit)$/i);
		let nativeActions = null;
		if (nativeSubmit && (nativePrev || nativeNext)) {
			let node = nativeSubmit.parentElement;
			while (node && node !== document.body) {
				if (node.contains(nativePrev || nativeNext)) {
					nativeActions = node;
					break;
				}
				node = node.parentElement;
			}
		}
		if (!nativeActions) {
			const anchor = nativeSubmit || nativePrev || nativeNext;
			nativeActions = anchor && anchor.closest("div.flex");
		}
		if (nativeActions) nativeActions.classList.add("aimatic-pearson-native-actions");
		else if (nativeSubmit) nativeSubmit.classList.add("aimatic-pearson-native-actions");
	}

	function paintShell() {
		if (!questionCounter()) {
			const existing = document.querySelector(".aimatic-pearson");
			if (existing) existing.hidden = true;
			document.body.classList.remove("aimatic-pearson-sitting");
			return;
		}
		document.body.classList.add("aimatic-pearson-sitting");
		const shell = ensureShell();
		shell.hidden = false;
		const number = currentNumber();
		const total = questionTotal();
		const flags = syncCurrentFlag(loadFlags());
		shell.querySelectorAll(".aimatic-pearson-title").forEach(function (node) { setText(node, examTitle()); });
		setText(shell.querySelector(".aimatic-pearson-progress"), total
			? (number + " of " + total)
			: String(number));
		const clock = timerText();
		shell.querySelectorAll(".aimatic-pearson-time").forEach(function (node) {
			setText(node, clock ? (/time remaining/i.test(clock) ? clock : ("Time Remaining " + clock)) : "");
		});
		const nativeClock = Array.from(document.querySelectorAll("span")).find(function (node) {
			return /^\s*Time\s*:?\s*$/i.test(node.textContent || "") && node.childNodes.length === 1;
		});
		const nativeClockHost = nativeClock && nativeClock.closest(".flex.flex-col");
		if (nativeClockHost) nativeClockHost.classList.add("aimatic-pearson-native-time");
		const review = shell.querySelector(".aimatic-pearson-review");
		const flagged = flags.has(number);
		review.classList.toggle("is-on", flagged);
		review.setAttribute("aria-pressed", flagged ? "true" : "false");
		const prev = shell.querySelector('[data-pearson="prev"]');
		const next = shell.querySelector('[data-pearson="next"]');
		prev.hidden = number <= 1;
		// Lesson chrome used to stamp display:none on any "Previous"/"Next" button.
		prev.style.removeProperty("display");
		next.style.removeProperty("display");
		hideNativeChrome();
		hidePastAttempts();
		const calc = document.querySelector(".aimatic-calc-toggle");
		const calcSlot = shell.querySelector(".aimatic-pearson-calc-slot");
		if (calc && calcSlot && calc.parentElement !== calcSlot) calcSlot.append(calc);
		const screen = reviewScreen();
		if (screen && !screen.hidden) {
			const active = shell.querySelector("[data-filter].is-active");
			paintReview(active ? active.dataset.filter : "all");
		}
	}

	function hidePastAttempts() {
		document.querySelectorAll("div.mt-10").forEach(function (node) {
			const text = node.textContent || "";
			if (/Score out of|No Quiz submissions found/.test(text)) {
				node.classList.add("aimatic-pearson-past-attempts");
			}
		});
	}

	function apply() {
		if (!isMockPage()) return;
		relabel(document.body);
		if (!isMockSitting()) return;
		bindStartGate();
		ensureCalculator();
		const style = ensureStyleChoice();
		if (style !== "pearson") {
			clearPearson();
			return;
		}
		hidePastAttempts();
		paintShell();
	}

	function start() {
		bindStartGate();
		if (window.AimaticLmsDom) {
			window.AimaticLmsDom.observe(apply).run();
		} else {
			apply();
		}
	}
	if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
	else start();
})();
