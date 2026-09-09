from __future__ import annotations

from collections import Counter
from urllib.parse import quote

import frappe
from frappe.utils import strip_html

from aimaticlearning.lms_learning.analytics import build_learning_map
from aimaticlearning.lms_learning.utils import user_can_access_course

VALID_RATINGS = ("hard", "good", "easy")
RECALL_PREFIX = "recall:"
PREFERRED_COURSE = "business-law-practice-blp"


def encode_recall_tags(rating: str | None, concept: str | None = None) -> str:
	normalised = _normalise_rating(rating) or "hard"
	parts = [f"{RECALL_PREFIX}{normalised}"]
	if concept and str(concept).strip():
		parts.append(str(concept).strip())
	return ", ".join(parts)


def parse_recall_rating(concept_tags: str | None, correct: int | bool | None = None) -> str | None:
	for part in _split_parts(concept_tags):
		lowered = part.lower()
		if lowered.startswith(RECALL_PREFIX):
			value = lowered[len(RECALL_PREFIX) :].strip()
			if value in VALID_RATINGS:
				return value
	if correct is None:
		return None
	return "hard" if not int(correct) else "good"


def latest_ratings_from_attempts(attempts: list[dict]) -> dict[str, str]:
	latest: dict[str, str] = {}
	for row in attempts:
		name = row.get("learning_flashcard")
		if not name or name in latest:
			continue
		rating = parse_recall_rating(row.get("concept_tags"), row.get("correct"))
		if rating:
			latest[name] = rating
	return latest


def apply_rating_filter(cards: list[dict], ratings: dict[str, str], rating_filter: str | None) -> list[dict]:
	wanted = (rating_filter or "").strip().lower()
	filtered = []
	for card in cards:
		last = ratings.get(card.get("name"))
		card["last_rating"] = last
		if wanted in ("", "all", "*"):
			filtered.append(card)
		elif wanted == "unreviewed" and last is None:
			filtered.append(card)
		elif last == wanted:
			filtered.append(card)
	return filtered


def load_latest_ratings(user: str, learning_module: str) -> dict[str, str]:
	attempts = frappe.get_all(
		"Learning Attempt Detail",
		filters={
			"user": user,
			"learning_module": learning_module,
			"learning_flashcard": ["is", "set"],
		},
		fields=["learning_flashcard", "concept_tags", "correct", "modified"],
		order_by="modified desc",
		limit_page_length=5000,
	)
	return latest_ratings_from_attempts(attempts)


def filter_cards_for_user(
	cards: list[dict],
	user: str,
	learning_module: str,
	rating_filter: str | None,
) -> list[dict]:
	return apply_rating_filter(cards, load_latest_ratings(user, learning_module), rating_filter)


