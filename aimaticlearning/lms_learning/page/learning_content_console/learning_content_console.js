frappe.pages["learning-content-console"].on_page_load = function (wrapper) {
	window.cur_frm = null;
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Content Studio"),
		single_column: true,
	});

	const MODULE_KEY = "aimatic-content-studio-module";
	const state = {
		modules: [],
		tree: null,
		bundle: null,
		tab: "notes",
		notesControl: null,
		savedNotes: "",
		savedHeading: "",
		chapterQuery: "",
		chapterFilter: "all",
		itemQuery: "",
		expandedItem: "",
		headingDirty: false,
		notesEdited: false,
		notesSelection: "",
	};

	const $root = $(`
		<div class="aimatic-content-studio">
			<div class="studio-toolbar">
				<select class="form-control module-select"></select>
				<button class="btn btn-default btn-refresh">${__("Refresh")}</button>
				<button class="btn btn-default btn-add-course">${__("Add course")}</button>
				<a class="btn btn-default-dark btn-preview" target="_blank" rel="noopener" hidden>${__("Preview notes")}</a>
				<span class="studio-status text-muted"></span>
				<span class="shortcut-hint">${__("Ctrl/Cmd+S saves the open pane")}</span>
			</div>
			<div class="studio-shell">
				<aside class="studio-chapters"></aside>
				<section class="studio-main">
					<div class="studio-empty">${__("Pick a subject, then a chapter. Notes, MCQs, and cards for that chapter stay in this window.")}</div>
				</section>
			</div>
		</div>
	`).appendTo(page.body);

	function esc(value) {
		return frappe.utils.escape_html(value || "");
	}

	function setStatus(message, dirty) {
		const $status = $root.find(".studio-status");
		$status.text(message || "");
		$status.toggleClass("is-dirty", Boolean(dirty));
	}

	function sanitizeNotesHtml(html) {
		let text = html || "";
		const wrapped = text.match(/^\s*<div class="ql-editor(?:\s[^"]*)?"[^>]*>([\s\S]*)<\/div>\s*$/i);
		if (wrapped) text = (wrapped[1] || "").trim();
		else text = text.trim();
		const visible = text.replace(/<\/?p>/gi, " ").replace(/<br\s*\/?>/gi, " ").replace(/&nbsp;/gi, " ").replace(/\s+/g, " ").trim();
		if (!visible) return "";
		return text;
	}

	function currentNotes() {
		if (state.notesControl) return state.notesControl.get_value() || "";
		return (state.bundle && state.bundle.notes_html) || "";
	}

	function notesDirty() {
		return sanitizeNotesHtml(currentNotes()) !== sanitizeNotesHtml(state.savedNotes);
	}

	function baselineNotes() {
		state.savedNotes = sanitizeNotesHtml(currentNotes());
		state.notesEdited = false;
	}

	function isDirty() {
		if (!state.bundle) return false;
		if (state.headingDirty) return true;
		if (state.notesEdited) return true;
		if ($root.find(".mcq-card.dirty, .flashcard-card.dirty").length) return true;
		return false;
	}

	function captureNotesSelection() {
		const editor = $root.find(".pane-notes .ql-editor")[0];
		if (!editor) return;
		const sel = window.getSelection();
		if (!sel || !sel.rangeCount || !sel.toString().trim()) return;
		if (!editor.contains(sel.anchorNode)) return;
		state.notesSelection = sel.toString().replace(/\s+/g, " ").trim();
	}

	function confirmDiscardItemEdits() {
		if (!$root.find(".mcq-card.dirty, .flashcard-card.dirty").length) return Promise.resolve(true);
		return confirmUnsaved(__("You have unsaved MCQ or card edits."));
	}

	function confirmLeave() {
		if (!isDirty()) return Promise.resolve(true);
		return confirmUnsaved(__("You have unsaved edits in this chapter."));
	}

	function confirmUnsaved(message) {
		return new Promise((resolve) => {
			let settled = false;
			const finish = (ok) => {
				if (settled) return;
				settled = true;
				resolve(ok);
			};
			const dialog = new frappe.ui.Dialog({
				title: __("Unsaved edits"),
				primary_action_label: __("Discard"),
				primary_action() {
					finish(true);
					dialog.hide();
				},
			});
			dialog.set_secondary_action_label(__("Stay"));
			dialog.set_secondary_action(() => {
				finish(false);
				dialog.hide();
			});
			dialog.$body.html(`<p>${frappe.utils.escape_html(message)}</p>`);
			dialog.onhide = () => finish(false);
			dialog.show();
		});
	}

	function markSaved() {
		if (!state.bundle) return;
		baselineNotes();
		state.savedHeading = state.bundle.chapter_title || "";
		state.headingDirty = false;
		$root.find(".mcq-card.dirty, .flashcard-card.dirty").removeClass("dirty");
		setStatus(__("Saved"), false);
	}

	function studioCall(opts) {
		return frappe.call(opts);
	}

	function selectedModule() {
		return $root.find(".module-select").val();
	}

	function loadModules() {
		return studioCall({
			method: "aimaticlearning.lms_learning.content_studio.get_studio_tree",
		}).then((r) => {
			state.modules = (r.message && r.message.modules) || [];
			const $select = $root.find(".module-select");
			const remembered = localStorage.getItem(MODULE_KEY);
			const current = $select.val() || remembered;
			$select.empty();
			if (!state.modules.length) {
				$select.append(`<option value="">${__("No learning modules")}</option>`);
				return;
			}
			state.modules.forEach((row) => {
				const prefix = row.pathway && row.pathway !== "Other" ? row.pathway + " · " : "";
				$select.append(
					`<option value="${esc(row.name)}">${esc(prefix + (row.title || row.name))}</option>`
				);
			});
			if (current && state.modules.some((row) => row.name === current)) {
				$select.val(current);
			}
			return loadTree();
		});
	}

	function loadTree() {
		const learning_module = selectedModule();
		if (!learning_module) return Promise.resolve();
		return studioCall({
			method: "aimaticlearning.lms_learning.content_studio.get_studio_tree",
			args: { learning_module },
		})
			.then((r) => {
				state.tree = r.message || {};
				renderChapters();
			});
	}

	function renderChapters() {
		const $list = $root.find(".studio-chapters");
		$list.empty();
		const chapters = (state.tree && state.tree.chapters) || [];
		const target = (state.tree && state.tree.target_chapter_mcq_count) || 20;
		const emptyCount = chapters.filter((chapter) => !chapter.notes_chars).length;
		const shortCount = chapters.filter((chapter) => (chapter.mcq_count || 0) < target).length;
		const staleCount = chapters.filter((chapter) => chapter.notes_status === "out_of_sync").length;
		$list.append(
			`<input class="form-control chapter-filter" placeholder="${__("Filter chapters")}" value="${esc(state.chapterQuery)}">`
		);
		$list.append(`
			<div class="chapter-coverage">
				<button type="button" class="btn btn-xs ${state.chapterFilter === "all" ? "btn-primary" : "btn-default"} btn-chapter-filter" data-filter="all">${__("All")} ${chapters.length}</button>
				<button type="button" class="btn btn-xs ${state.chapterFilter === "empty" ? "btn-primary" : "btn-default"} btn-chapter-filter" data-filter="empty">${__("Empty notes")} ${emptyCount}</button>
				<button type="button" class="btn btn-xs ${state.chapterFilter === "short" ? "btn-primary" : "btn-default"} btn-chapter-filter" data-filter="short">${__("Short MCQ")} ${shortCount}</button>
				<button type="button" class="btn btn-xs ${state.chapterFilter === "stale" ? "btn-primary" : "btn-default"} btn-chapter-filter" data-filter="stale">${__("Out of sync")} ${staleCount}</button>
			</div>
		`);
		if (!chapters.length) {
			$list.append(`<div class="text-muted">${__("No chapter profiles for this subject.")}</div>`);
			$list.append(
				`<button type="button" class="btn btn-sm btn-primary btn-add-chapter" style="width:100%;margin-top:8px;">${__("Add chapter")}</button>`
			);
			return;
		}
		const query = (state.chapterQuery || "").toLowerCase();
		let shown = 0;
		chapters.forEach((chapter) => {
			const haystack = `${chapter.chapter_title || ""} ${chapter.name}`.toLowerCase();
			if (query && haystack.indexOf(query) === -1) return;
			if (state.chapterFilter === "empty" && chapter.notes_chars) return;
			if (state.chapterFilter === "short" && (chapter.mcq_count || 0) >= target) return;
			if (state.chapterFilter === "stale" && chapter.notes_status !== "out_of_sync") return;
			shown += 1;
			const active = state.bundle && state.bundle.name === chapter.name ? "active" : "";
			const empty = !chapter.notes_chars ? "is-empty" : "";
			const short = (chapter.mcq_count || 0) < target ? "is-short" : "";
			const stale = chapter.notes_status === "out_of_sync" ? "is-stale" : "";
			const number = chapter.outline_idx ? `${chapter.outline_idx}. ` : "";
			const notesChip = notesStatusChip(chapter);
			const pub = cint(chapter.flashcard_published);
			const review = cint(chapter.flashcard_under_review);
			const draft = cint(chapter.flashcard_draft);
			$list.append(`
				<div class="chapter-row">
					<button type="button" class="chapter-btn ${active} ${empty} ${short} ${stale}" data-profile="${esc(chapter.name)}">
						<span class="chapter-title">${esc(number + (chapter.chapter_title || ""))}</span>
						<span class="chapter-chips">${notesChip}
							<span class="studio-chip">${chapter.mcq_count || 0}/${target} MCQs</span>
							<span class="studio-chip">${pub} pub · ${review} review · ${draft} draft</span>
						</span>
					</button>
					<div class="chapter-pos">
						<button type="button" class="btn btn-xs btn-default btn-move-chapter" data-profile="${esc(chapter.name)}" data-dir="up" title="${__("Move up")}">↑</button>
						<button type="button" class="btn btn-xs btn-default btn-move-chapter" data-profile="${esc(chapter.name)}" data-dir="down" title="${__("Move down")}">↓</button>
					</div>
				</div>
			`);
		});
		if (!shown) {
			$list.append(`<div class="text-muted">${__("No chapters match that filter.")}</div>`);
		}
		$list.append(
			`<button type="button" class="btn btn-sm btn-primary btn-add-chapter" style="width:100%;margin-top:8px;">${__("Add chapter")}</button>`
		);
	}

	function notesStatusChip(row) {
		const status = (row && row.notes_status) || "empty";
		const label = (row && row.notes_status_label) || __("Notes");
		return `<span class="studio-chip notes-chip notes-${esc(status)}">${esc(label)}</span>`;
	}

	function openChapter(chapter_profile, opts) {
		opts = opts || {};
		const load = function () {
			return studioCall({
				method: "aimaticlearning.lms_learning.content_studio.get_chapter_bundle",
				args: { chapter_profile },
			}).then((r) => {
				state.bundle = r.message;
				state.tab = state.tab || "notes";
				state.savedNotes = sanitizeNotesHtml((state.bundle && state.bundle.notes_html) || "");
				state.savedHeading = (state.bundle && state.bundle.chapter_title) || "";
				state.headingDirty = false;
				state.notesEdited = false;
				state.itemQuery = "";
				state.expandedItem = "";
				state.notesControl = null;
				renderChapters();
				renderMain();
				setStatus("", false);
			});
		};
		if (opts.force) return load();
		return confirmLeave().then((ok) => {
			if (!ok) return;
			return load();
		});
	}

	function updateHeaderMeta() {
		const bundle = state.bundle;
		if (!bundle) return;
		const notesLabel = bundle.notes_status_label || __("Notes");
		$root.find(".studio-header-meta").html(
			`${esc(bundle.module_title || "")} · revision ${cint(bundle.source_revision)} · ${bundle.mcq_count}/${bundle.target_chapter_mcq_count} MCQs · <span class="studio-chip notes-chip notes-${esc(bundle.notes_status || "empty")}">${esc(notesLabel)}</span> · ${cint(bundle.flashcard_published)} pub cards`
		);
		$root.find(".chapter-heading").val(bundle.chapter_title || "");
		if (bundle.preview_url) {
			$root.find(".btn-preview").attr("href", bundle.preview_url).removeAttr("hidden");
		}
	}

	function refreshOpenChapter(opts) {
		opts = opts || {};
		if (!state.bundle) return;
		const keepNotes = Boolean(opts.keepNotes);
		const notesHtml = keepNotes ? currentNotes() : null;
		const keepExpanded = state.expandedItem;
		return studioCall({
			method: "aimaticlearning.lms_learning.content_studio.get_chapter_bundle",
			args: { chapter_profile: state.bundle.name },
		}).then((r) => {
			state.bundle = r.message;
			if (keepNotes && notesHtml !== null) {
				state.bundle.notes_html = notesHtml;
			} else {
				state.savedNotes = sanitizeNotesHtml((state.bundle && state.bundle.notes_html) || "");
				state.notesEdited = false;
			}
			state.savedHeading = (state.bundle && state.bundle.chapter_title) || "";
			state.headingDirty = false;
			if (opts.expand) state.expandedItem = opts.expand;
			else state.expandedItem = keepExpanded;
			updateHeaderMeta();
			renderChapters();
			if (state.tab === "mcqs") renderMcqs($root.find(".pane-mcqs"));
			if (state.tab === "cards") renderCards($root.find(".pane-cards"));
			setStatus(opts.status || "", false);
			return loadTree();
		});
	}

	function showActivePane() {
		$root.find(".studio-pane").attr("hidden", true);
		$root.find(".btn-tab").removeClass("btn-primary").addClass("btn-default");
		$root.find(`.btn-tab[data-tab="${state.tab}"]`).removeClass("btn-default").addClass("btn-primary");
		const paneClass = state.tab === "cards" ? "pane-cards" : state.tab === "mcqs" ? "pane-mcqs" : "pane-notes";
		const $pane = $root.find("." + paneClass);
		$pane.removeAttr("hidden");
		if (state.tab === "notes") {
			if (!$pane.find(".notes-editor-host").length) renderNotes($pane);
		} else if (state.tab === "mcqs") {
			renderMcqs($pane);
		} else {
			renderCards($pane);
		}
	}

	function renderMain() {
		const $main = $root.find(".studio-main");
		const bundle = state.bundle;
		const $preview = $root.find(".btn-preview");
		if (!bundle) {
			$preview.attr("hidden", true);
			$main.html(
				`<div class="studio-empty">${__("Pick a subject, then a chapter. Notes, MCQs, and cards for that chapter stay in this window.")}</div>`
			);
			return;
		}

		$preview.attr("href", bundle.preview_url).removeAttr("hidden");
		const notesLabel = bundle.notes_status_label || __("Notes");
		$main.html(`
			<div class="studio-header">
				<div class="chapter-heading-row">
					<input class="form-control chapter-heading" maxlength="140" value="${esc(bundle.chapter_title)}" aria-label="${__("Chapter heading")}">
					<button type="button" class="btn btn-primary btn-save-heading">${__("Rename chapter")}</button>
					<button type="button" class="btn btn-default btn-remove-chapter">${__("Remove chapter")}</button>
				</div>
				<div class="text-muted studio-header-meta">
					${esc(bundle.module_title)} · revision ${cint(bundle.source_revision)} · ${bundle.mcq_count}/${bundle.target_chapter_mcq_count} MCQs · <span class="studio-chip notes-chip notes-${esc(bundle.notes_status || "empty")}">${esc(notesLabel)}</span> · ${cint(bundle.flashcard_published)} pub cards
				</div>
			</div>
			<div class="studio-tabs">
				<button type="button" class="btn btn-tab ${state.tab === "notes" ? "btn-primary" : "btn-default"}" data-tab="notes">${__("Notes")}</button>
				<button type="button" class="btn btn-tab ${state.tab === "mcqs" ? "btn-primary" : "btn-default"}" data-tab="mcqs">${__("MCQs")}</button>
				<button type="button" class="btn btn-tab ${state.tab === "cards" ? "btn-primary" : "btn-default"}" data-tab="cards">${__("Cards")}</button>
			</div>
			<div class="studio-pane pane-notes" hidden></div>
			<div class="studio-pane pane-mcqs" hidden></div>
			<div class="studio-pane pane-cards" hidden></div>
		`);
		showActivePane();
	}

	function cint(value) {
		return parseInt(value || 0, 10) || 0;
	}

	function renderNotes($pane) {
		const bundle = state.bundle || {};
		const inSync = Boolean(bundle.notes_in_sync);
		const status = bundle.notes_status || "empty";
		const editorLabel = inSync
			? __("Learner notes (published)")
			: __("Studio working copy");
		const syncBanner = inSync
			? `<div class="notes-sync-banner is-sync"><span class="studio-chip notes-chip notes-in_sync">${__("In sync")}</span> ${__("Studio and learner notes match. Save publishes both.")}</div>`
			: `<div class="notes-sync-banner is-drift">
					<span class="studio-chip notes-chip notes-${esc(status)}">${esc(bundle.notes_status_label || __("Out of sync"))}</span>
					${__("Studio working copy")} ${cint(bundle.notes_studio_chars)} chars · ${__("Learner published")} ${cint(bundle.notes_learner_chars)} chars.
					<div class="notes-sync-actions">
						<button type="button" class="btn btn-sm btn-primary btn-sync-to-learner">${__("Sync to learner")}</button>
						<button type="button" class="btn btn-sm btn-default btn-pull-learner">${__("Pull learner → studio")}</button>
					</div>
				</div>`;
		$pane.html(`
			${syncBanner}
			<p class="text-muted" style="margin-top:8px;">
				${__("Section headings inside the notes: use Heading 2 / 3 in the editor toolbar. The chapter heading above is what learners see in the outline.")}
			</p>
			<div class="notes-editor-label">${esc(editorLabel)}</div>
			<div class="notes-editor-host"></div>
			<div class="mcq-actions">
				<button type="button" class="btn btn-primary btn-save-notes">${__("Save notes")}</button>
				<span class="notes-count text-muted"></span>
			</div>
		`);
		state.notesControl = frappe.ui.form.make_control({
			parent: $pane.find(".notes-editor-host"),
			df: {
				fieldtype: "Text Editor",
				fieldname: "notes_html",
				label: editorLabel,
			},
			only_input: true,
			render_input: 1,
		});
		state.notesControl.set_value(state.bundle.notes_html || "");
		baselineNotes();
		function updateCount() {
			const html = sanitizeNotesHtml(currentNotes());
			const text = html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
			$pane.find(".notes-count").text(
				__(" {0} characters · {1} words")
					.replace("{0}", html.length)
					.replace("{1}", text ? text.split(" ").length : 0)
			);
			if (state.notesEdited) setStatus(__("Unsaved notes"), true);
			else if (!isDirty()) setStatus("", false);
		}
		function bindNotesUserEdits() {
			const quill = state.notesControl && state.notesControl.quill;
			if (!quill || quill.__aimaticStudioBound) return;
			quill.__aimaticStudioBound = true;
			quill.on("text-change", function (_delta, _old, source) {
				if (source !== "user") {
					if (!state.notesEdited) baselineNotes();
					updateCount();
					return;
				}
				if (notesDirty()) {
					state.notesEdited = true;
					setStatus(__("Unsaved notes"), true);
				}
				updateCount();
			});
		}
		bindNotesUserEdits();
		updateCount();
		setTimeout(function () {
			if (!state.notesEdited) baselineNotes();
			bindNotesUserEdits();
			updateCount();
		}, 0);
		setTimeout(function () {
			if (!state.notesEdited) baselineNotes();
			updateCount();
		}, 400);
		$pane.find(".notes-editor-host").on("input change", updateCount);
	}

	function matchesQuery(text, query) {
		if (!query) return true;
		return (text || "").toLowerCase().indexOf(query) !== -1;
	}

	function renderMcqs($pane) {
		const questions = state.bundle.questions || [];
		$pane.html(`
			<div class="mcq-actions" style="margin-bottom:12px;">
				<button type="button" class="btn btn-primary btn-add-mcq">${__("Add MCQ")}</button>
				<button type="button" class="btn btn-default btn-collapse-all">${__("Collapse all")}</button>
				<input class="form-control item-filter" placeholder="${__("Filter questions")}" value="${esc(state.itemQuery)}">
			</div>
			<div class="mcq-new" hidden></div>
			<div class="mcq-list"></div>
		`);
		if (!questions.length) {
			$pane.find(".mcq-list").html(
				`<div class="text-muted">${__("No chapter MCQs yet. Add one here — it writes the question, tags, and chapter quiz together.")}</div>`
			);
			return;
		}
		const query = (state.itemQuery || "").toLowerCase();
		let shown = 0;
		questions.forEach((question, index) => {
			const haystack = `${question.question || ""} ${question.concept || ""}`;
			if (!matchesQuery(haystack, query)) return;
			shown += 1;
			$pane.find(".mcq-list").append(mcqCard(question, index + 1, question.lms_question !== state.expandedItem));
		});
		if (!shown) {
			$pane.find(".mcq-list").html(`<div class="text-muted">${__("No questions match that filter.")}</div>`);
		}
	}

	function renderCards($pane) {
		const cards = state.bundle.flashcards || [];
		$pane.html(`
			<p class="text-muted" style="margin-top:0;">
				${__("Published cards need a source quote copied from this chapter’s notes. Drafts can be saved without a quote.")}
			</p>
			<div class="mcq-actions" style="margin-bottom:12px;">
				<button type="button" class="btn btn-primary btn-add-card">${__("Add flashcard")}</button>
				<button type="button" class="btn btn-default btn-collapse-all">${__("Collapse all")}</button>
				<input class="form-control item-filter" placeholder="${__("Filter cards")}" value="${esc(state.itemQuery)}">
				${
					state.bundle.flashcards_url
						? `<a class="btn btn-default" href="${esc(state.bundle.flashcards_url)}" target="_blank" rel="noopener">${__("Preview deck")}</a>`
						: ""
				}
			</div>
			<div class="card-new" hidden></div>
			<div class="card-list"></div>
		`);
		if (!cards.length) {
			$pane.find(".card-list").html(`<div class="text-muted">${__("No flashcards in this chapter yet.")}</div>`);
			return;
		}
		const query = (state.itemQuery || "").toLowerCase();
		let shown = 0;
		cards.forEach((card, index) => {
			const haystack = `${card.front || ""} ${card.back || ""} ${card.concept || ""}`;
			if (!matchesQuery(haystack, query)) return;
			shown += 1;
			$pane.find(".card-list").append(flashcardForm(card, index + 1, card.name !== state.expandedItem));
		});
		if (!shown) {
			$pane.find(".card-list").html(`<div class="text-muted">${__("No cards match that filter.")}</div>`);
		}
	}

	function emptyQuestion() {
		return {
			lms_question: "",
			question: "",
			options: [
				{ text: "", is_correct: 0, explanation: "" },
				{ text: "", is_correct: 0, explanation: "" },
				{ text: "", is_correct: 0, explanation: "" },
				{ text: "", is_correct: 0, explanation: "" },
				{ text: "", is_correct: 0, explanation: "" },
			],
			concept: "",
			difficulty: "Medium",
			source_reference: "",
			learning_objective: "",
			question_role: "Chapter MCQ",
			revision: 1,
		};
	}

	function emptyCard() {
		return {
			name: "",
			front: "",
			back: "",
			concept: "",
			difficulty: "Medium",
			source_reference: "",
			source_quote: "",
			status: "Draft",
			revision: 1,
		};
	}

	function flashcardForm(card, number, collapsed) {
		const status = card.status || "Draft";
		const preview = (card.front || __("New card")).replace(/\s+/g, " ").slice(0, 90);
		const collapsedClass = collapsed ? "is-collapsed" : "";
		return $(`
			<div class="mcq-card flashcard-card ${collapsedClass}" data-card="${esc(card.name || "")}">
				<button type="button" class="item-summary btn-expand-item">
					<strong>${number ? __("Card") + " " + number : __("New card")}</strong>
					<span>${esc(preview)}</span>
					<small>${esc(status)}</small>
				</button>
				<div class="item-body">
				<div style="font-weight:600;margin-bottom:8px;">${esc(status)}</div>
				<textarea class="form-control card-front" rows="2" placeholder="${__("Front")}">${esc(card.front)}</textarea>
				<textarea class="form-control card-back" rows="3" placeholder="${__("Back")}" style="margin-top:6px;">${esc(card.back)}</textarea>
				<div class="row" style="margin-top:8px;">
					<div class="col-sm-4">
						<input class="form-control card-concept" placeholder="${__("Concept")}" value="${esc(card.concept)}">
					</div>
					<div class="col-sm-2">
						<select class="form-control card-difficulty">
							<option ${card.difficulty === "Easy" ? "selected" : ""}>Easy</option>
							<option ${card.difficulty === "Medium" ? "selected" : ""}>Medium</option>
							<option ${card.difficulty === "Hard" ? "selected" : ""}>Hard</option>
						</select>
					</div>
					<div class="col-sm-3">
						<select class="form-control card-status">
							${["Draft", "Under Review", "Published", "Retired"]
								.map(
									(item) =>
										`<option ${status === item ? "selected" : ""}>${item}</option>`
								)
								.join("")}
						</select>
					</div>
					<div class="col-sm-3">
						<input class="form-control card-source" placeholder="${__("Source reference")}" value="${esc(card.source_reference)}">
					</div>
				</div>
				<textarea class="form-control card-quote" rows="2" placeholder="${__("Exact quote from these notes (required to publish)")}" style="margin-top:6px;">${esc(card.source_quote)}</textarea>
				<div class="mcq-actions">
					<button type="button" class="btn btn-primary btn-save-card">${__("Save card")}</button>
					<button type="button" class="btn btn-default btn-quote-from-notes">${__("Use selected notes")}</button>
				</div>
				</div>
			</div>
		`);
	}

	function readCard($card) {
		return {
			name: $card.data("card") || "",
			front: $card.find(".card-front").val(),
			back: $card.find(".card-back").val(),
			concept: $card.find(".card-concept").val(),
			difficulty: $card.find(".card-difficulty").val(),
			source_reference: $card.find(".card-source").val(),
			source_quote: $card.find(".card-quote").val(),
			status: $card.find(".card-status").val(),
		};
	}

	function optionLetter(idx) {
		return String.fromCharCode(65 + idx);
	}

	function optionRowHtml(option, idx, qid) {
		const checked = option.is_correct ? "checked" : "";
		return `
			<div class="option-row">
				<input type="radio" name="correct-${esc(qid)}" value="${idx}" ${checked} title="${__("Correct option")}">
				<span class="option-letter">${optionLetter(idx)}</span>
				<div>
					<textarea class="form-control option-text" data-idx="${idx}" rows="2" placeholder="${__("Option")} ${optionLetter(idx)}">${esc(option.text)}</textarea>
					<textarea class="form-control option-expl" data-idx="${idx}" rows="2" placeholder="${__("Explanation")}" style="margin-top:4px;">${esc(option.explanation)}</textarea>
					<button type="button" class="btn btn-xs btn-default btn-remove-option">${__("Remove option")}</button>
				</div>
			</div>
		`;
	}

	function reindexOptions($card) {
		const qid = $card.data("question") || "new";
		$card.find(".option-row").each(function (idx) {
			$(this).find("input[type=radio]").attr("name", "correct-" + qid).val(idx);
			$(this).find(".option-text, .option-expl").attr("data-idx", idx);
			$(this).find(".option-letter").text(optionLetter(idx));
			$(this).find(".option-text").attr("placeholder", __("Option") + " " + optionLetter(idx));
		});
	}

	function mcqCard(question, number, collapsed) {
		const qid = question.lms_question || "new";
		const options = (question.options || []).length ? question.options : emptyQuestion().options;
		const optionHtml = options.map((option, idx) => optionRowHtml(option, idx, qid)).join("");
		const preview = (question.question || __("New question")).replace(/\s+/g, " ").slice(0, 110);
		const collapsedClass = collapsed ? "is-collapsed" : "";
		const onQuiz = question.on_chapter_quiz !== false;
		const quizFlag = question.lms_question ? (onQuiz ? __("on quiz") : __("not on quiz")) : __("new");
		return $(`
			<div class="mcq-card ${collapsedClass}" data-question="${esc(question.lms_question || "")}">
				<button type="button" class="item-summary btn-expand-item">
					<strong>${number ? __("Question") + " " + number : __("New question")}</strong>
					<span>${esc(preview)}</span>
					<small>rev ${cint(question.revision)} · ${esc(question.difficulty || "Medium")} · ${esc(quizFlag)}</small>
				</button>
				<div class="item-body">
				<textarea class="form-control mcq-stem" rows="3" placeholder="${__("Question stem")}">${esc(question.question)}</textarea>
				<div class="row" style="margin-top:8px;">
					<div class="col-sm-4">
						<input class="form-control mcq-concept" placeholder="${__("Concept")}" value="${esc(question.concept)}">
					</div>
					<div class="col-sm-2">
						<select class="form-control mcq-difficulty">
							<option ${question.difficulty === "Easy" ? "selected" : ""}>Easy</option>
							<option ${question.difficulty === "Medium" ? "selected" : ""}>Medium</option>
							<option ${question.difficulty === "Hard" ? "selected" : ""}>Hard</option>
						</select>
					</div>
					<div class="col-sm-6">
						<input class="form-control mcq-source" placeholder="${__("Source reference")}" value="${esc(question.source_reference)}">
					</div>
				</div>
				<input class="form-control mcq-objective" placeholder="${__("Learning objective")}" value="${esc(question.learning_objective || "")}" style="margin-top:8px;">
				<div class="option-host" style="margin-top:10px;">${optionHtml}</div>
				<div class="mcq-actions">
					<button type="button" class="btn btn-default btn-add-option">${__("Add option")}</button>
					<button type="button" class="btn btn-primary btn-save-mcq">${__("Save MCQ")}</button>
					${
						question.lms_question
							? `<button type="button" class="btn btn-default btn-move-mcq" data-dir="up">${__("Move up")}</button>
					<button type="button" class="btn btn-default btn-move-mcq" data-dir="down">${__("Move down")}</button>
					<button type="button" class="btn btn-default btn-duplicate-mcq">${__("Duplicate")}</button>
					<button type="button" class="btn btn-default btn-unlink-mcq">${__("Remove from chapter quiz")}</button>`
							: ""
					}
				</div>
				</div>
			</div>
		`);
	}

	function readMcqCard($card) {
		const options = [];
		$card.find(".option-text").each(function () {
			const idx = $(this).data("idx");
			options.push({
				text: $(this).val(),
				explanation: $card.find(`.option-expl[data-idx="${idx}"]`).val(),
				is_correct: $card.find(`input[type=radio]:checked`).val() == String(idx) ? 1 : 0,
			});
		});
		return {
			lms_question: $card.data("question") || "",
			question: $card.find(".mcq-stem").val(),
			options,
			concept: $card.find(".mcq-concept").val(),
			difficulty: $card.find(".mcq-difficulty").val(),
			source_reference: $card.find(".mcq-source").val(),
			learning_objective: $card.find(".mcq-objective").val(),
		};
	}

	$root.on("change", ".module-select", function () {
		const previous = state.tree && state.tree.learning_module;
		confirmLeave().then((ok) => {
			if (!ok) {
				if (previous) $root.find(".module-select").val(previous);
				return;
			}
			localStorage.setItem(MODULE_KEY, selectedModule() || "");
			state.bundle = null;
			return loadTree().then(renderMain);
		});
	});
	$root.on("click", ".btn-refresh", function () {
		confirmLeave().then((ok) => {
			if (!ok) return;
			const current = state.bundle && state.bundle.name;
			return loadTree().then(() => {
				if (current) return openChapter(current, { force: true });
				renderMain();
			});
		});
	});
	$root.on("input", ".chapter-filter", function () {
		state.chapterQuery = $(this).val() || "";
		renderChapters();
		$root.find(".chapter-filter").focus();
		const el = $root.find(".chapter-filter")[0];
		if (el) el.setSelectionRange(el.value.length, el.value.length);
	});
	$root.on("click", ".btn-chapter-filter", function () {
		state.chapterFilter = $(this).data("filter") || "all";
		renderChapters();
	});
	$root.on("input", ".item-filter", function () {
		state.itemQuery = ($(this).val() || "").toLowerCase();
		$root.find(".mcq-list .mcq-card, .card-list .flashcard-card").each(function () {
			const text = $(this).text().toLowerCase();
			$(this).toggle(!state.itemQuery || text.indexOf(state.itemQuery) !== -1);
		});
	});
	$root.on("click", ".btn-expand-item", function () {
		const $card = $(this).closest(".mcq-card");
		const id = $card.data("question") || $card.data("card") || "";
		state.expandedItem = $card.hasClass("is-collapsed") ? id : "";
		$root.find(".mcq-card").addClass("is-collapsed");
		if (state.expandedItem) $card.removeClass("is-collapsed");
	});
	$root.on("click", ".btn-collapse-all", function () {
		state.expandedItem = "";
		$root.find(".mcq-card").addClass("is-collapsed");
	});
	$root.on("click", ".btn-add-option", function () {
		const $card = $(this).closest(".mcq-card");
		if ($card.find(".option-row").length >= 10) {
			frappe.show_alert({ message: __("Each MCQ can have at most 10 options."), indicator: "orange" });
			return;
		}
		$card.find(".option-host").append(optionRowHtml({ text: "", is_correct: 0, explanation: "" }, 0, $card.data("question") || "new"));
		reindexOptions($card);
		$card.addClass("dirty");
		setStatus(__("Unsaved MCQ edits"), true);
	});
	$root.on("click", ".btn-remove-option", function () {
		const $card = $(this).closest(".mcq-card");
		if ($card.find(".option-row").length <= 2) {
			frappe.show_alert({ message: __("Each MCQ needs at least 2 options."), indicator: "orange" });
			return;
		}
		$(this).closest(".option-row").remove();
		reindexOptions($card);
		$card.addClass("dirty");
		setStatus(__("Unsaved MCQ edits"), true);
	});
	$root.on("input change", ".mcq-card :input, .flashcard-card :input", function () {
		$(this).closest(".mcq-card").addClass("dirty");
		setStatus(__("Unsaved edits"), true);
	});
	$root.on("input", ".chapter-heading", function () {
		state.headingDirty = true;
		setStatus(__("Unsaved heading"), true);
	});
	$root.on("click", ".chapter-btn", function () {
		const profile = $(this).data("profile");
		if (state.bundle && state.bundle.name === profile) return;
		openChapter(profile);
	});
	$root.on("click", ".btn-move-chapter", function (event) {
		event.preventDefault();
		event.stopPropagation();
		const profile = $(this).data("profile");
		const direction = $(this).data("dir");
		studioCall({
			method: "aimaticlearning.lms_learning.content_studio.reorder_studio_chapter",
			args: { chapter_profile: profile, direction },
			freeze: true,
			callback: (r) => {
				if (r.message && r.message.changed === false) {
					frappe.show_alert({ message: __("Already at the end of the outline."), indicator: "blue" });
					return;
				}
				loadTree();
			},
		});
	});
	$root.on("click", ".btn-tab", function () {
		const next = $(this).data("tab");
		if (next === state.tab) return;
		confirmDiscardItemEdits().then((ok) => {
			if (!ok) return;
			if (state.notesControl && state.bundle) {
				captureNotesSelection();
				state.bundle.notes_html = currentNotes();
			}
			state.tab = next;
			state.itemQuery = "";
			showActivePane();
		});
	});
	$root.on("click", ".btn-save-heading", function () {
		saveHeading();
	});
	$root.on("click", ".btn-remove-chapter", function () {
		if (!state.bundle) return;
		const heading = state.bundle.chapter_title || "";
		frappe.prompt(
			[
				{
					fieldtype: "HTML",
					options: `<p>${__(
						"This removes the chapter from the learner outline and retires its flashcards. MCQ records stay in the question bank, unlinked from this chapter quiz. Type the heading to confirm."
					)}</p>`,
				},
				{
					fieldname: "confirm_title",
					label: __("Type {0}").replace("{0}", heading),
					fieldtype: "Data",
					reqd: 1,
				},
			],
			(values) => {
				studioCall({
					method: "aimaticlearning.lms_learning.content_studio.remove_studio_chapter",
					args: {
						chapter_profile: state.bundle.name,
						confirm_title: values.confirm_title,
					},
					freeze: true,
					freeze_message: __("Removing chapter"),
					callback: (r) => {
						const moved = r.message && r.message.moved_assessment;
						frappe.show_alert({
							message: moved
								? __("Chapter removed. Module assessment moved to another chapter.")
								: __("Chapter removed from this subject."),
							indicator: "green",
						});
						state.bundle = null;
						state.notesControl = null;
						loadTree().then(renderMain);
					},
				});
			},
			__("Remove chapter")
		);
	});
	$root.on("keydown", ".chapter-heading", function (event) {
		if (event.key === "Enter") {
			event.preventDefault();
			saveHeading();
		}
	});
	function saveHeading() {
		if (!state.bundle) return;
		const chapter_title = ($root.find(".chapter-heading").val() || "").trim();
		studioCall({
			method: "aimaticlearning.lms_learning.content_studio.save_chapter_heading",
			args: {
				chapter_profile: state.bundle.name,
				chapter_title,
			},
			freeze: true,
			freeze_message: __("Renaming chapter"),
			callback: (r) => {
				const result = r.message || {};
				const extra = result.notes_heading_updated
					? __(" Matching heading in the notes was updated.")
					: "";
				frappe.show_alert({
					message: (result.changed ? __("Chapter renamed.") : __("Chapter heading unchanged.")) + extra,
					indicator: "green",
				});
				if (result.notes_heading_updated) {
					openChapter(state.bundle.name, { force: true }).then(loadTree);
					return;
				}
				if (state.bundle) state.bundle.chapter_title = chapter_title;
				state.savedHeading = chapter_title;
				state.headingDirty = false;
				updateHeaderMeta();
				loadTree();
				if (!isDirty()) setStatus(__("Saved"), false);
			},
		});
	}
	$root.on("click", ".btn-save-notes", function () {
		if (!state.bundle || !state.notesControl) return;
		studioCall({
			method: "aimaticlearning.lms_learning.content_studio.save_chapter_notes",
			args: {
				chapter_profile: state.bundle.name,
				notes_html: sanitizeNotesHtml(state.notesControl.get_value()),
			},
			freeze: true,
			freeze_message: __("Saving notes"),
			callback: (r) => {
				const result = r.message || {};
				if (result.skipped_quiz_lesson) {
					frappe.show_alert({
						message: __("Notes saved on the profile, but not onto a quiz-wired lesson."),
						indicator: "orange",
					});
				} else {
					frappe.show_alert({ message: __("Notes saved"), indicator: "green" });
				}
				if (state.bundle && result.source_revision != null) {
					state.bundle.source_revision = result.source_revision;
				}
				if (state.bundle && result.notes_status) {
					state.bundle.notes_status = result.notes_status;
					state.bundle.notes_status_label = result.notes_status_label;
					state.bundle.notes_in_sync = result.notes_in_sync;
					state.bundle.notes_html = sanitizeNotesHtml(state.notesControl.get_value());
					state.bundle.learner_notes_html = state.bundle.notes_html;
					state.bundle.notes_studio_chars = state.bundle.notes_html.length;
					state.bundle.notes_learner_chars = state.bundle.notes_html.length;
				}
				markSaved();
				updateHeaderMeta();
				loadTree().then(() => {
					const $pane = $root.find(".pane-notes");
					if ($pane.length && state.tab === "notes") renderNotes($pane);
				});
			},
		});
	});
	$root.on("click", ".btn-sync-to-learner", function () {
		if (!state.bundle) return;
		const run = function () {
			studioCall({
				method: "aimaticlearning.lms_learning.content_studio.sync_notes_to_learner",
				args: { chapter_profile: state.bundle.name },
				freeze: true,
				freeze_message: __("Publishing notes to learner"),
				callback: () => {
					frappe.show_alert({ message: __("Learner notes updated from Studio copy"), indicator: "green" });
					openChapter(state.bundle.name, { force: true }).then(loadTree);
				},
			});
		};
		if (notesDirty()) {
			frappe.confirm(__("Save Studio notes first, then sync? Unsaved editor text is not used by Sync."), () => {
				$root.find(".btn-save-notes").click();
			});
			return;
		}
		run();
	});
	$root.on("click", ".btn-pull-learner", function () {
		if (!state.bundle) return;
		const run = function () {
			studioCall({
				method: "aimaticlearning.lms_learning.content_studio.pull_learner_notes_to_studio",
				args: { chapter_profile: state.bundle.name },
				freeze: true,
				freeze_message: __("Pulling learner notes"),
				callback: () => {
					frappe.show_alert({ message: __("Studio copy replaced with learner notes"), indicator: "green" });
					openChapter(state.bundle.name, { force: true }).then(loadTree);
				},
			});
		};
		if (notesDirty() || state.notesEdited) {
			frappe.confirm(__("Discard unsaved Studio edits and pull learner notes?"), run);
			return;
		}
		frappe.confirm(__("Replace Studio working copy with the learner-published notes?"), run);
	});
	$root.on("click", ".btn-add-mcq", function () {
		const $host = $root.find(".mcq-new");
		$host.removeAttr("hidden").empty().append(mcqCard(emptyQuestion(), 0, false));
	});
	$root.on("click", ".btn-save-mcq", function () {
		if (!state.bundle) return;
		const payload = readMcqCard($(this).closest(".mcq-card"));
		studioCall({
			method: "aimaticlearning.lms_learning.content_studio.save_chapter_mcq",
			args: {
				chapter_profile: state.bundle.name,
				lms_question: payload.lms_question,
				question: payload.question,
				options: payload.options,
				concept: payload.concept,
				difficulty: payload.difficulty,
				source_reference: payload.source_reference,
				learning_objective: payload.learning_objective,
			},
			freeze: true,
			freeze_message: __("Saving MCQ"),
			callback: (r) => {
				frappe.show_alert({ message: __("MCQ saved"), indicator: "green" });
				state.tab = "mcqs";
				const savedName = (r.message && r.message.lms_question) || payload.lms_question;
				refreshOpenChapter({ keepNotes: true, expand: savedName, status: __("Saved") });
			},
		});
	});
	$root.on("click", ".btn-unlink-mcq", function () {
		if (!state.bundle) return;
		const $card = $(this).closest(".mcq-card");
		const lms_question = $card.data("question");
		frappe.confirm(__("Remove this question from the chapter quiz? The question record is kept."), () => {
			studioCall({
				method: "aimaticlearning.lms_learning.content_studio.unlink_chapter_mcq",
				args: {
					chapter_profile: state.bundle.name,
					lms_question,
				},
				freeze: true,
				callback: () => {
					frappe.show_alert({ message: __("Removed from chapter quiz"), indicator: "green" });
					state.tab = "mcqs";
					refreshOpenChapter({ keepNotes: true, status: __("Saved") });
				},
			});
		});
	});
	$root.on("click", ".btn-add-course", function () {
		frappe.prompt(
			[
				{
					fieldname: "title",
					label: __("Course title"),
					fieldtype: "Data",
					reqd: 1,
				},
				{
					fieldname: "short_introduction",
					label: __("Short introduction"),
					fieldtype: "Small Text",
				},
			],
			(values) => {
				studioCall({
					method: "aimaticlearning.lms_learning.content_studio.add_studio_course",
					args: values,
					freeze: true,
					freeze_message: __("Creating course"),
					callback: (r) => {
						const moduleName = r.message && r.message.learning_module;
						frappe.show_alert({
							message: __("Course created unpublished. Add chapters in this window."),
							indicator: "green",
						});
						loadModules().then(() => {
							if (moduleName) {
								$root.find(".module-select").val(moduleName);
								state.bundle = null;
								return loadTree().then(renderMain);
							}
						});
					},
				});
			},
			__("Add course")
		);
	});
	$root.on("click", ".btn-add-chapter", function () {
		const learning_module = selectedModule();
		if (!learning_module) {
			frappe.msgprint(__("Pick a subject first."));
			return;
		}
		frappe.prompt(
			[
				{
					fieldname: "chapter_title",
					label: __("Chapter heading"),
					fieldtype: "Data",
					reqd: 1,
				},
				{
					fieldname: "outline_idx",
					label: __("Student position"),
					fieldtype: "Int",
					default: ((state.tree && state.tree.chapters) || []).length + 1,
					description: __("1 is the first chapter learners see."),
				},
			],
			(values) => {
				studioCall({
					method: "aimaticlearning.lms_learning.content_studio.add_studio_chapter",
					args: {
						learning_module,
						chapter_title: values.chapter_title,
						outline_idx: values.outline_idx,
					},
					freeze: true,
					freeze_message: __("Creating chapter"),
					callback: (r) => {
						const profile = r.message && r.message.chapter_profile;
						frappe.show_alert({ message: __("Chapter added"), indicator: "green" });
						loadTree().then(() => {
							if (profile) return openChapter(profile);
						});
					},
				});
			},
			__("Add chapter")
		);
	});
	$root.on("click", ".btn-quote-from-notes", function () {
		const $card = $(this).closest(".flashcard-card");
		captureNotesSelection();
		const quote = (state.notesSelection || "").trim();
		if (!quote) {
			frappe.show_alert({
				message: __("Select a sentence in Notes first, then use it as the source quote."),
				indicator: "orange",
			});
			return;
		}
		$card.find(".card-quote").val(quote);
		$card.addClass("dirty");
		setStatus(__("Unsaved card edits"), true);
	});
	$root.on("click", ".btn-add-card", function () {
		const $host = $root.find(".card-new");
		$host.removeAttr("hidden").empty().append(flashcardForm(emptyCard(), 0, false));
	});
	$root.on("click", ".btn-save-card", function () {
		if (!state.bundle) return;
		const payload = readCard($(this).closest(".flashcard-card"));
		studioCall({
			method: "aimaticlearning.lms_learning.content_studio.save_flashcard",
			args: {
				chapter_profile: state.bundle.name,
				name: payload.name,
				front: payload.front,
				back: payload.back,
				concept: payload.concept,
				difficulty: payload.difficulty,
				source_reference: payload.source_reference,
				source_quote: payload.source_quote,
				status: payload.status,
			},
			freeze: true,
			freeze_message: __("Saving card"),
			callback: (r) => {
				frappe.show_alert({ message: __("Flashcard saved"), indicator: "green" });
				state.tab = "cards";
				const savedName = (r.message && r.message.name) || payload.name;
				refreshOpenChapter({ keepNotes: true, expand: savedName, status: __("Saved") });
			},
		});
	});

	$root.on("click", ".btn-move-mcq", function () {
		if (!state.bundle) return;
		const $card = $(this).closest(".mcq-card");
		const lms_question = $card.data("question");
		const direction = $(this).data("dir");
		const moveMcq = function () {
			studioCall({
				method: "aimaticlearning.lms_learning.content_studio.reorder_chapter_mcq",
				args: {
					chapter_profile: state.bundle.name,
					lms_question,
					direction,
				},
				freeze: true,
				callback: (r) => {
					if (r.message && r.message.changed === false) {
						frappe.show_alert({ message: __("Already at the end of the quiz."), indicator: "blue" });
						return;
					}
					state.tab = "mcqs";
					refreshOpenChapter({ keepNotes: true, expand: lms_question });
				},
			});
		};
		if ($card.hasClass("dirty")) {
			confirmUnsaved(__("This question has unsaved edits.")).then((ok) => {
				if (ok) moveMcq();
			});
			return;
		}
		moveMcq();
	});
	$root.on("click", ".btn-duplicate-mcq", function () {
		if (!state.bundle) return;
		const lms_question = $(this).closest(".mcq-card").data("question");
		frappe.confirm(__("Add a copy of this question to the chapter quiz? Edit the copy before learners sit it."), () => {
			studioCall({
				method: "aimaticlearning.lms_learning.content_studio.duplicate_chapter_mcq",
				args: {
					chapter_profile: state.bundle.name,
					lms_question,
				},
				freeze: true,
				freeze_message: __("Duplicating question"),
				callback: (r) => {
					frappe.show_alert({ message: __("Copy added to the chapter quiz"), indicator: "green" });
					state.tab = "mcqs";
					const copyName = r.message && r.message.lms_question;
					refreshOpenChapter({ keepNotes: true, expand: copyName, status: __("Saved") });
				},
			});
		});
	});

	function saveActivePane() {
		if (!state.bundle) return;
		if (document.activeElement && $(document.activeElement).hasClass("chapter-heading")) {
			saveHeading();
			return;
		}
		if (state.tab === "notes") {
			$root.find(".btn-save-notes").click();
			return;
		}
		const $dirty = $root.find(".mcq-card.dirty:not(.is-collapsed)").first();
		if ($dirty.length) {
			$dirty.find(".btn-save-mcq, .btn-save-card").first().click();
			return;
		}
		const $open = $root.find(".mcq-card:not(.is-collapsed)").first();
		if ($open.length) {
			$open.find(".btn-save-mcq, .btn-save-card").first().click();
		}
	}

	function bindStudioGuards() {
		$(document).off("keydown.aimaticStudio").on("keydown.aimaticStudio", function (event) {
			if (!(event.ctrlKey || event.metaKey) || event.key.toLowerCase() !== "s") return;
			if (!$(".aimatic-content-studio").length) return;
			event.preventDefault();
			saveActivePane();
		});
		$(window).off("beforeunload.aimaticStudio").on("beforeunload.aimaticStudio", function (event) {
			if (!isDirty()) return;
			event.preventDefault();
			event.returnValue = "";
		});
	}

	function unbindStudioGuards() {
		$(document).off("keydown.aimaticStudio");
		$(window).off("beforeunload.aimaticStudio");
	}

	bindStudioGuards();
	$(wrapper).off("hide.aimaticStudio show.aimaticStudio");
	$(wrapper).on("hide.aimaticStudio", unbindStudioGuards);
	$(wrapper).on("show.aimaticStudio", function () {
		window.cur_frm = null;
		bindStudioGuards();
	});

	loadModules();
};
