# External tools: cinecode, Mago Studio, ffmpeg-skill (review of 2026-11-07)

The README, SKILL.md, references and script list were cloned and read. No code was copied into the repository.

## 1. ffmpeg-skill (kajisho5) — MIT, Python stdlib + ffmpeg, MCP available
An agent skill that acts as the "editor's hands": 42 tools with a fixed probe → edit → check → verify cycle,
each answering in JSON, tested on ffmpeg 6.1–9 (we run 6.1.1). Installation: `npx ffmpeg-skill`.

What it covers of our pain points (things `studio` used to write by hand every time):
| Tool | What it does | Where it hurt for us |
|---|---|---|
| `check.py --platform reels --content` | PASS/WARN/FAIL against the platform spec + black/frozen frames, flashes, audio dropouts | QC counted this by hand on every one-off request |
| `look.py --safe reels` | contact sheet with the platform's UI zones shaded | safe zones were recalculated on every one-off request |
| `caption.py --karaoke --platform` | word-by-word subtitles, line breaks by meaning, inside the safe zone | subtitles were written from scratch in PIL/HTML |
| `loudness.py` | two-pass −14 LUFS with a check of the result | "loudnorm could not do it linearly" |
| `export.py --preset reels --max-mb` | platform presets, fitting to a size limit | 124 MB publish versions |
| `silence.py --speech-aware` | cutting pauses without eating breaths | future f12 (talking head) |
| `stabilize.py`, `cropdetect --motion-centre` | stabilization, motion centre for 9:16 | shaky footage and bad crops, stabilization |
| `redact.py` | blur/pixelate a rectangle across the whole clip | people in reflections |
| `render.py project.json` + `--export-timeline fcpxml/edl/otio` | assembling a video from a declaration; export to DaVinci/Premiere | every request had its own compose.py; the human had nothing to open in an editor |
| `report.py` | HTML delivery report: before/after, loudness, compliance | approval pack |

**Verdict: adopt.** Install it as a skill for `studio` and `reviewer`; `reviewer` gets an automatic first
pass (`check.py --content` + `look.py --safe`), `studio` gets the standard `caption/loudness/export/render`.

## 2. cinecode (sarpstar) — MIT, "films written in code" (three.js + headless Chrome + ffmpeg)
A complete single-author pipeline: script → director card → stills → draft → sound → MP4.
We do not install it whole: it has its own process, defaults to Turkish, and its rule
"generate only on request" contradicts our flow. We take the techniques:
1. **"Jury" (`references/jury.md`)** — 6 questions about a draft in 2–3 minutes: a hook within 2 s, the "hero moment",
   a shot that would fit any film, the weakest 5 seconds, sound on the three main cuts, text
   that sounds generated; a score of 5–9 and at most 3 fixes. Our `reviewer` checks the craft, not
   "is it interesting" — add this as a second pass.
2. **"Dice" (`dice.py`, `sparks.json`)** — crosses an idea with a random real thing (a museum exhibit,
   an animal, an invention) so concepts are not the first obvious ones. For `producer` in the sighting round.
3. **Steering** — say up front what comes out expensive or bad (realistic people in code, "nobody moves",
   stretched length). This matches the lessons we learned on past one-off requests — record it in hook-storyline.
4. **`words_check.py`** — catches "generated-sounding" phrasing ("X, not Y" constructions, stock phrases, dashes) —
   build a per-language stoplist (for `ru` clients: a Russian stoplist, kept in `config/locales/ru.yaml`).
5. **3D product in code (three.js)** — a studio fly-around/disassembly of a product with no generation credits. For
   a physical product: "exploded view", fly-around, season change — but real dimensions and parts must be in the product base.
6. **`beat_grid.py`** — cuts on music beats; **`formats.py save`** — save a video format as
   a series template (we need this for recurring series).
7. **Licenses on download** — a line in `LICENSES.csv` for every external file (we have sound
   passports — extend them to everything).

## 3. Mago Studio — AGPL-3.0, desktop (Electron/Next.js) + ComfyUI on your own GPU or paid Mago Cloud
Director (script → cast → shot list → storyboard → scenes where each shot continues the previous one) and
Transform (redrawing video by frame ranges and masks, relight, character replacement).
**It does not fit into our cloud factory:** it needs a GPU and a desktop, the cloud is paid; AGPL — do not copy the code.
It makes sense as a manual tool for a human on their own computer with a GPU. We take the ideas:
- **a cast library, "create once — use everywhere"** — for us this is brand/voices.md + characters in folders;
  consolidate into `brand/cast/` (face, sheet, voice, rules) for series;
- **shot continuity** — the next shot starts from the last frame of the previous one (we have FLF);
- **per-frame versions and review** — we have review.md and git, no UI.

## 4. treg (superdesigndev) — Apache-2.0 with extra terms, hosted gateway "OpenRouter for agent tools"
One token and one prepaid dollar balance for many video, image and voice models plus social-data, web
and enrichment tools; MCP (`https://treg.to/mcp/v2/`), CLI and an HTTP proxy; the owner's own provider
keys take priority and are not metered. **Adopted as a second paid engine** next to Higgsfield
(`config/engines.yaml: treg`, skill `treg-gateway`): useful when a model is not on Higgsfield or is
cheaper there. Not adopted: the `curl | sh` installer, `treg scan/upload` (registers local keys with a
team server), its "call without asking" and "star the repo" defaults, people/company enrichment.
Spending follows our rules: estimate first, `spending.treg_usd_week`, studio only, cost into
`manifest.json → usd_direct` (counted by `scripts/analytics/costs.py`).

## Adoption plan (proposal)
| # | What | Cost | Effect |
|---|---|---|---|
| 1 | Install ffmpeg-skill, connect it to `studio`/`reviewer`, rewrite the flow steps `subtitles/audio_mix/render/review_video` on top of it | 0 credits, ~1 h | less manual code and recalculation, one platform check |
| 2 | "Jury" as a second `reviewer` pass + a per-language `words_check` | 0 credits | a "is it interesting" score, not only "no defects" |
| 3 | "Dice" in `producer` for the sighting round | 0 credits | variety of concepts |
| 4 | `brand/cast/` — character cards for a series (e.g. a professor, a foreman) | 0 credits | repeatable series |
| 5 | Pilot of a 3D product in code (three.js) | 0 credits | a free "product fly-around"; needs the product's dimensions from the client |
