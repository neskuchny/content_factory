// beans.mjs: every bean is a seeded paper ellipse whose position is a pure function of t.
// Route of a bean: door -> chute -> tray -> (tray tips) -> bin ... bin -> scoop -> bag. Nothing appears from nowhere.
import { mulberry32, lerp } from './rng.mjs';
import { quad } from './anim.mjs';

export function makeBeans(A, seed) {
  const E = A.E, rnd = mulberry32(seed ^ 0x0BEA2);
  const beans = [];
  const C0 = [262, 860], C1 = [378, 958], NORM = [-100 / 156, 120 / 156]; // chute start, end, unit normal (screen)
  const pour = E.pour, tip = E.tip;

  // -- 40 roasted beans: drum -> chute -> tray -> bin
  for (let i = 0; i < pour.n; i++) {
    const g = rnd() + rnd() - 1;
    const b = {
      kind: 'tray', i, size: 12 + rnd() * 4, rot: rnd() * Math.PI,
      t0: pour.t[0] + (i / (pour.n - 1)) * (pour.t[1] - pour.t[0] - 0.02) + (rnd() - 0.5) * 0.008,
      chute: pour.chute_s + (rnd() - 0.5) * 0.06, lane: (rnd() - 0.5) * 9,
      door: [205 + (rnd() - 0.5) * 18, 810 + (rnd() - 0.5) * 18],
      L: null, lip: [498 + rnd() * 8, 980 + (rnd() - 0.5) * 8], K: [538 + (rnd() - 0.5) * 14, 800 + (rnd() - 0.5) * 20], Eb: [598 + rnd() * 74, 902],
    };
    const hump = 15 * (1 - g * g) * (0.45 + 0.55 * rnd());
    b.L = [412 + g * 62, 985 - 6 - hump + (rnd() - 0.5) * 3];
    beans.push(b);
  }
  const order = beans.map((b) => b).sort((a, b) => b.L[0] - a.L[0]);
  order.forEach((b, r) => { b.depart = tip.depart[0] + (r / (pour.n - 1)) * (tip.depart[1] - tip.depart[0]); });

  // -- 2 x 12 beans in the scoop: bin -> bowl -> bag
  E.scoop_pours.forEach((sp, j) => {
    for (let k = 0; k < sp.n; k++) {
      const col = k % 6, row = Math.floor(k / 6);
      const hump = 4 * (1 - Math.pow((col - 2.5) / 2.5, 2));
      beans.push({
        kind: 'scoop', trip: j, k, size: 12 + rnd() * 4, rot: rnd() * Math.PI,
        load: E.scoop_dips[j], leave: sp.t[0] + (k / (sp.n - 1)) * (sp.t[1] - sp.t[0]), fall: sp.fall_s + (rnd() - 0.5) * 0.03,
        H: [-16 + col * 6.4 + (rnd() - 0.5) * 2.5, -7 - row * 6 - hump + (rnd() - 0.5) * 2],
        M: [828 + rnd() * 86, 838],
      });
    }
  });

  const chuteAt = (u, lane) => [lerp(C0[0], C1[0], u) + NORM[0] * lane, lerp(C0[1], C1[1], u) + NORM[1] * lane];

  // state: {layer, frame:'world'|'tray'|'scoop', x, y, rot, tag, shadow} or null (not visible)
  function state(b, t) {
    if (b.kind === 'tray') {
      const tA = b.t0 + pour.door_to_chute_s, tB = tA + b.chute, tC = tB + pour.fall_s;
      if (t < b.t0) return null;
      if (t < tA) {
        const u = (t - b.t0) / pour.door_to_chute_s, e = Math.pow(u, 1.5);
        const to = chuteAt(0, b.lane);
        return { layer: 'chute', frame: 'world', x: lerp(b.door[0], to[0], e), y: lerp(b.door[1], to[1], e), rot: b.rot + u, tag: 'door_to_chute', shadow: true };
      }
      if (t < tB) {
        const u = (t - tA) / b.chute, s = 0.4 * u + 0.6 * u * u, p = chuteAt(s, b.lane);
        return { layer: 'chute', frame: 'world', x: p[0], y: p[1], rot: b.rot + 2 * u, tag: 'chute', shadow: true };
      }
      if (t < tC) {
        const u = (t - tB) / pour.fall_s, from = chuteAt(1, b.lane);
        return { layer: 'tray', frame: 'tray', x: lerp(from[0], b.L[0], u), y: lerp(from[1], b.L[1], u * u), rot: b.rot + u, tag: 'fall', shadow: true };
      }
      if (t < b.depart) return { layer: 'tray', frame: 'tray', x: b.L[0], y: b.L[1], rot: b.rot, tag: 'tray', shadow: false };
      const tH = b.depart + tip.slide_s;
      if (t < tH) {
        const u = (t - b.depart) / tip.slide_s, e = u * u;
        return { layer: 'tray', frame: 'tray', x: lerp(b.L[0], b.lip[0], e), y: lerp(b.L[1], b.lip[1], e), rot: b.rot + 3 * u, tag: 'slide', shadow: false };
      }
      if (t < tH + tip.hop_s) {
        const u = (t - tH) / tip.hop_s, w0 = A.trayToWorld(b.lip, tH), p = quad(w0, b.K, b.Eb, u);
        return { layer: 'hop', frame: 'world', x: p[0], y: p[1], rot: b.rot + 3 + 4 * u, tag: 'hop', shadow: true };
      }
      return null; // inside the bin
    }
    // scoop beans
    if (t < b.load) return null;
    if (t < b.leave) return { layer: 'scoop', frame: 'scoop', x: b.H[0], y: b.H[1], rot: b.rot, tag: 'scoop', shadow: false };
    if (t < b.leave + b.fall) {
      const u = (t - b.leave) / b.fall, pose = A.scoopPose(b.leave), s0 = A.scoopLocalToWorld(pose, b.H);
      const k = [(s0[0] + b.M[0]) / 2 + 14, Math.min(s0[1], b.M[1]) - 22], p = quad(s0, k, b.M, u);
      return { layer: 'throw', frame: 'world', x: p[0], y: p[1], rot: b.rot + 5 * u, tag: 'throw', shadow: true };
    }
    return null; // inside the bag
  }
  // event times of every bean (for project/sound.py): written to data/bean_events.json by render.cjs --events
  function events() {
    return beans.map((b) => {
      const r6 = (v) => +v.toFixed(4);
      if (b.kind === 'tray') {
        const tA = b.t0 + pour.door_to_chute_s, tB = tA + b.chute, tC = tB + pour.fall_s, tH = b.depart + tip.slide_s;
        return { kind: 'tray', i: b.i, door: r6(b.t0), chute: r6(tA), fall: r6(tB), land: r6(tC), depart: r6(b.depart), hop: r6(tH), arrive: r6(tH + tip.hop_s) };
      }
      return { kind: 'scoop', trip: b.trip, k: b.k, load: r6(b.load), leave: r6(b.leave), land: r6(b.leave + b.fall) };
    });
  }
  return { list: beans, state, events };
}
