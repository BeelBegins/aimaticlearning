import frappe


def run():
    meta_rows = frappe.get_all(
        "Learning Question Meta",
        filters={"learning_module": "LMOD-00553"},
        fields=["name", "lms_question", "question_role"],
    )
    role_counts = {}
    for r in meta_rows:
        role_counts[r.question_role] = role_counts.get(r.question_role, 0) + 1

    assessment_qs = frappe.get_all(
        "LMS Quiz Question",
        filters={"parent": "dispute-resolution-module-assessment-99-mcqs"},
        pluck="question",
    )
    meta_by_q = {r.lms_question: r for r in meta_rows}
    overlap = sum(1 for q in assessment_qs if q in meta_by_q)

    print(frappe.as_json({
        "role_counts_before": role_counts,
        "meta_rows": len(meta_rows),
        "assessment_questions": len(assessment_qs),
        "overlap": overlap,
    }))

    updated = 0
    for q in assessment_qs:
        meta = meta_by_q.get(q)
        if meta and meta.question_role != "Both":
            frappe.db.set_value("Learning Question Meta", meta.name, "question_role", "Both", update_modified=True)
            updated += 1
    frappe.db.commit()

    module = frappe.get_doc("Learning Module Config", "LMOD-00553")
    module.refresh_counts()
    module.save(ignore_permissions=True)
    frappe.db.commit()
    print(frappe.as_json({
        "updated_to_both": updated,
        "module_mcq_count_after": module.module_mcq_count,
        "published_flashcard_count_after": module.published_flashcard_count,
        "chapter_count_after": module.chapter_count,
    }))
