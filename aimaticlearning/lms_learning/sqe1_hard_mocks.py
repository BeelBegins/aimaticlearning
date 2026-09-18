"""Assemble January 2027 SQE1 hard mock sittings from the reviewed 5-option bank.

Do not invent keys. Do not copy Kaplan. Do not reuse a question across sittings.
Quiz lessons keep EditorJS content empty.
"""

from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

import frappe
from frappe.utils import now_datetime

from aimaticlearning.lms_learning.outline_sync import (
	link_chapter_to_course,
	link_lesson_to_chapter,
	new_quiz_lesson_values,
)

COURSE_NAME = "sqe1-hard-mocks"
COURSE_TITLE = "SQE1 Hard Mocks (January 2027)"
DURATION_MINUTES = 153
PASSING_PERCENTAGE = 60
MAX_ATTEMPTS = 3
SHOW_ANSWERS = 0
LOBBY_URL = "/learning-mock-exam"
QUIZ_LESSON_BODY = (
	"<p>This is a timed January 2027 SQE1 session: 85 questions in 153 minutes. "
	"Do not refresh or close the window until you submit.</p>"
)

# SRA area -> Examic course(s). Criminal Liability has no 5-option course bank.
AREA_COURSES = {
	"blp": ("business-law-practice-blp",),
	"dr": ("dispute-resolution",),
	"legal_services": ("legal-services",),
	"tort": ("tort-law",),
	"contract": ("contract-law",),
	"legal_system": ("public-law",),
	"wills": ("wills-and-administration-of-estates",),
	"trusts": ("equity-and-trust-law",),
	"land": ("land-law",),
	"property": ("property-practice",),
	"accounts": ("solicitors-accounts",),
	"criminal_litigation": ("criminal-litigation",),
}

# Per-mock counts. Session 1 and 2 each sum to 85. All values sit in Annex 4.
FLK1_COUNTS = (
	{"blp": 33, "dr": 25, "legal_services": 27, "tort": 30, "contract": 28, "legal_system": 27},
	{"blp": 33, "dr": 25, "legal_services": 27, "tort": 30, "contract": 28, "legal_system": 27},
	{"blp": 34, "dr": 25, "legal_services": 26, "tort": 30, "contract": 29, "legal_system": 26},
)
FLK2_COUNTS = (
	{
		"wills": 21,
		"accounts_wills": 8,
		"trusts": 28,
		"land": 28,
		"property": 21,
		"accounts_property": 8,
		"criminal_liability": 28,
		"criminal_practice": 28,
	},
	{
		"wills": 21,
		"accounts_wills": 8,
		"trusts": 28,
		"land": 28,
		"property": 21,
		"accounts_property": 8,
		"criminal_liability": 28,
		"criminal_practice": 28,
	},
	{
		"wills": 21,
		"accounts_wills": 8,
		"trusts": 28,
		"land": 28,
		"property": 21,
		"accounts_property": 8,
		"criminal_liability": 28,
		"criminal_practice": 28,
	},
)

SESSION_AREAS = {
	"flk1_s1": ("blp", "dr", "legal_services"),
	"flk1_s2": ("tort", "contract", "legal_system"),
	"flk2_s1": ("wills", "accounts_wills", "trusts", "land"),
	"flk2_s2": ("property", "accounts_property", "criminal_liability", "criminal_practice"),
}

TAX_RE = re.compile(
	r"\b(income tax|corporation tax|capital gains|cgt|vat|inheritance tax|iht|sdlt|stamp duty|land transaction tax|ltt|business property relief|private residence relief)\b",
	re.I,
)
WALES_RE = re.compile(r"\b(wales|welsh|senedd|ltt|land transaction tax)\b", re.I)
ETHICS_RE = re.compile(
	r"\b(sra principle|code of conduct|professional conduct|integrity|confidential|conflict of interest|money laundering|aml|poca|slapp|nda)\b",
	re.I,
)
HARD_MARKERS = (
	"best advice",
	"most likely",
	"which of the following",
	"advise",
	"calculate",
	"client",
	"on the facts",
)


def _plain(text: str) -> str:
	return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


def hardness_key(row: dict) -> tuple:
	"""Hard tags first; 5-option bank is almost all Medium, so rank by application."""
	diff = (row.get("difficulty") or "Medium").title()
	rank = {"Hard": 0, "Medium": 1, "Easy": 2}.get(diff, 1)
	text = _plain(row.get("question") or "").lower()
	markers = sum(1 for token in HARD_MARKERS if token in text)
	return (rank, -markers, -len(text), row.get("name") or "")


