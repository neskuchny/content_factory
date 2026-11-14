# Human decisions for request REQ-20270118-1 (FICTIONAL demo)

The orchestrator copies the owner's replies here word for word. A row with no date is a decision still due.
Steps 9–16 of `harness.md` do not start without a dated "yes" row for the stop before them.

| Date | Decision | Effect on the harness |
|---|---|---|
| 2027-01-18 | Code film (f18), 0 credits: no generation, no voice, no stock, no people | Flow f18, `budget_credits: 0`; no Higgsfield step; no "AI visualization" badge (nothing is generated) |
| 2027-01-18 | Facts only from `product-base/roasting-process.md` and `product-base/care-tips.md` | `beats.md` → Facts: every on-screen line cites a file; claims without a source are dropped |
| 2027-01-18 | The owner adds `REQ-20270118-1: 0` under `request_credits` in `permissions.yaml` (locked file, owner only) — done | Agents do not edit `permissions.yaml`; the 0-credit limit is now in that file |
| 2027-01-19 | Concept 1 "Freshness dial" (radio tuning dial) chosen out of 3 | `beats.md`, `card.md`, `shotlist.json` describe concept 1; concepts 2 and 3 are dropped |
| 2027-01-19 | One version, 18 s; hook "When is your coffee at its best?" | No sighting variants for this request (the topic already had 3 in W02-R01); other hook lines are listed in `beats.md` for later |
| 2027-01-19 | No music; code-made sounds; the stamp sound is the main hit | `card.md` §7: stamp at 10.20 is the loudest event |
| 2027-01-19 | CTA "Check the roast date on yours" + @example_brewline, plus a small "Fictional demo brand" line on the end card | `shotlist.json → texts_exact` T6, `cta`; the logo layer stays off (no SVG in the demo) |
| 2027-01-20 | Stills (harness step 8), the owner's reply to the 3 questions, as in the demo: "Take it. 1) Yes, the dial in days with the copper band is clear. 2) The roaster pictogram is fine, it does not need to look like our machine. 3) Texts are OK." (`stills/sheet.jpg`, thumbs 0.50 / 10.20 / 17.00) | Step 8 `done`; steps 9–10 may start. Texts, dial metaphor and pictogram stay as they are |
| 2027-01-21 | Draft with sound (harness step 11), the owner's reply to "Pace and sound OK? Shall we render the final?", as in the demo: "Take it. Pace is calm, the stamp is the loudest sound, as I asked. Render the final." (`draft_v1.mp4`, 540x960, -14 LUFS) | Step 11 `done`; step 12 (render) and 13 may start |
| 2027-01-22 | QC: PASS with fixes, jury 7/9 (`production/review.md`). The owner, as in the demo: "Do jury fixes 1 and 2 and the bigger disclosure line; skip the loop-back." | Fixes applied and re-checked (`review.md` → "Re-check after fixes"); the copper day counter is an accepted exception to the copper rule |
| 2027-01-22 | Final in the approval pack (harness step 16), the owner's reply, as in the demo: "Take it." Facts: ✔, AI: no | Publisher prepares a manual kit (`publish-kit`); publishing stays manual (`permissions.yaml`). Telegram: `adaptations/telegram_channel.md` |
