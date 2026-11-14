// main.mjs: Freshness dial (REQ-20270118-1). Frame contract:
//   window.READY -> {frames, fps, width, height};  window.__seek(t) draws frame t synchronously;  window.__grab(fmt) -> dataURL
//   window.__drawn text strings on the frame;  window.__boxes() named screen rects (design units, 1080x1920)
//   window.__state() {day, knob_deg, band_lit, drum_rev, ...};  window.__beans() visible beans;  window.__dump(a,b) per-frame records.
// A frame is a pure function of (t, seed, timeline). Math.random, Date and performance.now are not used.
import { loadFonts, fontTest } from './fonts.mjs';
import { makeGrainTile, paintGrain } from './grain.mjs';
import { Paper, C, SEED } from './cut.mjs';
import { makeAnim } from './anim.mjs';
import { makeBeans } from './beans.mjs';
import { drawShelf, drawRoaster, drawTray, drawBin, drawScoop, drawBag, drawLever } from './set.mjs';
import { drawRadio } from './radio.mjs';
import { layoutTitles, drawTitles, drawCounter } from './titles.mjs';

const q = new URLSearchParams(location.search);
const W = +q.get('w') || 1080, H = +q.get('h') || 1920, SEEDQ = +q.get('seed') || SEED;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const ctx = cv.getContext('2d');

window.READY = (async () => {
  await loadFonts();
  const T = await (await fetch('../data/timeline.json')).json();
  const A = makeAnim(T), P = new Paper(ctx, W, H), B = makeBeans(A, SEEDQ);
  const tile = makeGrainTile(SEEDQ), LAY = layoutTitles(P, T);
  let last = null;

  function render(t) {
    P.begin();
    ctx.fillStyle = C.cream; ctx.fillRect(0, 0, 1080, 1920);
    const BS = [];
    for (const b of B.list) { const s = B.state(b, t); if (s) BS.push([b, s]); }
    drawShelf(P);
    drawRoaster(P, A, t, A.slide('roaster', t), BS);
    drawTray(P, A, t, A.slide('tray', t), BS);
    drawBin(P, A, t, A.slide('bin', t), BS);
    drawScoop(P, A, t, A.slide('bin', t), BS);
    drawBag(P, A, t, BS);
    drawLever(P, A, t, A.slide('lever', t));
    const rs = drawRadio(P, A, t);
    drawTitles(P, A, T, LAY, t);
    drawCounter(P, A, T, t);
    paintGrain(ctx, tile, P.S);
    last = { t, BS, day: rs.day, knob_deg: rs.kd, band_amt: rs.amt };
  }

  const state = () => ({
    t: last.t, day: last.day, knob_deg: last.knob_deg, band_lit: A.lit(last.day), band_amt: last.band_amt, drum_rev: A.drumRev(last.t),
    door_open: A.doorOpen(last.t), lid_a: A.lidA(last.t), lid_b: A.lidB(last.t), tray_deg: A.trayAngle(last.t), imprint: A.imprint(last.t),
    lever_deg: A.leverTheta(last.t),
  });
  const beansWorld = () => last.BS.map(([b, s]) => {
    let p = [s.x, s.y];
    if (s.frame === 'tray') { p = A.trayToWorld(p, last.t); p[0] += A.slide('tray', last.t); }
    else if (s.frame === 'scoop') p = A.scoopLocalToWorld(A.scoopPose(last.t), p);
    return { id: b.kind + (b.trip != null ? b.trip : '') + (b.k != null ? '_' + b.k : '_' + b.i), tag: s.tag, x: +p[0].toFixed(2), y: +p[1].toFixed(2) };
  });

  window.__seek = (t) => render(t);
  window.__grab = (fmt) => cv.toDataURL(fmt === 'jpeg' ? 'image/jpeg' : 'image/png', 0.92);
  Object.defineProperty(window, '__drawn', { get: () => P.drawn });
  window.__boxes = () => P.boxes;
  window.__state = state;
  window.__beans = beansWorld;
  window.__fontTest = fontTest;
  window.__timeline = T;
  window.__beanEvents = () => B.events();
  // cover (shotlist.json -> cover): frame 12.70 zoomed on the dial (band lit) + the label "Day 5 to 28", all drawn by code
  window.__cover = () => {
    render(T.cover.frame_t);
    const tmp = document.createElement('canvas'); tmp.width = W; tmp.height = H; tmp.getContext('2d').drawImage(cv, 0, 0);
    const k = W / 1080;
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = C.cream; ctx.fillRect(0, 0, W, H);
    const sx = 90 * k, sy = 1100 * k, sw = 900 * k, sh = 225 * k;            // dial close-up: the face with band 5..28 and the needle
    ctx.drawImage(tmp, sx, sy, sw, sh, 0, 760 * k, W, sh * (W / sw));
    ctx.setTransform(k, 0, 0, k, 0, 0);
    ctx.font = '600 150px Fraunces'; ctx.textBaseline = 'alphabetic'; ctx.letterSpacing = '0px';
    const parts = [['Day ', C.espresso], ['5 to 28', C.copper]]; let x = 80;
    for (const [s, col] of parts) { ctx.fillStyle = col; ctx.fillText(s, x, 560); x += ctx.measureText(s).width; }
    paintGrain(ctx, tile, P.S);
    return cv.toDataURL('image/jpeg', 0.92);
  };
  window.__dump = (a, b) => {
    const out = [];
    for (let f = a; f <= b; f++) {
      render(f / T.fps);
      out.push({ f, s: state(), drawn: P.drawn.map((d) => ({ id: d.id, text: d.text, lines: d.lines || null })), boxes: JSON.parse(JSON.stringify(P.boxes)), beans: beansWorld() });
    }
    return out;
  };
  return { frames: T.frames, fps: T.fps, width: W, height: H };
})();