def is_eligible(row: dict) -> bool:
	opts = [row.get(f"option_{i}") for i in range(1, 6)]
	if any(not (opt or "").strip() for opt in opts):
		return False
	correct = sum(int(row.get(f"is_correct_{i}") or 0) for i in range(1, 6))
	if correct != 1:
		return False
	if int(row.get("ai_generated") or 0):
		return False
	return True


def flag_text(row: dict) -> dict:
	blob = " ".join(
		[
			_plain(row.get("question") or ""),
			row.get("concept") or "",
			row.get("chapter_title") or "",
			row.get("source_reference") or "",
		]
	)
	return {
		"tax": bool(TAX_RE.search(blob)),
		"wales": bool(WALES_RE.search(blob)),
		"ethics_aml": bool(ETHICS_RE.search(blob)),
	}


def classify_accounts(row: dict) -> str:
	blob = f"{row.get('chapter_title') or ''} {row.get('concept') or ''}".lower()
	if "conveyanc" in blob or "completion" in blob or "exchange of contract" in blob:
		return "accounts_property"
	if any(token in blob for token in ("will", "estate", "probate", "executor", "intesta", "iht")):
		return "accounts_wills"
	if "chapter 8" in blob:
		return "accounts_property"
	return "accounts_generic"


def take_striped(pool: list[dict], counts: list[int]) -> list[list[dict]]:
	"""Deal hardest-first round-robin so each mock is hard, not Mock 1 only."""
	ordered = sorted(pool, key=hardness_key)
	buckets = [[] for _ in counts]
	need = list(counts)
	cursor = 0
	n = len(counts)
	for row in ordered:
		if sum(need) == 0:
			break
		for _ in range(n):
			if need[cursor] > 0:
				buckets[cursor].append(row)
				need[cursor] -= 1
				cursor = (cursor + 1) % n
				break
			cursor = (cursor + 1) % n
	for bucket, expected in zip(buckets, counts, strict=True):
		if len(bucket) != expected:
			raise ValueError(f"Needed {expected} items, striped {len(bucket)} from {len(pool)}")
	return buckets


def _swap_in_flag(bucket: list[dict], unused: list[dict], used: set[str], key: str) -> None:
	if any(flag_text(row)[key] for row in bucket):
		return
	chosen_ids = {row["name"] for row in bucket}
	candidate = next((row for row in unused if row["name"] not in chosen_ids and flag_text(row)[key]), None)
	if not candidate:
		return
	dropped = bucket[-1]["name"]
	bucket[-1] = candidate
	used.discard(dropped)
	used.add(candidate["name"])


def allocate(pools: dict[str, list[dict]]) -> dict:
	used: set[str] = set()

	def take(src: str, counts: list[int]) -> list[list[dict]]:
		available = [row for row in pools.get(src, []) if row["name"] not in used]
		if sum(counts) > len(available):
			raise ValueError(f"Pool {src} has {len(available)} items, need {sum(counts)}")
		buckets = take_striped(available, counts)
		for bucket in buckets:
			for row in bucket:
				used.add(row["name"])
		return buckets

	blp = take("blp", [c["blp"] for c in FLK1_COUNTS])
	dr = take("dr", [c["dr"] for c in FLK1_COUNTS])
	ls = take("legal_services", [c["legal_services"] for c in FLK1_COUNTS])
	tort = take("tort", [c["tort"] for c in FLK1_COUNTS])
	contract = take("contract", [c["contract"] for c in FLK1_COUNTS])
	legal_system = take("legal_system", [c["legal_system"] for c in FLK1_COUNTS])
	for idx in range(3):
		_swap_in_flag(blp[idx], [r for r in pools["blp"] if r["name"] not in used], used, "tax")

	wills = take("wills", [c["wills"] for c in FLK2_COUNTS])
	trusts = take("trusts", [c["trusts"] for c in FLK2_COUNTS])
	land = take("land", [c["land"] for c in FLK2_COUNTS])
	property_ = take("property", [c["property"] for c in FLK2_COUNTS])
	for idx in range(3):
		_swap_in_flag(wills[idx], [r for r in pools["wills"] if r["name"] not in used], used, "tax")
		_swap_in_flag(property_[idx], [r for r in pools["property"] if r["name"] not in used], used, "tax")

	accounts = [row for row in pools.get("accounts", []) if row["name"] not in used]
	property_acc = [row for row in accounts if classify_accounts(row) == "accounts_property"]
	wills_acc = [row for row in accounts if classify_accounts(row) == "accounts_wills"]
	generic_acc = [row for row in accounts if classify_accounts(row) == "accounts_generic"]
	acc_property_pool = property_acc + generic_acc
	taken_prop = take_striped(acc_property_pool, [c["accounts_property"] for c in FLK2_COUNTS])
	prop_ids = {row["name"] for bucket in taken_prop for row in bucket}
	for row_id in prop_ids:
		used.add(row_id)
	acc_wills_pool = [row for row in (wills_acc + generic_acc) if row["name"] not in used]
	taken_wills_acc = take_striped(acc_wills_pool, [c["accounts_wills"] for c in FLK2_COUNTS])
	for bucket in taken_wills_acc:
		for row in bucket:
			used.add(row["name"])

	crim = [row for row in pools.get("criminal_litigation", []) if row["name"] not in used]
	# No 5-option Criminal Law bank. Split hardest Criminal Litigation across
	# both criminal blueprint areas and flag the liability side as proxy.
	crim_sorted = sorted(crim, key=hardness_key)
	liability_pool = crim_sorted[0::2]
	practice_pool = crim_sorted[1::2]
	taken_cl = take_striped(liability_pool, [c["criminal_liability"] for c in FLK2_COUNTS])
	for bucket in taken_cl:
		for row in bucket:
			used.add(row["name"])
	practice_pool = [row for row in practice_pool + liability_pool if row["name"] not in used]
	taken_cp = take_striped(practice_pool, [c["criminal_practice"] for c in FLK2_COUNTS])

	papers = []
	for idx in range(3):
		papers.append(
			{
				"mock": idx + 1,
				"flk1": {
					"blp": blp[idx],
					"dr": dr[idx],
					"legal_services": ls[idx],
					"tort": tort[idx],
					"contract": contract[idx],
					"legal_system": legal_system[idx],
				},
				"flk2": {
					"wills": wills[idx],
					"accounts_wills": taken_wills_acc[idx],
					"trusts": trusts[idx],
					"land": land[idx],
					"property": property_[idx],
					"accounts_property": taken_prop[idx],
					"criminal_liability": taken_cl[idx],
					"criminal_practice": taken_cp[idx],
				},
			}
		)
	return {"papers": papers, "gaps": _gaps(pools, papers)}


