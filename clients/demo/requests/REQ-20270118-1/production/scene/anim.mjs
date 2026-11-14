// anim.mjs: every moving thing as a pure function of time t (seconds). No state carried between frames.
import { clamp, lerp, smoothstep, easeInOutCubic, easeInOutSine } from './rng.mjs';

// ---- PCHIP (same formulas as project/build_timeline.py and scipy)
function pchipSlopes(xs, ys) {
  const n = xs.length, h = [], dl = [], d = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) { h.push(xs[i + 1] - xs[i]); dl.push((ys[i + 1] - ys[i]) / h[i]); }
  for (let k = 1; k < n - 1; k++) {
    if (dl[k - 1] * dl[k] <= 0) d[k] = 0;
    else { const w1 = 2 * h[k] + h[k - 1], w2 = h[k] + 2 * h[k - 1]; d[k] = (w1 + w2) / (w1 / dl[k - 1] + w2 / dl[k]); }
  }
  const edge = (h0, h1, d0, d1) => {
    const v = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1);
    if ((v > 0) !== (d0 > 0) || v === 0) return 0;
    if ((d0 > 0) !== (d1 > 0) && Math.abs(v) > 3 * Math.abs(d0)) return 3 * d0;
    return v;
  };
  d[0] = edge(h[0], h[1], dl[0], dl[1]);
  d[n - 1] = edge(h[n - 2], h[n - 3], dl[n - 2], dl[n - 3]);
  return d;
}
function makeNeedle(keys) {
  const xs = keys.map((k) => k.t), ys = keys.map((k) => k.day), d = pchipSlopes(xs, ys);
  return (t) => {
    if (t <= xs[0]) return ys[0];
    if (t >= xs[xs.length - 1]) return ys[ys.length - 1];
    let lo = 0, hi = xs.length - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (xs[m] <= t) lo = m; else hi = m; }
    const h = xs[lo + 1] - xs[lo], s = (t - xs[lo]) / h;
    const h00 = 2 * s ** 3 - 3 * s ** 2 + 1, h10 = s ** 3 - 2 * s ** 2 + s, h01 = -2 * s ** 3 + 3 * s ** 2, h11 = s ** 3 - s ** 2;
    return h00 * ys[lo] + h10 * h * d[lo] + h01 * ys[lo + 1] + h11 * h * d[lo + 1];
  };
}

// ---- the brand curve cubic-bezier(0.22, 1, 0.36, 1)
function cubicBezier(x1, y1, x2, y2) {
  const bx = (u) => 3 * (1 - u) * (1 - u) * u * x1 + 3 * (1 - u) * u * u * x2 + u * u * u;
  const by = (u) => 3 * (1 - u) * (1 - u) * u * y1 + 3 * (1 - u) * u * u * y2 + u * u * u;
  return (x) => {
    x = clamp(x, 0, 1);
    let lo = 0, hi = 1;
    for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (bx(m) < x) lo = m; else hi = m; }
    return by((lo + hi) / 2);
  };
}
export const easeBrand = cubicBezier(0.22, 1, 0.36, 1);
const quad = (p0, k, p1, e) => [(1 - e) * (1 - e) * p0[0] + 2 * e * (1 - e) * k[0] + e * e * p1[0], (1 - e) * (1 - e) * p0[1] + 2 * e * (1 - e) * k[1] + e * e * p1[1]];
export { quad };

