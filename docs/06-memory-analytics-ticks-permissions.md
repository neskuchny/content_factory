# Memory, analytics, ticks, and permissions

> Stage 3. Date: 2026-10-24. Sources: Claude Code documentation (hooks, permissions, sub-agents,
> routines, headless, memory) and research on platform APIs. Verified on real data: collection and
> scoring against a public Telegram channel, and the gatekeeper against a client's shared drive.
> **[UNVERIFIED]** — not verified.

---

## 1. Memory: four layers by how locked they are

| Layer | What | Where | Who writes | How it is protected |
|---|---|---|---|---|
| **1. Locked layer** | Factory framework, the client's business and product, taboos, permissions | `CLAUDE.md`, `.claude/`, `flows/`, `config/`, `scripts/`, `templates/`; `clients/<c>/passport.yaml`, `product-base/`, `permissions.yaml`, `brand/consents.md` | **Humans only** | The `scripts/guard/guard.py` hook blocks writes by any agent. Plus GitHub branch protection (see §4.4) |
| **2. Compressed experience** | What was published, what works, where we are now, the learned style | `memory/published-log.md`, `channel-state.md`, `targeting-map.md`, `hooks-library.yaml`, `platform-learnings.md`, `MEMORY.md` (index ≤ 200 lines); `brand/voice.md`, `visual.md`, `tokens.json` | analyst (conclusions), feedback (style, log, compaction) | Permissions by matrix: each agent writes only its own files. No rule is made from a single case |
| **3. Cells (numbers)** | Metric snapshots, baselines, post scores, the "unit ↔ post" link | `analytics/snapshots.jsonl`, `baselines.json`, `scores.jsonl`, `registry.jsonl` | **Scripts only** (+ publisher writes registry) | Agents may not write, read only |
| **4. Assets** | Brand kit, golden references, sources, archive | `brand/assets/`, `brand/golden/`, shared drive / Google Drive, `weeks/` | human, feedback (golden), studio (templates) | Sources are read-only; the drive is accessed through public read links |

Plus **the agent's own craft memory** (`memory: project` → `.claude/agent-memory/<agent>/MEMORY.md`,
the first 200 lines go into context): how to use a tool better, typical mistakes.
Facts about a client are never written there.

**Why files in git and not a database at the start:** every memory change has an author, a diff,
and a rollback. The feedback agent's edits are visible and checkable. A database (Supabase and the
like) becomes necessary when there is a client interface or analytics across many clients at once.
The cell schema does not change because of that.

**Why not `chmod 444`, as another agent proposed:** cloud runs clone the repository from scratch
every time, and git does not store write permissions. Protection has to live in the repository
itself: the hook and the branch rules.

### Compaction (the `memory-compaction` skill)
- **Weekly:** one line per unit in `published-log`; `MEMORY.md` as a short index
  (state, 3–5 key conclusions, topics on pause).
