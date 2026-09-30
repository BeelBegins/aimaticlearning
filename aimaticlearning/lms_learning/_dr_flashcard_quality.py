import frappe


def run():
    out = {}
    for label, course_chapter in [
        ("ch1", "0554 Chapter 1: Dispute Resolution In England & Wales"),
        ("ch6", "0564 Chapter 6: Remedies"),
        ("ch12", "0574 Chapter 12: Interim Applications"),
        ("ch21", "0592 Chapter 21: Enforcement of Judgments"),
    ]:
        cards = frappe.get_all(
            "Learning Flashcard",
            filters={"learning_module": "LMOD-00553", "course_chapter": course_chapter, "status": "Published"},
            fields=["name", "front", "back", "source_reference", "source_quote", "concept"],
            order_by="creation asc",
        )
        out[label] = [
            {
                "front": c.front,
                "back": (c.back or "")[:100],
                "source_reference": c.source_reference,
                "quote": (c.source_quote or "")[:80],
            }
            for c in cards[:8]
        ]
        fronts = [c.front for c in cards]
        out[label + "_dup_fronts"] = len(fronts) - len(set(fronts))
        quotes = [c.source_quote for c in cards]
        out[label + "_dup_quotes"] = len(quotes) - len(set(quotes))
        out[label + "_tort_mentions"] = sum(1 for c in cards if "tort" in (c.front or "").lower() or "tort" in (c.back or "").lower())
    print(frappe.as_json(out))
