# f18 — Code film

A video where **every frame is drawn by code**: a three.js 3D scene (light, materials, camera) or
2D (paper cut-out, ink, a clay shader, motion design), rendered frame by frame in headless Chromium
and assembled by ffmpeg. **0 generation credits.** Ideas and rules are based on sarpstar/cinecode
(MIT): a hook with action from the first frame, one action per beat, "half the size is not half the
detail", frames are pure functions of time, sound from the first version, stills before rendering.

**Use it for:** explaining a principle (sun and shade on a site, how ventilation works, the seasons),
a stylized "product" fly-around, infographics with depth, storytelling without people, serial formats.
**Do not use it for:** realistic people/animals (code draws them badly → a stylized cast, or show
them through objects); an exact copy of the client's product without dimensions and joints from
product-base (then only a conventional "generic structure", labeled as such).

## Steps
| # | Step | Output | Check |
|---|---|---|---|
| 1 | `beats` + dice (`idea-dice`) | logline, 3 concepts, the human's choice | not "a film for any company" |
| 2 | Director card | `card.md`: language (3D/2D/material), light, palette (no "default AI palette"), typeface, camera per beat, sound | every device has a reason drawn from this story |
| 3 | The world in full detail | `scene/` (HTML + three.js/GSAP), deterministic seed | no "placeholder cubes" in the draft |
| 4 | Stills | 1 frame per beat → human/reviewer | `review_still` |
| 5 | Half-size draft | 540×960, 30 fps, frames as a function of time | the hook acts within 2 s |
| 6 | Sound | ambience, sounds for actions (code/Openverse CC0), voice from `brand/voices.md` | −14 LUFS (`ffmpeg-skill loudness.py`) |
| 7 | Render 1080×1920 | `final/*.mp4` + `publish` (`export.py --preset reels --max-mb 40`) | `check.py --platform reels --content` |
| 8 | QC + jury | `review.md` | `look.py --safe reels`, skill `jury` |

Render: Playwright/Chromium (already installed), `window.__seek(t)` in the scene → a frame screenshot → `ffmpeg -framerate 30`.
The engine is in `config/engines.yaml`: `code_film` → engine code.
