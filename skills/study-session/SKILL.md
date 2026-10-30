# Skill: study-session

The frame for one study block. Opens it, keeps it honest, closes it.

## Getting in (learned 30 Oct 2026)

- Login always starts at the learner's Bud portal, **`web.bud.co.uk`**. The Bud session carries the
  SSO into the QA platform - from the Bud activity page, follow the SSO link into `app.qa.com`.
- **Never open app.qa.com cold.** Its login page is a dead end: it does not lead anywhere useful.
- A wrong or guessed QA URL bounces to `/login/` even with a live session. Recover by navigating to
  a known-good course or learning-path URL (the session survives), never by logging in again.
- Discover real URLs from inside a loaded page - its own links, or the LP API - not from guesses.

## Open (first ten minutes)

1. Three cold questions on the previous block, answered from memory. Correct gently, give the term,
   move on. This is retrieval, not a quiz show - wrong answers are the point and get recorded.
2. Read `learner/progress.md` (last entry) and `learner/study-plan.md` (where this block sits).
3. Read the portal plan page again. The shape of what is left matters more than the percentage.
4. Say what this block will cover and confirm it fits. **Never start a unit that cannot be finished
   in the block.** A two hour lesson is a two block lesson once retrieval and note writing are added -
   QA durations exclude them, and they add roughly a third.

## Run

- Deliver through the other skills, one unit at a time: listen, retrieve, explain, write notes, mark.
- Sound always on at full volume. If they cannot hear it, nothing else matters.
- Real pace, set by the learner. The voice is the learner's judgement call, not the clock's.
- If a pause is asked for, stop cleanly at the current point, record where, and resume from there.

## Close (last ten minutes)

1. Ask them to explain the block back in their own words.
2. Write the `learner/progress.md` entry: what was done, roughly how long, what was learned the hard
   way, and exactly where the next block starts. This is the audit trail - write it while it is fresh.
3. Update `study-plan.md` if the plan slipped.
4. Report briefly: what completed, where the resume point is, what the next block is, any decision
   needed from the learner.

## Rules that have been learned the hard way

- A missed block slides to the next slot. It is never crammed in. Extra blocks happen only when the
  learner asks.
- One block per working day, on the learner's chosen days, in work hours.
- Never batch the closing chores to "later". The progress entry written the same day is worth ten
  written from memory.
- Deadlines in the plan are far apart and the nearest one is often not the next stage. Read the plan
  before promising a date.
- **Progress pointers use names, never numbers:** `activity name | lesson name`. Row numbers and
  portal ids (LP 16057, unit ids) are technical plumbing for URLs only. Numbered pointers are how a
  session loses its place. (Learned 30 Oct 2026.)
- If the stage ends in a Knowledge Check, offer the `knowledge-check` supports at open and close
  (warm-up, harvest, readiness call). The offer is the coach's job; the sitting is the learner's.
