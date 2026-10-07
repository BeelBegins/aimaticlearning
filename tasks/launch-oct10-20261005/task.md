# Task: launch-oct10-20261005

Superseded 2026-10-07 for pricing, free period and payments: see `tasks/pricing-subscription-20261007/task.md` and `skills/lms-billing/`. The $25 and 2-month text below is history.

Goal: Student launch on 2026-10-10. Self-service signup enrols every published
course; 2 months free and 2 free mock exams; mock attempts 10; unified notes
typography. Owner decisions below are binding for any agent.

Environment (site `lms.aimatic.tech`; local-only or live): code is committed
locally on `main` (after `89c02ab`, not pushed). Live site NOT yet updated.

Owner decisions:
- 2 months free = copy plus stored end date `User.examic_free_until`
  (signup + 60 days). No access lock, no redirect, no trial screen yet.
- Payments are out of scope. Copy only: after 2 free months £25/month (GBP) covers FLK1 and
  FLK2 together, all courses and all mocks, not per course. No payment code, gateway or Wise work in this task.
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

Status: review (live rollout done 2026-10-05; owner checks remain).

Live rollout record (2026-10-05, owner approved):
- `run-patch` add_user_free_until and set_attempt_limits on the LMS site: done
  (16 mock quizzes and the exam 3 -> 10; BLP and Tort module assessments -> 0).
- `szl` migrated (backup `20261005_204841`); owner restarted web and workers.
- Verified after restart: hooks loaded, lobby locks mocks 3 and 4, guest redirect
  works, `/terms` `/privacy` `/refund-policy` 200, signup page links them.
- Throwaway signup `nabeelmehmood448+examictest1@gmail.com` through the real
  `sign_up` endpoint: 13 enrolments, `examic_free_until` 2026-12-04, welcome email
  sent. Frappe also queued its own "Set your password" and "password changed"
  mails (standard behaviour, not our code). The test user still exists.

Remaining issues / next step:
1. Owner reviews the draft legal text. Price settled by owner: £25/month for FLK1 and FLK2 together (copy updated).
2. Delete the test user and the three SQL-probe users (needs approval).
3. Confirm academic review status of dispute-resolution, legal-services, criminal-law (all 13 published live).
4. Four SZL `aimatic` patches remain pending on the LMS site and were not run; uninstalling `aimatic` there is an owner call.
5. Unpushed commits need push approval.
6. Live change 2026-10-05 (owner approved): `Role LMS Student.home_page` set to empty (was `/lms/courses`) so `/` shows the website to everyone. Rollback: set it back to `/lms/courses`.
