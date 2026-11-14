# Video catalog: formats, flows, tools

> Stage 2. Sources: a voice description of the tasks, research (3 parallel research passes), and a direct
> check of the Higgsfield MCP catalog (`models_explore`). Date: 2026-10-24. **[UNVERIFIED]** marks unverified claims.
>
> Executable flows live in `flows/`, one file per video format. This document is an overview and rationale.

---

## 0. Two rules everything rests on

### Rule 1. Source skeleton first, task second
Any incoming material (video, audio, photos, texts, ideas) is first turned into a
**skeleton**: a reusable description of what we received. The task is applied to it
only after that. Skill: `source-skeleton`.

Why: a one-hour conference recording, described once (who, what is said and when, which topics,
where the strong moments are), yields Reels, Shorts, quotes and posts. A video cut straight "for
30 seconds" cannot be reused.

How this is done in practice (claude-shorts, browser-use/video-use):
- Claude does **not watch** video. It reads a transcript with word timestamps and looks at frames.
  The main "view" for the LLM is a compact `packed.md` (lines like `[012.4–015.9] S1 text`), not JSON.
- Transcript: faster-whisper / WhisperX (free) or ElevenLabs Scribe (about $0.22/hour,
  with speakers and sound events).
- Scenes: PySceneDetect for a rough pass, TransNetV2 for accuracy. Keyframes: 1 per scene plus one every 2–3 s.
- Frame captions: Claude vision in batches. Gemini can watch the whole video (1 frame/s, up to 1 h)
  or use Higgsfield `video_analysis` [UNVERIFIED].
- The skeleton is stored next to the file hash so the file is not indexed twice. Phone VFR → CFR.

### Rule 2. Choose or build the flow (harness) before the work
A complex video cannot be made off the cuff. The director (agent `director`), given the brief and skeleton:
1. picks a standard flow from `flows/`, or **builds a new one on the spot** from the steps
   of the library and writes it to the video's `harness.md`;
2. sets the input, output, check and cost for each step;
3. studio and reviewer then follow the steps strictly. State lives in files, so after
   a failure the work resumes from the unfinished step.

---

## 1. How a task arrives

| Input mode | Example | What the system does |
|---|---|---|
| **Text only** | "A video about how our building handles winter" | No skeleton needed → director picks a flow without source footage (infographic, AI visualization, avatar, film) or requests a shoot brief |
| **Video** | A walkthrough of a site | Skeleton → flow that fits the task |
| **Video + images** | A walkthrough plus a designer's renders | Skeleton of both → match images to moments in the speech → inserts |
| **One long video** | A 1-hour conference | Skeleton → cutting (long→short) |
| **Many short videos** | 10 phone clips | Skeleton of each → assembly (many→one) |

The input channel is a task on the board (Linear: text + attachments) or a folder
`clients/<c>/requests/<REQ-id>/` with `brief.md` and files. The answer is a finished video in the approval pack.

---

## 2. Video formats (flows f00–f17; the later `f18` code film is in `flows/f18-code-film.md`)

Complexity: ● simple (code) · ●● medium (code + 1–2 generations) · ●●● complex (multi-step generation and seams).

