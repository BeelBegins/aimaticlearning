# Exam-mode harness

Headless check of `lms_exam_tools.js/.css` against a stand-in for the LMS quiz DOM.
It never touches a live site. It covers Start prompting for style on every attempt,
Pearson shell, flag, last-Next review screen, jumping to a far question, the End Test
confirm dialog sitting above the review, and normal style staying unchanged.

    PLAYWRIGHT_PATH=/path/to/node_modules/playwright CHROME_PATH=/path/to/chrome \
      node scripts/exam-mode-harness/run.js

Screenshots go to `shots/` (ignored). The harness only imitates Quiz.vue; confirm real
selectors on a test sitting before trusting a pass for a new LMS release.