def _gaps(pools: dict, papers: list) -> list[str]:
	gaps = [
		"Criminal Law has no 5-option reviewed items; FLK2 Criminal Liability is filled from Criminal Litigation as a proxy.",
		"Eligible Hard tags are all 4-option or AI-generated; hardness is Hard-then-Medium plus longer application stems.",
	]
	for area, need in (
		("dr", sum(c["dr"] for c in FLK1_COUNTS)),
		("legal_services", sum(c["legal_services"] for c in FLK1_COUNTS)),
		("legal_system", sum(c["legal_system"] for c in FLK1_COUNTS)),
	):
		have = len(pools.get(area, []))
		if have < need + 10:
			gaps.append(f"{area} pool is tight: {have} eligible for {need} selected.")
	return gaps


def session_rows(paper: dict, session: str) -> list[dict]:
	out = []
	for area in SESSION_AREAS[session]:
		for row in paper["flk1" if session.startswith("flk1") else "flk2"][area]:
			item = dict(row)
			item["sra_area"] = area
			item["session"] = session
			item["mock"] = paper["mock"]
			item.update(flag_text(row))
			if area == "criminal_liability":
				item["liability_proxy"] = True
			out.append(item)
	return out


def summarise(allocation: dict) -> dict:
	summary = {"mocks": [], "gaps": allocation["gaps"], "unique_questions": 0}
	seen = []
	for paper in allocation["papers"]:
		mock = {"mock": paper["mock"], "sessions": {}}
		for session in SESSION_AREAS:
			rows = session_rows(paper, session)
			seen.extend(row["name"] for row in rows)
			diff = {}
			for row in rows:
				diff[row.get("difficulty") or "Medium"] = diff.get(row.get("difficulty") or "Medium", 0) + 1
			areas = {}
			source = paper["flk1" if session.startswith("flk1") else "flk2"]
			for area in SESSION_AREAS[session]:
				areas[area] = len(source[area])
			mock["sessions"][session] = {
				"count": len(rows),
				"areas": areas,
				"difficulty": diff,
				"ethics_aml": sum(1 for row in rows if row.get("ethics_aml")),
				"tax": sum(1 for row in rows if row.get("tax")),
				"wales": sum(1 for row in rows if row.get("wales")),
			}
		summary["mocks"].append(mock)
	summary["unique_questions"] = len(set(seen))
	summary["duplicate"] = len(seen) != len(set(seen))
	return summary


