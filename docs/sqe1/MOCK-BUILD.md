# Building SQE1 mocks without missing anything

Read [FORMAT.md](FORMAT.md) and both topic checklists first. This file is the
assembly procedure. Do not build until the dry-run report exists and the user
has approved it.

## What “covers everything” means

For each mock **sitting** (FLK1 + FLK2):

1. Every Annex 4 area appears in that paper inside its percentage range.
2. Session grouping, 85/85, 153 minutes, five options, one key, closed book.
3. Ethics items appear in more than one session of the sitting (pervasive).
4. Taxation only in BLP, Property, and Wills, and at least one tax item in
   each of those areas across the three sittings.
5. At least one England/Wales difference item per sitting (property tax,
   income tax, Welsh language PD, or Senedd legislation).
6. Solicitors Accounts sampled in **both** FLK2 sessions.
7. Combined-subject items exist, but the **primary** tag stays inside the
   session list.
8. Across the three sittings, every heading in `FLK1-TOPICS.md` and
   `FLK2-TOPICS.md` is either used or explicitly listed as “bank has no
   reviewed 5-option item”.

A 150-question single-subject module assessment does not satisfy this.

## Examic course → SRA area

| SRA area | Session | Examic LMS Course |
|---|---|---|
| Business Law and Practice | FLK1 S1 | Business Law and Practice |
| Dispute Resolution | FLK1 S1 | Dispute Resolution |
| Legal Services | FLK1 S1 | Legal Services |
| Tort | FLK1 S2 | Tort Law |
| Contract Law | FLK1 S2 | Contract Law |
| Legal System (incl. public law / EU) | FLK1 S2 | Public Law |
| Wills + Accounts (wills) | FLK2 S1 | Wills and Administration of Estates; Solicitors' Accounts |
| Trusts Law | FLK2 S1 | Equity and Trust Law |
| Land Law | FLK2 S1 | Land Law |
| Property + Accounts (property) | FLK2 S2 | Property Practice; Solicitors' Accounts |
| Criminal Liability | FLK2 S2 | Criminal Law |
| Criminal Law and Practice | FLK2 S2 | Criminal Litigation |

Do not put Criminal Law items in FLK1. Do not put BLP items in FLK2.

## Item eligibility (hard rules)

Use only `LMS Question` rows that are:

- five options (`option_1`–`option_5` all set);
- exactly one `is_correct_*`;
- `Learning Question Meta.ai_generated = 0`;
- reviewed answer + explanation + source locator;
- not the historically ambiguous Criminal Law notes-only items.

Never invent a key. Never pad by duplicating a question across sittings.
Never copy Kaplan wording.

Prefer Hard, then Medium. Easy only if a heading would otherwise be empty.

## Suggested counts per 170 paper

Pick a mix that sums to 170 and respects the ranges. A balanced default:

### FLK1 (Session 1 = 85, Session 2 = 85)

| Area | Default | Allowed |
|---:|---:|---|
| BLP | 30 | 24–34 |
| Dispute Resolution | 28 | 24–34 |
| Legal Services | 27 | 20–27 |
| Tort | 29 | 24–34 |
| Contract | 28 | 24–34 |
| Legal System | 28 | 24–34 |
| **Total** | **170** | |

Adjust if a pool is short; stay inside the ranges; S1 and S2 must each be 85.

### FLK2

| Area | Default | Allowed |
|---:|---:|---|
| Wills (incl. accounts-wills) | 29 | 24–34 |
| Trusts | 28 | 24–34 |
| Land | 28 | 24–34 |
| Property (incl. accounts-property) | 29 | 24–34 |
| Criminal Liability | 28 | 24–34 |
| Criminal Law and Practice | 28 | 24–34 |
| **Total** | **170** | |

## Dry-run report (required before any write)

For each of Mock 1, 2, 3, and each of the four sessions, list:

- question name / ID
- Examic course
- SRA primary area
- topic heading from the checklist
- difficulty
- ethics flag / AML flag / tax flag / Wales flag
- whether the item is 5-option single-key human-reviewed

Then totals vs Annex 4, vs 85 per session, vs the 20% ethics+AML cap, and
headings still unused.

If DR, Legal Services, Public Law, or Criminal Law cannot fill three unique
papers inside the ranges, **stop** and report the shortfall. Do not reuse
questions silently.

## LMS records when building (after approval)

- New `LMS Quiz` per session (four quizzes per sitting × three sittings).
- `Course Lesson` with `quiz_id` set and `content = ""`.
- No auto-enrol. Leave unpublished until academic review of the dry-run.
- Backup `lms.aimatic.tech` with files before any insert.
- Time limit 153 minutes per session quiz if the quiz doctype supports it.
- After the sittings exist, `sync_frontend_report()` writes staff coverage at
  `/learning-mock-report`. Learners use `/learning-mock-exam`. No question IDs
  or keys on either page.

## Known bank gaps (2026-09-17, do not ignore)

- Criminal Law: items exist but are **not** 5-option scored. FLK2 Session 2
  cannot yet be a proper Criminal Liability paper.
- Hard tags are scarce (~73 site-wide). “Kaplan hard” is selection and
  application style, not a Hard-only paper.
- Dispute Resolution, Legal Services, and Public Law 5-option pools are
  tight for three unique 170-question FLK1 papers at SRA weights.
- 4-option questions are ineligible.
- `ai_generated = 1` items are ineligible.

Until those gaps close, the honest product is fewer unique sittings, or a
Mock 3 with documented overlap — never a fake full cover.

## Kaplan

There is no Kaplan exam report on this bench or in LMS private files. Do not
retrieve, paste, or reconstruct Kaplan papers. Style target is SRA sample
questions plus harder application from our reviewed bank.