| Flow | Format | Essence | Compl. | Key tools |
|---|---|---|---|---|
| `f01` | **Showing with augmented visuals** | A person shows an object; on top: overlay labels, callouts, images, transitions, "what it could look like" inserts | ● | ffmpeg, HyperFrames/Remotion |
| `f02` | **Environment change around a person** | "What if this were a modern style": the whole picture changes, the person stays | ●●● | Kling 3.0 Omni Edit / Kling 4.0 edit / Seedance 2.5 edit + Nano Banana reference frame |
| `f03` | **Video + images sent in** | A team member sent a video and visualizations; the system decides what to insert where | ● | skeleton + matching, code |
| `f04` | **Object appears (B-roll insert)** | Site → frame with a building → "growing" motion → insert into the video | ●● | Nano Banana Pro / GPT Image → Kling O3 First/Last Frame → code |
| `f05` | **Object appears right in the frame** | A building grows next to the person, then the shot returns to reality | ●●● | same + "reality → AI → reality" seam (clip reversal) |
| `f06` | **Interior after renovation + exterior flyover** | A renovation visualization over a walkthrough, then a "drone" shot around the house under the speaker's voice | ●● | edit model, Kling/Cinema Studio/Veo 3.1, J-cut |
| `f07` | **Long → short** | Turn an hour into a 30 s Reels | ● | skeleton, claude-shorts, rubric scoring |
| `f08` | **Many → one** | Assemble a coherent overview from 10 clips | ● | skeleton, story, EDL, loudnorm, LUT |
| `f09` | **Restoration and outpainting** | Clean up, extend the edges, stabilize, recover color | ●● | ffmpeg vidstab/LUT, Kling edit / FLUX 3 Video Edit, Reframe, Topaz |
| `f10` | **Infographic** | Fully drawn / on the client's materials / built from materials | ● | HyperFrames/Remotion, Playwright |
| `f11` | **Comic and cartoon** | A swipe-through with panels (motion comic) or a cartoon | ●● | character-sheet, Nano Banana Pro, Remotion parallax, Seedance/Kling |
| `f12` | **Talking-person edit** | Talking head: pause cutting, subtitles, shot-size changes, cutaways | ● | video-use / ffmpeg, code |
| `f13` | **Digital avatar** | The owner's avatar and voice speak new text without a shoot | ●● | HeyGen Avatar V or Sync Lipsync 3, ElevenLabs |
| `f14` | **Interface video (SaaS)** | Screen, zoom on click, cursor, highlight, interleaved with AI scenes and stock | ●● | Playwright recordVideo, Remotion/HyperFrames, stock (Pexels/Pixabay) |
| `f15` | **Process + extra visuals** | A real process (production, assembly) + 3D, AI fragments, stock | ●● | code + Higgsfield + stock |
| `f16` | **Film video (premium, 60 s)** | As if a studio shot it: dramaturgy, one grade, recurring elements | ●●● | treatment → shotlist JSON → frames → Seedance/Kling/Cinema Studio → grade, grain, sound |
| `f17` | **Product video** | Concept + product photo → ad (realism / cartoon / art) | ●● | product-photoshoot, Seedance @-references, Kling Elements, packshot in code |
| `f00` | **Text only** | Router: picks one of the flows or builds a new one | — | director |

Storyline, hooks and splitting the material into meaningful pieces are not a separate video format but a layer
every flow needs. That is the skill `hook-storyline`.

---

## 3. What the research found (and how it differs from the initial description)

### 3.1 Higgsfield models, verified in the catalog
| Task | Model | Note |
|---|---|---|
| Edit finished video by text + reference | **Kling 3.0 Omni Edit**, **Kling 4.0** (video-edit, 3–30 s), **Seedance 2.5** and **Cinema Studio 4.0** (`video_edit`, 4–30 s), **FLUX 3 Video Edit** (≤15 s, 1 credit/s), Gemini Omni Flash 1.1 (edit ≤30 s) | Edit changes the **whole clip**. A smooth transformation mid-clip is not possible; the transition is built in the edit (wipe / flash / cut on a word) |
| Video between two frames | **Kling 3.0 Omni (Frames)**, 3–15 s; Kling 4.0 keyframes | Basis of "object appears" |
| Video from a frame / references | Seedance 2.0/2.5 (up to 9 images, 3 videos, 3 audio), Kling 3 Omni (up to 7 references), Cinema Studio 3/4 (camera, lens, genre), **Veo 3.1** (4/6/8 s, start frame; not visible in the general list, available by ID), MiniMax H3 | There is **no** Seedance 3.0; the latest version is 2.5 |
| Extend a clip | Seedance 2.5 / Cinema Studio 4.0 `video_extension` | |
| Replace an object / transfer motion | Genjutsu replace object / motion control | |
| Change format 16:9 → 9:16 | Reframe (up to 60 s, 1080p) | Expensive: 30 s at 1080p ≈ 365 credits. For a talking head a face-tracking crop is cheaper |
| Utility | Video Background Remover, SAM 3 Video, Depth Anything Video, Deflicker, FPS boost, Upscale, Topaz | Depth and masks are for parallax and compositing |
| Lips to sound | Sync Lipsync 3 | Best option for dubbing real footage of the owner |
| Images | Nano Banana Pro/2.1, GPT Image 2.5, Seedream 5, FLUX.2 Outpaint, Image Decompose (split into layers), Soul Location | |
| Cloud editing | **Higgsedit** (workflow `video-editing`): timeline, titles, 2.5D camera, shaders, render in the Higgsfield sandbox | Alternative to local ffmpeg/Remotion. No LUT support |

