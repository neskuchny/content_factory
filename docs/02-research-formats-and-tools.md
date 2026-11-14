# Content factories: types, formats, tools

> Stage 1.2 — continuation of `01-research-content-factory.md`.
> Date: 2026-10-24. The **[UNVERIFIED]** mark means the source is marketing material or a single mention.
> Prices in ₽ (rubles) are the Russian-market figures claimed by the sources.

---

## 1. What kinds of content factories exist (market models)

"Content factory" in 2026 is an umbrella term. The following models actually occur:

| Model | How it works | Economics (as claimed by the market) | Strong / weak |
|---|---|---|---|
| **1. "Expert + team" (repackaging)** | The expert films long-form (podcast, livestream, interview), the team cuts it into shorts and posts | from 100k ₽/month; 1 hour of filming yields 10–20 units | Personal brand, but the expert is the bottleneck |
| **2. Digital twin** | An avatar of the expert built from one recording with consent "films" in their place | 100–200k ₽/month + a one-off setup (Eco-OS: +290k ₽) | 3+ videos a day with no filming; needs a high-quality setup |
| **3. AI blogger / character / mascot** | A fictional character runs the account | 100–300k ₽/month | Scales without people, but does not build a personal brand |
| **4. UGC factory** | Dozens of micro- and nano-bloggers (real or AI) film to a brief | 1,500–3,000 ₽ per video, record 300 ₽ **[UNVERIFIED]** | +38 % conversion vs studio creatives **[UNVERIFIED]**; creator rotation |
| **5. Clip factory / clipping** | Mass cutting of long video, uniquification | $500–1,500/month per client **[UNVERIFIED]** | Cheap; mass re-posting leads to shadow bans |
| **6. Account media network** | The same content spread across many accounts | — | Reach; ban risk, register accounts in your own name |
| **7. Faceless channels** | Script + voice-over + visuals with no face (explainers, stories, documentaries) | — | Works, but YouTube cuts "mass repetitive" content |
| **8. AI series** | A bet on reach, not on sales | about 400 ₽ per video **[UNVERIFIED]** | Reach, but weak conversion |
| **9. Ad creative factory** | Generation and multiplication of ad variants for A/B testing | — | This is where AI gives the clearest ROI |

Key market observations:
- Models **combine** (UGC + AI + clipping + network).
- Skeptics write that "there are no proper cases with confirmed sales among purely AI factories"
  **[UNVERIFIED]**. AI works as a **production accelerator given a strong script**, as a video hook,
  a mascot, and a replacement for expensive promo production.
- **Does not work:** mass uniquification and re-posting of old videos.

---

## 2. Case study: Eco-OS / "AI Pushka" — the "sighting month"

This is the live product closest to our task. The figures are the seller's claims **[UNVERIFIED]**,
but the **methodology** is very valuable.

**Offer:** 90 units a month (75 reels + 15 carousels) for B2B services (construction and others).
Price 99k ₽ for a pilot, then 180k ₽/month. From the client: a 1-hour interview and 1–3 hours
of voice messages or takes per month.

**The "sighting round" methodology** (worth adopting as the basis):
1. **Aim:** find the buyer's pain and name it in the first phrase.
2. **Volume → measurement → amplification:** each topic gets **3–5 variants**, and they differ
   completely (hook, cover, editing, length, ending), not only in the first line.
3. **Weekly phases:**
   - week 1 — the "fork" (a wide spread of topics);
   - week 2 — refining the winners;
   - weeks 3–4 — scaling the winners and new variants.
4. **Source of hooks:** the client's interview and real objects, plus formulas from what is already
   "taking off" for the client and on the market.
5. **Retention:** see where the viewer drops off and fix that moment.
6. **The month's result is the "targeting map":** which topics, hooks, designs and lengths brought buyers.
   This is the **factory's memory**.
7. **Client interface:** the week's plan, 3–5 variants per video, **"Take it" / "Not this"** buttons,
   comments. This is exactly our human gate.

**Numbers that change priorities** (data **[UNVERIFIED]**):
- The simplest format (white text + subtitles) produced the most leads.
- Videos watched through for 15+ s: 40 of them brought 178 leads. Videos under 10 s: 158 of them — 15 leads.
- "Prophecy-threat": 18 posts, 135 leads. Tutorials: 45 posts, 6 leads. Cases with screenshots: 11 posts, 0 leads.
- One script in different designs: 167k vs 16.6k views.
- Pilot: out of 96 reels, 79 got fewer than 3,000 views, 5 "shot up" (up to 208k).
  **A factory is a lottery with a controlled number of tickets.**

