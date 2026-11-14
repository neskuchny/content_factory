---
id: REQ-20270118-1
client: demo
flow: f18-code-film            # standard flow; two stops with the owner: stills (step 8) and draft with sound (step 11)
brief: ./brief.md
decisions: ./decisions.md
beats: ./beats.md
shotlist: ./shotlist.json      # source of truth for timing, layout, texts and sound events
card: ./card.md                # director card (studio reads it; does not copy it)
skeleton: []                   # text-only request: no source files to index (f00 → no-shoot format → f18)
engine: code_film              # config/engines.yaml → engine code
budget_credits: 0              # no generation, no voice, no stock (decisions 2027-01-18)
production_dir: clients/demo/requests/REQ-20270118-1/production/
outputs:
  video: final/REQ-20270118-1.mp4        # 1080×1920, 30 fps, 18.0 s (540 frames), H.264 yuv420p, AAC 48 kHz, −14 LUFS
  publish: publish/REQ-20270118-1.mp4    # export.py --preset reels --max-mb 40
  cover: final/cover.png                 # dial close-up at 12.70 + "Day 5 to 28" (code)
  manifest: final/manifest.json
  costs: costs.md                        # one line: 0 credits
  log: log.md
---
# Harness REQ-20270118-1 "Freshness dial": code film (f18), 2D flat paper-cut, limit 0 credits (FICTIONAL demo)

## Why this flow
- Input mode: **text only**. `media-index/` has A-0002 (stamping clip), but the owner asked for no footage
  (`brief.md`). f00 points to a no-shoot format. The topic is a timeline with numbers, and an infographic (f10) would
  explain it, but the owner wants a small story with sound and 0 credits. That is **f18** with a 2D Canvas.
- Simple before flashy: one static set, one scene, no cuts, no 3D. It is the first code film for this client, so step
  10 starts with a 5-second pilot (0.0–5.1).

## Technical decisions
| Decision | What | Why |
|---|---|---|
| Engine | Canvas 2D, plain ES modules, no libraries | flat paper with a static camera does not need three.js or WebGL |
| Browser | Playwright + Chromium headless; flags `--disable-gpu --disable-accelerated-2d-canvas --force-color-profile=srgb --hide-scrollbars`; viewport = frame size, DPR 1 | software raster: the same frame gives the same bytes on the same machine |
| Network | the page is served from a fake origin by `page.route`; **every other request is aborted and logged** to `.cache/REQ-20270118-1/net.log` | rendering does not depend on the network; one external request fails the step |
| Frame contract | `window.READY` → `{frames, fps, width, height}` after `document.fonts.ready`; `window.__seek(t)` draws frame t synchronously; `window.__drawn` = text strings on the frame; `window.__boxes()` = named screen rects (titles, labels, needle, knob, band, bag, label, pad, roaster, tray, bin, scoop); `window.__state()` = `{day, knob_deg, band_lit, drum_rev}` | a frame is a pure function of (t, seed, timeline); a script checks texts, safe zones and mechanics without eyes |
| Determinism | seed 20270118 in the URL; mulberry32; **forbidden:** `Math.random`, `Date`, `performance.now`, state carried between frames | checked in step 7 |
| Text | titles and labels by code only, with the local Fraunces 600 and Inter 700 (OFL) | CLAUDE.md §5.3 |
| Sound | `project/sound.py` (numpy, seed 20270118); events are computed from `timeline.json` (one detent click per day crossed) | every sound belongs to a visible event; Openverse is not needed |
| Assembly | PNG frames → `sequence.py` → `audio.py --replace` → `loudness.py -I -14 --tp -1` → `export.py --preset reels --max-mb 40` → `check.py --platform reels --content` (`.claude/skills/ffmpeg-skill/scripts/`) | ffmpeg-skill tools, not raw ffmpeg |

**Time estimate (director, not measured):** flat shapes and two shadow depths come to about 0.1–0.3 s per frame at
1080×1920 with PNG capture. That makes about 1–3 min for 540 frames and seconds for the half-size draft. Gate in step 7:
≤ 1.0 s per frame at full size on 10.20 (the heaviest frame: stamp, beans, all props). If it is slower, first cache the
static set (backdrop, shelf, radio body) as one bitmap, with a byte-for-byte check against the uncached frame.

## Notes for studio and reviewer
- **Texts do not change.** Titles, labels and the end card come from `shotlist.json → texts_exact`,
  `scene_labels_exact` and `cta`, character for character. If a line does not fit, change the size (titles not below
  60 px) or the line break, never the words.
- **Copper only on the lit band and the keyword** (`card.md` §3). The needle, roaster and bag are never copper.
- **The mechanics are part of acceptance** (`card.md` §8). On every frame `knob_deg = 12 × day`, and `band_lit` is true
  exactly when 5 < day ≤ 28. Do not change who moves what without asking director.
- 0 credits: Higgsfield is never called. A step that would need credits is a stop and a question via the orchestrator.
  No "AI visualization" badge (nothing is generated). The logo layer is off (no SVG in the demo).
