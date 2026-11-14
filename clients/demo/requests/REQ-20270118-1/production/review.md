# review.md: REQ-20270118-1 "Freshness dial" (FICTIONAL demo)

_reviewer, harness step 14 (`review_video` + `jury`). Video checked: `freshness_dial.mp4` (the publish file, 1080x1920, 18.0 s). Frame extracts and contact sheets are in the scratch folder, not in the repo._

```
verdict: PASS with fixes
issues:
  - [0.0-5.0, 8.0-11.5, 13.5-14.1] the needle sits on top of the dial numerals "0", "5" and "28" and
    cuts through the glyph (confirmed at 1.40, 8.0-11.4 and 13.5) → move the numerals below the
    tick row or shorten the needle so it stops above them. 0 credits, code only. Does not block:
    each numeral is still readable and the owner approved the stills on 2027-01-20.
  - [17.0-18.0] "Fictional demo brand" is about 24 px tall at 1080 px width (contrast 4.7:1, fine) →
    raise it to about 30 px; it is the disclosure line, so it should be easy to read on a phone.
    Does not block.
  - [whole film] check.py WARN: no subtitle track → explained, not a defect. The film has no speech;
    all words are burned in by code (`manifest.json`: voice null).
```
Nothing in the technical pass or the fact check is a FAIL. The jury fixes below are optional and the human picks which to apply.

## 1. Technical (ffmpeg-skill)
`check.py freshness_dial.mp4 --platform reels --content`: **19 checks, 0 failed, 1 WARN** (subtitles, see above).

| Check | Result |
|---|---|
| Duration / aspect / size | 18.00 s, 9:16, 1080x1920 |
| fps / VFR | 30, constant |
| Codec | h264, yuv420p, bt709/bt709 tagged; AAC 2 ch 48 kHz |
| File size | 6.4 MB |
| Loudness / true peak | -14.0 LUFS (my own ebur128 run: -14.2), -1.2 dBTP (astats peak -1.2 dB); no clipping, flat factor 0 |
| Black / frozen / flashes | 0 % black, longest frozen 3.1 s (limit 5.4 s), 0 flashes |
| Audio | 0 % silent, 0 dropouts |
| First frame | luma 204, spread 59 (not flat) |

Remark: loudness range is 13 LU (the bed is -45 dBFS and the hits are loud). That is acceptable for a no-music film, but a phone speaker will make the room tone hard to hear.

**Safe zones** (`look.py --safe reels --tiles 3x2`; top 8 % = 154 px, bottom 20 % = 1536 px, left 5 % = 54 px, right 12 % = 950 px):
- All six titles, the handle and the demo line are inside the zone: left edge about 63 px, top at about 17 % of the height, the longest line (T5) ends at about 74 % of the width.
- The radio ends at about 78 % of the height, so about 20 px above the bottom UI zone. That is tight but clear.
- Only props enter the shaded right strip: the stamp-lever stand and the radio knob (non-text, decorative). The "28" numeral sits at about 81 % of the width, clear of it.
- Nothing is inside the top or bottom zones. About 20 % of the frame under the radio is empty: that is the bottom UI zone, which is correct.

**Frames every 0.5 s** (36 frames, `m1.png` and `m2.png` in the scratch `qc/` folder): no flicker, crooked posts or garbled text. The edges wobble by design. No hands, faces or people. The text fades are clean. The titles do not overlap objects.

**Cause in frame (±10 frames, harness step 14):**
- 10.20 (frames 296-316): no imprint at frame 305 (the pad is above the label); imprint "ROAST DATE" present and pad touching the label at frame 306 (= 10.20); the lever then swings up. ✔
- 11.60 (frames 340-358): the band is unlit at frames 340-347 and copper at 350; the needle is held at 5 until it starts to move, then moves on. The audio tone starts at 11.6. ✔ (a 2-3 frame offset, inside the tolerance)
- 3.00 (frames 80-100): the drum door opens first (dark hole at 88-92), beans appear on the chute at about frame 100. ✔
- 1.40 (frames 32-52): the needle settles on 0 at 42 and is still to 52; the settle tap is at 1.40. ✔
- Audio and picture line up: the 100 ms RMS jumps at exactly 1.4 s (-11.6 dBFS), 3.0 s (-11.2) and 10.2 s (-10.0, the loudest), and the quiet window before 10.2 is -41 dBFS, so the stamp starts on the frame of the hit.

