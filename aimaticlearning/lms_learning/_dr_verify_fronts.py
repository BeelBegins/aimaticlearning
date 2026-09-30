import frappe


def run():
    profiles = frappe.get_all(
        "Learning Chapter Profile",
        filters={"learning_module": "LMOD-00553"},
        fields=["chapter_title", "course_chapter"],
        order_by="creation asc",
    )
    bad = []
    for p in profiles:
        fronts = frappe.get_all(
            "Learning Flashcard",
            filters={"learning_module": "LMOD-00553", "course_chapter": p.course_chapter, "status": "Published"},
            pluck="front",
        )
        dup = len(fronts) - len(set(fronts))
        tort = sum(1 for f in fronts if "tort" in f.lower())
        print(f"{p.chapter_title:55s} n={len(fronts):>3} dup_fronts={dup} tort_mentions={tort}")
        if dup or tort:
            bad.append(p.chapter_title)
    print("BAD:", bad)
