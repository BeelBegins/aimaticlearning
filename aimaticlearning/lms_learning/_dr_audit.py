import re
import json

import frappe

COURSE = "dispute-resolution"
MODULE = "LMOD-00553"


def _chapter_no(title):
    m = re.search(r"(\d+)", title or "")
    return int(m.group(1)) if m else 999


def run():
    out = {}
    out["course"] = frappe.db.get_value(
        "LMS Course", COURSE, ["name", "title", "published"], as_dict=True
    )
    out["module"] = frappe.db.get_value(
        "Learning Module Config",
        MODULE,
        [
            "name",
            "lms_course",
            "source_file",
            "target_chapter_mcq_count",
            "module_assessment_count",
            "module_assessment_quiz",
            "module_mcq_count",
            "import_status",
        ],
        as_dict=True,
    )
    profs = frappe.get_all(
        "Learning Chapter Profile",
        filters={"learning_module": MODULE},
        fields=[
            "name",
            "chapter_title",
            "course_chapter",
            "notes_lesson",
            "chapter_quiz",
            "mcq_count",
            "source_revision",
        ],
        order_by="creation asc",
    )
    profs.sort(key=lambda p: _chapter_no(p["chapter_title"]))
    for p in profs:
        if p["chapter_quiz"]:
            p["quiz_question_count"] = frappe.db.count(
                "LMS Quiz Question", {"parent": p["chapter_quiz"]}
            )
        else:
            p["quiz_question_count"] = None
        fc = frappe.db.count(
            "Learning Flashcard",
            {"learning_module": MODULE, "course_chapter": p["course_chapter"], "status": "Published"},
        )
        fc_all = frappe.db.count(
            "Learning Flashcard", {"learning_module": MODULE, "course_chapter": p["course_chapter"]}
        )
        p["flashcards_published"] = fc
        p["flashcards_total"] = fc_all
    out["profiles"] = profs

    chs = frappe.get_all("Course Chapter", filters={"course": COURSE}, fields=["name", "title"])
    order = frappe.get_all("Chapter Reference", filters={"parent": COURSE}, fields=["chapter", "idx"], order_by="idx")
    oidx = {o.chapter: o.idx for o in order}
    for c in chs:
        c["idx"] = oidx.get(c.name, 999)
    chs.sort(key=lambda c: c["idx"])
    out["chapter_order"] = chs

    print(json.dumps(out, indent=1, default=str))
    return {"n_profiles": len(profs), "n_chapters": len(chs)}
