import frappe
from frappe.utils import now_datetime, add_to_date


def run():
    since = add_to_date(now_datetime(), minutes=-30)
    out = {}
    for dt in ["Course Lesson", "Learning Chapter Profile", "Learning Flashcard", "LMS Question", "LMS Quiz", "Learning Question Meta", "Course Chapter"]:
        rows = frappe.get_all(
            dt,
            filters={"modified": [">", since]},
            fields=["name", "modified"],
            order_by="modified desc",
            limit_page_length=500,
        )
        # Filter to rows plausibly related to dispute-resolution / LMOD-00553
        related = []
        for r in rows:
            name = (r.name or "")
            if "dispute" in name.lower() or "LMOD-00553" in name:
                related.append(r)
        out[dt] = {"total_recent": len(rows), "dr_related_recent": related[:20]}
    print(frappe.as_json(out))
    return {"since": str(since)}
