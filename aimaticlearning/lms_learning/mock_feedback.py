"""Post-submission score/area/answer-key report for SQE1 hard mock sittings.

Released immediately per student after their own submission (by design —
see docs/current-state.md). Does not touch LMS Quiz.show_answers, which stays
0 so the exam itself remains closed-book; this is a separate, explicit
download action after the attempt is already scored.

Timing/pace feedback (as in third-party SQE mock reports) is intentionally
not included: LMS Quiz Submission and LMS Quiz Result carry no per-question
or per-attempt timestamp field, so any pace numbers would have to be invented.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import escape_html
from frappe.utils.pdf import get_pdf

from aimaticlearning.lms_learning.statistics import can_view_statistics

AREA_DISPLAY = {
	"business-law-practice-blp": "Business Law and Practice",
	"dispute-resolution": "Dispute Resolution",
	"legal-services": "Legal Services",
	"tort-law": "Tort",
	"contract-law": "Contract",
	"public-law": "The English Legal System and Constitutional Law",
	"wills-and-administration-of-estates": "Wills and Administration of Estates",
	"equity-and-trust-law": "Equity and Trust Law",
	"land-law": "Land Law",
	"property-practice": "Property Practice",
	"solicitors-accounts": "Solicitors' Accounts",
	"criminal-litigation": "Criminal Litigation",
	"criminal-law": "Criminal Law",
}

BANDS = ((70, "Good"), (50, "Average"))


def _band(pct: int) -> str:
	for threshold, label in BANDS:
		if pct >= threshold:
			return label
	return "Weak"


def _correct_index(row: dict) -> int | None:
	for i in range(1, 6):
		if int(row.get(f"is_correct_{i}") or 0):
			return i
	return None


def _submission_rows(submission: str) -> list[dict]:
	return frappe.db.sql(
		"""
		SELECT r.question_name, r.answer, r.is_correct,
		       q.question, q.option_1, q.option_2, q.option_3, q.option_4, q.option_5,
		       q.is_correct_1, q.is_correct_2, q.is_correct_3, q.is_correct_4, q.is_correct_5,
		       q.explanation_1, q.explanation_2, q.explanation_3, q.explanation_4, q.explanation_5,
		       m.concept, m.source_reference, cfg.lms_course
		FROM `tabLMS Quiz Result` r
		INNER JOIN `tabLMS Question` q ON q.name = r.question_name
		LEFT JOIN `tabLearning Question Meta` m ON m.lms_question = q.name
		LEFT JOIN `tabLearning Module Config` cfg ON cfg.name = m.learning_module
		WHERE r.parent = %s
		ORDER BY r.idx
		""",
		(submission,),
		as_dict=True,
	)


def _check_access(sub: dict) -> None:
	user = frappe.session.user
	if user == "Guest":
		frappe.throw(_("You do not have access to this report."), frappe.PermissionError)
	if user == sub.member or can_view_statistics(user):
		return
	frappe.throw(_("You do not have access to this report."), frappe.PermissionError)


def build_submission_report(submission: str) -> dict:
	sub = frappe.db.get_value(
		"LMS Quiz Submission",
		submission,
		[
			"name", "member", "member_name", "quiz", "quiz_title", "course",
			"score", "score_out_of", "percentage", "passing_percentage", "creation",
		],
		as_dict=True,
	)
	if not sub:
		frappe.throw(_("Submission not found."))
	_check_access(sub)

	rows = _submission_rows(submission)
	areas: dict[str, dict] = {}
	key_rows = []
	for row in rows:
		label = AREA_DISPLAY.get(row.lms_course, row.lms_course or "General")
		bucket = areas.setdefault(label, {"correct": 0, "total": 0, "strengths": [], "weaknesses": []})
		bucket["total"] += 1
		concept = (row.concept or "").strip() or "Untagged"
		if row.is_correct:
			bucket["correct"] += 1
			bucket["strengths"].append(concept)
		else:
			bucket["weaknesses"].append(concept)

		correct_idx = _correct_index(row)
		key_rows.append(
			{
				"question": row.question,
				"options": [row.get(f"option_{i}") for i in range(1, 6)],
				"correct_option": row.get(f"option_{correct_idx}") if correct_idx else None,
				"your_answer": row.answer,
				"is_correct": bool(row.is_correct),
				"explanation": row.get(f"explanation_{correct_idx}") if correct_idx else None,
				"source_reference": row.source_reference,
				"concept": concept,
				"area": label,
			}
		)

	area_summary = []
	for label, b in areas.items():
		pct = round(100 * b["correct"] / b["total"]) if b["total"] else 0
		area_summary.append(
			{
				"area": label,
				"correct": b["correct"],
				"total": b["total"],
				"percentage": pct,
				"band": _band(pct),
				"strengths": sorted(set(b["strengths"]))[:8],
				"weaknesses": sorted(set(b["weaknesses"]))[:8],
			}
		)
	area_summary.sort(key=lambda a: a["percentage"])

	return {
		"submission": sub.name,
		"member": sub.member,
		"member_name": sub.member_name or sub.member,
		"quiz_title": sub.quiz_title,
		"date_completed": str(sub.creation),
		"total_questions": sub.score_out_of,
		"score": sub.score,
		"percentage": sub.percentage,
		"passing_percentage": sub.passing_percentage,
		"passed": sub.percentage >= sub.passing_percentage,
		"areas": area_summary,
		"answer_key": key_rows,
	}


def _esc(text) -> str:
	return escape_html(text or "")


def render_report_html(report: dict) -> str:
	overall_band = _band(report["percentage"])
	pass_line = "PASS" if report["passed"] else "BELOW PASS THRESHOLD"
	area_rows = "".join(
		f"""
		<tr>
			<td>{_esc(a['area'])}</td>
			<td>{a['correct']}/{a['total']} ({a['percentage']}%)</td>
			<td>{_esc(a['band'])}</td>
			<td>{_esc(', '.join(a['strengths']) or '-')}</td>
			<td>{_esc(', '.join(a['weaknesses']) or '-')}</td>
		</tr>
		"""
		for a in report["areas"]
	)
	key_rows = ""
	for i, k in enumerate(report["answer_key"], start=1):
		status = "Correct" if k["is_correct"] else "Incorrect"
		options_html = "".join(
			f"<li>{_esc(opt)}{' &#10003; correct' if opt == k['correct_option'] else ''}"
			f"{' (your answer)' if opt == k['your_answer'] else ''}</li>"
			for opt in k["options"]
			if opt
		)
		key_rows += f"""
		<div class="question-block">
			<p class="q-meta">Q{i} &middot; {_esc(k['area'])} &middot; {_esc(k['concept'])} &middot; {status}</p>
			<p class="q-text">{_esc(k['question'])}</p>
			<ul>{options_html}</ul>
			{f'<p class="q-explain">{_esc(k["explanation"])}</p>' if k['explanation'] else ''}
			{f'<p class="q-source">Source: {_esc(k["source_reference"])}</p>' if k['source_reference'] else ''}
		</div>
		"""
	return f"""
	<html>
	<head>
	<style>
		body {{ font-family: Arial, sans-serif; font-size: 12px; color: #1a1a1a; }}
		h1 {{ font-size: 18px; margin-bottom: 4px; }}
		h2 {{ font-size: 14px; margin-top: 24px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
		table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
		th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; font-size: 11px; }}
		th {{ background: #f2f2f2; }}
		.summary {{ margin: 12px 0; }}
		.question-block {{ margin-bottom: 14px; page-break-inside: avoid; }}
		.q-meta {{ color: #666; font-size: 10px; margin-bottom: 2px; }}
		.q-text {{ font-weight: bold; margin: 2px 0; }}
		.q-explain {{ background: #f7f7f7; padding: 6px; margin-top: 4px; }}
		.q-source {{ color: #666; font-size: 10px; }}
	</style>
	</head>
	<body>
		<h1>{_esc(report['quiz_title'])}</h1>
		<div class="summary">
			<p>Candidate: {_esc(report['member_name'])}</p>
			<p>Date completed: {_esc(report['date_completed'])}</p>
			<p>Total questions: {report['total_questions']}</p>
			<p>Score: {report['score']}/{report['total_questions']} &mdash; {report['percentage']}% ({overall_band}) &mdash; {pass_line}</p>
		</div>
		<h2>Performance by Area of Law</h2>
		<table>
			<tr><th>Area</th><th>Score</th><th>Band</th><th>Strengths (topics)</th><th>Weaknesses (topics)</th></tr>
			{area_rows}
		</table>
		<h2>Answer Key</h2>
		{key_rows}
	</body>
	</html>
	"""


def build_submission_report_pdf(submission: str) -> bytes:
	report = build_submission_report(submission)
	html = render_report_html(report)
	return get_pdf(html)


def download_mock_feedback_pdf(submission: str):
	pdf = build_submission_report_pdf(submission)
	frappe.local.response.filename = f"{submission}-feedback.pdf"
	frappe.local.response.filecontent = pdf
	frappe.local.response.type = "download"
