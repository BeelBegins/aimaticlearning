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

	function escapeStudyBuddyText(text) {
		const node = document.createElement("div");
		node.textContent = text == null ? "" : String(text);
		return node.innerHTML;
	}

	function formatStudyBuddyInline(text) {
		return escapeStudyBuddyText(text)
			.replace(/`([^`]+)`/g, "<code>$1</code>")
			.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
	}

	function renderStudyBuddyMarkdown(text) {
		const root = document.createElement("div");
		root.className = "aimatic-study-buddy-md";
		const lines = String(text || "").replace(/\r\n/g, "\n").split("\n");
		let list = null;
		let listType = null;

		function closeList() {
			if (!list) return;
			root.append(list);
			list = null;
			listType = null;
		}

		lines.forEach(function (line) {
			const numbered = line.match(/^\s*\d+[.)]\s+(.*)$/);
			const bullet = line.match(/^\s*[-*]\s+(.*)$/);
			if (numbered) {
				if (listType !== "ol") {
					closeList();
					list = document.createElement("ol");
					listType = "ol";
				}
				const item = document.createElement("li");
				item.innerHTML = formatStudyBuddyInline(numbered[1]);
				list.append(item);
				return;
			}
			if (bullet) {
				if (listType !== "ul") {
					closeList();
					list = document.createElement("ul");
					listType = "ul";
				}
				const item = document.createElement("li");
				item.innerHTML = formatStudyBuddyInline(bullet[1]);
				list.append(item);
				return;
			}
			closeList();
			if (!line.trim()) return;
			const paragraph = document.createElement("p");
			paragraph.innerHTML = formatStudyBuddyInline(line);
			root.append(paragraph);
		});
		closeList();
		if (!root.childNodes.length) {
			const paragraph = document.createElement("p");
			paragraph.textContent = text || "";
			root.append(paragraph);
		}
		return root;
	}

	function lessonStudyBuddyKey(context) {
		return context.course + ":" + context.chapter;
	}

	function studyBuddyStorageKey(context) {
		return "aimatic-study-buddy:" + lessonStudyBuddyKey(context);
	}

	function createStudyBuddyConversationId() {
		if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
		const bytes = new Uint8Array(16);
		window.crypto.getRandomValues(bytes);
		bytes[6] = (bytes[6] & 15) | 64;
		bytes[8] = (bytes[8] & 63) | 128;
		const hex = Array.from(bytes, function (byte) { return byte.toString(16).padStart(2, "0"); }).join("");
		return hex.slice(0, 8) + "-" + hex.slice(8, 12) + "-" + hex.slice(12, 16) + "-" + hex.slice(16, 20) + "-" + hex.slice(20);
	}

	function studyBuddyConversationId(context, reset) {
		const key = studyBuddyStorageKey(context);
		let value = reset ? "" : window.localStorage.getItem(key);
		if (!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value || "")) {
			value = createStudyBuddyConversationId();
			window.localStorage.setItem(key, value);
		}
		return value;
	}

	function studyBuddySourceLabel(result) {
		const sources = Array.isArray(result.sources) ? result.sources : [];
		const labels = sources.map(function (source) { return source.label; }).filter(Boolean);
		if (labels.length) return labels.join(" · ");
		return result.source && result.source.label;
	}

	function appendStudyBuddyMessage(host, kind, text, sourceLabel) {
		host.hidden = false;
		const message = document.createElement("section");
		message.className = "aimatic-study-buddy-message aimatic-study-buddy-message-" + kind;
		message.setAttribute("aria-label", kind === "user" ? "You" : "Study Buddy");
		if (kind === "assistant") message.append(renderStudyBuddyMarkdown(text));
		else {
			const body = document.createElement("p");
			body.textContent = text;
			message.append(body);
		}
		if (sourceLabel) {
			const source = document.createElement("small");
			source.textContent = "Source: " + sourceLabel;
			message.append(source);
		}
		host.append(message);
		host.scrollTop = host.scrollHeight;
		return message;
	}

	function appendStudyBuddyFailure(host, text, retry) {
		host.hidden = false;
		const message = document.createElement("section");
		message.className = "aimatic-study-buddy-message aimatic-study-buddy-message-error";
		message.setAttribute("role", "alert");
		const body = document.createElement("p");
		body.textContent = text;
		const button = document.createElement("button");
		button.type = "button";
		button.className = "aimatic-study-buddy-retry";
		button.textContent = "Retry";
		button.addEventListener("click", function () {
			message.remove();
			retry();
		});
		message.append(body, button);
		host.append(message);
		host.scrollTop = host.scrollHeight;
	}

	function studyBuddyServerMessage(payload, response) {
		if (response.status === 429) return "You have reached the 40-question hourly limit. Please try again after it resets.";
		if (payload && typeof payload.message === "string") return payload.message;
		if (payload && payload._server_messages) {
			try {
				const messages = JSON.parse(payload._server_messages);
				for (const raw of messages) {
					const parsed = JSON.parse(raw);
					if (parsed && parsed.message) return parsed.message;
				}
			} catch (_) {}
		}
		return "Study Buddy is temporarily unavailable. Please retry this question.";
	}

	async function studyBuddyJson(response) {
		let payload = {};
		try { payload = await response.json(); } catch (_) {}
		if (!response.ok) throw new Error(studyBuddyServerMessage(payload, response));
		return payload;
	}

	function loadStudyBuddyHistory(dock, context) {
		const card = dock.querySelector("[data-study-buddy]");
		if (!card || !context) return;
		const key = lessonStudyBuddyKey(context);
		if (card.dataset.studyBuddyChapter === key) return;
		card.dataset.studyBuddyChapter = key;
		const conversationId = studyBuddyConversationId(context, false);
		card.dataset.studyBuddyConversation = conversationId;
		const transcript = card.querySelector("[data-study-buddy-transcript]");
		const status = card.querySelector("[data-study-buddy-status]");
		if (transcript) {
			transcript.innerHTML = "";
			transcript.hidden = true;
		}
		card.classList.remove("is-chatting");
		card.dataset.studyBuddyHistory = "[]";
		const params = new URLSearchParams({
			course: context.course,
			chapter: String(context.chapter),
			lesson: String(context.lesson),
			conversation_id: conversationId,
		});
		fetch("/api/method/aimaticlearning.lms_learning.study_buddy.get_study_buddy_history?" + params.toString(), {
			credentials: "same-origin",
		})
			.then(studyBuddyJson)
			.then(function (payload) {
				if (card.dataset.studyBuddyChapter !== key || !transcript) return;
				if (payload.message && payload.message.conversation_id) {
					card.dataset.studyBuddyConversation = payload.message.conversation_id;
					window.localStorage.setItem(studyBuddyStorageKey(context), payload.message.conversation_id);
				}
				const turns = (payload.message && payload.message.turns) || [];
				const history = [];
				turns.forEach(function (turn) {
					if (turn.question) appendStudyBuddyMessage(transcript, "user", turn.question);
					if (turn.answer) appendStudyBuddyMessage(transcript, "assistant", turn.answer);
					if (turn.question && turn.answer) {
						history.push({ role: "user", content: turn.question }, { role: "assistant", content: turn.answer });
					}
				});
				if (history.length) {
					card.classList.add("is-chatting");
					card.dataset.studyBuddyHistory = JSON.stringify(history.slice(-12));
					if (status) status.textContent = "Recent questions from this chapter. Not legal advice.";
				}
			})
			.catch(function () {
				if (status) status.textContent = "Could not load recent questions. You can still start a new chat.";
			});
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
		if (hint) hint.textContent = "Approved chapter context is selected automatically.";
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
		const newChat = dock.querySelector("[data-study-buddy-new]");
		toggle.addEventListener("click", function () {
			setStudyBuddyOpen(dock, dock.querySelector("[data-study-buddy-panel]").hidden);
		});
		if (closer) closer.addEventListener("click", function () { setStudyBuddyOpen(dock, false); });
		if (newChat) newChat.addEventListener("click", function () {
			const context = currentLessonContext();
			if (!context || submit.disabled) return;
			const conversationId = studyBuddyConversationId(context, true);
			card.dataset.studyBuddyConversation = conversationId;
			card.dataset.studyBuddyHistory = "[]";
			transcript.innerHTML = "";
			transcript.hidden = true;
			card.classList.remove("is-chatting");
			input.value = "";
			status.textContent = "New chapter chat started. Not legal advice.";
			input.focus();
		});
		document.addEventListener("keydown", function (event) {
			if (event.key === "Escape") setStudyBuddyOpen(dock, false);
		});
		card.querySelectorAll("[data-study-buddy-prompt]").forEach(function (button) {
			button.addEventListener("click", function () {
				input.value = button.dataset.studyBuddyPrompt;
				if (submit.disabled) return;
				if (typeof form.requestSubmit === "function") form.requestSubmit();
				else form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
			});
		});
		input.addEventListener("keydown", function (event) {
			if (event.key !== "Enter" || event.shiftKey) return;
			event.preventDefault();
			if (submit.disabled) return;
			if (typeof form.requestSubmit === "function") form.requestSubmit();
			else form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
		});
		async function sendQuestion(question, addUserMessage) {
			const context = currentLessonContext();
			if (!context) {
				status.textContent = "Open a lesson before asking Study Buddy.";
				return;
			}
			let history = [];
			try { history = JSON.parse(card.dataset.studyBuddyHistory || "[]"); } catch (_) {}
			if (addUserMessage) appendStudyBuddyMessage(transcript, "user", question);
			card.classList.add("is-chatting");
			if (input.value.trim() === question) input.value = "";
			submit.disabled = true;
			status.textContent = "Working on your question…";
			const mcq = liveMcqContext();
			const conversationId = card.dataset.studyBuddyConversation || studyBuddyConversationId(context, false);
			card.dataset.studyBuddyConversation = conversationId;
			const controller = new AbortController();
			const timer = window.setTimeout(function () { controller.abort(); }, 55000);
			try {
				const response = await fetch("/api/method/aimaticlearning.lms_learning.study_buddy.ask_study_buddy", {
					method: "POST",
					credentials: "same-origin",
					signal: controller.signal,
					headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.csrf_token || "" },
					body: JSON.stringify({
						course: context.course,
						chapter: context.chapter,
						lesson: context.lesson,
						question: question,
						history: JSON.stringify(history),
						attempt_context: mcq ? JSON.stringify(mcq) : "",
						conversation_id: conversationId,
					}),
				});
				const payload = await studyBuddyJson(response);
				const result = payload.message || {};
				if (!result.answer) throw new Error("Study Buddy could not complete that answer. Please retry.");
				if (result.conversation_id) {
					card.dataset.studyBuddyConversation = result.conversation_id;
					window.localStorage.setItem(studyBuddyStorageKey(context), result.conversation_id);
				}
				appendStudyBuddyMessage(transcript, "assistant", result.answer, studyBuddySourceLabel(result));
				history.push({ role: "user", content: question }, { role: "assistant", content: result.answer });
				card.dataset.studyBuddyHistory = JSON.stringify(history.slice(-12));
				status.textContent = result.notice || "Answered from approved material in this chapter. Not legal advice.";
			} catch (error) {
				const message = error.name === "AbortError"
					? "Study Buddy took too long to answer. Please retry this question."
					: (error.message || "Study Buddy is temporarily unavailable. Please retry this question.");
				status.textContent = message;
				if (!input.value.trim()) input.value = question;
				appendStudyBuddyFailure(transcript, message, function () { sendQuestion(question, false); });
			} finally {
				window.clearTimeout(timer);
				submit.disabled = false;
			}
		}

		form.addEventListener("submit", function (event) {
			event.preventDefault();
			const question = input.value.trim();
			if (!question) {
				input.focus();
				return;
			}
			sendQuestion(question, true);
		});
	}

	function addStudyBuddyDock() {
		const context = currentLessonContext();
		if (!context) {
			const leftover = document.querySelector(".aimatic-study-buddy-dock");
			if (leftover) leftover.remove();
			return;
		}
		let dock = document.querySelector(".aimatic-study-buddy-dock");
		if (dock) {
			refreshStudyBuddyTopic(dock.querySelector("[data-study-buddy]"));
			loadStudyBuddyHistory(dock, context);
			return;
		}
		dock = document.createElement("div");
		dock.className = "aimatic-study-buddy-dock";
		dock.innerHTML =
			'<button type="button" class="aimatic-study-buddy-fab" data-study-buddy-toggle aria-expanded="false" aria-controls="aimatic-study-buddy-panel">Study Buddy</button>' +
			'<section id="aimatic-study-buddy-panel" class="aimatic-lms-ai-card aimatic-study-buddy" data-study-buddy data-study-buddy-panel hidden>' +
				'<div class="aimatic-study-buddy-head">Study Buddy' +
					'<button type="button" class="aimatic-study-buddy-new" data-study-buddy-new>New chat</button>' +
					'<button type="button" class="aimatic-study-buddy-close" data-study-buddy-close aria-label="Close Study Buddy">×</button></div>' +
				'<div class="aimatic-lms-ai-context"><strong data-study-buddy-topic>This lesson</strong><small data-study-buddy-hint>Approved chapter context is selected automatically.</small></div>' +
				'<div class="aimatic-study-buddy-transcript" data-study-buddy-transcript aria-live="polite" hidden></div>' +
				'<div class="aimatic-study-buddy-prompts" aria-label="Suggested questions">' +
					'<button type="button" data-study-buddy-prompt="Explain the key rule in simple terms.">Explain the key rule</button>' +
					'<button type="button" data-study-buddy-prompt="Test me on the most important points in this lesson.">Test my recall</button>' +
					'<button type="button" data-study-buddy-prompt="What should I remember for SQE-style questions?">Focus my revision</button>' +
				'</div>' +
				'<form class="aimatic-study-buddy-form"><label class="sr-only" for="aimatic-study-buddy-question">Ask Study Buddy</label><textarea id="aimatic-study-buddy-question" rows="2" maxlength="1200" placeholder="Ask this lesson"></textarea><button type="submit">Send</button></form>' +
				'<p class="aimatic-study-buddy-status" data-study-buddy-status>Not legal advice.</p>' +
			'</section>';
		document.body.appendChild(dock);
		setStudyBuddyOpen(dock, false);
		wireStudyBuddy(dock);
		loadStudyBuddyHistory(dock, context);
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