- **Monthly:** lines older than a quarter are folded into a summary ("Q3: 12 Reels about glazing,
  before/after with a number worked best, the topic "prices" is overheated"). Refuted conclusions
  are deleted with a changelog entry.
- Full scripts stay in `weeks/` as an archive and are not read by default.

---

## 2. Analytics: what worked and what did not

### 2.1 The loop
```
publisher publishes → registry.jsonl (our unit, rubric, hook type, flow ↔ platform post)
   ↓ hourly tick (no model)
collectors → snapshots.jsonl (post metrics over time)
   ↓
baseline.py → baselines.json (channel × format baseline) + scores.jsonl (multiplier, label)
   ↓ retro (model)
analyst (perf-loop) → channel-state, hooks-library, targeting-map, platform-learnings
feedback → golden references, style;  producer → next week's plan based on these conclusions
```

### 2.2 Relative scoring (the answer to "is a million a lot or a little?")
- **Baseline** = median of the last 20 posts of **this channel and format** at **the same post age**
  (72 h; for Telegram also 24 h). Median, not mean: one viral post does not break the baseline.
  Posts younger than 48 h and pinned posts are excluded from the baseline.
- **Multiplier** = post metric / baseline. Labels: **ANOMALY ≥ 3** · **WIN ≥ 1.8** · **OK 0.6–1.8** · **MISS < 0.6**.
- **Channel growth** is the trajectory of the baseline itself (`channel-state.md`: now, a month ago,
  a quarter ago). A thousand → a million shows up as a jump of the baseline and a run of ANOMALY labels.
- **Small samples:** with a baseline of fewer than 8 posts the labels are preliminary. The conclusion
  "the hook works" is drawn after ≥ 3 posts of that type. Paid seeding is marked in registry and is
  not mixed with organic.

### 2.3 Verified against a public Telegram channel
`scripts/collect/telegram_public.py` collected the posts from a public channel page (no keys).
`scripts/analytics/baseline.py` computed the baseline from them (median, p25, p75), and the most
recent posts showed up as a real dip below the baseline. Caveat: this was a first snapshot, and old
posts have views accumulated over their whole lifetime. A fair score at 24/72 h age starts once the
collector has run daily for a week, and the script warns about this.

### 2.4 How to collect metrics per platform
| Platform | Own posts | Others' posts (trends) | Notes |
|---|---|---|---|
| **Telegram** | MTProto (Telethon): views, forwards, reactions for any public channel; `stats.getBroadcastStats` — for an admin with `can_view_stats` (≈500+ subscribers); **TGStat API** (free for 2 own channels) | Public preview `t.me/s/…` (our collector), TGStat Search / Callback | Forwards are the main value signal in TG; the preview does not show them |
| **YouTube** | Analytics API: views, engagedViews, retention, `relativeRetentionPerformance`; impressions and CTR — **Reporting API** (reach reports) | Data API v3 (quota 10,000/day) | Shorts "viewed / swiped away" exists only in Studio; the substitute is engagedViews/views [UNVERIFIED] |
| **Instagram** | Graph API: views, reach, saved, shares, `ig_reels_avg_watch_time`, `reels_skip_rate` (beta); Stories — only 24 h | Apify scrapers (public data) | ⚠️ For clients in Russia: Meta is designated extremist there, and advertising on its resources has been banned since 2025-09-01. Keep publishing under a separate flag in permissions and do not run paid promotion |
| **VK** | `stats.getPostReach` (only communities of 5,000+ members); otherwise public views, likes, reposts | Apify VK Posts Scraper | |
| **Threads** | Insights API: views, likes, replies, reposts, quotes, shares | — | Also Meta |
| **Pinterest** | API v5: impressions, saves, pin clicks, outbound clicks | — | |
| **Rutube, Yandex Maps** | No public API → weekly manual export or a screenshot of the dashboard | — | manual |
| Everything at once (SaaS) | **LiveDune** (Russian market: Instagram, TG, VK, YouTube, OK; has an API, from ~1,900 RUB/month [UNVERIFIED]), Metricool MCP (no VK and TG), Supermetrics (plugin exists, needs authorization) | Popsters (competitors, export) | Pick one source per client |

### 2.5 Trends (the `trend-scout` skill)
List of references → daily collection → **anomalies relative to the author's own baseline** (≥ 3×) →
breakdown (core meaning, hook, structure, packaging, why it worked) → fitting to the client
(score 0–5 by closeness to the product, tone, availability of sources, risk) → `trends/<W>.md` → producer.
The approach is the same as vidIQ Outliers (2/5/10×) and Paddy Galloway (videos 5–15× above baseline).
Scrape only public data and without login. Store aggregates, no personal data.

### 2.6 Hooks (library `hooks-library.yaml` + the `perf-loop` skill)
- 7 hook types; each has per-platform statistics: n and median multiplier.
- For each topic, 3–5 variants of different types. The hook type is recorded in the plan and in registry.
- Selection: 70 % proven (n ≥ 3, median ≥ 1.2), 30 % exploration.
- **MISS with a weak start → re-hook:** the same video, new first 1–3 s and a new headline, re-release.
- Built-in platform A/B tests: Instagram **Trial Reels** (shown to non-followers first), YouTube
  **Test & Compare** (up to 3 thumbnails or titles, the winner by share of watch time).
- Higgsfield `virality_predictor` is a hint before publishing, not a replacement for real data.

### 2.7 Transfer between platforms
Once a week: a winner on one platform → the same substance in the wrapper of another. If a topic
failed twice on a platform, "do not transfer X to Y" is written to `platform-learnings` → "Filters".

---

## 3. Ticks: wake the model only when there is work

### 3.1 The "dumb gatekeeper" principle
A tick is first a **script without a model** (`scripts/ticks/precheck.py`), and only if it finds
work is a **specific** agent woken, with a ceiling on steps and budget. The gatekeeper checks:
| Check | Whom it wakes |
|---|---|
| New files on the client's drive (public API) | media-indexer (at most 30 files per run, priority: high first) |
| Mon–Tue and the week has not started | orchestrator (stages 0–2) |
| A human answered in the approval pack | publisher + feedback |
| Posts reached 24/72/168 h | only the collector scripts (no model needed) |
| Sunday, no retro yet | analyst (perf-loop + memory-compaction) |

Verified: without a network the gatekeeper returned "no work" (code 3). With a network it found a
large client archive (thousands of files) on the drive. That is why the indexer processes the archive
in batches, and why listing the drive takes minutes: an hourly tick needs a listing cache (the next step).

### 3.2 Three ways to run
| Option | How | When to choose |
|---|---|---|
| **A. GitHub Actions + cloud task** (recommended) | `.github/workflows/factory-ticks.yml`: every hour it collects metrics for free and runs the gatekeeper. If there is work, it POSTs to the **API trigger** of the "Dispatcher" cloud task (`/fire`, text = list of wake-ups) | No server of your own; the model is spent only on work |
| **B. Your own server** | `scripts/ticks/run.sh` via cron: collectors → gatekeeper → `claude -p … --agent <name> --permission-mode dontAsk --max-turns 40 --max-budget-usd 3` | You need the Telegram channel (the session must be open) or DaVinci on the same machine |
| **C. Cloud tasks only** | Schedule in claude.ai/code/routines (no more than once per hour) | For rare heavy ticks (week plan, retro); every run spends the limit even if there is no work |

Cloud task limits: no more than once per hour, up to 100 runs per hour per account, and the API
trigger allows up to 30 calls per hour per task. Text from `/fire` arrives as **untrusted data**
(`<routine-fire-payload>`), so the dispatcher prompt explicitly allows reading only the list of
wake-ups from it (see `docs/04-setup.md`).

### 3.3 Protection against loops
`--max-turns`, `--max-budget-usd`, the credit limit in `permissions.yaml`, 3 FAILs on a step go to a human.
All tasks are visible: cloud ones in claude.ai/code/routines, your own in `crontab` and `.github/workflows/`.

---

## 4. Permissions: who can do what

### 4.1 Four levels (from soft to hard)
1. **Agent tools** (the header of `.claude/agents/*.md`): `tools` / `disallowedTools`. Paid
   Higgsfield generations are available only to studio. Director and reviewer may read the model
   catalog but not generate. Analyst, producer, adapter, publisher, and feedback do not see Higgsfield.
   Analyst and media-indexer read the web; they do not publish and do not spend.
2. **File permissions** — the `scripts/guard/guard.py` hook driven by `config/permissions-matrix.yaml`:
   - the locked layer (`protected`) is closed to all agents;
   - each role has its own list of writable paths;
   - secrets (`.env`, `secrets/`) are unreadable to everyone;
   - Bash commands that write to files (`>`, `tee`, `sed -i`, `cp`/`mv`/`rm`) are checked by the same rules.
     This is a heuristic: it does not parse ffmpeg and the like, which is why level 4 backs it up;
   - every decision is written to `.cache/guard.log`.
   The hook sees which subagent calls the tool (`agent_type`), so one matrix serves everyone.
   Verified with 12 scenarios (feedback cannot edit CLAUDE.md; studio cannot edit the brand voice;
   onboarding cannot edit client permissions; studio via Bash cannot edit the client passport; secrets are closed).
3. **Executor ≠ controller.** Studio does not give itself a PASS: the verdict is written by reviewer
   (`review.md` is the only file reviewer may write). Only publisher publishes, and only what a
   human approved. Only orchestrator creates tasks.
4. **Git and external accounts.**
   - Runs work in the `factory` branch; changes reach `main` only through a pull request. Enable
     protection on `main` and CODEOWNERS on `CLAUDE.md`, `.claude/`, `config/`, `flows/`, `scripts/`,
     `clients/*/passport.yaml`, `permissions.yaml`, `product-base/`.
   - Platform tokens have minimal rights: for analytics, read-only statistics access;
     publishing tokens exist only in the run where publisher is enabled. The client's drive is read-only.

### 4.2 Owner and runs
- A main session without `agent_type` is the **owner** (a human working interactively): everything is allowed except secrets.
- Scheduled runs set `FACTORY_MODE=run` (a cloud environment variable or `run.sh`). Then the main
  session becomes **orchestrator** and the locked layer is closed to it. Runs need a **separate
  cloud environment** with this variable. [NV: passing environment variables to the hook in the
  cloud is not described directly in the docs — check with the first run.]
- The rules in `.claude/settings.json` apply in a cloud task only if the task has **a single repository**.

### 4.3 Write matrix (short)
| Agent | May write |
|---|---|
| orchestrator | weeks, one-off requests, quotas / channels (after a human "yes"), changelog, proposals |
| producer | plan, shoot brief, scripts, request briefs |
| director | harness, beats, shotlist |
| studio | production folders, costs, brand templates, `.cache` |
| reviewer | only `review.md` |
| adapter | adaptations |
| publisher | publishing log, kits, registry |
| media-indexer | media-index, `.cache` |
| analyst | references, trends, 00-inputs, 08-retro, targeting-map, channel-state, hooks-library, platform-learnings |
| feedback | memory/, voice, visual, tokens, golden, brand/references |
| onboarding | clients/, except permissions and analytics |
| all | nothing from the locked layer |

---

## 5. Amendments to another agent's scheme
| Proposal | How we did it and why |
|---|---|
| `chmod 444` on the core | The cloud clones anew and permissions are not preserved → hook + branch protection |
| SQLite/Supabase for cells | JSONL in git at the start (diff, rollback, no infrastructure); a database when a UI is needed |
| Separate "Archivist" and "Meaning agent" | Compaction is the `memory-compaction` skill at feedback/analyst; meaning is producer. Fewer agents, fewer handoffs |
| Wake agents every 2 h by a model cron | A gatekeeper script: the model only when there is work |
| Apify / TGStat / Metricool | Yes, as sources. But Telegram and some metrics are free: the public preview and MTProto; for Russia — LiveDune |
| "Score > 1.8 → automatically into golden references" | Only the label is automatic. A golden reference is saved after a review and with a reason, otherwise flukes end up in the references |

## Sources
- [Hooks](https://code.claude.com/docs/en/hooks.md) · [Permissions](https://code.claude.com/docs/en/permissions.md) · [Sub-agents](https://code.claude.com/docs/en/sub-agents.md) · [Settings in the cloud](https://code.claude.com/docs/en/settings.md) · [Sandboxing](https://code.claude.com/docs/en/sandboxing.md)
- [Routines / scheduled tasks](https://code.claude.com/docs/en/routines.md) · [Headless](https://code.claude.com/docs/en/headless.md) · [CLI](https://code.claude.com/docs/en/cli-reference.md) · [Memory](https://code.claude.com/docs/en/memory.md)
- [Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/) · [YouTube Analytics metrics](https://developers.google.com/youtube/analytics/metrics) · [YouTube Reporting reports](https://developers.google.com/youtube/reporting/v1/reports/channel_reports) · [Telegram stats](https://core.telegram.org/api/stats) · [VK stats.getPostReach](https://dev.vk.ru/ru/method/stats.getPostReach) · [Threads Insights](https://developers.facebook.com/docs/threads/insights/)
- [Apify MCP](https://docs.apify.com/platform/integrations/mcp) · [TGStat API](https://api.tgstat.ru/docs/ru/start/intro.html) · [Metricool MCP](https://help.metricool.com/faqs-about-the-metricool-mcp-1i3w0) · [Postiz MCP](https://docs.postiz.com/mcp/introduction) · [LiveDune](https://toolfox.ru/services/s/livedune) · [Google Trends API](https://developers.google.com/search/blog/2025/07/trends-api)
- [vidIQ Outliers](https://support.vidiq.com/en/articles/9660010-outliers) · [Paddy Galloway](https://outlierkit.com/resources/paddy-galloway-growth-strategy/) · [Trial Reels / changelog](https://developers.facebook.com/docs/instagram-platform/changelog) · [YouTube Test & Compare](https://thumbnailtest.com/news/youtube-releases-title-test-compare/)
- [Meta in Russia: advertising ban](https://www1.ru/en/news/2025/04/07/prezident-rf-utverdil-zakon-zapreshhaiushhii-reklamu-v-instagram-i-facebook.amp.html) · [Meta v. Bright Data](https://www.fbm.com/post/102kqw7/)