- No people, no hands, no calendar date, no bag label design, no real roaster look.
- Paths are relative to `production/`. Statuses: `todo → doing → done | fail(n) | skipped | blocked`. Studio keeps
  step statuses in `log.md` (a table with the same `#`); `harness.md` changes only through director. After `fail(3)` on
  any step: stop and ask a human via the orchestrator.
- Temporary files go to `.cache/REQ-20270118-1/`. In Bash, use absolute paths only (CLAUDE.md §9).

## `production/` layout
```
production/
  data/texts.json, data/timeline.json
  scene/index.html, scene/*.mjs     # grain, cut, set, radio, beans, titles, main
  scene/fonts/                      # Fraunces 600, Inter 700 woff2 + OFL.txt
  project/render.cjs                # Playwright: --probe | --stills t,t | --frames --range a:b --w --h | --checks
  project/build_timeline.py         # shotlist.json → data/timeline.json + checks
  project/checks.py                 # texts, safe zones, mechanics, causes in frame
  project/sound.py                  # → audio/mix_raw.wav, audio/sfx_events.json
  audio/ stills/ draft/ frames/ (temporary) final/ publish/
  log.md costs.md review.md
```

## Steps
| # | Step (library / f18) | Input | Output | Check | Status |
|---|---|---|---|---|---|
| 0 | preflight | machine | `log.md` §0 | Node 20+, Playwright with Chromium, ffmpeg ≥ 6.1, Python 3.10+ with numpy; ≥ 2 GB free; `render.cjs --probe` on an empty page: canvas draws, 0 external requests | done |
| 1 | skeleton | `brief.md` | nothing to index | text-only request; `media-index/` checked, A-0002 not used (brief) | done |
| 2 | beats + dice (f18 §1) | brief, product base | `beats.md`, `shotlist.json` | 3 concepts, owner's choice in `decisions.md` (2027-01-19); hook acts from frame 0; one event at a time | done |
| 3 | card (f18 §2) | beats | `card.md` | every device has a reason from this story | done |
| 4 | texts + fact-check | `shotlist.json` | `data/texts.json` | every string = `texts_exact`, `scene_labels_exact`, `cta` character for character; `python3 scripts/qa/words_check.py --client demo data/texts.json` gives only the 4 expected hints ("best" ×2, "5 days", "28 days"; `beats.md` → Facts) | done |
| 5 | timeline | `shotlist.json` | `data/timeline.json` | 540 frames; beats join without gaps and sum to 18.0 s; each title on screen ≥ 0.6 + 0.25 s per word and ≥ 1.5 s; needle keys, events, text windows and sfx carried over | done |
| 6 | fonts + render harness | font files | `scene/fonts/`, `project/render.cjs` | md5 of the woff2 files in `log.md`; test line "When is your coffee at its best? 0 5 28 @example_brewline ROAST DATE" in both fonts → `stills/font_test.png`, no fallback glyphs | done |
| 7 | world: scene + checks (f18 §3) | `card.md`, timeline, texts | `scene/`, `project/checks.py` | **Determinism:** frame 270 twice → same md5; frames 400 → 100 and 100 in a fresh browser → same md5; a grep over `scene/` for `Math.random`, `Date(` and `performance.now` finds 0. **Network:** 0 external requests. **Texts:** `__drawn` = `texts.json` where a line is fully shown. **Safe zones:** every text box inside x 60–940, y 250–1520 on every frame. **Mechanics** (every frame): abs(knob_deg − 12·day) ≤ 0.5°; `band_lit` ⇔ 5 < day ≤ 28; the needle never passes 5 during 5.78–11.6. **Causes** (`card.md` §8): beans only on chute/tray/bin/scoop paths; imprint absent before frame 306 and present from it, with the pad box touching the label box on frame 306. **Overlap:** no object box overlaps a title box. No placeholder shapes | done |
| 8 | stills = review_still → owner (f18 §4), **STOP 1** | scene | `stills/S_<t>.png` at `shotlist.json → stills_t` (11), `stills/thumbs/*_390.png`, `stills/sheet.jpg` (time + "cause → event" under each still) | **reviewer:** set and dial readable at 390 px; one leading event per still; cause in the same frame; copper only on band and keyword; texts exact and inside safe zones; frame 0.00 not empty or flat; reads as cut paper, not vector icons. Then the **owner**: orchestrator sends one message with `sheet.jpg`, thumbs 0.50, 10.20, 17.00 and 3 questions (below). Status `blocked: awaiting the owner` until a dated "yes" row is in `decisions.md` | done |
| 9 | audio_mix (f18 §6, skill `sound-design`) | timeline, `card.md` §7 | `audio/sound-audit.md` (event → sound → layers), `audio/mix_raw.wav` (48 kHz stereo, exactly 18.000 s), `audio/sfx_events.json`, `audio/sources.md` ("all code, seed 20270118") | every event in the beats has a sound; clicks = integer days crossed (31 + 5 + 23 + 14); the warm tone is on the same frames as `band_lit` (±1); peak on the event frame; loudest in order: 10.20, 1.40, 3.00; no music, no whooshes; the tail is not digital zero | done |
| 10 | half-size draft (f18 §5) | scene, timeline, mix | `draft/pilot_0-5.mp4` (0.0–5.1) first, then `draft/draft_v1.mp4` 540×960 with sound, `draft/draft_v1_sheet.png` | pilot: the reviewer checks motion (sweep, settle, pour) before the full draft; `look.py --tiles 4x3`; strips with `look.py --at` at 12 fps for 0.0–1.8, 2.8–4.0, 5.2–8.0, 8.6–10.8, 11.5–15.0; no jerks; grain and cut edges do not flicker; a "mute" viewer can say what the film is about in one sentence | done |
| 11 | draft → owner, **STOP 2** | `draft/draft_v1.mp4` | answer in `decisions.md` | orchestrator sends the draft in one message, 1 question: "Pace and sound OK? Shall we render the final?" Status `blocked: awaiting the owner` until a dated "yes" row | done |
| 12 | render (f18 §7) | scene, timeline, mix | `frames/*.png` → `final/picture.mp4` → `final/REQ-20270118-1.mp4` → `publish/REQ-20270118-1.mp4` | `render.cjs --frames --range 0:539 --w 1080 --h 1920` → `sequence.py --dir frames --pattern "%05d.png" --start-number 0 --fps 30` (540 frames counted, then PNGs deleted) → `audio.py picture.mp4 --replace audio/mix_raw.wav` → `loudness.py -I -14 --tp -1` → `export.py --preset reels --max-mb 40` | done |
| 13 | cover + manifest | final | `final/cover.png`, `final/manifest.json` | cover = `shotlist.json → cover` (code-set title "Day 5 to 28"). Manifest (skill `style-memory`): flow, seed, versions (Playwright, Chromium, ffmpeg), font md5 and licences, `audio.source: code`, `generations: []`, `credits: 0`, `label_ai: false`, `voice: null`, `music: null`, `logo.enabled: false` | done |
| 14 | review_video + jury (f18 §8) | publish file | `review.md` | `check.py publish/REQ-20270118-1.mp4 --platform reels --content` all PASS (a WARN is explained); `look.py --safe reels --tiles 3x2`: no text under the Reels interface; −14 LUFS ±1, peak ≤ −1 dBTP; first frame not flat; "cause in frame" repeated on video (±10 frames around 1.40, 3.00, 10.20, 11.60). Then skill `jury`: 6 answers with timecodes, score 5–9, ≤ 3 fixes. `review.md` = PASS | done |
| 15 | adaptation: Telegram (adapter) | final, caption in `beats.md` | `adaptations/telegram_channel.md` + `look.py --at 12.7` picture | one picture (band lit + T5) and a short text; **no new facts** relative to the hub (`channels.yaml` → telegram format_notes) | done |
| 16 | approval pack (orchestrator) | final, cover, adaptation | a unit in the approval pack; the reply in `decisions.md` | one line to answer: "Take it / Redo: …"; `Facts: ✔`, `AI: no`. Publishing stays manual: after "Take it" the publisher prepares a kit (skill `publish-kit`) and a line in `analytics/registry.jsonl` | done |

