import frappe
from frappe.utils import now_datetime, add_to_date


def run():
    since = add_to_date(now_datetime(), minutes=-15)
    out = {"now": str(now_datetime()), "since": str(since)}
    fc = frappe.get_all(
        "Learning Flashcard",
        filters={"learning_module": "LMOD-00553", "modified": [">", since]},
        fields=["name", "modified", "status", "course_chapter"],
        order_by="modified desc",
        limit_page_length=50,
    )
    out["flashcards_recent"] = fc
    qm = frappe.get_all(
        "Learning Question Meta",
        filters={"learning_module": "LMOD-00553", "modified": [">", since]},
        fields=["name", "modified", "course_chapter"],
        order_by="modified desc",
        limit_page_length=50,
    )
    out["question_meta_recent"] = qm
    print(frappe.as_json(out))
