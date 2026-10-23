"""Build a read-along WAV with Edge neural voices.

Replaces the System.Speech path in build-readalong.ps1. SAPI voices sound robotic
and sit at about 0.9x speed, which makes a 40 minute lesson drag. Edge neural
voices are far clearer and take a rate multiplier, so the same script can be
delivered briskly.

Synthesises each segment, pads it, concatenates, applies two-pass loudnorm and
writes manifest.json. Segment order and target indices are preserved exactly, so
the read-along engine keeps working unchanged.

    python build-readalong-edge.py --json units-llms-readalong.json --out ra-llms
    python build-readalong-edge.py ... --rate +40% --voice en-GB-ThomasNeural
"""
import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import edge_tts

VOICE = "en-GB-RyanNeural"
RATE = "+0%"
PITCH = "+0Hz"
PAD = 0.55
WORKERS = 6
RETRIES = 4


def clean(t: str) -> str:
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    t = t.replace("\u2014", ", ").replace("\u2013", ", ")
    t = t.replace("(", ", ").replace(")", ", ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r",\s*,", ",", t)
    t = re.sub(r"\s+([.,])", r"\1", t)
    return t.strip()


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def duration(path: str) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path])
    return float(r.stdout.strip())


async def synth_one(sem, idx, text, voice, rate, pitch, mp3, wav, pad):
    async with sem:
        for attempt in range(1, RETRIES + 1):
            try:
                c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                await c.save(mp3)
                if os.path.getsize(mp3) < 200:
                    raise RuntimeError("tiny output")
                break
            except Exception as e:
                if attempt == RETRIES:
                    raise RuntimeError(f"seg {idx} failed after {RETRIES}: {e}")
                await asyncio.sleep(1.2 * attempt)

    def to_wav():
        r = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-i", mp3, "-af", f"apad=pad_dur={pad}",
                 "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", wav])
        if r.returncode != 0:
            raise RuntimeError(f"seg {idx} ffmpeg: {r.stderr[:300]}")
        return duration(wav)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, to_wav)


async def build(args):
    data = json.load(open(args.json, encoding="utf-8-sig"))
    seg_dir = os.path.join(args.out, "seg")
    os.makedirs(seg_dir, exist_ok=True)
    for f in os.listdir(seg_dir):
        os.remove(os.path.join(seg_dir, f))

    flat = []
    for u in data["units"]:
        for s in u["segments"]:
            flat.append((u["unit"], u["slug"], s["target"], clean(s["text"])))

    print(f"segments {len(flat)}   voice {args.voice}   rate {args.rate}", flush=True)

    sem = asyncio.Semaphore(args.workers)
    jobs = []
    for i, (_, _, _, text) in enumerate(flat, start=1):
        mp3 = os.path.join(seg_dir, f"seg_{i:03d}.mp3")
        wav = os.path.join(seg_dir, f"pad_{i:03d}.wav")
        jobs.append(synth_one(sem, i, text, args.voice, args.rate, args.pitch,
                              mp3, wav, args.pad))

    have = all(os.path.exists(os.path.join(seg_dir, f"pad_{i:03d}.wav"))
               for i in range(1, len(flat) + 1))
    if args.reuse and have:
        print("reusing existing segments", flush=True)
        durs = [duration(os.path.join(seg_dir, f"pad_{i:03d}.wav"))
                for i in range(1, len(flat) + 1)]
    else:
        durs = await asyncio.gather(*jobs)
    print(f"synthesised {len(durs)} segments   audio {sum(durs):.1f}s", flush=True)

    concat = os.path.join(args.out, "concat.txt")
    with open(concat, "w", encoding="ascii") as fh:
        for i in range(1, len(flat) + 1):
            p = os.path.abspath(os.path.join(seg_dir, f"pad_{i:03d}.wav"))
            fh.write(f"file '{p.replace(os.sep, '/')}'\n")

    joined = os.path.join(args.out, "joined.wav")
    r = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", joined])
    if r.returncode != 0:
        raise SystemExit(f"concat failed: {r.stderr[:400]}")

    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", joined,
             "-af", "loudnorm=I=-12:TP=-1.0:LRA=11:print_format=json",
             "-f", "null", "NUL"])
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr, re.S)
    if not m:
        raise SystemExit("loudnorm analysis failed")
    d = json.loads(m.group(0))

    filt = (f"loudnorm=I=-12:TP=-1.0:LRA=11:measured_I={d['input_i']}"
            f":measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
            f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}"
            f":linear=true")
    final = os.path.join(args.out, "readalong.wav")
    r = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", joined,
             "-af", filt, "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", final])
    if r.returncode != 0:
        raise SystemExit(f"loudnorm render failed: {r.stderr[:400]}")

    manifest, cursor, k = [], 0.0, 0
    for u in data["units"]:
        segs = []
        for s in u["segments"]:
            dd = round(durs[k], 3)
            segs.append({"target": s["target"], "start": round(cursor, 3), "dur": dd})
            cursor += dd
            k += 1
        manifest.append({"unit": u["unit"], "slug": u["slug"],
                         "start": segs[0]["start"], "segs": segs})

    out = {"file": final, "total": round(duration(final), 3), "units": manifest}
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)

    print(f"\nDONE  segments={len(flat)}  total={out['total']:.1f}s")
    for u in manifest:
        end = max(s["start"] + s["dur"] for s in u["segs"])
        print(f"  unit {u['unit']}  {u['start']:.3f} -> {end:.3f}  ({end - u['start']:.0f}s)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", default="units-llms-readalong.json")
    p.add_argument("--out", default="ra-llms")
    p.add_argument("--voice", default=VOICE)
    p.add_argument("--rate", default=RATE)
    p.add_argument("--pitch", default=PITCH)
    p.add_argument("--pad", type=float, default=PAD)
    p.add_argument("--workers", type=int, default=WORKERS)
    p.add_argument("--reuse", action="store_true",
                   help="reuse existing pad_*.wav instead of re-synthesising")
    args = p.parse_args()
    asyncio.run(build(args))


if __name__ == "__main__":
    main()
