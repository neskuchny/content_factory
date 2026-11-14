# Production log: REQ-20270118-1 "Freshness dial" (f18, 2D code film) (FICTIONAL demo)

_studio. Statuses of the `harness.md` steps with the same `#`. 0 credits; Higgsfield was never called._

| # | Step | Status | Result |
|---|---|---|---|
| 0 | preflight | done | section 0 |
| 1 | skeleton | done | text-only, nothing to index |
| 2 | beats + dice | done | director |
| 3 | card | done | director |
| 4 | texts + fact-check | done | `data/texts.json` equals the shotlist; `words_check.py --client demo` gives exactly the 4 expected hints (T1 "best", T3 "5 days", T5 "Best", "28 days") |
| 5 | timeline | done | `data/timeline.json`: 540 frames, beats join without gaps to 18.0 s, every title on screen at least its reading time, 73 clicks = 31 + 5 + 23 + 14, lit intervals 0.20-0.95 and 11.60-18.00 |
| 6 | fonts + render harness | done | section 1 |
| 7 | world: scene + checks | done | section 2, `data/checks_report.json` (22 checks, all PASS) |
| 8 | stills, STOP 1 | done | section 3; owner "Take it" 2027-01-20 in `decisions.md` |
| 9 | audio_mix | done | `audio/sound-audit.md`, `sfx_events.json`, `sound_measure.json`, `sources.md` |
| 10 | half-size draft | done | section 4 |
| 11 | draft, STOP 2 | done | owner "Take it" 2027-01-21 in `decisions.md` |
| 12 | render | done | section 5 |
| 13 | cover + manifest | done | `final/cover.jpg`, `final/manifest.json` |
| 14 | review_video + jury | todo | reviewer |
| 15 | adaptation: Telegram | todo | adapter |
| 16 | approval pack | todo | orchestrator |

## 0. Preflight
Node 22.22.0, Playwright 1.63.0 + Chromium 153.0.8010.12, ffmpeg 6.1.1, Python 3.13.17 with numpy 2.5.3 and scipy 1.18.1,
8.7 GB free (shared with other jobs). `render.cjs --probe`: canvas draws, shadows and `letterSpacing` work, 0 external requests.

## 1. Fonts and harness
Local files only; the page never loads from the network (every non-`film.local` request is aborted; `net.log` total: 0 blocked).
Fraunces and Inter come from the npm packages `@fontsource/fraunces` and `@fontsource/inter` (no network during render; the packages were
downloaded once). Both are SIL OFL 1.1, so the two small latin woff2 files are kept in `scene/fonts/` with their licences next to them.
Fraunces 600 `b8dca52ca5f9e27747e5db1cf8820465`, Inter 700 `8ca0a51552960933d0fd52c19175cbe9`.
`stills/font_test.jpg`: the test line in both fonts, `missing_glyphs: []`, no fallback. No Literata substitution was needed.

## 2. World and checks (step 7)
- Determinism: frame 270 twice, same md5; frame 100 after frame 400 equals frame 100 in a fresh browser; 60 frames (every 9th) rendered forward and
  then in reverse in one page: 0 differences (`render.cjs --verify`, at 1080x1920 and at 540x960). `grep` over `scene/` for `Math.random`, `Date(`, `performance.now`: 0.
  An early bug (bin lid outline cached with its first position) was caught by this test and fixed: a cached cut edge never changes shape,
  moving parts are moved with a transform.
- Network: 0 external requests in every run.
- `project/checks.py` over all 540 frames: texts equal `texts.json`, one title at a time, safe zone x 60-940 / y 250-1520 for every text box,
  knob = 12 x day (0.5 deg tolerance, and per-frame ratio), `band_lit` iff 5 < day <= 28 (and equal to the Python PCHIP), the needle never passes 5 during
  5.78-11.6 (max day 5.000000), beans only on the door/chute/tray/bin-corridor/scoop/bag-mouth paths with the door open, the lid up and the tray tipped when they
  should be, imprint absent before frame 306 and present from it, pad box touches the label box on frame 306 and on no earlier frame, no object box
  overlaps a title box, frame 0 already has the needle moving (31 -> 30.59 -> 30.16).
- Speed: 0.10-0.17 s per frame at 1080x1920 including PNG capture on the heaviest frames (10.20, 5.50, 3.90), well under the 1.0 s gate: no caching of the static set was needed.
- No placeholder shapes: every object is a drawn paper part.

