#!/usr/bin/env python3
"""Search and download sounds from Openverse (api.openverse.org), respecting licenses.

For a commercial client the default is CC0 and CC BY only (license=cc0,by):
- CC0: no conditions;
- CC BY: attribution (author, title, license, link) is required in the post caption;
- NC (non-commercial), ND (no derivatives) and SA (share-alike) are excluded.

Every downloaded sound is saved to the client's library with a <file>.json passport
(source, author, license, attribution line). The studio puts these data into the video's manifest.json.

Key (optional): OPENVERSE_CLIENT_ID / OPENVERSE_CLIENT_SECRET in the environment give a
higher request limit. To obtain: POST /v1/auth_tokens/register/ (name, description, email),
confirm the email, then client_credentials. Keys are never written to the repository.

Usage:
  python3 scripts/media/openverse.py search "whoosh" --max-sec 3
  python3 scripts/media/openverse.py get <id> --client demo --tag seam
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.openverse.org/v1"
ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "openverse"
UA = {"User-Agent": "content-factory-sound/1.0"}


def token():
    cid, sec = os.environ.get("OPENVERSE_CLIENT_ID"), os.environ.get("OPENVERSE_CLIENT_SECRET")
    if not (cid and sec):
        return None
    body = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid, "client_secret": sec}).encode()
    with urllib.request.urlopen(urllib.request.Request(f"{API}/auth_tokens/token/", data=body, headers=UA), timeout=30) as r:
        return json.load(r)["access_token"]


def call(url, tok, tries=4):
    headers = dict(UA)
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    delay = 5
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as r:
                return json.load(r)
        except Exception as e:  # 429 / 504 / timeout: the service is slow for anonymous requests
            if i == tries - 1:
                raise
            print(f"openverse: {e} - retrying in {delay} s", file=sys.stderr)
            time.sleep(delay)
            delay *= 2


def search(a, tok):
    q = {"q": a.query, "license": a.license, "page_size": a.n}
    if a.category:
        q["category"] = a.category
    if a.max_sec:
        q["length"] = "short" if a.max_sec <= 30 else "medium"
    key = CACHE / (urllib.parse.quote(json.dumps(q, sort_keys=True), safe="")[:180] + ".json")
    CACHE.mkdir(parents=True, exist_ok=True)
    if key.exists():
        data = json.loads(key.read_text())
    else:
        data = call(f"{API}/audio/?{urllib.parse.urlencode(q)}", tok)
        key.write_text(json.dumps(data))
    rows = []
    for r in data.get("results", []):
        dur = (r.get("duration") or 0) / 1000
        if a.max_sec and dur > a.max_sec:
            continue
        rows.append(r)
        print(f"{r['id']}  {r['license']:<4}{(r.get('license_version') or ''):<5} {dur:6.1f}s  "
              f"{r.get('source',''):<11} {r.get('filetype') or '':<5} {r['title'][:60]}")
    print(f"total found: {data.get('result_count')}, shown: {len(rows)}", file=sys.stderr)


def get(a, tok):
    r = call(f"{API}/audio/{a.id}/", tok)
    lic = r.get("license", "")
    if lic not in ("cc0", "by", "pdm"):
        sys.exit(f"license {lic} is not suitable for commercial use with modifications")
    out = ROOT / "clients" / a.client / "brand" / "sounds" / (a.tag or "misc")
    out.mkdir(parents=True, exist_ok=True)
    ext = (r.get("filetype") or Path(urllib.parse.urlparse(r["url"]).path).suffix.lstrip(".") or "mp3")
    name = f"ov_{r['id'][:8]}_{''.join(c if c.isalnum() else '-' for c in r['title'].lower())[:40]}.{ext}"
    with urllib.request.urlopen(urllib.request.Request(r["url"], headers=UA), timeout=120) as src:
        (out / name).write_bytes(src.read())
    attribution = r.get("attribution") or f"\"{r['title']}\" by {r.get('creator')}, {lic.upper()} {r.get('license_version') or ''}"
    meta = {"source": "openverse", "id": r["id"], "title": r["title"], "creator": r.get("creator"),
            "license": lic, "license_version": r.get("license_version"), "license_url": r.get("license_url"),
            "foreign_landing_url": r.get("foreign_landing_url"), "provider": r.get("source"),
            "duration_s": (r.get("duration") or 0) / 1000,
            "attribution_required": lic == "by", "attribution": attribution if lic == "by" else None}
    (out / (name + ".json")).write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(out / name)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--license", default="cc0,by")
    s.add_argument("--category", help="sound_effect | music | ...")
    s.add_argument("--max-sec", type=float)
    s.add_argument("-n", type=int, default=20)
    g = sub.add_parser("get")
    g.add_argument("id")
    g.add_argument("--client", required=True)
    g.add_argument("--tag", help="folder in brand/sounds: seam, assemble, ambience, music...")
    a = ap.parse_args()
    tok = token()
    (search if a.cmd == "search" else get)(a, tok)


if __name__ == "__main__":
    main()
