from pathlib import Path
from aimaticlearning.lms_learning.mcq_import import parse_mcqs_from_docx

CHAPTERS = [
    "Chapter 1: Dispute Resolution In England & Wales",
    "Chapter 2: New Client Considerations",
    "Chapter 3: Funding Litigation",
    "Chapter 4: Alternative Dispute Resolution",
    "Chapter 5: Pre-Action Considerations",
    "Chapter 6: Remedies",
    "Chapter 7: The Protocols and Pre-action Conduct",
    "Chapter 8: Commencing Proceedings",
    "Chapter 9: Defending A Claim",
    "Chapter 10: Drafting Statements Of Case",
    "Chapter 11: Case Management",
    "Chapter 12: Interim Applications",
    "Chapter 13: Part 36 Offers",
    "Chapter 14: Disclosure and Inspection",
    "Chapter 15: Witness Statements and Documentary Evidence",
    "Chapter 16: Expert Evidence",
    "Chapter 17: Settlement and Discontinuance",
    "Chapter 18: Trial",
    "Chapter 19: Costs",
    "Chapter 20: Appeals",
    "Chapter 21: Enforcement of Judgments",
]


def run():
    path = Path(
        "/home/nabeel/frappe-bench/sites/lms.aimatic.tech/private/files/Dispute Resolution - Quesiton Bank.docx"
    )
    parsed = parse_mcqs_from_docx(path)
    by_section = {}
    for q in parsed:
        by_section.setdefault(q["section_id"], []).append(q)
    ordered_ids = sorted(by_section)
    out = [f"total={len(parsed)} nonempty_sections={len(ordered_ids)} expected_chapters={len(CHAPTERS)}"]
    for rank, sid in enumerate(ordered_ids):
        rows = by_section[sid]
        ch = CHAPTERS[rank] if rank < len(CHAPTERS) else "???"
        out.append(f"rank={rank+1} section_id={sid} n={len(rows)} chapter_guess={ch!r}")
        out.append(f"   Q1: {rows[0]['question'][:90]!r}")
    print("\n".join(out))
    return {"ok": True}