### 3.2 Corrections to the initial description of the flows
- **There is no separate "video-to-video character-locked environment swap" mode.** There are edit models
  (above): they redraw the whole clip from a reference. The scheme for f02: the original and the edited
  version, the same length → wipe or flash transition on the trigger phrase → Lipsync 3 if the lips drift.
- **Going "back to reality" (f05)** is possible with a **reversal** trick. An FLF clip A→B (the building grows)
  is played backwards: B→A, the building "disappears". The last frame of the reversal is exactly
  the real frame A, so the seam into the real video is seamless. The alternative is a whip pan or a cut to another shot.
- **DaVinci Resolve MCP:** Studio 21.1 only (about $295), runs locally on the machine with Resolve.
  Applying LUT and CDL via scripts is possible. "Auto color grading" via MCP is not documented [UNVERIFIED].
  In the cloud, color is done in ffmpeg (`lut3d`, `eq`, `curves`) + color-matcher.
- **Seedance 3.0 does not exist** (the catalog has 2.0 / 2.0 Mini / 2.5).
- **Standard flows are stored as files in `flows/`, not in a database:** they are visible, versioned, and edited via diff.

### 3.3 Techniques that keep the result from looking "AI-made"
1. **Reference frames matter more than the video prompt.** First a perfect still (frame A from the video → frame B with
   the object), check it, and only then the video. 80% of defects are caught at the cheap step.
2. **The seam frame is the exact source frame:** `ffmpeg -ss T -frames:v 1`. Same fps and resolution.
   The first 2–6 "unstable" frames of an AI clip are trimmed.
3. **Masking seams:** a speed ramp over 5–8 frames + whoosh, whip pan, a shared grade and **one grain**
   over real and AI pieces, and color-matching the AI clip to the reference frame.
4. **Generate 5–10 s, use 1.5–3 s in the edit.** A 60 s premium video has 20–30 cuts.
   Plan 3–5 generations per final shot: in a documented project about 25% reached the edit.
5. **Hide AI's weak spots:** close-up hands, text, crowds, liquids, fast head turns →
   framing, shallow depth of field, silhouettes, camera movement instead of object movement.
6. **Text, labels, logos and the final packshot come from code or a real photo**, not from generation.
7. **Sound is half of the "expensive" feel:** room tone, foley, SFX layers, music edited to the beat.
   The generator's native sound is usually replaced.
8. **Morphs give AI away.** Prefer hard cuts, match cuts on shape and movement, start/end frames.
9. **Post-processing in order:** selection → upscale → white balance and contrast normalization →
   creative LUT at 60–80% → light softening of the "AI sharpness" → grain.

### 3.4 Hooks and retention (skill `hook-storyline`)
- The hook is the same in three channels: **what is said, what is seen, what is written**. It is written last.
- Hook types: contradiction, result first, "the mistake everyone makes", visual shock or
  before/after, open loop, a number or a stake.
- A pattern interrupt every 2–4 s: shot change, zoom, text, sound.
- Timings: 15 s: hook 0–2 s → value → CTA; 30 s: 3 / 18 / 6 / 3; 60 s: hook + 3 mini-loops of 15 s + CTA.
- Platform metrics: Instagram looks at watch time, **shares per reach** and likes per reach;
  YouTube Shorts looks at "viewed vs. swiped away". Industry figures for drop-off in the first 1–3 s (30–50%) are [UNVERIFIED].
- Hypothesis to test per client: videos watched past 15 s generate leads, very short ones (under 10 s) rarely do. Check it against the client's own metrics.

