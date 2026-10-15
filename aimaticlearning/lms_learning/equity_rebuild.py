"""Rebuild Equity and Trust Law to the six chapters of its Word source.

The live course was split into eight chapters and its notes reworded by an
unrecorded session (13-14 October 2026). This module restores the source
structure without losing learner progress:

* six existing Course Chapters are reused (titles changed, names and lesson
  names kept); the two surplus chapters are removed through Content Studio's
  chapter removal after their flashcards and question tags are moved;
* notes lessons get the source notes verbatim, with each chapter's summary and
  glossary moved to the Module Assessment revision lesson and the embedded MCQ,
  answer and self-assessment sections left out;
* chapter quizzes hold exactly the source's 20 questions per chapter, reusing
  existing LMS Questions (shared with mocks) and creating only the missing ones;
* the retired 8-section source File row is removed and the module points to
  the six-chapter source.

``dry_run`` writes nothing. ``apply`` snapshots every touched field first;
``rollback`` restores that snapshot.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import frappe
from docx import Document
from docx.table import Table

from aimaticlearning.lms_learning.content_format import (
	clean_text,
	iter_docx_blocks,
	paragraph_kind,
	render_content_blocks,
	render_table_html,
)

COURSE = "equity-and-trust-law"
SOURCE_FILE = "EQUITY AND TRUSTSd306bc.docx"
SOURCE_FILE_ID = "bed22e0354"
RETIRED_FILE_ID = "7e662d8062"  # "Eq nd trust.docx", the 8-section source, no longer on disk
MODULE = "LMOD-01110"
MODULE_CHAPTER = "8861 Module Assessment"

# Source chapter number -> existing Course Chapter reused for it.
CHAPTER_MAP = {
	1: "1111 Chapter 1: Foundations Of English Trust Law",
	2: "1115 Chapter 3: Constitution Of Trusts",
	3: "1113 Chapter 2: Requirements For A Valid Trust",
	4: "1121 Chapter 6: Resulting And Constructive Trusts",
	5: "1117 Chapter 4: Trustees' Duties And Powers",
	6: "1119 Chapter 5: Breach Of Trust And Remedies",
}
# Chapters whose content now lives inside a reused chapter above; removed.
DETACHED = {
	"1123 Chapter 7: Charitable Trusts": 3,
	"1125 Chapter 8: Variation Of Trusts": 4,
}

_TITLE_RE = re.compile(r"^(?:EQUITY AND TRUSTS:\s*)?CHAPTER\s+(\d)\s*(?::\s*(.*))?$", re.I)
_MCQ_HEAD_RE = re.compile(r"^(?:CHAPTER\s+\d\s*:?\s*)?MULTIPLE CHOICE QUESTIONS FOR SQE1 PREPARATION$", re.I)
_QUESTION_RE = re.compile(r"^QUESTION\s+(\d+)$", re.I)
_ANSWER_RE = re.compile(r"^ANSWER\s+(\d+)\s*:\s*([A-E])\b\s*[.\-–—:]?\s*(.*)$", re.I)
_OPTION_RE = re.compile(r"(?:^|\s)([A-E])\.\s+")
_SNAPSHOT = "equity_rebuild_snapshot.json"


def source_path() -> Path:
	return Path(frappe.get_site_path("private", "files", SOURCE_FILE))


# ---------------------------------------------------------------- splitting


def split_source(path: Path | None = None) -> list[dict]:
	"""Split the Word file into six chapters of notes, summary and MCQ blocks."""
	document = Document(str(path or source_path()))
	chapters: list[dict] = []
	current = None
	region = None
	pending_title = False
	for block in iter_docx_blocks(document):
		if isinstance(block, Table):
			if current is not None and region != "mcq":
				current[region].append({"kind": "table", "html": render_table_html(block)})
			continue
		text = clean_text(block.text)
		if not text:
			continue
		match = _TITLE_RE.match(text)
		if match and not _MCQ_HEAD_RE.match(text):
			number = int(match.group(1))
			if current is None or number != current["number"]:
				current = {"number": number, "title": (match.group(2) or "").strip(), "notes": [], "summary": [], "mcq": []}
				chapters.append(current)
				region = "notes"
				pending_title = not current["title"]
				continue
			# Second "CHAPTER N" line for the same chapter opens its MCQ section.
			region = "mcq"
			continue
		if current is None:
			continue
		if pending_title:
			current["title"] = text
			pending_title = False
			continue
		if _MCQ_HEAD_RE.match(text):
			region = "mcq"
			continue
		if region != "mcq" and text.upper() == "SUMMARY AND GLOSSARY":
			region = "summary"
			continue
		if region == "mcq":
			current["mcq"].append(text)
			continue
		item = paragraph_kind(block)
		if item["kind"] != "empty":
			current[region].append(item)
	return chapters


def chapter_title(chapter: dict) -> str:
	return f"Chapter {chapter['number']}: {chapter['title']}"


def notes_html(chapter: dict) -> str:
	blocks = [{"kind": "heading", "text": chapter_title(chapter), "level": 2}, *chapter["notes"]]
	return render_content_blocks(_promote_headings(_strip_rules(blocks)))


_LETTERED = re.compile(r"^\([a-z]\)\s+[A-Z]")
_NUMBERED_LABEL = re.compile(r"^(?:Exception|Principle)\s+\d+:\s+[A-Z]")
_UPPER_QUESTION = re.compile(r"^\d+\.\s+[A-Z][A-Z0-9 ,'’:&()\-—]+\?$")


def _promote_headings(blocks: list[dict]) -> list[dict]:
	"""Promote section labels the generic detector missed so siblings match.

	The source styles every label as Normal text; the shared heuristic rejects
	labels ending in "?" or starting "(a)", leaving some sections as headings
	and their siblings as paragraphs.
	"""
	out = []
	for block in blocks:
		text = block.get("text", "")
		if block.get("kind") == "paragraph" and _is_label(text):
			block = {"kind": "heading", "text": text, "level": 3}
		out.append(block)
	return out


def _is_label(text: str) -> bool:
	if len(text) > 100 or text.endswith((".", ":", ";", ",")):
		return False
	if _LETTERED.match(text) or _NUMBERED_LABEL.match(text) or _UPPER_QUESTION.match(text):
		return True
	words = re.findall(r"[A-Za-z][A-Za-z'’-]*", text)
	if text.endswith("?") and 2 <= len(words) <= 6 and text[0].isupper():
		return True
	if not words or len(words) > 10 or not re.fullmatch(r"[A-Za-z0-9 '’,()\-?]+", text):
		return False
	title_case = sum(1 for word in words if word[0].isupper()) / len(words)
	return title_case >= 0.6


def revision_html(chapters: list[dict]) -> str:
	blocks: list[dict] = []
	for chapter in chapters:
		blocks.append({"kind": "heading", "text": chapter_title(chapter), "level": 2})
		blocks.extend(_strip_rules(chapter["summary"]))
	return render_content_blocks(blocks)


def _strip_rules(blocks: list[dict]) -> list[dict]:
	"""Drop Word's underscore separator lines; they carry no content."""
	return [b for b in blocks if not re.fullmatch(r"_+", b.get("text", "") or "_x")]


