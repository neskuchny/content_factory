---
flow: f16-brand-film
title: Brand film (premium, ~60 s, "as if shot by a studio")
inputs: [brief, brand, optionally real footage and the product]
complexity: ●●●
cost: high — 20–30 final shots × 3–5 generations; the budget is agreed separately
---
## Steps
| # | Step | Details |
|---|---|---|
| 1 | Treatment | Idea, tone, references, palette, a **through visual anchor** (an object, a color, a device), music. Agree it with a human |
| 2 | beats | Story spine: hook 0–3 s, setup up to 10 s, development up to 45 s, climax and product up to 55 s, CTA |
| 3 | shotlist.json | For each shot: shot size, angle, camera move, lens (body, focal length, aperture), light, action, `gen_duration` 5–10 s, `edit_duration` 1.5–3 s, source (gen / real footage / code), prompt, **fallback**. Mark the shots AI is weak at (hands, text, crowds, liquids) and replace them with an angle, a silhouette or real footage |
| 4 | Anchor block | The prompt text shared by a scene (light, location, grade) is repeated verbatim in all of its shots |
| 5 | Key frames | First **all** the static storyboard frames (Nano Banana Pro + character-sheet / product references). Get the storyboard approved |
| 6 | i2v | Seedance 2.x — narrative and continuity; Kling 3/4 — precise shot control and Elements; Cinema Studio 4.0 — camera, lens, genre; Veo 3.1 — realism. 3–5 generations per shot |
| 7 | Edit | Straight cuts and match cuts on shape and motion; transitions via start/end frames; no morphing |
| 8 | Post | Selection → upscale → normalization → LUT at 60–80 % → soften the "AI sharpness" → shared grain. Resolve MCP if Studio is available, otherwise ffmpeg |
| 9 | Sound | Room tone, foley, SFX layers, music, cutting to the beat. Replace the generator's native sound. Avoid lipsync where possible |
| 10 | overlay | Logo, text, the final packshot — in code or a real photo |
| 11 | review_video | "Can you tell it is AI?" — a list of the frames that give it away, and replace them |

## Benchmarks
A professional's 30-second video takes 2 days. For 60 s, allow 3–7 days and a separate credit budget [UNVERIFIED].
