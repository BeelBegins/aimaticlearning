import frappe


def run():
    for cc in [
        "0562 Chapter 5: Pre-Action Considerations",
        "0564 Chapter 6: Remedies",
        "0566 Chapter 7: The Protocols and Pre-action Conduct",
    ]:
        cards = frappe.get_all(
            "Learning Flashcard",
            filters={"learning_module": "LMOD-00553", "course_chapter": cc, "status": "Published"},
            fields=["front"],
        )
        for c in cards:
            if "tort" in c.front.lower():
                print(cc, "->", c.front)