def build_revision_board(
	user: str,
	course: str | None = None,
	learning_module: str | None = None,
) -> dict:
	modules = accessible_modules(user)
	selected = _select_module(modules, course, learning_module)
	if not selected:
		return {
			"selected": None,
			"modules": modules,
			"empty_reason": "no_access",
			"flashcards": _empty_flashcard_counts(),
			"has_flashcards": False,
			"has_attempts": False,
			"weaknesses": [],
			"strengths": [],
			"recommendations": [
				"Ask your instructor to enrol you on a course before revision data can appear."
			],
			"chapters": [],
			"study_urls": {},
			"quiz_history": [],
			"quiz_summary": _empty_quiz_summary(),
			"missed_questions": [],
			"mock_exam": _empty_mock_exam(),
		}

	learning_map = build_learning_map(selected["name"], user)
	quiz_history = _prepare_quiz_history(learning_map.get("quiz_history") or [], selected["lms_course"])
	quiz_summary = _build_quiz_summary(quiz_history)
	missed_questions = _load_missed_questions(user, selected)
	mock_exam = _build_mock_exam(selected, quiz_history)
	published_cards = frappe.get_all(
		"Learning Flashcard",
		filters={"learning_module": selected["name"], "status": "Published"},
		fields=["name", "course_chapter", "concept", "difficulty"],
		limit_page_length=2000,
	)
	ratings = load_latest_ratings(user, selected["name"])
	counts = Counter(ratings.values())
	flashcards = {
		"published": len(published_cards),
		"hard": int(counts.get("hard") or 0),
		"good": int(counts.get("good") or 0),
		"easy": int(counts.get("easy") or 0),
		"unreviewed": max(len(published_cards) - len(ratings), 0),
	}
	hard_by_chapter: dict[str, int] = Counter()
	for card in published_cards:
		if ratings.get(card.name) == "hard" and card.course_chapter:
			hard_by_chapter[card.course_chapter] += 1

	chapters = []
	for stats in learning_map.get("chapter_stats") or []:
		course_chapter = stats.get("course_chapter")
		chapters.append(
			{
				"chapter_title": stats.get("chapter_title"),
				"course_chapter": course_chapter,
				"mastery_pct": stats.get("mastery_pct") or 0,
				"attempts": stats.get("attempts") or 0,
				"group": _group(stats.get("mastery_pct") or 0, stats.get("attempts") or 0),
				"hard_cards": int(hard_by_chapter.get(course_chapter) or 0),
				"notes_url": _notes_url(selected["name"], selected["lms_course"], course_chapter),
				"flashcard_url": _lesson_url(selected["lms_course"], course_chapter, "flashcard"),
			}
		)

	recommendations = list(learning_map.get("revision_recommendations") or [])
	if flashcards["hard"]:
		recommendations.insert(
			0,
			f"Revise {flashcards['hard']} flashcard{'s' if flashcards['hard'] != 1 else ''} you rated Hard.",
		)
	elif flashcards["published"] and not ratings:
		recommendations.insert(
			0,
			"Open a chapter Flashcards lesson and rate recall as Hard, Good, or Easy. This page then becomes your revision queue.",
		)
	elif not flashcards["published"]:
		recommendations.insert(
			0,
			"This subject does not have published flashcards yet. Use the notes and, when they appear, chapter MCQs.",
		)

	if missed_questions:
		recommendations.insert(0, f"Review {len(missed_questions)} missed MCQ{'s' if len(missed_questions) != 1 else ''} and reopen the linked chapter notes.")

	base = f"/learning-flashcards?learning_module={selected['name']}"
	return {
		"selected": selected,
		"modules": modules,
		"empty_reason": None,
		"flashcards": flashcards,
		"has_flashcards": flashcards["published"] > 0,
		"has_attempts": bool(ratings) or bool(quiz_history) or any((row.get("attempts") or 0) > 0 for row in chapters),
		"weaknesses": learning_map.get("weaknesses") or [],
		"strengths": learning_map.get("strengths") or [],
		"recommendations": recommendations[:6],
		"chapters": chapters,
		"study_urls": {
			"hard": f"{base}&rating=hard",
			"good": f"{base}&rating=good",
			"easy": f"{base}&rating=easy",
			"unreviewed": f"{base}&rating=unreviewed",
			"all": base,
			"course": f"/lms/courses/{selected['lms_course']}",
		},
		"quiz_history": quiz_history,
		"quiz_summary": quiz_summary,
		"missed_questions": missed_questions,
		"mock_exam": mock_exam,
	}


def accessible_modules(user: str) -> list[dict]:
	rows = frappe.get_all(
		"Learning Module Config",
		fields=["name", "title", "lms_course", "module_assessment_quiz", "module_assessment_count"],
		order_by="creation asc",
	)
	modules = []
	for row in rows:
		if not row.lms_course or not user_can_access_course(row.lms_course, user):
			continue
		published = frappe.db.count(
			"Learning Flashcard",
			{"learning_module": row.name, "status": "Published"},
		)
		modules.append(
			{
				"name": row.name,
				"title": row.title,
				"lms_course": row.lms_course,
				"published_flashcards": published,
				"module_assessment_quiz": row.module_assessment_quiz,
				"module_assessment_count": row.module_assessment_count,
			}
		)
	return modules