**Their formats:** cartoons, infographics, comics, sketches, serious breakdowns, classic
(text + subtitles), carousels, digital twin, voice-to-infographic, quote clips from
popular interviews.

**Takeaway for us:** the main value of their product is not generation but the **"fork →
metrics → amplification" cycle with a targeting map**. Our orchestrator and feedback agent
should work exactly this way.

---

## 3. Four production "engines"

To the question "Claude on its own, skills on their own, Higgsfield on its own — what else?" the answer is:
a factory has **four classes of engines**, and each format is assembled from a combination of them.

### 3.1 Plain Claude — video and graphics in code
The trend of autumn 2026: Opus 5.5 does motion design **in code** (HTML/CSS/GSAP/Canvas/Three.js
or React). Headless Chrome renders the frames, ffmpeg assembles the MP4. Claude looks at the frames itself
and corrects them. This is also confirmed by the example in the source description: a 90 s video in 40 minutes, about 50 %
of the session limit on Pro.
- **Works even without skills** — the model knows GSAP, Canvas and ffmpeg. But with skills
  the result is steadier and reproducible.
- The prompt from the description is essentially: "download and break down the references frame by frame → copy the
  visual system → topic from the post → free TTS, music, SFX → balance the volume → document the project".
- **Best suited for:** explainers, infographics, kinetic typography, branded intros, data, carousels
  (HTML → PNG via Playwright).
- **Weak at:** photorealism, people, real products in scenes.

### 3.2 Skills and plugins for Claude Code
| Skill / tool | What it does | Installation |
|---|---|---|
| **HyperFrames** (HeyGen, Apache 2.0) | HTML + GSAP → deterministic MP4; about 450 blocks; `/media-use` for VO, music, SFX | `npx skills add heygen-com/hyperframes` or the plugin |
| **Remotion Agent Skills** (official) | React video, templates with JSON data, subtitles | `npx skills add remotion-dev/skills`; ⚠️ paid for companies of 4+ people |
| **Anatomy** | Interactive isometric "explainer machines" (SVG / WebGL / 3D) from a single line | `npx skills add wheresryan22/anatomy` |
| **claude-shorts** (MIT) | Clipping: faster-whisper → Claude scores candidates → human picks → FFmpeg → Remotion 9:16 | GitHub AgriciDaniel/claude-shorts |
| **video-use** (browser-use) | Footage editing from a word-level transcript: pauses, fillers, grade, subtitles | Needs an ElevenLabs Scribe key |
| podcli (AGPL, MCP), goose-skills video-clipper | Alternatives for clipping | — |
| Social Canvas, Instagram Carousel Maker, Open Carrusel | HTML → PNG carousels with self-checking | — |
| skill-creator (anthropics/skills) | Creating the factory's **own** skills | Built in |
| Kokoro-82M, Edge TTS | Free local voice-over | — |

### 3.3 Higgsfield (MCP, already connected)
**About 100 models:**
- images: Nano Banana Pro/2, GPT Image 2.5, Seedream 5, FLUX, Soul 2.0, Recraft,
  Ideogram, **Image Decompose**, Outpaint, Topaz;
- video: Kling 3/4, Seedance 2/2.5, Cinema Studio 4.0, MiniMax, Wan, Grok,
  Genjutsu (motion control / replace object), Sync Lipsync 3, Reframe, Upscale,
  background removal, Dubbing;
- audio: ElevenLabs v4, Seed Audio, Sonilo music;
- 3D: Image to 3D, Rigging.

**13 ready-made workflows** (effectively ready-made skills):
- `faceless-video` — explainer, story, kids' content, picture story, fairy tales, with voice-over and subtitles;
- `ugc-video` — review, unboxing, try-on, tutorial, website tour, product voiceover;
- `ad-multiplier` — 10 versions of one ad, re-shoot for another market or cast;
- `ads-studio` — static ads from the brand's website;
- `product-photoshoot` — packshot, lifestyle, carousels, try-on;
- `brand-asset-creation` — logo, identity, merch, banners, decks;
- `character-sheet` — consistent characters;
- `thumbnail-generation` — covers;
- `narration` — "insert me as the narrator into this video";
- `video-montage` — joining, soundtrack, subtitles;
- `video-editing` — editing and motion graphics in Higgsedit;
- `katana` — remix from a reference video;
- `website-builder-flow`.

Plus `virality_predictor` (virality forecast, retention, hook strength) and `video_analysis`.

**Best suited for:** photorealism, people, products, UGC, ads, cinematic shots.

