from __future__ import annotations

from collections import Counter

import frappe

from aimaticlearning.lms_learning.analytics import build_learning_map
from aimaticlearning.lms_learning.utils import user_can_access_course

VALID_RATINGS = ("hard", "good", "easy")
RECALL_PREFIX = "recall:"
PREFERRED_COURSE = "business-law-practice-blp"
FLASHCARD_TITLE_MARKERS = ("flashcard",)
MCQ_TITLE_MARKERS = ("practice mcq", "mcq", "practice questions", "quiz")


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


def latest_mcq_results_from_attempts(attempts: list[dict]) -> dict[str, dict]:
	"""Latest Learning Attempt Detail per LMS Question, excluding flashcard reviews."""
	latest: dict[str, dict] = {}
	for row in attempts:
		if row.get("learning_flashcard"):
			continue
		name = row.get("lms_question")
		if not name or name in latest:
			continue
		latest[name] = {
			"correct": int(row.get("correct") or 0),
			"concept_tags": row.get("concept_tags") or "",
			"course_chapter": row.get("course_chapter"),
		}
	return latest


def summarise_mcq_results(results: dict[str, dict], quiz_history: list | None = None) -> dict:
	correct = sum(1 for row in results.values() if row.get("correct"))
	incorrect = sum(1 for row in results.values() if not row.get("correct"))
	return {
		"attempted": len(results),
		"correct": correct,
		"incorrect": incorrect,
		"quizzes": len(quiz_history or []),
	}


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


def lesson_title_matches_activity(title: str | None, activity: str) -> bool:
	lowered = (title or "").lower()
	if activity == "flashcard":
		return any(marker in lowered for marker in FLASHCARD_TITLE_MARKERS)
	if activity == "mcq":
		if any(marker in lowered for marker in FLASHCARD_TITLE_MARKERS):
			return False
		return any(marker in lowered for marker in MCQ_TITLE_MARKERS)
	return False


def rank_revision_recommendations(
	*,
	flashcards: dict,
	has_ratings: bool,
	weaknesses: list[dict],
	chapters: list[dict],
	mcqs: dict,
	quiz_history: list | None = None,
) -> list[str]:
	"""Rank next-step copy from combined flashcard, MCQ, mastery, and quiz signals."""
	ranked: list[tuple[int, str]] = []
	hard = int(flashcards.get("hard") or 0)
	published = int(flashcards.get("published") or 0)
	incorrect = int(mcqs.get("incorrect") or 0)
	attempted_mcqs = int(mcqs.get("attempted") or 0)

	if hard:
		ranked.append(
			(
				100,
				f"Revise {hard} flashcard{'s' if hard != 1 else ''} you rated Hard.",
			)
		)
	needs_work = [row for row in chapters if row.get("group") == "needs_work"]
	if needs_work:
		titles = ", ".join(row.get("chapter_title") or "Chapter" for row in needs_work[:2])
		ranked.append(
			(
				90,
				f"Revisit {titles} — mastery is below 50% after chapter attempts.",
			)
		)
	for item in weaknesses[:3]:
		ranked.append(
			(
				80,
				f"Review concept '{item['concept']}' ({item['mastery_pct']}% over {item['attempts']} attempts).",
			)
		)
	if incorrect:
		ranked.append(
			(
				75,
				f"Retry {incorrect} MCQ{'s' if incorrect != 1 else ''} you answered incorrectly.",
			)
		)
	low_quizzes = [
		row
		for row in (quiz_history or [])
		if row.get("percentage") is not None and float(row.get("percentage") or 0) < 60
	]
	if low_quizzes:
		quiz = low_quizzes[0]
		title = quiz.get("quiz_title") or "chapter MCQs"
		ranked.append(
			(
				70,
				f"Retake {title} — latest score {float(quiz.get('percentage') or 0):.0f}%.",
			)
		)
	if published and not has_ratings:
		ranked.append(
			(
				50,
				"Open a chapter Flashcards lesson and rate recall as Hard, Good, or Easy. This page then becomes your revision queue.",
			)
		)
	elif not published:
		ranked.append(
			(
				40,
				"This subject does not have published flashcards yet. Use the notes and chapter MCQs.",
			)
		)
	if not attempted_mcqs and not hard and not weaknesses and not needs_work:
		ranked.append(
			(
				20,
				"Complete chapter MCQs and flashcards so this board can rank what to restudy next.",
			)
		)

	seen: set[str] = set()
	ordered: list[str] = []
	for _score, text in sorted(ranked, key=lambda item: -item[0]):
		if text in seen:
			continue
		seen.add(text)
		ordered.append(text)
		if len(ordered) >= 6:
			break
	return ordered


def load_latest_ratings(user: str, learning_module: str) -> dict[str, str]:
	attempts = _load_attempt_details(user, learning_module, flashcards=True)
	return latest_ratings_from_attempts(attempts)


