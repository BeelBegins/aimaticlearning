import re
import frappe


def run():
    lesson = frappe.db.get_value(
        "Course Lesson",
        "0567 Draft notes — Chapter 7: The Protocols and Pre-action Conduct",
        ["name", "body"],
        as_dict=True,
    )
    body = lesson.body or ""
    print("len(body):", len(body))
    heads = [(m.start(), m.group()) for m in re.finditer(r"<h[1-6][^>]*>.*?</h[1-6]>", body)]
    print("true heading tags:", len(heads))
    for pos, h in heads[:30]:
        print(pos, h[:100])
    for key in ["Key Terms", "Summary"]:
        idx = body.find(key)
        print(f"--- {key} at {idx} ---")
        print(body[max(0, idx - 100): idx + 600])