export function makeAnim(T) {
  const E = T.events, EPS = T.lit.eps, FPS = T.fps;
  const needle = makeNeedle(T.needle_keys);
  const day = (t) => needle(t);
  const lit = (d) => d > 5 + EPS && d <= 28 + EPS;

  // band colour amount: a 3-frame ramp from every lit/unlit transition (a pure function of t)
  const fade = T.lit.fade_frames / FPS, a0 = T.lit.initial ? 1 : 0;
  const sm01 = (u) => { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); };
  function bandAmt(t) {
    let t0 = -1e9, v0 = a0, tg = a0;
    const val = (x) => v0 + (tg - v0) * sm01((x - t0) / fade);
    for (const tr of T.lit.transitions) {
      if (t < tr.t) break;
      const v = val(tr.t); t0 = tr.t; v0 = v; tg = tr.lit ? 1 : 0;
    }
    return val(t);
  }

  // drum
  function drumRev(t) {
    const d = E.drum, a = d.spin_up[0], b = Math.min(t, d.slow[1]);
    if (b <= a) return 0;
    const w = (x) => d.rev_per_s * smoothstep(d.spin_up[0], d.spin_up[1], x) * (1 - smoothstep(d.slow[0], d.slow[1], x));
    const n = 240; let s = 0, prev = w(a);
    for (let i = 1; i <= n; i++) { const x = a + (b - a) * i / n, cur = w(x); s += (prev + cur) / 2 * (b - a) / n; prev = cur; }
    return s;
  }
  function doorScale(t) {
    const d = E.door;
    if (t < d.open_t) return 1;
    if (t < d.open_t + d.open_dur) return Math.cos(Math.PI * (t - d.open_t) / d.open_dur);
    if (t < d.close_t) return -1;
    if (t < d.close_t + d.close_dur) return -Math.cos(Math.PI * (t - d.close_t) / d.close_dur);
    return 1;
  }
  const doorOpen = (t) => doorScale(t) < 0;

  const stirAngle = (t) => 2 * Math.PI * E.stir.revs * easeInOutSine((t - E.stir.t[0]) / (E.stir.t[1] - E.stir.t[0]));

  // lids
  const lid = (L, t) => L.lift * (smoothstep(L.up[0], L.up[0] + L.dur, t) - smoothstep(L.up[1] - L.dur, L.up[1], t));
  const lidA = (t) => lid(E.lid_a, t), lidB = (t) => lid(E.lid_b, t);

  // tray tip (degrees, positive = clockwise, lifts the left side)
  const trayAngle = (t) => E.tip.deg * (smoothstep(E.tip.up[0], E.tip.up[1], t) - smoothstep(E.tip.down[0], E.tip.down[1], t));
  function trayToWorld(p, t) { // local tray point -> world, at time t (before any slide-out)
    const a = trayAngle(t) * Math.PI / 180, px = E.tip.pivot[0], py = E.tip.pivot[1];
    const dx = p[0] - px, dy = p[1] - py;
    return [px + dx * Math.cos(a) - dy * Math.sin(a), py + dx * Math.sin(a) + dy * Math.cos(a)];
  }

  // scoop pose
  function scoopPose(t) {
    const K = E.scoop_keys;
    if (t <= K[0].t) return { x: K[0].x, y: K[0].y, rot: K[0].rot };
    if (t >= K[K.length - 1].t) { const k = K[K.length - 1]; return { x: k.x, y: k.y, rot: k.rot }; }
    let i = 0; while (K[i + 1].t <= t) i++;
    const a = K[i], b = K[i + 1], e = easeInOutCubic((t - a.t) / (b.t - a.t));
    const p = b.ctrl ? quad([a.x, a.y], b.ctrl, [b.x, b.y], e) : [lerp(a.x, b.x, e), lerp(a.y, b.y, e)];
    return { x: p[0], y: p[1], rot: lerp(a.rot, b.rot, e) };
  }
  const scoopLocalToWorld = (pose, l) => {
    const r = pose.rot * Math.PI / 180, k = E.scoop_scale, lx = l[0] * k, ly = l[1] * k;
    return [pose.x + lx * Math.cos(r) - ly * Math.sin(r), pose.y + lx * Math.sin(r) + ly * Math.cos(r)];
  };

  // stamp lever
  const LV = E.lever;
  function leverTheta(t) {
    if (t <= LV.down[0]) return LV.th_rest;
    if (t < LV.down[1]) { const u = (t - LV.down[0]) / (LV.down[1] - LV.down[0]); return LV.th_rest + (LV.th_hit - LV.th_rest) * u * u; }
    if (t <= LV.up[0]) return LV.th_hit;
    if (t < LV.up[1]) return LV.th_hit + (LV.th_rest - LV.th_hit) * easeBrand((t - LV.up[0]) / (LV.up[1] - LV.up[0]));
    return LV.th_rest;
  }
  function leverTip(t) {
    const th = leverTheta(t) * Math.PI / 180;
    return [LV.pivot[0] - LV.L * Math.cos(th), LV.pivot[1] + LV.L * Math.sin(th)];
  }
  const EPSF = 1e-6;
  const imprint = (t) => t >= LV.hit - EPSF;
  const squashing = (t) => t >= LV.hit - EPSF && t < LV.hit + LV.squash_s - EPSF;
  const bagDip = (t) => (t < LV.hit - EPSF ? 0 : LV.bag_dip * (t < LV.hit + LV.squash_s - EPSF ? 1 : 1 - smoothstep(LV.hit + LV.squash_s, LV.hit + LV.squash_s + 0.04, t)));
  const foldAmt = (t) => easeInOutCubic((t - E.bag_fold[0]) / (E.bag_fold[1] - E.bag_fold[0]));

  // call to action
  const CT = E.cta;
  const slideAt = (name) => CT.stagger.find((s) => s[0] === name)[1];
  const slide = (name, t) => CT.slide_dx[name] * easeBrand((t - slideAt(name)) / CT.slide_dur);
  const bagMove = (t) => easeBrand((t - CT.t[0]) / (CT.t[1] - CT.t[0]));

  return { day, lit, bandAmt, drumRev, doorScale, doorOpen, stirAngle, lidA, lidB, trayAngle, trayToWorld, scoopPose, scoopLocalToWorld,
    leverTheta, leverTip, imprint, squashing, bagDip, foldAmt, slide, bagMove, E, T };
}
