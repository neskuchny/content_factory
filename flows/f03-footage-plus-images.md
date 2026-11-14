---
flow: f03-footage-plus-images
title: Video + supplied images
inputs: [video, a set of images (renders, photos, diagrams), optionally a note on what is what]
complexity: ●
cost: no generations
---
## Essence
An employee sent a video and images, for example "this is a video of the site, these are the
designer's visualizations". The system decides on its own where to put each image so that it looks good.

## Steps
| # | Step | Details |
|---|---|---|
| 1 | skeleton (video) | Speech blocks and visual blocks |
| 2 | skeleton (images) | A caption for each image: what is in it, which part of the object it relates to, quality |
| 3 | matching | A table "image → moment of speech or frame" where it illustrates what is said. An image without a pair is not inserted |
| 4 | beats + select + cut | A script built around the matched moments |
| 5 | overlay | How to present an image: full-screen 1.5–3 s (Ken Burns), a before/after wipe with a video frame, PiP, parallax (Depth Anything + layers) |
| 6 | label_ai | If the images are visualizations rather than photos of the finished work |
| 7 | subtitles, grade, audio_mix → render → review_video | |

## Rule
If the human's explanation contradicts the skeleton ("this is a photo of the kitchen" but the photo
shows a bathroom), ask; do not guess.
