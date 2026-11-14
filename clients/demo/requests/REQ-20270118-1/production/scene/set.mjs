// set.mjs: the shelf and everything on it: roaster (generic pictogram), chute, cooling tray, resting bin, scoop, bag, stamp lever.
import { C, mix, rrect, ell, poly, bar } from './cut.mjs';

const SCOOP_C = mix(C.creamDark, C.espLight, 0.55);
const KRAFT_BACK = mix(C.kraft, C.espresso, 0.30);
const KRAFT_SIDE = mix(C.kraft, C.espresso, 0.12);
const KRAFT_FLAP = mix(C.kraft, C.cream, 0.18);
const KRAFT_CREASE = mix(C.kraft, C.espresso, 0.22);
const BEAN_SLIT = mix(C.bean, C.espresso, 0.55);
const CHUTE_FLOOR = C.creamDark;
const LID_C = mix(C.creamDark, C.espLight, 0.3);

export function drawBean(P, b, s) {
  const ctx = P.ctx, rx = b.size / 2, ry = b.size / 2 * 0.72;
  ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(s.rot);
  P.fill('bean' + b.kind + (b.trip != null ? b.trip : '') + (b.k != null ? b.k : b.i), ell(0, 0, rx, ry), C.bean, { shadow: s.shadow ? 'lifted' : null });
  P.fill('slit' + b.kind + (b.trip != null ? b.trip : '') + (b.k != null ? b.k : b.i), bar(-rx * 0.62, 0, rx * 0.62, 0, 1.6), BEAN_SLIT);
  ctx.restore();
}

function drawBeansLayer(P, B, beanStates, layer, frame) {
  for (const [b, s] of beanStates) if (s.layer === layer && (!frame || s.frame === frame)) drawBean(P, b, s);
}

export function drawShelf(P) {
  P.fill('shelf', rrect(60, 1040, 960, 20, 4), C.espLight, { shadow: 'standing', box: 'shelf' });
}

export function drawRoaster(P, A, t, dx, BS) {
  const ctx = P.ctx, rev = A.drumRev(t), sx = A.doorScale(t);
  ctx.save(); ctx.translate(dx, 0);
  const o = { box: 'roaster' };
  P.fill('r_legL', rrect(100, 898, 30, 142, 6), C.espLight, { shadow: 'standing', ...o });
  P.fill('r_legR', rrect(280, 898, 30, 142, 6), C.espLight, { shadow: 'standing', ...o });
  P.fill('r_base', rrect(80, 886, 250, 24, 8), C.espLight, { shadow: 'standing', ...o });
  P.fill('r_chim', rrect(290, 600, 25, 126, 5), C.espLight, { shadow: 'standing', ...o });
  P.fill('r_hop', poly([[160, 642], [250, 642], [236, 724], [174, 724]]), C.espLight, { shadow: 'standing', ...o });
  P.fill('r_hoprim', rrect(150, 630, 110, 16, 6), C.creamDark, { shadow: 'standing', ...o });
  P.fill('r_drum', rrect(90, 720, 230, 180, 18), C.espLight, { shadow: 'standing', edge: true, ...o });
  P.fill('r_gauge', ell(122, 752, 14, 14), C.creamDark);
  P.fill('r_gauge_n', bar(122, 752, 130, 744, 4), C.espresso);
  // chute (a channel: darker walls, light floor so the beans read)
  P.fill('chute_wall', poly([[270.9, 846.9], [390.9, 946.9], [369.1, 973.1], [249.1, 873.1]]), C.espLight, { shadow: 'standing', ...o });
  P.fill('chute_floor', poly([[267.7, 850.8], [387.7, 950.8], [372.3, 969.2], [252.3, 869.2]]), CHUTE_FLOOR);
  // front disc with six spokes, spinning with the drum
  P.fill('r_disc', ell(205, 810, 70, 70), C.creamDark);
  P.fill('r_disc_in', ell(205, 810, 58, 58), C.espLight);
  for (let k = 0; k < 6; k++) {
    ctx.save(); ctx.translate(205, 810); ctx.rotate(rev * Math.PI * 2 + k * Math.PI / 3);
    P.fill('spoke' + k, bar(0, 0, 54, 0, 10), C.creamDark);
    ctx.restore();
  }
  P.fill('r_hub', ell(205, 810, 14, 14), C.creamDark);
  // beans emerging and sliding down the chute (only while the door is open)
  drawBeansLayer(P, null, BS, 'chute');
  // door: flips on its vertical axis; inner side is espresso
  if (Math.abs(sx) > 0.04) {
    ctx.save(); ctx.translate(205, 810); ctx.scale(sx, 1);
    P.fill('r_door', ell(0, 0, 34, 34), sx > 0 ? C.creamDark : C.espresso, { shadow: sx > 0 ? 'standing' : 'lifted' });
    if (sx > 0) P.fill('r_door_h', rrect(14, -4, 14, 8, 3), C.espLight);
    ctx.restore();
  }
  ctx.restore();
}

