#!/usr/bin/env python3
"""Credit spend summary per request and video of a client.

Input:
  clients/<c>/requests/*/                      - one-off requests
  clients/<c>/weeks/*/04-production/*/         - videos of the weekly plan
  in each: production/final/manifest.json -> "credits" (a number or a dict with "total");
           otherwise production/costs.md | cost.md | costs.md in the video folder | weeks/<W>/costs.md
           (looks for a line with "total" / "total spent" and the number on it; not found -> "no data")
  config/pricing.yaml -> higgsfield.credit_usd

Output: clients/<c>/analytics/costs.md (and stdout: a short summary).
Invents nothing: if there is no number, the table says "no data".

Usage: python3 scripts/analytics/costs.py --client demo
       [--repo <repository root>] [--out <file instead of clients/<c>/analytics/costs.md>]
"""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

try:
    import yaml  # pyyaml
except ImportError:  # pragma: no cover
    yaml = None

# Repository root: scripts/analytics/costs.py -> ../..  (changed via --repo or set_root()).
ROOT = Path(__file__).resolve().parents[2]

VERDICT_RE = re.compile(r"(?i)verdict\s*:\s*(.+)")
TOTAL_RE = re.compile(r"(?i)(total|total spent)")
NUM_RE = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)(?![\w])")
BOLD_NUM_RE = re.compile(r"\*\*\s*(\d+(?:[.,]\d+)?)\s*\*\*")
VIDEO_EXT = {".mp4", ".mov", ".webm"}


def set_root(path):
    global ROOT
    ROOT = Path(path).resolve()


# ---------- shared helpers (also used by scripts/dashboard/build.py) ----------

def rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def read(p) -> str:
    try:
        return Path(p).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def frontmatter(text: str) -> dict:
    """YAML header between the first '---' lines. Without pyyaml: simple key: value parsing."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    block = m.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(block)
            if isinstance(data, dict):
                return data
        except yaml.YAMLError:
            pass
    out = {}
    for line in block.splitlines():
        mm = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if mm:
            out[mm.group(1)] = mm.group(2).split(" #")[0].strip()
    return out


def load_pricing():
    p = ROOT / "config" / "pricing.yaml"
    txt = read(p)
    rate = None
    if yaml is not None and txt:
        try:
            data = yaml.safe_load(txt) or {}
            rate = (data.get("higgsfield") or {}).get("credit_usd")
        except yaml.YAMLError:
            rate = None
    if rate is None:
        m = re.search(r"credit_usd:\s*([\d.]+)", txt)
        rate = float(m.group(1)) if m else None
    return (float(rate) if rate is not None else None), rel(p)


def find_units(client_dir: Path):
    """List of (unit_id, unit_dir, kind, week) for requests and weekly videos."""
    units = []
    for d in sorted((client_dir / "requests").glob("*/")):
        if d.is_dir() and not d.name.startswith("."):
            units.append((d.name, d, "request", None))
    for d in sorted((client_dir / "weeks").glob("*/04-production/*/")):
        if d.is_dir() and not d.name.startswith("."):
            units.append((d.name, d, "week", d.parent.parent.name))
    return units


def prod_dir(unit_dir: Path) -> Path:
    p = unit_dir / "production"
    return p if p.is_dir() else unit_dir


def final_dir(unit_dir: Path):
    f = prod_dir(unit_dir) / "final"
    return f if f.is_dir() else None


def flow_of(unit_dir: Path):
    """flow from harness.md, otherwise flow/flow_hint from brief.md. Returns (flow, source)."""
    for name, keys in (("harness.md", ("flow",)), ("brief.md", ("flow", "flow_hint"))):
        fm = frontmatter(read(unit_dir / name))
        for k in keys:
            v = fm.get(k)
            if v:
                v = str(v).split("#")[0].strip()
                if v == "custom" and name == "harness.md":
                    hint = frontmatter(read(unit_dir / "brief.md")).get("flow_hint")
                    if hint:
                        return f"custom (based on {str(hint).split('#')[0].strip()})", "harness.md:flow + brief.md:flow_hint"
                return v, f"{name}:{k}"
    return None, None


def load_manifest(unit_dir: Path):
    fd = final_dir(unit_dir)
    if not fd:
        return None
    p = fd / "manifest.json"
    if not p.is_file():
        return None
    try:
        return json.loads(read(p))
    except json.JSONDecodeError:
        return {"__error__": "manifest.json cannot be parsed (JSON)"}


def credits_from_manifest(m):
    if not isinstance(m, dict) or "__error__" in m or "credits" not in m:
        return None
    c = m["credits"]
    if isinstance(c, bool):
        return None
    if isinstance(c, (int, float)):
        return float(c)
    if isinstance(c, dict):
        t = c.get("total")
        if isinstance(t, (int, float)) and not isinstance(t, bool):
            return float(t)
    return None


def credits_from_md(text: str, unit_id: str = None):
    """Number from a "total" / "total spent" line (the last such line is used).
    For the shared weekly costs.md only lines containing the video ID are considered."""
    found = None
    for line in text.splitlines():
        if unit_id and unit_id not in line:
            continue
        t = TOTAL_RE.search(line)
        if not t:
            continue
        tail = line[t.end():]
        mm = BOLD_NUM_RE.search(tail) or NUM_RE.search(tail)
        if mm:
            found = float(mm.group(1).replace(",", "."))
    return found


def credits_of(unit_dir: Path, week_dir: Path = None):
    """(credits | None, source string)."""
    # 1) reconciled fact: production/credits.json {"credits": number, "source": "..."} takes priority over everything
    cj = prod_dir(unit_dir) / "credits.json"
    if cj.is_file():
        try:
            c = json.loads(read(cj)).get("credits")
            if isinstance(c, (int, float)) and not isinstance(c, bool):
                return float(c), rel(cj) + " -> credits (reconciled)"
        except (json.JSONDecodeError, AttributeError):
            pass
    m = load_manifest(unit_dir)
    v = credits_from_manifest(m)
    if v is not None:
        return v, rel(final_dir(unit_dir) / "manifest.json") + " -> credits"
    candidates = [prod_dir(unit_dir) / n for n in ("costs.md", "cost.md")]
    candidates += [unit_dir / n for n in ("costs.md", "cost.md")]
    for p in candidates:
        if p.is_file():
            v = credits_from_md(read(p))
            if v is not None:
                return v, rel(p) + " -> \"total\" line"
    if week_dir is not None:
        p = week_dir / "costs.md"
        if p.is_file():
            v = credits_from_md(read(p), unit_dir.name)
            if v is not None:
                return v, rel(p) + f" -> line {unit_dir.name}"
    return None, "no data: no credits in final/manifest.json and no \"total\" line in costs.md"


def last_verdict(unit_dir: Path):
    """Latest reviewer verdict: (text | None, file | None)."""
    for p in (prod_dir(unit_dir) / "review.md", unit_dir / "review.md"):
        if p.is_file():
            last = None
            for line in read(p).splitlines():
                mm = VERDICT_RE.search(line)
                if mm:
                    last = mm.group(1)
            if last:
                last = re.sub(r"[*#`]", "", last).strip()
                return last, rel(p)
            return None, rel(p)
    return None, None


def final_videos(unit_dir: Path):
    """Final videos (without light copies). Revisions `_v1/_v2` (lowercase v) are one video, the latest is kept;
    variants `_V1/_V2/_V3` are different videos. Returns (kept, replaced by a revision)."""
    fd = final_dir(unit_dir)
    if not fd:
        return [], []
    vids = [p for p in sorted(fd.iterdir())
            if p.is_file() and p.suffix.lower() in VIDEO_EXT and "_light" not in p.stem]
    groups = {}
    for p in vids:
        mm = re.match(r"^(.*)_v(\d+)$", p.stem)  # only lowercase v = revision
        key, rev = (mm.group(1), int(mm.group(2))) if mm else (p.stem, 0)
        groups.setdefault(key, []).append((rev, p))
    keep, replaced = [], []
    for items in groups.values():
        items.sort()
        keep.append(items[-1][1])
        replaced += [p for _, p in items[:-1]]
    return sorted(keep), sorted(replaced)


def light_videos(unit_dir: Path):
    fd = final_dir(unit_dir)
    if not fd:
        return []
    out = [p for p in sorted(fd.glob("*_light.*")) if p.suffix.lower() in VIDEO_EXT]
    if (fd / "light").is_dir():
        out += [p for p in sorted((fd / "light").iterdir()) if p.suffix.lower() in VIDEO_EXT]
    return out


def variants_of(manifest):
    if not isinstance(manifest, dict) or "__error__" in manifest:
        return []
    v = manifest.get("variants")
    if isinstance(v, dict):
        return list(v.keys())
    return []


def collect(client: str):
    client_dir = ROOT / "clients" / client
    rate, rate_src = load_pricing()
    rows = []
    for uid, udir, kind, week in find_units(client_dir):
        week_dir = (client_dir / "weeks" / week) if week else None
        flow, flow_src = flow_of(udir)
        credits, credits_src = credits_of(udir, week_dir)
        usd = round(credits * rate, 4) if (credits is not None and rate is not None) else None
        verdict, verdict_src = last_verdict(udir)
        manifest = load_manifest(udir)
        finals, replaced = final_videos(udir)
        n = len(finals)
        rows.append({
            "id": uid, "kind": kind, "week": week, "dir": rel(udir),
            "flow": flow, "flow_src": flow_src,
            "credits": credits, "credits_src": credits_src, "usd": usd,
            "verdict": verdict, "verdict_src": verdict_src,
            "finals": [rel(p) for p in finals], "replaced": [rel(p) for p in replaced],
            "light": [rel(p) for p in light_videos(udir)],
            "variants": variants_of(manifest),
            "usd_per_video": round(usd / n, 4) if (usd is not None and n) else None,
            "has_production": (udir / "production").is_dir() or final_dir(udir) is not None,
            "manifest_error": manifest.get("__error__") if isinstance(manifest, dict) else None,
        })
    known = [r for r in rows if r["credits"] is not None]
    total_cr = round(sum(r["credits"] for r in known), 4)
    total_usd = round(total_cr * rate, 4) if rate is not None else None
    total_videos = sum(len(r["finals"]) for r in known)
    return {
        "client": client, "rate": rate, "rate_src": rate_src, "rows": rows,
        "total_credits": total_cr, "total_usd": total_usd,
        "total_videos_with_cost": total_videos,
        "usd_per_video_avg": round(total_usd / total_videos, 4) if (total_usd is not None and total_videos) else None,
        "unknown": [r["id"] for r in rows if r["credits"] is None],
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


# ---------- output ----------

def fmt_num(x):
    if x is None:
        return "no data"
    return f"{x:.2f}".rstrip("0").rstrip(".") or "0"


def fmt_usd(x):
    return "no data" if x is None else "$" + f"{x:.2f}"


def verdict_text(r):
    if not r["has_production"]:
        return "not started (no production/)"
    if r["verdict"]:
        return r["verdict"]
    return "no verdict in review.md" if r["verdict_src"] else "no review.md"


def versions_text(r):
    parts = []
    if r["variants"]:
        parts.append(f"hooks: {len(r['variants'])} ({', '.join(r['variants'])})")
    n = len(r["finals"])
    parts.append(f"final videos: {n}" if n else "no final videos")
    if r["replaced"]:
        parts.append(f"old revisions: {len(r['replaced'])} (not counted)")
    return "; ".join(parts)


def render_md(data):
    L = [f"# Spend per request - {data['client']}", "",
         f"Generated: {data['generated']} by `scripts/analytics/costs.py`. Do not edit by hand.",
         "Rate: 1 credit = " + (("$" + str(data["rate"])) if data["rate"] is not None else "no data")
         + f" (`{data['rate_src']}` -> higgsfield.credit_usd).", "",
         "| request | format (flow) | credits | $ | QC verdict | versions / hooks | $ per finished video |",
         "|---|---|---|---|---|---|---|"]
    for r in data["rows"]:
        L.append("| {id} | {flow} | {cr} | {usd} | {v} | {ver} | {per} |".format(
            id=r["id"] + (f" ({r['week']})" if r["week"] else ""),
            flow=r["flow"] or "no data", cr=fmt_num(r["credits"]), usd=fmt_usd(r["usd"]),
            v=verdict_text(r).replace("|", "/"), ver=versions_text(r),
            per=fmt_usd(r["usd_per_video"]) if r["finals"] else "—"))
    L += ["", "## Total",
          f"- Credits across requests with known spend: **{fmt_num(data['total_credits'])}** = **{fmt_usd(data['total_usd'])}**.",
          f"- Final videos in these requests: {data['total_videos_with_cost']}; on average {fmt_usd(data['usd_per_video_avg'])} per video."]
    if data["unknown"]:
        L.append(f"- No spend data: {', '.join(data['unknown'])}. Not included in the total.")
    L += ["", "## Where the numbers come from"]
    for r in data["rows"]:
        L.append(f"- {r['id']}: credits - {r['credits_src']}; flow - {r['flow_src'] or 'none'}; "
                 f"verdict - {r['verdict_src'] or 'no review.md'}.")
    L += ["", "Rules: \"$ per finished video\" = request $ / number of final videos in `final/`. Light copies "
          "(`*_light`, `final/light/`) are not counted. Revisions of one video (`_v1`, `_v2`) count as one video (the latest), "
          "hook variants (`_V1` to `_V3`) are different videos. Carousels and covers are not counted as videos.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Credit spend summary per client request")
    ap.add_argument("--client", required=True)
    ap.add_argument("--repo", help="repository root (default: two levels above the script)")
    ap.add_argument("--out", help="output file (default: clients/<c>/analytics/costs.md)")
    args = ap.parse_args()
    if args.repo:
        set_root(args.repo)
    client_dir = ROOT / "clients" / args.client
    if not client_dir.is_dir():
        raise SystemExit(f"no such client: {client_dir}")
    data = collect(args.client)
    out = Path(args.out) if args.out else client_dir / "analytics" / "costs.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_md(data), encoding="utf-8")
    print(f"written: {out}")
    for r in data["rows"]:
        print(f"  {r['id']}: {fmt_num(r['credits'])} cr., {fmt_usd(r['usd'])}, final videos {len(r['finals'])}")
    print(f"total: {fmt_num(data['total_credits'])} cr. = {fmt_usd(data['total_usd'])}"
          + (f"; no data: {', '.join(data['unknown'])}" if data["unknown"] else ""))


if __name__ == "__main__":
    main()
