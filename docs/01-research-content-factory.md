# Content factory: research on methodologies

> Stage 1 — analysis of the problem domain before designing the system.
> Date: 2026-10-24. Sources are listed at the end of the document.

---

## 1. What a content factory is

There is no single definition. The industry converges on the following:

**A content factory is a streamlined, repeatable system for producing, distributing and analyzing
a large volume of content for all of a company's platforms.** It works "like an industrial plant":
there is raw material (information), a conveyor (stages), roles, quality standards (QC), a warehouse
(backlog / archive) and feedback (analytics → plan adjustment).

How it differs from "just SMM":

| SMM / one-off production | Content factory |
|---|---|
| Every post is a separate project | A conveyor with fixed stages and templates |
| Quality depends on the individual author | Quality is set by standards (style, checklists, examples) |
| A plan "by inspiration" | A plan driven by strategy and conveyor capacity |
| No memory of what worked | Retro and analytics every week |
| One piece of material, one publication | One piece of material is broken into dozens of units (atomization) |

A key idea from practice: *"it is not only neural networks, avatars, a crowd of creators or
automation"* — the foundation of a factory is strategy, analytics, trend watching, production,
publishing, retro and the sales funnel. Neural networks are only machines on the shop floor.

---

## 2. Classic methodologies (without AI)

### 2.1 Strategy layer
- **Rubric list / content pillars.** 3–5 core brand topics. More than that blurs the brand
  (a typical mistake is 7+ pillars, or pillars chosen only for SEO).
- **Target audience and content goals.** Every rubric is tied to a goal: reach, trust, sales, retention.
- **Tone of voice and visual style** — fixed in writing and with examples. Without this,
  any automation "drifts".

### 2.2 Content models
- **Hero / Hub / Help** (the Google/YouTube model): rare big "hero" content,
  regular "hub" content (rubrics, series) and constant "help" content (answers to questions, utility).
- **Pillar → atomization (Gary Vaynerchuk's "inverted pyramid" / COPE —
  Create Once, Publish Everywhere).** One big piece of material (a talk, a podcast, a video
  from an event) is cut into quotes, carousels, shorts, an article, and posts for each platform.
  This is the main volume lever: a factory does not so much "invent" as **reprocess**.
- **News hooks.** 20–30 % of the calendar is left free for news and trends.

### 2.3 Production conveyor
Typical stages (all sources agree, give or take the names):

```
Collect raw material → Select topics → Meanings/concepts → Brief → Script/text
  → Production (images, video, editing, voice-over) → QC / review
  → Human approval → Publishing → Analytics → Retro → (next cycle's plan)
```

### 2.4 Operations layer (Content Ops)
- **People / Process / Technology** — roles, procedures, tools.
- **The editorial calendar** as a single point of coordination.
- **Planning from capacity:** the plan must not exceed the conveyor's throughput —
  one of the most frequent reasons for collapse.
- **Weekly rhythm:** planning meeting → production → retro.
- **Testing by volume:** "the winner is whoever can test dozens of hypotheses
  a week", not whoever polishes one perfect video.

---

## 3. The AI content factory: agentic patterns

Anthropic ("Building effective agents") identifies a set of basic patterns. They map directly onto a factory:

| Pattern | Essence | Where in the factory |
|---|---|---|
| **Prompt chaining** | Steps in a chain, one's output is the next one's input | Brief → script → text |
| **Routing** | A classifier sends the task to the right branch | Video / audio / text / image are different branches |
| **Parallelization** | Independent subtasks in parallel | Searching several sources; creative variants |
| **Orchestrator–workers** | The main agent decides which subtasks are needed | The weekly orchestrator hands out tasks to workers |
| **Evaluator–optimizer** | One makes, the other critiques, loop until "ok" | Image generator + artifact reviewer; author + editor |

Anthropic's key recommendations:
1. **Start with the simplest scheme** and add complexity only where a weakness is actually visible.
2. **An evaluator only makes sense if it can reliably tell good from bad** —
   otherwise the loop closes on itself. That is why a reviewer needs criteria, golden references and examples.
3. Agents are not a replacement for deterministic steps where a step can be described rigidly.

### 2026 practice (Claude Code pipelines)
- Roles are defined as subagents with their own context and tool set, and
  hand each other **structured artifacts** (files), not a "conversation".
- Almost all have a **human gate before publishing**.
- Three-level quality checks: deterministic checks → LLM judge →
  a human only for exceptions.

---

## 4. Typical failures and how they are avoided

