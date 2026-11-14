---
name: video-code
description: "Editing and motion graphics in code — assembling Reels from source footage with ffmpeg, subtitles, overlay labels, kinetic typography, carousels and covers via HTML, rendering with HyperFrames or Remotion. Use for all units with engine code."
---

# Video and graphics in code

## Tools (installed once, see docs/04-setup.md)
- `ffmpeg` / `ffprobe` — cutting, joining, loudness, frames for checking.
- **HyperFrames** (`npx skills add heygen-com/hyperframes`) — HTML + GSAP → MP4. The main
  motion-graphics tool: free license, has `/media-use` for voiceover, music and sounds.
- **Remotion** (`npx skills add remotion-dev/skills`) — React templates driven by data. A company
  of 4 or more people needs a commercial license.
- Playwright — HTML → PNG for carousels, covers, Stories.

## Typical Reels from real footage
1. Take the moments from `media-index/moments.md` according to the script.
2. `ffmpeg`: cut by timecodes, 1080×1920, loudness normalization (`loudnorm`, −14 LUFS).
3. Subtitles from speech (whisper → words) in the style of `brand/visual.md`; hook text in the first 1–2 s.
4. Overlay labels (solution name, CTA) — from a template in `brand/templates/`.
5. Final render. 3–4 frames for self-checking: `ffmpeg -vf fps=1/3`.

## Carousels and covers
HTML template from `brand/templates/` → data from the script → a Playwright screenshot of each slide
(1080×1350). After rendering, look at the PNGs yourself and check line wrapping, cropping, legibility.

## Rules
- All texts, numbers and logos are in code; use fonts that cover the script of the client's language
  (for `ru` clients: Cyrillic).
- 9:16 safe zones: put nothing important in the top 250 px or the bottom 400 px.
- Keep the project (HTML/composition) next to the final file — it is editable, the mp4 is not.