# -------------------------------------------------------------------- MCQs


def parse_mcqs(chapter: dict) -> list[dict]:
	"""Parse the chapter's source questions with options, key and explanation."""
	lines = chapter["mcq"]
	questions: dict[int, dict] = {}
	answers: dict[int, dict] = {}
	current_q = None
	current_a = None
	in_answers = False
	for line in lines:
		if re.fullmatch(r"_+", line):
			continue
		upper = line.upper()
		if upper.startswith("ANSWERS AND EXPLANATIONS"):
			in_answers = True
			current_q = None
			continue
		if upper.startswith("SELF-ASSESSMENT GUIDE"):
			break
		if in_answers:
			match = _ANSWER_RE.match(line)
			if match:
				current_a = {"key": match.group(2).upper(), "text": [match.group(3).strip()]}
				answers[int(match.group(1))] = current_a
			elif current_a is not None:
				current_a["text"].append(line)
			continue
		match = _QUESTION_RE.match(line)
		if match:
			current_q = {"number": int(match.group(1)), "stem": [], "options": {}}
			questions[current_q["number"]] = current_q
			continue
		if current_q is None or upper.startswith("INSTRUCTIONS:"):
			continue
		options = _split_options(line)
		if options:
			current_q["options"].update(options)
		elif current_q["options"]:
			# A wrapped option line continues the last option.
			last = sorted(current_q["options"])[-1]
			current_q["options"][last] += " " + line
		else:
			current_q["stem"].append(line)
	out = []
	for number in sorted(questions):
		q = questions[number]
		a = answers.get(number, {})
		explanation = " ".join(t for t in a.get("text", []) if t).strip()
		out.append(
			{
				"number": number,
				"stem": "\n".join(q["stem"]).strip(),
				"options": [q["options"].get(letter, "") for letter in "ABCDE"],
				"key": a.get("key"),
				"explanation": explanation,
			}
		)
	return out