## Questions to the human (step 8, one message)
1. A radio dial in days after roast, with the copper band from 5 to 28: OK?
2. The roaster is a simple pictogram, not our real machine. Is that fine?
3. Texts OK? (six titles, `beats.md` → Texts)

## Budget
| Step | What | Expected, credits | Limit, credits |
|---|---|---|---|
| all | image, video, voice, music or sound generation | 0 | 0 |
| | **Total** | **0** | **0** |
Owner time: stills + 3 questions (step 8), draft + 1 question (step 11), the final in the approval pack (step 16).
Machine time for the whole run with 2 iterations of stills: about 30 min.

## If something goes wrong
| Situation | Action |
|---|---|
| The paper looks like "vector icons with drop shadows" 3 times on the stills | stop; ask the owner: keep it flat (no cut-edge noise, one shadow depth) or stop (`shotlist.json → fallback`) |
| The owner rejects the dial metaphor | stop; question to director. Another concept is a new card and shotlist, not an edit by studio |
| The owner rejects the roaster pictogram | replace it with a closed drum seen from the front (disc and door only); the timing does not change |
| A title does not fit in 2 lines at 68 px | smaller size (not below 60 px) or a different break; the words stay |
| The needle crosses 5 during the hops, so the band flickers | fix the interpolation (PCHIP, hold keys); never move the band |
| A frame takes > 1.0 s after caching the static set | render the final in the background with a status file; do not remove the grain or the cut edges |
| `check.py` warns about the first frame | frame 0 already shows the whole set and the moving needle; raise the contrast of the shelf and the radio, keep the motion |