### 3.4 Other: what else exists
| Tool | Purpose | Limitations |
|---|---|---|
| **DaVinci Resolve 21.1 — official MCP** (since September 2026) | Claude / Claude Code / Codex controls the project: timeline editing, media, batch render, color grading | ⚠️ **Studio only** (about $295); does not work on Free. Community alternative — samuelgursky/davinci-resolve-mcp |
| **Codex CLI `$imagegen`** (gpt-image-2) | Images on a ChatGPT subscription with no API key | "Claude → Codex" bridges are a ToS gray area |
| **HeyGen** (Avatar IV/V) | Digital twin with a built-in consent procedure | Paid |
| **ComfyUI** | Product placement, SeedVR2 (video restoration), local pipelines | Needs a GPU |
| **Topaz** | Gentle restoration and upscaling | Subscription $33–67/month |
| **Blender + MCP**, **Manim** | 3D breakdowns, math and data | Entry barrier |
| **Postiz** | Auto-posting | — |
| Opus Clip / Vizard / Napkin | SaaS for clipping and infographics | External dependency |

---

## 4. Format matrix: how to make each one

Legend: **C** — Claude code (HTML/Remotion/HyperFrames/ffmpeg), **S** — skill,
**H** — Higgsfield, **O** — other.

| # | Format | Simplest working path | Engine | Main pitfalls |
|---|---|---|---|---|
| 1 | **Showcases** (product, 360°, runway, real-estate property) | Remove the background and upscale the photo → studio shot → image-to-video (one movement per clip, 5–10 s) → joining, price, CTA in Remotion. Real estate: push-in on each photo or first/last frame along the buyer's route | **H** + **C** | AI invents the back side in 360° (real angles or Image to 3D are needed); lettering "floats"; must not show what is not in the property |
| 2 | **Clipping** | The claude-shorts skill: whisper → Claude scores 8–12 candidates → human picks → cut on word boundaries → 9:16 with face tracking → animated subtitles | **S** + **C** (H: `virality_predictor` for ranking) | Cut on word and silence boundaries; tracking holds two speakers in frame poorly; Higgsfield's shorts_studio is not for long video |
| 3 | **Visuals around an object** | Remove background → edit model (Nano Banana) with the product as a reference, 3–4 scenes → selection → relight / upscale → optionally image-to-video. A simple composite (product over a background plus text) — in code | **H** (`product-photoshoot`) / **C** | Redrawn logo and proportions, light does not match the scene |
| 4 | **Restoration / outpainting** | Scan → moderate upscale → edit "restore, keep identity" → outpaint for edges and format change; video: cleanup → ×2 upscale. Keep the original | **H** (+O: Topaz, SeedVR2) | A generative model **predicts**, it does not restore: faces "change", human review is needed |
| 5 | **Splitting into parts** (exploded view, anatomy) | Concepts: the **Anatomy** skill. Product: 2 frames (assembled / disassembled) → Kling start/end frame. Precise engineering: three.js from a GLB with parts | **S** / **H** (+Image Decompose) / **C** | AI invents the insides of a real product — check against the schematic; video "melts" small details |
| 6 | **Infographics** | Static: Claude lays out HTML/SVG → Playwright to PNG 1080×1350. Animated: a Remotion or HyperFrames template + JSON with data. Voice-to-infographic: transcript → structure → the same pipeline | **C** + **S** | **Numbers and text only in code**, not by generation; Cyrillic fonts, line breaks |
| 7 | **Comics** | `character-sheet` → one panel per call with a reference → Claude lays out the page and speech in HTML/SVG. Animated — pan and zoom in Remotion | **H** + **C** | Models hold more than 2 characters in frame poorly; text in the image is unreliable — speech bubbles in code; a character "bible" in every prompt |
| 8 | **Putting a person into the edit** | Photo of the person + reference clip → Genjutsu / motion control → voice via `create_voice` or `dubbing` → assembly. Talking head — `narration` or a HeyGen twin | **H** (+O: HeyGen) | **The person's consent is mandatory** and is stored; deepfake labeling (EU AI Act Art. 50 from 02.08.2026); one character per frame; hands, occlusions |
| 9 | **Storyline** (series) | "Bible" (characters, locations) → beat list and shot list as JSON (Claude) → master portrait of each hero → frames with references → image-to-video per frame | **C** (script) + **H** | A character "drifts" after 3–4 shots; two people in frame get mixed up |
| 10 | **Film** | Script → shot list → references → keyframes (Nano Banana Pro) → image-to-video (Seedance / Kling / Cinema Studio) → ffmpeg concat → VO, SFX, music. A `shot_NN/` folder per shot | **C** (orchestration) + **H** | Video generation is the most expensive part, catch errors at the keyframe stage; dialogue and lip sync are weak |
| 11 | **Object video** (product / UGC) | `ugc-video` or `ads-studio` from a photo or URL → `ad-multiplier` for variations → price and CTA badges in code | **H** + **C** | Distortion of packaging and logo, check every frame; labeling of AI UGC |
| 12 | **Brand video** | Brand book → tokens (colors, fonts, SVG logo) in Remotion or HyperFrames → kinetic typography and logo reveal in code → atmospheric B-roll via Higgsfield → voice and music | **C** + **S** (+H for B-roll) | The logo **always** from SVG in code (it flickers in generation); an editable project is worth more than a "baked" mp4 |

