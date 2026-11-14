---
name: seamless-insert
description: "Seamless AI inserts into real footage — anchor frames A/B, first/last frame, reversing to return to reality, matching fps, color and grain, hiding seams. Use in flows f02, f04, f05, f06 and wherever an AI clip is joined to real footage."
---

# Seamless AI insert into real video

## Anchor frames
1. **Frame A — an exact frame from the source:** `ffmpeg -ss <T> -i src.mp4 -frames:v 1 -q:v 1 A.png`
   (T comes from the skeleton; prefer a moment without camera or person movement).
2. **Frame B** = image_edit(A): only the target zone changes. Check the A/B difference outside the zone —
   it must match. If it does not, redo the edit.
3. **Static before video:** the reviewer checks B before any video generation.
4. **Video A→B:** Kling 3.0 Omni (Frames) or Kling 4.0 keyframes. The camera is static in the prompt.
5. **Return:** reverse the clip (`ffmpeg -vf reverse -af areverse`; the audio is replaced anyway).
   The last frame of the reversed clip = A = a real frame, so the seam is clean.

## Fitting the AI clip to the source
```bash
# fps and size as in the source, trim the unstable edges
ffmpeg -i ai.mp4 -vf "fps=30,scale=1080:1920:flags=lanczos,trim=start_frame=4,setpts=PTS-STARTPTS" ai_fit.mp4
# common grain over the whole video (after joining)
ffmpeg -i joined.mp4 -vf "noise=alls=6:allf=t" out.mp4
```
- Phone HDR (HLG) → convert to SDR first, otherwise the color will "jump".
- Match the AI clip's color to frame A: `eq`/`curves` by hand from 2–3 measurements, or color-matcher.
  Then apply a common LUT to the whole video.

## Hiding the seam
- Speed ramp of 5–8 frames + a whoosh at the join.
- Whip pan (motion blur), a flash, or a wipe on a word.
- Cut on an action or a word ("right here…").
- No morphing. A straight cut or a match cut is more honest and looks more expensive.

## Seam check
The reviewer watches ±10 frames around every join (`ffmpeg -ss <t-0.3> -t 0.6 -vf fps=30 seam_%02d.png`):
a jump in color, brightness, geometry, the person's pose, sharpness.
