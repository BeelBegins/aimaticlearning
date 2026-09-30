"""Fix broken 'tort principle' template fronts on Dispute Resolution flashcards.

Keeps back / source_quote / source_reference untouched (already valid, exact
notes quotes). Only rewrites `front` (and the placeholder `concept`) using a
deterministic heading/lead-phrase derived from the existing back text — no
AI, no OpenRouter, no new source material.
"""

import html
import re

import frappe

MODULE = "LMOD-00553"

HEADING_RE = re.compile(r"^([A-Z][^\-:–]{2,58}?)\s*[\-:–]\s+\S")
# Prefer a natural break: sentence end, semicolon, or a clause boundary
# (comma / "which" / "that" / "where" / "unless") within a readable span.
BREAK_RE = re.compile(
	r"^(.{15,110}?)(?:(?<!\(.)[.;](?=\s|$)|(?<!e\.g)(?<!i\.e)(?<!\betc),\s|"
	r"\s+(?:which|that|where|unless|provided|before|after|so that)\b)",
	re.I,
)


def _clean(text: str) -> str:
	text = html.unescape(text or "")
	text = re.sub(r"<[^>]+>", " ", text)
	return re.sub(r"\s+", " ", text).strip()


def derive_heading(back: str) -> str:
	text = _clean(back)
	m = HEADING_RE.match(text)
	if m:
		heading = m.group(1).strip().rstrip(".:;,")
		if len(heading) >= 3:
			return heading, True
	m2 = BREAK_RE.match(text)
	if m2:
		lead = m2.group(1).strip()
	else:
		words = text.split()
		lead = " ".join(words[:12]).rstrip(".,;:")
	return lead, False


def make_front(heading: str, is_definition: bool) -> str:
	if is_definition:
		return f"What is {heading}?"
	lead = heading[0].lower() + heading[1:] if heading[:1].isupper() and not heading[:2].isupper() else heading
	return f'What do the notes say about "{lead}"?'


def build_updates(course_chapter: str, status_filter="Published"):
	cards = frappe.get_all(
		"Learning Flashcard",
		filters={"learning_module": MODULE, "course_chapter": course_chapter, "status": status_filter},
		fields=["name", "front", "back", "concept"],
		order_by="creation asc",
	)
	used_fronts = set()
	updates = []
	for c in cards:
		back = c.back or ""
		heading, is_def = derive_heading(back)
		front = make_front(heading, is_def)
		base_front = front
		n = 2
		while front in used_fronts:
			front = f"{base_front[:-1]} ({n})?" if base_front.endswith("?") else f"{base_front} ({n})"
			n += 1
		used_fronts.add(front)
		updates.append(
			{
				"name": c.name,
				"old_front": c.front,
				"new_front": front,
				"old_concept": c.concept,
				"new_concept": heading[:140],
			}
		)
	return updates


def run(apply=False, chapters=None):
	apply = str(apply).lower() in ("1", "true", "yes")
	profiles = frappe.get_all(
		"Learning Chapter Profile",
		filters={"learning_module": MODULE},
		fields=["name", "chapter_title", "course_chapter"],
		order_by="creation asc",
	)
	report = {}
	total = 0
	changed = 0
	for p in profiles:
		if chapters and p.chapter_title not in chapters:
			continue
		updates = build_updates(p.course_chapter)
		report[p.chapter_title] = {
			"count": len(updates),
			"sample": updates[:5],
		}
		total += len(updates)
		if apply:
			for u in updates:
				if u["new_front"] != u["old_front"] or u["new_concept"] != u["old_concept"]:
					frappe.db.set_value(
						"Learning Flashcard",
						u["name"],
						{"front": u["new_front"], "concept": u["new_concept"]},
						update_modified=True,
					)
					changed += 1
	if apply:
		frappe.db.commit()
	print(frappe.as_json({"total_cards": total, "changed": changed, "report": report}))
	return {"total_cards": total, "changed": changed}
