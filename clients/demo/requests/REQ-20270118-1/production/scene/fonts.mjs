// fonts.mjs: Fraunces 600 and Inter 700 (SIL OFL 1.1), local woff2 files only. System fonts are never used.
export const FONTS = [
  ['Fraunces', '600', 'fonts/fraunces-latin-600-normal.woff2'],
  ['Inter', '700', 'fonts/inter-latin-700-normal.woff2'],
];
export async function loadFonts() {
  await Promise.all(FONTS.map(async ([fam, weight, url]) => {
    const f = new FontFace(fam, `url(${new URL(url, location.href).href})`, { weight, style: 'normal' });
    await f.load(); document.fonts.add(f);
  }));
  await document.fonts.ready;
}
// Test line in both fonts; missing glyphs are found by comparing widths against two different fallback families.
export function fontTest() {
  const c = document.createElement('canvas'); c.width = 1400; c.height = 250; const x = c.getContext('2d');
  x.fillStyle = '#F6EFE6'; x.fillRect(0, 0, 1400, 250); x.fillStyle = '#2B1D14';
  const S = 'When is your coffee at its best? 0 5 28 @example_brewline ROAST DATE';
  const rows = [['600 33px Fraunces', 'Fraunces 600'], ['700 33px Inter', 'Inter 700']];
  rows.forEach(([f, n], i) => { x.font = f; x.fillText(S, 24, 80 + i * 110); x.font = '18px sans-serif'; x.fillText(n, 24, 108 + i * 110); });
  const miss = [];
  for (const fam of ['600 40px Fraunces', '700 40px Inter']) {
    for (const ch of new Set(S.replace(/ /g, ''))) {
      x.font = fam.replace(/Fraunces|Inter/, (m) => m + ', serif'); const w1 = x.measureText(ch).width;
      x.font = fam.replace(/Fraunces|Inter/, (m) => m + ', monospace'); const w2 = x.measureText(ch).width;
      if (Math.abs(w1 - w2) > 0.01) miss.push(fam + ':' + ch);
    }
  }
  const loaded = [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family + ' ' + f.weight);
  return { png: c.toDataURL('image/jpeg', 0.9), missing_glyphs: miss, loaded };
}
