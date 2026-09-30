import frappe


def run():
    out = {}
    for mod, label in [("LMOD-00526", "contract"), ("LMOD-00662", "tort")]:
        cards = frappe.get_all(
            "Learning Flashcard",
            filters={"learning_module": mod, "status": "Published"},
            fields=["name", "front", "back", "source_reference", "source_quote", "concept"],
            order_by="creation asc",
            limit_page_length=8,
        )
        out[label] = [
            {
                "front": c.front,
                "back": (c.back or "")[:90],
                "concept": c.concept,
                "ref": c.source_reference,
            }
            for c in cards
        ]
        fronts = frappe.get_all(
            "Learning Flashcard",
            filters={"learning_module": mod, "status": "Published"},
            pluck="front",
        )
        out[label + "_total"] = len(fronts)
        out[label + "_unique_fronts"] = len(set(fronts))
    print(frappe.as_json(out))