def _split_options(line: str) -> dict[str, str] | None:
	if not re.match(r"^[A-E]\.\s+", line):
		return None
	parts = _OPTION_RE.split(" " + line)
	# parts: ['', 'A', 'text', 'B', 'text', ...]
	found = {}
	for i in range(1, len(parts) - 1, 2):
		found[parts[i]] = parts[i + 1].strip()
	letters = list(found)
	if letters != list("ABCDE")[: len(letters)]:
		return {letters[0]: line[3:].strip()} if len(letters) == 1 else None
	return found


def _norm(value: str | None) -> str:
	text = re.sub(r"<[^>]+>", " ", value or "")
	text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
	return re.sub(r"[^a-z0-9£]+", " ", text.lower()).strip()


def match_questions(source: list[dict]) -> list[dict]:
	"""Find each source question's existing LMS Question by stem."""
	rows = frappe.db.sql("select name, question from `tabLMS Question`", as_dict=True)
	index = {}
	for row in rows:
		index.setdefault(_norm(row.question)[:160], []).append(row.name)
	result = []
	for q in source:
		stem = _norm(q["stem"])[:160]
		names = index.get(stem) or [
			name for key, names in index.items() if key[:90] == stem[:90] for name in names
		]
		item = dict(q, matches=names)
		if len(names) == 1:
			doc = frappe.db.get_value("LMS Question", names[0], ["*"], as_dict=True)
			site_key = "".join("ABCDE"[k - 1] for k in range(1, 6) if doc.get(f"is_correct_{k}"))
			item["site_key"] = site_key
			item["option_diffs"] = [
				"ABCDE"[k - 1]
				for k in range(1, 6)
				if _norm(doc.get(f"option_{k}")) != _norm(q["options"][k - 1])
			]
		result.append(item)
	return result


# ----------------------------------------------------------------- dry run


