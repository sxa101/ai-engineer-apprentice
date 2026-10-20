# Setup and use

How to get the AI Engineer Apprentice System running, and what a study block actually looks like.

Setup takes about fifteen minutes. The first block takes longer than usual because there is no previous
block to open with.

---

## Before you start

| You need | Why |
|---|---|
| An AI agent with browser tools | The prompt assumes Playwright-style `browser_*` tools to drive the course pages |
| A Bud account | Bud is the learning portal. It single-signs-on into the QA platform where the content lives |
| ffmpeg on `PATH` | Only for the spoken read out. Check with `ffmpeg -version` |
| Windows | Only for the audio pipeline, which uses the Windows speech engine. Everything else is portable |
| About 75 minutes | For the first block. Do not start one you cannot finish |

Check ffmpeg:

```powershell
ffmpeg -version
```

Check the speech engine has voices installed:

```powershell
Add-Type -AssemblyName System.Speech
(New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() |
  ForEach-Object { $_.VoiceInfo.Name }
```

If that returns nothing, the read aloud will not work. You can still use the prompt - say no to read
aloud in step 3 and reading units get delivered as text with retrieval.

---

## Step 1 - put the prompt somewhere permanent

Copy `AI-Engineer-Apprentice-System.md` into a folder you will keep. The prompt calls this `<ROOT>`.

**Default is `~/bud`** - on Windows, `C:\Users\<yourname>\bud`.

If you want somewhere else, that is fine. Pick it now, because every path in the prompt derives from it.
If the folder does not exist, the agent should ask you where to put it rather than creating one you did
not choose.

Expected layout once set up:

```
<ROOT>/
├── AI-Engineer-Apprentice-System.md
└── ai-apprenticeship/
    ├── study-plan.md          # schedule, rules, unit URLs
    ├── progress.md            # per block log, append only
    ├── notes/                 # one file per lesson
    ├── audio/                 # read aloud scripts and renders
    └── labs/                  # lab notebooks and saved cells
```

The agent creates this on first run.

---

## Step 2 - start a session and paste the prompt

Open a session with your agent. Paste the **whole** `AI-Engineer-Apprentice-System.md` file in as the
first message.

Do not summarise it. The file is written to be self contained - every rule, every script, every trap is
in there. Trimming it removes the parts that stop the agent taking shortcuts.

The agent should confirm it has read it and then move into setup.

---

## Step 3 - work through first-run setup

The prompt's section 2 lists six things. The agent should ask, not assume.

**Folder.** Where your study folder lives. Defaults to `~/bud`.

**Profile.** Section 1 of the prompt. Two fields matter most and are worth thinking about before you
answer:

- *Can you read comfortably?* If not, audio is the only channel that works and every reading unit gets
  spoken and highlighted. Say so plainly - it changes the whole delivery.
- *What does your organisation actually do?* Several activities ask you to apply ideas to your own
  workplace. A textbook answer will be marked wrong by reality. Be honest about your stack, your release
  process, how much is automated, and where the real gaps are. The prompt explicitly tells the agent not
  to let you claim maturity you do not have.

**Read aloud.** Default is **yes**. It speaks the page words one segment per page block and highlights
the matching block, so you can follow along without reading.

Ask for a short test render before committing to a full unit. If you cannot hear it, the problem is
usually the OS mixer rather than the audio file - `set-volume.ps1` (given in full in section 11.5 of the
prompt) forces the default output to 100% and unmutes it.

**Schedule.** Which days, and how long. Default is one 75 minute block per working day in work hours.

Pick something you will actually keep. The prompt holds to whatever you choose and slides a missed block
to the next slot rather than cramming it in. A plan that moves every time something slips is not a plan.

**Portals.** Confirm you are logged in to Bud. Content opens from Bud by single sign on into the QA
platform, so if Bud is not authenticated nothing downstream works. If you get logged out mid-session,
log back in - do not ask the agent to work around the login.

**Baseline.** Where you actually are in the course. The agent should read the Bud plan and the QA course
sidebar rather than assuming you are on activity 1.3.

