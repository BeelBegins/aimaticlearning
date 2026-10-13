# Signup, free period, mock access and public theme

- Self-service signup (`/login#signup`, Website User) runs `validate_signup_email`
  (plain addresses only) then `start_student_signup`, which queues
  `complete_student_signup`: enrols every published course with
  `disable_self_learning = 0`, sets `User.examic_free_until` (free month, from `Examic Billing Settings`) and creates an `Examic Subscription` and sends one welcome email. Existing and staff-invited users are never
  backfilled. Pricing, plans and payments: see `skills/lms-billing/SKILL.md`.
- Mocks 1 and 2 are free (`FREE_SITTINGS` in `exam_product.py`); 3 and 4 are locked
  for non-staff in the lobby and by a redirect in `page_renderer.py`. Mock attempts
  per session are `MAX_ATTEMPTS` (10); MCQ quizzes are unlimited.
- Check currently installed apps and available patch commands before
  migrating. The previous server's migration failure is historical and does
  not describe this Examic site. Restart only the required services.
- Public website (2026-10-13): Home (`sqe`), SQE1, Pricing, How It Works, Resources, About
  (+4 subpages), Contact and the legal pages all extend `templates/examic_site/base.html`
  (one header, footer, cookie banner; `examic_site.css`/`.js`). Set `ex_title`,
  `ex_description`, `ex_path`, `ex_active` before `extends`. Static pages carry
  `no_cache: 1` front matter because Frappe's page cache is shared by guests and students.
  Facts come from `lms_learning/public_site.py` (settings, published courses, mock count);
  never hard-code volume figures or "expert reviewed" claims. The contact form posts to
  `contact.submit_enquiry` (guest, rate limited, emails the support mailbox). Legal copy is
  EXAMIC LTD's handover text and still needs owner or legal review; the privacy provider list
  and retention periods are deliberately marked as not yet published.
- Resumable launch state: `tasks/launch-oct10-20261005/task.md`.
- Public `/sqe` theme: white, royal blue `#00247D`, flag red `#CF142B`, ink `#0E1B3D`.
  All of it lives in `public/css/sqe_frappe_theme.css`, scoped as
  `:is(html[data-examic-theme], html) body .sqe-site` because `lms_soft_themes.css`
  also styles `.sqe-site` with `!important`. Never use black or grey for buttons or
  their hover/active states. `/login` (sign in and sign up) repeats the same button
  colours in `public/css/examic_login.css`, because Frappe's own `btn-primary` is near-black. Logo files are `examic-study-header-uk.png` and
  `examic-study-mark-uk.svg` (originals kept). Live Website Settings `app_logo` still
  points at the old mark until `configure_lms_student_access` is run (needs approval).
- **Student portal theme is locked, not selectable.** There is no theme picker.
  `lms_soft_themes.js` writes one fixed `EXAMIC_THEME` tokens object (the same
  hex values as `sqe_frappe_theme.css` above) as `--examic-theme-*` custom
  properties on every `/lms` page load; `lms_soft_themes.css` carries the
  matching no-JS fallback and bridges those tokens into the `--aimatic-*`
  names `lms_student_experience.css` consumes (that file has no hardcoded
  off-brand hex left; every colour there is a token with a hex fallback that
  already matches the locked palette). If the brand palette in
  `sqe_frappe_theme.css` ever changes, update the same hex in
  `lms_soft_themes.js`'s `EXAMIC_THEME`, `lms_soft_themes.css`'s
  `html[data-examic-theme]` fallback block, and the `var(--aimatic-*, #hex)`
  fallbacks in `lms_student_experience.css` — three places, one value.
- Upstream LMS's own light/dark/system toggle (`apps/lms/frontend`) is
  deliberately hidden for students, not broken: `lms_soft_themes.js` forces
  light mode on every render, so the toggle would do nothing if left visible.
  It is hidden by matching its rendered label text, never by editing
  `apps/lms`: the desktop user-menu row labelled `"Toggle Theme"`
  (`UserDropdown.vue`) is hidden in `lms_soft_themes.js`
  (`hideUpstreamThemeToggle`, scoped to `[data-slot="item"]`, the attribute
  frappe-ui's `Menu` component puts on every dropdown row); the mobile "You"
  row labelled `"Colour mode"` (`mobileSettings.ts`) and its
  `data-testid="colour-mode-sheet"` sheet are hidden in pure CSS in
  `lms_soft_themes.css` via `[aria-label="Colour mode"]`. Both are scoped to
  `body.aimatic-lms-student`, so Administrator/Instructor/Moderator accounts
  never lose their working dark mode. If an `apps/lms` upgrade renames either
  label, these selectors silently stop matching — the toggle reappears
  looking broken again, which is the signal to update the label strings here.
- Routing: `/` shows the public site (`/sqe`) to everyone. `Role LMS Student.home_page`
  is empty on purpose (was `/lms/courses`; restore it to roll back, and keep
  `configure_lms_student_access` in step). Login still lands in `/lms` through
  `System Settings.default_app`. Logged-in users see "Open my portal" on `/sqe`, and the
  portal sidebar has an `.aimatic-site-link` back to `/sqe` — the Examic mark
  (`examic-study-mark-uk.svg`), not text, added by `addSiteLink()` in
  `lms_soft_themes.js`.