def dry_run(out_dir: str | None = None) -> dict:
	"""Report the rebuild plan and write HTML/JSON previews. Writes no records."""
	path = source_path()
	chapters = split_source(path)
	report = {"source": str(path), "md5": hashlib.md5(path.read_bytes()).hexdigest(), "chapters": []}
	target = Path(out_dir or frappe.get_site_path("private", "equity_rebuild_preview"))
	target.mkdir(parents=True, exist_ok=True)
	for chapter in chapters:
		html = notes_html(chapter)
		(target / f"chapter_{chapter['number']}_notes.html").write_text(html)
		mcqs = match_questions(parse_mcqs(chapter))
		report["chapters"].append(
			{
				"number": chapter["number"],
				"title": chapter_title(chapter),
				"reuses": CHAPTER_MAP.get(chapter["number"]),
				"notes_words": len(re.sub(r"<[^>]+>", " ", html).split()),
				"summary_blocks": len(chapter["summary"]),
				"headings": [b["text"] for b in chapter["notes"] if b["kind"] == "heading"],
				"mcqs": [
					{
						"n": q["number"],
						"stem": q["stem"][:70],
						"source_key": q["key"],
						"options_parsed": sum(1 for o in q["options"] if o),
						"has_explanation": bool(q["explanation"]),
						"matches": q["matches"],
						"site_key": q.get("site_key"),
						"option_diffs": q.get("option_diffs"),
					}
					for q in mcqs
				],
			}
		)
	(target / "module_revision.html").write_text(revision_html(chapters))
	(target / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
	return report


def refresh_notes(confirm: str | None = None) -> dict:
	"""Re-render the six notes lessons and profiles from the source after apply."""
	if confirm != "refresh notes":
		frappe.throw('Pass confirm="refresh notes" to rewrite the notes.')
	updated = []
	for chapter in split_source():
		course_chapter = CHAPTER_MAP[chapter["number"]]
		html = notes_html(chapter)
		profile = frappe.get_doc("Learning Chapter Profile", {"course_chapter": course_chapter})
		frappe.db.set_value("Course Lesson", profile.notes_lesson, {"body": html, "content": ""})
		profile.notes_html = html
		profile.save(ignore_permissions=True)
		updated.append(profile.notes_lesson)
	frappe.db.commit()
	return {"updated": updated}


# -------------------------------------------------------------------- apply

def _snapshot_path() -> Path:
	return Path(frappe.get_site_path("private", _SNAPSHOT))


def _doc_dict(doctype: str, name: str) -> dict | None:
	if not frappe.db.exists(doctype, name):
		return None
	return json.loads(frappe.as_json(frappe.get_doc(doctype, name).as_dict()))


def _take_snapshot(plan: list[dict]) -> dict:
	snap: dict = {"docs": [], "flashcards": [], "meta": []}
	names: list[tuple[str, str]] = [("LMS Course", COURSE), ("Learning Module Config", MODULE), ("File", RETIRED_FILE_ID)]
	for chapter in [*CHAPTER_MAP.values(), *DETACHED, MODULE_CHAPTER]:
		names.append(("Course Chapter", chapter))
		for lesson in frappe.get_all("Course Lesson", filters={"chapter": chapter}, pluck="name"):
			names.append(("Course Lesson", lesson))
			quiz = frappe.db.get_value("Course Lesson", lesson, "quiz_id")
			if quiz:
				names.append(("LMS Quiz", quiz))
		for profile in frappe.get_all("Learning Chapter Profile", filters={"course_chapter": chapter}, pluck="name"):
			names.append(("Learning Chapter Profile", profile))
		for progress in frappe.get_all("LMS Course Progress", filters={"chapter": chapter}, pluck="name"):
			names.append(("LMS Course Progress", progress))
	for item in plan:
		for q in item["questions"]:
			if q.get("name"):
				names.append(("LMS Question", q["name"]))
	for doctype, name in dict.fromkeys(names):
		doc = _doc_dict(doctype, name)
		if doc:
			snap["docs"].append(doc)
	chapters = [*CHAPTER_MAP.values(), *DETACHED]
	snap["flashcards"] = frappe.get_all(
		"Learning Flashcard", filters={"course_chapter": ["in", chapters]}, fields=["name", "course_chapter", "status"]
	)
	snap["meta"] = frappe.get_all(
		"Learning Question Meta", filters={"learning_module": MODULE}, fields=["name", "course_chapter"]
	)
	return snap


def build_plan() -> tuple[list[dict], list[dict]]:
	"""Resolve every source chapter and question to its target record."""
	chapters = split_source()
	if [c["number"] for c in chapters] != [1, 2, 3, 4, 5, 6]:
		frappe.throw(f"Expected six source chapters, got {[c['number'] for c in chapters]}")
	plan = []
	for chapter in chapters:
		questions = match_questions(parse_mcqs(chapter))
		if len(questions) != 20:
			frappe.throw(f"Chapter {chapter['number']} has {len(questions)} source questions, expected 20")
		for q in questions:
			if len(q["matches"]) > 1:
				frappe.throw(f"Chapter {chapter['number']} Q{q['number']} matches several questions: {q['matches']}")
			q["name"] = q["matches"][0] if q["matches"] else None
			if q["name"] and q["site_key"] != q["key"]:
				frappe.throw(f"Chapter {chapter['number']} Q{q['number']} key differs: site {q['site_key']} source {q['key']}")
			if not q["name"] and (sum(1 for o in q["options"] if o) != 5 or not q["key"] or not q["explanation"]):
				frappe.throw(f"Chapter {chapter['number']} Q{q['number']} is incomplete in the source")
		plan.append({"chapter": chapter, "course_chapter": CHAPTER_MAP[chapter["number"]], "questions": questions})
	return chapters, plan


def apply(confirm: str | None = None) -> dict:
	"""Rebuild the course. Pass confirm="rebuild equity" to write."""
	if confirm != "rebuild equity":
		frappe.throw('Pass confirm="rebuild equity" to apply the rebuild.')
	from aimaticlearning.lms_learning import content_studio

	frappe.set_user("Administrator")
	chapters, plan = build_plan()
	path = _snapshot_path()
	if path.exists():
		frappe.throw(f"Snapshot {path} already exists; roll back or move it before re-applying.")
	path.write_text(json.dumps(_take_snapshot(plan), indent=1, ensure_ascii=False, default=str))

	md5 = hashlib.md5(source_path().read_bytes()).hexdigest()
	created = []
	for item in plan:
		chapter, course_chapter = item["chapter"], item["course_chapter"]
		title = chapter_title(chapter)
		html = notes_html(chapter)
		frappe.db.set_value("Course Chapter", course_chapter, "title", title)
		quiz_name = None
		for row in frappe.get_doc("Course Chapter", course_chapter).lessons:
			lesson = frappe.get_doc("Course Lesson", row.lesson)
			if lesson.quiz_id:
				quiz_name = lesson.quiz_id
				lesson.title = f"Chapter MCQ — {title}"
			elif "data-aimatic-flashcard-deck" in (lesson.body or ""):
				lesson.title = f"Flashcards — {title}"
			else:
				lesson.title = title
				lesson.body = html
				lesson.content = ""
			lesson.save(ignore_permissions=True)
		names = []
		for q in item["questions"]:
			if q["name"]:
				# Ch6 Q20 D is the one source option restored; other differing options are
				# UK spellings or half-finished working the site already cleaned up.
				if chapter["number"] == 6 and q["number"] == 20:
					frappe.db.set_value("LMS Question", q["name"], "option_4", q["options"][3])
				names.append(q["name"])
			else:
				names.append(_create_question(chapter, q, course_chapter))
				created.append(names[-1])
			_tag_question(names[-1], course_chapter, chapter, q)
		quiz = frappe.get_doc("LMS Quiz", quiz_name)
		quiz.title = f"{title} — Chapter MCQ"
		quiz.set("questions", [{"question": name, "marks": 1} for name in names])
		quiz.total_marks = len(names)
		quiz.save(ignore_permissions=True)
		profile = frappe.get_doc("Learning Chapter Profile", {"course_chapter": course_chapter})
		profile.chapter_title = title
		profile.notes_html = html
		profile.mcq_count = len(names)
		profile.source_revision = (profile.source_revision or 0) + 1
		profile.concept_tags = f"source:{SOURCE_FILE_ID} hash:{md5} locator:{title}"
		profile.save(ignore_permissions=True)

	# Move cards and question tags out of the two surplus chapters, then remove them.
	for old, number in DETACHED.items():
		target = CHAPTER_MAP[number]
		frappe.db.sql("update `tabLearning Flashcard` set course_chapter=%s where course_chapter=%s", (target, old))
		frappe.db.sql("update `tabLearning Question Meta` set course_chapter=%s where course_chapter=%s", (target, old))
		profile = frappe.db.get_value("Learning Chapter Profile", {"course_chapter": old}, "name")
		title = frappe.db.get_value("Course Chapter", old, "title")
		content_studio.remove_studio_chapter(profile, confirm_title=title)

	content_studio._write_course_outline(COURSE, [*(CHAPTER_MAP[n] for n in range(1, 7)), MODULE_CHAPTER])

	revision = frappe.db.get_value("Course Lesson", {"chapter": MODULE_CHAPTER, "quiz_id": ["is", "not set"]}, "name")
	frappe.db.set_value("Course Lesson", revision, {"body": revision_html(chapters), "content": ""})

	module = frappe.get_doc("Learning Module Config", MODULE)
	module.source_file = SOURCE_FILE_ID
	module.refresh_counts()
	module.save(ignore_permissions=True)
	if frappe.db.exists("File", RETIRED_FILE_ID):
		frappe.db.delete("File", {"name": RETIRED_FILE_ID})
	frappe.db.commit()
	return {"snapshot": str(path), "created_questions": created}


def _explanation(q: dict) -> str:
	"""Drop the answer line's restatement of the option text."""
	text = q["explanation"]
	option = q["options"]["ABCDE".index(q["key"])]
	if option and _norm(text).startswith(_norm(option)):
		text = text[len(option) :].lstrip(" .-–—")
	return text.strip()


def _create_question(chapter: dict, q: dict, course_chapter: str) -> str:
	key = "ABCDE".index(q["key"]) + 1
	values = {"doctype": "LMS Question", "question": q["stem"], "type": "Choices", "marks": 1}
	for k in range(1, 6):
		values[f"option_{k}"] = q["options"][k - 1]
		values[f"is_correct_{k}"] = 1 if k == key else 0
	values[f"explanation_{key}"] = _explanation(q)
	return frappe.get_doc(values).insert(ignore_permissions=True).name


def _tag_question(name: str, course_chapter: str, chapter: dict, q: dict) -> None:
	meta = frappe.db.get_value("Learning Question Meta", {"lms_question": name}, "name")
	if meta:
		frappe.db.set_value("Learning Question Meta", meta, "course_chapter", course_chapter)
		return
	frappe.get_doc(
		{
			"doctype": "Learning Question Meta",
			"lms_question": name,
			"learning_module": MODULE,
			"course_chapter": course_chapter,
			"concept": chapter_title(chapter),
			"difficulty": "Medium",
			"question_role": "Chapter MCQ",
			"source_reference": f"{SOURCE_FILE} Ch{chapter['number']} Q{q['number']}",
			"revision": 1,
			"ai_generated": 0,
		}
	).insert(ignore_permissions=True)


# ----------------------------------------------------------------- rollback


def rollback(confirm: str | None = None) -> dict:
	"""Restore the snapshot taken by ``apply``. Pass confirm="rollback equity"."""
	if confirm != "rollback equity":
		frappe.throw('Pass confirm="rollback equity" to restore the snapshot.')
	frappe.set_user("Administrator")
	path = _snapshot_path()
	snap = json.loads(path.read_text())
	order = ["File", "Course Chapter", "LMS Quiz", "Course Lesson", "Learning Chapter Profile", "LMS Course", "Learning Module Config", "LMS Question", "LMS Course Progress"]
	restored = 0
	for doctype in order:
		for data in (d for d in snap["docs"] if d["doctype"] == doctype):
			if frappe.db.exists(doctype, data["name"]):
				doc = frappe.get_doc(doctype, data["name"])
				doc.update({k: v for k, v in data.items() if k not in ("modified", "creation")})
				doc.flags.ignore_validate = True
				doc.save(ignore_permissions=True)
			else:
				doc = frappe.get_doc(data)
				doc.flags.ignore_validate = True
				doc.insert(ignore_permissions=True, ignore_links=True, ignore_if_duplicate=True, set_name=data["name"])
			restored += 1
	for row in snap["flashcards"]:
		frappe.db.set_value("Learning Flashcard", row["name"], {"course_chapter": row["course_chapter"], "status": row["status"]}, update_modified=False)
	for row in snap["meta"]:
		frappe.db.set_value("Learning Question Meta", row["name"], "course_chapter", row["course_chapter"], update_modified=False)
	frappe.db.commit()
	path.rename(path.with_suffix(".rolled-back.json"))
	return {"restored_docs": restored}
