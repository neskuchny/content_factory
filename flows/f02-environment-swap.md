---
flow: f02-environment-swap
title: Swapping the environment around a person
inputs: [video of a person speaking in a real room or on a site]
complexity: ●●●
cost: 1–3 video_edit of 5–10 s each + 2–4 images
---
## Essence
The person says: "What if this were a modern style…" — and **the whole picture** changes: a
different room around the same person, who keeps talking.

## Good to know
Edit models (Kling 3.0 Omni Edit, Kling 4.0 edit, Seedance 2.5 / Cinema Studio 4.0 `video_edit`,
FLUX 3 Video Edit) repaint the **whole clip** from a reference. They do not do a smooth
transformation in the middle of a clip. The moment of transition is assembled in the edit.

## Steps
| # | Step | Details |
|---|---|---|
| 1 | skeleton | Find the timecode of the trigger phrase in the transcript |
| 2 | cut | A = before the phrase (real), B = 5–10 s from the phrase (will be redone). Long pieces go as 5–10 s segments |
| 3 | extract_frame | A frame from B |
| 4 | image_edit | The finished interior **with the same geometry** (windows, walls, floor in place), the person untouched → style reference |
| 5 | review_still | Geometry, light, the person unchanged |
| 6 | video_edit | B + reference. Prompt: first **what to keep** ("keep the person, face, clothing, gestures, lip movement and camera motion identical"), then **what to change** ("replace only walls/floor/ceiling with the interior from the reference"). 50–150 words, one edit at a time |
| 7 | lipsync *(if lips drift)* | Sync Lipsync 3 from the original audio track |
| 8 | seam | Transition A → B' on a word: wipe (`xfade=wipeleft`), flash, or a quick zoom + whoosh. The original sound is continuous |
| 9 | label_ai | "AI visualization" for the whole duration of B' |
| 10 | grade + audio_mix → render → review_video | |

## Pitfalls
Drift of the face and hands; furniture "floats" when the camera moves; several people in the frame
sharply reduce stability. It works best with a slow camera and one person.
A pilot on a 5-second piece is mandatory before serial production.
