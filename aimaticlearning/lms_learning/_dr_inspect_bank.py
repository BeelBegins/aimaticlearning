from pathlib import Path
import re
from docx import Document


def run():
    path = Path("/home/nabeel/frappe-bench/sites/lms.aimatic.tech/private/files/Dispute Resolution - Quesiton Bank.docx")
    document = Document(str(path))
    paras = [" ".join((p.text or "").split()) for p in document.paragraphs]
    paras = [p for p in paras if p]
    heads = [(i, p) for i, p in enumerate(paras) if re.search(r'chapter\s*\d+', p, re.I) and len(p) < 100]
    out = [f"total non-empty paragraphs: {len(paras)}", f"chapter-like lines: {len(heads)}"]
    for i, h in heads:
        out.append(f"{i}: {h!r}")
    print("\n".join(out))
    return {"total": len(paras), "heads": len(heads)}
