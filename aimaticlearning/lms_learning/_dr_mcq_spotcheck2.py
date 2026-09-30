import frappe


def run():
    for quiz in [
        "chapter-6-remedies-chapter-mcq",
        "chapter-8-commencing-proceedings-chapter-mcq",
        "chapter-20-appeals-chapter-mcq",
    ]:
        rows = frappe.get_all(
            "LMS Quiz Question", filters={"parent": quiz}, fields=["question"], order_by="idx", limit_page_length=3
        )
        print("===", quiz, "===")
        for r in rows:
            q = frappe.get_doc("LMS Question", r.question)
            print((q.question or "")[:150])
            for i in range(1, 6):
                opt = q.get(f"option_{i}")
                correct = q.get(f"is_correct_{i}")
                if opt:
                    print("  -", opt[:90], "CORRECT" if correct else "")
            print()
