// render.cjs: Playwright harness for "Freshness dial" (REQ-20270118-1). Canvas 2D, software raster, network closed.
// The page is served from the fake origin http://film.local/ by page.route. Every other request is aborted and logged
// to <cache>/net.log; one external request makes the run exit with code 3.
// Modes:  --probe | --fonttest | --stills --times a,b [--outdir D --prefix S_ --w --h --format png|jpeg]
//         --frames --range a:b [--w --h --workers N --outdir D --format png|jpeg] | --dump a:b [--out FILE]
//         --verify | --perf --times a,b | --status
// Frame cache (PNG frames, net.log, dumps) goes to $FILM_CACHE or, by default, <repo>/.cache/REQ-20270118-1/ (git-ignored).
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const PROD = path.resolve(__dirname, '..');
const CACHE = process.env.FILM_CACHE || path.resolve(PROD, '../../../../../.cache/REQ-20270118-1');
const ORIGIN = 'http://film.local/';
const NETLOG = path.join(CACHE, 'net.log');
const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.woff2': 'font/woff2' };
fs.mkdirSync(CACHE, { recursive: true });

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  if (i < 0) return def;
  const v = process.argv[i + 1];
  return v === undefined || v.startsWith('--') ? true : v;
}

async function launch(w, h) {
  const browser = await chromium.launch({ headless: true, args: ['--disable-gpu', '--disable-accelerated-2d-canvas', '--force-color-profile=srgb', '--hide-scrollbars'] });
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const net = { blocked: [], served: 0 };
  await page.route('**/*', async (route) => {
    const url = route.request().url();
    if (!url.startsWith(ORIGIN)) { net.blocked.push(url); return route.abort(); }
    const rel = decodeURIComponent(url.slice(ORIGIN.length).split('?')[0]);
    const f = path.join(PROD, rel);
    if (!f.startsWith(PROD) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) return route.fulfill({ status: 404, body: 'nf' });
    net.served++;
    return route.fulfill({ status: 200, contentType: MIME[path.extname(f)] || 'application/octet-stream', body: fs.readFileSync(f), headers: { 'cache-control': 'no-store' } });
  });
  page.on('console', (m) => { if (arg('verbose', false) || m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.type(), m.text()); });
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));
  return { browser, page, net };
}

const qs = (extra) => new URLSearchParams(Object.assign({ seed: '20270118' }, extra)).toString();
const md5 = (b) => crypto.createHash('md5').update(b).digest('hex');
async function dataToBuf(page, expr) { const b64 = await page.evaluate(expr); return Buffer.from(b64.split(',')[1], 'base64'); }
async function openScene(page, w, h) { await page.goto(ORIGIN + 'scene/index.html?' + qs({ w, h })); return page.evaluate('window.READY'); }

async function worker(w, h, format, frames, outdir, status) {
  const { browser, page, net } = await launch(w, h);
  try {
    await openScene(page, w, h);
    for (const f of frames) {
      await page.evaluate(`window.__seek(${f}/30)`);
      const buf = await dataToBuf(page, `window.__grab(${JSON.stringify(format)})`);
      fs.writeFileSync(path.join(outdir, String(f).padStart(5, '0') + (format === 'png' ? '.png' : '.jpg')), buf);
      status.done++;
      if (status.done % 20 === 0 || status.done === status.total) fs.writeFileSync(path.join(CACHE, 'render_status.json'), JSON.stringify({ done: status.done, total: status.total }));
    }
  } finally { await browser.close(); }
  return net.blocked;
}