### Cross-cutting rules (derived from all the formats)
1. **Text, numbers, logos, prices — only in code.** Generative models distort them.
2. **Frame first, then video.** Errors are caught at the cheap stage (keyframe), not at the
   expensive one (video).
3. **The project "bible"** — references for characters, locations, product and brand tokens —
   is the single source for all agents.
4. **Short clips + joining** are more reliable than long generation.
5. **A human checks** restoration, inserting people and real products — that is where AI
   "invents".
6. **Consent and labeling** for everything that involves real people.

---

## 5. Review of another agent's architecture: what is right and what to fix

The other agent's scheme (CLAUDE.md + skills + MCP, roles, weekly cycle) **broadly matches**
best practice and our first document. Needed clarifications:

| Item in the scheme | Correction |
|---|---|
| "A server with Claude Code / Claude Cowork" | **Cowork is a desktop app.** There is no confirmation that it can be run headless on your own Linux server. For a server — **Claude Code** (VPS + tmux/systemd) or Claude Code **cloud sessions and scheduled tasks** with no server at all |
| "Searcher on Sonnet 3.5" | The model is outdated → Haiku 5.5 or Sonnet 5.5 |
| "Telegram as an entry point" | Channels deliver messages **only to an open session** → a permanently running process is needed. Alternative — Remote Control from the Claude app |
| "Cron on the server" | Cloud scheduled tasks: no more often than hourly, up to 100 runs an hour, work without your own server, see connectors. Your own cron is needed only if you need your own server |
| "A DB for variables" | To start, **files in git** (`config/*.yaml`) are better: versioning, rollback, readability, review of the feedback agent's edits via diff. A DB (Supabase) — when a UI for the client or analytics appears |
| "Google Drive for creatives" | Fine for media files and for the client. Texts, plans and memory — in git |
| "Remotion for motion" | Add **HyperFrames** (Apache 2.0, free for business; Remotion has a paid license from 4 people) |
| "A video-editor MCP" | Specifically: **DaVinci Resolve 21.1 MCP (Studio only)** or ffmpeg / video-use / Higgsfield `video-montage` with no licenses |
| "The reviewer agent is simple" | The reviewer **must** be able to tell good from bad (otherwise evaluator-optimizer closes on itself). It needs criteria, golden references and at least a mid-tier model with vision. Plus `virality_predictor` as an objective metric |
| No metrics in the loop | Add the **"fork → metrics → amplification"** cycle and the **targeting map** from the Eco-OS methodology — this is the main quality engine |
| No variety | Add **3–5 fully different variants per topic** (hook, cover, editing, length) |

---

## 6. Conclusions for the design

1. **The core of the factory is the "sighting round" cycle, not generation:** a fork of topics → 3–5 variants → metrics →
   amplifying the winners → targeting map (memory).
2. **Routing by engine:** the orchestrator picks an engine (C / S / H / O) for each content unit
   from the matrix in section 4. The matrix lives in config, not in a prompt.
3. **The cheapest and most "lead-generating" format is the simple one** (text + subtitles,
   clips, infographics in code). We build it first and in the largest volume. Expensive
   generative formats — selectively, for proven topics.
4. **Starting set of machines:** Claude code + HyperFrames/Remotion + claude-shorts +
   Higgsfield (the ugc / faceless / product-photoshoot / ad-multiplier / character-sheet workflows) +
   Anatomy. DaVinci MCP — an option if you have Studio.
5. **Mandatory gates:** checking text and numbers (code only), human checking of people and products,
   consents, AI labeling.

---

## Sources

Sources marked (RU) are in Russian.

