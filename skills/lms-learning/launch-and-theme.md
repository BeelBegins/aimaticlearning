# Signup, free period, mock access and public theme

- Self-service signup (`/login#signup`, Website User) runs `validate_signup_email`
  (plain addresses only) then `start_student_signup`, which queues
  `complete_student_signup`: enrols every published course with
  `disable_self_learning = 0`, sets `User.examic_free_until` (+60 days, no access
  lock) and sends one welcome email. Existing and staff-invited users are never
  backfilled. Payments are out of scope; copy only says £25/month (GBP, FLK1 and FLK2 together) after the free period.
- Mocks 1 and 2 are free (`FREE_SITTINGS` in `exam_product.py`); 3 and 4 are locked
  for non-staff in the lobby and by a redirect in `page_renderer.py`. Mock attempts
  per session are `MAX_ATTEMPTS` (10); MCQ quizzes are unlimited.
- `bench migrate` fails on the LMS site (leftover `aimatic` app patches need
  `Item`): apply `aimaticlearning` patches with `run-patch`. Restart needs root
  `supervisorctl`, which only the owner runs.
- Terms, Privacy and Refund pages are plain drafts in `www/`.
- Resumable launch state: `tasks/launch-oct10-20261005/task.md`.
- Public `/sqe` theme: white, royal blue `#00247D`, flag red `#CF142B`, ink `#0E1B3D`.
  All of it lives in `public/css/sqe_frappe_theme.css`, scoped as
  `:is(html[data-examic-theme], html) body .sqe-site` because `lms_soft_themes.css`
  also styles `.sqe-site` with `!important`. Never use black or grey for buttons or
  their hover/active states. Logo files are `examic-study-header-uk.png` and
  `examic-study-mark-uk.svg` (originals kept). The portal theme picker has a default
  "UK Blue & Red" theme in `lms_soft_themes.js`. Live Website Settings `app_logo` still
  points at the old mark until `configure_lms_student_access` is run (needs approval).
