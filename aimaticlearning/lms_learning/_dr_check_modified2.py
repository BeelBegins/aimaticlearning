import frappe


def run():
    names = [
        "0565 Draft notes — Chapter 6: Remedies",
        "0577 Draft notes — Chapter 13: Part 36 Offers",
        "0563 Draft notes — Chapter 5: Pre-Action Considerations",
    ]
    for n in names:
        d = frappe.db.get_value(
            "Course Lesson", n, ["name", "modified", "modified_by", "owner"], as_dict=True
        )
        body_len = len(frappe.db.get_value("Course Lesson", n, "body") or "")
        print(d, "body_len=", body_len)

    # Version log for chapter 7 lesson to see recent change history
    versions = frappe.get_all(
        "Version",
        filters={"ref_doctype": "Course Lesson", "docname": "0567 Draft notes — Chapter 7: The Protocols and Pre-action Conduct"},
        fields=["name", "creation", "owner"],
        order_by="creation desc",
        limit_page_length=5,
    )
    print("versions:", versions)
