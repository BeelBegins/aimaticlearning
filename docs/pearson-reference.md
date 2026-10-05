# Pearson-style sitting: observed reference

Source: live walkthrough of `https://www.mctmocktests.com/mcts/6771baf35c9d9`
("FLK1 - Mock Test 16 - 50 Questions", QLTS School) on 2026-10-05, using the
"Pearson VUE-like Simulation" format. MCT states its player is similar to, not
identical to, the official Pearson VUE platform. Everything below was seen in
that player; do not add behaviour that is not listed here. Earlier Cursor plans
(`~/.cursor/plans/*Pearson*`) were written without seeing this page and wrongly
assumed a Skip button and a numbered review grid.

Never copy MCT branding, ads, questions or watermark into Examic.

## Flow

1. **Format modal** before the test: "Pearson VUE-like Simulation" (default,
   no feedback until the end) or "Immediate Feedback". Notes: timer is only a
   pace indicator, real SQE cannot pause. Optional "extra time" checkbox.
   (MCT then asks for an email to send the score; Examic must not.)
2. **Question screen** (one question per page). No sidebar, no site chrome.
3. **Between questions**: occasional full-page interstitial with a 10 s
   countdown and a disabled **Continue** until it ends. These are MCT ads;
   Examic does not need them.
4. **Last question -> Next** opens the **Item Review Screen**.
5. **End Test** ends the sitting. Not pressed during this walkthrough, so the
   confirm dialog is unobserved.

## Question screen layout

- **Top bar**, dark grey `#565656`, white text, Tahoma/Arial, ~80 px tall.
  Left: test title (large), under it `Calculator` (underlined C, icon).
  Right, stacked: `Time Remaining 84:59` with clock icon and a **Pause**
  button; below it `1 of 50` with a stack icon; below that
  **Flag for Review** (flag icon, underlined F) and a round speaker button
  (read aloud).
- **Body**: white. Stem in a serif face, dark `#00111d`; the final question
  line is bold. Options below as a plain vertical list.
- **Options**: an open **radio circle** followed by the text. Selecting shows
  a dotted/filled radio only. **No row highlight, no card, no letters A-E.**
- **Flag state**: the flag icon turns yellow and the "Flag for Review" text
  turns yellow. Unflagged is white.
- **Footer**, same grey `#565656`, ~40 px, fixed bottom. Buttons sit at the
  right edge with a thin divider: `Previous` (left arrow, underlined P) and
  `Next` (right arrow, underlined N). On question 1 only `Next` shows. Hover
  turns the label yellow.
- **No Skip button.** No separate submit/check button in this format.
- Keyboard hints: underlined letters are the access keys (P, N, F, C).

## Item Review Screen

- Same grey top bar: title, `Instructions` link, `Time Remaining: 83:59`.
- Centered heading **Item Review Screen**.
- Grey section bar `Section` (collapsible) with `(49 Unseen/Incomplete)`
  count at the right.
- A plain **list, one row per question** (not a number grid):
  flag icon (filled if flagged), link `Question N`, then a status in
  coloured text: `Answered` in green, `Incomplete` in red. Thin black rule
  between rows. Clicking a row opens that question.
- **Footer** same grey, 42 px: `End Test` bottom-left; at the right
  `Review All`, `Review Incomplete`, `Review Flagged` (white 18 px text,
  icons, underlined access letter).
- Pausing shows `Resume` in place of `Pause`.

## Gaps against the current Examic code

Check each against `lms_exam_tools.js` / `.css` before declaring done:

| Reference | Examic Pearson mode today |
|---|---|
| Radio circle only, no highlight, no A-E letters | CSS tries to remove highlight but still shows `.aimatic-mcq-option-letter` chips |
| Footer has only Previous/Next | Skip button exists; spec says none |
| Flag for Review is yellow when set | uses orange `is-on` button |
| Review is a row list with Answered/Incomplete status, Review All / Incomplete / Flagged | numbered grid in a modal card |
| Review reached from last Next | opened from a button |
| Whole screen is the grey bars + white body | extra card, `#eef1f4` body, padding |
| Time Remaining counts down in the top bar | verify against native timer |

## Not yet observed

- Calculator window look, Instructions text, End Test confirmation, the
  Immediate Feedback format, and mobile layout. Capture them before building
  those parts.

## Deliberate differences from the MCT player

Added after learner testing on 2026-10-05; keep them:

- **Review Screen** button at the left of the footer, so the review list can be opened
  from any question (MCT only reaches it from the last Next).
- **Exit to Mock Exams** link in the top bar (MCT has no exit).
- A review row jumps straight to its question (one native step to save the answer being
  left, then a direct set of the active question), never one question at a time.
