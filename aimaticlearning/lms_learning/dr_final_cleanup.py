import frappe


def run():
    out = {}
    # 1. Retire Chapter 8's stray Draft flashcards (never delete).
    drafts = frappe.get_all(
        "Learning Flashcard",
        filters={
            "learning_module": "LMOD-00553",
            "course_chapter": "3893 Chapter 8: Commencing Proceedings",
            "status": "Draft",
        },
        pluck="name",
    )
    for name in drafts:
        frappe.db.set_value("Learning Flashcard", name, "status", "Retired", update_modified=True)
    out["retired_ch8_drafts"] = len(drafts)

    # 2. Refresh cached counters on every Learning Chapter Profile.
    profiles = frappe.get_all(
        "Learning Chapter Profile", filters={"learning_module": "LMOD-00553"}, pluck="name"
    )
    refreshed = 0
    for p in profiles:
        doc = frappe.get_doc("Learning Chapter Profile", p)
        doc.refresh_mcq_count()
        refreshed += 1
    out["profiles_refreshed"] = refreshed

    # 3. Refresh module-level counters.
    module = frappe.get_doc("Learning Module Config", "LMOD-00553")
    module.refresh_counts()
    module.save(ignore_permissions=True)
    out["module_after"] = {
        "target_chapter_mcq_count": module.target_chapter_mcq_count,
        "module_assessment_count": module.module_assessment_count,
        "module_mcq_count": module.module_mcq_count,
        "flashcard_target": module.flashcard_target,
    }

    frappe.db.commit()
    print(frappe.as_json(out))
