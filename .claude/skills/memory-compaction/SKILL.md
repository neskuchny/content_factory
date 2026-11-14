---
name: memory-compaction
description: "Compact the client's memory: a week folds into journal lines, a quarter into a summary, and MEMORY.md stays a short index. Use at the retro at the end of the week and once a month."
---

# Memory compaction

Goal: at the start of work the agent reads **little** but knows the essentials: what has already happened, what works, where we are now.

## Weekly (after the retro)
1. For each published unit, **one line** in `memory/published-log.md`:
   `| 2026-10-21 | W43-R02 | instagram | Site walkthrough | finished install on site, "no drafts" | pain_direct | reels/f01 | 2.4 | WIN |`
2. Full scripts and files stay in `weeks/<W>/` (this is the archive; it is not read by default).
3. Update `memory/MEMORY.md` as an **index** (≤ 200 lines):
   - state (onboarding, current week, open questions);
   - the 3–5 main conclusions of recent weeks with links to files;
   - topics on pause (overheated) and candidate topics;
   - the client's latest feedback in one line.

## Monthly
1. Fold `published-log` lines older than a quarter into a "Summaries" block:
   "Q3: 12 Reels about installation; best performer: before/after with a number in the first line (median ×1.9);
   the 'prices' topic is overheated — paused until December".
2. In `targeting-map`, `hooks-library` and `platform-learnings`: delete conclusions refuted by
   fresh data (with a note in `changelog.md`).
3. Check for repeats: topics that came out ≥ 3 times in 2 months → "on pause".

## Where to remember what (short)
| What | Where | Changed by |
|---|---|---|
| Business, product, taboos, permissions | `passport.yaml`, `product-base/`, `permissions.yaml`, `CLAUDE.md` | human only (locked layer) |
| Style and tone, learned rules | `brand/voice.md`, `brand/visual.md`, `brand/tokens.json` | feedback, with evidence |
| What was published | `memory/published-log.md` | retro |
| What works | `targeting-map`, `hooks-library`, `platform-learnings`, `channel-state` | analyst |
| Numbers | `analytics/*.jsonl` | scripts only |
| Golden references and assets | `brand/golden/`, `brand/assets/`, Drive | feedback, human |
| An agent's experience in its own craft | `.claude/agent-memory/<agent>/MEMORY.md` | the agent itself (not about the client) |
