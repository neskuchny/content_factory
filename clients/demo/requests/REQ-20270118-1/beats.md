# beats.md — REQ-20270118-1 "Freshness dial" (f18 code film, 2D flat paper-cut) — FICTIONAL demo

_director, 2027-01-19. Skill `hook-storyline`. Timing source of truth: `shotlist.json`._

**Logline.** The bottom of the frame is a paper radio. Its tuning dial does not show stations: it shows **days after
roast**. Above it, on a shelf, are a small roaster, a cooling tray, a resting bin and a bag. The needle starts at day 0
when the beans leave the drum. It clicks forward one day at a time while the beans rest. On day 5 the bag is filled
and stamped with its roast date. Then the needle glides through the copper band from 5 to 28, where the coffee is best
brewed, and a warm tone plays like a station coming in. Last: "Check the roast date on yours."

**Structure:** expert, one tip: question → proof (the timeline) → one practical step. **18.0 s**, 540 frames, 30 fps.
No voice. A new event at least every 2.4 s.

**Hook (0–2.6 s), the same in three channels:** *seen:* the knob turns, the needle sweeps from day 31 to day 0, and the
band flashes copper as the needle crosses it; *written:* "When is your coffee at its best?"; *heard:* one detent
click per day and a short warm tone while the needle is in the band. Type: open loop (the flash is answered in beat 5).

## Concepts (f18 step 1 + skill `idea-dice`, `scripts/qa/dice.py 3 --seed 20270118`)
| # | Spark | Concept | Verdict |
|---|---|---|---|
| 1 | radio receiver | **Freshness dial.** A tuning dial in days after roast; the copper band 5–28 is the "station" | **chosen** (decisions 2027-01-19): one mechanism carries all the facts; a cause is visible for every move |
| 2 | binoculars | "Spot the date": two round lenses scan a bag and find the stamp | dropped: too close to W02-R01 variant C ("Don't buy a bag without this") |
| 3 | harvesting into buckets | "28 cups": a row of paper cups, one per day, filling with copper | dropped: a cup per day reads as a cups-per-bag number that is not in `product-base/` |

## Beats
| # | t, s | beat (type) | what is said | what is seen (source: code) | cause in frame | text on screen |
|---|---|---|---|---|---|---|
| 1 | 0.0–2.6 | hook · open loop | — | Frame 0 shows the whole set: shelf with roaster, tray, bin, bag; the radio with the needle at day 31, already moving. The needle sweeps left; the band is copper 0.20–0.95 while the needle is inside it; it settles on 0 at 1.40 (small overshoot, still at 1.60) | the knob turns 12° per day; one click per day | T1 "When is your coffee at its best?" |
| 2 | 2.6–5.1 | day 0 · roast | — | The drum spins up; 2.90 the door flips open; 3.00–3.80 beans pour down the chute into the cooling tray; 3.80–5.10 the stir arm turns in the tray; the drum slows down | beans come only out of the open door, along the chute | T2 "Day 0: roasted on site" |
| 3 | 5.1–8.5 | rest · 5 days | — | 5.15 the bin lid lifts; 5.30–5.80 the tray tips and the beans slide into the bin; 5.85 the lid closes. Then **only the needle moves**: one hop per day at 5.90 / 6.40 / 6.90 / 7.40 / 7.90 → day 5 | the tray tips toward the open bin; knob click per hop; resting = stillness | T3 "We rest the beans 5 days" |
| 4 | 8.5–11.4 | pack · stamp | — | 8.60 the lid lifts; the scoop fills the bag twice (8.80, 9.40); 9.70 the lid closes; 9.85–10.00 the bag top folds over (sealed); 10.00 the stamp lever swings down, **10.20 the pad hits the label** and the imprint "ROAST DATE" appears; the lever swings back up | the scoop carries the beans; the imprint appears on the frame the pad touches the label | T4 "Then every bag gets its roast date" |
| 5 | 11.4–15.0 | answer · the band | — | 11.60–13.80 the needle glides 5 → 28; the band turns copper the frame the needle passes 5; labels 5 and 28 sit at its edges; 14.20–14.80 the needle comes back to day 14 and stays | the knob turns; the band is copper only while the needle is inside it | T5 "Best brewed about 5 to 28 days after roast" |
| 6 | 15.0–18.0 | viewer's step · CTA | — | 15.00–15.60 the roaster, tray, bin and lever slide out to the sides; 15.00–15.80 the bag comes to the centre (×1.35) with its stamped label facing us; the needle stays in the lit band; hold from 16.0 | one object left: the bag with its date | T6 "Check the roast date on yours" + "@example_brewline" + "Fictional demo brand" |

