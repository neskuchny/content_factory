---
flow: f14-saas-ui
title: Video about an interface / service
inputs: [access to the service or a screencast/mockups; brief: which pain we solve]
complexity: ●●
cost: 0–4 i2v for AI scenes
---
## Steps
| # | Step | Details |
|---|---|---|
| 1 | beats | A pain from life (1 phrase) → one task solved in the interface → result and metric → CTA. As few screens as possible |
| 2 | Recording script | JSON: Playwright steps + a line of narration per step |
| 3 | Recording | Playwright `recordVideo` + a log of click coordinates. We draw the cursor ourselves (Playwright does not render it) |
| 4 | UI animation | Zoom and pan driven by the click log (deterministic), button highlight, a smoothed cursor, a 3D tilt of the screen. Limit the speed and scale of the zoom (otherwise it makes viewers dizzy) |
| 5 | Cutaways | AI scenes "a person solves a problem in life" (i2v) or stock (Pexels / Pixabay / Storyblocks, ID and license into the manifest) |
| 6 | overlay, subtitles, voice/music, audio_mix → render → review_video | |

## Rule
The interface text is real, taken from the recording. Do not generate screenshots.
