#!/usr/bin/env python3
"""The "dumb gatekeeper": decides whom to wake without spending a single model token.

Checks repository files (and the public Yandex Disk listing) and prints a JSON list
of wakes: [{"client", "agent", "reason", "prompt"}]. An empty list means no model is started.

Usage:
  python3 scripts/ticks/precheck.py            # all clients
  python3 scripts/ticks/precheck.py --client demo --no-network
Exit code: 0 = there is work, 3 = no work (handy for `if` in cron/Actions).
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime.now(timezone.utc)
METRIC_AGES_H = [24, 72, 168]
BATCH = 30  # files per indexer run: a large archive is processed in batches


def iso_week(d=NOW):
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def load_yaml(p):
    import yaml
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def yadisk_files(public_url, path="/", depth=2):
    """File names in a public Yandex Disk folder (no key needed)."""
    out = []
    q = urllib.parse.urlencode({"public_key": public_url, "path": path, "limit": 200})
    try:
        with urllib.request.urlopen(f"https://cloud-api.yandex.net/v1/disk/public/resources?{q}", timeout=20) as r:
            data = json.load(r)
    except Exception:
        return None
    for it in data.get("_embedded", {}).get("items", []):
        if it["type"] == "file":
            out.append(f"{public_url}:{it['path']}")
        elif depth > 0:
            sub = yadisk_files(public_url, it["path"], depth - 1)
            out += sub or []
    return out


def check_client(c, network):
    base = ROOT / "clients" / c
    wakes = []
    week = iso_week()
    wdir = base / "weeks" / week

    # 1. new source files -> media-indexer
    if network:
        known = (base / "media-index" / "index.md").read_text(encoding="utf-8") if (base / "media-index" / "index.md").exists() else ""
        new = 0
        for src in (load_yaml(base / "sources.yaml").get("yandex_disk") or []):
            files = yadisk_files(src["url"])
            if files is None:
                continue
            new += sum(1 for f in files if f.split(":", 1)[1] not in known)
        if new:
            wakes.append({"agent": "media-indexer", "reason": f"{new} new files on the Disk",
                          "prompt": f"You are media-indexer. Client {c}. New files: {new}. Build skeletons for at most "
                                    f"{BATCH} files in this run: first the priority: high folders from sources.yaml, "
                                    f"within them video first, then the most recent. Update media-index."})

    # 2. week stage -> orchestrator (if the week has not started and today is Mon-Tue)
    if NOW.weekday() <= 1 and not (wdir / "01-plan.md").exists():
        wakes.append({"agent": "orchestrator", "reason": f"week {week} not started",
                      "prompt": f"You are orchestrator. Client {c}. Run stages 0-2 of week {week} using the weekly-cycle skill."})

    # 3. human answers in the approval pack -> publisher and feedback
    ap = wdir / "06-approval.md"
    if ap.exists():
        txt = ap.read_text(encoding="utf-8")
        # each "## <ID>" section is parsed on its own, so a decision cannot leak into a neighbouring section
        decided = []
        for sec in re.split(r"(?m)^## ", txt)[1:]:
            uid = sec.split(None, 1)[0] if sec.strip() else ""
            d = re.search(r"(?m)^\s*(?:[-*]\s*)?decision:\s*(\S.*)$", sec)
            if uid and d and not d.group(1).startswith("pending"):
                decided.append((uid, d.group(1)))
        pubs = (wdir / "07-publications.md").read_text(encoding="utf-8") if (wdir / "07-publications.md").exists() else ""
        todo = [uid for uid, _ in decided if uid not in pubs]
        if todo:
            wakes.append({"agent": "publisher", "reason": f"decisions on {len(todo)} units are waiting for publishing",
                          "prompt": f"You are publisher. Client {c}, week {week}. Process the approved units: {', '.join(todo)}."})
            wakes.append({"agent": "feedback", "reason": "new human decisions and comments",
                          "prompt": f"You are feedback. Client {c}, week {week}. Process the decisions in 06-approval.md."})

    # 4. metrics: posts that reached 24/72/168 h -> scripts only, no model
    reg = base / "analytics" / "registry.jsonl"
    if reg.exists():
        due = 0
        for line in reg.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            pub = datetime.fromisoformat(r["published_at"].replace("Z", "+00:00"))
            age = (NOW - pub).total_seconds() / 3600
            if any(a <= age < a + 6 for a in METRIC_AGES_H):
                due += 1
        if due:
            wakes.append({"agent": "script:collect", "reason": f"{due} posts reached a checkpoint age",
                          "prompt": "collect"})

    # 5. retro on Sunday if it does not exist yet
    if NOW.weekday() == 6 and wdir.exists() and not (wdir / "08-retro.md").exists():
        wakes.append({"agent": "analyst", "reason": "weekly retro",
                      "prompt": f"You are analyst. Client {c}, week {week}. Stage 8 using the perf-loop skill, then memory-compaction."})

    for w in wakes:
        w["client"] = c
    return wakes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client")
    ap.add_argument("--no-network", action="store_true")
    a = ap.parse_args()
    clients = [a.client] if a.client else sorted(p.name for p in (ROOT / "clients").iterdir()
                                                  if (p / "channels.yaml").exists())
    wakes = []
    for c in clients:
        wakes += check_client(c, not a.no_network)
    print(json.dumps(wakes, ensure_ascii=False, indent=2))
    sys.exit(0 if wakes else 3)


if __name__ == "__main__":
    main()