### Changes against `shotlist.json` / `card.md` (starting values; meaning and causes unchanged)
- Chimney, hopper rim, gauge, bin ribs, lid handle, lever stand and hinge added as details. Chute drawn as a channel (dark walls, light floor) so dark beans read.
- Bean length 12-16 px (spec 8-12) so the beans are visible at 390 px. All 40 beans slide off the tray (spec 25), so the tray is empty after the tip.
- Tray tip: beans hop in an arc into the gap under the lifted lid (the bin mouth is higher than the tray, so they cannot slide). Tray up 5.30-5.45, down 5.62-5.80.
- Bean departure 5.34-5.46, slide 0.10 s, hop 0.22 s, so the last bean is in the bin at 5.78, before the lid closes at 5.85.
- Scoop timings fitted into 8.60-9.66: dips at 8.74 and 9.22, pours 8.92-9.04 and 9.40-9.52 (spec 8.8-9.0 and 9.4-9.55). Scoop drawn 1.2x and a darker tint (cream_dark mixed 55 % with esp_light) so it separates from the cream backdrop; parked at x 748.
- Stamp lever: arm length 180 px, rest angle -35 deg, impact 38.9 deg, so the pad (100 x 22) lands on the top edge of the label (box overlap 6 px at frame 306). The pad does not cover the imprint.
- Imprint "ROAST DATE" is set in two lines (ROAST / DATE) at 22 px because one line (about 140 px) is wider than the 110 px label; the three bars sit side by side under it. The words are unchanged.
- Door flips in 0.08 s (open 2.90, close 4.40), so it is open before the first bean at 3.00.
- Titles balanced over two lines without splitting the copper keyword; the exit fade uses the brand curve mirrored so the line stays readable until the last 0.1 s.
- CTA slide-outs use a distance per object (roaster -520, tray -640, bin -800 with the scoop, lever +340 px) so nothing is left at the screen edge at 17.00.
- Lid colour: cream_dark mixed 30 % with esp_light for contrast. Paper edge: light top-left cut edge (a lighter sheet under the colour sheet, no strokes, no gradients).

## 3. Stills (step 8)
11 stills at `stills_t` rendered at full size; full-size PNGs are not kept in the repo. `stills/sheet.jpg` (257 KB, time + cause -> event under each), thumbs 0.50 / 10.20 / 17.00 as 390 px JPG.
Studio self-check before the owner: set and dial readable at 390 px; one leading event per still; the cause in the same frame; copper only on the band and the keyword;
texts exact and inside the safe zones; frame 0.00 shows the whole set and the needle at day 31, not flat; reads as cut paper (wobbling edges, two shadow depths, grain), no
"vector icons" retry needed. The unlit band (cream_dark on the cream dial) is faint by design.

## 4. Draft (step 10)
Pilot `pilot_0-5.mp4` (0.0-5.1 s, 153 frames, picture only) first, then `draft_v1.mp4` 540x960 with sound, -14.0 LUFS, -1.1 dBTP. `draft/draft_v1_sheet.jpg`: `look.py --tiles 4x3`.
Strips at 12 fps (`project/strips.py`) for 0.0-1.8, 2.8-4.0, 5.2-8.0, 8.6-10.8, 11.5-15.0: no jerks; the scoop trips (3-4 frame moves) read as snappy, not as jumps.
The grain and the cut edges are static by construction (not a function of the frame number).

## 5. Final render (step 12)
`render.cjs --frames --range 0:539 --w 1080 --h 1920 --workers 2` (37 s), `sequence.py` (540 frames counted, then the PNGs were deleted), `audio.py --replace`,
`loudness.py -I -14 --tp -1` (-14.0 LUFS, -1.1 dBTP), `export.py --preset reels --max-mb 40` (6.4 MB). `check.py --platform reels --content`: 19 checks, 0 failed,
1 WARN (no subtitle track: the film has no speech and its words are burned in by code). Also made: a 720x1280 proxy (0.7 MB) and a 720 px poster (the cover).

## Where the big files are (not in the repo)
Videos, frame caches, the full-size stills and `mix_raw.wav` live under the scratch folder
`/tmp/claude-0/-home-user/6dfa4614-e576-52e2-b3cd-720823eab608/scratchpad/showcase/` (`en_videos/demo/`, `cache/REQ-20270118-1/`), outside the repo tree. In a real run `FILM_CACHE`
defaults to `<repo>/.cache/REQ-20270118-1/` (git-ignored). Other deviations from the layout in `harness.md`: `draft_v1_sheet`, `cover` and the font test are JPG, not PNG;
the draft and final mp4 are not kept in `draft/`, `final/`, `publish/`; the harness thumbs are `*_390.jpg`.
