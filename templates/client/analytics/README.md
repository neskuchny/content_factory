# Cell memory: metrics (written by scripts only)

| file | written by | what |
|---|---|---|
| `registry.jsonl` | publisher | link "our unit ↔ post on a platform": `{unit_id, platform, channel, post_id, url, published_at, rubric, hook_type, format, flow}` |
| `snapshots.jsonl` | collectors in `scripts/collect/*` | snapshots of a post's metrics over time |
| `baselines.json` | `scripts/analytics/baseline.py` | channel × format baseline |
| `scores.jsonl` | `scripts/analytics/baseline.py` | multiplier and label of every post (ANOMALY / WIN / OK / MISS) |
| `collect.sh` | human | which collectors to run for this client |

Agents **read** these files and write their conclusions to `memory/` (channel-state, hooks-library, platform-learnings, targeting-map).
