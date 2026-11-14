---
name: perf-loop
description: "Performance loop — how to read the metrics of your own publications relative to the channel norm, what to do with winners, anomalies and misses, how to update the hooks library and channel state, and how to carry winners over to other platforms. Use at the retro (stage 8) and when new scores arrive."
---

# Performance loop

## Input (read, do not write — scripts write these)
- `analytics/scores.jsonl` — the multiplier and label of each post relative to the channel × format norm.
- `analytics/baselines.json` — the norms. `analytics/registry.jsonl` — which of our content units each post corresponds to (rubric, hook type, flow).

## Why relative numbers
A million views against a channel norm of 2 million is a drop. A thousand → a million is an event.
So compare a post **with the norm of its own channel and format at the same age** (72 h; for
Telegram also 24 h), and measure channel growth by **the trajectory of the norm itself**.

## Labels and actions
| Label | Multiplier | Action |
|---|---|---|
| **ANOMALY** | ≥ 3 | Break it into atoms: topic, pain point, hook (first 1–3 s or first line), length, pace, cover, CTA. Save it as a golden reference (`style-memory`). Propose 2–3 follow-ups and a carry-over to other platforms |
| **WIN** | 1.8–3 | Into `targeting-map` and `hooks-library`. The topic can be scaled up (sighting round → scale) |
| **OK** | 0.6–1.8 | Log only (`published-log`), so we do not repeat ourselves |
| **MISS** | < 0.6 | Diagnose: if the hook is weak (low retention of the opening / few reactions despite good reach), propose a **re-hook** — new first 1–3 s and a new headline, same video, re-released on another platform or a week later. If the topic is weak, mark the topic |

**Small samples:** with `low_sample` (norm based on < 8 posts) labels are provisional. The conclusion
"this hook type works" requires ≥ 3 posts of that type on the platform. Account for the day of the
week, news hooks and paid seeding (seeding distorts reach — flag it in the registry).

## Update memory
1. `memory/channel-state.md` — the norm now, a month and a quarter ago, the trend, the best post of the period.
2. `memory/hooks-library.yaml` — for each hook type per platform: n, median multiplier.
3. `memory/targeting-map.md` — topics, hooks, formats, lengths, covers: what works and what does not, with evidence.
4. `memory/platform-learnings.md` — conclusions per platform and the results of carry-overs.

## Cross-platform carry-over (once a week)
For every WIN/ANOMALY: the meaning stays, the wrapper changes to fit the platform (Telegram post → Reels with
an infographic → carousel). If a topic has failed twice on a platform, write "do not carry X over to Y" in
`platform-learnings` → "Filters".

## Choosing hooks for next week
70 % — proven types (n ≥ 3, median ≥ 1.2 on this platform), 30 % — exploration. The hook type of
each unit is recorded in the plan and in the registry; without it, learning is impossible.
