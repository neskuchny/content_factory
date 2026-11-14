---
flow: f08-many-to-one
title: Many clips → one coherent video
inputs: [several short clips, for example from a phone]
complexity: ●
cost: no generations
---
## Steps
| # | Step | Details |
|---|---|---|
| 1 | skeleton | Each clip separately; VFR → CFR; loudness, sharpness, shake |
| 2 | beats | The logic of a route: arrival → facade → inside / workshop → details → result → CTA. Or hook → problem → demonstration → verdict → CTA |
| 3 | A-roll / B-roll | A-roll — the take with the best sound (speech). B-roll is picked from the scenes by tags. Among takes of one phrase, choose by picture and sound |
| 4 | gaps | If a beat has no shot → a shoot brief (`shoot-brief`) or an f04/f10 insert |
| 5 | cut → EDL | Cuts, transitions, word-level subtitles |
| 6 | grade | Different phones → normalize balance and contrast, then one shared LUT |
| 7 | audio_mix | `loudnorm`, noise suppression, music under the voice |
| 8 | render → review_video | |