def load_pools() -> dict[str, list[dict]]:
	rows = frappe.db.sql(
		"""
		SELECT
			q.name, q.question, q.option_1, q.option_2, q.option_3, q.option_4, q.option_5,
			q.is_correct_1, q.is_correct_2, q.is_correct_3, q.is_correct_4, q.is_correct_5,
			m.difficulty, m.ai_generated, m.concept, m.source_reference, m.learning_module,
			cfg.lms_course, IFNULL(ch.title, '') AS chapter_title
		FROM `tabLearning Question Meta` m
		INNER JOIN `tabLMS Question` q ON q.name = m.lms_question
		INNER JOIN `tabLearning Module Config` cfg ON cfg.name = m.learning_module
		LEFT JOIN `tabCourse Chapter` ch ON ch.name = m.course_chapter
		""",
		as_dict=True,
	)
	pools: dict[str, list[dict]] = {key: [] for key in AREA_COURSES}
	course_to_area = {}
	for area, courses in AREA_COURSES.items():
		for course in courses:
			course_to_area[course] = area
	for row in rows:
		if not is_eligible(row):
			continue
		area = course_to_area.get(row.lms_course)
		if not area:
			continue
		pools[area].append(dict(row))
	return pools


def dry_run() -> dict:
	allocation = allocate(load_pools())
	report = summarise(allocation)
	report["selection"] = {
		f"mock{paper['mock']}": {
			session: [row["name"] for row in session_rows(paper, session)]
			for session in SESSION_AREAS
		}
		for paper in allocation["papers"]
	}
	return report


def _ensure_course() -> str:
	existing = frappe.db.exists("LMS Course", COURSE_NAME) or frappe.db.get_value(
		"LMS Course", {"title": COURSE_TITLE}
	)
	if existing:
		course = frappe.get_doc("LMS Course", COURSE_NAME)
		course.title = COURSE_TITLE
		course.upcoming = 0
		course.short_introduction = (
			"Three SQE1 sittings in the January 2027 format. "
			"Hardest reviewed 5-option items. Not Kaplan papers."
		)
		course.description = (
			"<p>January 2027 SQE1 hard mocks: 170 questions per FLK, two 85-question "
			"sessions of 153 minutes, subjects grouped by session.</p>"
			"<p>Criminal Liability items are Criminal Litigation proxies because the "
			"Criminal Law course has no 5-option reviewed keys.</p>"
		)
		course.save(ignore_permissions=True)
		return course.name

	course = frappe.get_doc(
		{
			"doctype": "LMS Course",
			"title": COURSE_TITLE,
			"published": 0,
			"upcoming": 0,
			"disable_self_learning": 1,
			"short_introduction": (
				"Three unpublished SQE1 sittings in the January 2027 format. "
				"Hardest reviewed 5-option items. Not Kaplan papers."
			),
			"description": (
				"<p>January 2027 SQE1 hard mocks: 170 questions per FLK, two 85-question "
				"sessions of 153 minutes, subjects grouped by session.</p>"
			),
		}
	)
	course.append("instructors", {"instructor": "Administrator"})
	course.insert(ignore_permissions=True)
	if course.name != COURSE_NAME:
		frappe.rename_doc("LMS Course", course.name, COURSE_NAME, force=True)
	return COURSE_NAME


def _ensure_quiz(title: str, question_names: list[str], lesson_name: str | None = None) -> str:
	name = frappe.db.get_value("LMS Quiz", {"course": COURSE_NAME, "title": title})
	if name:
		quiz = frappe.get_doc("LMS Quiz", name)
	else:
		quiz = frappe.get_doc(
			{
				"doctype": "LMS Quiz",
				"title": title,
				"course": COURSE_NAME,
				"max_attempts": MAX_ATTEMPTS,
				"show_answers": SHOW_ANSWERS,
				"show_submission_history": 1,
				"passing_percentage": PASSING_PERCENTAGE,
				"duration": DURATION_MINUTES,
				"shuffle_questions": 1,
				"total_marks": len(question_names),
			}
		)
		quiz.insert(ignore_permissions=True)
		name = quiz.name
		quiz = frappe.get_doc("LMS Quiz", name)

	quiz.max_attempts = MAX_ATTEMPTS
	quiz.show_answers = SHOW_ANSWERS
	quiz.duration = DURATION_MINUTES
	quiz.shuffle_questions = 1
	quiz.passing_percentage = PASSING_PERCENTAGE
	quiz.set("questions", [])
	for question in question_names:
		quiz.append("questions", {"question": question, "marks": 1})
	quiz.total_marks = len(question_names)
	if lesson_name:
		quiz.lesson = lesson_name
	quiz.save(ignore_permissions=True)
	return quiz.name


def _ensure_chapter(index: int, title: str) -> str:
	existing = frappe.db.get_value("Course Chapter", {"course": COURSE_NAME, "title": title})
	if existing:
		return existing
	chapter = frappe.get_doc({"doctype": "Course Chapter", "title": title, "course": COURSE_NAME})
	chapter.insert(ignore_permissions=True)
	return chapter.name


