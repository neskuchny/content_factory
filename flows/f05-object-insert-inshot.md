---
flow: f05-object-insert-inshot
title: An object appears right in the shot with the person and disappears
inputs: [video: a person speaks on a site, product references]
complexity: ●●●
cost: 2–4 images + 2–4 flf_video
---
## Essence
A person stands on a site and talks → right in this shot, next to them, a structure grows →
a "how it will look" pause → the structure disappears and the video continues from the same
place, the person talking on.

## Key technique — reverse
An FLF clip A→B (the appearance). Its **reverse** gives B→A (the disappearance). The last frame of
the reverse is exactly the real frame A, so the return to the real video is seamless.

## Steps
| # | Step | Details |
|---|---|---|
| 1 | skeleton | A moment T where the person is **static** (standing, pointing at the spot) for 3+ seconds. Camera on a tripod or otherwise steady |
| 2 | extract_frame | Frame A exactly at T (`-ss T -frames:v 1`), plus the source fps and resolution |
| 3 | image_edit | B = A + the structure; **the person and everything around unchanged** |
| 4 | review_still | The person is unchanged (face, pose, clothing); the A/B difference is only in the object zone |
| 5 | flf_video | A → B, "static camera; the person stands still; the structure assembles", 5–8 s. The person may "come alive" — 3–4 attempts, pick the best |
| 6 | hold *(opt.)* | 1–2 s freeze frame of B or a short i2v "the light came on" |
| 7 | reverse | Reverse the A→B clip (or a separate B→A generation) |
| 8 | seam | Real up to T → [A→B] → hold → [B→A] → real from T. Match fps and resolution, trim 2–6 unstable frames at the edges of the AI pieces, shared grain, speed ramp + whoosh |
| 9 | audio | The original voice: either a pause in the speech for the duration of the insert, or speech under the insert (J/L-cut) |
| 10 | label_ai → grade → render → review_video | Review the seams frame by frame (±10 frames around each joint) |

## If it does not work
The person gets deformed → take a frame where the person has left the shot, or switch to f04
(the insert as a separate piece) — that is the honest fallback.