async function main() {
  const w = +arg('w', 1080), h = +arg('h', 1920);
  if (arg('status', false)) { console.log(fs.readFileSync(path.join(CACHE, 'render_status.json'), 'utf8')); return; }
  const { browser, page, net } = await launch(w, h);
  const t0 = Date.now();
  let blockedExtra = [];
  try {
    if (arg('probe', false)) {
      await page.setContent('<canvas id=c width=64 height=64></canvas>');
      const info = await page.evaluate(() => {
        const c = document.getElementById('c'); const x = c.getContext('2d');
        x.fillStyle = '#123456'; x.fillRect(0, 0, 64, 64); x.shadowColor = 'rgba(0,0,0,0.5)'; x.shadowBlur = 6; x.shadowOffsetX = 4; x.fillStyle = '#ffeedd'; x.fillRect(4, 4, 20, 20);
        x.letterSpacing = '3px';
        const d = x.getImageData(10, 10, 1, 1).data, e = x.getImageData(40, 40, 1, 1).data, s = x.getImageData(26, 12, 1, 1).data;
        return { draws_px: [...d], bg_px: [...e], shadow_px: [...s], letterSpacing: x.letterSpacing, ua: navigator.userAgent };
      });
      console.log('PROBE', JSON.stringify(info), 'chromium', browser.version());
    } else {
      const ready = await openScene(page, w, h);
      console.log('READY', JSON.stringify(ready), 'in', ((Date.now() - t0) / 1000).toFixed(1), 's');
      const format = arg('format', 'png');
      const grab = () => dataToBuf(page, `window.__grab(${JSON.stringify(format)})`);
      if (arg('fonttest', false)) {
        const r = await page.evaluate('window.__fontTest()');
        fs.mkdirSync(path.join(PROD, 'stills'), { recursive: true });
        fs.writeFileSync(path.join(PROD, 'stills/font_test.jpg'), Buffer.from(r.png.split(',')[1], 'base64'));
        console.log('FONTTEST missing_glyphs:', JSON.stringify(r.missing_glyphs), 'loaded:', JSON.stringify(r.loaded));
      } else if (arg('stills', false)) {
        const times = String(arg('times')).split(',').map(Number);
        const outdir = path.resolve(PROD, arg('outdir', 'stills'));
        fs.mkdirSync(outdir, { recursive: true });
        const timing = [];
        for (const t of times) {
          const a = Date.now();
          await page.evaluate(`window.__seek(${t})`);
          const b = Date.now();
          const buf = await grab();
          const c = Date.now();
          fs.writeFileSync(path.join(outdir, arg('prefix', 'S_') + t.toFixed(2) + (format === 'png' ? '.png' : '.jpg')), buf);
          timing.push({ t, seek_s: +((b - a) / 1000).toFixed(3), grab_s: +((c - b) / 1000).toFixed(3), bytes: buf.length, md5: md5(buf) });
          console.log('still', t, 'seek', ((b - a) / 1000).toFixed(3), 'grab', ((c - b) / 1000).toFixed(3));
        }
        fs.writeFileSync(path.join(CACHE, 'timing_' + arg('prefix', 'S_') + w + '.json'), JSON.stringify(timing, null, 1));
      } else if (arg('perf', false)) {
        for (const t of String(arg('times')).split(',').map(Number)) {
          const ms = [];
          for (let i = 0; i < 3; i++) { const a = Date.now(); await page.evaluate(`window.__seek(${t})`); const b = Date.now(); await grab(); ms.push([b - a, Date.now() - b]); }
          console.log('perf', t, 'seek/grab ms', JSON.stringify(ms));
        }
      } else if (arg('cover', false)) {
        const b64 = await page.evaluate('window.__cover()');
        fs.mkdirSync(path.join(PROD, 'final'), { recursive: true });
        fs.writeFileSync(path.join(PROD, 'final/cover.jpg'), Buffer.from(b64.split(',')[1], 'base64'));
        console.log('COVER -> final/cover.jpg');
      } else if (arg('events', false)) {
        const res = await page.evaluate('window.__beanEvents()');
        fs.writeFileSync(path.join(PROD, 'data/bean_events.json'), JSON.stringify(res));
        console.log('EVENTS', res.length, 'beans -> data/bean_events.json');
      } else if (arg('dump', false)) {
        const [a, b] = String(arg('dump')).split(':').map(Number);
        const res = await page.evaluate(`window.__dump(${a},${b})`);
        const out = arg('out', path.join(CACHE, 'dump.json'));
        fs.writeFileSync(out, JSON.stringify(res));
        console.log('DUMP', res.length, 'frames ->', out);
      } else if (arg('verify', false)) {
        const hash = async (t) => { await page.evaluate(`window.__seek(${t})`); return md5(await grab()); };
        const res = {};
        res.k270_a = await hash(270 / 30);
        res.k270_b = await hash(270 / 30);
        res.k400 = await hash(400 / 30);
        res.k100_after_400 = await hash(100 / 30);
        const second = await launch(w, h);
        await openScene(second.page, w, h);
        await second.page.evaluate('window.__seek(100/30)');
        res.k100_fresh = md5(await dataToBuf(second.page, 'window.__grab("png")'));
        blockedExtra = second.net.blocked;
        await second.browser.close();
        // order independence: 60 frames (every 9th) forward, then the same frames in reverse in the same page
        const fr = []; for (let f = 0; f < 540; f += 9) fr.push(f);
        const fwd = {}; for (const f of fr) fwd[f] = await hash(f / 30);
        let diff = 0; for (const f of fr.slice().reverse()) if ((await hash(f / 30)) !== fwd[f]) diff++;
        res.order_test_frames = fr.length; res.order_test_diffs = diff;
        res.k270_equal = res.k270_a === res.k270_b;
        res.k100_equal = res.k100_after_400 === res.k100_fresh;
        console.log('VERIFY', JSON.stringify(res, null, 1));
        if (!(res.k270_equal && res.k100_equal && diff === 0)) process.exitCode = 4;
      } else if (arg('frames', false)) {
        const [a, b] = String(arg('range', '0:0')).split(':').map(Number);
        const outdir = path.resolve(arg('outdir', path.join(CACHE, 'frames')));
        fs.mkdirSync(outdir, { recursive: true });
        const nw = +arg('workers', 1);
        const all = []; for (let f = a; f <= b; f++) all.push(f);
        const status = { done: 0, total: all.length };
        const parts = Array.from({ length: nw }, (_, i) => all.filter((_, j) => j % nw === i));
        await page.close().catch(() => {});
        const res = await Promise.all(parts.map((p) => worker(w, h, format, p, outdir, status)));
        blockedExtra = res.flat();
        console.log('FRAMES', all.length, '->', outdir);
      }
    }
  } finally {
    const all = net.blocked.concat(blockedExtra);
    console.log('NET blocked:', all.length, all.slice(0, 5).join(' '), '| served', net.served, '| total', ((Date.now() - t0) / 1000).toFixed(1), 's');
    fs.appendFileSync(NETLOG, JSON.stringify({ at: 'run', argv: process.argv.slice(2).join(' '), blocked: all }) + '\n');
    await browser.close().catch(() => {});
    if (all.length) process.exitCode = 3;
  }
}
main().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