def _ensure_quiz_lesson(chapter: str, title: str, quiz_name: str) -> str:
	existing = frappe.db.get_value(
		"Course Lesson",
		{"course": COURSE_NAME, "chapter": chapter, "quiz_id": quiz_name},
	)
	if existing:
		frappe.db.set_value("Course Lesson", existing, "content", "")
		frappe.db.set_value("Course Lesson", existing, "title", title)
		frappe.db.set_value("Course Lesson", existing, "body", QUIZ_LESSON_BODY)
		link_lesson_to_chapter(chapter, existing)
		return existing
	lesson = frappe.get_doc(
		new_quiz_lesson_values(
			title=title,
			course=COURSE_NAME,
			chapter=chapter,
			quiz_id=quiz_name,
			body=QUIZ_LESSON_BODY,
		)
	)
	lesson.insert(ignore_permissions=True)
	link_lesson_to_chapter(chapter, lesson.name)
	return lesson.name


def repair_quiz_lesson_bodies() -> dict:
	"""Mount the timed papers: Frappe only renders quiz_id when body is non-empty."""
	updated = []
	for name in frappe.get_all(
		"Course Lesson",
		filters={"course": COURSE_NAME},
		pluck="name",
	):
		lesson = frappe.get_doc("Course Lesson", name)
		if not (lesson.quiz_id or "").strip():
			continue
		lesson.content = ""
		lesson.body = QUIZ_LESSON_BODY
		lesson.save(ignore_permissions=True)
		updated.append({"lesson": lesson.name, "quiz": lesson.quiz_id, "body": len(lesson.body or "")})
	frappe.db.commit()
	return {"updated": len(updated), "lessons": updated}


def sitting_url(chapter_idx: int, lesson_idx: int) -> str:
	return f"/lms/courses/{COURSE_NAME}/learn/{int(chapter_idx)}-{int(lesson_idx)}"


def unlink_report_chapter() -> dict:
	"""Keep Coverage and gaps off the learner outline. Staff still use /learning-mock-report."""
	if not frappe.db.exists("LMS Course", COURSE_NAME):
		return {"removed": [], "kept": []}
	course = frappe.get_doc("LMS Course", COURSE_NAME)
	removed = []
	kept = []
	for row in course.get("chapters") or []:
		title = frappe.db.get_value("Course Chapter", row.chapter, "title") or ""
		if title == REPORT_CHAPTER_TITLE:
			removed.append(row.chapter)
		else:
			kept.append(row.chapter)
	if removed:
		course.set("chapters", [])
		for name in kept:
			course.append("chapters", {"chapter": name})
		course.save(ignore_permissions=True)
	return {"removed": removed, "kept": kept}


def close_book_quizzes() -> dict:
	updated = []
	for name in frappe.get_all("LMS Quiz", {"course": COURSE_NAME}, pluck="name"):
		frappe.db.set_value("LMS Quiz", name, "show_answers", SHOW_ANSWERS)
		updated.append(name)
	return {"updated": len(updated), "quizzes": updated}


def apply_student_exam_view() -> dict:
	"""Unlink gaps from the outline and close the book on session quizzes."""
	unlinked = unlink_report_chapter()
	quizzes = close_book_quizzes()
	frappe.db.commit()
	return {"unlinked": unlinked, "quizzes": quizzes}


def student_lobby(user: str | None = None) -> dict:
	"""Enrolled-safe lobby: sittings and start URLs. No question IDs or keys."""
	from aimaticlearning.lms_learning.utils import throw_access_denied, user_can_access_course

	user = user or frappe.session.user
	if user == "Guest" or not user_can_access_course(COURSE_NAME, user):
		throw_access_denied()
	if not frappe.db.exists("LMS Course", COURSE_NAME):
		frappe.throw("Hard mock course is not installed.")
	course = frappe.get_doc("LMS Course", COURSE_NAME)
	mocks = []
	for chapter_idx, crow in enumerate(course.get("chapters") or [], start=1):
		chapter = frappe.get_doc("Course Chapter", crow.chapter)
		title = chapter.title or ""
		if title == REPORT_CHAPTER_TITLE:
			continue
		sessions = []
		for lesson_idx, lrow in enumerate(chapter.get("lessons") or [], start=1):
			lesson = frappe.get_doc("Course Lesson", lrow.lesson)
			if not (lesson.quiz_id or "").strip():
				continue
			attempts = frappe.db.count(
				"LMS Quiz Submission",
				{"quiz": lesson.quiz_id, "member": user},
			)
			sessions.append(
				{
					"title": lesson.title,
					"duration": DURATION_MINUTES,
					"questions": 85,
					"attempts": int(attempts or 0),
					"max_attempts": MAX_ATTEMPTS,
					"start_url": sitting_url(chapter_idx, lesson_idx),
				}
			)
		if sessions:
			mocks.append({"title": title, "sessions": sessions})
	return {
		"title": COURSE_TITLE,
		"format": (
			"January 2027 sitting: 85 questions, 153 minutes, closed book, "
			f"{MAX_ATTEMPTS} attempts per session."
		),
		"course": COURSE_NAME,
		"lobby_url": LOBBY_URL,
		"published": int(course.published or 0),
		"mocks": mocks,
	}


