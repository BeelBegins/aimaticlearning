"""Generalized cleanup of embedded quiz/glossary content leaking into student
notes, across every subject (generalizes the earlier Dispute-Resolution-only
dr_clean_notes.py, which was never run beyond that one subject).

Removes non-substantive sections (chapter summaries, glossaries, key terms,
exam-technique/"how questions are tested" guides, and embedded MCQ blocks
with answer keys) from Course Lesson.body and Learning Chapter Profile.notes_html.

Run with `bench --site lms.aimatic.tech execute`.
"""

import json
import os
import re
from datetime import datetime

import frappe
from bs4 import BeautifulSoup

SKIP_LESSON_TITLE = re.compile(r"chapter\s*mcq|flashcard|module\s*assessment", re.I)

JUNK_HEADING = re.compile(
    r"""^\s*(
        (chapter\s+)?summary(\s+of\s+.*)?
        |summary\s*(&|and)\s*key\s*points?
        |glossary(\s+of\s+terms)?
        |key\s*terms?
        |key\s*(study\s*)?points?
        |key\s*takeaways?
        |takeaways?
        |self[\s-]*assessment.*
        |check\s+your\s+understanding.*
        |test\s+yourself.*
        |answer\s*key.*
        |answers?\s*((and|with)\s*explanations?)?
        |(embedded\s+)?(mcqs?|multiple[\s-]choice\s+questions?).*
        |practice\s+(questions?|mcqs?).*
        |quiz.*
        |revision\s+(tips?|checklist).*
        |how\s+.*\s+is\s+tested\s+in\s+the\s+sqe1.*
        |common\s+question\s+formats?\s+include.*
        |exam\s+strateg(y|ies).*
        |conclusion
    )\s*[:.]?\s*$""",
    re.I | re.X,
)

# Headings that mark a whole terminal MCQ dump (question bank + answer key).
# Verified across every real instance found in this LMS: this heading is
# always the last (or second-to-last, followed only by a stray malformed
# options-as-heading fragment) section of the chapter, so it is safe to
# remove everything from this heading to the end of the document rather
# than stopping at the next same-level heading tag.
TERMINAL_JUNK_HEADING = re.compile(
    r"""^\s*(
        scenario[\s-]based\s+multiple[\s-]choice\s+questions?.*
        |chapter\s+\w+\s*[:\-]?\s*multiple[\s-]choice\s+questions?.*
        |question\s+\d+\s*[:.]?\s*answer\s+[a-z]\.?
    )\s*[:.]?\s*$""",
    re.I | re.X,
)

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

# Safety cap for the general JUNK_HEADING removals (summary/glossary/key-terms
# style sections run at most a few hundred to ~2500 chars in this bank). Does
# NOT apply to TERMINAL_JUNK_HEADING matches, which are allowed to be large —
# a real embedded MCQ+answer-key dump legitimately runs to 15k+ chars, and the
# heading text itself is specific enough that false positives aren't a risk.
MAX_JUNK_BLOCK_CHARS = 3000


def _heading_text(tag):
    return re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip()


def _plain_len(nodes):
    total = 0
    for node in nodes:
        getter = getattr(node, "get_text", None)
        total += len(getter(" ", strip=True)) if getter else len(str(node))
    return total


def clean_html(html: str):
    """Return (cleaned_html, removed_section_labels, skipped_oversized_labels)."""
    if not html or not html.strip():
        return html, [], []

    soup = BeautifulSoup(html, "html.parser")
    removed = []
    skipped = []
    rejected_ids = set()

    while True:
        target = None
        terminal = False
        for tag in soup.find_all(list(HEADING_TAGS)):
            if id(tag) in rejected_ids:
                continue
            text = _heading_text(tag)
            if TERMINAL_JUNK_HEADING.match(text):
                target = tag
                terminal = True
                break
            if JUNK_HEADING.match(text):
                target = tag
                terminal = False
                break
        if target is None:
            break

        level = int(target.name[1])
        label = _heading_text(target)
        doomed = [target]
        if terminal:
            # Consume to end of document — a verified-terminal MCQ dump.
            for sib in target.next_siblings:
                doomed.append(sib)
        else:
            for sib in target.next_siblings:
                name = getattr(sib, "name", None)
                if name in HEADING_TAGS and int(name[1]) <= level:
                    break
                doomed.append(sib)

            if _plain_len(doomed) > MAX_JUNK_BLOCK_CHARS:
                rejected_ids.add(id(target))
                skipped.append(f"<h{level}> {label} (oversized, {_plain_len(doomed)} chars)")
                continue

        for node in doomed:
            node.extract()
        removed.append(f"<h{level}> {label}" + (" [terminal]" if terminal else ""))

    return str(soup), removed, skipped


def _chapter_no(title):
    m = re.search(r"(\d+)", title or "")
    return int(m.group(1)) if m else 999