def _select_module(modules: list[dict], course: str | None, learning_module: str | None) -> dict | None:
	if learning_module:
		for module in modules:
			if module["name"] == learning_module:
				return module
	if course:
		for module in modules:
			if module["lms_course"] == course:
				return module
	for module in modules:
		if module["lms_course"] == PREFERRED_COURSE:
			return module
	return modules[0] if modules else None


def _lesson_url(course: str | None, course_chapter: str | None, title_contains: str | None = None) -> str | None:
	if not course or not course_chapter:
		return None
	chapter_idx = frappe.db.get_value(
		"Chapter Reference",
		{"parent": course, "chapter": course_chapter},
		"idx",
	)
	if not chapter_idx:
		return None
	refs = frappe.get_all(
		"Lesson Reference",
		filters={"parent": course_chapter},
		fields=["lesson", "idx"],
		order_by="idx asc",
	)
	if not refs:
		return None
	if title_contains:
		for ref in refs:
			title = (frappe.db.get_value("Course Lesson", ref.lesson, "title") or "").lower()
			if title_contains.lower() in title:
				return f"/lms/courses/{course}/learn/{int(chapter_idx)}-{int(ref.idx)}"
		return None
	return f"/lms/courses/{course}/learn/{int(chapter_idx)}-{int(refs[0].idx)}"


def _empty_flashcard_counts() -> dict:
	return {"published": 0, "hard": 0, "good": 0, "easy": 0, "unreviewed": 0}


def _group(mastery_pct: float, attempts: int) -> str:
	if not attempts:
		return "not_started"
	if mastery_pct >= 75:
		return "strong"
	if mastery_pct >= 50:
		return "developing"
	return "needs_work"


def _normalise_rating(rating: str | None) -> str | None:
	value = (rating or "").strip().lower()
	if value == "known":
		value = "easy"
	return value if value in VALID_RATINGS else None


def _split_parts(raw: str | None) -> list[str]:
	if not raw:
		return []
	return [part.strip() for part in str(raw).split(",") if part.strip()]


def _prepare_quiz_history(rows: list[dict], course: str) -> list[dict]:
	history = []
	for row in rows:
		item = dict(row)
		item["url"] = _quiz_url(course, item.get("quiz"))
		history.append(item)
	return history


def _build_quiz_summary(history: list[dict]) -> dict:
	attempts = len(history)
	passed = sum(1 for row in history if row.get("passed"))
	mock_attempts = sum(1 for row in history if row.get("kind") == "mock_exam")
	chapter_attempts = attempts - mock_attempts
	average = (
		round(sum(float(row.get("percentage") or 0) for row in history) / attempts, 1)
		if attempts
		else 0
	)
	return {
		"attempts": attempts,
		"passed": passed,
		"failed": max(attempts - passed, 0),
		"pass_rate_pct": round(100 * passed / attempts, 1) if attempts else 0,
		"average_pct": average,
		"chapter_mcq_attempts": chapter_attempts,
		"mock_exam_attempts": mock_attempts,
		"latest": history[0] if history else None,
	}


def _build_mock_exam(selected: dict, history: list[dict]) -> dict:
	quiz = selected.get("module_assessment_quiz")
	if not quiz:
		return _empty_mock_exam()
	attempts = [row for row in history if row.get("quiz") == quiz]
	question_count = frappe.db.count("LMS Quiz Question", {"parent": quiz})
	return {
		"available": True,
		"quiz": quiz,
		"title": frappe.db.get_value("LMS Quiz", quiz, "title") or "Module mock exam",
		"question_count": int(question_count or selected.get("module_assessment_count") or 0),
		"attempts": len(attempts),
		"url": _quiz_url(selected["lms_course"], quiz) or f"/lms/courses/{selected['lms_course']}",
		"latest": attempts[0] if attempts else None,
	}


