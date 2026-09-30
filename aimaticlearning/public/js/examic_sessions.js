(function () {
	"use strict";

	const COURSE_PATH = /^\/lms\/courses\/business-law-practice-blp(?:\/|$)/;
	const resumeQuizTitles = new Set();
	const nativeRemoveItem = Storage.prototype.removeItem;
	const nativeSendBeacon = navigator.sendBeacon && navigator.sendBeacon.bind(navigator);
	const nativeFetch = window.fetch.bind(window);

	function onCourse() {
		return COURSE_PATH.test(window.location.pathname);
	}

	function lessonCourse() {
		const match = window.location.pathname.match(/^\/lms\/courses\/([^/]+)/);
		return match ? match[1] : "";
	}


	function safeJson(value, fallback) {
		try { return JSON.parse(value) || fallback; } catch (error) { return fallback; }
	}

	Storage.prototype.removeItem = function (key) {
		if (this === window.localStorage && resumeQuizTitles.has(key)) {
			resumeQuizTitles.delete(key);
			return;
		}
		return nativeRemoveItem.call(this, key);
	};

	if (nativeSendBeacon) {
		navigator.sendBeacon = function (url, data) {
			const target = String(url || "");
			if (target.includes("lms.lms.doctype.lms_quiz.lms_quiz.submit_quiz") && onCourse()) {
				const timed = document.querySelector('[data-examic-quiz-timed="1"]');
				if (!timed) return true;
			}
			return nativeSendBeacon(url, data);
		};
	}

	window.fetch = function (input, options) {
		const requestUrl = typeof input === "string" ? input : (input && input.url) || "";
		const request = nativeFetch(input, options);
		if (!String(requestUrl).includes("aimaticlearning.lms_learning.api.review_flashcard")) return request;
		return request.then(function (response) {
			if (response.ok) {
				const payload = safeJson((options && options.body) || "{}", {});
				updateFlashcardProgress(payload.rating);
			}
			return response;
		});
	};

	function makeButton(label, className) {
		const button = document.createElement("button");
		button.type = "button";
		button.className = className;
		button.textContent = label;
		return button;
	}

	function quizSavedAnswers(title) {
		const rows = safeJson(localStorage.getItem(title), []);
		return Array.isArray(rows) ? rows.filter(function (row) {
			return row && Array.isArray(row.answer) && row.answer.some(Boolean);
		}).length : 0;
	}

	function dedupeQuizChrome() {
		// Vue remounts the question wrapper while moving through a quiz. Keep
		// one active toolbar across those changing parents, not one per wrapper.
		const toolbars = Array.from(document.querySelectorAll(
			".examic-quiz-toolbar:not(.examic-quiz-saved-notice)"
		));
		toolbars.slice(1).forEach(function (toolbar) { toolbar.remove(); });
		document.querySelectorAll(".examic-quiz-session-controls").forEach(function (controls) {
			const card = controls.parentElement;
			if (!card) return;
			card.querySelectorAll(":scope > .examic-quiz-session-controls").forEach(function (node, nodeIndex) {
				if (nodeIndex > 0) node.remove();
			});
		});
	}

	function decorateQuizStart(startButton) {
		const card = startButton.closest("div.border.text-center");
		if (!card) return;
		const titleNode = card.querySelector(".text-lg-semibold");
		const title = titleNode && titleNode.textContent.trim();
		if (!title) return;
		if (card.querySelector(":scope > .examic-quiz-session-controls")) {
			card.dataset.examicQuizReady = "1";
			return;
		}
		if (card.dataset.examicQuizReady === "1") return;
		card.dataset.examicQuizReady = "1";
		card.classList.add("examic-quiz-start");
		const label = startButton.querySelector("span") || startButton;
		label.textContent = "Start new session";

		const saved = quizSavedAnswers(title);
		const controls = document.createElement("div");
		controls.className = "examic-quiz-session-controls";
		const note = document.createElement("p");
		note.textContent = saved
			? saved + " answered question" + (saved === 1 ? " is" : "s are") + " saved on this device."
			: "Your answers are saved on this device until you submit or abandon the session.";
		controls.append(note);

		if (saved) {
			const resume = makeButton("Resume saved session", "examic-session-button examic-session-primary");
			resume.addEventListener("click", function () {
				resumeQuizTitles.add(title);
				startButton.click();
			});
			const abandon = makeButton("Abandon saved session", "examic-session-link");
			abandon.addEventListener("click", function () {
				if (!window.confirm("Abandon this saved session? Your unsubmitted answers will be removed.")) return;
				nativeRemoveItem.call(localStorage, title);
				controls.remove();
				card.dataset.examicQuizReady = "";
				decorateQuizStart(startButton);
			});
			controls.append(resume, abandon);
		}
		card.append(controls);
	}

	function exitQuizWithoutReload(timed) {
		// Answers already live in localStorage under the quiz title.
		if (timed) {
			const submit = Array.from(document.querySelectorAll("button span")).find(function (span) {
				return /^(Submit|End session & submit)$/.test(span.textContent.trim());
			});
			if (submit) {
				submit.closest("button").click();
				return;
			}
		}
		const notice = document.createElement("div");
		notice.className = "examic-quiz-toolbar examic-quiz-saved-notice";
		notice.setAttribute("role", "status");
		notice.innerHTML = "<span>Progress saved on this device. Leave this lesson when you want — resume later from Start.</span>";
		const existing = document.querySelector(".examic-quiz-toolbar");
		if (existing && existing.parentElement) {
			existing.replaceWith(notice);
		}
	}

	function decorateQuizActivity() {
		if (!onCourse()) return;
		dedupeQuizChrome();
		document.querySelectorAll("button span").forEach(function (span) {
			if (/^(Start|Start the Quiz)$/.test(span.textContent.trim())) decorateQuizStart(span.closest("button"));
			if (span.textContent.trim() === "Submit") span.textContent = "End session & submit";
			if (span.textContent.trim() === "Try Again") span.textContent = "Start another session";
		});

		const counters = Array.from(document.querySelectorAll(".text-sm.text-ink-gray-5")).filter(function (counter) {
			return /^Question\s+\d+\s+-/.test(counter.textContent.trim());
		});
		if (!counters.length) return;

		const questionCard = counters[0].closest("div.border.rounded-lg");
		const host = questionCard && questionCard.parentElement;
		if (!host) return;

		// One toolbar for the whole quiz host — never re-insert on each question mutation.
		if (
			host.dataset.examicQuizToolbar === "1" ||
			host.querySelector(".examic-quiz-toolbar") ||
			document.querySelector(".examic-quiz-toolbar:not(.examic-quiz-saved-notice)")
		) {
			dedupeQuizChrome();
			return;
		}

		const instructions = host.parentElement && host.parentElement.textContent;
		const timed = /complete all the questions in\s+\d+\s+minutes/i.test(instructions || "");
		host.dataset.examicQuizTimed = timed ? "1" : "0";
		host.dataset.examicQuizToolbar = "1";
		const toolbar = document.createElement("div");
		toolbar.className = "examic-quiz-toolbar";
		const copy = document.createElement("span");
		copy.textContent = timed ? "Timed attempt in progress" : "Session in progress · answers save on this device";
		const end = makeButton(timed ? "End & submit attempt" : "End & save for later", "examic-session-link");
		end.addEventListener("click", function () {
			const message = timed
				? "End this timed attempt now? Your current answers will be submitted for scoring."
				: "Keep your answers on this device and pause this session? You can resume from Start without reloading.";
			if (!window.confirm(message)) return;
			exitQuizWithoutReload(timed);
		});
		toolbar.append(copy, end);
		host.insertBefore(toolbar, host.firstChild);

		document.querySelectorAll(".text-lg-semibold").forEach(function (heading) {
			if (heading.textContent.trim() !== "Quiz Summary") return;
			const card = heading.closest("div.border.rounded-lg");
			if (!card || card.querySelector(".examic-result-guidance")) return;
			const guidance = document.createElement("p");
			guidance.className = "examic-result-guidance";
			guidance.textContent = "Review the explanations, note any weak topics, then revisit the lesson or start another focused session.";
			card.append(guidance);
		});
	}

	function flashcardKey(host) {
		return "examic:flashcards:" + (host.dataset.learningModule || "course") + ":" + (host.dataset.courseChapter || "chapter") + ":" + (host.dataset.ratingFilter || "all");
	}

	function getFlashcardState(host) {
		return safeJson(localStorage.getItem(flashcardKey(host)), null);
	}

	function setFlashcardState(host, state) {
		localStorage.setItem(flashcardKey(host), JSON.stringify(state));
	}

	function showFlashcard(study, index) {
		const cards = Array.from(study.querySelectorAll("[data-ach-card]"));
		cards.forEach(function (card, cardIndex) {
			card.hidden = cardIndex !== index;
			const front = card.querySelector(".ach-card-front");
			const back = card.querySelector(".ach-card-back");
			const flip = card.querySelector("[data-ach-flash-card]");
			const label = card.querySelector(".ach-flip-label");
			if (front) front.hidden = false;
			if (back) back.hidden = true;
			if (flip) {
				flip.classList.remove("is-back");
				flip.setAttribute("aria-pressed", "false");
				flip.setAttribute("aria-label", "Flashcard. Select to reveal the answer.");
			}
			if (label) label.textContent = "Select to reveal";
		});
		study.querySelectorAll("[data-ach-rating]").forEach(function (button) { button.disabled = true; });
	}

	function abandonFlashcardSession(host) {
		nativeRemoveItem.call(localStorage, flashcardKey(host));
		const rating = host.dataset.ratingFilter && host.dataset.ratingFilter !== "all"
			? host.dataset.ratingFilter
			: "";
		if (window.AimaticFlashcards && typeof window.AimaticFlashcards.reload === "function") {
			window.AimaticFlashcards.reload(host, rating);
			return;
		}
		window.location.reload();
	}

	function renderFlashcardSummary(host, state, complete) {
		const intro = host.querySelector(".examic-flash-intro");
		const study = host.querySelector("[data-ach-flash-study]");
		if (!intro || !study) return;
		study.hidden = true;
		intro.hidden = false;
		intro.innerHTML = '<p class="examic-session-kicker">' + (complete ? "Session complete" : "Session paused") + '</p>' +
			'<h3>' + state.index + ' of ' + state.total + ' cards reviewed</h3>' +
			'<div class="examic-flash-results"><span><strong>' + state.counts.hard + '</strong>Hard</span><span><strong>' + state.counts.good + '</strong>Good</span><span><strong>' + state.counts.easy + '</strong>Easy</span></div>' +
			'<p>' + (complete ? "Use Revise Hard for the cards that need another look, or open your weak-area board." : "Your place and recall ratings are saved on this device.") + '</p>';
		const actions = document.createElement("div");
		actions.className = "examic-session-actions";
		const resume = makeButton(complete ? "Study deck again" : "Resume session", "examic-session-button examic-session-primary");
		resume.addEventListener("click", function () {
			if (complete) state = { index: 0, total: state.total, counts: { hard: 0, good: 0, easy: 0 }, startedAt: Date.now() };
			setFlashcardState(host, state);
			intro.hidden = true;
			study.hidden = false;
			showFlashcard(study, Math.min(state.index, state.total - 1));
		});
		if (complete) {
			["hard", "good", "easy"].forEach(function (rating) {
				if (!state.counts[rating]) return;
				const revise = makeButton("Revise " + rating[0].toUpperCase() + rating.slice(1), "examic-session-button");
				revise.addEventListener("click", function () {
					nativeRemoveItem.call(localStorage, flashcardKey(host));
					if (window.AimaticFlashcards && window.AimaticFlashcards.reload) {
						window.AimaticFlashcards.reload(host, rating);
					} else {
						window.location.hash = "revise-" + rating;
						window.location.reload();
					}
				});
				actions.append(revise);
			});
			const weak = document.createElement("a");
			weak.className = "examic-session-link";
			weak.href = "/learning-revision" + (lessonCourse() ? "?course=" + encodeURIComponent(lessonCourse()) : "");
			weak.textContent = "Open weak areas";
			actions.append(weak);
		}
		const abandon = makeButton("Abandon session", "examic-session-link");
		abandon.addEventListener("click", function () {
			if (!window.confirm("Abandon this flashcard session and remove its saved progress?")) return;
			abandonFlashcardSession(host);
		});
		actions.append(resume, abandon);
		intro.append(actions);
	}

	function decorateFlashcardDeck(host) {
		const study = host.querySelector("[data-ach-flash-study]");
		if (!study || host.dataset.examicSessionReady) return;
		const cards = Array.from(study.querySelectorAll("[data-ach-card]"));
		if (!cards.length) return;
		host.dataset.examicSessionReady = "1";
		const intro = document.createElement("section");
		intro.className = "examic-flash-intro";
		study.before(intro);
		let state = getFlashcardState(host);
		if (!state || state.total !== cards.length) state = { index: 0, total: cards.length, counts: { hard: 0, good: 0, easy: 0 }, startedAt: null };
		study.hidden = true;
		intro.innerHTML = '<p class="examic-session-kicker">Flashcard session</p><h3>' + cards.length + ' cards ready</h3><p>Reveal each answer, then rate your recall as hard, good or easy. You can pause and resume safely on this device.</p>';
		const actions = document.createElement("div");
		actions.className = "examic-session-actions";
		const start = makeButton(state.index ? "Resume at card " + (state.index + 1) : "Start deck", "examic-session-button examic-session-primary");
		start.addEventListener("click", function () {
			if (!state.startedAt) state.startedAt = Date.now();
			setFlashcardState(host, state);
			intro.hidden = true;
			study.hidden = false;
			showFlashcard(study, Math.min(state.index, state.total - 1));
		});
		if (state.index) {
			const abandon = makeButton("Abandon saved session", "examic-session-link");
			abandon.addEventListener("click", function () {
				if (!window.confirm("Abandon this saved flashcard session?")) return;
				abandonFlashcardSession(host);
			});
			actions.append(start, abandon);
		} else actions.append(start);
		intro.append(actions);

		const toolbar = document.createElement("div");
		toolbar.className = "examic-flash-toolbar";
		const progress = document.createElement("span");
		progress.textContent = "Session in progress";
		const end = makeButton("End & save for later", "examic-session-link");
		end.addEventListener("click", function () {
			state = getFlashcardState(host) || state;
			renderFlashcardSummary(host, state, false);
		});
		toolbar.append(progress, end);
		study.prepend(toolbar);
	}

	function updateFlashcardProgress(rating) {
		const host = Array.from(document.querySelectorAll("[data-aimatic-flashcard-deck]")).find(function (item) {
			const study = item.querySelector("[data-ach-flash-study]");
			return study && !study.hidden;
		});
		if (!host || !["hard", "good", "easy"].includes(rating)) return;
		const cards = host.querySelectorAll("[data-ach-card]");
		const state = getFlashcardState(host) || { index: 0, total: cards.length, counts: { hard: 0, good: 0, easy: 0 }, startedAt: Date.now() };
		state.counts[rating] += 1;
		state.index = Math.min(state.index + 1, state.total);
		setFlashcardState(host, state);
		if (state.index >= state.total) setTimeout(function () { renderFlashcardSummary(host, state, true); }, 60);
	}

	function polish() {
		decorateQuizActivity();
		document.querySelectorAll("[data-aimatic-flashcard-deck]").forEach(decorateFlashcardDeck);
	}

	const observer = window.AimaticLmsDom && window.AimaticLmsDom.observe(polish);
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", function () {
			if (observer) observer.run();
			else polish();
		});
	} else if (observer) {
		observer.run();
	} else {
		polish();
	}
})();
