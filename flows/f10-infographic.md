---
flow: f10-infographic
title: Infographic
inputs: [text or data; optionally the client's materials]
complexity: ●
cost: 0–3 images (backgrounds, icons)
---
## Three modes
| Mode | What | How |
|---|---|---|
| **Drawn** | Everything in code: numbers, charts, icons, kinetic typography | HyperFrames / Remotion with brand tokens |
| **On materials** | Graphics around the client's photo or screenshot: arrows, callouts, numbers | The photo as a layer + overlay |
| **From materials** | The client's materials are the basis of the frames, graphics tie them together | Prepare the materials (remove_background, stylize with image_edit to the style) + overlay |

## Steps
| # | Step | Details |
|---|---|---|
| 1 | Structure | One main takeaway + 3–5 supports. Every number comes from product-base (`fact-check`) |
| 2 | Style | `brand/tokens.json`, components, the series' golden template (skill `style-memory`) |
| 3 | Materials | Missing backgrounds or icons → image_gen in the brand style. Quality photos from the client take priority |
| 4 | Assembly | JSON scene manifest → components → preview |
| 5 | Self-check | Frames every 2 s: line wraps, cropping, legibility, overlaps |
| 6 | render (9:16 video or a 1080×1350 PNG carousel) → review | |

## Rule
Numbers and text only in code. An image model distorts them.
