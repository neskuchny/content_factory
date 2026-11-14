// titles.mjs: titles (Fraunces 600, 68 px, copper keyword), CTA handle and demo mark. Text only by code.
import { C } from './cut.mjs';
import { easeBrand } from './anim.mjs';

const FONT_T = '600 68px Fraunces', LH = 68 * 1.12, X0 = 60, MAXW = 880, BASE1 = 340;

export function layoutTitles(P, T) {
  const ctx = P.ctx; ctx.save(); ctx.font = FONT_T; ctx.letterSpacing = '0px';
  const sp = ctx.measureText(' ').width, out = {};
  for (const t of T.titles) {
    const ks = t.text.indexOf(t.keyword), ke = ks + t.keyword.length;
    let idx = 0; const words = [];
    for (const w of t.text.split(' ')) {
      const pieces = []; let cur = '', curKw = null;
      for (let i = 0; i < w.length; i++) {
        const kw = idx + i >= ks && idx + i < ke;
        if (curKw !== null && kw !== curKw) { pieces.push({ s: cur, kw: curKw }); cur = ''; }
        cur += w[i]; curKw = kw;
      }
      pieces.push({ s: cur, kw: curKw });
      for (const p of pieces) p.w = ctx.measureText(p.s).width;
      words.push({ pieces, w: pieces.reduce((a, p) => a + p.w, 0) });
      idx += w.length + 1;
    }
    const total = words.reduce((a, w) => a + w.w, 0) + sp * (words.length - 1);
    let lines;
    if (total <= MAXW) lines = [words];
    else { // balanced two-line break (smallest widest line)
      let best = null;
      for (let k = 1; k < words.length; k++) {
        const a = words.slice(0, k), b = words.slice(k);
        const wa = a.reduce((s, w) => s + w.w, 0) + sp * (a.length - 1), wb = b.reduce((s, w) => s + w.w, 0) + sp * (b.length - 1);
        const m = Math.max(wa, wb);
        const inside = a[a.length - 1].pieces[a[a.length - 1].pieces.length - 1].kw && b[0].pieces[0].kw; // would split the keyword
        const score = m + (inside ? 10000 : 0);
        if (m <= MAXW && (!best || score < best.score)) best = { m, score, lines: [a, b] };
      }
      lines = best ? best.lines : [words];
    }
    const widths = lines.map((l) => l.reduce((s, w) => s + w.w, 0) + sp * (l.length - 1));
    out[t.id] = { lines, widths, sp, wmax: Math.max(...widths) };
  }
  ctx.restore();
  return out;
}

export function drawTitles(P, A, T, LAY, t) {
  const ctx = P.ctx;
  const list = [...T.titles, ...T.extras.map((x) => ({ ...x, extra: true }))];
  for (const tt of list) {
    if (t < tt.t0 || t > tt.t1) continue;
    const inn = tt.in != null ? tt.in : 0.35, out = tt.out != null ? tt.out : 0.25;
    const ein = easeBrand((t - tt.t0) / inn);
    // out: the brand curve mirrored (slow start, quick end), so the line is still readable until the last 0.1 s
    const uo = Math.min(1, Math.max(0, (t - (tt.t1 - out)) / out));
    const aout = tt.extra || tt.exit === false ? 1 : easeBrand(1 - uo);
    const alpha = ein * aout;
    if (alpha <= 0.002) continue;
    const dy = 24 * (1 - ein);
    if (tt.extra) {
      const big = tt.id === 'HANDLE';
      P.text(tt.text, X0, tt.y + dy, { font: '700 ' + (tt.size || (big ? 44 : 26)) + 'px Inter', color: C.espresso, base: 'middle', alpha: alpha * tt.alpha, id: tt.id, box: tt.id });
      continue;
    }
    const L = LAY[tt.id];
    ctx.save(); ctx.globalAlpha *= alpha;
    let y = BASE1 + dy;
    const asc = 68 * 0.74, desc = 68 * 0.25;
    L.lines.forEach((line, li) => {
      let x = X0;
      line.forEach((w, wi) => {
        for (const p of w.pieces) {
          ctx.font = FONT_T; ctx.fillStyle = p.kw ? C.copper : C.espresso; ctx.textBaseline = 'alphabetic'; ctx.letterSpacing = '0px';
          ctx.fillText(p.s, x, y + li * LH); x += p.w;
        }
        x += L.sp;
      });
    });
    ctx.restore();
    P.regRect(tt.id, X0, BASE1 + dy - asc, X0 + L.wmax, BASE1 + dy + LH * (L.lines.length - 1) + desc);
    P.drawn.push({ id: tt.id, text: tt.text, lines: L.lines.map((l) => l.map((w) => w.pieces.map((p) => p.s).join('')).join(' ')), alpha });
  }
}

// Day counter on the five hops (review fix, jury 1). "Day n" in copper under the title: the word "Day " is fixed, the numeral pops at the
// click time of each hop (rise 14 px + fade over 0.12 s on the brand curve) and the previous numeral leaves upward. It goes out with T3.
// A pure function of t and timeline.counter. Copper is allowed here by the director's decision for this fix (band, keywords, counter).
export function drawCounter(P, A, T, t) {
  const K = T.counter, ctx = P.ctx, it = K.items;
  if (!K || t < it[0].t || t > K.t1) return;
  let k = 0; while (k + 1 < it.length && it[k + 1].t <= t) k++;
  const e = easeBrand((t - it[k].t) / K.pop_s);
  const uo = Math.min(1, Math.max(0, (t - (K.t1 - K.out)) / K.out)), aout = easeBrand(1 - uo);
  if (aout <= 0.002) return;
  ctx.save(); ctx.font = K.font; ctx.letterSpacing = '0px';
  const wDay = ctx.measureText('Day ').width, wNum = ctx.measureText(String(it[k].n)).width;
  const m = ctx.measureText('Day ' + it[k].n); ctx.restore();
  const aDay = (k === 0 ? e : 1) * aout;
  P.text('Day ', K.x, K.y, { font: K.font, color: C.copper, alpha: aDay });
  P.text(String(it[k].n), K.x + wDay, K.y + K.rise_px * (1 - e), { font: K.font, color: C.copper, alpha: e * aout });
  if (k > 0 && e < 0.999) P.text(String(it[k - 1].n), K.x + wDay, K.y - K.rise_px * e, { font: K.font, color: C.copper, alpha: (1 - e) * aout });
  // registered once as one text "Day n" (the numeral on top of the screen position it settles at)
  P.regRect('COUNTER', K.x, K.y - m.actualBoundingBoxAscent, K.x + wDay + wNum, K.y + m.actualBoundingBoxDescent);
  P.drawn.push({ id: 'COUNTER', text: 'Day ' + it[k].n, alpha: e * aout, n: it[k].n, settled: e >= 0.999 });
}
