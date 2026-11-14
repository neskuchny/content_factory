# Director card — REQ-20270118-1 "Freshness dial" (f18 code film, 2D) — FICTIONAL demo

_director, 2027-01-19. Card rule (f18 step 2): every device has a reason taken from this story; no reason, no device.
Numbers are starting values for the first still. Studio may change them after the stills and writes every change
to `production/log.md`. Coordinates are screen pixels at 1080×1920 (static camera, y down)._

## 0. In one line
A paper radio whose dial counts days after roast. Each day is one click. The copper band from 5 to 28 is the station
where the coffee is best brewed. Above the radio, the beans travel from the drum to a stamped bag. The feeling: a calm,
tidy desk toy in three brand colours. The only bright moment is copper, and copper always means "best brewed".

## 1. Language and material
**2D Canvas, flat paper-cut, front view, static camera.** Why:
- The story is a timeline. A dial makes the timeline a physical object with one moving part (the needle). One cause
  (the knob) explains every move of the needle. That is easy to read and easy to check by script.
- Flat paper keeps it robust for code: solid fills, a light grain, two shadow depths. There is no 3D, no lighting
  model, and no texture that can flicker.
- No footage and no people: everything that "works" is a tool (door, tray, lid, scoop, stamp lever, knob). No hands
  are drawn: the knob turns by itself, as a convention, like the hands of a clock.
- **The roaster is a pictogram, not a portrait.** Brand and model are not confirmed (`roasting-process.md` → Not
  confirmed). It is a generic small drum roaster (hopper, drum with a front door, chimney, chute, legs). It must not
  copy any real machine. The owner confirms it on the stills (harness step 8). The bag is a plain kraft flat-bottom bag
  with a cream label: no wordmark, no label design and no weight are printed on it.

### 1.1 Paper
- Backdrop: cream `#F6EFE6` with a grain tile of 512×512 px. The tile comes from a seeded noise function (mulberry32,
  seed 20270118) at load time, luminance ±2 %. The grain does not move from frame to frame.
- Cut edge: every shape's outline is offset by seeded noise, ±1.2 px at 1080 wide (scaled by W/1080). It is fixed per
  shape, not per frame. **No strokes, no gradients, no gloss.** Every line is a filled shape at least 6 px thick, except
  the dial ticks (6 px) and the grille slots (10 px).

### 1.2 Set (from `shotlist.json → world`)
- Shelf: strip `#54473E`, y 1040–1060, x 60–1020. Stage objects stand on it.
- Roaster x 70–330, y 600–1040 · cooling tray (ellipse) centre 425,985 · resting bin x 575–715, y 860–1040 · bag
  x 790–950, y 820–1040 · stamp lever pivot 1010,760 (the arm rests up).
- Radio body x 60–1020, y 1090–1500, `#2B1D14`, radius 16. Dial face x 110–970, y 1130–1310, cream. Dial: day d sits
  at x = 150 + 26·d (day 0 = 150, 5 = 280, 28 = 878, 31 = 956). Needle 8×170 px, espresso. Knob r 62 at 900,1430.
  Label "DAYS AFTER ROAST" cream on espresso at y 1345. Five grille slots x 120–780, y 1390–1470.
- Titles: x 60–940, y 260–520, left-aligned, at most 2 lines.

## 2. Light and shadow
One soft light from the top left. Shadows are offset (6, 8) px in espresso, with two depths only:
| Depth | What | Shadow |
|---|---|---|
| standing | roaster, tray, bin, bag, radio body | offset 6,8 · blur 12 · alpha 0.20 |
| lifted | scoop, stamp lever, beans in flight, door when open | offset 10,14 · blur 18 · alpha 0.14 |
| printed | ticks, labels, imprint, titles | none |
Why: two depths are enough to tell "stands on the shelf" from "moves in the air". One shadow style for everything
would make it look like vector icons.

## 3. Palette (brand `tokens.json` + tints mixed only from it)
| Role | Colour | Mix |
|---|---|---|
| backdrop, dial face, titles on dark | cream `#F6EFE6` | brand bg |
| text, radio body, needle, ticks | espresso `#2B1D14` | brand primary |
| **band, keyword in each title** | copper `#C26A2E` | brand accent |
| bag kraft | `#E1BA9C` | cream 60 % + copper 40 % |
| unlit band, knob | `#E6DED5` | cream 92 % + espresso 8 % |
| shelf, roaster parts, tray, bin, grille | `#54473E` | espresso 80 % + cream 20 % |
| roasted beans | `#51301B` | espresso 75 % + copper 25 % |
Rules: **copper means "best brewed" or a keyword and nothing else.** No copper on the needle, the roaster or the bag.
Contrast: espresso on cream 14:1; copper keywords on cream 3.4:1 (large text only, ≥ 60 px, which meets the 3:1 rule);
espresso labels on the copper band 4.2:1.

## 4. Fonts (local files, OFL 1.1)
- Fraunces SemiBold 600 for titles: 68 px, line height 1.12, keyword in copper.
- Inter Bold 700 for scene labels and the end card: dial numbers 44 px; "DAYS AFTER ROAST" 30 px with letter spacing
  0.12 em; imprint "ROAST DATE" 22 px (×1.35 in beat 6); handle 44 px; "Fictional demo brand" 26 px in espresso at 60 %.