def _targets():
    """All Learning Chapter Profiles across every course, sorted for a stable report."""
    profiles = frappe.get_all(
        "Learning Chapter Profile",
        fields=["name", "learning_module", "chapter_title", "notes_lesson", "course_chapter"],
        order_by="learning_module asc, creation asc",
        limit_page_length=1000,
    )
    rows = []
    for p in profiles:
        course = frappe.db.get_value("Learning Module Config", p.learning_module, "lms_course")
        lesson = None
        if p.notes_lesson:
            lesson = frappe.db.get_value(
                "Course Lesson",
                p.notes_lesson,
                ["name", "title", "course", "body", "content", "quiz_id"],
                as_dict=True,
            )
        rows.append((p, course, lesson))
    rows.sort(key=lambda r: (r[1] or "", _chapter_no(r[0].chapter_title)))
    return rows


def run(apply=False):
    apply = str(apply).lower() in ("1", "true", "yes")
    rows = _targets()
    report = []
    backup = {}

    for profile, course, lesson in rows:
        entry = {"profile": profile.name, "course": course, "chapter": profile.chapter_title}

        if not lesson:
            entry["skipped"] = "no notes lesson linked"
            report.append(entry)
            continue
        if SKIP_LESSON_TITLE.search(lesson.title or ""):
            entry["skipped"] = f"activity lesson: {lesson.title}"
            report.append(entry)
            continue
        if lesson.quiz_id:
            entry["skipped"] = f"quiz-wired lesson (quiz_id={lesson.quiz_id})"
            report.append(entry)
            continue

        body = lesson.body or ""
        notes_html = frappe.db.get_value("Learning Chapter Profile", profile.name, "notes_html") or ""

        new_body, removed_body, skipped_body = clean_html(body)
        new_notes, removed_notes, skipped_notes = clean_html(notes_html)

        if not (removed_body or removed_notes or skipped_body or skipped_notes):
            continue  # nothing of interest — omit clean chapters from the report

        entry.update(
            {
                "lesson": lesson.name,
                "lesson_title": lesson.title,
                "body_before": len(body),
                "body_after": len(new_body),
                "notes_html_before": len(notes_html),
                "notes_html_after": len(new_notes),
                "removed": sorted(set(removed_body) | set(removed_notes)),
                "skipped_oversized": sorted(set(skipped_body) | set(skipped_notes)),
                "content_len": len(lesson.content or ""),
            }
        )

        if apply and (new_body != body or new_notes != notes_html):
            backup[profile.name] = {
                "lesson": lesson.name,
                "body": body,
                "notes_html": notes_html,
                "content": lesson.content,
            }
            frappe.db.set_value(
                "Course Lesson", lesson.name, {"body": new_body, "content": ""}, update_modified=True
            )
            frappe.db.set_value(
                "Learning Chapter Profile", profile.name, "notes_html", new_notes, update_modified=True
            )
            from aimaticlearning.lms_learning.content_studio import _log_manual_version

            _log_manual_version("Course Lesson", lesson.name, {"body": (body, new_body)})
            _log_manual_version("Learning Chapter Profile", profile.name, {"notes_html": (notes_html, new_notes)})
            entry["written"] = True
        else:
            entry["written"] = False

        report.append(entry)

    if apply:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = os.path.join(
            "/home/nabeel/frappe-bench/sites/lms.aimatic.tech/private/files/lms_learning_exports",
            f"leaked-notes-cleanup-backup-{stamp}.json",
        )
        with open(path, "w") as fh:
            json.dump(backup, fh, indent=1)
        frappe.db.commit()
        print(f"BACKUP: {path}")

    print(json.dumps(report, indent=1))

    total_before = sum(e.get("body_before", 0) for e in report)
    total_after = sum(e.get("body_after", 0) for e in report)
    print(f"\nTOTAL body {total_before} -> {total_after} (removed {total_before - total_after} chars)")
    print(f"chapters flagged: {len(report)}")
    print("APPLIED" if apply else "DRY RUN — nothing written")


def dry_run():
    run(apply=False)


def apply_changes():
    run(apply=True)


def verify():
    rows = _targets()
    bad = 0
    for profile, course, lesson in rows:
        if not lesson:
            continue
        body = lesson.body or ""
        notes = frappe.db.get_value("Learning Chapter Profile", profile.name, "notes_html") or ""
        match = body == notes
        leftovers = [
            _heading_text(t)
            for t in BeautifulSoup(body, "html.parser").find_all(list(HEADING_TAGS))
            if JUNK_HEADING.match(_heading_text(t)) or TERMINAL_JUNK_HEADING.match(_heading_text(t))
        ]
        closed = body.count("<article") == body.count("</article>")
        if leftovers or not closed or (lesson.content or ""):
            bad += 1
            print(
                f"{course} | {profile.chapter_title} | body={len(body)} notes_html={len(notes)} "
                f"identical={match} content_empty={not (lesson.content or '')} "
                f"article_balanced={closed} leftovers={leftovers}"
            )
    print("PROBLEMS:", bad)
