---
name: ai-visualization
description: "Create \"what it could look like\" AI visualizations through the Higgsfield MCP: the client's real product on a site or in an interior, a structure appearing and being assembled, lifestyle scenes. Preserves the product's geometry and always carries a label. Use for content units of type V and for pins that use AI."
---

# AI visualization of a real product

Full flows: `flows/f04-object-insert-broll.md` (insert as a separate segment),
`flows/f05-object-insert-inshot.md` (inserted directly into a shot with a person). For seams, see the `seamless-insert` skill.

## Input
- The unit's script (what to show, in what order).
- **Product references** from `product-base/media/`: real photos of the product from 2–3 angles,
  dimensions, profile color. Do not start without references; request them through the orchestrator.
- A photo of the site or house (if the scene is "at the client's place") or a description of the surroundings.

## Pipeline (cheap first, expensive later)
1. **Key frames (images).** `generate_image` with an edit model (Nano Banana Pro / GPT Image /
   Seedream) and the product references. You need 2–4 frames of the scene: empty site → structure →
   life in it (evening, dinner, plants).
   Prompt: product, angle, light, time of day, surroundings. The prompt must end with:
   "preserve the geometry, profiles and proportions of the product exactly as in the reference; no text in the frame".
2. **Frame review** (reviewer). Rejects are filtered out here, while it is still cheap.
3. **Video.** `generate_video` image-to-video or start/end frame (Kling / Seedance / Cinema
   Studio). One camera move per clip, 5–8 s. The "structure appears" effect is a transition
   from the empty frame to the finished frame.
4. **Video review** (reviewer): posts, glazing, flicker, faces.
5. **Assembly in code:** stitching, subtitles, a permanent, legible **"AI visualization"** badge,
   CTA. Render with HyperFrames or Remotion.

## Cost
Before steps 1 and 3, estimate the credits and record them in `weeks/<W>/costs.md`. Regenerate a frame
at most 3 times, then ask the human.

## Never
- Present an AI visualization as a completed project (including on Yandex Maps).
- Generate text, prices or logos inside the image.
- Insert real people without consent (`brand/consents.md`).
