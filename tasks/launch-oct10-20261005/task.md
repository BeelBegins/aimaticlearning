# Task: launch-oct10-20261005

Goal: Student launch on 2026-10-10. Self-service signup enrols every published
course; 2 months free and 2 free mock exams; mock attempts 10; unified notes
typography. Owner decisions below are binding for any agent.

Environment (site `lms.aimatic.tech`; local-only or live): code is committed
locally on `main` (after `89c02ab`, not pushed). Live site NOT yet updated.

Owner decisions:
- 2 months free = copy plus stored end date `User.examic_free_until`
  (signup + 60 days). No access lock, no redirect, no trial screen yet.
- Payments are out of scope. Copy only: after 2 free months $25/month = all
  courses and all mocks. No payment code, gateway or Wise work in this task.
- 2 free mocks = Mock 1 and Mock 2 (`FREE_SITTINGS = 2`); Mock 3 and 4 locked
  for non-staff (lobby tile + redirect in `page_renderer.py`).
- Mock attempts 10 per session. MCQs and module assessments unlimited.
- Existing students are left alone; no backfill. No Mock 5.
- Notes, MCQ, explanation and BLP content are out of scope (manual proofread).

Files / allowed edit paths: `lms_learning/{enrollment,exam_product,page_renderer,sqe1_hard_mocks}.py`,
`hooks.py`, `patches/{add_user_free_until,set_attempt_limits}.py`, `www/{sqe,learning_mock_exam,terms,privacy,refund-policy}.html`,
`templates/lms_learning/examic_signup_form.html`, `public/css/lms_learning.css`.

Acceptance criteria: throwaway signup shows 13 courses, one welcome email with
end date, mocks 3/4 locked and `/lms/quiz/mock-3-*` redirects, sessions show 10
attempts, notes consistent on phone and desktop.

Constraints: no core edits; live steps need approval; backup LMS only on request.

Base commit and existing local changes: backup `20261005_163213` pairs with
git `679eab8` (rollback point). Commits: be4c25a attempts, f5b2bcd mock lock,
9f52ab0 signup hardening + legal pages, a282554 typography, 6d0754a docs;
earlier f343484 enrolment, bc4de8d copy.

Skills used: `lms-learning`, `lms-exam-mode`.

Verification: `../../env/bin/python -m unittest aimaticlearning.lms_learning.test_signup_enrolment aimaticlearning.lms_learning.test_exam_product` (13 pass); typography checked on BLP, Contract, Public Law bodies at 1280 and 390 px.

Status: review (code done and committed; live rollout pending).

Remaining issues / next step:
1. Live: run `add_user_free_until` then `set_attempt_limits` on the LMS site.
   `bench migrate` on this site fails first on the leftover `aimatic` app
   (`add_item_principal_controls`: no `Item` doctype; three more SZL patches
   are pending behind it). Do not run SZL patches here; use `run-patch` for the
   two aimaticlearning patches, or uninstall `aimatic` from the LMS site (owner call).
2. Worker restart (shared with live `szl`) is needed for the hook, lock and
   `?v` asset bumps. Not done.
3. `szl` was migrated 2026-10-05 20:50 for shelf-price commit `943d548`
   (backup `20261005_204841-szl-database.sql.gz`); it also still needs a restart.
4. Terms, Privacy, Refund text is a draft: owner review before launch.
5. Three SQL-probe users (28 Sep) await owner approval to delete.
6. Open question: currency. Site copy says $25; another agent report mentions
   GBP and Wise. Owner must settle currency before any payment work.
7. `docs/current-state.md` lists dispute-resolution, legal-services,
   criminal-law as unpublished; live read-only check on 2026-10-05 shows all 13
   published. Confirm with owner whether the academic review is done.
8. Unpushed commits need push approval.