SESSION_TITLES = {
	"flk1_s1": "FLK1 Session 1 — BLP, Dispute Resolution, Legal Services",
	"flk1_s2": "FLK1 Session 2 — Tort, Contract, Legal System",
	"flk2_s1": "FLK2 Session 1 — Wills, Accounts, Trusts, Land",
	"flk2_s2": "FLK2 Session 2 — Property, Accounts, Crime",
}

AREA_LABELS = {
	"blp": "Business Law and Practice",
	"dr": "Dispute Resolution",
	"legal_services": "Legal Services",
	"tort": "Tort",
	"contract": "Contract Law",
	"legal_system": "Legal System / Public Law / EU",
	"wills": "Wills and Administration of Estates",
	"accounts_wills": "Solicitors’ Accounts (wills)",
	"trusts": "Trusts",
	"land": "Land Law",
	"property": "Property Practice",
	"accounts_property": "Solicitors’ Accounts (property)",
	"criminal_liability": "Criminal Liability",
	"criminal_practice": "Criminal Law and Practice",
}

REPORT_URL = "/learning-mock-report"
REPORT_CHAPTER_TITLE = "Coverage and gaps"
REPORT_LESSON_TITLE = "Coverage and gaps"


def explain_gap(text: str | dict) -> dict:
	if isinstance(text, dict):
		return {
			"id": text.get("id") or "coverage",
			"title": text.get("title") or "Coverage note",
			"detail": text.get("detail") or "",
		}
	if text.startswith("Criminal Law"):
		return {
			"id": "criminal-liability",
			"title": "Criminal Liability uses Criminal Litigation items",
			"detail": (
				"The Criminal Law course has no reviewed five-option questions, "
				"so FLK2 Criminal Liability slots are filled from Criminal Litigation. "
				"They are not SRA-primary Criminal Liability items."
			),
		}
	if text.startswith("Eligible Hard"):
		return {
			"id": "hard-tags",
			"title": "Hard-tagged items could not be used",
			"detail": (
				"Every Hard-tagged question is four-option or AI-generated. "
				"These papers use the hardest reviewed five-option Medium items "
				"(longer application stems), spread across the three sittings."
			),
		}
	if text.startswith("dr pool"):
		return {
			"id": "dispute-resolution",
			"title": "Dispute Resolution pool is fully used",
			"detail": (
				"All 75 eligible five-option Dispute Resolution items appear across "
				"the three sittings (25 in each FLK1 Session 1)."
			),
		}
	if text.startswith("legal_services pool"):
		return {
			"id": "legal-services",
			"title": "Legal Services pool is fully used",
			"detail": (
				"All 80 eligible five-option Legal Services items appear across "
				"the three sittings."
			),
		}
	if text.startswith("legal_system pool"):
		return {
			"id": "legal-system",
			"title": "Legal System / Public Law pool is fully used",
			"detail": (
				"All 80 eligible five-option Public Law items appear across "
				"the three sittings."
			),
		}
	return {"id": "coverage", "title": "Coverage note", "detail": text}


def frontend_payload(summary: dict, generated: str | None = None) -> dict:
	"""Learner-safe report: no question IDs, stems, or keys."""
	mocks = []
	for mock in summary.get("mocks") or []:
		sessions = []
		for key, title in SESSION_TITLES.items():
			data = (mock.get("sessions") or {}).get(key) or {}
			sessions.append(
				{
					"id": key,
					"title": title,
					"count": data.get("count") or 0,
					"areas": [
						{"id": area, "label": AREA_LABELS.get(area, area), "count": count}
						for area, count in (data.get("areas") or {}).items()
					],
					"difficulty": data.get("difficulty") or {},
					"ethics_aml": data.get("ethics_aml") or 0,
					"tax": data.get("tax") or 0,
					"wales": data.get("wales") or 0,
				}
			)
		mocks.append({"mock": mock.get("mock"), "sessions": sessions})
	return {
		"title": "SQE1 hard mock coverage",
		"format": "January 2027: 170 questions per FLK, two sessions of 85, 153 minutes each.",
		"generated": generated,
		"unique_questions": summary.get("unique_questions") or 0,
		"duplicate": bool(summary.get("duplicate")),
		"gaps": [explain_gap(text) for text in summary.get("gaps") or []],
		"mocks": mocks,
		"report_url": REPORT_URL,
		"course": COURSE_NAME,
		"published": int(summary.get("published") or 0),
	}


