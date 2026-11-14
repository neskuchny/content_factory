---
name: sound-design
description: "Sound design for videos — where to get music and sound effects (Openverse, Epidemic Sound, generation), how to check licenses for a commercial client, how to keep the client's sound library, and how to place sounds along the edit. Use at the audio_mix step of any video and when building a signature sound."
---

# Sound design

Sound is half of the "expensive" feeling. Without it a video looks like a slideshow; with bad or
"stocky 2010s" sounds it looks cheap.

## 1. Where to get it (in order)
| # | Source | When | Price | Quality | License |
|---|---|---|---|---|---|
| 1 | **Client library** `clients/<c>/brand/sounds/<tag>/` | Always first: signature sounds repeat from video to video and become the "memorable element" | 0 | verified | already recorded in the sound passport |
| 2 | **Openverse** (`scripts/media/openverse.py`) — 5M+ sounds and music (Freesound, Jamendo, Wikimedia…), search with license and length filters | Effects (whoosh, click, glass, metal, assembly), ambiences, simple music | 0 | fine for social media and promo, not for TV | **CC0 and CC BY only** |
| 3 | **Epidemic Sound MCP** (beta, official) — 55k tracks, 250k effects, trimming a track to length, search by mood/BPM/reference | Flagship videos, brand films, when a "studio" sound is needed | paid subscription; search is free, download requires the subscription | high | per the terms of the subscription and the **workspace**; for client work — Business plan, check the terms |
| 4 | **Generation** in Higgsfield: `mirelo_text_to_audio` (effects), `sonilo_music` (music), ElevenLabs (voice) | An exact sound for a specific on-screen event that libraries do not have | credits | varies; risk of "AI slop" | per Higgsfield terms |
| — | Mixkit | Not by default: a small and outdated selection | 0 | — | — |

## 2. Licenses (commercial client)
- Use **CC0** (no conditions) and **CC BY** (attribution required). The script filters out everything else.
- **Do not use:** NC (non-commercial — ours is advertising), ND (no derivatives — we cut and process),
  SA (share-alike — requires the same license for the video).
- Next to every sound lies a passport `<file>.json` (author, license, link, attribution line).
  Studio carries it into the video's `manifest.json` → `audio[]`.
- For CC BY the attribution line goes into the publication caption or description (adapter/publisher take it from the manifest).
- Music with recognizable melodies and "brand sounds" (ringtones, jingles) — do not use.

## 3. Working with Openverse
- `python3 scripts/media/openverse.py search "<what>" --max-sec 3 [--category sound_effect]` — a list with id, license, length.
- Listen (download to a temporary folder) and choose; then
  `python3 scripts/media/openverse.py get <id> --client <c> --tag <seam|assemble|ambience|music|ui>` —
  the sound goes into the client library with a passport.
- Anonymous access: 20 requests/min, 200/day; with a free key (an e-mail is required) — 100/min, 10,000/day.
  Key: `OPENVERSE_CLIENT_ID` / `OPENVERSE_CLIENT_SECRET` in the environment (a cloud-environment secret), not in the repository.
- ⚠️ From the cloud environment the service responds unreliably (as of 2026-10-27 new requests often return 504 after ~60 s).
  So: search ahead of time and in batches, responses are cached in `.cache/openverse/`, put what you need straight into the client library.

## 4. Placing sound
1. **Layers:** ambience (quiet, the whole video) → music → accent effects → voice.
2. **Accents are tied to edit events** from the timeline (`manifest.json`): a cut/seam — whoosh;
   a badge appearing — a soft click; the "assembly" of a structure — a series of metal/glass sounds in time with the growth;
   the finale — a short "hit" under the CTA.
3. **Music** is trimmed to the video's length (not cut off), the edit follows the beat; under voice — lower it by 8–12 dB (ducking).
4. **Loudness:** −14 LUFS integrated, peak ≤ −1 dBTP (`ffmpeg loudnorm`). Do not use the audio from video generators (Kling etc.).
5. **Less is more:** 1 effect per event, no "carpet" of swooshes. Check by listening on a phone.
6. A successful sound approved by the human is saved as signature (`brand/sounds/` + an entry in `brand/visual.md` → "Memorable element").