def load_latest_mcq_results(user: str, learning_module: str) -> dict[str, dict]:
	attempts = _load_attempt_details(user, learning_module, questions=True)
	return latest_mcq_results_from_attempts(attempts)


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
			"mcqs": _empty_mcq_counts(),
			"has_flashcards": False,
			"has_attempts": False,
			"weaknesses": [],
			"strengths": [],
			"recommendations": [
				"Ask your instructor to enrol you on a course before revision data can appear."
			],
			"chapters": [],
			"quiz_history": [],
			"study_urls": {},
		}

	learning_map = build_learning_map(selected["name"], user)
	published_cards = frappe.get_all(
		"Learning Flashcard",
		filters={"learning_module": selected["name"], "status": "Published"},
		fields=["name", "course_chapter", "concept", "difficulty"],
		limit_page_length=2000,
	)
	ratings = load_latest_ratings(user, selected["name"])
	mcq_results = load_latest_mcq_results(user, selected["name"])
	quiz_history = list(learning_map.get("quiz_history") or [])
	mcqs = summarise_mcq_results(mcq_results, quiz_history)
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
	incorrect_by_chapter: dict[str, int] = Counter()
	for row in mcq_results.values():
		chapter = row.get("course_chapter")
		if chapter and not row.get("correct"):
			incorrect_by_chapter[chapter] += 1

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
				"incorrect_mcqs": int(incorrect_by_chapter.get(course_chapter) or 0),
				"notes_url": _lesson_url(selected["lms_course"], course_chapter),
				"flashcard_url": _lesson_url(selected["lms_course"], course_chapter, "flashcard"),
				"mcq_url": _lesson_url(selected["lms_course"], course_chapter, "mcq"),
			}
		)

	recommendations = rank_revision_recommendations(
		flashcards=flashcards,
		has_ratings=bool(ratings),
		weaknesses=list(learning_map.get("weaknesses") or []),
		chapters=chapters,
		mcqs=mcqs,
		quiz_history=quiz_history,
	)

	base = f"/learning-flashcards?learning_module={selected['name']}"
	first_mcq = next((row.get("mcq_url") for row in chapters if row.get("mcq_url")), None)
	retry_mcq = next(
		(row.get("mcq_url") for row in chapters if row.get("incorrect_mcqs") and row.get("mcq_url")),
		first_mcq,
	)
	return {
		"selected": selected,
		"modules": modules,
		"empty_reason": None,
		"flashcards": flashcards,
		"mcqs": mcqs,
		"has_flashcards": flashcards["published"] > 0,
		"has_attempts": bool(ratings) or bool(mcq_results) or any((row.get("attempts") or 0) > 0 for row in chapters),
		"weaknesses": learning_map.get("weaknesses") or [],
		"strengths": learning_map.get("strengths") or [],
		"recommendations": recommendations[:6],
		"chapters": chapters,
		"quiz_history": quiz_history[:8],
		"study_urls": {
			"hard": f"{base}&rating=hard",
			"good": f"{base}&rating=good",
			"easy": f"{base}&rating=easy",
			"unreviewed": f"{base}&rating=unreviewed",
			"all": base,
			"course": f"/lms/courses/{selected['lms_course']}",
			"mcq": first_mcq,
			"incorrect_mcq": retry_mcq,
		},
	}


def accessible_modules(user: str) -> list[dict]:
	rows = frappe.get_all(
		"Learning Module Config",
		fields=["name", "title", "lms_course"],
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
		activity = _activity_from_marker(title_contains)
		for ref in refs:
			title = frappe.db.get_value("Course Lesson", ref.lesson, "title") or ""
			if activity:
				if lesson_title_matches_activity(title, activity):
					return f"/lms/courses/{course}/learn/{int(chapter_idx)}-{int(ref.idx)}"
			elif title_contains.lower() in title.lower():
				return f"/lms/courses/{course}/learn/{int(chapter_idx)}-{int(ref.idx)}"
		return None
	return f"/lms/courses/{course}/learn/{int(chapter_idx)}-{int(refs[0].idx)}"


def _activity_from_marker(title_contains: str) -> str | None:
	lowered = (title_contains or "").lower()
	if "flashcard" in lowered:
		return "flashcard"
	if lowered in ("mcq", "quiz", "practice") or "mcq" in lowered or "question" in lowered:
		return "mcq"
	return None


def _load_attempt_details(user: str, learning_module: str, *, flashcards: bool = False, questions: bool = False) -> list[dict]:
	filters: dict = {"user": user, "learning_module": learning_module}
	if flashcards and not questions:
		filters["learning_flashcard"] = ["is", "set"]
	elif questions and not flashcards:
		filters["lms_question"] = ["is", "set"]
	return frappe.get_all(
		"Learning Attempt Detail",
		filters=filters,
		fields=["learning_flashcard", "lms_question", "concept_tags", "correct", "course_chapter", "modified"],
		order_by="modified desc",
		limit_page_length=5000,
	)


def _empty_flashcard_counts() -> dict:
	return {"published": 0, "hard": 0, "good": 0, "easy": 0, "unreviewed": 0}


def _empty_mcq_counts() -> dict:
	return {"attempted": 0, "correct": 0, "incorrect": 0, "quizzes": 0}


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
