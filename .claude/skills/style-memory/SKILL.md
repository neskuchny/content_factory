---
name: style-memory
description: "Brand style memory — tokens, component library, the video's manifest, golden references of successful videos, the memorable element, a switchable logo. Use when assembling any video and when the human says \"I like this one\"."
---

# Style memory

## What is stored per client
```
clients/<c>/brand/
  tokens.json        # colors, fonts, radii, easing, durations, 9:16 safe zones
  visual.md          # style description + the MEMORABLE ELEMENT (the brand's recurring device)
  templates/         # components: badge, callout, titles, transition, CTA, "AI visualization" badge, logo layer
  references/        # external references the client likes (link + why)
  golden/<name>/     # golden references: successful videos that later videos are built from
  assets/            # logo SVG, fonts
```

## manifest.json — for every video
Lives next to the final file. It lets you rebuild the video and repeat the style.
```json
{"id":"W44-R03","flow":"f05-object-insert-inshot","duration":31.2,
 "logo":{"enabled":true,"src":"brand/assets/logo.svg","position":"top-left"},
 "tracks":[{"t0":0,"t1":2.1,"src":"a1b2c3d4e5f6@40.1","component":null},
           {"t0":2.1,"t1":7.8,"src":"gen/flf_A_B.mp4","label_ai":true},
           {"t0":0,"t1":31.2,"component":"subtitles/bold-yellow","data":"captions.json"}],
 "generations":[{"step":"flf_video","model":"kling_o3_flf","prompt":"…","seed":123,"credits":40}],
 "grade":{"lut":"brand/luts/warm.cube","strength":0.7,"grain":6},
 "music":{"src":"…","license":"…"}, "stock":[]}
```

## Golden references
When the human says "I like this one because…":
1. The feedback agent copies `manifest.json`, prompts, models, seeds, presets and the preview into `brand/golden/<rubric>-<short-name>/`.
2. It writes `why.md` **in the human's own words**: what exactly they like (pace, badge, transition, color).
3. In `visual.md` the rubric links to the golden reference.
The director builds the next video of this rubric from the golden reference: the same components, pace, grade.

## Rules
- The logo is a separate layer, switched off by a flag without re-editing. For localizations — an export without text.
- AI B-roll is brought to the brand style: prompt prefix and references from `visual.md`, a common LUT.
- The memorable element is present in every video of the rubric. Without it, videos are not remembered.