**Factory models and cases**
- [Content factory in 2026: models and AI bloggers — Sostav (RU)](https://www.sostav.ru/blogs/283819/76646)
- [Content factory: types, economics, cases — Sostav (RU)](https://www.sostav.ru/blogs/288206/81161)
- [UGC factory — Sostav (RU)](https://www.sostav.ru/publication/ugc-zavod-rost-biznes-metrik-cherez-sistemnuyu-rabotu-s-ugc-kontentom-82334.html)
- [A content factory made of bloggers — eLama (RU)](https://elama.ru/blog/kontent-zavod/)
- [AI Pushka / Eco-OS — content sighting round (RU)](https://eco-os.ru/p/c8p4-kontent-pristrelka)
- [3 business models for AI video in 2026 — AI Fire](https://www.aifire.co/p/3-profitable-business-models-for-ai-video-in-2026-a-guide)
- [Faceless YouTube 2026 — Aliteq](https://aliteq.com/make-money-faceless-youtube-ai-2026)
- [Faceless and UGC with Higgsfield Skills](https://higgsfield.ai/blog/faceless-videos-ugc-ads-2026)

**Video in code / Opus 5.5**
- [Prompt for Opus 5.5 — @tips_ai (RU)](https://telegra.ph/Promt-dlya-Opus-55-09-28)
- [Claude Code motion graphics with Opus 5.5 — Charlie Hills](https://charliehills.substack.com/p/claude-code-motion-graphics)
- [awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos)
- [HyperFrames — HeyGen](https://github.com/heygen-com/hyperframes)
- [HyperFrames + Claude Code](https://themenonlab.blog/blog/hyperframes-claude-code-writes-renders-videos)
- [Remotion Agent Skills](https://www.remotion.dev/docs/ai/skills)
- [video-use for editing](https://themenonlab.blog/blog/video-use-ai-video-editing-claude-code-agents)
- [Anatomy skill](https://skills.wheresryan.sh/anatomy)

**Formats**
- [claude-shorts](https://github.com/AgriciDaniel/claude-shorts) · [podcli](https://mcpservers.org/ru/servers/nmbrthirteen/podcli) · [goose video-clipper](https://www.skills.sh/gooseworks-ai/goose-skills/video-clipper) · [autoclip](https://github.com/artbyjazi/autoclip)
- [AI video for e-commerce](https://oakgen.ai/blog/ai-video-ecommerce-guide) · [AI for real estate — Invideo](https://invideo.io/blog/how-to-create-real-estate-videos-using-ai/) · [Kling try-on](https://kling.ai/topics/try-on-clothes-online-ai)
- [Product Placement — ComfyUI](https://www.comfy.org/workflows/template_product_placement-723870e886d7/) · [UGC Factory explained](https://higgsfield.ai/blog/Higgsfield-UGC-Factory-Explained)
- [Restoration with Nano Banana 2 — arXiv 2604.03061](https://arxiv.org/abs/2604.03061) · [Video upscale — ComfyUI](https://docs.comfy.org/tutorials/utility/video-upscale)
- [Kling start/end frames](https://higgsfield.ai/blog/Kling-Start-End-Frames) · [Exploded view prompt](https://llmbase.ai/prompts/legebdary-exploded-view-prompt-for-nanobanana)
- [Open Carrusel](https://github.com/Hainrixz/open-carrusel) · [Social Canvas](https://claudskills.com/skills/social-canvas/)
- [Comics with Nano Banana Pro](https://anifusion.ai/blog/mastering-nano-banana-pro-comic-manga-generation/) · [Popcorn — consistency](https://higgsfield.ai/blog/how-to-keep-ai-persona-consistent-higgsfield-popcorn)
- [HeyGen avatar consent](https://developers.heygen.com/docs/avatar-consent) · [Deepfake labeling under the EU AI Act](https://www.srd-rechtsanwaelte.de/en/blog/deepfake-labelling-under-the-ai-act-what-the-new-eu-guidance-clarifies)
- [Kling 3 consistency](https://kling.ai/blog/kling-3-subject-binding-character-consistency) · [AI movie: Claude Code + Seedance](https://kompozy.io/how-to/ai-movie-pipeline-claude-code-seedance)
- [Marketing Studio Higgsfield](https://higgsfield.ai/blog/new-marketing-studio-higgsfield) · [AI logo animation: a case](https://contra.com/p/rbcrqFsR-ai-accelerated-logo-animation-and-motion-design)

**Tools**
- [DaVinci Resolve 21.1 adds MCP — Digital Production](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/)
- [Resolve 21.1 MCP — YMCinema](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/)
- [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp)
- [Codex CLI image generation](https://codex.danielvaughan.com/2026/04/27/codex-cli-image-generation-gpt-image-2-visual-development-workflows/)
- [Cowork scheduled tasks — Anthropic](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-cowork)
- [Cowork vs Claude Code](https://www.ssdnodes.com/learn/claude-cowork-vs-claude-code)
- [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills)
