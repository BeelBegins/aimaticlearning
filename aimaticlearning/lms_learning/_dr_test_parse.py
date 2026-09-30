from pathlib import Path
from aimaticlearning.lms_learning.mcq_import import parse_mcqs_from_docx


def run():
    path = Path(
        "/home/nabeel/frappe-bench/sites/lms.aimatic.tech/private/files/Dispute Resolution - Quesiton Bank.docx"
    )
    parsed = parse_mcqs_from_docx(path)
    by_section = {}
    for q in parsed:
        sid = q["section_id"]
        by_section.setdefault(sid, []).append(q)
    out = [f"total parsed questions: {len(parsed)}", f"sections: {len(by_section)}"]
    for sid in sorted(by_section):
        rows = by_section[sid]
        no_correct = sum(1 for r in rows if not any(o.get("is_correct") for o in r["options"]))
        opt_counts = {}
        for r in rows:
            opt_counts[len(r["options"])] = opt_counts.get(len(r["options"]), 0) + 1
        out.append(
            f"section {sid}: n={len(rows)} first_src={rows[0]['source_reference']} "
            f"opt_counts={opt_counts} no_correct={no_correct}"
        )
    print("\n".join(out))
    return {"total": len(parsed), "sections": len(by_section)}
