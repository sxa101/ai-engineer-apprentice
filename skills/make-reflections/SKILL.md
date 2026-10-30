# Skill: make-reflections

Write reflections and short personal answers in the learner's voice, for their review. A reflection is
not an essay and not a progress report for the assessor. It is the learner thinking out loud on paper.

## The form

Write it the way a C programmer writes C: clear, flat, very short. One idea per sentence. State the
thing, state why, stop.

- No warm-up sentence. No restating what was just read. No decorative linking words.
- No "I have learned that...", no "this has given me a greater understanding of...". Say the thing.
- **Hard cap: three bullets.** Two is better.
- Length: 200-300 words is a ceiling for a big stage, not a target. Shorter is nearly always better.
  If it can be cut, cut it.

## What actually makes text read as machine generated

It is almost never length. It is:

- **Parallel structure everywhere** - bullets the same length, same shape, same beat. The biggest tell
  and the hardest to see in your own draft.
- **Triads.** Everything arriving in threes.
- Every sentence doing a full tidy job. No fragments, no run-ons, no half-finished thought.
- No friction - no contractions, no clumsy clause, no admitted uncertainty.

Fix it by varying the shape, not by adding adjectives.

## Reach for a parallel, not an adjective

The strongest reflections map a new idea onto something the learner already understands properly,
state the mapping plainly, then draw the consequence. Worked example, accepted verbatim by a learner:

> Key learnings: generative AI is attention in parallel. Attention lets any word reach any other word
> in one step, so distance stops mattering.

One sentence carries the whole module because it is built on something already known rather than
described from outside.

## The gate

- The draft is **always human reviewed before it goes anywhere.** Write it, present it, stop.
- Grounded in what the learner actually said in retrieval and what is in their notes - including the
  wrong answers and the corrections. Those are the authentic details.
- If the draft needs the notes to make sense, the draft needs rewriting. Notes never travel with it.

## The build pipeline (learned 30 Oct 2026)

- One markdown source per reflection in `learner/submissions/`, named after the full activity in
  kebab case (`activity-1-3-discover-building-and-automating-with-generative-ai-reflection.md`).
  All wording changes go in the md, never the docx.
- Build with `build-submission-docx.py` in the same folder, then verify the page count with Word COM
  (`ComputeStatistics(2)`). One A4 page is roughly 480 words at the current styling. A reflection
  that runs past one page gets cut, not shrunk.
- The docx is named `Activity-<n>.<stage>-<Full Activity Name>-Reflection.docx`. There will be many
  Discover, Practise and Apply reflections; the full activity name is what keeps them apart.
- If the docx is open in Word, the build fails with a file lock. Ask for it to be closed rather than
  fighting the lock.
- The no-ai-slop skill (`~/.agents/skills/no-ai-slop/SKILL.md`) governs the final pass. If the
  runtime skill registry does not see it, read it from disk and apply it by hand.
