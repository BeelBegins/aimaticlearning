import re
import frappe


def run():
    prof = frappe.db.get_value(
        "Learning Chapter Profile",
        {"learning_module": "LMOD-00553", "chapter_title": "Chapter 7: The Protocols and Pre-action Conduct"},
        ["name", "notes_lesson"],
        as_dict=True,
    )
    print("profile:", prof)
    lesson_name = prof.notes_lesson
    body = frappe.db.get_value("Course Lesson", lesson_name, "body") or ""
    print("lesson_name repr:", repr(lesson_name))
    print("len(body):", len(body))
    heads = [(m.start(), m.group()) for m in re.finditer(r"<h[1-6][^>]*>.*?</h[1-6]>", body)]
    print("true heading tags:", len(heads))
    idx = body.find("Key Terms")
    print("Key Terms idx:", idx)
    print(body[max(0, idx - 60): idx + 400])
    idx2 = body.find("Summary")
    print("Summary idx:", idx2)
    print(body[max(0, idx2 - 60): idx2 + 400])
