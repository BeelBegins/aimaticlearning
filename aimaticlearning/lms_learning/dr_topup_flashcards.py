"""Top up Chapter 10 (+2) and Chapter 20 (+4) to reach 30 Published flashcards
each, using additional exact-quote sentences from their own cleaned notes_html
not already used by an existing card. Also retire Chapter 8's stray Draft
duplicates (never delete, per hard rule).
"""

import html
import re

import frappe

from aimaticlearning.lms_learning.dr_fix_flashcard_fronts import derive_heading, make_front

MODULE = "LMOD-00553"

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\u00a3])")


def _plain(html_text: str) -> str:
	text = html.unescape(html_text or "")
	text = re.sub(r"<[^>]+>", " ", text)
	return re.sub(r"\s+", " ", text).strip()


FRAGMENT_SPLIT_RE = re.compile(r"(?<=[.;:])\s+(?=[A-Z0-9\u00a3])")


def _candidates(notes_html: str, used_quotes: set[str]) -> list[str]:
	plain = _plain(notes_html)
	sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(plain) if s.strip()]
	out = []
	for s in sentences:
		if len(s) < 40 or len(s) > 400 or s in used_quotes:
			continue
		out.append(s)
	if len(out) < 6:
		# Thin chapter: also split on ';'/':' for extra distinct fragments.
		for frag in FRAGMENT_SPLIT_RE.split(plain):
			frag = frag.strip()
			if len(frag) < 30 or len(frag) > 400:
				continue
			if frag in used_quotes or frag in out:
				continue
			out.append(frag)
	return out


def run(apply=False):
	apply = str(apply).lower() in ("1", "true", "yes")
	targets = [
		("Chapter 10: Drafting Statements Of Case", "0570 Chapter 10: Drafting Statements Of Case", 2),
		("Chapter 20: Appeals", "0590 Chapter 20: Appeals", 4),
	]
	report = {}
	for title, course_chapter, need in targets:
		profile = frappe.db.get_value(
			"Learning Chapter Profile",
			{"learning_module": MODULE, "course_chapter": course_chapter},
			["name", "notes_html"],
			as_dict=True,
		)
		existing = frappe.get_all(
			"Learning Flashcard",
			filters={"learning_module": MODULE, "course_chapter": course_chapter, "status": "Published"},
			fields=["front", "source_quote"],
		)
		used_fronts = {e.front for e in existing}
		used_quotes = {_plain(e.source_quote) for e in existing}
		candidates = _candidates(profile.notes_html, used_quotes)
		created = []
		for cand in candidates:
			if len(created) >= need:
				break
			heading, is_def = derive_heading(cand)
			front = make_front(heading, is_def)
			n = 2
			base = front
			while front in used_fronts:
				front = f"{base[:-1]} ({n})" if base.endswith("?") else f"{base} ({n})"
				n += 1
			used_fronts.add(front)
			back = cand if len(cand) <= 500 else cand[:499].rsplit(" ", 1)[0] + "…"
			card = {
				"front": front,
				"back": cand,
				"concept": heading[:140],
				"source_reference": f"{title} notes",
				"source_quote": cand,
			}
			created.append(card)
			if apply:
				doc = frappe.get_doc(
					{
						"doctype": "Learning Flashcard",
						"learning_module": MODULE,
						"course_chapter": course_chapter,
						"concept": card["concept"],
						"front": card["front"],
						"back": card["back"],
						"difficulty": "Medium",
						"source_reference": card["source_reference"],
						"source_quote": card["source_quote"],
						"revision": 1,
						"ai_generated": 0,
						"status": "Published",
					}
				)
				doc.insert(ignore_permissions=True)
		report[title] = {"needed": need, "created": len(created), "cards": created}

	if apply:
		frappe.db.commit()
	print(frappe.as_json(report))
	return report
