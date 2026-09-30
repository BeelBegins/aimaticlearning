import re
import frappe


def run():
    lesson = frappe.db.get_value(
        "Course Lesson", "0565 Draft notes — Chapter 6: Remedies", ["name", "body"], as_dict=True
    )
    body = lesson.body or ""
    idx = body.find("Summary of Common Remedies")
    print("idx:", idx, "len(body):", len(body))
    print("--- context before (200) ---")
    print(body[max(0, idx - 400): idx])
    print("--- context after (2000) ---")
    print(body[idx: idx + 2000])
    # count headings after this point
    after = body[idx:]
    heads = re.findall(r"<h[1-6][^>]*>", after)
    print("headings after point:", len(heads))
