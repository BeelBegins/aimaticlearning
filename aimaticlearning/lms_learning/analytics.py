from __future__ import annotations

from collections import defaultdict

import frappe
from frappe.utils import cint, flt, now_datetime

# Chapter "strong" needs both good marks and full chapter-MCQ coverage.
# Flashcard Easy ratings never count toward chapter mastery.
STRONG_MASTERY_PCT = 75.0
DEVELOPING_MASTERY_PCT = 50.0


def build_learning_map(learning_module: str, user: str) -> dict:
	chapters = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": learning_module},
		fields=["name", "chapter_title", "course_chapter", "concept_tags", "chapter_quiz"],
		order_by="creation asc",
	)
	chapters = [row for row in chapters if not _is_module_assessment_title(row.chapter_title)]
	# Prefer learner outline order when the course is wired.
	course = frappe.db.get_value("Learning Module Config", learning_module, "lms_course")
	outline_idx = {}
	if course:
		for rec in frappe.get_all(
			"Chapter Reference",
			filters={"parent": course},
			fields=["chapter", "idx"],
			limit_page_length=500,
		):
			outline_idx[rec.chapter] = rec.idx
		chapters.sort(
			key=lambda row: (
				0 if outline_idx.get(row.course_chapter) else 1,
				outline_idx.get(row.course_chapter) or 10_000,
				row.chapter_title or "",
			)
		)

	quiz_sizes = _quiz_question_counts(
		[row.chapter_quiz for row in chapters if row.chapter_quiz]
	)
	quiz_to_chapter = {
		row.chapter_quiz: (row.course_chapter or row.name)
		for row in chapters
		if row.chapter_quiz
	}

	attempts = frappe.get_all(
		"Learning Attempt Detail",
		filters={"learning_module": learning_module, "user": user},
		fields=[
			"course_chapter",
			"lms_question",
			"learning_flashcard",
			"correct",
			"time_seconds",
			"concept_tags",
			"question_revision",
			"modified",
		],
		order_by="modified desc",
		limit_page_length=5000,
	)
	quiz_rows = []
	if course:
		quiz_rows = frappe.db.sql(
			"""
			select s.name, s.quiz, s.percentage, s.course, q.title as quiz_title
			from `tabLMS Quiz Submission` s
			inner join `tabLMS Quiz` q on q.name = s.quiz
			where s.member = %(user)s and s.course = %(course)s
			order by s.modified desc
			""",
			{"user": user, "course": course},
			as_dict=True,
		)

	latest_quiz_pct: dict[str, float] = {}
	for row in quiz_rows:
		chapter_key = quiz_to_chapter.get(row.quiz)
		if not chapter_key or chapter_key in latest_quiz_pct:
			continue
		latest_quiz_pct[chapter_key] = flt(row.percentage)

	chapter_stats: dict[str, dict] = {}
	for chapter in chapters:
		key = chapter.course_chapter or chapter.name
		quiz_size = cint(quiz_sizes.get(chapter.chapter_quiz) or 0)
		chapter_stats[key] = {
			"chapter_profile": chapter.name,
			"chapter_title": chapter.chapter_title,
			"course_chapter": chapter.course_chapter,
			"chapter_quiz": chapter.chapter_quiz,
			"quiz_size": quiz_size,
			"attempts": 0,
			"correct": 0,
			"avg_time": 0.0,
			"mastery_pct": 0.0,
			"quiz_pct": None,
			"mcq_covered": False,
			"concept_tags": chapter.concept_tags or "",
			"group": "not_started",
		}

	# Latest MCQ result per question (flashcard reviews excluded).
	latest_mcq: dict[str, dict] = {}
	for row in attempts:
		if row.get("learning_flashcard") or not row.get("lms_question"):
			continue
		qid = row.lms_question
		if qid in latest_mcq:
			continue
		latest_mcq[qid] = row

	concept_stats: dict[str, dict] = defaultdict(lambda: {"attempts": 0, "correct": 0})
	time_totals: dict[str, float] = defaultdict(float)
	time_counts: dict[str, int] = defaultdict(int)
	correct_by_chapter: dict[str, int] = defaultdict(int)
	attempted_by_chapter: dict[str, int] = defaultdict(int)

	for qid, row in latest_mcq.items():
		key = row.course_chapter or "general"
		if key not in chapter_stats:
			continue
		attempted_by_chapter[key] += 1
		if row.correct:
			correct_by_chapter[key] += 1
		if row.time_seconds:
			time_totals[key] += float(row.time_seconds)
			time_counts[key] += 1
		for concept in _split_tags(row.concept_tags):
			concept_stats[concept]["attempts"] += 1
			if row.correct:
				concept_stats[concept]["correct"] += 1

	strengths: list[dict] = []
	weaknesses: list[dict] = []
	nodes: list[dict] = []
	links: list[dict] = []

	for key, stats in chapter_stats.items():
		attempted = int(attempted_by_chapter.get(key) or 0)
		correct = int(correct_by_chapter.get(key) or 0)
		stats["attempts"] = attempted
		stats["correct"] = correct
		quiz_size = int(stats["quiz_size"] or 0)
		quiz_pct = latest_quiz_pct.get(key)
		stats["quiz_pct"] = quiz_pct
		# Full chapter MCQ attempt = every quiz question answered, or a quiz submission.
		covered = bool(quiz_pct is not None) or (quiz_size > 0 and attempted >= quiz_size)
		stats["mcq_covered"] = covered

		if quiz_pct is not None:
			stats["mastery_pct"] = round(flt(quiz_pct), 1)
		elif attempted:
			stats["mastery_pct"] = round(100 * correct / attempted, 1)
		else:
			stats["mastery_pct"] = 0.0

		if time_counts.get(key):
			stats["avg_time"] = round(time_totals[key] / time_counts[key], 1)

		group = _mastery_group(
			stats["mastery_pct"],
			attempted,
			covered=covered,
		)
		stats["group"] = group
		nodes.append(
			{
				"id": key,
				"label": stats["chapter_title"],
				"mastery_pct": stats["mastery_pct"],
				"attempts": attempted,
				"group": group,
				"mcq_covered": covered,
			}
		)

	for concept, stats in concept_stats.items():
		if not stats["attempts"]:
			continue
		pct = round(100 * stats["correct"] / stats["attempts"], 1)
		entry = {"concept": concept, "mastery_pct": pct, "attempts": stats["attempts"]}
		if pct >= STRONG_MASTERY_PCT and stats["attempts"] >= 3:
			strengths.append(entry)
		elif pct < 60 and stats["attempts"] >= 2:
			weaknesses.append(entry)

	strengths.sort(key=lambda x: (-x["mastery_pct"], -x["attempts"]))
	weaknesses.sort(key=lambda x: (x["mastery_pct"], -x["attempts"]))

	# Simple sequential learning path links between chapters.
	ordered_keys = [c.course_chapter or c.name for c in chapters]
	for idx in range(1, len(ordered_keys)):
		links.append({"source": ordered_keys[idx - 1], "target": ordered_keys[idx], "value": 1})

	return {
		"learning_module": learning_module,
		"user": user,
		"generated_at": now_datetime(),
		"chapter_stats": list(chapter_stats.values()),
		"strengths": strengths[:10],
		"weaknesses": weaknesses[:10],
		"visual_map": {"nodes": nodes, "links": links},
		"quiz_history": quiz_rows,
		"revision_recommendations": _revision_recommendations(weaknesses),
	}