## 2. Facts (skill `fact-check`; all sources in `clients/demo/product-base/`)
| On screen | Source | |
|---|---|---|
| T1 "When is your coffee at its best?" (a question, not a claim) | the answer is `care-tips.md` → Freshness. A question with "best" is not the hype in `brand/voice.md` ("best coffee ever") | ✔ |
| T2 "Day 0: roasted on site" | `roasting-process.md` → Steps #2 and Equipment (drum roaster in the shop's back room); `products.md` → "roasted on site" | ✔ |
| Cooling tray (picture only, 3.0-5.1) | `roasting-process.md` → Steps #3 ("a few minutes": the film does not give a duration) | ✔ |
| T3 "We rest the beans 5 days" and the 5 hops | `roasting-process.md` → Steps #4 | ✔ |
| T4 "Then every bag gets its roast date", the fold and the stamp | `roasting-process.md` → Steps #5 ("sealed and stamped with the roast date"); `products.md` → Specifications ("Every bag carries a printed roast date") | ✔ |
| T5 "Best brewed about 5 to 28 days after roast", the band, "5", "28", "DAYS AFTER ROAST" | `care-tips.md` → Freshness ("from about 5 to 28 days after the roast date printed on the bag"). "About" is kept; no number is rounded | ✔ |
| T6 "Check the roast date on yours" | an instruction, not a claim; relies on `products.md` (every bag has a printed roast date) | ✔ |
| "@example_brewline" | `channels.yaml` → instagram.url | ✔ |
| "Fictional demo brand" | disclosure for the demo, not a product claim | ✔ |
| Caption in `beats.md` ("Grind just before brewing", 5 days, 5 to 28 days) | `care-tips.md` → Freshness; `roasting-process.md` #4 | ✔ |

