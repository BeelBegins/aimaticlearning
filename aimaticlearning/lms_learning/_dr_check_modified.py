import frappe


def run():
    names = [
        "0555 Draft notes — Chapter 1: Dispute Resolution In England & Wales",
        "0567 Draft notes — Chapter 7: The Protocols and Pre-action Conduct",
        "0569 Draft notes — Chapter 9: Defending A Claim",
        "0571 Draft notes — Chapter 10: Drafting Statements Of Case",
        "0573 Draft notes — Chapter 11: Case Management",
        "0585 Draft notes — Chapter 17: Settlement and Discontinuance",
    ]
    for n in names:
        d = frappe.db.get_value(
            "Course Lesson", n, ["name", "modified", "modified_by", "owner", "creation"], as_dict=True
        )
        body_len = len(frappe.db.get_value("Course Lesson", n, "body") or "")
        print(d, "body_len=", body_len)
