---
flow: f17-product-commercial
title: Product commercial
inputs: [product photos (ideally 2–3 angles), benefits from product-base, style: realism / cartoon / art]
complexity: ●●
cost: 3–8 images + 3–6 i2v
---
## Steps
| # | Step | Details |
|---|---|---|
| 1 | Concept | What we sell (1 main benefit + 2–3 supports), where the product "lives", the style. Quick variants — the Higgsfield workflows `product-photoshoot` / `ads-studio` / `ugc-video` |
| 2 | Packshot | remove_background + upscale. Missing angles — Nano Banana Pro "keep product, logo, lettering unchanged". Labels that wrap around the packaging need extra real photos |
| 3 | Scene frames | image_edit / product-photoshoot: the product in an environment. A style (cartoon or art) — image-to-image by style |
| 4 | review_still | Geometry, label, product color = reality |
| 5 | i2v | Seedance 2.x with @-roles for references (product / packaging / motion) or Kling Elements (up to 7 references). Shots: orbit "slow 180° orbit, product static centered"; macro 100 mm f/2.8 slide across the texture; splash — what moves and where, the product stays still |
| 6 | Final | **The final packshot and frames with a legible label are a real photo** with 2.5D animation in code, not a generation |
| 7 | overlay (benefits, price — facts, CTA), music, audio_mix → render → review_video (logo frame by frame) | |
| 8 | Variants | `ad-multiplier` for A/B versions of one ad |
