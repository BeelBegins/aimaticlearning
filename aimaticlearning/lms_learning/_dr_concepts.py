import frappe


def run():
    cards = frappe.get_all(
        "Learning Flashcard",
        filters={"learning_module": "LMOD-00553", "course_chapter": "0554 Chapter 1: Dispute Resolution In England & Wales", "status": "Published"},
        fields=["name", "concept", "back", "source_quote"],
        order_by="creation asc",
    )
    for c in cards:
        print(repr(c.concept), "|", (c.back or "")[:70])
    concepts = [c.concept for c in cards]
    print("unique concepts:", len(set(concepts)), "/", len(concepts))
