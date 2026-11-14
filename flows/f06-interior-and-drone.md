---
flow: f06-interior-and-drone
title: Interior after renovation + exterior fly-around under the voice
inputs: [walkthrough of a property, a photo of the facade/site or a render, optionally a design project]
complexity: ●●
cost: 2–6 images + 1–3 video_edit/i2v
---
## Essence
A person shows an apartment or house → "how it will look after renovation" inserts (per our
design) → then a "drone" flies around the house outside while the person's voice from inside
continues off-screen.

## Steps
| # | Step | Details |
|---|---|---|
| 1 | skeleton | Blocks: rooms; the moment where the speech is about the house from outside, the location, the roof |
| 2 | extract_frame | Frames of the rooms (static angles) |
| 3 | image_edit | "After renovation" with the same geometry; if there is a design project, use its references |
| 4 | review_still | Windows and openings in place, the style matches the project |
| 5 | renovation delivery | A before/after wipe (code) **or** f02 for a change in motion **or** flf_video A→B |
| 6 | fly-around | Facade photo (upscale) → optionally an end frame "higher and wider" → flf_video / i2v (Kling, Cinema Studio, Veo 3.1). **One move**: "slow drone orbit ≤90° around the house, steady, no morphing of architecture", 5–8 s |
| 7 | audio | J-cut: the speaker's voice is continuous, the fly-around runs as B-roll over it |
| 8 | label_ai | On all AI pieces: the renovation — "project visualization", the fly-around — "AI visualization" |
| 9 | grade, subtitles, audio_mix → render → review_video | |

## Pitfalls
The fly-around "invents" neighboring houses and terrain, and the architecture morphs at large
angles. Keep the orbit ≤90° and do not pass it off as footage of the real object.
