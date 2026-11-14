# Flow library

A flow is a step-by-step route for producing one kind of video. The `director` agent takes a
standard flow or **assembles a new one from the steps below** and writes it to
`weeks/<W>/04-production/<ID>/harness.md` (or `requests/<REQ>/harness.md`).
After that, studio and reviewer follow the steps strictly in order.

## harness.md format
```markdown
---
id: W44-R03
flow: f05-object-insert-inshot      # or custom
brief: ../../03-scripts/W44-R03.md
skeleton: [clients/<c>/media-index/assets/<asset>.md]
budget_credits: 400
---
| # | step (from the library) | input | output | check | status |
|---|---|---|---|---|---|
| 1 | extract_frame | asset A @ 00:12.40 | frames/A.png | exact frame, no blur | done |
| 2 | image_edit | frames/A.png + product-base/media/product-* | frames/B.png | review_still PASS | todo |
```
Statuses: `todo → doing → done | fail(n) | skipped`. After 3 `fail`s the step goes to a human.

## Step library
| Step | What it does | Tool |
|---|---|---|
| `skeleton` | Source skeleton (skill `source-skeleton`) | whisper/Scribe, PySceneDetect, ffmpeg, Claude vision |
| `beats` | Beat list and storyline (skill `hook-storyline`) | Claude |
| `shotlist` | Shot list JSON: shot size, angle, camera move, lens, light, action, gen_duration, edit_duration, source, prompt, fallback | Claude |
| `select` | Pick fragments from the skeleton according to the script | Claude over `packed.md` |
| `cut` | Cut by timecodes, on word boundaries, CFR, 1080×1920 | ffmpeg |
| `extract_frame` | Exact seam frame `ffmpeg -ss T -frames:v 1 -q:v 1` | ffmpeg |
| `image_gen` | Generate a frame from scratch from references | Higgsfield: Nano Banana Pro / GPT Image 2.5 / Seedream 5 |
| `image_edit` | Paint in or replace parts of a frame, keep the rest | Higgsfield: Nano Banana Pro / GPT Image 2.5 edit |
| `outpaint` | Extend the edges, change the aspect ratio | FLUX.2 Pro Outpaint |
| `review_still` | Check the still before video (geometry, light, shadows, A/B difference outside the object) | reviewer |
| `flf_video` | Video between frames A and B | Kling 3.0 Omni (Frames) / Kling 4.0 keyframes |
| `i2v` | Video from a frame or references | Seedance 2.0/2.5, Kling 3/4, Cinema Studio 3/4, Veo 3.1 |
| `video_edit` | Repaint a clip from text and a reference | Kling 3.0 Omni Edit / Kling 4.0 edit / Seedance 2.5 edit / FLUX 3 Video Edit |
| `video_extend` | Extend a clip | Seedance 2.5 / Cinema Studio 4.0 extension |
| `replace_object` | Replace an object in a video | Genjutsu replace object |
| `lipsync` | Match lips to audio | Sync Lipsync 3 |
| `voice` | Voice-over or voice clone | ElevenLabs via Higgsfield `generate_audio` / `create_voice` |
| `reverse` | Reverse a clip (B→A) to return to reality | ffmpeg `reverse` |
| `seam` | Real ↔ AI seam (skill `seamless-insert`) | ffmpeg / HyperFrames |
| `overlay` | Badges, callouts, PiP, before/after, logo layer | HyperFrames / Remotion |
| `subtitles` | Word-level subtitles in the brand style | HyperFrames / Remotion / ASS; `ffmpeg-skill caption.py --karaoke --platform reels` |
| `stock` | Stock cutaways (ID and license go into the manifest) | Pexels / Pixabay / Storyblocks |
| `stabilize` / `redact` | Stabilize a clip; blur a rectangle (people in reflections, license plates) | `ffmpeg-skill stabilize.py`, `redact.py`, `cropdetect.py --motion-centre` (centre for 9:16) |
| `cast` | A series character — only from the card `brand/cast/<name>.md` (references, voice, engine, price) | director |
| `grade` | Normalization, LUT, matching AI color to the real footage, grain | ffmpeg `lut3d`/`eq`/`noise`; Resolve MCP (optional) |
| `audio_mix` | Voice, music, SFX, whoosh, −14 LUFS (skill `sound-design`: client library → Openverse → Epidemic Sound → generation) | `ffmpeg-skill audio.py` (ducking) + `loudness.py` (−14 LUFS with verification), `scripts/media/openverse.py` |
| `label_ai` | "AI visualization" badge on AI-generated pieces | overlay |
| `render` | Final render + `manifest.json`; a version per platform | HyperFrames / Remotion / ffmpeg / Higgsedit; `ffmpeg-skill export.py --preset reels --max-mb 40`, `render.py project.json` (+ `--export-timeline fcpxml` for DaVinci) |
| `review_video` | Check the final: `check.py --platform --content` + `look.py --safe` + frame by frame; then the jury | reviewer (skills `ffmpeg-skill`, `jury`) |
| `golden` | Save a successful video to `brand/golden/` (skill `style-memory`) | feedback |

## Catalog
| Flow | Kind |
|---|---|
| [f00](f00-text-only.md) | Text only → router |
| [f01](f01-walkthrough-overlay.md) | Walkthrough with augmented visuals |
| [f02](f02-environment-swap.md) | Swapping the environment around a person |
| [f03](f03-footage-plus-images.md) | Video + supplied images |
| [f04](f04-object-insert-broll.md) | An object appears (B-roll insert) |
| [f05](f05-object-insert-inshot.md) | An object appears right in the shot and disappears |
| [f06](f06-interior-and-drone.md) | Interior after renovation + exterior fly-around |
| [f07](f07-long-to-short.md) | Long → short |
| [f08](f08-many-to-one.md) | Many → one |
| [f09](f09-restoration.md) | Restoration and inpainting |
| [f10](f10-infographic.md) | Infographic |
| [f11](f11-comic-cartoon.md) | Comic and cartoon |
| [f12](f12-talking-head.md) | Talking-head edit |
| [f13](f13-avatar.md) | Digital avatar |
| [f14](f14-saas-ui.md) | Video about an interface |
| [f15](f15-process-plus-visuals.md) | Process + extra visuals |
| [f16](f16-brand-film.md) | Brand film (premium) |
| [f17](f17-product-commercial.md) | Product commercial |
| [f18](f18-code-film.md) | Code film (three.js / 2D, 0 credits) |

## Rules for all flows
1. When source material exists, the first step is `skeleton` (if there is none yet).
2. Before every paid step, estimate the credits. The total goes to `costs.md`; the limit comes from `harness.md`.
3. Check stills before video (`review_still` before `flf_video` / `i2v` / `video_edit`).
4. Text, numbers, logos and labels are applied only in `overlay`.
5. Every AI-generated piece gets `label_ai`.
6. The final is `render` + `review_video` + `manifest.json`.
