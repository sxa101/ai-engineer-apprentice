# AI Engineer Apprentice System

An operating prompt that turns an AI coding agent into a study coach for the **QA / NVIDIA AI Engineer
Apprenticeship (Level 6)**, and lets someone work through the course at a real pace instead of clicking
through it.

It is one Markdown file. Paste it into a session and the agent knows how to run a study block: what to
deliver, in what order, how to check the work actually landed, and how to mark a unit complete without
fooling itself.

---

## The problem it solves

Course platforms measure completion. Completion is easy to fake. You can open a lesson, harvest the
text in ninety seconds, press the tick, and the progress bar moves while nothing goes into your head.

This prompt is built around the opposite idea: **a ticked unit is not evidence of learning**. It is
evidence that a button was clicked.

So every unit goes through the same loop, and the tick comes last:

1. **Listen.** The material is delivered as speech, at real pace, with the page highlighting the block
   being spoken. Or the video plays to the end, unmuted.
2. **Retrieve.** Plain questions, answered from memory. Not multiple choice, not a recap.
3. **Explain.** Got it, carry on. Did not get it, explain another way and ask again.
4. **Write it down.** Notes in the learner's own voice, straight after they answer, including the wrong
   answers and the corrections.
5. **Only then mark it complete.**

The retrieval step is not a formality. In the run that produced this prompt, six units were ticked in a
first sweep and came back half understood on a second pass. Retrieval is what caught it.

---

## What is in the box

| File | What it is |
|---|---|
| [`AI-Engineer-Apprentice-System.md`](AI-Engineer-Apprentice-System.md) | The prompt itself. Self contained - paste it in and go |
| [`SETUP.md`](SETUP.md) | How to set it up and use it, step by step |

The prompt covers:

- **A learner profile** you fill in once, so answers reflect a real workplace rather than a textbook.
- **A writing register** for anything submitted - plain, short, slightly imperfect, with a banned word
  list. Because submissions get reviewed by a human, not polished by a machine.
- **The learning loop** in full, including why the order matters.
- **Read aloud with browser highlight** - on by default. The page words are spoken one segment per page
  block, so the highlight is exact. Built for people who cannot read comfortably.
- **The course structure** - activities in a Discover / Practise / Apply shape, and how each unit type
  is delivered.
- **Hard won technical notes** - how to mark a unit complete (it is an `<a>`, not a `<button>`, and it
  is two steps), how to verify a lesson through the API rather than the page, how to extract content
  reliably, and the Playwright and PowerShell traps that cost real time.
- **Lab protocol** - labs are learner led, time limited and irreversible once submitted. Never run ahead,
  never submit without an explicit go-ahead.
- **Full source** for every script it refers to, so a fresh setup does not have to reverse engineer
  anything.

---

## Requirements

- An AI agent that can drive a browser. The prompt assumes Playwright-style `browser_*` tools.
- A Windows machine for the audio pipeline (SAPI plus ffmpeg). The rest works anywhere.
- Access to the course: a Bud learning portal account, which gives single sign on to the QA platform.
- ffmpeg on `PATH` if you want the spoken read out.

Nothing in the prompt contains a learner's data. It is a template - you fill in section 1 yourself.

---

## Quick start

1. Copy `AI-Engineer-Apprentice-System.md` somewhere you will keep it, for example `~/bud/`.
2. Open a session with your agent and paste the whole file in as the first message.
3. Work through section 2 of the prompt with the agent. It will ask you for your folder, your profile,
   whether you want read aloud, and your schedule. Answer honestly - the answers change the delivery.
4. Start the first block.

Full instructions, including the audio setup and the portal chain, are in [`SETUP.md`](SETUP.md).

---

## The course

- **Standard:** [ST1398 AI Engineer, Level 6](https://skillsengland.education.gov.uk/apprenticeships/st1398-v1-0?view=standard)
  - the apprenticeship standard this maps to, published by Skills England.
- **Provider:** [QA / NVIDIA AI Engineer Level 6](https://www.qa.com/apprenticeships/ai/nvidia-ai-engineer-level-6/)
  - the course itself.
- **Portal login:** [Bud](https://auth.bud.co.uk/Account/Login) - the learning portal. Content opens from
  here by single sign on into the QA platform.

The course runs as a sequence of activities, each in three stages: **Discover**, **Practise**, **Apply**.
The prompt does not assume you are on any particular activity - it reads the plan and finds where you
actually are.

---

## Notes on the approach

**The audio is not an accessibility extra.** For some learners it is the only channel that works. The
read aloud pipeline exists because a reading unit with no speech is a wall.

**Everything automated is administration.** Navigation, marking, verification, extraction. Never the
learning itself. If the agent is doing the thinking, the block has failed.

**Written work is reviewed by a human before it goes anywhere.** That applies to lab submissions too.
They are irreversible and they carry the learner's name.

**The prompt is meant to be edited.** It has an enhancement log at the bottom. Every time a block
teaches something that would have cost time to rediscover, add it there and date it. A stale copy of the
prompt is worse than no copy.

---

## Status

Working, and proven across a full activity. The technical notes in section 10 and 11 are not guesses -
each one is a trap that was hit, diagnosed and written down.

It is also tied to one platform. The selectors, the API shape and the marking flow are QA's. If your
provider differs, sections 10.1 to 10.3 are the parts you will need to redo.

---

## Licence

No licence file yet. Treat it as all rights reserved until one is added.