- Studio downloads the woff2 files once (Google Fonts or the `@fontsource` packages) into `production/scene/fonts/`
  with `OFL.txt`, and writes their md5 into `log.md`. The page never loads fonts from the network.
- Why these: they are the brand fonts (`visual.md`). There is no voice, so the titles carry the message, and they use
  the heading font, not the subtitle style.

## 5. Camera
Static for all 18 s, with no shake and no zoom. Why: the dial must stay readable at all times, and every cause stays in
the frame. Beat 6 makes the bag bigger by moving the object (×1.35), not the camera.

## 6. Motion
- Easing is the brand curve `cubic-bezier(0.22, 1, 0.36, 1)`. Titles come in over 0.35 s (they slide up 24 px and fade
  in) and go out over 0.25 s. Every title stays at least 1.5 s (`tokens.json → durations`).
- The needle follows monotone cubic interpolation through the keys in `shotlist.json`. The hook ends with an overshoot
  to −0.3 day, settling at 1.60. The hops in beat 3 have **no overshoot**, so the needle never crosses 5 by accident.
- The band turns copper over 3 frames when the needle enters (5 < day ≤ 28) and turns back over 3 frames when it leaves.
- Beans are 8–12 px seeded paper ellipses. Their paths are pure functions of t (a ballistic arc plus a seeded offset),
  with no physics state carried between frames.
- One leading event at a time (beats table). Nothing moves for decoration: no idle wobble, no particles, no smoke.

## 7. Sound (code only, `production/project/sound.py`, seed 20270118)
Idea: **each object sounds like what it is, and the band has its own tone.** No music (owner, 2027-01-19). No voice.
| Beat | Sound | Why |
|---|---|---|
| all | room tone at about −45 dBFS | not dead silence |
| 1 | a detent click for **every day the needle crosses** (31 clicks, rate follows speed); 0.20–0.95 a warm two-note tone (sine partials, D4 + A4, attack 80 ms); 1.40 needle settle tap | the hook is audible from frame 0; the tone is tied to the band |
| 2 | drum rumble (60–120 Hz noise, modulated by drum rotation) 2.60–4.40; 2.90 door clack; 3.00–3.80 bean pour (seeded grain clicks, density falls off); 3.80–5.10 soft scrape of the stir arm | each visible action has its sound |
| 3 | 5.15 lid tap; 5.30–5.80 a smaller pour into the bin; 5.85 lid closes; five single clicks at the hops; almost silent otherwise | rest is stillness |
| 4 | scoop digs and patters into the paper bag ×2; 9.85 paper crinkle; **10.20 stamp thunk** (body 80–150 Hz + paper slap); lever spring at 10.30 | the owner asked to keep the stamp sound (W02-R01) |
| 5 | clicks per day 11.60–13.80 (23) and 14.20–14.80 (14); the warm tone sustains while the band is copper, 11.60 to the end, at −10 LU under the effects | the "station comes in" |
| 6 | paper slides as the props leave and the bag comes forward; the tone holds, then fades 17.40–18.00 to −30 dB (not to digital zero) | a quiet, warm ending |
Loudest events, in order: stamp 10.20, needle settle 1.40, bean pour 3.00. The peak of each sound is on the frame of
its event. Master −14 LUFS, true peak ≤ −1 dBTP (`loudness.py`). No whooshes. Licences: all code (`audio/sources.md`).

## 8. Logic: every event has a visible cause
| Event | Cause in the same frame | Where to check |
|---|---|---|
| the needle moves | the knob turns by day × 12°; one click per day | `__state()` every frame; stills 0.00, 6.90, 12.70 |
| the band is copper | needle inside 5 < day ≤ 28 | `__state()`; stills 0.50 (lit), 1.60 (unlit), 10.20 (unlit at 5), 12.70 (lit) |
| the warm tone plays | band copper (same frames ±1) | `sfx_events.json` vs `__state()` |
| beans fall into the tray | the drum door is open; beans follow the chute | still 3.30 |
| the stir arm turns | beans are in the tray (3.80–5.10 only) | still 4.50 |
| beans go into the bin | the tray tips; the lid is up | strip 5.1–5.9 (draft) |
| beans go into the bag | the scoop carries them from the bin | still 9.10 |
| the imprint appears | the stamp pad touches the label on that frame | still 10.20 |
| the props leave, the bag comes forward | CTA: one object with its date | still 17.00 |
This table is part of acceptance (reviewer, harness steps 7, 8 and 14).

## 9. What we do not do
- People, hands, faces on objects, mascots.
- A real roaster's look, brand marks, a bag label design, a weight or a calendar date printed in the scene.
- Text inside a drawing except code-set labels (CLAUDE.md §5.3); no "AI visualization" badge (nothing is generated).
- Steam, smoke, particles for their own sake, whooshes, music, camera moves, morphing.
- A second accent colour, or copper on anything that is not the band or a keyword.

## 10. Memory → what is done here
| From memory | Here |
|---|---|
| W02-R01: "Please keep the stamp sound." | the stamp is the loudest sound of the film (§7) |
| W02-C01: "slide 3 has too many words" | one title on screen at a time, at most 9 words; the second tip moved to the caption |
| REQ-20270111-1: calm, no music | no music; one warm tone tied to the band |
| `consents.md`: no people | no hands either; tools move by themselves |
