import frappe


def run():
    for quiz in ["chapter-6-remedies-chapter-mcq", "chapter-8-commencing-proceedings-chapter-mcq", "chapter-20-appeals-chapter-mcq"]:
        rows = frappe.get_all(
            "LMS Quiz Question",
            filters={"parent": quiz},
            fields=["question"],
            order_by="idx",
            limit_page_length=3,
        )
        print("===", quiz, "===")
        for r in rows:
            q = frappe.db.get_value("LMS Question", r.question, ["question", "type"], as_dict=True)
            opts = frappe.get_all(
                "LMS Question Option", filters={"parent": r.question}, fields=["option", "is_correct"], order_by="idx"
            )
            print(q.question[:150] if q else None)
            for o in opts:
                print("  -", o.option[:80], "CORRECT" if o.is_correct else "")
            print()