Checked and not found on screen: no price, no flavour word, no "stale after 28 days", no "small batches", no roasting time, no health claim, no customer story. The dial scale runs past 28 and the needle starts at 31; this is only a scale, and nothing is said about it.
Remarks, not defects:
- The stamp prints the words "ROAST DATE" and three blank bars, not a calendar date: correct, since no date is in the product base.
- Day 5 is both the end of the rest (#4) and the start of the band (care-tips). The film shows them side by side and does not say that one causes the other. ✔
- The roaster, tray, bin and bag are pictograms. `product-base/` has no appearance data (roaster brand and model are "Not confirmed"), and the owner approved the pictogram on 2027-01-20 (`decisions.md`). The "AI visualization" rule does not apply: nothing is generated (`manifest.json`: `generations: []`, `label_ai: false`). The pictogram can still be read as an old hand coffee mill (see jury Q3).
- The scoop and lid move without hands; "filled by hand" is not claimed on screen.

## 3. Words (`scripts/qa/words_check.py --lang en data/texts.json`)
4 findings, exactly the 4 expected in `beats.md`: "best" (T1), "5 days" (T3), "best" and "28 days" (T5). Each is covered by a row above. No generated-sounding phrase. All six titles are 9 words or fewer (the longest, T5, has 8), in the plural "we" voice from `brand/voice.md`.

## 4. Brand (`brand/voice.md`, `brand/visual.md`)
- Palette: cream, espresso and copper only. Copper is used only on the keyword and the lit band (checked on every half second; the needle, roaster and bag are never copper). Fonts: Fraunces for titles, Inter for the labels, both from the local files.
- Tone: calm, plain, one tip. No hype, no people, no music. The film is made with 0 credits.
- Labeling: no AI badge, correctly (nothing generated). The caption needs no AI note.
- Prohibited list: no text inside a generation, no stock, no distorted real products (none are defined in the demo).

## Jury (skill `jury`; the technical pass has no FAIL)
1. **Hook (0-2 s):** yes. At frame 0 the whole set is on screen and the needle is already sweeping from 31 toward 0 with a click per day; the band flashes copper at 0.20-0.95 and the needle settles at 1.40. Weak spot: the needle is a thin line on a dial about 300 px tall at 390 px preview width, so what a viewer sees first is a title and a small gauge, not a big move. The hook works as built; I do not propose a change to it.
2. **Main moment:** the stamp at **10.20**: the pad hits, the imprint appears on that frame, and it is the loudest sound (-10.0 dBFS vs -11.6 at 1.40 and -11.2 at 3.00). It hits harder than the answer at 11.60 (the band lights, tone -12.3), which carries the real message. That is acceptable (the stamp sets up the CTA), but the answer feels softer than its setup.
3. **A frame like everyone else's:** the held end frame at **16.0-18.0** (one kraft bag, a label, a radio). It is clean but could belong to any brand's "check the date" reel. The radio dial is the distinctive idea; the bag is not. Also, the roaster at 0-5 s (spoked drum, hopper, a chute that looks like a crank) reads as a vintage hand grinder to some viewers. The owner accepted this, so it is a note and not a fix.
4. **Weakest 5 seconds:** **5.9-8.4**, then into the rest of beat 3 (about 4.4-8.4). The title is static, nothing else moves, and only the needle hops five times; the stillness is meant ("resting = stillness") but 2.5 s of a thin needle moving on a small dial is the least readable stretch. The next weakest is the final hold at **16.0-18.0** (2 s of a static bag with only a fading tone) and 14.2-15.0, after the glide has ended.
5. **Sound on picture:** yes, all three main events have their own sound: settle tap at 1.40, bean rush at 3.00 and the stamp thunk at 10.20, each verified at the hit (jump of 14-30 dB against the 100 ms before). The warm tone enters at 11.6 with the band. The five hops at 5.9-7.9 have only clicks of about -25 dBFS RMS (the quietest part of the film, which matches Q4).
6. **Words:** no line sounds generated. `words_check` gives only the four expected hints, all sourced. T5 is the longest line at 8 words; it is readable for 3.45 s. The captions and CTA are plain.

**Score: 7 of 9** (a solid professional piece). It is coherent: one mechanism carries every fact, every move has a visible cause, the sound is made by the objects, and the stamp lands on the right frame. It is not an 8 because the dial and objects are small, the 5.9-8.4 stretch and the end hold are static, and the closing frame is generic.

**Fixes (most important first; the human chooses; the jury does not block release):**
1. **5.9-7.9, add a day counter (wow, 0 credits, code).** On each of the five hops, a small copper numeral 1, 2, 3, 4, 5 pops above the needle (about 0.12 s ease, brand curve) and the one before it fades; the numeral is code text (CLAUDE.md §5.3) and comes from the "5 days" fact, so no new facts. The click stays; add a soft tick on top. This turns the quietest 2.5 s into a visible count-up that the viewer can follow. Re-render only 5.8-8.0: about 2 minutes.
2. **0.0-5.0, 8.0-11.5, 13.5-14.1, stop the needle covering "0", "5" and "28" (0 credits).** Move the three numerals 14 px below the ticks (they currently sit on the needle's path) or end the needle 16 px above them. The "5" is half hidden through the whole stamp scene and the "0" through the whole roast scene. `checks.py` can assert that no needle box overlaps a numeral box.
3. **17.0-18.0, loop-back, so the Reel loops into the hook (0 credits).** Slide the props back in from 17.2 and push the needle to 31 by 18.0 (keep the handle on screen to 17.2, about 2.2 s of CTA), so the last frame equals frame 0. Reels loop automatically, so the first frame becomes the answer to the end card, and the generic end frame is on screen for less time. If the owner wants the 2-second hold, drop this one.

## Notes for the approval pack (one line)
"Jury 7/9; main fix: a 1-5 day counter on the five hops (5.9-7.9, 0 credits). Also: the dial numerals are covered by the needle (0 credits). Facts ✔, AI: no."

## Not done / limits
- I looked at 36 frames (every 0.5 s) and several full-resolution crops; I did not step through all 540 frames. `data/checks_report.json` (studio's own 540-frame check) was not re-run.
- `loudness.py` was not re-run; I measured with ebur128 and astats.
- `permissions.yaml` was not edited; the 0-credit row is still due from the owner (`decisions.md`, 2027-01-18).
