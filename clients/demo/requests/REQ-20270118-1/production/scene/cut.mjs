// cut.mjs: paper-cut drawing kit. Palette, cut-edge noise (fixed per shape, never per frame), two shadow depths,
// text and box registration. Everything is a filled shape: no strokes, no gradients.
import { vnoise1, hashStr } from './rng.mjs';

export const SEED = 20270118;
export const C = { cream: '#F6EFE6', espresso: '#2B1D14', copper: '#C26A2E', kraft: '#E1BA9C', creamDark: '#E6DED5', espLight: '#54473E', bean: '#51301B' };
const h2r = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
export const mix = (a, b, p) => { // p = share of b
  const x = h2r(a), y = h2r(b);
  return '#' + x.map((v, i) => Math.round(v * (1 - p) + y[i] * p).toString(16).padStart(2, '0')).join('');
};
export const SHADOW = { standing: { ox: 6, oy: 8, blur: 12, a: 0.20 }, lifted: { ox: 10, oy: 14, blur: 18, a: 0.14 } };
const CUT_AMP = 1.2; // px at 1080 wide

// ---- outlines (closed polylines in local coordinates), subdivided so the cut edge can wobble along every side
function subdiv(pts, step = 9) {
  const out = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i + 1) % pts.length];
    const n = Math.max(1, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / step));
    for (let k = 0; k < n; k++) out.push([a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n]);
  }
  return out;
}
export function poly(arr) { return subdiv(arr); }
export function rrect(x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  const pts = [];
  const arc = (cx, cy, a0) => { for (let i = 0; i <= 4; i++) { const a = a0 + (Math.PI / 2) * i / 4; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } };
  arc(x + w - r, y + r, -Math.PI / 2); arc(x + w - r, y + h - r, 0); arc(x + r, y + h - r, Math.PI / 2); arc(x + r, y + r, Math.PI);
  return subdiv(pts);
}
export function ell(cx, cy, rx, ry) {
  const n = Math.max(20, Math.round((Math.PI * (rx + ry)) / 7));
  const pts = [];
  for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2; pts.push([cx + rx * Math.cos(a), cy + ry * Math.sin(a)]); }
  return pts;
}
export function bar(x0, y0, x1, y1, th, N) { // a straight strip of thickness th; N = fixed split count (for strips whose length changes)
  const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy) || 1, nx = -dy / L * th / 2, ny = dx / L * th / 2;
  const A = [x0 + nx, y0 + ny], B = [x1 + nx, y1 + ny], Cc = [x1 - nx, y1 - ny], D = [x0 - nx, y0 - ny];
  if (!N) return subdiv([A, B, Cc, D]);
  const pts = [], seg = (a, b, n) => { for (let k = 0; k < n; k++) pts.push([a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n]); };
  seg(A, B, N); seg(B, Cc, 2); seg(Cc, D, N); seg(D, A, 2);
  return pts;
}

export class Paper {
  constructor(ctx, W, H) {
    this.ctx = ctx; this.W = W; this.H = H; this.S = W / 1080;
    this.cache = new Map(); this.boxes = {}; this.drawn = [];
  }
  begin() {
    const { ctx, S } = this;
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    ctx.shadowColor = 'rgba(0,0,0,0)'; ctx.shadowBlur = 0; ctx.shadowOffsetX = 0; ctx.shadowOffsetY = 0;
    ctx.setTransform(S, 0, 0, S, 0, 0);
    this.boxes = {}; this.drawn = [];
  }
  // cut edge: fixed offset per vertex from seeded noise
  cut(key, pts, dyn) { // dyn: geometry changes between frames (fixed vertex count), so it is not cached
    let p = dyn ? null : this.cache.get(key);
    if (p) return p;
    const hs = hashStr(key) ^ SEED;
    p = pts.map((q, i) => [q[0] + (vnoise1(i * 0.55, hs) - 0.5) * 2 * CUT_AMP, q[1] + (vnoise1(i * 0.55 + 57.3, hs ^ 0x9e37) - 0.5) * 2 * CUT_AMP]);
    if (!dyn) this.cache.set(key, p);
    return p;
  }
  path(p) {
    const ctx = this.ctx;
    ctx.beginPath(); ctx.moveTo(p[0][0], p[0][1]);
    for (let i = 1; i < p.length; i++) ctx.lineTo(p[i][0], p[i][1]);
    ctx.closePath();
  }
  // o: {shadow:'standing'|'lifted', edge:true, alpha, box:'name'}
  fill(key, pts, color, o = {}) {
    const { ctx, S } = this;
    const p = this.cut(key, pts, o.dyn);
    ctx.save();
    if (o.alpha != null) ctx.globalAlpha *= o.alpha;
    if (o.shadow) {
      const sh = SHADOW[o.shadow];
      ctx.shadowColor = `rgba(43,29,20,${sh.a})`; ctx.shadowOffsetX = sh.ox * S; ctx.shadowOffsetY = sh.oy * S; ctx.shadowBlur = sh.blur * S;
    }
    this.path(p);
    if (o.edge) { // light catches the top-left cut edge: a lighter sheet under, the colour sheet shifted over it
      ctx.fillStyle = mix(color, C.cream, 0.32); ctx.fill();
      ctx.shadowColor = 'rgba(0,0,0,0)';
      ctx.save(); ctx.clip(); ctx.translate(1.6, 1.9); this.path(p); ctx.fillStyle = color; ctx.fill(); ctx.restore();
    } else { ctx.fillStyle = color; ctx.fill(); }
    ctx.restore();
    if (o.box) this.reg(o.box, p);
  }
  // union of the transformed points into boxes[name], in design units
  reg(name, p) {
    const m = this.ctx.getTransform(), S = this.S;
    let b = this.boxes[name];
    for (const q of p) {
      const X = (m.a * q[0] + m.c * q[1] + m.e) / S, Y = (m.b * q[0] + m.d * q[1] + m.f) / S;
      if (!b) b = this.boxes[name] = [X, Y, X, Y];
      else { if (X < b[0]) b[0] = X; if (Y < b[1]) b[1] = Y; if (X > b[2]) b[2] = X; if (Y > b[3]) b[3] = Y; }
    }
  }
  regRect(name, x0, y0, x1, y1) { this.reg(name, [[x0, y0], [x1, y1]]); }
  // printed text (no shadow). o: {font, color, align, base, spacing, alpha, id, box, drawnText}
  text(str, x, y, o) {
    const { ctx } = this;
    ctx.save();
    ctx.font = o.font; ctx.fillStyle = o.color; ctx.textAlign = o.align || 'left'; ctx.textBaseline = o.base || 'alphabetic';
    ctx.letterSpacing = o.spacing || '0px';
    if (o.alpha != null) ctx.globalAlpha *= o.alpha;
    ctx.fillText(str, x, y);
    const m = ctx.measureText(str);
    ctx.restore();
    const w = m.width, asc = m.actualBoundingBoxAscent, desc = m.actualBoundingBoxDescent;
    const x0 = o.align === 'center' ? x - w / 2 : o.align === 'right' ? x - w : x;
    if (o.box) this.reg(o.box, [[x0, y - asc], [x0 + w, y + desc]]);
    if (o.id) this.drawn.push({ id: o.id, text: o.drawnText || str });
    return w;
  }
}
