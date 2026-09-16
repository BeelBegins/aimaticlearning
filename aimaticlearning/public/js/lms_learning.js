(function () {
	"use strict";

	// The LMS Vue shell (_lms.html, in Frappe LMS core) emits no <link rel="canonical">
	// or og:url tag at all, and this app is reachable on three live hostnames
	// (lms.aimatic.tech, examic.study, www.examic.study) serving identical content -
	// without this, search engines see the same page three times with no signal for
	// which URL is authoritative. examic.study is the public brand, so it is canonical.
	// Core template can't be edited here, so the tag is inserted client-side instead.
	var SEO_CANONICAL_HOST = "https://examic.study";

	function ensureCanonicalTags() {
		var path = window.location.pathname.replace(/\/+$/, "") || "/";
		var canonicalUrl = SEO_CANONICAL_HOST + path;

		var linkEl = document.head.querySelector('link[rel="canonical"]');
		if (!linkEl) {
			linkEl = document.createElement("link");
			linkEl.setAttribute("rel", "canonical");
			document.head.appendChild(linkEl);
		}
		linkEl.setAttribute("href", canonicalUrl);

		var ogUrlEl = document.head.querySelector('meta[property="og:url"]');
		if (!ogUrlEl) {
			ogUrlEl = document.createElement("meta");
			ogUrlEl.setAttribute("property", "og:url");
			document.head.appendChild(ogUrlEl);
		}
		ogUrlEl.setAttribute("content", canonicalUrl);
	}

	ensureCanonicalTags();

	function isLmsRoute() {
		return /^\/lms(?:\/|$)/.test(window.location.pathname);
	}

	function currentLessonContext() {
		const course = window.location.pathname.match(/^\/lms\/courses\/([^/]+)\/learn\/(\d+)-(\d+)/);
		if (!course) return null;
		return { course: course[1], chapter: Number(course[2]), lesson: Number(course[3]) };
	}

	function findLessonAside() {
		return document.querySelector(".aimatic-lms-chapter-rail") || Array.from(document.querySelectorAll("aside")).find(function (node) {
			return node.querySelector("ul") && node.querySelector("a, button");
		});
	}

	function lessonHeadingText() {
		const heading = document.querySelector(".aimatic-lms-lesson-main h1, main h1, h1");
		return heading ? heading.textContent.trim() : "";
	}

	function liveMcqContext() {
		const counter = Array.from(document.querySelectorAll(".text-sm.text-ink-gray-5, .text-sm")).find(function (node) {
			return /^Question\s+\d+\s+-/.test((node.textContent || "").trim());
		});
		if (!counter) return null;
		const card = counter.closest("div.border.rounded-lg") || counter.closest("div.border");
		if (!card) return null;
		const match = (counter.textContent || "").match(/^Question\s+(\d+)/);
		const questionEl = card.querySelector(".text-ink-gray-9.font-semibold, .font-semibold");
		const options = [];
		const selected = [];
		card.querySelectorAll("label").forEach(function (label) {
			const optionNode = label.querySelector("span.ms-2, span.flex-1, .text-ink-gray-9");
			const value = ((optionNode && optionNode.innerText) || "").replace(/\s+/g, " ").trim();
			if (!value || /^mark for review$/i.test(value)) return;
			options.push(value);
			const input = label.querySelector("input[type=radio], input[type=checkbox]");
			if (input && input.checked) selected.push(value);
		});
		if (!((questionEl && questionEl.innerText.trim()) || options.length)) return null;
		let quizTitle = "";
		document.querySelectorAll(".text-lg-semibold").forEach(function (node) {
			const value = (node.textContent || "").trim();
			if (value && value !== "Quiz Summary") quizTitle = value;
		});
		return {
			question_index: match ? Number(match[1]) : null,
			question: questionEl ? questionEl.innerText.trim() : "",
			options: options.slice(0, 6),
			selected_options: selected.slice(0, 6),
			quiz_title: quizTitle,
		};
	}

	function appendStudyBuddyMessage(host, kind, text, sourceLabel) {
		host.hidden = false;
		const message = document.createElement("section");
		message.className = "aimatic-study-buddy-message aimatic-study-buddy-message-" + kind;
		const label = document.createElement("strong");
		label.textContent = kind === "user" ? "You" : "Study Buddy";
		const body = document.createElement("p");
		body.textContent = text;
		message.append(label, body);
		if (sourceLabel) {
			const source = document.createElement("small");
			source.textContent = "Source: " + sourceLabel;
			message.append(source);
		}
		host.append(message);
		host.scrollTop = host.scrollHeight;
	}

	function setStudyBuddyOpen(dock, open) {
		const panel = dock.querySelector("[data-study-buddy-panel]");
		const toggle = dock.querySelector("[data-study-buddy-toggle]");
		if (!panel || !toggle) return;
		panel.hidden = !open;
		toggle.setAttribute("aria-expanded", String(open));
		dock.classList.toggle("is-open", open);
		if (open) {
			const input = panel.querySelector("textarea");
			if (input) input.focus();
		}
	}

	function refreshStudyBuddyTopic(card) {
		const topic = card.querySelector("[data-study-buddy-topic]");
		const hint = card.querySelector("[data-study-buddy-hint]");
		if (!topic) return;
		const mcq = liveMcqContext();
		if (mcq && mcq.question) {
			topic.textContent = mcq.question.length > 90 ? mcq.question.slice(0, 87) + "…" : mcq.question;
			if (hint) hint.textContent = "Live MCQ context is included with your question.";
			return;
		}
		topic.textContent = lessonHeadingText() || "This lesson";
		if (hint) hint.textContent = "Lesson context is selected automatically.";
	}

	function wireStudyBuddy(dock) {
		const card = dock.querySelector("[data-study-buddy]");
		if (!card) return;
		refreshStudyBuddyTopic(card);
		if (card.dataset.studyBuddyReady) return;
		card.dataset.studyBuddyReady = "1";
		card.dataset.studyBuddyHistory = "[]";
		const input = card.querySelector("textarea");
		const form = card.querySelector("form");
		const submit = form.querySelector("button[type=submit]");
		const status = card.querySelector("[data-study-buddy-status]");
		const transcript = card.querySelector("[data-study-buddy-transcript]");
		const toggle = dock.querySelector("[data-study-buddy-toggle]");
		const closer = dock.querySelector("[data-study-buddy-close]");
		toggle.addEventListener("click", function () {
			setStudyBuddyOpen(dock, dock.querySelector("[data-study-buddy-panel]").hidden);
		});
		if (closer) closer.addEventListener("click", function () { setStudyBuddyOpen(dock, false); });
		document.addEventListener("keydown", function (event) {
			if (event.key === "Escape") setStudyBuddyOpen(dock, false);
		});
		card.querySelectorAll("[data-study-buddy-prompt]").forEach(function (button) {
			button.addEventListener("click", function () {
				input.value = button.dataset.studyBuddyPrompt;
				input.focus();
			});
		});
		form.addEventListener("submit", function (event) {
			event.preventDefault();
			const question = input.value.trim();
			const context = currentLessonContext();
			if (!question) {
				input.focus();
				return;
			}
			if (!context) {
				status.textContent = "Open a lesson before asking Study Buddy.";
				return;
			}
			let history = [];
			try { history = JSON.parse(card.dataset.studyBuddyHistory || "[]"); } catch (_) {}
			appendStudyBuddyMessage(transcript, "user", question);
			input.value = "";
			submit.disabled = true;
			status.textContent = "Checking the approved material for this lesson…";
			const mcq = liveMcqContext();
			fetch("/api/method/aimaticlearning.lms_learning.study_buddy.ask_study_buddy", {
				method: "POST",
				credentials: "same-origin",
				headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.csrf_token || "" },
				body: JSON.stringify({
					course: context.course,
					chapter: context.chapter,
					lesson: context.lesson,
					question: question,
					history: JSON.stringify(history),
					attempt_context: mcq ? JSON.stringify(mcq) : "",
				}),
			})
				.then(function (response) {
					if (!response.ok) throw new Error("Study Buddy is temporarily unavailable.");
					return response.json();
				})
				.then(function (payload) {
					const result = payload.message || {};
					if (!result.answer) throw new Error("Study Buddy could not complete that answer.");
					appendStudyBuddyMessage(transcript, "assistant", result.answer, result.source && result.source.label);
					history.push({ role: "user", content: question }, { role: "assistant", content: result.answer });
					card.dataset.studyBuddyHistory = JSON.stringify(history.slice(-6));
					status.textContent = result.notice || "Source-grounded response for the selected lesson.";
				})
				.catch(function (error) {
					status.textContent = error.message || "Study Buddy is temporarily unavailable. Please try again.";
				})
				.finally(function () { submit.disabled = false; });
		});
	}

	function addStudyBuddyDock() {
		if (!currentLessonContext()) {
			const leftover = document.querySelector(".aimatic-study-buddy-dock");
			if (leftover) leftover.remove();
			return;
		}
		let dock = document.querySelector(".aimatic-study-buddy-dock");
		if (dock) {
			refreshStudyBuddyTopic(dock.querySelector("[data-study-buddy]"));
			return;
		}
		dock = document.createElement("div");
		dock.className = "aimatic-study-buddy-dock";
		dock.innerHTML =
			'<button type="button" class="aimatic-study-buddy-fab" data-study-buddy-toggle aria-expanded="false" aria-controls="aimatic-study-buddy-panel">Study Buddy</button>' +
			'<section id="aimatic-study-buddy-panel" class="aimatic-lms-ai-card aimatic-study-buddy" data-study-buddy data-study-buddy-panel hidden>' +
				'<div class="aimatic-lms-ai-kicker"><span class="aimatic-lms-ai-spark">✦</span> Study Buddy AI <b>Source-grounded beta</b>' +
					'<button type="button" class="aimatic-study-buddy-close" data-study-buddy-close aria-label="Close Study Buddy">×</button></div>' +
				'<div class="aimatic-lms-ai-context"><span>Grounded in approved material</span><strong data-study-buddy-topic>This lesson</strong><small data-study-buddy-hint>Lesson context is selected automatically.</small></div>' +
				'<h2>Ask about this lesson.</h2>' +
				'<p>Designed to explain, test and focus revision using the selected lesson—not generic prompts or copied text.</p>' +
				'<div class="aimatic-study-buddy-transcript" data-study-buddy-transcript aria-live="polite" hidden></div>' +
				'<div class="aimatic-study-buddy-prompts" aria-label="Suggested questions">' +
					'<button type="button" data-study-buddy-prompt="Explain the key rule in simple terms.">Explain the key rule</button>' +
					'<button type="button" data-study-buddy-prompt="Test me on the most important points in this lesson.">Test my recall</button>' +
					'<button type="button" data-study-buddy-prompt="What should I remember for SQE-style questions?">Focus my revision</button>' +
				'</div>' +
				'<form class="aimatic-study-buddy-form"><label class="sr-only" for="aimatic-study-buddy-question">Ask Study Buddy</label><textarea id="aimatic-study-buddy-question" rows="3" maxlength="1200" placeholder="Ask a focused question about this lesson"></textarea><button type="submit">Ask Study Buddy <span aria-hidden="true">↗</span></button></form>' +
				'<p class="aimatic-study-buddy-status" data-study-buddy-status>Your question and this lesson&rsquo;s approved text are sent to Study Buddy for a source-grounded response. Not legal advice.</p>' +
			'</section>';
		document.body.appendChild(dock);
		setStudyBuddyOpen(dock, false);
		wireStudyBuddy(dock);
	}

	function decorateLessonPage() {
		if (!isLmsRoute()) return;
		document.body.classList.add("aimatic-lms-learner");

		const aside = findLessonAside();
		if (aside) {
			aside.classList.add("aimatic-lms-chapter-rail");
			const parent = aside.parentElement;
			if (parent) {
				parent.classList.remove("aimatic-lms-lesson-grid");
				Array.from(parent.children).forEach(function (child) {
					if (child === aside) return;
					if (child.classList.contains("aimatic-lms-ai-rail")) {
						child.remove();
						return;
					}
					child.classList.add("aimatic-lms-lesson-main");
				});
			}
		}
		addStudyBuddyDock();
	}
	function initChapterHub(root) {
		if (!root || root.dataset.aimaticHubReady) return;
		root.dataset.aimaticHubReady = "1";

		const tabs = root.querySelectorAll(".ach-tab");
		const panels = root.querySelectorAll(".ach-panel[data-ach-panel]");
		tabs.forEach(function (tab) {
			tab.addEventListener("click", function () {
				const name = tab.dataset.achTab;
				tabs.forEach(function (item) {
					const active = item === tab;
					item.classList.toggle("is-active", active);
					item.setAttribute("aria-selected", active ? "true" : "false");
				});
				panels.forEach(function (panel) {
					const active = panel.dataset.achPanel === name;
					panel.classList.toggle("is-active", active);
					panel.hidden = !active;
				});
			});
		});

		const study = root.querySelector("[data-ach-flash-study]");
		if (!study) return;
		const items = Array.from(study.querySelectorAll("[data-ach-card]"));
		const ratings = study.querySelectorAll("[data-ach-rating]");
		let current = items.findIndex(function (item) { return !item.hidden; });
		if (current < 0) current = 0;

		function flip(item) {
			const front = item.querySelector(".ach-card-front");
			const back = item.querySelector(".ach-card-back");
			const card = item.querySelector("[data-ach-flash-card]");
			const revealed = !back.hidden;
			front.hidden = revealed;
			back.hidden = !revealed;
			card.classList.toggle("is-back", revealed);
			ratings.forEach(function (button) { button.disabled = !revealed; });
		}

		function showNext() {
			items[current].hidden = true;
			current += 1;
			if (current >= items.length) {
				study.innerHTML = '<div class="ach-flash-complete"><strong>Deck complete</strong><span>Revise Hard cards from Revision, or study this deck again.</span><p><a href="/learning-revision?course=business-law-practice-blp">Open weak areas</a></p></div>';
				return;
			}
			items[current].hidden = false;
			const card = items[current].querySelector("[data-ach-flash-card]");
			const front = items[current].querySelector(".ach-card-front");
			const back = items[current].querySelector(".ach-card-back");
			front.hidden = false;
			back.hidden = true;
			card.classList.remove("is-back");
			ratings.forEach(function (button) { button.disabled = true; });
		}

		items.forEach(function (item) {
			const card = item.querySelector("[data-ach-flash-card]");
			card.addEventListener("click", function () { flip(item); });
			card.addEventListener("keydown", function (event) {
				if (event.key === "Enter" || event.key === " ") {
					event.preventDefault();
					flip(item);
				}
			});
		});

		ratings.forEach(function (button) {
			button.disabled = true;
			button.addEventListener("click", function () {
				const item = items[current];
				if (!item || button.disabled) return;
				button.disabled = true;
				frappe.call({
					method: "aimaticlearning.lms_learning.api.review_flashcard",
					args: { name: item.dataset.achCardName, rating: button.dataset.achRating },
					callback: showNext,
					errorback: function () { button.disabled = false; },
				});
			});
		});
	}

	function bootHubs() {
		document.querySelectorAll(".aimatic-chapter-hub").forEach(initChapterHub);
	}

	function boot() {
		if (!isLmsRoute()) return;
		decorateLessonPage();
		setTimeout(decorateLessonPage, 250);
		setTimeout(decorateLessonPage, 800);
		bootHubs();
		setTimeout(decorateLessonPage, 1800);
	}

	function apply() {
		ensureCanonicalTags();
		if (!isLmsRoute()) return;
		decorateLessonPage();
		bootHubs();
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

(function hideBuiltOnFrappe() {
	function hide() {
		document.querySelectorAll(".footer-powered, a[href*=\"frappeframework.com?source=website_footer\"]").forEach(function (el) {
			el.style.setProperty("display", "none", "important");
			el.setAttribute("aria-hidden", "true");
		});
		document.querySelectorAll("span.lucide-zap.size-4.text-ink-gray-7.cursor-pointer").forEach(function (icon) {
			icon.style.setProperty("display", "none", "important");
			icon.setAttribute("aria-hidden", "true");
		});
	}
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", hide);
	} else {
		hide();
	}
	setTimeout(hide, 500);
	setTimeout(hide, 2000);
})();
