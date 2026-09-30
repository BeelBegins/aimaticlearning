"""Learner dashboard for SQE1 prep.

Session-user data only. Lecture hours are not invented: mix uses notes,
chapter MCQs, and flashcard coverage, plus `time_seconds` only when recorded.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
import re

import frappe
from frappe.utils import cint, date_diff, flt, getdate

from aimaticlearning.lms_learning.sqe1_hard_mocks import COURSE_NAME as EXAM_COURSE
from aimaticlearning.lms_learning.revision import (
	latest_mcq_results_from_attempts,
	latest_ratings_from_attempts,
)
from aimaticlearning.lms_learning.sqe_pathway import FLK1_SUBJECTS, FLK2_SUBJECTS
from aimaticlearning.lms_learning.utils import user_can_access_course

DASHBOARD_URL = "/learning-dashboard"
SITTING_LABEL = "January 2027"
SITTING_DATE = "2027-01-31"
PATHWAYS = (
	("FLK1", "SQE1 · FLK1", FLK1_SUBJECTS),
	("FLK2", "SQE1 · FLK2", FLK2_SUBJECTS),
)


def hours_from_seconds(seconds) -> float | None:
	"""Return hours to 1 decimal, or None when nothing was timed."""
	value = flt(seconds)
	if value <= 0:
		return None
	return round(value / 3600.0, 1)


def lesson_kind(title: str | None, quiz_id: str | None) -> str:
	lowered = (title or "").lower()
	if quiz_id:
		if "module assessment" in lowered:
			return "module"
		if "flashcard" in lowered:
			return "flashcard"
		return "mcq"
	if "flashcard" in lowered:
		return "flashcard"
	return "notes"


def quiz_kind(quiz: str | None, course: str | None, title: str | None, module_quizzes: set[str]) -> str:
	if course == EXAM_COURSE:
		return "mock"
	if quiz and quiz in module_quizzes:
		return "module"
	if "module assessment" in (title or "").lower():
		return "module"
	return "practice"


def mix_ratio(done: int, total: int) -> float:
	if total <= 0:
		return 0.0
	return round(min(100.0, 100.0 * max(0, done) / total), 1)


def score_percent(correct: int, attempted: int) -> float:
	if attempted <= 0:
		return 0.0
	return round(100.0 * correct / attempted, 1)


def score_change(latest: float | None, previous: float | None) -> float | None:
	if latest is None or previous is None:
		return None
	return round(flt(latest) - flt(previous), 1)


def first_name(full_name: str | None, given: str | None = None) -> str:
	full = (full_name or "").strip()
	given_name = (given or "").strip()
	if given_name and given_name != full:
		return given_name.split()[0]
	parts = (full or given_name).split()
	return parts[0] if parts else "there"


def sitting_is_complete(score_out_of, answered) -> bool:
	"""A timed paper counts only when every question was answered."""
	out_of = cint(score_out_of)
	return out_of > 0 and cint(answered) >= out_of


_TITLE_SPLIT = re.compile(r"\s*(?:—|–|-{2,})\s*")
_TITLE_PREFIX = re.compile(
	r"^(?:chapter mcq|practice mcqs?|flashcards?|study notes|notes)$",
	re.IGNORECASE,
)


def plain_title(title: str | None) -> str:
	"""Drop em dashes used as title separators. They read as generated copy."""
	parts = [part.strip(" -") for part in _TITLE_SPLIT.split(title or "") if part.strip(" -")]
	if not parts:
		return ""
	if len(parts) >= 2 and _TITLE_PREFIX.match(parts[0]):
		return parts[-1]
	if len(parts) >= 2:
		return ": ".join(parts)
	return parts[0]


def week_start(value) -> date:
	day = getdate(value)
	return day - timedelta(days=day.weekday())


def pace_status(actual: int, planned: int) -> str:
	if actual <= 0:
		return "unstarted"
	if planned <= 0:
		return "ahead" if actual > 0 else "unstarted"
	ratio = actual / planned
	if ratio >= 1.08:
		return "ahead"
	if ratio >= 0.92:
		return "on_track"
	return "behind"


def weekly_progress(
	event_dates: list,
	*,
	start,
	sitting,
	today,
	target: int,
) -> dict:
	"""Cumulative coverage vs a linear plan. Values are item counts, not hours."""
	start_day = getdate(start)
	sitting_day = getdate(sitting)
	today_day = getdate(today)
	if sitting_day < start_day:
		sitting_day = start_day
	end_actual = min(today_day, sitting_day)
	by_week: Counter[date] = Counter()
	for raw in event_dates:
		if not raw:
			continue
		day = getdate(raw)
		if day < start_day:
			day = start_day
		if day > sitting_day:
			continue
		by_week[week_start(day)] += 1

	actual = []
	running = 0
	cursor = week_start(start_day)
	last = week_start(end_actual)
	while cursor <= last:
		running += int(by_week.get(cursor) or 0)
		actual.append({"date": str(cursor), "value": running})
		cursor += timedelta(days=7)

	span = max(date_diff(sitting_day, start_day), 1)
	planned = []
	cursor = week_start(start_day)
	last_plan = week_start(sitting_day)
	while cursor <= last_plan:
		elapsed = min(max(date_diff(cursor, start_day), 0), span)
		planned.append({"date": str(cursor), "value": round(target * elapsed / span)})
		cursor += timedelta(days=7)
	if planned and planned[-1]["value"] != target:
		planned.append({"date": str(sitting_day), "value": int(target)})

	actual_now = actual[-1]["value"] if actual else 0
	elapsed_now = min(max(date_diff(end_actual, start_day), 0), span)
	planned_now = round(target * elapsed_now / span) if target else 0
	return {
		"unit": "items",
		"start": str(start_day),
		"sitting": str(sitting_day),
		"actual": actual,
		"planned": planned,
		"actual_now": actual_now,
		"planned_now": planned_now,
		"target": int(target),
		"pace": pace_status(actual_now, planned_now),
	}


def pick_next_action(mix: dict, continue_item: dict | None, hard_cards: int) -> dict:
	if hard_cards:
		return {
			"title": "Revise Hard cards",
			"detail": "",
			"href": "/learning-revision",
		}
	if continue_item and continue_item.get("href"):
		return {
			"title": plain_title(continue_item.get("title")) or "Continue studying",
			"detail": continue_item.get("detail") or "Pick up the lesson you last opened.",
			"href": continue_item["href"],
		}
	notes = mix.get("notes") or {}
	if int(notes.get("total") or 0) and int(notes.get("done") or 0) < int(notes["total"]):
		return {
			"title": "Read the next chapter notes",
			"detail": f"{int(notes['done'])} of {int(notes['total'])} notes chapters complete.",
			"href": "/lms/courses",
		}
	mcq = mix.get("mcq") or {}
	if int(mcq.get("total") or 0) and int(mcq.get("done") or 0) < int(mcq["total"]):
		return {
			"title": "Practise chapter MCQs",
			"detail": f"{int(mcq['done'])} of {int(mcq['total'])} chapter questions attempted.",
			"href": "/lms/courses",
		}
	return {
		"title": "Sit a timed mock",
		"detail": "Practice coverage looks full. A sitting will show exam pacing.",
		"href": "/learning-mock-exam",
	}


def empty_dashboard(user: str, learner: dict) -> dict:
	return {
		"learner": learner,
		"sitting": _sitting_payload(getdate()),
		"empty_reason": "no_access",
		"next_action": {
			"title": "Browse SQE1 subjects",
			"detail": "Enrol on a subject so coverage, MCQs and revision can appear here.",
			"href": "/lms/courses",
		},
		"mix": {
			"notes": _empty_mix(),
			"mcq": _empty_mix(),
			"review": _empty_mix(),
		},
		"progress": weekly_progress([], start=getdate(), sitting=SITTING_DATE, today=getdate(), target=0),
		"recent": [],
		"scoreboard": {
			"practice": _empty_board(),
			"module": _empty_board(),
			"mock": _empty_board(),
		},
		"subjects": [],
		"recommendations": [
			"Ask your instructor to enrol you on a course before dashboard data can appear."
		],
		"user": user,
	}


def build_student_dashboard(user: str) -> dict:
	today = getdate()
	learner = _learner_payload(user)
	subjects = _accessible_subjects(user)
	if not subjects:
		return empty_dashboard(user, learner)

	courses = [row["course"] for row in subjects]
	modules = _modules_for_courses(courses)
	module_by_course = {row["lms_course"]: row for row in modules}
	module_names = [row["name"] for row in modules]
	module_quizzes = {row["module_assessment_quiz"] for row in modules if row.get("module_assessment_quiz")}
	profiles = _chapter_profiles(module_names)
	quiz_sizes = _quiz_question_counts(
		[row["chapter_quiz"] for row in profiles if row.get("chapter_quiz")] + list(module_quizzes)
	)
	flash_counts = _published_flashcard_counts(module_names)
	lessons = _course_lessons(courses)
	progress_rows = _course_progress(user, courses)
	attempts = _attempt_rows(user, module_names)
	submissions = _quiz_submissions(user)
	enrollments = _enrollments(user, courses)
	indexes = _learn_indexes(courses, [row["chapter"] for row in lessons if row.get("chapter")])

	progress_by_lesson = {row["lesson"]: row for row in progress_rows}
	kind_by_lesson = {row["name"]: lesson_kind(row.get("title"), row.get("quiz_id")) for row in lessons}

	notes_total = sum(1 for row in lessons if kind_by_lesson[row["name"]] == "notes")
	notes_done = sum(
		1
		for row in lessons
		if kind_by_lesson[row["name"]] == "notes" and (progress_by_lesson.get(row["name"]) or {}).get("status") == "Complete"
	)
	chapter_quiz_names = {
		row["chapter_quiz"]
		for row in profiles
		if row.get("chapter_quiz") and row["chapter_quiz"] not in module_quizzes
	}
	mcq_total = sum(int(quiz_sizes.get(name) or 0) for name in chapter_quiz_names)
	mcq_latest = latest_mcq_results_from_attempts(attempts)
	mcq_done = len(mcq_latest)
	mcq_correct = sum(1 for row in mcq_latest.values() if row.get("correct"))
	mcq_seconds = sum(flt(row.get("time_seconds")) for row in attempts if row.get("lms_question") and not row.get("learning_flashcard"))
	review_total = sum(int(flash_counts.get(name) or 0) for name in module_names)
	ratings = latest_ratings_from_attempts(attempts)
	review_done = len(ratings)
	hard_cards = sum(1 for rating in ratings.values() if rating == "hard")
	review_seconds = sum(flt(row.get("time_seconds")) for row in attempts if row.get("learning_flashcard"))

	mix = {
		"notes": _mix_bucket(notes_done, notes_total, None),
		"mcq": _mix_bucket(mcq_done, mcq_total, mcq_seconds),
		"review": _mix_bucket(review_done, review_total, review_seconds),
	}
	mix["review"]["hard"] = hard_cards

	event_dates = _coverage_event_dates(attempts, progress_rows, lessons, kind_by_lesson)
	observed_starts = event_dates + [row.get("creation") for row in enrollments]
	start = study_start_date(observed_starts, today, SITTING_DATE)
	progress = weekly_progress(
		event_dates,
		start=start,
		sitting=SITTING_DATE,
		today=today,
		target=notes_total + mcq_total + review_total,
	)

	continue_item = _continue_item(enrollments, lessons, indexes, kind_by_lesson)
	course_titles = {row["course"]: row["title"] for row in subjects}
	recent = _recent_activity(
		progress_rows,
		lessons,
		indexes,
		kind_by_lesson,
		course_titles,
	)
	answered = _answered_by_submission([row.name for row in submissions if row.get("course") == EXAM_COURSE])

	scoreboard = {
		"practice": _practice_board(subjects, module_by_course, attempts, submissions, module_quizzes),
		"module": _module_board(subjects, module_by_course, submissions, quiz_sizes),
		"mock": _mock_board(submissions, answered),
	}
	subject_cards = _subject_cards(
		subjects,
		module_by_course,
		enrollments,
		attempts,
		indexes,
		lessons,
		progress_rows,
	)
	next_action = pick_next_action(mix, continue_item, hard_cards)
	if next_action["href"] == "/lms/courses" and subject_cards:
		next_action["href"] = subject_cards[0].get("continue_href") or subject_cards[0]["href"]

	return {
		"learner": learner,
		"sitting": _sitting_payload(today),
		"empty_reason": None,
		"next_action": next_action,
		"mix": mix,
		"progress": progress,
		"recent": recent,
		"scoreboard": scoreboard,
		"subjects": subject_cards,
		"recommendations": _recommendations(hard_cards, mix, progress, mcq_correct, mcq_done),
		"user": user,
	}


def _empty_mix() -> dict:
	return {"done": 0, "total": 0, "percent": 0.0, "seconds": 0, "hours": None}


def _mix_bucket(done: int, total: int, seconds) -> dict:
	return {
		"done": int(done),
		"total": int(total),
		"percent": mix_ratio(done, total),
		"seconds": int(flt(seconds or 0)),
		"hours": hours_from_seconds(seconds),
	}


def _empty_board() -> dict:
	return {"groups": [], "totals": {"correct": 0, "attempted": 0, "percent": 0.0, "change": None}}


def _sitting_payload(today) -> dict:
	sitting = getdate(SITTING_DATE)
	return {
		"label": SITTING_LABEL,
		"date": str(sitting),
		"days_left": max(date_diff(sitting, getdate(today)), 0),
	}


def _learner_payload(user: str) -> dict:
	row = frappe.db.get_value("User", user, ["first_name", "full_name"], as_dict=True) or {}
	full = row.get("full_name") or user
	return {"full_name": full, "first_name": first_name(full, row.get("first_name"))}


def _accessible_subjects(user: str) -> list[dict]:
	rows = []
	for key, label, subjects in PATHWAYS:
		for subject in subjects:
			course = subject["course"]
			if not user_can_access_course(course, user):
				continue
			rows.append(
				{
					"course": course,
					"title": subject["title"],
					"pathway": key,
					"pathway_label": label,
					"href": f"/lms/courses/{course}",
				}
			)
	return rows


def _modules_for_courses(courses: list[str]) -> list[dict]:
	if not courses:
		return []
	return frappe.get_all(
		"Learning Module Config",
		filters={"lms_course": ["in", courses]},
		fields=["name", "title", "lms_course", "module_assessment_quiz"],
		limit_page_length=50,
	)


def _chapter_profiles(modules: list[str]) -> list[dict]:
	if not modules:
		return []
	return frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": ["in", modules]},
		fields=["name", "learning_module", "chapter_title", "course_chapter", "chapter_quiz"],
		limit_page_length=2000,
	)


def _quiz_question_counts(names: list[str]) -> dict[str, int]:
	wanted = [name for name in names if name]
	if not wanted:
		return {}
	rows = frappe.db.sql(
		"""
		select parent, count(*) as n
		from `tabLMS Quiz Question`
		where parent in %(names)s
		group by parent
		""",
		{"names": wanted},
		as_dict=True,
	)
	return {row.parent: cint(row.n) for row in rows}


def _published_flashcard_counts(modules: list[str]) -> dict[str, int]:
	if not modules:
		return {}
	rows = frappe.db.sql(
		"""
		select learning_module, count(*) as n
		from `tabLearning Flashcard`
		where status = 'Published' and learning_module in %(modules)s
		group by learning_module
		""",
		{"modules": modules},
		as_dict=True,
	)
	return {row.learning_module: cint(row.n) for row in rows}


def _course_lessons(courses: list[str]) -> list[dict]:
	if not courses:
		return []
	return frappe.get_all(
		"Course Lesson",
		filters={"course": ["in", courses]},
		fields=["name", "title", "quiz_id", "chapter", "course"],
		limit_page_length=5000,
	)


def _course_progress(user: str, courses: list[str]) -> list[dict]:
	if not courses:
		return []
	return frappe.get_all(
		"LMS Course Progress",
		filters={"member": user, "course": ["in", courses]},
		fields=["lesson", "status", "modified", "course", "chapter"],
		order_by="modified desc",
		limit_page_length=5000,
	)


def _attempt_rows(user: str, modules: list[str]) -> list[dict]:
	if not modules:
		return []
	return frappe.get_all(
		"Learning Attempt Detail",
		filters={"user": user, "learning_module": ["in", modules]},
		fields=[
			"learning_module",
			"course_chapter",
			"lms_question",
			"learning_flashcard",
			"correct",
			"time_seconds",
			"concept_tags",
			"modified",
		],
		order_by="modified desc",
		limit_page_length=20000,
	)


def _quiz_submissions(user: str) -> list[dict]:
	return frappe.get_all(
		"LMS Quiz Submission",
		filters={"member": user},
		fields=["name", "quiz", "quiz_title", "course", "percentage", "score", "score_out_of", "modified"],
		order_by="modified desc",
		limit_page_length=5000,
	)


def _enrollments(user: str, courses: list[str]) -> list[dict]:
	if not courses:
		return []
	return frappe.get_all(
		"LMS Enrollment",
		filters={"member": user, "course": ["in", courses], "docstatus": 0},
		fields=["course", "progress", "current_lesson", "creation", "modified"],
		limit_page_length=50,
	)


def _learn_indexes(courses: list[str], chapters: list[str]) -> dict:
	chapter_idx = {}
	lesson_idx = {}
	if courses:
		for row in frappe.get_all(
			"Chapter Reference",
			filters={"parent": ["in", courses]},
			fields=["parent", "chapter", "idx"],
			limit_page_length=2000,
		):
			chapter_idx[(row.parent, row.chapter)] = cint(row.idx)
	wanted = [name for name in chapters if name]
	if wanted:
		for row in frappe.get_all(
			"Lesson Reference",
			filters={"parent": ["in", wanted]},
			fields=["parent", "lesson", "idx"],
			limit_page_length=8000,
		):
			lesson_idx[(row.parent, row.lesson)] = cint(row.idx)
	return {"chapter": chapter_idx, "lesson": lesson_idx}


def _learn_url(course: str | None, chapter: str | None, lesson: str | None, indexes: dict) -> str | None:
	if not course:
		return None
	chapter_no = indexes["chapter"].get((course, chapter)) if chapter else None
	lesson_no = indexes["lesson"].get((chapter, lesson)) if chapter and lesson else None
	if chapter_no and lesson_no:
		return f"/lms/courses/{course}/learn/{int(chapter_no)}-{int(lesson_no)}"
	return f"/lms/courses/{course}"


def study_start_date(observed_dates: list, today, sitting) -> date:
	"""Start the plan at first real activity/enrolment, not an invented term start."""
	floor = getdate(sitting) - timedelta(days=270)
	observed = [getdate(raw) for raw in observed_dates if raw]
	start = min(observed) if observed else getdate(today) - timedelta(days=30)
	if start < floor:
		start = floor
	if start > getdate(today):
		start = getdate(today)
	return start


def _coverage_event_dates(attempts, progress_rows, lessons, kind_by_lesson) -> list:
	seen_q: set[str] = set()
	seen_c: set[str] = set()
	dates = []
	for row in reversed(list(attempts)):
		qid = row.get("lms_question")
		cid = row.get("learning_flashcard")
		if qid and qid not in seen_q:
			seen_q.add(qid)
			dates.append(row.get("modified"))
		if cid and cid not in seen_c:
			seen_c.add(cid)
			dates.append(row.get("modified"))
	notes = {row["name"] for row in lessons if kind_by_lesson.get(row["name"]) == "notes"}
	seen_n: set[str] = set()
	for row in reversed(list(progress_rows)):
		lesson = row.get("lesson")
		if lesson in notes and row.get("status") == "Complete" and lesson not in seen_n:
			seen_n.add(lesson)
			dates.append(row.get("modified"))
	return dates


def _continue_item(enrollments, lessons, indexes, kind_by_lesson) -> dict | None:
	by_name = {row["name"]: row for row in lessons}
	for row in enrollments:
		lesson = row.get("current_lesson")
		if not lesson or lesson not in by_name:
			continue
		info = by_name[lesson]
		href = _learn_url(info.get("course"), info.get("chapter"), info["name"], indexes)
		kind = kind_by_lesson.get(lesson) or "notes"
		return {
			"date": str(getdate(row.get("modified"))),
			"title": info.get("title") or "Continue studying",
			"detail": "Resume this lesson",
			"kind": kind,
			"href": href,
			"course": info.get("course"),
		}
	return None


def _recent_activity(progress_rows, lessons, indexes, kind_by_lesson, course_titles) -> list[dict]:
	by_name = {row["name"]: row for row in lessons}
	items = []
	for row in progress_rows:
		lesson = by_name.get(row.get("lesson"))
		if not lesson:
			continue
		kind = kind_by_lesson.get(lesson["name"]) or "notes"
		items.append(
			{
				"date": str(getdate(row.modified)),
				"sort": row.modified,
				"title": plain_title(lesson.get("title")) or "Lesson",
				"subject": course_titles.get(lesson.get("course")) or "",
				"kind": kind,
				"href": _learn_url(lesson.get("course"), lesson.get("chapter"), lesson["name"], indexes),
			}
		)
	items.sort(key=lambda row: row.get("sort") or "", reverse=True)
	out = []
	seen = set()
	for row in items:
		key = (row.get("title"), row.get("subject"), row.get("kind"))
		if key in seen:
			continue
		seen.add(key)
		row.pop("sort", None)
		out.append(row)
		if len(out) >= 6:
			break
	return out


def _answered_by_submission(names: list[str]) -> dict[str, int]:
	wanted = [name for name in names if name]
	if not wanted:
		return {}
	rows = frappe.db.sql(
		"""
		select parent, count(*) as n
		from `tabLMS Quiz Result`
		where parent in %(names)s
		group by parent
		""",
		{"names": wanted},
		as_dict=True,
	)
	return {row.parent: cint(row.n) for row in rows}


def _practice_board(subjects, module_by_course, attempts, submissions, module_quizzes) -> dict:
	attempts_by_module: dict[str, list] = defaultdict(list)
	for row in attempts:
		if row.get("lms_question") and not row.get("learning_flashcard"):
			attempts_by_module[row.get("learning_module")].append(row)
	subs_by_course: dict[str, list] = defaultdict(list)
	for row in submissions:
		if quiz_kind(row.get("quiz"), row.get("course"), row.get("quiz_title"), module_quizzes) != "practice":
			continue
		subs_by_course[row.get("course")].append(row)
	groups = []
	totals_correct = totals_attempted = 0
	for key, label, _subjects in PATHWAYS:
		rows = []
		for subject in subjects:
			if subject["pathway"] != key:
				continue
			module = module_by_course.get(subject["course"]) or {}
			latest = latest_mcq_results_from_attempts(attempts_by_module.get(module.get("name"), []))
			correct = sum(1 for item in latest.values() if item.get("correct"))
			attempted = len(latest)
			course_subs = subs_by_course.get(subject["course"]) or []
			latest_pct = flt(course_subs[0].percentage) if course_subs else (score_percent(correct, attempted) if attempted else None)
			previous_pct = flt(course_subs[1].percentage) if len(course_subs) > 1 else None
			rows.append(
				_board_row(
					subject["title"],
					correct,
					attempted,
					subject["href"],
					latest=latest_pct,
					previous=previous_pct,
				)
			)
			totals_correct += correct
			totals_attempted += attempted
		if rows:
			groups.append({"key": key, "title": label, "rows": rows, "totals": _board_totals(rows)})
	return {"groups": groups, "totals": {"correct": totals_correct, "attempted": totals_attempted, "percent": score_percent(totals_correct, totals_attempted), "change": None}}


def _module_board(subjects, module_by_course, submissions, quiz_sizes) -> dict:
	groups = []
	totals_correct = totals_attempted = 0
	subs_by_quiz: dict[str, list] = defaultdict(list)
	for row in submissions:
		if row.get("quiz"):
			subs_by_quiz[row.quiz].append(row)
	for key, label, _subjects in PATHWAYS:
		rows = []
		for subject in subjects:
			if subject["pathway"] != key:
				continue
			module = module_by_course.get(subject["course"]) or {}
			quiz = module.get("module_assessment_quiz")
			course_subs = subs_by_quiz.get(quiz) or []
			latest = course_subs[0] if course_subs else None
			previous = course_subs[1] if len(course_subs) > 1 else None
			attempted = cint(latest.score_out_of) if latest else int(quiz_sizes.get(quiz) or 0)
			correct = cint(latest.score) if latest else 0
			if latest and not attempted:
				attempted = 0
			href = f"/lms/courses/{subject['course']}"
			rows.append(
				_board_row(
					subject["title"],
					correct,
					attempted if latest else 0,
					href,
					latest=flt(latest.percentage) if latest else None,
					previous=flt(previous.percentage) if previous else None,
				)
			)
			if latest:
				totals_correct += correct
				totals_attempted += attempted
		if rows:
			groups.append({"key": key, "title": label, "rows": rows, "totals": _board_totals(rows)})
	return {"groups": groups, "totals": {"correct": totals_correct, "attempted": totals_attempted, "percent": score_percent(totals_correct, totals_attempted), "change": None}}


def _mock_board(submissions, answered: dict[str, int] | None = None) -> dict:
	rows = []
	answered = answered or {}
	exam_subs = [
		row
		for row in submissions
		if row.get("course") == EXAM_COURSE and sitting_is_complete(row.get("score_out_of"), answered.get(row.get("name")))
	]
	by_quiz: dict[str, list] = defaultdict(list)
	for row in exam_subs:
		by_quiz[row.quiz].append(row)
	totals_correct = totals_attempted = 0
	for quiz, course_subs in by_quiz.items():
		latest = course_subs[0]
		previous = course_subs[1] if len(course_subs) > 1 else None
		correct = cint(latest.score)
		attempted = cint(latest.score_out_of)
		rows.append(
			_board_row(
				latest.quiz_title or quiz,
				correct,
				attempted,
				"/learning-mock-exam",
				latest=flt(latest.percentage),
				previous=flt(previous.percentage) if previous else None,
			)
		)
		totals_correct += correct
		totals_attempted += attempted
	groups = [{"key": "MOCK", "title": "SQE1 sittings", "rows": rows, "totals": _board_totals(rows)}] if rows else []
	return {
		"groups": groups,
		"totals": {
			"correct": totals_correct,
			"attempted": totals_attempted,
			"percent": score_percent(totals_correct, totals_attempted),
			"change": None,
		},
	}


def _board_row(subject: str, correct: int, attempted: int, href: str, *, latest=None, previous=None) -> dict:
	percent = score_percent(correct, attempted) if attempted else 0.0
	return {
		"subject": plain_title(subject),
		"correct": int(correct),
		"attempted": int(attempted),
		"percent": percent,
		"latest": None if latest is None else round(flt(latest), 1),
		"change": score_change(latest, previous),
		"href": href,
	}


def _board_totals(rows: list[dict]) -> dict:
	correct = sum(int(row["correct"]) for row in rows)
	attempted = sum(int(row["attempted"]) for row in rows)
	changes = [row["change"] for row in rows if row.get("change") is not None]
	return {
		"correct": correct,
		"attempted": attempted,
		"percent": score_percent(correct, attempted),
		"change": round(sum(changes) / len(changes), 1) if changes else None,
	}


def _subject_cards(subjects, module_by_course, enrollments, attempts, indexes, lessons, progress_rows):
	enroll_by_course = {row.course: row for row in enrollments}
	attempts_by_module: dict[str, list] = defaultdict(list)
	for row in attempts:
		attempts_by_module[row.get("learning_module")].append(row)
	lessons_by_course: dict[str, list] = defaultdict(list)
	for row in lessons:
		lessons_by_course[row.get("course")].append(row)
	complete_by_course: Counter[str] = Counter()
	for row in progress_rows:
		if row.get("status") == "Complete" and row.get("course"):
			complete_by_course[row.course] += 1
	lesson_course = {row["name"]: row.get("course") for row in lessons}
	outline_by_course: Counter[str] = Counter()
	for (_chapter, lesson_name) in indexes["lesson"]:
		course = lesson_course.get(lesson_name)
		if course:
			outline_by_course[course] += 1
	cards = []
	for subject in subjects:
		module = module_by_course.get(subject["course"]) or {}
		enroll = enroll_by_course.get(subject["course"])
		latest = latest_mcq_results_from_attempts(
			[row for row in attempts_by_module.get(module.get("name"), []) if row.get("lms_question")]
		)
		attempted = len(latest)
		correct = sum(1 for row in latest.values() if row.get("correct"))
		course_lessons = lessons_by_course[subject["course"]]
		continue_href = subject["href"]
		if enroll and enroll.get("current_lesson"):
			match = next((row for row in course_lessons if row["name"] == enroll.current_lesson), None)
			if match:
				continue_href = _learn_url(match.get("course"), match.get("chapter"), match["name"], indexes) or subject["href"]
		total_lessons = outline_by_course[subject["course"]] or len(course_lessons)
		cards.append(
			{
				"course": subject["course"],
				"title": subject["title"],
				"pathway": subject["pathway"],
				"href": subject["href"],
				"continue_href": continue_href,
				"progress": mix_ratio(complete_by_course[subject["course"]], total_lessons),
				"mcq_percent": score_percent(correct, attempted) if attempted else 0.0,
				"attempted": attempted,
			}
		)
	return cards


def _recommendations(hard_cards: int, mix: dict, progress: dict, mcq_correct: int, mcq_done: int) -> list[str]:
	lines = []
	if hard_cards:
		lines.append(f"Revise {hard_cards} Hard flashcard{'s' if hard_cards != 1 else ''}.")
	pace = progress.get("pace")
	if pace == "behind":
		lines.append("Coverage is behind the January 2027 plan. Add a notes or MCQ block today.")
	elif pace == "ahead":
		lines.append("You are ahead of the default study plan. Keep the same weekly cadence.")
	elif pace == "unstarted":
		lines.append("Complete a notes lesson or chapter MCQ so this board can track coverage.")
	notes = mix.get("notes") or {}
	if notes.get("total") and notes.get("done", 0) < notes["total"] * 0.3:
		lines.append("Notes coverage is still thin. Read the next unread chapter before more MCQs.")
	if mcq_done and score_percent(mcq_correct, mcq_done) < 60:
		lines.append(f"Chapter MCQ accuracy is {score_percent(mcq_correct, mcq_done):.0f}%. Retry incorrect items from Revision.")
	if not lines:
		lines.append("Keep rotating notes, chapter MCQs and flashcards. Timed mocks wait until coverage is broader.")
	return lines[:5]