def _quiz_question_counts(quiz_names: list[str]) -> dict[str, int]:
	names = [name for name in quiz_names if name]
	if not names:
		return {}
	rows = frappe.db.sql(
		"""
		select parent, count(*) as n
		from `tabLMS Quiz Question`
		where parent in %(names)s
		group by parent
		""",
		{"names": names},
		as_dict=True,
	)
	return {row.parent: cint(row.n) for row in rows}


def _split_tags(raw: str | None) -> list[str]:
	if not raw:
		return []
	return [
		part.strip()
		for part in raw.split(",")
		if part.strip() and not part.strip().lower().startswith("recall:")
	]


def _is_module_assessment_title(title: str | None) -> bool:
	return "module assessment" in (title or "").lower()


def _mastery_group(mastery_pct: float, attempts: int, *, covered: bool = False) -> str:
	"""Chapter mastery group from MCQ evidence only.

	strong — chapter MCQs fully covered (quiz submission or every quiz question
	attempted) and marks >= 75%. Flashcards alone never qualify.
	"""
	pct = flt(mastery_pct)
	if covered and pct >= STRONG_MASTERY_PCT:
		return "strong"
	if not attempts and not covered:
		return "not_started"
	if pct >= DEVELOPING_MASTERY_PCT:
		return "developing"
	return "needs_work"


def _revision_recommendations(weaknesses: list[dict]) -> list[str]:
	recommendations = []
	for item in weaknesses[:5]:
		recommendations.append(
			f"Review concept '{item['concept']}' ({item['mastery_pct']}% over {item['attempts']} attempts)."
		)
	if not recommendations:
		recommendations.append("Continue chapter MCQs and flashcards to build a fuller learning map.")
	return recommendations
