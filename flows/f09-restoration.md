---
flow: f09-restoration
title: Restoration and inpainting
inputs: [raw video or photo: dark, shaky, with clutter, in the wrong format]
complexity: ●●
cost: from 0 (ffmpeg) to video_edit / Reframe / upscaling
---
## Steps (in order of rising price — stop as soon as it is good enough)
| # | Step | Tool |
|---|---|---|
| 1 | Stabilization **before any AI edits** | ffmpeg `vidstabdetect` → `vidstabtransform=smoothing=30,unsharp` |
| 2 | Light and color | ffmpeg `eq`, `curves`, `colorbalance`, `lut3d`; Resolve MCP if Studio is available |
| 3 | Noise and flicker | ffmpeg `hqdn3d`; Higgsfield Video Deflicker |
| 4 | Remove an object, clutter, people | Kling Omni Edit / Kling 4.0 edit ("remove …, keep everything else identical"), FLUX 3 Video Edit (≤15 s), Genjutsu replace. Long footage in segments |
| 5 | Format 16:9 → 9:16 | A talking head — crop on the face + blurred background (cheap); otherwise Higgsfield Reframe (≤60 s, 30 s at 1080p ≈ 365 credits). Photos — FLUX.2 Outpaint |
| 6 | Upscale | Higgsfield Video Upscale / Topaz |
| 7 | review_video | Before/after comparison, keep the original |

## Pitfalls
A generative model **makes things up**, it does not restore. For the client's real objects you
must not change the construction, brand and materials. Human review is mandatory.
