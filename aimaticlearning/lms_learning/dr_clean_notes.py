"""One-off cleanup of Dispute Resolution study notes (module LMOD-00553).

Removes non-substantive sections (chapter summaries, glossaries, key terms/points,
embedded MCQ / answer-key / self-assessment blocks) from Course Lesson.body and
Learning Chapter Profile.notes_html. Mirrors clean_contract_notes.py.
Run with `bench --site lms.aimatic.tech execute`.
"""

import json
import os
import re
from datetime import datetime

import frappe
from bs4 import BeautifulSoup

MODULE = "LMOD-00553"
COURSE = "dispute-resolution"

SKIP_LESSON_TITLE = re.compile(r"chapter\s*mcq|flashcard|module\s*assessment", re.I)

JUNK_HEADING = re.compile(
	r"""^\s*(
		(chapter\s+)?summary(\s+of\s+.*)?
		|summary\s*(&|and)\s*key\s*points?
		|glossary(\s+of\s+terms)?
		|key\s*terms?
		|key\s*(study\s*)?points?
		|key\s*takeaways?
		|takeaways?
		|self[\s-]*assessment.*
		|check\s+your\s+understanding.*
		|test\s+yourself.*
		|answer\s*key.*
		|answers?\s*(and\s*explanations?)?
		|(embedded\s+)?(mcqs?|multiple[\s-]choice\s+questions?).*
		|practice\s+(questions?|mcqs?).*
		|quiz.*
		|revision\s+(tips?|checklist).*
		|conclusion
	)\s*[:.]?\s*$""",
	re.I | re.X,
)

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

# Safety cap: real chapter-summary / glossary / key-terms / self-assessment blocks
# in these notes run at most a few hundred to ~2500 chars. If a candidate junk
# block would remove more than this, it is almost certainly a false positive
# (e.g. a bare intro paragraph in a chapter with no further heading tags to
# bound it) — skip removal instead of risking wiping the whole chapter.
MAX_JUNK_BLOCK_CHARS = 3000


def _heading_text(tag):
	return re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip()


def _plain_len(nodes) -> int:
	total = 0
	for node in nodes:
		getter = getattr(node, "get_text", None)
		total += len(getter(" ", strip=True)) if getter else len(str(node))
	return total


def clean_html(html: str):
	"""Return (cleaned_html, removed_section_labels, skipped_oversized_labels)."""
	if not html or not html.strip():
		return html, [], []

	soup = BeautifulSoup(html, "html.parser")
	removed = []
	skipped = []
	rejected_ids = set()

	while True:
		target = None
		for tag in soup.find_all(list(HEADING_TAGS)):
			if id(tag) in rejected_ids:
				continue
			if JUNK_HEADING.match(_heading_text(tag)):
				target = tag
				break
		if target is None:
			break

		level = int(target.name[1])
		label = _heading_text(target)
		doomed = [target]
		for sib in target.next_siblings:
			name = getattr(sib, "name", None)
			if name in HEADING_TAGS and int(name[1]) <= level:
				break
			doomed.append(sib)

		if _plain_len(doomed) > MAX_JUNK_BLOCK_CHARS:
			rejected_ids.add(id(target))
			skipped.append(f"<h{level}> {label} (oversized, {_plain_len(doomed)} chars)")
			continue

		for node in doomed:
			node.extract()
		removed.append(f"<h{level}> {label}")

	# Trailing pseudo-headings: bold/strong-only paragraphs used as section titles.
	# Never treat the very first content block of the document as a junk heading —
	# that is the chapter's own opening title in notes with no true <h*> tags.
	root = soup.find("article") or soup
	children = [c for c in root.children if getattr(c, "name", None)]
	rejected_p_ids = set()
	idx = 0
	while idx < len(children):
		node = children[idx]
		if idx == 0:
			idx += 1
			continue
		if node.name == "p" and id(node) not in rejected_p_ids:
			text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
			only_strong = bool(node.find(["strong", "b"])) and len(text) <= 80
			if (only_strong or len(text) <= 60) and JUNK_HEADING.match(text):
				doomed = [node]
				for sib in children[idx + 1 :]:
					if sib.name in HEADING_TAGS:
						break
					sib_text = re.sub(r"\s+", " ", sib.get_text(" ", strip=True)).strip()
					if sib.name == "p" and len(sib_text) <= 80 and JUNK_HEADING.match(sib_text):
						break
					doomed.append(sib)

				if _plain_len(doomed) > MAX_JUNK_BLOCK_CHARS:
					rejected_p_ids.add(id(node))
					skipped.append(f"<p> {text} (oversized, {_plain_len(doomed)} chars)")
					idx += 1
					continue

				for n in doomed:
					n.extract()
				removed.append(f"<p> {text}")
				children = [c for c in root.children if getattr(c, "name", None)]
				idx = 0
				continue
		idx += 1

	return str(soup), removed, skipped