| Failure | Cause | Antidote |
|---|---|---|
| **Tone drift, monotony** (the same phrases, slogans) | The model gravitates toward "average readability", no golden references | Style guide + a bank of successful examples + a memory of "what has already run" |
| **Brand dilution** | No link "AI draft → human review" | A mandatory approval gate |
| **Approval bottleneck** | Everything waits for one person | Batch approval once a day/week, auto-publishing for low-risk rubrics |
| **Plan exceeds capacity** | Throughput is not tracked | A planner agent computes "no less than needed, no more than possible" |
| **Vague steps** | A step is described so that the agent interprets it its own way | Clear input/output definitions for every stage |
| **Prompt injection from the web** | A search agent pulls in untrusted text | A searcher with no write/publish rights; raw material is treated only as data |
| **No recovery after a failure** | The conveyor lives in a single session | State in files/the task board, a checkpoint after every stage |
| **Feedback damages the system** | Feedback is poured "as is" into all prompts | A separate feedback curator, changes are targeted and versioned |
| **Obsolescence** | Content was true at the time of publication | Periodic review of "evergreen" content |

The main conclusion of practitioners: **the feedback loop matters more than the choice of model.**

---

## 5. What the Claude ecosystem provides "out of the box" (verified against the documentation)

This matters because the task is *not to program a factory but to assemble it from ready-made parts*.

| What the factory needs | Ready-made mechanism | Notes |
|---|---|---|
| Role agents | **Subagents** — `.claude/agents/*.md` (YAML header + prompt) | Fields: `model` (haiku/sonnet/opus/…), `effort`, `tools`, `mcpServers`, `skills`, `memory`, `maxTurns`. Picked up without a restart |
| Cheap/expensive models | `model:` and `effort:` on each agent | Search/routine — Haiku/Sonnet; meanings, feedback — Opus with high effort |
| Agent memory | `memory: project` → `.claude/agent-memory/<name>/MEMORY.md` | Lives in git, a human can read and edit it |
| Shared rules | `CLAUDE.md` in the repository root | The factory's "constitution", read by all agents |
| Abilities | **Skills** (folders with `SKILL.md`) | Search, scripts, style, Remotion video, etc. |
| Schedules (crons) | **Scheduled tasks** (formerly Routines) — Anthropic cloud | Pro/Max/Team/Ent; cron no more often than hourly; limit of 100 runs/hour; work with the laptop switched off; clone the repository; use connectors |
| Event-driven start | API trigger (`/fire`) or GitHub trigger | E.g. "new material arrived" → run |
| Chat with the system | **Channels**: Telegram / Discord / iMessage | ⚠️ Works only while the session is open → a permanently running process is needed (VPS/server) |
| Task board | Linear / Notion / Asana / ClickUp connectors | Linear is already connected in this environment |
| Disk / storage | Google Drive connector | Connected |
| Database | Supabase (MCP) or just files in git | YAML/JSON in the repo is enough to start |
| Image/video generation | **Higgsfield MCP** (images, video, audio, shorts) | Connected in this environment |
| Motion graphics | **Remotion** + Remotion Agent Skills (`npx skills add remotion-dev/skills`) | React video from code; ⚠️ commercial license for companies of 4+ employees |
| Publishing | Postiz (plugin), TikTok via Higgsfield | Available in the plugin catalog |

---

## 6. Checking the ideas from the source recording against best practices

**Confirmed by practice (keep):**
1. **A volume-planner agent** ("no less than necessary and not too much") — this is
   capacity planning, a key content-ops function.
2. **External collection + top-up when short** — trend watching with a re-run if the
   week's quota is not reached.
3. **Separating "variables" from "constants"** — absolutely right: constants in
   `CLAUDE.md`/agent prompts, variables (how much, of what, when) in a separate
   config. This is the protection against non-professionals breaking things.
4. **"Doer + reviewer" pairs** for images and texts — the evaluator-optimizer pattern.
5. **A separate feedback agent that makes changes "very carefully"** — matches
   best practice (a curator, targeted versioned edits).
6. **An expensive model for meanings and feedback, a cheap one for the stream** — the right economics.
7. **Separating "in progress" / "done" (archive)** + a memory of past posts —
   protection against repeats and drift.
8. **An onboarding agent** that interviews the client at the start and configures the stream.
9. **Processing raw material** (photo/video from an event → editing) — this is
   atomization of pillar content, the main volume lever.

**What should be adjusted:**
1. **"Sonnet 3.5" is outdated** — Haiku/Sonnet/Opus 5.5 are current now; Haiku or Sonnet is enough for search.
2. **A Telegram channel does not wake the system by itself** — the session must be open. For "always
   on" you need either a server with a permanent session, or a combination: the schedule does the
   work, and Telegram is only an interface for requests and reports.
3. **"Free-spirited agents" must be balanced by a rigid stage framework** (harness):
   inside a stage the agent is free, but a stage's input/output and gates are fixed.
   Otherwise — drift and "the system started going crazy by itself".
4. **A mandatory human gate** before publishing is needed (the "like/dislike" choice
   is present in the recording; it must be made an integral stage).
5. **The searcher must not have write/publish rights** (prompt injection from the web).
6. **State lives in files/the task board, not in session memory** — for recovery after failures.
7. **Cowork**: according to third-party data, in 2026 Cowork may have been merged into regular
   Claude — before betting on it we will check the current state; the fallback is Remotion
   directly in Claude Code (a cloud session or a server).

