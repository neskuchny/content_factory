// grain.mjs: the paper grain. One 512x512 tile from seeded noise, luminance +-2 %, static (never changes between frames).
import { hash2, pnoise } from './rng.mjs';

export function makeGrainTile(seed) {
  const N = 512;
  const c = document.createElement('canvas'); c.width = N; c.height = N;
  const x = c.getContext('2d');
  const img = x.createImageData(N, N);
  for (let j = 0; j < N; j++) {
    for (let i = 0; i < N; i++) {
      // fine per-pixel noise plus a soft fibre-like layer (periodic, so the tile has no seam)
      const f = pnoise(i / 4, j / 4, 128, seed ^ 0x51) * 0.45 + pnoise(i / 1.6, j / 9, 320, seed ^ 0x77) * 0.25 + hash2(i, j, seed) * 0.30;
      const v = (f - 0.5) * 2;               // -1..1
      const a = Math.min(1, Math.abs(v) * 1.5) * 0.04; // +-2 % of full range on average
      const k = (j * N + i) * 4;
      if (v < 0) { img.data[k] = 43; img.data[k + 1] = 29; img.data[k + 2] = 20; }       // espresso
      else { img.data[k] = 255; img.data[k + 1] = 250; img.data[k + 2] = 240; }          // light paper
      img.data[k + 3] = Math.round(a * 255);
    }
  }
  x.putImageData(img, 0, 0);
  return c;
}

export function paintGrain(ctx, tile, S) {
  ctx.save();
  ctx.setTransform(S, 0, 0, S, 0, 0);
  ctx.fillStyle = ctx.createPattern(tile, 'repeat');
  ctx.fillRect(0, 0, 1080, 1920);
  ctx.restore();
}