## Logic check (director)
- **The dial is the only clock.** The needle moves only when the knob turns (12° per day, one click per day). The band
  is copper only while the needle is between 5 and 28; at exactly 5 (beat 4) it stays unlit. The rule is the same in
  the hook and in beat 5, so the early flash makes sense afterwards.
- **The beans go one way:** drum → chute → tray → bin → scoop → bag. Nothing appears from nowhere. Every step is
  started by the object before it (door, tray tip, lid, scoop).
- **Day 5 is two facts side by side.** Packing happens on day 5 (`roasting-process.md` #4–5), and the band starts at 5
  (`care-tips.md`). The film shows both and does not claim one causes the other.
- **The stamp prints the words "ROAST DATE" and three blank bars**, not a calendar date. A made-up date would be a fact
  that is not in the product base.
- The camera is static. Nothing is generated, so no "AI visualization" label is needed.

## Texts (character for character; studio does not change them)
Titles (Fraunces 600, copper keyword in brackets):
- T1 "When is your coffee at its best?" [best]
- T2 "Day 0: roasted on site" [Day 0]
- T3 "We rest the beans 5 days" [5 days]
- T4 "Then every bag gets its roast date" [roast date]
- T5 "Best brewed about 5 to 28 days after roast" [5 to 28 days]
- T6 "Check the roast date on yours" [roast date]
Scene labels (Inter 700): "0", "5", "28", "DAYS AFTER ROAST", "ROAST DATE". End card: "@example_brewline", "Fictional demo brand".

## Facts (skill `fact-check`)
| On screen | Fact | Source |
|---|---|---|
| T2 "roasted on site", the drum | "A batch is roasted in a small drum roaster on site" | `product-base/roasting-process.md` → Steps #2; Equipment |
| Cooling tray (picture only) | "Roasted beans cool on a cooling tray for a few minutes" | `product-base/roasting-process.md` → Steps #3 |
| T3 "We rest the beans 5 days", 5 hops | "Beans rest for 5 days before they are packed for sale" | `product-base/roasting-process.md` → Steps #4 |
| T4, the fold, the stamp | "Bags are filled by hand, sealed and stamped with the roast date"; "Every bag carries a printed roast date" | `product-base/roasting-process.md` → Steps #5; `product-base/products.md` → Specifications |
| T5, the band 5–28, "DAYS AFTER ROAST" | "Best brewed from about 5 to 28 days after the roast date printed on the bag" | `product-base/care-tips.md` → Freshness |
| T6 | an instruction, not a claim; it relies on the roast date being on every bag | `product-base/products.md` → Specifications |
| "@example_brewline" | Instagram handle (placeholder) | `channels.yaml` → instagram.url |

**Dropped (no source, or a second idea):** "small batches" (in `passport.yaml`, not in `product-base/`); "12–15
minutes" (true, `roasting-process.md` #2, but it adds a second number to beat 2); "grind just before brewing" (true,
`care-tips.md`; a second tip, so it goes to the caption); "fresher is always better", "stale after 28 days", flavour
words (no source). No prices, no health claims, no people.
`words_check.py --lang en` is expected to flag "best" (T1, T5) and "5 days", "28 days" (T3, T5): each is covered by a
row above. Any other finding means rewriting the line.

## Pattern interrupts
0.00 sweep · 0.20 band flash · 0.95 band off · 1.40 settle · 2.60 drum · 2.90 door · 3.00 pour · 3.80 stir arm ·
5.15 lid · 5.30 tray tips · 5.90–7.90 five hops · 8.80 / 9.40 scoops · 9.85 fold · 10.20 stamp · 11.60 sweep ·
13.80 day 28 · 14.20 back to 14 · 15.00 bag forward · 15.50 handle · hold.

## Later hook lines (0 credits, T1 only; after the jury, if the owner asks)
"Your bag has a best window" · "Tune in to the roast date". Same render, only T1 changes; producer checks them.

## Caption and link (for the publish kit)
Caption: "Look for the roast date on the bag. We rest our beans for 5 days before packing. They are best brewed about
5 to 28 days after the roast date. Grind just before brewing." (sources: roasting-process #4, care-tips → Freshness)
Link in bio: `https://brewline.example/visit?utm_source=instagram&utm_medium=social&utm_campaign=2027-W03&utm_content=REQ-20270118-1-bio`
