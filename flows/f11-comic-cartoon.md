---
flow: f11-comic-cartoon
title: Comic and cartoon
inputs: [brief, optionally real people or the product as references]
complexity: ●●
cost: 4–15 images; for a cartoon + i2v for each panel
---
## Formats
- **Page-turner (motion comic):** panels and screens flip, 2.5D parallax, speech bubbles in code.
- **Cartoon:** panels animated via i2v, voice-over by role.

## Steps
| # | Step | Details |
|---|---|---|
| 1 | Tone and style to fit the product | Premium and an adult audience: graphic novel, architectural sketch (line + watercolor), editorial illustration, ligne claire. **Not** a children's cartoon, Pixar-style 3D or anime if the product is expensive. Check against `brand/voice.md` |
| 2 | beats | Story spine or PAS: 4–8 panels, one idea per panel |
| 3 | Characters | The Higgsfield `character-sheet` workflow: a turnaround in 4 views + close-up and medium shot. The sheet is attached to every prompt. Real people — only with consent |
| 4 | Panels | Nano Banana Pro with the character sheet; either a whole page or panel by panel (with an empty zone for text). No more than 2 characters in a frame |
| 5 | review_still | Consistency of faces and clothing, the product as in product-base |
| 6a | Page-turner | Image Decompose or remove_background / Depth Anything → layers; HyperFrames/Remotion: a "camera" over the page, parallax, bubbles and sound-effect lettering in code, paper texture, grain |
| 6b | Cartoon | i2v per panel (Seedance / Kling + Elements), ElevenLabs voices for each character, lipsync if needed |
| 7 | audio_mix → render → review_video | |
