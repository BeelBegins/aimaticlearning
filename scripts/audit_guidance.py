#!/usr/bin/env python3
"""Check that every agent adapter resolves to shared LMS skills."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []
skills = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())

for name in skills:
    text = (ROOT / "skills" / name / "SKILL.md").read_text()
    meta = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not meta or f"name: {name}" not in meta.group(1) or "description:" not in meta.group(1):
        errors.append(f"skills/{name}/SKILL.md: frontmatter name/description missing")
    if len(text.split()) > 1000:
        errors.append(f"skills/{name}/SKILL.md: over 1000 words, split it")
    if not (ROOT / ".cursor" / "skills" / name).exists():
        errors.append(f".cursor/skills/{name}: missing adapter link")

for adapter in (".claude/skills", ".codex/skills", ".agents/skills"):
    if not (ROOT / adapter).resolve() == (ROOT / "skills").resolve():
        errors.append(f"{adapter}: must link to skills/")

for rel in ("AGENTS.md", "CLAUDE.md", ".cursor/rules/shared-project.mdc", "docs/priorities.md"):
    if not (ROOT / rel).exists():
        errors.append(f"{rel}: missing")
if len((ROOT / "AGENTS.md").read_text().split()) > 600:
    errors.append("AGENTS.md: over 600 words")
for md in (ROOT / "tasks").glob("*/task.md"):
    if not md.read_text().startswith("# Task:"):
        errors.append(f"{md.relative_to(ROOT)}: must start with '# Task:'")

print("\n".join(errors) or "LMS guidance OK")
sys.exit(1 if errors else 0)
