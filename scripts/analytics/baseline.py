#!/usr/bin/env python3
"""Relative scoring of publications: rolling channel baseline and post multiplier.

Input:  clients/<c>/analytics/snapshots.jsonl  (metric snapshots written by the collectors)
        clients/<c>/analytics/registry.jsonl   (optional: our unit ID, rubric, hook type for a post)
Output: clients/<c>/analytics/baselines.json   (baseline per channel and format)
        clients/<c>/analytics/scores.jsonl     (score of each post)
        stdout: short summary for the agent (anomalies and misses)

Rules (docs/06-...):
- the metric is taken at a fixed post age (default 72 h) so that like is compared with like;
  if there is no snapshot of that age, take the latest one and mark age_ok=false;
- baseline = median of the last N (default 20) posts of the same channel and format, older than the window;
- multiplier = metric / baseline; labels: ANOMALY >=3, WIN >=1.8, OK 0.6-1.8, MISS <0.6;
- with a sample of < 8 posts the labels are preliminary (low_sample).
"""
import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

LABELS = [(3.0, "ANOMALY"), (1.8, "WIN"), (0.6, "OK"), (0.0, "MISS")]


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def label(m):
    for edge, name in LABELS:
        if m >= edge:
            return name
    return "MISS"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--metric", default="views")
    ap.add_argument("--age-hours", type=float, default=72)
    ap.add_argument("--window", type=int, default=20)
    ap.add_argument("--by-format", action="store_true", help="separate baseline per format")
    args = ap.parse_args()

    base = Path("clients") / args.client / "analytics"
    snaps = [json.loads(l) for l in (base / "snapshots.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    registry = {}
    reg_path = base / "registry.jsonl"
    if reg_path.exists():
        for l in reg_path.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                registry[(r["platform"], r["channel"], str(r["post_id"]))] = r

    # metric value at the required age: first snapshot with age >= target, otherwise the latest
    by_post = defaultdict(list)
    for s in snaps:
        if s.get(args.metric) is None or not s.get("published_at"):
            continue
        by_post[(s["platform"], s["channel"], str(s["post_id"]))].append(s)

    posts = []
    for key, rows in by_post.items():
        rows.sort(key=lambda r: r["fetched_at"])
        pub = ts(rows[0]["published_at"])
        pick, age_ok = rows[-1], False
        for r in rows:
            if (ts(r["fetched_at"]) - pub).total_seconds() / 3600 >= args.age_hours:
                pick, age_ok = r, True
                break
        age_h = (ts(pick["fetched_at"]) - pub).total_seconds() / 3600
        # the first snapshot was taken long after the target age -> this is the all-time accumulated value
        lifetime = age_h > max(2 * args.age_hours, args.age_hours + 48)
        posts.append({"key": key, "published_at": pick["published_at"], "format": pick.get("format", "all"),
                      "value": pick[args.metric], "age_h": round(age_h, 1), "age_ok": age_ok, "lifetime": lifetime,
                      "text_head": pick.get("text_head", "")})

    posts.sort(key=lambda p: p["published_at"])
    groups = defaultdict(list)
    for p in posts:
        g = (p["key"][0], p["key"][1], p["format"] if args.by_format else "all")
        groups[g].append(p)

    baselines, scores = {}, []
    for g, items in groups.items():
        for i, p in enumerate(items):
            prev = [x["value"] for x in items[max(0, i - args.window):i] if x["age_ok"]]
            if len(prev) < 3:
                continue
            med = statistics.median(prev)
            mult = p["value"] / med if med else None
            reg = registry.get(p["key"], {})
            scores.append({"platform": g[0], "channel": g[1], "format": g[2], "post_id": p["key"][2],
                           "published_at": p["published_at"], args.metric: p["value"], "age_h": p["age_h"],
                           "age_ok": p["age_ok"], "lifetime": p["lifetime"], "baseline": med, "n": len(prev),
                           "multiplier": round(mult, 2) if mult else None,
                           "label": label(mult) if mult else None, "low_sample": len(prev) < 8,
                           "unit_id": reg.get("unit_id"), "rubric": reg.get("rubric"), "hook_type": reg.get("hook_type"),
                           "text_head": p["text_head"][:80]})
        mature = [x["value"] for x in items if x["age_ok"]][-args.window:]
        if mature:
            baselines["/".join(g)] = {"metric": args.metric, "age_hours": args.age_hours, "n": len(mature),
                                      "median": statistics.median(mature),
                                      "p25": statistics.quantiles(mature, n=4)[0] if len(mature) >= 4 else None,
                                      "p75": statistics.quantiles(mature, n=4)[2] if len(mature) >= 4 else None}

    (base / "baselines.json").write_text(json.dumps(baselines, ensure_ascii=False, indent=2), encoding="utf-8")
    with (base / "scores.jsonl").open("w", encoding="utf-8") as f:
        for s in scores:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    if any(p["lifetime"] for p in posts):
        print("WARNING: some values are accumulated all-time totals (no snapshot at the required age). "
              "Run the collector daily to make the scoring fair.")
    for g, b in baselines.items():
        print(f"BASELINE {g}: median {args.metric}@{args.age_hours:g}h = {b['median']:.0f} (n={b['n']}, p25={b['p25']}, p75={b['p75']})")
    for s in scores[-args.window:]:
        if s["label"] in ("ANOMALY", "WIN", "MISS"):
            flag = " (low sample)" if s["low_sample"] else ""
            print(f"{s['label']:7} x{s['multiplier']:<5} {s['channel']}/{s['post_id']} {s['published_at'][:10]} {s['text_head']}{flag}")


if __name__ == "__main__":
    main()
