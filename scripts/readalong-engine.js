(function () {
  var PFX = sessionStorage.getItem('raPrefix') || 'ra07';
  var START = parseInt(sessionStorage.getItem(PFX + 'start') || '0', 10);
  if (!START) return;
  var M = null;
  try { M = JSON.parse(sessionStorage.getItem(PFX + 'manifest') || 'null'); } catch (e) { return; }
  if (!M || !M.units) return;

  var lastKey = null, chip = null, note = null, styled = false, navGuard = 0;

  function elapsed() {
    var p = sessionStorage.getItem(PFX + 'paused');
    if (p !== null && p !== '') return parseFloat(p);
    var s = parseInt(sessionStorage.getItem(PFX + 'start') || '0', 10) || START;
    var t = (Date.now() - s) / 1000;
    // A bounded run must not keep rolling after the voice has stopped, or the page
    // walks itself through later units with no sound and nothing highlighted.
    var stop = parseFloat(sessionStorage.getItem(PFX + 'stop'));
    if (!isNaN(stop) && t >= stop) return stop;
    return t;
  }

  function isPaused() {
    var p = sessionStorage.getItem(PFX + 'paused');
    if (p !== null && p !== '') return true;
    var stop = parseFloat(sessionStorage.getItem(PFX + 'stop'));
    return !isNaN(stop) && elapsed() >= stop;
  }

  // One call to move the read-along to a position, paused or running.
  // Used by the player to keep the highlight on the voice after a pause.
  window.__raSet = function (sec, paused) {
    if (paused) {
      sessionStorage.setItem(PFX + 'paused', String(sec));
    } else {
      sessionStorage.removeItem(PFX + 'paused');
      sessionStorage.setItem(PFX + 'start', String(Date.now() - sec * 1000));
    }
    lastKey = null;
    return true;
  };
  window.__raNow = function () { return elapsed(); };

  function unitEnd(u) {
    var e = 0;
    for (var i = 0; i < u.segs.length; i++) { var s = u.segs[i]; if (s.start + s.dur > e) e = s.start + s.dur; }
    return e;
  }

  function currentUnit() {
    var e = elapsed();
    for (var i = 0; i < M.units.length; i++) {
      var u = M.units[i];
      if (e >= u.start && e < unitEnd(u)) return u;
    }
    return null;
  }

  function segAt(u, e) {
    for (var i = 0; i < u.segs.length; i++) {
      var s = u.segs[i];
      if (e >= s.start && e < s.start + s.dur) return s;
    }
    return null;
  }

  function onSlug(u) { return location.pathname.indexOf('/' + u.slug + '/') !== -1; }

  function ensureUI() {
    if (styled) return;
    var root = document.body || document.documentElement;
    if (!root) return;
    var staleChip = document.getElementById('ra-chip');
    if (staleChip) staleChip.remove();
    var staleNote = document.getElementById('ra-note');
    if (staleNote) staleNote.remove();
    styled = true;
    var st = document.createElement('style');
    st.id = 'ra-style';
    st.textContent =
      '.ra-hl{background:#ffe680 !important;box-shadow:0 0 0 4px #ffe680,0 2px 12px rgba(0,0,0,.18) !important;border-radius:4px !important;transition:background .12s,box-shadow .12s;}' +
      '#ra-chip{position:fixed;bottom:16px;right:16px;z-index:2147483647;background:#111;color:#fff;font:600 12px/1.45 system-ui,-apple-system,sans-serif;padding:8px 12px;border-radius:8px;opacity:.9;pointer-events:none;max-width:280px;}' +
      '#ra-note{position:fixed;bottom:16px;left:16px;z-index:2147483647;background:#0a7a4a;color:#fff;font:600 12px/1.45 system-ui,-apple-system,sans-serif;padding:8px 12px;border-radius:8px;opacity:.93;pointer-events:none;}';
    root.appendChild(st);
    chip = document.createElement('div');
    chip.id = 'ra-chip';
    chip.textContent = 'read-along loading';
    root.appendChild(chip);
  }

  function getBlocks() {
    var c = document.querySelector('div[class*="sc-147c5efa-0"]');
    if (!c) return null;
    var out = [];
    for (var i = 0; i < c.children.length; i++) {
      var el = c.children[i];
      var t = (el.innerText || '').replace(/\s+/g, ' ').trim();
      if (!t || /^Mark it or miss it!/.test(t) || /^Mark as completed$/.test(t)) {
        out.push(null);
        continue;
      }
      out.push(el);
    }
    return out.length ? out : null;
  }

  function clearHl() {
    var all = document.querySelectorAll('.ra-hl');
    for (var i = 0; i < all.length; i++) all[i].classList.remove('ra-hl');
  }

  function setNote(text) {
    if (!text) { if (note) { note.remove(); note = null; } return; }
    if (note && !note.isConnected) note = null;
    if (!note) {
      var host = document.body || document.documentElement;
      if (!host) return;
      note = document.createElement('div');
      note.id = 'ra-note';
      host.appendChild(note);
    }
    note.textContent = text;
  }

  function tickInner() {
    ensureUI();
    var e = elapsed();
    var u = currentUnit();

    if (!u) {
      if (chip) chip.textContent = e < M.units[0].start ? 'read-along waiting' : 'read-along finished';
      clearHl();
      return;
    }

    if (!onSlug(u)) {
      if (Date.now() - navGuard > 6000) {
        navGuard = Date.now();
        clearHl();
        location.href = M.base + u.slug + '/' + M.ctx;
      }
      return;
    }

    var blocks = getBlocks();
    var s = segAt(u, e);
    if (!s) return;

    var idx = -1;
    for (var i = 0; i < u.segs.length; i++) if (u.segs[i] === s) idx = i;

    // The clock has to move every tick, not just when the segment changes.
    if (chip) chip.textContent = 'Unit ' + u.unit + '  ' + (idx + 1) + '/' + u.segs.length +
      '   ' + Math.floor(e / 60) + ':' + ('0' + Math.floor(e % 60)).slice(-2) +
      (isPaused() ? '   paused' : '');

    var key = u.unit + ':' + s.target + ':' + (blocks ? blocks.length : 0);
    if (key === lastKey) return;
    lastKey = key;

    if (s.target < 0) {
      clearHl();
      setNote('Commentary');
      return;
    }

    setNote(null);
    if (!blocks || !blocks[s.target]) { clearHl(); return; }
    clearHl();
    var el = blocks[s.target];
    el.classList.add('ra-hl');
    try { el.scrollIntoView({ block: 'center', behavior: 'auto' }); } catch (err) { }
  }


  window.__raErr = null;
  function tick() {
    try { tickInner(); } catch (e) { window.__raErr = String((e && e.stack) || e); }
  }
  if (window.__raTimer) clearInterval(window.__raTimer);
  window.__raTimer = setInterval(tick, 250);
  tick();
})();
