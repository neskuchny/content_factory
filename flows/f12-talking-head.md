---
flow: f12-talking-head
title: Talking-head edit
inputs: [video of a person talking]
complexity: ●
cost: no generations
---
## Steps
| # | Step | Details |
|---|---|---|
| 1 | skeleton | Word-level transcript, pauses, fillers, takes |
| 2 | cut | Remove pauses, "um"s, failed takes — by words, checking the frames at every cut (the video-use approach) |
| 3 | Cold hook | The strong phrase goes first |
| 4 | Dynamics | Change of scale (crop 1.2–1.5× on accents), a light push-in, B-roll cutaways from the archive every 4–6 s |
| 5 | overlay | Theses, name and role, facts (from product-base) |
| 6 | subtitles | Word by word, highlight the key words |
| 7 | grade, audio_mix (noise reduction, −14 LUFS) → render → review_video | |

## Tool
browser-use/video-use (transcript-based editing) or ffmpeg + HyperFrames.
