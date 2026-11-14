#!/usr/bin/env bash
# Tick for a self-hosted server (cron). Gatekeeper first (no tokens), then only the agents that have work.
# crontab:  17 * * * *  cd /srv/content_auto && scripts/ticks/run.sh >> .cache/ticks.log 2>&1
set -euo pipefail
cd "$(dirname "$0")/../.."
export FACTORY_MODE=run          # main session = orchestrator, locked layer closed (scripts/guard)

git pull -q --ff-only || true

# 1. collectors and metric calculation, no model
for c in $(ls clients); do
  [ -f "clients/$c/analytics/collect.sh" ] && bash "clients/$c/analytics/collect.sh" || true
  [ -f "clients/$c/analytics/snapshots.jsonl" ] && python3 -I scripts/analytics/baseline.py --client "$c" >/dev/null || true
done

# 2. gatekeeper
if ! wakes=$(python3 -I scripts/ticks/precheck.py); then
  echo "$(date -Is) nothing to do"; git add -A clients && git commit -qm "tick: metrics" && git push -q || true
  exit 0
fi

# 3. wake only the agents that have work; hard cap on turns and budget
echo "$wakes" | python3 -I -c '
import json,sys
for w in json.load(sys.stdin):
    if not w["agent"].startswith("script:"):
        print(w["agent"]+"\t"+w["prompt"])' | while IFS=$'\t' read -r agent prompt; do
  echo "$(date -Is) wake $agent"
  claude -p "$prompt" --agent "$agent" --permission-mode dontAsk \
    --max-turns 40 --max-budget-usd 3 --output-format json > ".cache/last-$agent.json" || echo "agent $agent failed"
done

git add -A clients && git commit -qm "tick: agents" && git push -q || true
