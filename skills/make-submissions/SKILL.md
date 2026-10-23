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
