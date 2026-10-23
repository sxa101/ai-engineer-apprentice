"""Slice the lesson audio into one file per page (unit).

The master readalong.wav is a single continuous recording. Working a page at a
time means each page needs its own audio and its own manifest, with segment
times measured from the start of that page rather than from the start of the
lesson. Nothing is re-synthesised: the slices are taken straight out of the
master with a stream copy, so the voice and the loudness are unchanged.

    python split-pages.py ra-llms
"""
import json
import os
import subprocess
import sys


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else "ra-llms"
    run_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), run)
    master = os.path.join(run_dir, "readalong.wav")
    manifest = json.load(open(os.path.join(run_dir, "manifest.json"), encoding="utf-8-sig"))
    out_dir = os.path.join(run_dir, "pages")
    os.makedirs(out_dir, exist_ok=True)

    units = manifest["units"]
    total = float(manifest["total"])

    for i, u in enumerate(units):
        start = float(u["start"])
        end = float(units[i + 1]["start"]) if i + 1 < len(units) else total
        dur = round(end - start, 3)

        wav = os.path.join(out_dir, "unit-%d.wav" % u["unit"])
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", "%.3f" % start, "-t", "%.3f" % dur,
            "-i", master, "-c", "copy", wav,
        ]
        subprocess.run(cmd, check=True)

        segs = [
            {"target": s["target"], "start": round(float(s["start"]) - start, 3), "dur": round(float(s["dur"]), 3)}
            for s in u["segs"]
        ]
        page = {
            "total": dur,
            "units": [{"unit": u["unit"], "slug": u["slug"], "start": 0.0, "segs": segs}],
        }
        with open(os.path.join(out_dir, "unit-%d.json" % u["unit"]), "w", encoding="utf-8") as fh:
            json.dump(page, fh, indent=1)

        size = os.path.getsize(wav) / 1048576.0
        print("unit %d  %7.3fs  %5.1f MB  %s" % (u["unit"], dur, size, u["slug"]))


if __name__ == "__main__":
    main()
