---
name: source-skeleton
description: "Source skeleton — indexing any incoming material (video, audio, photos, texts) into a reusable timecoded description before any task is applied to it. Use as the first step for any material."
---

# Source skeleton

**Rule:** first describe what we received, and only then decide what to make of it.
A skeleton is made once per file and reused by all videos.

## Where it lives
`clients/<c>/media-index/assets/<asset_id>/`
- `skeleton.json` — the machine description (schema below);
- `packed.md` — a compact view for LLM reading (this is the main view; there is no need to read the JSON);
- `frames/` — key frames (not committed if heavy; the list of timecodes is kept).
`asset_id` = the first 12 characters of the file's sha1. If it already exists, do not index again.

## Order for video
1. `ffprobe`: duration, fps, resolution, VFR? → if VFR, convert to a CFR copy in `.cache/`.
2. Audio: `ffmpeg -af ebur128` (loudness), `silencedetect` (pauses), clipping.
3. Word-level transcript (faster-whisper cannot open .mov directly because of the PyAV version:
   first `ffmpeg -i in.mov -ac 1 -ar 16000 <abs>/.cache/media/<id>.wav`, then pass the model a
   numpy array; model `small`, cpu, int8, `language=<client language code>`, `word_timestamps=True`): faster-whisper/WhisperX (`word_timestamps`) or ElevenLabs Scribe
   (speakers + events). The language is the client's `passport.yaml: language`.
4. Scenes: PySceneDetect (`detect-adaptive`). If it is not installed — `ffmpeg select='gt(scene,0.3)'`.
5. Key frames: 1 per scene + one every 2–3 s inside long ones. A contact sheet via `tile`.
6. Frame captions: review the frames in batches and describe the shot size (CU/MS/WS/screen/B-roll), what is in frame
   (object, product, detail, people — who), camera movement, quality (sharpness, shake, light),
   on-screen text.
7. Strong moments: hooks, "wow" frames, complete thoughts, emotions → `highlights`.
8. Write `skeleton.json` and `packed.md` and a line in `media-index/index.md`.

## For photos and images
Caption: what is depicted, the object, the angle, quality, a real photo or a visualization, whether it works as a
product reference. For a batch — grouping by object.

## For texts and audio
Theses, facts (candidates for product-base — only after the client confirms), quotes with timecodes.

## skeleton.json schema
```json
{
  "asset_id": "a1b2c3d4e5f6", "source": "yadisk:/phone/IMG_0412.MOV",
  "type": "video", "duration": 184.2, "fps": 30, "res": "1080x1920", "vfr": false,
  "audio": {"lufs": -21.5, "clipping": false, "noise": "wind"},
  "transcript": [{"t0": 12.40, "t1": 12.88, "w": "so", "spk": "S1"}],
  "scenes": [{"id": "s07", "t0": 40.1, "t1": 52.6, "shot": "WS", "caption": "empty plot, a fence on the right, the founder points at the spot",
              "camera": "static", "quality": {"sharp": 4, "shake": 1, "light": 4}, "people": ["founder"],
              "objects": ["plot"], "text_on_screen": null, "usable": true}],
  "events": [{"t": 75.0, "type": "pause", "dur": 2.1}],
  "highlights": [{"t0": 40.1, "t1": 46.0, "score": 4, "reason": "clean static shot — frame A for f04/f05"}]
}
```

## packed.md (example)
```
# a1b2c3d4e5f6 — IMG_0412.MOV — 3:04, 9:16, 30fps, audio: wind
[000.0–012.3] s01 MS the founder at the gate — "This is the plot where the owners want a garden room…"
[040.1–052.6] s07 WS empty plot, static ★ frame A for an insert
...
```
