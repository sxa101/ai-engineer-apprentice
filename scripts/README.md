# Read-along toolchain

The working scripts for the read-along pipeline: render a lesson to speech, slice it one page per
file, play it, and keep the browser tab highlighting the exact block being spoken. The operating
model and the traps live in [`skills/read-along/SKILL.md`](../skills/read-along/SKILL.md); the why
is in the system document, sections 6 and 11.

These copies are kept in step with the live ones under `learner/audio/`. If a block changes a script,
copy it back here the same day.

## The pipeline, in order

```
units-<lesson>-readalong.json        # hand-built scrape archive: units, segments, targets, commentary
python build-readalong-edge.py --json units-x-readalong.json --out ra-x
python split-pages.py ra-x           # one wav + one manifest per page, stream copy, no re-encode

# per page, in this order:
ra-page.ps1 -Status                  # where every page is up to - run this first, every block
ra-page.ps1 -Unit 5                  # play page 5 (blocks until the page audio ends)
python make-page-inject.py 5 ra-x <course-slug>   # bake inject-page-5.js + sync-page-5.js
# copy both into the Playwright allowed root, then run inject-page-5.js via run_code
ra-page-sync.ps1 -Unit 5             # re-bake sync-page-5.js from the live position, run it
# page ends -> mark it -> next page
```

## Files

| Script | Purpose |
|---|---|
| `build-readalong-edge.py` | Render the units JSON to one WAV (Edge neural voice, per-segment synthesis, two-pass loudnorm) plus `manifest.json` with exact segment timings |
| `split-pages.py` | Slice the master WAV one file per page with `ffmpeg -ss -t -c copy`; rebase segment times to each page |
| `ra-page.ps1` | Play one page from its saved position; own state file, pause flag, `-Status` view |
| `make-page-inject.py` | Bake engine + that page's manifest + resume position into a single Playwright snippet per page |
| `ra-page-sync.ps1` | Work out where the voice really is and emit the `__raSet` snippet that moves the highlight onto it |
| `readalong-engine.js` | The injected engine: highlight, chip, stop clamp, `__raSet`/`__raNow` |

## The traps that cost time

- **Always sync immediately after the inject.** The baked start is stale by load time (about four
  seconds), and after any pause in the setup the gap is bigger. `ra-page-sync.ps1` adds the age of the
  state file back on.
- **The Playwright MCP only reads files from its allowed roots.** The baked `inject-page-N.js` /
  `sync-page-N.js` land next to the run dir; copy them into the worktree (or cwd the browser session
  runs from) before running them with `run_code`'s `filename`.
- **The inject snippet navigates by itself** - it does the `goto` and waits for the content container.
  Do not navigate the tab first; run the inject and let it land.
- **One manifest per page.** The engine cannot walk into a later unit because it cannot see one. The
  `stop` clamp freezes the clock at the page end.
- Voice `en-GB-RyanNeural`, rate `+0%`, pad `0.55s`, loudnorm `I=-12`. The pace was raised and walked
  back four times; do not change it unless the learner asks.
