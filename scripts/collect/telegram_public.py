#!/usr/bin/env python3
"""Statistics collector for a public Telegram channel via the web preview t.me/s/<channel>.

No keys and no model. Writes view snapshots to analytics/snapshots.jsonl:
one line = one post at the moment of collection. Repeated runs produce new snapshots, from which
baseline.py computes views at a fixed post age (24 h, 72 h, 7 d).

Limitations: view counts are rounded ("1.5K"), and the preview has no forwards or reach;
those need MTProto/TGStat (see docs/06-memory-analytics-ticks-permissions.md).

Usage:
  python3 scripts/collect/telegram_public.py --channel example_channel --client demo --pages 3
"""
import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

POST_RE = re.compile(r'<div class="tgme_widget_message_wrap.*?(?=<div class="tgme_widget_message_wrap|\Z)', re.S)


def parse_views(s):
    s = s.strip().upper().replace(",", ".")
    mult = 1
    if s.endswith("K"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("M"):
        mult, s = 1_000_000, s[:-1]
    try:
        return int(float(s) * mult)
    except ValueError:
        return None


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).split()


def fetch(channel, before=None):
    url = f"https://t.me/s/{channel}" + (f"?before={before}" if before else "")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 content-factory-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse_page(page, channel):
    posts = []
    for block in POST_RE.findall(page):
        m_id = re.search(rf'data-post="{re.escape(channel)}/(\d+)"', block)
        if not m_id:
            continue
        m_views = re.search(r'tgme_widget_message_views">([^<]*)', block)
        m_date = re.search(r'<time datetime="([^"]+)"', block)
        m_text = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', block, re.S)
        text = " ".join(strip_tags(m_text.group(1))) if m_text else ""
        reactions = sum(parse_views(x) or 0 for x in re.findall(r'tgme_reaction[^>]*>.*?</i>\s*([\d.,KM]+)', block, re.S))
        if re.search(r"tgme_widget_message_video|tgme_widget_message_roundvideo", block):
            fmt = "video"
        elif re.search(r"tgme_widget_message_photo", block):
            fmt = "photo"
        else:
            fmt = "text"
        posts.append({
            "post_id": int(m_id.group(1)),
            "published_at": m_date.group(1) if m_date else None,
            "views": parse_views(m_views.group(1)) if m_views else None,
            "reactions": reactions or None,
            "format": fmt,
            "text_head": text[:160],
            "chars": len(text),
        })
    return posts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--pages", type=int, default=2, help="pages of ~20 posts each")
    args = ap.parse_args()

    out = Path("clients") / args.client / "analytics" / "snapshots.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    seen, before = {}, None
    for _ in range(args.pages):
        posts = parse_page(fetch(args.channel, before), args.channel)
        if not posts:
            break
        for p in posts:
            seen[p["post_id"]] = p
        before = min(p["post_id"] for p in posts)

    with out.open("a", encoding="utf-8") as f:
        for p in sorted(seen.values(), key=lambda x: x["post_id"]):
            row = {"platform": "telegram", "channel": args.channel, "fetched_at": fetched_at, **p}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{len(seen)} posts -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