def _chapter_no(title):
	m = re.search(r"(\d+)", title or "")
	return int(m.group(1)) if m else 999


def _targets():
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": MODULE},
		fields=["name", "chapter_title", "notes_lesson", "course_chapter"],
		order_by="creation asc",
	)
	rows = []
	for p in profiles:
		if not p.notes_lesson:
			rows.append((p, None))
			continue
		lesson = frappe.db.get_value(
			"Course Lesson", p.notes_lesson, ["name", "title", "course", "body", "content", "quiz_id"], as_dict=True
		)
		rows.append((p, lesson))
	rows.sort(key=lambda r: _chapter_no(r[0].chapter_title))
	return rows


def run(apply=False):
	apply = str(apply).lower() in ("1", "true", "yes")
	rows = _targets()
	report = []
	backup = {}

	for profile, lesson in rows:
		entry = {"profile": profile.name, "chapter": profile.chapter_title}

		if not lesson:
			entry["skipped"] = "no notes lesson linked"
			report.append(entry)
			continue
		if lesson.course != COURSE:
			entry["skipped"] = f"lesson belongs to course {lesson.course}"
			report.append(entry)
			continue
		if SKIP_LESSON_TITLE.search(lesson.title or ""):
			entry["skipped"] = f"activity lesson: {lesson.title}"
			report.append(entry)
			continue
		if lesson.quiz_id:
			entry["skipped"] = f"quiz-wired lesson (quiz_id={lesson.quiz_id})"
			report.append(entry)
			continue

		body = lesson.body or ""
		notes_html = frappe.db.get_value("Learning Chapter Profile", profile.name, "notes_html") or ""

		new_body, removed_body, skipped_body = clean_html(body)
		new_notes, removed_notes, skipped_notes = clean_html(notes_html)

		entry.update(
			{
				"lesson": lesson.name,
				"lesson_title": lesson.title,
				"body_before": len(body),
				"body_after": len(new_body),
				"notes_html_before": len(notes_html),
				"notes_html_after": len(new_notes),
				"removed": sorted(set(removed_body) | set(removed_notes)),
				"skipped_oversized": sorted(set(skipped_body) | set(skipped_notes)),
				"content_len": len(lesson.content or ""),
			}
		)

		if apply and (new_body != body or new_notes != notes_html):
			backup[profile.name] = {
				"lesson": lesson.name,
				"body": body,
				"notes_html": notes_html,
				"content": lesson.content,
			}
			frappe.db.set_value(
				"Course Lesson", lesson.name, {"body": new_body, "content": ""}, update_modified=True
			)
			frappe.db.set_value(
				"Learning Chapter Profile", profile.name, "notes_html", new_notes, update_modified=True
			)
			entry["written"] = True
		else:
			entry["written"] = False

		report.append(entry)

	if apply:
		stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
		path = os.path.join("/tmp", f"dispute-resolution-notes-backup-{stamp}.json")
		with open(path, "w") as fh:
			json.dump(backup, fh, indent=1)
		frappe.db.commit()
		print(f"BACKUP: {path}")

	print(json.dumps(report, indent=1))

	total_before = sum(e.get("body_before", 0) for e in report)
	total_after = sum(e.get("body_after", 0) for e in report)
	print(f"\nTOTAL body {total_before} -> {total_after} (removed {total_before - total_after} chars)")
	print("APPLIED" if apply else "DRY RUN — nothing written")


def dry_run():
	run(apply=False)


def apply_changes():
	run(apply=True)


def verify():
	rows = _targets()
	bad = 0
	for profile, lesson in rows:
		if not lesson:
			continue
		body = lesson.body or ""
		notes = frappe.db.get_value("Learning Chapter Profile", profile.name, "notes_html") or ""
		match = body == notes
		leftovers = [
			_heading_text(t)
			for t in BeautifulSoup(body, "html.parser").find_all(list(HEADING_TAGS))
			if JUNK_HEADING.match(_heading_text(t))
		]
		closed = body.count("<article") == body.count("</article>")
		if not match or leftovers or not closed or (lesson.content or ""):
			bad += 1
		print(
			f"{profile.chapter_title} | body={len(body)} notes_html={len(notes)} identical={match} "
			f"content_empty={not (lesson.content or '')} article_balanced={closed} leftovers={leftovers}"
		)
	print("PROBLEMS:", bad)
