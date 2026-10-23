# Skill: read-along

Deliver reading units as speech, at real pace, with the browser tab highlighting the exact block being
spoken. Built for people who cannot read comfortably - it is the primary channel, not an accessibility
extra.

The full build procedure and script sources are in the reference prompt
([`../../AI-Engineer-Apprentice-System.md`](../../AI-Engineer-Apprentice-System.md), sections 6 and 11).
This skill is the operating model and the traps.

## The delivery model: one page at a time

The whole-lesson timeline has one failure that keeps recurring: the engine derives position from a
wall clock, so when the audio stops, the page keeps walking. Three separate bugs in one day all had
the same root - a position that was inferred rather than owned. The fix is structural:

1. **One WAV per lesson** built by the TTS pipeline (neural voice, natural rate).
2. **Split into one file per page** with `ffmpeg -ss -t -c copy` - a stream copy that does not
   re-encode, so voice and level are untouched. Segment times are rebased to the page.
3. **One player per page** with its own state file, pause flag and remainder file. The manifest holds
   exactly one unit, so the engine cannot see a later page to walk into.
4. **A `stop` clamp in sessionStorage** freezes `elapsed()` at the page end, and `isPaused()` reports
   true once clamped. Verified live: at page end the position sits at exactly the page total and the
   tab does not move on.

The loop, one page at a time:

```
ra-page.ps1 -Status                 # where each page is up to - run this first, every block
ra-page.ps1 -Unit 6                 # play page 6 from its saved position
python make-page-inject.py 6        # bake the tab for page 6
# copy inject-page-6.js / sync-page-6.js into the Playwright allowed root, run inject via run_code
ra-page-sync.ps1 -Unit 6            # correct the tab to the real voice position
# page ends -> the tab stays on that page -> mark it -> the platform advances itself
```

**Always sync immediately after the inject.** The player writes its position about once a second, so
a baked-in start is already stale by the time the tab finishes loading - measured at roughly four
seconds. The sync helper adds the age of the state file back on. After a sync, page and voice agree to
well under a second. **The Playwright MCP only reads files from its allowed roots**, so the baked
`inject-page-N.js` / `sync-page-N.js` must be copied from the run dir into the browser session's root
before `run_code` can load them by filename. The inject snippet does its own navigation - run it, do
not navigate the tab first.

The script sources are tracked in [`scripts/`](../../scripts/README.md), kept in step with the live
copies under `learner/audio/`.

## Video units are not read-along units

A video unit plays itself. The platform auto-plays on arrival, auto-advances at the end, and
auto-marks the unit on watch-through - no manual marking, no audio pipeline. Two things to do:

- **The player defaults to muted, and re-mutes when `play()` is called from code.** Set
  `muted=false; volume=1` just after play starts, then verify. Sound is the whole point.
- The control bar is hover-hidden, so clicking `.vjs-play-control` from Playwright times out. Call
  `document.querySelector('video').play()` directly.

## Keep a transcript of every module (since 23 Oct 2026)

Every unit of a lesson gets a transcript file in `learner/transcripts/`, named `NN-slug` with `NN`
the course step number:

- **Video units:** the platform exposes subtitles as plain VTT on a public CDN - filter the network
  log for `\.(m3u8|vtt|mp4|srt)` and the VTT URL is there (`subtitles.platform.qa.com/dam/subtitles/`
  `{uuid}.vtt`). No auth; curl works. One UUID per video.
- **Text units:** extract the page blocks (same recipe as the scrape) into a `.txt`.
- **Summary pages** the learner would rather not hear read out (references, links): write a
  key-ideas summary at his register instead, as `.md` beside the raw extract, and read *that* over
  the page. Ask before the block which pages get the verbatim read and which get summarised.

## Rules

- **Let it play.** Do not interfere, do not speed it up, do not skip segments.
- **Pace is natural (+0%)** unless the learner asks for a change. It was raised and walked back four
  times before settling; do not raise it again unless asked.
- If the highlight lands on the wrong paragraph, stop and fix it. An off-by-one highlight is worse
  than none, because the learner trusts it and reads the wrong block.
- Verify at the start of each page that the first highlight sits on the paragraph being spoken.
- When a page finishes, move straight into retrieval. Do not mark anything yet.

## Marking a page complete

The control is an **`<a role="button">`**, not a `<button>` - counting buttons returns 0 whether the
unit is done or not.

```
a[role="button"][aria-label="Mark this content as completed"]
```

Two steps, but treat the modal as optional: clicking the `<a>` may only open a confirmation dialog
(confirm inside `[role="dialog"][aria-label="Mark as completed the following content?"]`), or it may
save and auto-advance immediately if "don't show again" was ticked in a past session. Click, look for
the dialog, confirm it if present, carry on if not.

- **Guard every mark with the expected slug**, read off the URL: `/\/course\/[^/]+\/([^/?]+)/`. If it
  is not the page you think it is, refuse and stop.
- **Clicking the mark navigates the platform.** The evaluate that clicked it will often throw
  "execution context destroyed". Re-evaluate afterwards rather than trusting the return value.
- **Mark the moment the audio finishes, in course order.** Never batch to the end of a module - a
  batch claims every unit finished at the same minute, and temporal order is part of the evidence.
- **No control means already marked.** The control disappearing is the reliable done signal.
- **The platform has no un-mark.** A wrong tick can only be made true by playing the unit properly.

## Verifying a lesson - never trust the page

- The completion API (`/api/v3/userinteractions/course/{uuid}/`) is course level only; listen for it
  on page load (a direct fetch 401s - QA authenticates with a header).
- The real per-unit check is the sidebar: `[aria-label*="step is completed"]`, read after a reload.
- A stopped voice must stop the page. If the tab is rolling with no sound or highlights, suspect the
  wall clock and re-sync.

## Traps

- `ConvertFrom-Json` turns the ISO `updatedAt` stamp into a `[datetime]` - accept both that and the
  string form (parse with invariant culture) or the sync helper throws.
- `[Math]::Floor()` returns a double; cast to `[int]` before format strings.
- The References-style pages can have as few as three content blocks - do not wait for more.
- Injected engine content is frozen at registration. Change the engine, open a fresh tab.
- The platform auto-marks some units without being asked - activities on visit, reference pages,
  videos on watch-through. Check the sidebar before assuming a mark is needed, and never un-tick one
  you did not place; record it and move on.
