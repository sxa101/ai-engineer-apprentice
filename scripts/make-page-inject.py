"""Generate a Playwright injection script for a single page of the lesson.

Bakes the engine, that page's one-unit manifest and the page's own resume
position into one file. Because the manifest holds only this page, the engine
cannot wander into another unit: the highlight simply runs to the end of the
page and stops.

    python make-page-inject.py 5 ra-llms llms-and-natural-language-ai
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CTX = "?context_id=16057&context_resource=lp"


def main():
    unit = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run = sys.argv[2] if len(sys.argv) > 2 else "ra-llms"
    course = sys.argv[3] if len(sys.argv) > 3 else "llms-and-natural-language-ai"

    pages = os.path.join(HERE, run, "pages")
    page_man = json.load(open(os.path.join(pages, "unit-%d.json" % unit), encoding="utf-8-sig"))
    engine = open(os.path.join(HERE, "readalong-engine.js"), encoding="utf-8").read()

    state_p = os.path.join(pages, "unit-%d.state.json" % unit)
    elapsed = 0.0
    playing = False
    if os.path.exists(state_p):
        st = json.load(open(state_p, encoding="utf-8-sig"))
        elapsed = float(st.get("elapsed", 0))
        playing = bool(st.get("playing"))
    elapsed = min(elapsed, float(page_man["total"]))

    base = "https://app.qa.com/course/%s/" % course
    page_man["base"] = base
    page_man["ctx"] = CTX

    pfx = "ra" + "".join(w.capitalize() for w in run.replace("ra-", "").split("-"))
    slug = page_man["units"][0]["slug"]

    body = """async (page) => {
  const ENGINE = %s;
  const MANIFEST = %s;
  const ELAPSED = %s;
  const BASE = %s;
  const CTX = %s;
  const PFX = %s;
  const PLAYING = %s;

  await page.addInitScript(ENGINE);
  await page.goto(BASE + %s + '/' + CTX, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => {
    const c = document.querySelector('div[class*="sc-147c5efa-0"]');
    return c && c.children.length >= 3;
  }, { timeout: 45000 });

  await page.evaluate(([m, el, pfx, live]) => {
    sessionStorage.setItem('raPrefix', pfx);
    sessionStorage.setItem(pfx + 'manifest', JSON.stringify(m));
    sessionStorage.setItem(pfx + 'start', String(Date.now() - el * 1000));
    sessionStorage.setItem(pfx + 'stop', String(m.total));
    if (live) sessionStorage.removeItem(pfx + 'paused');
    else sessionStorage.setItem(pfx + 'paused', String(el));
  }, [MANIFEST, ELAPSED, PFX, PLAYING]);

  await page.evaluate(ENGINE);
  await page.waitForTimeout(1200);

  return JSON.stringify(await page.evaluate(() => {
    const hl = document.querySelector('.ra-hl');
    return {
      chip: (document.getElementById('ra-chip') || {}).textContent,
      note: (document.getElementById('ra-note') || {}).textContent || null,
      hl: hl ? hl.innerText.replace(/\\s+/g, ' ').trim().slice(0, 90) : null,
      err: window.__raErr
    };
  }));
}""" % (
        json.dumps(engine),
        json.dumps(page_man),
        repr(elapsed),
        json.dumps(base),
        json.dumps(CTX),
        json.dumps(pfx),
        "true" if playing else "false",
        json.dumps(slug),
    )

    out = os.path.join(HERE, "inject-page-%d.js" % unit)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(body)

    sync = """async (page) => {
  const SEC = %s;
  const PAUSED = %s;
  return JSON.stringify(await page.evaluate(([sec, paused]) => {
    if (!window.__raSet) return { error: 'engine not loaded' };
    window.__raSet(sec, paused);
    return { synced: sec, paused: paused };
  }, [SEC, PAUSED]));
}""" % (repr(elapsed), "true" if not playing else "false")

    sync_out = os.path.join(HERE, "sync-page-%d.js" % unit)
    with open(sync_out, "w", encoding="utf-8") as fh:
        fh.write(sync)

    print("wrote %s" % out)
    print("wrote %s" % sync_out)
    print("  prefix   %s" % pfx)
    print("  page     %d  %s" % (unit, slug))
    print("  length   %.2fs" % float(page_man["total"]))
    print("  position %.2fs  (%s)" % (elapsed, "live" if playing else "paused"))


if __name__ == "__main__":
    main()