def _load_missed_questions(user: str, selected: dict) -> list[dict]:
	rows = frappe.get_all(
		"Learning Attempt Detail",
		filters={
			"user": user,
			"learning_module": selected["name"],
			"correct": 0,
			"quiz_submission": ["is", "set"],
			"lms_question": ["is", "set"],
		},
		fields=[
			"quiz_submission",
			"lms_question",
			"course_chapter",
			"concept_tags",
			"question_revision",
			"modified",
		],
		order_by="modified desc",
		limit_page_length=100,
	)
	missed = []
	seen = set()
	for row in rows:
		key = (row.get("quiz_submission"), row.get("lms_question"))
		if not key[0] or not key[1] or key in seen:
			continue
		seen.add(key)
		meta = frappe.db.get_value(
			"Learning Question Meta",
			{"lms_question": row.lms_question},
			["concept", "course_chapter"],
			as_dict=True,
		)
		course_chapter = row.course_chapter or (meta and meta.course_chapter)
		profile = (
			frappe.db.get_value(
				"Learning Chapter Profile",
				{"learning_module": selected["name"], "course_chapter": course_chapter},
				["name", "chapter_title"],
				as_dict=True,
			)
			if course_chapter
			else None
		)
		concept = (meta and meta.concept) or _first_concept(row.concept_tags)
		notes_url = f"/learning-notes/{profile.name}" if profile else None
		if notes_url and concept:
			notes_url += "?focus=" + quote(str(concept))
		question_text = strip_html(frappe.db.get_value("LMS Question", row.lms_question, "question") or "")
		quiz_title = frappe.db.get_value("LMS Quiz Submission", row.quiz_submission, "quiz_title")
		quiz = frappe.db.get_value("LMS Quiz Submission", row.quiz_submission, "quiz")
		missed.append(
			{
				"question": _truncate(question_text) or "Missed question",
				"concept": concept or "Review the linked chapter",
				"chapter_title": profile.chapter_title if profile else None,
				"course_chapter": course_chapter,
				"quiz_title": quiz_title or "Quiz",
				"kind": "mock_exam" if quiz == selected.get("module_assessment_quiz") else "chapter_mcq",
				"question_revision": row.question_revision,
				"modified": row.modified,
				"notes_url": notes_url,
			}
		)
		if len(missed) >= 12:
			break
	return missed


def _notes_url(learning_module: str, course: str, course_chapter: str | None) -> str | None:
	if not course_chapter:
		return None
	profile = frappe.db.get_value(
		"Learning Chapter Profile",
		{"learning_module": learning_module, "course_chapter": course_chapter},
		"name",
	)
	if profile:
		return f"/learning-notes/{profile}"
	return _lesson_url(course, course_chapter)


def _quiz_url(course: str | None, quiz: str | None) -> str | None:
	if not course or not quiz:
		return None
	lesson = frappe.db.get_value(
		"Course Lesson",
		{"course": course, "quiz_id": quiz},
		["name", "chapter"],
		as_dict=True,
	)
	if not lesson or not lesson.chapter:
		return None
	chapter_idx = frappe.db.get_value(
		"Chapter Reference",
		{"parent": course, "chapter": lesson.chapter},
		"idx",
	)
	lesson_idx = frappe.db.get_value(
		"Lesson Reference",
		{"parent": lesson.chapter, "lesson": lesson.name},
		"idx",
	)
	if chapter_idx is None or lesson_idx is None:
		return None
	return f"/lms/courses/{course}/learn/{int(chapter_idx)}-{int(lesson_idx)}"


def _empty_quiz_summary() -> dict:
	return {
		"attempts": 0,
		"passed": 0,
		"failed": 0,
		"pass_rate_pct": 0,
		"average_pct": 0,
		"chapter_mcq_attempts": 0,
		"mock_exam_attempts": 0,
		"latest": None,
	}


def _empty_mock_exam() -> dict:
	return {
		"available": False,
		"quiz": None,
		"title": None,
		"question_count": 0,
		"attempts": 0,
		"url": None,
		"latest": None,
	}


def _first_concept(raw: str | None) -> str | None:
	for part in str(raw or "").split(","):
		part = part.strip()
		if part and not part.lower().startswith("recall:"):
			return part
	return None


def _truncate(value: str, limit: int = 180) -> str:
	value = " ".join(str(value or "").split())
	if len(value) <= limit:
		return value
	return value[: limit - 1].rstrip() + "…"