---

## Step 4 - run a block

A block is about 75 minutes of real content. Here is what happens.

### Opening

Three cold questions on the previous block, before any new material. If you cannot answer them, that is
the useful signal - it means the last block did not stick, and the prompt says to go back rather than
push on.

### The unit

Each unit is one page, and it is one of five types. The delivery differs:

**Video.** Plays to the end. The player tracks position, so skipping shows up. Sound is at full volume
and never muted - the player mutes itself on load because of the browser autoplay policy, so the agent
clicks once on the player then sets `muted = false; volume = 1.0`. The page auto-advances when it ends.

**Reading.** The read aloud plays first, with the matching block highlighted. Let it run. Then retrieval,
then notes, then the mark. In that order. If the highlight lands on the wrong paragraph, stop and fix it -
a wrong highlight is worse than none, because you trust it and read the wrong block.

**Activity (open response).** There is no text box on the platform. It just says record your answers in a
format of your choice. The deliverable is your notes file, and the answers in it are yours.

**Lab.** Interactive, time limited, and led by you. The agent clicks at human pace and tutors - it points
out the objective and the thing worth learning, then waits. It never runs ahead and never submits without
an explicit go-ahead. A submission is irreversible.

**Exam or knowledge check.** Never sat without being asked first.

### Closing

You explain the block back in your own words. Then the agent writes the notes and updates the plan and
the log.

---

## Step 5 - keep it alive

The prompt has an enhancement log at the bottom, newest at the top.

Every time a block teaches something that would have cost time to rediscover - a selector that moved, an
API that behaves oddly, a step that needs two clicks not one - add a line and date it.

That log is the reason the file is worth reading. It is also the reason a stale copy is worse than no
copy: it will confidently tell you something that is no longer true.

---

## What good looks like

**The tick comes last, and it is not the point.** If you cannot explain a unit a week later, the block
failed even when the platform says 100%.

**Wrong answers are the point.** Retrieval is where the gaps show up. The prompt tells the agent to write
your wrong answer into the notes next to the correction, because the pair is worth more a week later than
a clean summary.

**Notes are yours.** They record what you could actually explain, not what the page said. They get handed
back as they stand, not tidied into prose.

**The agent does administration, not thinking.** Navigation, marking, verification, extraction. If it is
doing the learning for you, stop it.

---

## Troubleshooting

**I cannot hear the audio.**
Run `set-volume.ps1` from section 11.5 of the prompt. Check the WAV is loud enough:

```powershell
ffmpeg -i <path>\readalong.wav -af volumedetect -f null NUL
```

You want a mean around -16 dB. If it reads about -25 dB, the loudnorm pass did not run.

**The highlight is one block behind the speech.**
The `target` values in the manifest were built against a filtered block list. They must be **raw child
indices** of the article container, with `null` kept for blank blocks. See section 11.3 of the prompt -
this is the single most likely bug in a fresh build.

**Nothing renders at all, no chip.**
The manifest is probably a bare array instead of `{base, ctx, units}`. The engine bails silently on
`!M.units`. See section 11.3.

**I edited the engine but the page still runs the old one.**
`addInitScript` content is frozen when it is registered. Open a fresh tab and register again.

**Marking did nothing.**
The control is an `<a role="button">`, not a `<button>`, and it is two steps - click it, then confirm
inside the modal. Auto-advancing to the next unit is the only real success signal. See section 10.1.

**The progress API returns 401.**
It authenticates with a header, not a cookie. Read it by listening for the response on page load instead
of calling it directly.

**A lab page will not connect.**
The panel reads "Ready" about thirty seconds before the endpoint accepts connections. Try the URL,
retry after 30 seconds. Do not trust the label.

---

## Where to read more

- The prompt itself, sections 4 and 5 - the objective and the loop.
- The prompt, section 8 - how the course is laid out.
- The prompt, sections 10 and 11 - every technical trap and every script.
- The [ST1398 standard](https://skillsengland.education.gov.uk/apprenticeships/st1398-v1-0?view=standard)
  for what the apprenticeship actually requires.
