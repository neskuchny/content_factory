---
name: jury
description: "Jury: a short creative review of a video draft after the technical QC. Six questions with timecodes (hook, key moment, \"shot like everyone else's\", the weakest 5 seconds, sound at the cuts, generated text), a score of 5–9 and at most three fixes. Use for the reviewer as a second pass on every video that has passed the technical checks, and when the human asks \"did it turn out interesting\"."
---

# Jury: is this interesting to watch

The idea and the questions are based on `references/jury.md` from sarpstar/cinecode (MIT). Adapted for the factory.

The technical QC answers "is there any defect". The jury answers "will people watch to the end and forward it". This is the reviewer's
second pass after the technical PASS. It is not a new render and not a lengthy check: 2–3 minutes over the already finished
materials.

## What to look at
- a contact sheet with the platform's safe zones: `python3 .claude/skills/ffmpeg-skill/scripts/look.py <video> --safe reels --tiles 3x2 -o <png>`;
- at most three individual frames at the moments the questions are about;
- `beats.md` / the script and the on-screen text;
- the output of `python3 scripts/qa/words_check.py <file with texts>`.

## Six questions: a timecode and one sentence for each
1. **Hook:** in the first 2 seconds, is the object/character already doing something? If not, what to show instead.
2. **Key moment:** where is it, and does it hit harder than everything around it?
3. **"Shot like everyone else's":** is there a shot that would fit any video from any company (template, stock, AI default)? Which one?
4. **The weakest 5 seconds:** where and why (static, repetitive, unclear, drawn out)?
5. **Sound on the picture:** do the three main cuts/hits each have their own sound?
6. **Words:** does any line sound generated (per `words_check.py` and by ear reading the text)?

## Then: at most three fixes
The most significant first. Each one: a timecode, what to change and how, in numbers. At least one should raise the "wow", not
only polish. Cost of the fix: 0 credits (done in code) or how many credits.

## Score (honest, against anchors)
5 — student work · 6 — template · 7 — solid professional · 8 — strong agency · 9 — award shortlist.
First drafts are usually 5–7.

## Where to write
In `review.md`, a "Jury" section: six answers, the score, up to three fixes. In the approval pack, one line:
the score and the main fix; the human chooses which fixes to apply.
The jury does not block release: only the technical QC blocks. A score below 6 is a reason to propose a
redo to the human, not an obligation to do one.