export function drawTray(P, A, t, dx, BS) {
  const ctx = P.ctx, E = A.E, pv = E.tip.pivot;
  ctx.save(); ctx.translate(dx, 0);
  ctx.translate(pv[0], pv[1]); ctx.rotate(A.trayAngle(t) * Math.PI / 180); ctx.translate(-pv[0], -pv[1]);
  P.fill('tray_o', ell(425, 985, 90, 28), C.espLight, { shadow: 'standing', edge: true, box: 'tray' });
  P.fill('tray_i', ell(425, 983, 79, 20), C.creamDark);
  drawBeansLayer(P, null, BS, 'tray');
  // stir arm: a bar swinging around the hub; flat view, so the sweep is squashed
  const ph = A.stirAngle(t);
  P.fill('stir_hub', ell(425, 983, 11, 8), C.espLight);
  P.fill('stir_arm', bar(425, 983, 425 + 74 * Math.cos(ph), 983 + 15 * Math.sin(ph), 12, 8), C.espLight, { shadow: 'lifted', dyn: true });
  ctx.restore();
}

export function drawBin(P, A, t, dx, BS) {
  const ctx = P.ctx, lid = A.lidA(t) + A.lidB(t);
  ctx.save(); ctx.translate(dx, 0);
  P.fill('bin_in', rrect(578, 868, 134, 24, 6), C.espresso, { box: 'bin' });          // dark mouth, seen when the lid is up
  drawBeansLayer(P, null, BS, 'hop');
  P.fill('bin_body', rrect(575, 880, 140, 160, 16), C.espLight, { shadow: 'standing', edge: true, box: 'bin' });
  P.fill('bin_rib1', rrect(587, 936, 116, 6, 3), C.creamDark);
  P.fill('bin_rib2', rrect(587, 984, 116, 6, 3), C.creamDark);
  ctx.save(); ctx.translate(0, -lid); // static outline, moved by a transform (a cached cut edge never changes shape)
  P.fill('bin_lid', rrect(565, 860, 160, 20, 7), LID_C, { shadow: lid > 1 ? 'lifted' : 'standing', box: 'bin' });
  P.fill('bin_lid_h', rrect(628, 852, 34, 10, 4), C.espLight, { box: 'bin' });
  ctx.restore();
  ctx.restore();
}

export function drawScoop(P, A, t, dx, BS) {
  const ctx = P.ctx, pose = A.scoopPose(t);
  ctx.save(); ctx.translate(dx, 0); ctx.translate(pose.x, pose.y); ctx.rotate(pose.rot * Math.PI / 180); ctx.scale(A.E.scoop_scale, A.E.scoop_scale);
  const bowl = [];
  for (let i = 0; i <= 14; i++) { const a = (i / 14) * Math.PI; bowl.push([24 * Math.cos(a), 24 * Math.sin(a)]); }
  P.fill('scoop_handle', bar(-20, -3, -90, -13, 9), SCOOP_C, { shadow: 'lifted', box: 'scoop' });
  P.fill('scoop_bowl', poly(bowl), SCOOP_C, { shadow: 'lifted', edge: true, box: 'scoop' });
  P.fill('scoop_lip', rrect(-27, -4, 54, 7, 3), SCOOP_C, { shadow: 'lifted', box: 'scoop' });
  drawBeansLayer(P, null, BS, 'scoop');
  ctx.restore();
}