---

## 7. Preliminary conclusion (basis for the next stage)

What the recording describes is feasible **without custom code**, on the principle
**"repository = factory"**:

```
content_auto/
├── CLAUDE.md                 # constitution: stages, gates, rules (constants)
├── config/                   # variables: quotas, platforms, schedule, rubrics
├── brand/                    # style, tone of voice, golden references, prohibitions
├── .claude/agents/           # roles (orchestrator, planner, searcher, …)
├── .claude/skills/           # abilities (search, script, Remotion, atomization, …)
├── .claude/agent-memory/     # agent memory (what has run, what worked)
├── inbox/                    # raw material: ideas, photos, video, client materials
├── pipeline/<week>/          # current cycle: plan → concepts → drafts → finished
└── archive/                  # done work, with metrics
```

+ a task board (Linear/Notion) as the shared board of agents and humans,
+ cloud scheduled tasks as the week's "crons",
+ a Telegram channel as a convenient entry point for the human,
+ Higgsfield / Remotion as the machines,
+ a human approval gate before publishing.

Detailed design comes after receiving data from prospective clients.

## 8. Questions for client data (what to find out)
1. Platforms and formats (Telegram, VK, YouTube Shorts, Reels, blog, podcast…).
2. Target weekly volumes, and whether there is a rigid regulation.
3. Sources of raw material: internal materials, news, experts, events.
4. Who approves and how much time they are ready to spend per week.
5. Whether auto-publishing is needed or only preparation.
6. Generation budget (Claude / Higgsfield subscriptions, etc.).
7. Whether there is a brand book, examples of successful content, prohibitions.
8. Which metrics to count as success and where to get them.

---

## Sources

Sources marked (RU) are in Russian.

- [Content factory — Click.ru glossary (RU)](https://blog.click.ru/glossary/kontent-zavod/)
- [What a content factory is — Unisender (RU)](https://www.unisender.com/ru/glossary/kontent-marketing/chto-takoe-kontent-zavod/)
- [MEDIA MIX on content factories — Sostav (RU)](https://www.sostav.ru/blogs/262075/95310)
- [What an AI content factory is — Sostav (RU)](https://www.sostav.ru/blogs/288806/97947)
- [How to launch an AI-based content factory — Sostav (RU)](https://www.sostav.ru/blogs/288806/96552)
- [A content factory for small business — SMMplanner (RU)](https://smmplanner.com/blog/chto-takoie-kontient-zavod-i-zachiem-on-malomu-bizniesu/amp/)
- [Gary Vee content framework — Biteable](https://biteable.com/blog/gary-vees-content-framework-one-video-30-content-pieces/)
- [Content repurposing at scale — Averi](https://www.averi.ai/how-to/content-repurposing-at-scale-how-to-turn-1-piece-into-20-assets)
- [Content Operations 101 — RivalFlow](https://www.rivalflow.com/blog/content-operations-101)
- [Content strategy skill (pillars, mistakes) — Tessl](https://tessl.io/registry/skills/github/rampstackco/claude-skills/content-strategy)
- [Building effective agents — Simon Willison's analysis](https://simonwillison.net/2024/Dec/20/building-effective-agents)
- [Anthropic effective agents — pattern map](https://agentpatterns.ai/agent-design/anthropic-effective-agents-framework/)
- [Claude Code: Subagents (documentation)](https://code.claude.com/docs/en/sub-agents)
- [Claude Code: Scheduled tasks / Routines (documentation)](https://code.claude.com/docs/en/routines)
- [Claude Code: Channels — Telegram/Discord (documentation)](https://code.claude.com/docs/en/channels)
- [Claude agent content pipeline — what broke (probl.me)](https://probl.me/blog/claude-agent-content-pipeline/)
- [Build an AI content pipeline with Claude Code — ChatbotX](https://chatbotx.io/blog/build-an-ai-content-pipeline-with-claude-code-the-complete-2026-guide/)
- [Multi-agent content OS with Claude Code](https://thenuancedperspective.substack.com/p/building-a-multi-agent-content-os)
- [Remotion Agent Skills with Claude Code — Tella](https://www.tella.com/blog/how-to-use-remotion-agent-skills-with-claude-code.md)
- [Making videos with Claude Code + Remotion — OpenReplay](https://blog.openreplay.com/making-videos-claude-code-remotion/)
- [Why AI content production fails — Averi](https://www.averi.ai/blog/ai-driven-content-production-why-your-system-fails)
- [AI content QA workflow — Markup.ai](https://markup.ai/?p=3379)
- [Brand consistency at scale — Adobe](https://experienceleague.adobe.com/en/perspectives/brand-consistency-at-scale)
- [Agentic content pipeline verification — Pebblous](https://blog.pebblous.ai/blog/agentic-content-pipeline-verification/en/)
