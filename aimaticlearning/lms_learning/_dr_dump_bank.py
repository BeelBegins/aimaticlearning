from pathlib import Path
from docx import Document


def run(a=1, b=60):
    a = int(a); b = int(b)
    path = Path("/home/nabeel/frappe-bench/sites/lms.aimatic.tech/private/files/Dispute Resolution - Quesiton Bank.docx")
    document = Document(str(path))
    paras = [" ".join((p.text or "").split()) for p in document.paragraphs]
    paras = [p for p in paras if p]
    out = []
    for i in range(a, min(b, len(paras))):
        out.append(f"{i}: {paras[i]!r}")
    print("\n".join(out))
    return {"n": len(out)}