### 3.5 Style memory (skill `style-memory`)
- `brand/tokens.json`: colors, fonts, radii, easing, durations, safe-zone grid.
- Component library: badge, callout, titles, transition, CTA, "AI visualization" badge.
- `manifest.json` per video: a timeline of references to components and skeleton fragments.
  This makes a video reproducible.
- **Golden references:** when a person says "I like this because…", the manifest, prompts,
  models, seeds and presets are saved to `brand/golden/<name>/` together with the reason. The next video
  in this series is built from the snapshot.
- **A memorable element** (the brand's recurring device) is a separate entry in `brand/visual.md`,
  mandatory for the series.
- **The logo is a switchable layer** (`logo.enabled`) + an export without text for localizations.
- AI B-roll breaks stylistic unity → the brand kit fixes a prompt prefix, references and a shared LUT.

### 3.6 Avatar, voice, consent
- HeyGen Avatar V: a double from 15–30 s of video, but in practice it is better to shoot 2–5 minutes. A recorded consent is required.
- Sync Lipsync 3 (available in Higgsfield): over **real** footage of the owner it is more realistic than an avatar from scratch.
- ElevenLabs: a professional voice clone needs 30+ minutes of clean recording, an instant one 1–2 minutes.
  Check the supported languages for the client's `language`; for `ru` clients Russian is supported, but check stress placement on a test text.
- Keep the avatar on screen no more than 3–5 s at a time, then B-roll.
- AI-content labeling rules vary by jurisdiction. Russia: since July 2026 labeling of AI content is **voluntary**, a bill making it mandatory is in the Duma.
  EU: mandatory since 2026-08-02. Our rule is to always label.

### 3.7 Stock and screens
- Pexels (free, 200 requests/h), Pixabay (cache responses for 24 h, no bulk
  downloading), Storyblocks (official MCP, subscription). Store the ID and license of every clip in the manifest.
- SaaS recording: Playwright `recordVideo` + a click-coordinates log → zoom and cursor in code (deterministic).

---

## 4. Tools: who is responsible for what

| Node | Tool | Role |
|---|---|---|
| Orchestration, agents, code | **Claude Code** (cloud tasks / server / manual) | Reads CLAUDE.md, skills, flows; writes the editing code; calls MCP |
| Editing in code, graphics, UI | **HyperFrames** (main, free), **Remotion** (license for companies of 4+ people), ffmpeg | Titles, badges, callouts, transitions, seams, infographics, motion comic, assembly |
| Editing in the Higgsfield cloud | **Higgsedit** (`video-editing`), `video-montage` | When rendering on the Higgsfield side is needed |
| Heavy editing and color | **DaVinci Resolve Studio 21.1 MCP** (optional, local) | LUT, render, project organization. Without Studio, ffmpeg |
| Video generation and editing | **Higgsfield MCP**: Kling 3/4 (+ Omni Edit, Frames), Seedance 2.0/2.5, Cinema Studio 3/4, Veo 3.1, Genjutsu | Scenes, A→B transitions, environment edits, flyovers |
| Images and outpainting | Nano Banana Pro/2.1, GPT Image 2.5, Seedream 5, FLUX.2 Outpaint | Frames B, interiors, product angles |
| Avatar and voice | Sync Lipsync 3, ElevenLabs (via Higgsfield), HeyGen (optional) | Talking double, dubbing |
| Video understanding | whisper / Scribe + ffmpeg frames + Claude vision; optionally Gemini, Higgsfield `video_analysis` | Source skeleton |
| Cutting | claude-shorts (MIT), video-use (MIT) | Long→short, talking head |
| Stock | Pexels, Pixabay, Storyblocks MCP | Cutaways |
| Claude Cowork / OpenAI | Cowork is a desktop app, not confirmed on a server; Codex CLI is an alternative executor and supports the same HyperFrames and Remotion skills | Optional |

---

## 5. Sources (key)
- Model catalog: Higgsfield MCP `models_explore` (verified 2026-10-24); workflow `video-editing` (Higgsedit)
- [browser-use/video-use](https://github.com/browser-use/video-use) · [claude-shorts](https://github.com/AgriciDaniel/claude-shorts) · [HyperFrames](https://github.com/heygen-com/hyperframes) · [Remotion props](https://www.remotion.dev/docs/passing-props)
- [Gemini video understanding](https://ai.google.dev/gemini-api/docs/video-understanding) · [ElevenLabs API pricing](https://elevenlabs.io/pricing/api) · [Scene detection benchmark (Cosmos)](https://arxiv.org/pdf/2501.03575)
- [Kling O1 prompt guide (fal)](https://fal.ai/learn/devs/kling-o1-prompt-guide) · [Kling 3.0 Omni upgrade](https://www.atlascloud.ai/blog/guides/kling-3-0-omni-upgrade) · [Runway Aleph: changing environments](https://academy.runwayml.com/aleph/change-environments-with-aleph) · [Kling 4.0](https://fal.ai/learn/tools/what-is-kling-4-0)
- [AI ↔ real video transitions (invideo)](https://invideo.io/faq/how-do-you-make-transitions-between-ai-generated-and/) · [Blending with live action](https://invideo.io/faq/how-do-you-blend-ai-generated-shots-with-live-action/) · [How to make AI video look less artificial](https://www.atlabs.ai/blog/how-to-make-ai-videos-look-less-artificial-in-2026-(step-by-step-guide))
- [AI drone (Kling)](https://kling.ai/topics/ai-drone-video) · [Kling Start/End Frames](https://higgsfield.ai/blog/Kling-Start-End-Frames)
- [Shot length limits Seedance/Kling](https://invideo.io/blog/seedance-kling-shot-length-limits/) · [AI shot list (Runway)](https://runway.com/resources/ai-shot-list) · [Shot list template (Magic Hour)](https://magichour.ai/blog/ai-video-shot-list-template) · [LUTs and grain](https://invideo.io/blog/luts-film-grain-ai-video/) · [Seedance 2 vs Kling 3 (fal)](https://fal.ai/learn/tools/seedance-2-0-vs-kling-3-0) · [PJ Accetturo (Saturation)](https://saturation.io/podcast/episode/pj-accetturo) · [Hedra: AI advertising](https://hedra.com/blog/ai-generated-advertising)
- [Sync-3](https://sync.so/docs/models/sync-3) · [HeyGen Avatar V](https://community.heygen.com/public/resources/how-to-get-the-best-results-with-avatar-v-in-heygen) · [ElevenLabs voice cloning](https://elevenlabs.io/voice-cloning) · [AI labeling in Russia (dp.ru)](https://www.dp.ru/a/2026/08/19/markirovku-ii-kontenta-v-rossii) · [EU AI Act Art. 50 (Baker McKenzie)](https://connectontech.bakermckenzie.com/new-eu-guidance-on-ai-transparency-what-should-companies-be-doing-from-2-august-2026)
- [Comics with Nano Banana Pro](https://anifusion.ai/blog/mastering-nano-banana-pro-comic-manga-generation/) · [Character sheet](https://invideo.io/faq/how-do-you-create-a-character-reference-sheet-using-nano/) · [Product photo → Seedance (Opus)](https://www.opus.pro/blog/product-photo-to-commercial-seedance) · [Seedance 2.5 product ad (Kapwing)](https://www.kapwing.com/resources/how-to-turn-a-product-photo-into-an-ai-product-ad-with-seedance-2-5/)
- [Pexels license](https://help.pexels.com/hc/en-us/articles/900005852323) · [Pixabay API](https://pixabay.com/api/docs/) · [Storyblocks MCP](https://www.storyblocks.com/resources/?p=36413) · [DemoForge](https://peerlist.io/dixitram/project/demoforge)
- [Resolve 21.1 MCP (Digital Production)](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/) · [YMCinema](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/) · [VOID video inpainting](https://letsdatascience.com/news/netflix-releases-void-video-inpainting-model-99ea59e8) · [Wan VACE inpainting](https://www.comfy.org/workflows/video_wan_vace_inpainting-a1bb55d904c9)
