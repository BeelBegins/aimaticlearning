import html
import re
import frappe


def _plain(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def run():
    out = {}
    for label, course_chapter in [
        ("ch10", "0570 Chapter 10: Drafting Statements Of Case"),
        ("ch20", "0590 Chapter 20: Appeals"),
    ]:
        profile = frappe.db.get_value(
            "Learning Chapter Profile",
            {"learning_module": "LMOD-00553", "course_chapter": course_chapter},
            ["name", "notes_html", "chapter_title"],
            as_dict=True,
        )
        cards = frappe.get_all(
            "Learning Flashcard",
            filters={"learning_module": "LMOD-00553", "course_chapter": course_chapter, "status": "Published"},
            fields=["name", "front", "source_reference", "source_quote"],
        )
        plain_notes = _plain(profile.notes_html)
        out[label] = {
            "profile": profile.name,
            "chapter_title": profile.chapter_title,
            "notes_html_len": len(profile.notes_html or ""),
            "plain_len": len(plain_notes),
            "published_count": len(cards),
            "existing_fronts": [c.front for c in cards],
            "existing_quotes_sample": [c.source_quote[:60] for c in cards[:5]],
        }
    print(frappe.as_json(out))