def public_json_path() -> Path:
	return Path(frappe.get_site_path("private", "files", "lms_learning_exports")) / "sqe1-hard-mocks-public.json"


def load_public_report() -> dict:
	path = public_json_path()
	if path.exists():
		return json.loads(path.read_text(encoding="utf-8"))
	return frontend_payload(
		{
			"mocks": [],
			"gaps": [
				{
					"id": "missing",
					"title": "Coverage report is not generated yet",
					"detail": "The January 2027 hard-mock sittings have not been assembled on this site.",
				}
			],
			"unique_questions": 0,
			"duplicate": False,
			"published": 0,
		}
	)


def report_lesson_body(payload: dict) -> str:
	parts = [
		"## Coverage and gaps",
		"",
		payload.get("format") or "",
		"",
		f"{int(payload.get('unique_questions') or 0)} unique reviewed five-option questions. "
		"No question is reused across the three sittings.",
		"",
		"## Gaps",
		"",
	]
	for gap in payload.get("gaps") or []:
		parts.append(f"- **{gap.get('title') or ''}** — {gap.get('detail') or ''}")
	parts.append("")
	for mock in payload.get("mocks") or []:
		parts.append(f"## Mock {int(mock.get('mock') or 0)}")
		parts.append("")
		for session in mock.get("sessions") or []:
			areas = ", ".join(
				f"{area['label']} {area['count']}" for area in session.get("areas") or []
			)
			parts.append(
				f"**{session.get('title') or ''}** — {int(session.get('count') or 0)} questions. {areas}."
			)
			parts.append("")
	parts.append(f"[Open the full coverage report]({REPORT_URL})")
	return "\n".join(parts)


def _link_chapter_first(course_name: str, chapter_name: str) -> None:
	course = frappe.get_doc("LMS Course", course_name)
	existing = [row.chapter for row in course.get("chapters") or []]
	course.set("chapters", [])
	course.append("chapters", {"chapter": chapter_name})
	for name in existing:
		if name != chapter_name:
			course.append("chapters", {"chapter": name})
	course.save(ignore_permissions=True)


def ensure_report_lesson() -> dict:
	"""Keep a staff notes lesson, but do not pin it on the learner outline."""
	if not frappe.db.exists("LMS Course", COURSE_NAME):
		frappe.throw("Hard mock course is not installed.")
	payload = load_public_report()
	chapter = _ensure_chapter(0, REPORT_CHAPTER_TITLE)
	existing = frappe.db.get_value(
		"Course Lesson",
		{"course": COURSE_NAME, "chapter": chapter, "title": REPORT_LESSON_TITLE},
	)
	body = report_lesson_body(payload)
	if existing:
		lesson = frappe.get_doc("Course Lesson", existing)
		lesson.body = body
		lesson.content = ""
		lesson.quiz_id = ""
		lesson.save(ignore_permissions=True)
		lesson_name = lesson.name
	else:
		lesson = frappe.get_doc(
			{
				"doctype": "Course Lesson",
				"title": REPORT_LESSON_TITLE,
				"course": COURSE_NAME,
				"chapter": chapter,
				"body": body,
				"content": "",
			}
		)
		lesson.insert(ignore_permissions=True)
		lesson_name = lesson.name
	link_lesson_to_chapter(chapter, lesson_name)
	frappe.db.set_value("Course Lesson", lesson_name, "content", "")
	unlink_report_chapter()
	return {"chapter": chapter, "lesson": lesson_name, "content": ""}


def sync_frontend_report() -> dict:
	"""Refresh the public report JSON and the in-course notes lesson. No quiz rebuild."""
	path = Path(frappe.get_site_path("private", "files", "lms_learning_exports")) / "sqe1-hard-mocks-dry-run.json"
	if path.exists():
		stored = json.loads(path.read_text(encoding="utf-8"))
		summary = stored.get("summary") or {}
		generated = stored.get("generated")
		gaps = stored.get("gaps") or summary.get("gaps") or []
		payload = frontend_payload(
			{
				"mocks": summary.get("mocks") or [],
				"gaps": gaps,
				"unique_questions": summary.get("unique_questions"),
				"duplicate": summary.get("duplicate"),
				"published": int(frappe.db.get_value("LMS Course", COURSE_NAME, "published") or 0)
				if frappe.db.exists("LMS Course", COURSE_NAME)
				else 0,
			},
			generated,
		)
		public_json_path().parent.mkdir(parents=True, exist_ok=True)
		public_json_path().write_text(json.dumps(payload, indent=2), encoding="utf-8")
	lesson = ensure_report_lesson()
	payload = load_public_report()
	payload["coverage_lesson"] = lesson
	frappe.db.commit()
	return payload