export function drawBag(P, A, t, BS) {
  const ctx = P.ctx, E = A.E, mv = A.bagMove(t), sc = 1 + (E.cta.scale - 1) * mv, dxb = (E.cta.bag_x - 870) * mv, dip = A.bagDip(t);
  ctx.save();
  ctx.translate(870 + dxb, 1040 + dip); ctx.scale(sc, sc); ctx.translate(-870, -1040);
  P.fill('bag_back', rrect(790, 820, 160, 220, 6), KRAFT_BACK, { shadow: 'standing', box: 'bag' });
  // beans thrown from the scoop fall into the mouth, behind the front panel
  drawBeansLayer(P, null, BS, 'throw');
  P.fill('bag_front', poly([[790, 840], [800, 836], [940, 836], [950, 840], [950, 1034], [944, 1040], [796, 1040], [790, 1034]]), C.kraft, { edge: true, box: 'bag' });
  P.fill('bag_side', rrect(932, 842, 18, 198, 4), KRAFT_SIDE);
  P.fill('label', rrect(815, 900, 110, 90, 4), C.cream, { box: 'label' });
  // fold: the top 40 px folds over (sealed)
  const f = A.foldAmt(t);
  if (f > 0.001) {
    ctx.save(); ctx.beginPath(); ctx.rect(780, 820, 180, 80); ctx.clip(); ctx.translate(0, 44 * f - 44); // the flap slides down over the mouth
    P.fill('bag_flap', poly([[788, 820], [952, 820], [952, 864], [788, 864]]), KRAFT_FLAP, { shadow: 'standing', box: 'bag' });
    P.fill('bag_crease', poly([[788, 859], [952, 859], [952, 864], [788, 864]]), KRAFT_CREASE);
    ctx.restore();
  }
  // imprint: appears on the frame the pad touches the label
  if (A.imprint(t)) {
    const o = { font: '700 22px Inter', color: C.espresso, align: 'center', base: 'middle' };
    P.text('ROAST', 870, 922, { ...o, box: 'IMPRINT' });
    P.text('DATE', 870, 946, { ...o, box: 'IMPRINT' });
    P.drawn.push({ id: 'IMPRINT', text: 'ROAST DATE' });
    for (let i = 0; i < 3; i++) P.fill('imp_bar' + i, rrect(829 + i * 30, 966, 22, 7, 2), C.espresso, { box: 'IMPRINT' });
  }
  ctx.restore();
}

export function drawLever(P, A, t, dx) {
  const ctx = P.ctx, LV = A.E.lever, tip = A.leverTip(t), th = A.leverTheta(t);
  ctx.save(); ctx.translate(dx, 0);
  P.fill('stand', rrect(990, 775, 30, 265, 6), C.espLight, { shadow: 'standing', edge: true, box: 'lever' });
  ctx.save(); ctx.translate(LV.pivot[0], LV.pivot[1]); ctx.rotate(-th * Math.PI / 180);
  P.fill('arm', bar(0, 0, -LV.L, 0, 16), C.espLight, { shadow: 'lifted', box: 'lever' });
  ctx.restore();
  P.fill('hinge', ell(LV.pivot[0], LV.pivot[1], 20, 20), C.creamDark, { box: 'lever' });
  // pad: hangs from the tip; squashes 4 % for two frames at the impact
  const sq = A.squashing(t) ? 1 - LV.squash : 1;
  // the bottom edge stays fixed while the pad squashes
  ctx.save(); ctx.translate(tip[0], tip[1] + 33); ctx.scale(1, sq);
  P.fill('pad_post', rrect(-6, -44, 12, 24, 3), C.espLight, { box: 'pad' });
  P.fill('pad', rrect(-50, -22, 100, 22, 5), C.espresso, { shadow: 'lifted', box: 'pad' });
  ctx.restore();
  ctx.restore();
}
