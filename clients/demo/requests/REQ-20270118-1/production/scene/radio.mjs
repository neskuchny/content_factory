// radio.mjs: the paper radio. The dial counts days after roast. One cause moves the needle: the knob (12 deg per day).
import { C, mix, rrect, ell, poly, bar } from './cut.mjs';

const X0 = 150, PXD = 26;
export const dayX = (d) => X0 + PXD * d;

export function drawRadio(P, A, t) {
  const ctx = P.ctx;
  const day = A.day(t), amt = A.bandAmt(t);
  // body and dial face
  P.fill('radio_body', rrect(60, 1090, 960, 410, 16), C.espresso, { shadow: 'standing', edge: true, box: 'radio' });
  P.fill('dial_face', rrect(110, 1130, 860, 180, 16), C.cream);
  // band 5..28 (copper only while the needle is inside)
  P.fill('band', rrect(dayX(5), 1145, dayX(28) - dayX(5), 125, 10), mix(C.creamDark, C.copper, amt), { box: 'band' });
  // ticks: a tick per day, longer at 0, 5 and 28
  for (let d = 0; d <= 31; d++) {
    const major = d === 0 || d === 5 || d === 28;
    const w = major ? 8 : 6, y0 = major ? 1150 : 1160, y1 = major ? 1198 : 1188;
    P.fill('tick' + d, bar(dayX(d), y0, dayX(d), y1, w), C.espresso);
  }
  // numbers (labels): baseline 1284 (was 1258) so the needle, which now ends at y 1226 (was 1305), never touches them (review fix, jury 2)
  for (const d of [0, 5, 28]) {
    P.text(String(d), dayX(d), 1284, { font: '700 44px Inter', color: C.espresso, align: 'center', id: 'L' + d, box: 'L' + d });
  }
  // needle
  const nx = dayX(day);
  ctx.save(); ctx.translate(nx, 0);
  P.fill('needle', poly([[-4, 1147], [0, 1135], [4, 1147], [4, 1226], [-4, 1226]]), C.espresso, { shadow: 'standing', box: 'needle' });
  ctx.restore();
  // label on the body
  P.text('DAYS AFTER ROAST', 540, 1345, { font: '700 30px Inter', color: C.cream, align: 'center', base: 'middle', spacing: '3.6px', id: 'LABEL_DAYS', box: 'LABEL_DAYS' });
  // grille
  for (let i = 0; i < 5; i++) P.fill('grille' + i, rrect(120, 1390 + 20 * i, 660, 10, 5), C.espLight);
  // knob: turns by exactly 12 deg per day
  const kd = 12 * day;
  ctx.save(); ctx.translate(900, 1430); ctx.rotate(kd * Math.PI / 180);
  const pts = [];
  for (let i = 0; i < 96; i++) { const a = (i / 96) * Math.PI * 2; pts.push([(62 + 3.2 * Math.cos(12 * a)) * Math.cos(a), (62 + 3.2 * Math.cos(12 * a)) * Math.sin(a)]); }
  P.fill('knob', pts, C.creamDark, { shadow: 'standing', edge: true, box: 'knob' });
  P.fill('knob_in', ell(0, 0, 44, 44), mix(C.creamDark, C.espLight, 0.12));
  P.fill('knob_mark', rrect(-5, -50, 10, 30, 4), C.espLight);
  ctx.restore();
  return { day, kd, amt };
}