def publish_course() -> dict:
	"""Publish the hard mocks for learners. Do not add them to /sqe. Do not auto-enrol."""
	if not frappe.db.exists("LMS Course", COURSE_NAME):
		frappe.throw("Hard mock course is not installed.")
	from aimaticlearning.lms_learning.outline_sync import clear_quiz_lesson_editorjs

	blocked = clear_quiz_lesson_editorjs(COURSE_NAME, dry_run=True)
	if blocked["count"]:
		frappe.throw(f"{blocked['count']} quiz lessons still have EditorJS content.")
	course = frappe.get_doc("LMS Course", COURSE_NAME)
	course.published = 1
	course.upcoming = 0
	course.disable_self_learning = 0
	course.short_introduction = (
		"Three SQE1 sittings in the January 2027 format. "
		"Hardest reviewed 5-option items. Not Kaplan papers."
	)
	course.save(ignore_permissions=True)
	frappe.db.commit()
	return sync_frontend_report()


def apply() -> dict:
	allocation = allocate(load_pools())
	report = summarise(allocation)
	course = _ensure_course()
	created = []
	for paper in allocation["papers"]:
		chapter_title = f"Mock {paper['mock']}"
		chapter = _ensure_chapter(paper["mock"], chapter_title)
		link_chapter_to_course(course, chapter)
		for session, title in SESSION_TITLES.items():
			quiz_title = f"Mock {paper['mock']} {title}"
			names = [row["name"] for row in session_rows(paper, session)]
			quiz_name = _ensure_quiz(quiz_title, names)
			lesson = _ensure_quiz_lesson(chapter, quiz_title, quiz_name)
			# Point quiz.lesson after the lesson exists.
			_ensure_quiz(quiz_title, names, lesson_name=lesson)
			created.append(
				{
					"mock": paper["mock"],
					"session": session,
					"quiz": quiz_name,
					"lesson": lesson,
					"count": len(names),
					"content": frappe.db.get_value("Course Lesson", lesson, "content") or "",
				}
			)
	report["created"] = created
	report["course"] = course
	report["published"] = int(frappe.db.get_value("LMS Course", course, "published") or 0)
	_write_report(report, allocation)
	report["coverage_lesson"] = ensure_report_lesson()
	frappe.db.commit()
	return report


def _write_report(report: dict, allocation: dict) -> None:
	payload = {
		"generated": str(now_datetime()),
		"summary": report,
		"gaps": allocation["gaps"],
	}
	private = Path(frappe.get_site_path("private", "files", "lms_learning_exports"))
	private.mkdir(parents=True, exist_ok=True)
	path = private / "sqe1-hard-mocks-dry-run.json"
	path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
	public = frontend_payload(
		{
			"mocks": report.get("mocks") or [],
			"gaps": allocation["gaps"],
			"unique_questions": report.get("unique_questions"),
			"duplicate": report.get("duplicate"),
			"published": report.get("published") or 0,
		},
		payload["generated"],
	)
	public_json_path().write_text(json.dumps(public, indent=2), encoding="utf-8")
	docs = Path("/home/nabeel/frappe-bench/apps/aimaticlearning/docs/sqe1/HARD-MOCKS-REPORT.md")
	lines = [
		"# SQE1 hard mocks — selection report",
		"",
		f"Generated {payload['generated']}. Course `{COURSE_NAME}` unpublished.",
		"",
		"## Gaps",
		"",
	]
	for gap in allocation["gaps"]:
		lines.append(f"- {gap}")
	lines += ["", "## Papers", ""]
	for mock in report["mocks"]:
		lines.append(f"### Mock {mock['mock']}")
		for session, data in mock["sessions"].items():
			lines.append(
				f"- `{session}`: {data['count']} items; areas {data['areas']}; "
				f"difficulty {data['difficulty']}; ethics/AML {data['ethics_aml']}; "
				f"tax {data['tax']}; Wales {data['wales']}"
			)
		lines.append("")
	lines += [
		f"Unique questions: {report['unique_questions']}. Duplicate: {report['duplicate']}.",
		"",
	]
	docs.write_text("\n".join(lines), encoding="utf-8")
