---
flow: f07-long-to-short
title: Long → short (Reels/Shorts from a big video)
inputs: [a long video: a conference, an episode, a big review]
complexity: ●
cost: no generations
---
## Steps
| # | Step | Details |
|---|---|---|
| 1 | skeleton | Mandatory for the whole video: word-level transcript, speakers, scenes, strong moments. The skeleton is reused for all cuts |
| 2 | candidates | 8–12 pieces of 20–60 s on phrase boundaries (skill `hook-storyline`) |
| 3 | scoring | 5 axes, 1–5 each: hook strength, completeness of the thought, emotion, density of value, payoff. Plus fit to the audience's pain from the passport. Optionally Higgsfield `virality_predictor` |
| 4 | selection | The top 3 go to the approval pack. The human chooses or asks for others |
| 5 | cold hook | Move the strongest phrase into the first 1–2 s (it can be taken from another point in the video) |
| 6 | cut | On word and silence boundaries, no broken phrases |
| 7 | reframe | 9:16 crop on the face (cheap) or Higgsfield Reframe (expensive, when the whole field of view matters) |
| 8 | subtitles, overlay (name, thesis), audio_mix → render → review_video | |

## Tool
The ready-made skill `claude-shorts` (MIT) does steps 1–8. You can use it or repeat its logic in code.
