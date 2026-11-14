# Sound audit: REQ-20270118-1 "Freshness dial" (FICTIONAL demo)

Idea (`card.md` section 7): each object sounds like what it is, and the lit band has its own warm tone. Every sound is
placed from `data/timeline.json` and `data/bean_events.json`, so it starts on the frame of its event. No music, no voice,
no whooshes. Layers: room (R), click (C), tone (T), mech (M), beans (B), hit (H).

| Event (time) | Sound | Layer |
|---|---|---|
| room, whole film | filtered noise, -45 dBFS RMS; the tail is never digital zero (RMS -38 dBFS at 17.8-18.0 with the tone) | R |
| 73 needle detents: 3 + 23 + 5 on the hook sweep 0.00-1.40 (31 with the settle), 5 hops 5.90 / 6.40 / 6.90 / 7.40 / 7.90, 23 glide 11.60-13.80, 14 back 14.20-14.80 | one click per integer day crossed (noise tick + 2 kHz ring + 190 Hz knock), panned with the needle; the day-0 detent is the settle tap | C |
| 1.40 needle settles on day 0 | settle tap: 165 to 95 Hz knock + tick (second loudest) | C |
| 0.20-0.95 and 11.60-18.00 band lit | warm tone D4 + A4, sine partials, attack 80 ms, release 30 ms; on the same frames as `band_lit` (215 tone frames vs 214 lit frames, one frame of offset at 11.60); 17.40-18.00 fades to -30 dB | T |
| 2.60-4.40 drum | rumble 55-130 Hz noise, level follows the spin speed, modulated by the six spokes | M |
| 2.90 / 4.40 door | wooden clack (softer on closing) | M |
| 3.00 beans start | first rush (band noise 350-1500 Hz) = third loudest event; then one grain tick per bean at the door and at the tray, rattle on the chute that follows the number of beans on it | B |
| 3.80-5.10 stir arm | soft scrape, level follows the arm speed | M |
| 5.15 / 5.85 bin lid | wooden tap | M |
| 5.34-5.78 tray tips | ticks as beans slide off, dull thuds into the bin | B |
| 8.60 / 9.70 bin lid | wooden tap | M |
| 8.71 / 9.19 scoop dips | grainy scrape; 8.92-9.04 and 9.40-9.52 patter of 12 grains on paper | B |
| 9.85-10.00 bag top folds | paper crinkle | M |
| 10.20 pad hits the label | STAMP THUNK: body 150 to 78 Hz + sub 46 Hz + paper slap = loudest event | H |
| 10.30 lever swings up | spring | M |
| 15.00-15.80 props slide out, bag comes forward | paper scuffs, level follows each object's speed (brand curve); no whoosh | M |

Measurements (`sound_measure.json`): BS.1770 integrated -14.0 LUFS before `loudness.py` (it then applies -0.55 dB);
limiter ceiling -1.4 dBFS, maximum gain reduction 7.2 dB; true peak after `loudness.py` -1.1 dBTP.
Loudest events by intended level: stamp 10.20, settle 1.40, pour 3.00, then the dense clicks. Effects-only RMS in the
250 ms from the event: stamp -15.0, pour -15.5 (the drum rumble is under it), settle -17.4 dBFS.

Deviation from the card: the card puts the tone 10 LU under the effects. With -14 LUFS and -1 dBTP for an 18 s film with
sparse hits, the sustained tone has to carry the loudness: it sits at about -15 dBFS RMS (peak -6 dBFS), the same level as the
effects' 250 ms RMS, and about 5 dB under the stamp's peak. `director` may ask for a quieter tone and a lower master.
