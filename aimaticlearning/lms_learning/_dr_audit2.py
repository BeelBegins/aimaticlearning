import frappe


def run():
    out = {}
    # Module assessment quiz
    quiz = frappe.db.get_value(
        "LMS Quiz",
        "dispute-resolution-module-assessment-99-mcqs",
        ["name", "title", "total_marks"],
        as_dict=True,
    )
    qcount = frappe.db.count("LMS Quiz Question", {"parent": "dispute-resolution-module-assessment-99-mcqs"})
    out["module_assessment_quiz"] = quiz
    out["module_assessment_qcount"] = qcount

    # Module Assessment chapter (idx 22, name 7387)
    ma_chapter = frappe.db.get_value("Course Chapter", {"course": "dispute-resolution", "title": "Module Assessment"}, "name")
    out["ma_chapter"] = ma_chapter
    if ma_chapter:
        lrefs = frappe.get_all("Lesson Reference", filters={"parent": ma_chapter}, fields=["lesson", "idx"], order_by="idx")
        lessons = []
        for lr in lrefs:
            d = frappe.db.get_value("Course Lesson", lr.lesson, ["name", "title", "quiz_id"], as_dict=True)
            lessons.append(d)
        out["ma_chapter_lessons"] = lessons

    # Flashcard status breakdown per thin chapter
    for ch_title, course_chapter in [
        ("Chapter 8", "3893 Chapter 8: Commencing Proceedings"),
        ("Chapter 10", "0570 Chapter 10: Drafting Statements Of Case"),
        ("Chapter 17", "0584 Chapter 17: Settlement and Discontinuance"),
        ("Chapter 20", "0590 Chapter 20: Appeals"),
    ]:
        rows = frappe.get_all(
            "Learning Flashcard",
            filters={"learning_module": "LMOD-00553", "course_chapter": course_chapter},
            fields=["name", "status", "front"],
        )
        status_counts = {}
        for r in rows:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
        out[f"flashcards_{ch_title}"] = status_counts

    # Module config counters
    mod = frappe.db.get_value(
        "Learning Module Config",
        "LMOD-00553",
        ["target_chapter_mcq_count", "module_assessment_count", "module_mcq_count", "flashcard_target"],
        as_dict=True,
    )
    out["module_config"] = mod

    print(frappe.as_json(out))
