# Skill: make-submissions

Uploading assessed work to the learning portal. This skill exists mostly to stop the two known ways a
submission goes wrong: uploading before review, and assuming a silent page means success.

## The gate, once more

Nothing is submitted without the learner's explicit go-ahead **after they have read the final
version**. Their declaration of authenticity is theirs to make; the coach never ticks it on their
behalf.

## The mechanics (Playwright)

- Make-a-submission is a toggle button, not a visible form. Toggle it first; the form appears after.
- The file input is hidden. Drive it with `setInputFiles` on the input element directly - do not click
  an "upload" button and wait for a chooser unless you have verified one opens.
- **After upload, a "Submit for marking" confirmation dialog appears - but it can sit underneath an
  older stale "delete draft?" dialog.** If submission clicks appear to do nothing, look for the
  delete dialog (z-index 1049) hiding the submit dialog (z-index 1050). Close the stale one, confirm
  the real one.
- **Deleting a draft can wipe recorded OTJ hours.** Do not delete a draft to "start clean" unless the
  learner has said so in those words.

## Verify, always

- **Reload the page and read the state back** after submitting. A quiet page is not a success signal;
  the only proof is the portal showing the submission in the state you expect.
- Record in `learner/progress.md`: what was submitted, when, and the verification result.

## What travels

- Only the reviewed document. Notes never attach, never merge into the docx, never ride along.
- The file must be the final reviewed version - re-check the filename and content after any last
  edit, because an older draft with the same name is the classic silent failure.
- Delete superseded drafts with the same name from `learner/submissions/` before staging. Two files
  that differ by one word are how the wrong one gets uploaded.

## The evidence set (learned 30 Oct 2026)

When a trainer asks for "the certificate of completion", it exists - the "Download your certificate"
link sits on the completed learning-path page (`app.qa.com/learning-paths/...`). Never claim a
certificate does not exist until that page has been checked and read for `cert` links. The full set:

1. Certificate PDF from the learning-path page.
2. Screenshot of the exam results page (score visible).
3. Screenshot of the completed learning path.
4. The reviewed document itself.

## Hours and comment travel in the same pass

- The Bud make-a-submission form has an inline "Off the job hours" number field. Log the hours there
  with the submission; it beats a separate visit to the OTJ tab.
- The comment answers the trainer's request directly, in the learner's voice, humanized per the
  no-ai-slop rules (no em dashes, active voice, no colon reveals).
- Anatomy that worked: comment box is `textarea.submit-comments`; the file input is
  `input[type="file"]` (hidden, off-viewport - `setInputFiles`, not click); the own-work checkbox and
  the Submit button belong to the learner, always.
