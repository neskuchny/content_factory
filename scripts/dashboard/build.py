#!/usr/bin/env python3
"""One screen per client: builds a self-contained HTML page from the factory's files.

Reads only the client's files (publishes nothing, does not touch the network) and writes
dashboard/<client>.html. Covers are embedded as thumbnails (<= 240 px, base64 JPEG),
videos are shown as repository paths. Empty sections say when they will be filled.

Usage: python3 scripts/dashboard/build.py --client demo
       [--repo <repository root>] [--out <html instead of dashboard/<c>.html>]
"""
import argparse
import base64
import html
import io
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analytics"))
import costs as C  # noqa: E402  (scripts/analytics/costs.py: the same spend parsing)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None
try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

THUMB = 240
MAX_COVERS = 6
ISSUES = []  # what could not be parsed; shown at the bottom of the page


def esc(s):
    return html.escape(str(s), quote=True)


# ---------- mini-markdown (only what occurs in the factory's files) ----------

def md_inline(s):
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep(line):
    return bool(re.match(r"^\s*\|?\s*:?-{2,}", line)) and set(line.replace("|", "").strip()) <= set("-: ")


def md_table(lines):
    head = split_row(lines[0])
    body = [split_row(l) for l in lines[2:]] if len(lines) > 1 and is_sep(lines[1]) else [split_row(l) for l in lines[1:]]
    out = ['<div class="tablewrap"><table><thead><tr>']
    out += [f"<th>{md_inline(h)}</th>" for h in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def md_block(text):
    """Lists, tables, paragraphs, subheadings. Code blocks are shown as is."""
    lines = text.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.strip().startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            out.append('<pre class="code">' + esc("\n".join(lines[i + 1:j])) + "</pre>")
            i = j + 1
            continue
        if line.lstrip().startswith("|"):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            out.append(md_table(lines[i:j]))
            i = j
            continue
        hm = re.match(r"^(#{1,6})\s+(.*)", line)
        if hm:
            out.append(f'<p class="subhead">{md_inline(hm.group(2))}</p>')
            i += 1
            continue
        lm = re.match(r"^\s*(\d+[.)]|[-*])\s+(.*)", line)
        if lm:
            ordered = lm.group(1)[0].isdigit()
            items = []
            while i < len(lines):
                m2 = re.match(r"^\s*(\d+[.)]|[-*])\s+(.*)", lines[i])
                if m2:
                    items.append([m2.group(2)])
                elif lines[i].strip() and (lines[i].startswith("  ") or lines[i].startswith("\t")) and items:
                    items[-1].append(lines[i].strip())
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{md_inline(' '.join(it))}</li>" for it in items) + f"</{tag}>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(\s*(\d+[.)]|[-*])\s|#|\s*\||```)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        if not para:  # defensive exit
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{md_inline(' '.join(para))}</p>")
    return "\n".join(out)


def sections(text):
    """Split markdown into (level, heading, body, line number)."""
    res, cur = [], None
    for n, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if cur:
                res.append(cur)
            cur = [len(m.group(1)), m.group(2).strip(), [], n]
        elif cur:
            cur[2].append(line)
    if cur:
        res.append(cur)
    out = []
    for idx, (lvl, title, body, n) in enumerate(res):
        # a section body includes its subsections up to the next heading of the same or a higher level
        full = list(body)
        for lvl2, t2, b2, _ in res[idx + 1:]:
            if lvl2 <= lvl:
                break
            full.append("#" * lvl2 + " " + t2)
            full += b2
        out.append((lvl, title, "\n".join(full).strip(), n))
    return out


def tables_in(text):
    """All markdown tables of a file: list of (header, rows)."""
    res, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]):
            head = split_row(lines[i])
            j = i + 2
            rows = []
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            res.append((head, rows))
            i = j
        else:
            i += 1
    return res


# ---------- request data ----------

def status_tables(text):
    """All step tables with a "status" column, in order: [[(no., step, status)], ...]."""
    res = []
    for head, rows in tables_in(text):
        low = [h.lower() for h in head]
        if "status" in low and head and (head[0].split() or [""])[0] in ("#", "No", "No."):  # also "# (f18)"
            k = low.index("status")
            out = []
            for r in rows:
                if len(r) > k and r[0]:
                    out.append((r[0], re.sub(r"[*`]", "", r[1]) if len(r) > 1 else "", re.sub(r"[*`]", "", r[k])))
            res.append(out)
    return res


def status_table(text):
    t = status_tables(text)
    return t[0] if t else []


def merged_steps(harness_rows, log_text):
    """Steps from harness; the status comes from harness, and if it is not done there, from the last status
    table in log.md (the studio keeps statuses there), otherwise it is noted that log.md has a section about this step."""
    log_status = {}
    for table in status_tables(log_text):
        for num, _, st in table:
            if re.match(r"^\d+[a-z]?$", num.strip()):
                log_status[num.strip()] = st
    mentions = set(log_step_mentions(log_text)) if log_text else set()
    out = []
    for num, name, st in harness_rows:
        key = num.strip()
        if "done" in st.lower() or "skip" in st.lower():
            out.append((key, name, st, "harness"))
        elif key in log_status:
            out.append((key, name, log_status[key], "log"))
        elif key.isdigit() and int(key) in mentions:
            out.append((key, name, "entry in log.md", "log-mention"))
        else:
            out.append((key, name, st, "harness"))
    return out


def step_counts(rows):
    done = sum(1 for _, _, s in rows if "done" in s.lower())
    skipped = sum(1 for _, _, s in rows if "skip" in s.lower() and "done" not in s.lower())
    return done, skipped, len(rows)


def log_step_mentions(text):
    nums = set()
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        for m in re.finditer(r"[Ss]teps?\s+(\d+)(?:\s*[-–]\s*(\d+))?", line):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            nums.update(range(a, b + 1) if b >= a and b - a < 40 else [a])
    return sorted(nums)


def brief_summary(text):
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, flags=re.S)
    for lvl, title, sec, _ in sections(body):
        if "what is needed" in title.lower():
            para = sec.split("\n\n")[0]
            para = re.sub(r"\s+", " ", para).strip()
            return para[:260] + ("…" if len(para) > 260 else "")
    return ""


def thumb_data_uri(path):
    if Image is None:
        ISSUES.append(f"Pillow is missing: cover {C.rel(path)} not embedded")
        return None
    try:
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((THUMB, THUMB))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=78, optimize=True)
            return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception as e:  # a broken file does not break the build
        ISSUES.append(f"cover {C.rel(path)} cannot be read: {e}")
        return None


def covers_of(unit_dir):
    fd = C.final_dir(unit_dir)
    if not fd:
        return []
    files = []
    if (fd / "covers").is_dir():
        files += sorted(p for p in (fd / "covers").iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    files += sorted(p for p in fd.glob("cover_*") if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    by_stem = {}
    for p in files:  # one cover per name, jpg preferred over png
        key = (p.parent, p.stem)
        if key not in by_stem or p.suffix.lower() in (".jpg", ".jpeg"):
            by_stem[key] = p
    picked = sorted(by_stem.values())[:MAX_COVERS]
    out = []
    for p in picked:
        uri = thumb_data_uri(p)
        if uri:
            out.append({"name": p.name, "path": C.rel(p), "uri": uri})
    return out


def publications_of(unit_dir):
    p = unit_dir / "publications.md"
    if not p.is_file():
        return None
    rows = []
    for head, body in tables_in(C.read(p)):
        low = [h.lower() for h in head]
        if "platform" in low and "status" in low:
            ip, ist = low.index("platform"), low.index("status")
            iu = next((k for k, h in enumerate(low) if h.startswith("url")), None)
            idt = next((k for k, h in enumerate(low) if "date" in h), None)
            for r in body:
                rows.append({
                    "platform": r[ip] if len(r) > ip else "",
                    "status": r[ist] if len(r) > ist else "",
                    "url": (r[iu] if iu is not None and len(r) > iu else "").strip(),
                    "date": (r[idt] if idt is not None and len(r) > idt else "").strip(),
                })
    if not rows:
        ISSUES.append(f"{C.rel(p)}: no table with \"platform\" and \"status\" columns")
    return {"path": C.rel(p), "rows": rows}


def unit_stage(r, pubs):
    if not r["has_production"]:
        return "not started", "idle"
    v = (r["verdict"] or "").upper()
    if pubs and pubs["rows"]:
        if any(x["url"] for x in pubs["rows"]):
            return "published", "ok"
        return "publish kit ready", "ok"
    if v.startswith("FAIL"):
        return "QC: FAIL", "bad"
    if v.startswith("PASS"):
        return "passed QC", "ok"
    if r["finals"]:
        return "awaiting review", "warn"
    return "in production", "warn"


def collect_units(client_dir, cost):
    by_id = {r["id"]: r for r in cost["rows"]}
    units = []
    for uid, udir, kind, week in C.find_units(client_dir):
        r = by_id[uid]
        harness = C.read(udir / "harness.md")
        log_p = C.prod_dir(udir) / "log.md"
        log = C.read(log_p)
        h_rows = status_table(harness)
        pubs = publications_of(udir)
        stage, tone = unit_stage(r, pubs)
        if harness and not h_rows:
            ISSUES.append(f"{uid}: no step table with a \"status\" column found in harness.md")
        units.append({
            **r, "kind": kind, "week": week,
            "brief": brief_summary(C.read(udir / "brief.md")),
            "harness_rows": h_rows, "harness_path": C.rel(udir / "harness.md") if harness else None,
            "steps": merged_steps(h_rows, log), "log_path": C.rel(log_p) if log else None,
            "covers": covers_of(udir), "pubs": pubs, "stage": stage, "tone": tone,
            "budget": str(C.frontmatter(harness).get("budget_credits") or C.frontmatter(C.read(udir / "brief.md")).get("budget_credits") or ""),
        })
    return units


# ---------- questions and answers ----------

Q_HEAD = re.compile(r"(?i)(question|to the human|to the client)")
Q_LINE = re.compile(r"(?i)(need to tell the human|put into the approval pack)")


def open_questions(client_dir):
    p = client_dir / "open-questions.md"
    if not p.is_file():
        return None
    groups = []
    for lvl, title, body, n in sections(C.read(p)):
        if lvl == 2:
            groups.append({"title": title, "html": md_block(body), "line": n})
    return {"path": C.rel(p), "groups": groups}


def unit_questions(units, client_dir):
    found = []
    for u in units:
        udir = C.ROOT / u["dir"]
        files = [udir / "harness.md", C.prod_dir(udir) / "review.md", C.prod_dir(udir) / "log.md"]
        for f in files:
            text = C.read(f)
            if not text:
                continue
            for lvl, title, body, n in sections(text):
                if lvl >= 2 and Q_HEAD.search(title) and body:
                    found.append({"unit": u["id"], "src": f"{C.rel(f)}:{n}", "title": title, "html": md_block(body)})
            last = None
            for n, line in enumerate(text.splitlines(), 1):
                if not line.startswith("#") and Q_LINE.search(line):
                    last = (n, line)
            if last:
                found.append({"unit": u["id"], "src": f"{C.rel(f)}:{last[0]}", "title": "\"Tell the human\" line",
                              "html": md_block(re.sub(r"^\s*(\d+[.)]|[-*])\s+", "", last[1]))})
    return found


UNRESOLVED = re.compile(r"(?i)(not decided|undecided|unresolved|awaiting|waiting|no answer|open)")


def decisions(units):
    answered, pending = [], []
    for u in units:
        p = C.ROOT / u["dir"] / "decisions.md"
        if not p.is_file():
            continue
        tabs = tables_in(C.read(p))
        if not tabs:
            ISSUES.append(f"{C.rel(p)}: decisions table not found")
        for head, rows in tabs:
            for r in rows:
                date = r[0] if r else ""
                joined = " ".join(r)
                item = {"unit": u["id"], "src": C.rel(p), "head": head, "row": r}
                if date.strip() in ("", "—", "-") or UNRESOLVED.search(joined):
                    pending.append(item)
                else:
                    answered.append(item)
    return answered, pending


def confirmed(client_dir):
    p = client_dir / "memory" / "confirmed-answers.md"
    if not p.is_file():
        return None
    tabs = tables_in(C.read(p))
    rows = tabs[0][1] if tabs else []
    head = tabs[0][0] if tabs else []
    return {"path": C.rel(p), "head": head, "rows": [r for r in rows if any(c.strip() for c in r)]}


# ---------- plan, competitors, metrics ----------

def weeks_plans(client_dir):
    return [p for p in sorted((client_dir / "weeks").glob("*/01-plan.md"))]


def targeting(client_dir):
    p = client_dir / "memory" / "targeting-map.md"
    if not p.is_file():
        return None
    tabs = tables_in(C.read(p))
    filled = []
    for head, rows in tabs:
        for r in rows:
            if any(c.strip() for c in r[1:]):
                filled.append(r)
    return {"path": C.rel(p), "head": tabs[0][0] if tabs else [], "rows": filled,
            "dims": [r[0] for head, rows in tabs for r in rows]}


def hooks(client_dir):
    p = client_dir / "memory" / "hooks-library.yaml"
    if not p.is_file():
        return None
    data = {}
    if yaml is not None:
        try:
            data = yaml.safe_load(C.read(p)) or {}
        except yaml.YAMLError as e:
            ISSUES.append(f"{C.rel(p)}: YAML cannot be parsed ({e})")
    types = data.get("types") or {}
    out = []
    for key, v in types.items():
        v = v or {}
        stats = v.get("stats") or {}
        out.append({"key": key, "title": v.get("title", key), "example": v.get("example") or "", "stats": stats})
    return {"path": C.rel(p), "types": out}


def find_refs(obj, path=""):
    """All references keys in channels.yaml: [(path, group, [links])]."""
    res = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if k == "references" and isinstance(v, dict):
                for g, links in v.items():
                    if isinstance(links, list):
                        res.append((path, g, [str(x) for x in links]))
            elif k == "references" and isinstance(v, list):
                res.append((path, "", [str(x) for x in v]))
            else:
                res += find_refs(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            res += find_refs(v, f"{path}[{i}]")
    return res


def references(client_dir):
    files = [p for p in sorted((client_dir / "references").rglob("*")) if p.is_file()]
    ch = client_dir / "channels.yaml"
    refs = []
    if ch.is_file() and yaml is not None:
        try:
            refs = find_refs(yaml.safe_load(C.read(ch)) or {})
        except yaml.YAMLError as e:
            ISSUES.append(f"{C.rel(ch)}: YAML cannot be parsed ({e})")
    trends = [p for p in sorted((client_dir / "trends").glob("*.md")) if p.name.lower() != "readme.md"]
    return files, refs, C.rel(ch), trends


def jsonl(p):
    rows, bad = [], 0
    if not p.is_file():
        return None, 0
    for line in C.read(p).splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
    if bad:
        ISSUES.append(f"{C.rel(p)}: {bad} lines could not be parsed as JSON")
    return rows, bad


# ---------- HTML ----------

CSS = """
/* Layout: summary header, chip navigation, then sections top to bottom; video cards in a grid, a single column on phones. */
:root {
  --bg: #eef1ee; --surface: #ffffff; --sunk: #e4e9e4; --ink: #17201b; --muted: #56635b; --line: #d3dbd4;
  --accent: #2a5f80; --accent-ink: #ffffff; --ok: #2c7443; --ok-bg: #e2f1e6; --warn: #925c00; --warn-bg: #f8ecd2;
  --bad: #a8352a; --bad-bg: #f8e3df; --idle: #5d6670; --idle-bg: #e7eaed;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans", "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, "SFMono-Regular", Menlo, Consolas, "Liberation Mono", monospace;
  --r: 10px;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #111613; --surface: #19201c; --sunk: #141a16; --ink: #e3e9e4; --muted: #9aa79f; --line: #2b352f;
  --accent: #7db3d6; --accent-ink: #0d1a22; --ok: #74c98f; --ok-bg: #1b3324; --warn: #e5ad4a; --warn-bg: #3a2c12;
  --bad: #f08a7c; --bad-bg: #3d1f1b; --idle: #a8b1ba; --idle-bg: #262c31; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #111613; --surface: #19201c; --sunk: #141a16; --ink: #e3e9e4; --muted: #9aa79f; --line: #2b352f;
  --accent: #7db3d6; --accent-ink: #0d1a22; --ok: #74c98f; --ok-bg: #1b3324; --warn: #e5ad4a; --warn-bg: #3a2c12;
  --bad: #f08a7c; --bad-bg: #3d1f1b; --idle: #a8b1ba; --idle-bg: #262c31; color-scheme: dark; }
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 15px/1.5 var(--sans); }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 20px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
a { color: var(--accent); }
a:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
code, .mono { font-family: var(--mono); font-size: .86em; }
code { background: var(--sunk); padding: .05em .35em; border-radius: 4px; overflow-wrap: anywhere; }
h1, h2, h3 { text-wrap: balance; line-height: 1.2; margin: 0; }
h1 { font-size: clamp(1.5rem, 1.1rem + 1.6vw, 2.1rem); font-weight: 750; letter-spacing: -.01em; }
h2 { font-size: 1.3rem; font-weight: 700; }
h3 { font-size: 1.02rem; font-weight: 700; }
p { margin: 0; }
.eyebrow { font-size: .74rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.muted { color: var(--muted); }
.small { font-size: .86rem; }
header.top { display: grid; gap: 14px; padding-bottom: 18px; border-bottom: 1px solid var(--line); }
.meta { display: flex; flex-wrap: wrap; gap: 6px 18px; color: var(--muted); font-size: .88rem; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.kpi { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); padding: 12px 14px; display: grid; gap: 2px; }
.kpi b { font-size: 1.45rem; font-variant-numeric: tabular-nums; font-weight: 700; }
.kpi span { color: var(--muted); font-size: .84rem; }
nav.toc { display: flex; flex-wrap: wrap; gap: 6px; }
nav.toc a { text-decoration: none; color: var(--ink); background: var(--sunk); border: 1px solid var(--line); padding: 4px 10px; border-radius: 999px; font-size: .86rem; }
nav.toc a:hover { border-color: var(--accent); color: var(--accent); }
nav.toc a .n { color: var(--muted); font-variant-numeric: tabular-nums; margin-left: 4px; }
section.block { padding-top: 34px; display: grid; gap: 14px; scroll-margin-top: 12px; }
.sechead { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px; }
.src { color: var(--muted); font-size: .8rem; font-family: var(--mono); overflow-wrap: anywhere; }
.empty { border: 1px dashed var(--line); border-radius: var(--r); padding: 14px 16px; color: var(--muted); background: transparent; }
.empty strong { color: var(--ink); font-weight: 600; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 360px), 1fr)); gap: 14px; align-items: start; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); padding: 16px; display: grid; gap: 12px; min-width: 0; }
.card-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; flex-wrap: wrap; }
.uid { font-family: var(--mono); font-weight: 700; font-size: .98rem; }
.pill { display: inline-flex; align-items: center; gap: 6px; font-size: .78rem; font-weight: 650; padding: 3px 9px; border-radius: 999px; max-width: 100%; }
.card-head .pill { white-space: nowrap; }
.pill::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.t-ok { color: var(--ok); background: var(--ok-bg); } .t-warn { color: var(--warn); background: var(--warn-bg); }
.t-bad { color: var(--bad); background: var(--bad-bg); } .t-idle { color: var(--idle); background: var(--idle-bg); }
dl.kv { display: grid; grid-template-columns: max-content 1fr; gap: 6px 12px; margin: 0; font-size: .9rem; }
dl.kv dt { color: var(--muted); }
dl.kv dd { margin: 0; min-width: 0; overflow-wrap: anywhere; }
.num { font-variant-numeric: tabular-nums; }
.bar { height: 6px; border-radius: 3px; background: var(--sunk); overflow: hidden; margin-top: 4px; }
.bar { display: flex; }
.bar i { display: block; height: 100%; background: var(--accent); }
.bar i.b2 { background: var(--warn); opacity: .55; }
ol.steps { margin: 0; padding: 0; list-style: none; display: grid; gap: 4px; font-size: .84rem; }
ol.steps li { display: flex; flex-wrap: wrap; gap: 4px 8px; align-items: baseline; }
ol.steps .pill { font-size: .72rem; padding: 1px 7px; }
.covers { display: flex; flex-wrap: wrap; gap: 8px; }
.covers figure { margin: 0; display: grid; gap: 4px; width: 92px; }
.covers img { width: 92px; height: auto; max-width: 100%; border-radius: 6px; border: 1px solid var(--line); background: var(--sunk); display: block; }
.covers figcaption { font-size: .7rem; color: var(--muted); font-family: var(--mono); overflow-wrap: anywhere; line-height: 1.25; }
ul.paths { margin: 0; padding: 0; list-style: none; display: grid; gap: 3px; }
ul.paths li { font-family: var(--mono); font-size: .76rem; overflow-wrap: anywhere; color: var(--ink); }
details { border-top: 1px solid var(--line); padding-top: 8px; }
details > summary { cursor: pointer; color: var(--accent); font-size: .88rem; font-weight: 600; }
details[open] > summary { margin-bottom: 8px; }
.tablewrap { overflow-x: auto; max-width: 100%; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: .86rem; }
th, td { text-align: left; vertical-align: top; padding: 7px 10px; border-bottom: 1px solid var(--line); }
th { background: var(--sunk); font-weight: 650; white-space: nowrap; }
tbody tr:last-child td { border-bottom: 0; }
td.mono { white-space: nowrap; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tfoot td { font-weight: 700; background: var(--sunk); }
.q { background: var(--surface); border: 1px solid var(--line); border-left: 3px solid var(--warn); border-radius: 8px; padding: 12px 14px; display: grid; gap: 8px; min-width: 0; }
.q.answered { border-left-color: var(--ok); }
.q .qhead { display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: baseline; }
.prose { display: grid; gap: 8px; font-size: .92rem; min-width: 0; }
.prose ol, .prose ul { margin: 0; padding-left: 1.3em; display: grid; gap: 5px; }
.prose .subhead { font-weight: 700; margin-top: 4px; }
.prose pre.code { margin: 0; padding: 10px; background: var(--sunk); border-radius: 6px; overflow-x: auto; font: .8rem/1.4 var(--mono); }
.stack { display: grid; gap: 10px; }
.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: 14px; align-items: start; }
.note { font-size: .84rem; color: var(--muted); }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font-size: .8rem; padding: 3px 9px; border-radius: 999px; background: var(--sunk); border: 1px solid var(--line); }
footer { margin-top: 40px; padding-top: 14px; border-top: 1px solid var(--line); color: var(--muted); font-size: .82rem; display: grid; gap: 6px; }
@media (max-width: 520px) { dl.kv { grid-template-columns: 1fr; gap: 0 0; } dl.kv dd { margin-bottom: 6px; } }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
html { scroll-behavior: smooth; }
"""


def empty(what, when):
    return f'<div class="empty"><strong>{esc(what)}</strong> Will appear when {esc(when)}.</div>'


def sec(id_, title, src, inner, count=None):
    cnt = f' <span class="muted num">· {count}</span>' if count is not None else ""
    srcs = "".join(f'<span class="src">{esc(s)}</span>' for s in (src if isinstance(src, list) else [src]) if s)
    return (f'<section class="block" id="{id_}"><div class="sechead"><h2>{esc(title)}{cnt}</h2>{srcs}</div>'
            f"{inner}</section>")


def fmt_cr(x):
    return "no data" if x is None else C.fmt_num(x) + " cr."


def unit_card(u):
    rows = []
    rows.append(("Format", f'<span class="mono">{esc(u["flow"] or "no data")}</span>'))
    # steps
    h_done, h_skip, h_total = step_counts(u["harness_rows"])
    steps = u["steps"]
    if steps:
        d = sum(1 for s in steps if "done" in s[2].lower())
        sk = sum(1 for s in steps if "skip" in s[2].lower() and "done" not in s[2].lower())
        men = sum(1 for s in steps if s[3] == "log-mention")
        t = len(steps)
        pct = int(100 * (d + sk) / t)
        pct2 = int(100 * men / t)
        steps_html = (f'<span class="num">{d} of {t} done</span>' + (f", {sk} skipped" if sk else "") +
                      (f", {men} more with a log.md entry but no status" if men else "") +
                      f'<div class="bar" aria-hidden="true"><i style="width:{pct}%"></i><i class="b2" style="width:{pct2}%"></i></div>')
        if h_done < d + sk:
            steps_html += (f'<span class="note">harness.md marks {h_done} of {h_total}; '
                           f'the other statuses are taken from the studio\'s log.md.</span>')
        tone = lambda s: "t-ok" if "done" in s.lower() else ("t-idle" if "skip" in s.lower() else ("t-warn" if "log" in s.lower() else "t-idle"))
        steps_html += ('<details><summary>Steps in order</summary><ol class="steps">' + "".join(
            f'<li><span class="mono">{esc(n)}</span> {esc(name)} <span class="pill {tone(st)}">{esc(st[:60])}</span></li>'
            for n, name, st, _ in steps) + "</ol></details>")
    else:
        steps_html = '<span class="muted">no harness.md yet; it will appear when the director picks a flow</span>'
    rows.append(("Steps", steps_html))
    if u["verdict"]:
        vt = "t-ok" if u["verdict"].upper().startswith("PASS") else ("t-bad" if u["verdict"].upper().startswith("FAIL") else "t-warn")
        rows.append(("QC", f'<span class="pill {vt}">{esc(u["verdict"])}</span>'))
    else:
        rows.append(("QC", f'<span class="muted">{"no verdict in review.md" if u["verdict_src"] else "no review.md yet"}</span>'))
    cr = fmt_cr(u["credits"])
    usd = C.fmt_usd(u["usd"]) if u["usd"] is not None else ""
    budget = f' <span class="note">· budget: {esc(u["budget"])}</span>' if u["budget"] else ""
    rows.append(("Spend", f'<span class="num">{esc(cr)}{(" · " + esc(usd)) if usd else ""}</span>{budget}'))
    # publishing
    if u["pubs"] and u["pubs"]["rows"]:
        chips = "".join(f'<span class="chip">{esc(x["platform"])}: {esc(x["status"])}'
                        f'{(" · " + esc(x["date"])) if x["date"] and x["date"] != "—" else ""}</span>' for x in u["pubs"]["rows"])
        rows.append(("Publishing", f'<div class="chips">{chips}</div>'))
    else:
        rows.append(("Publishing", '<span class="muted">not published (no publications.md)</span>'))
    kv = "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in rows)
    covers = ""
    if u["covers"]:
        covers = '<div class="covers">' + "".join(
            f'<figure><img src="{c["uri"]}" alt="Cover {esc(c["name"])}" loading="lazy"><figcaption>{esc(c["name"])}</figcaption></figure>'
            for c in u["covers"]) + "</div>"
    files = ""
    if u["light"] or u["finals"]:
        li = "".join(f"<li>{esc(p)}</li>" for p in u["light"]) or "<li class='muted'>no light copies</li>"
        fi = "".join(f"<li>{esc(p)}</li>" for p in u["finals"])
        files = (f'<div class="stack"><span class="eyebrow">Light copies for viewing</span><ul class="paths">{li}</ul></div>'
                 f'<details><summary>Master files ({len(u["finals"])})</summary><ul class="paths">{fi}</ul></details>')
    elif u["has_production"]:
        files = '<p class="muted small">No final videos yet; they will appear when the studio finishes rendering.</p>'
    brief = f'<p class="small">{md_inline(u["brief"])}</p>' if u["brief"] else ""
    where = esc(u["dir"]) + (f" · week {esc(u['week'])}" if u["week"] else "")
    return (f'<article class="card" id="u-{esc(u["id"])}"><div class="card-head"><div><div class="uid">{esc(u["id"])}</div>'
            f'<div class="src">{where}</div></div><span class="pill t-{u["tone"]}">{esc(u["stage"])}</span></div>'
            f'{brief}<dl class="kv">{kv}</dl>{covers}{files}</article>')


def render(client, passport, commit, built, cost, units, oq, uq, dec_ans, dec_pend, conf, plans, tmap, hk,
           refs_files, refs_links, ch_path, trends, registry, scores, costs_md_path, costs_md_exists):
    name = passport.get("name") or client
    n_q = (sum(len(re.findall(r"<li>", g["html"])) for g in oq["groups"]) if oq else 0) + len(dec_pend)
    n_videos = sum(len(u["finals"]) for u in units)
    out = []
    title = f"Dashboard: {name}" if len(str(name).split()) <= 3 else f"Dashboard: {client}"
    out.append("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
               "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">"
               f"<title>{esc(title)}</title>")
    out.append('<meta name="claude:viewport-fit-sides" content="cover">')
    out.append(f"<style>{CSS}</style></head><body><div class=\"wrap\">")

    toc = [("units", "Videos and requests", len(units)), ("waiting", "Waiting for your answer", None),
           ("answers", "Answers and decisions", None), ("plan", "Plan and topics", None),
           ("refs", "Competitors and trends", None), ("metrics", "Metrics", None), ("costs", "Spend", None)]
    out.append('<header class="top">')
    out.append(f'<div class="eyebrow">Content factory · client {esc(client)}</div><h1>{esc(name)}: everything on one screen</h1>')
    out.append(f'<div class="meta"><span>Built: <b class="num">{esc(built)}</b></span>'
               f'<span>Commit: <code>{esc(commit)}</code></span><span>Files: <code>clients/{esc(client)}/</code></span></div>')
    out.append('<div class="kpis">'
               f'<div class="kpi"><b>{len(units)}</b><span>requests and videos in progress</span></div>'
               f'<div class="kpi"><b>{n_videos}</b><span>final videos (without light copies)</span></div>'
               f'<div class="kpi"><b>{n_q}</b><span>open questions to the client and unanswered decisions</span></div>'
               f'<div class="kpi"><b>{esc(C.fmt_num(cost["total_credits"]))} cr.</b><span>spent · {esc(C.fmt_usd(cost["total_usd"]))}'
               + (f'; no data: {len(cost["unknown"])}' if cost["unknown"] else "") + '</span></div></div>')
    out.append('<nav class="toc" aria-label="Sections">' + "".join(
        f'<a href="#{i}">{esc(t)}{f"<span class=n>{c}</span>" if c is not None else ""}</a>' for i, t, c in toc) + "</nav>")
    out.append("</header>")

    # 1. Videos and requests
    if units:
        inner = '<div class="grid">' + "".join(unit_card(u) for u in units) + "</div>"
        inner += ('<p class="note">Steps come from the harness.md table; if a step is not marked there, the status is taken from the last '
                  'status table in the studio\'s log.md. The verdict is the last "verdict:" line in review.md.</p>')
    else:
        inner = empty("No requests or videos yet.", "a folder appears in requests/ or weeks/<W>/04-production/")
    out.append(sec("units", "Videos and requests", [f"clients/{client}/requests/*", f"clients/{client}/weeks/*/04-production/*"], inner, len(units)))

    # 2. Waiting for an answer
    parts = []
    if oq and oq["groups"]:
        parts.append('<h3>Open questions to the client</h3><p class="src">' + esc(oq["path"]) + "</p>")
        parts.append('<div class="cols">' + "".join(
            f'<div class="q"><div class="qhead"><b>{esc(g["title"])}</b><span class="src">line {g["line"]}</span></div>'
            f'<div class="prose">{g["html"]}</div></div>' for g in oq["groups"]) + "</div>")
    else:
        parts.append(empty("open-questions.md is missing or empty.", "the onboarding agent writes the questions to the client"))
    parts.append("<h3>Unanswered decisions (decisions.md)</h3>")
    if dec_pend:
        parts.append('<div class="stack">' + "".join(
            f'<div class="q"><div class="qhead"><b>{esc(d["unit"])}</b><span class="src">{esc(d["src"])}</span></div>'
            f'<div class="prose"><p>{" · ".join(md_inline(c) for c in d["row"] if c.strip())}</p></div></div>' for d in dec_pend) + "</div>")
    else:
        parts.append(empty("No unresolved rows in decisions.md.", "decisions.md gets a row with no date or marked \"undecided\""))
    parts.append("<h3>Questions from request harness, review and log files</h3>")
    if uq:
        parts.append('<p class="note">Found by headings containing "question", "to the human", "to the client" and by lines '
                     '"need to tell the human". Some may already be closed; check against the "Answers and decisions" section.</p>')
        parts.append('<div class="stack">' + "".join(
            f'<details class="q"><summary>{esc(q["unit"])} · {esc(q["title"])}</summary>'
            f'<p class="src">{esc(q["src"])}</p><div class="prose">{q["html"]}</div></details>' for q in uq) + "</div>")
    else:
        parts.append(empty("No question sections in the request files.", "the director or reviewer writes a \"Questions to the human\" section"))
    out.append(sec("waiting", "Waiting for your answer", "", "".join(parts)))

    # 3. Answers and decisions
    parts = []
    parts.append("<h3>Confirmed answers</h3>")
    if conf and conf["rows"]:
        parts.append(f'<p class="src">{esc(conf["path"])}</p>' + md_table(
            ["| " + " | ".join(conf["head"]) + " |", "|" + "---|" * len(conf["head"])] +
            ["| " + " | ".join(r) + " |" for r in conf["rows"]]))
    else:
        parts.append(empty("No confirmed answers yet.", "the client answers and the answer is recorded in memory/confirmed-answers.md"))
    parts.append("<h3>Decisions per request</h3>")
    if dec_ans:
        by_unit = {}
        for d in dec_ans:
            by_unit.setdefault((d["unit"], d["src"], tuple(d["head"])), []).append(d["row"])
        for (unit, src, head), rows in by_unit.items():
            parts.append(f'<div class="stack"><div class="qhead"><b class="mono">{esc(unit)}</b> <span class="src">{esc(src)}</span></div>' + md_table(
                ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]) + "</div>")
    else:
        parts.append(empty("No decisions yet.", "a human answers on a request and the orchestrator writes requests/<id>/decisions.md"))
    out.append(sec("answers", "Answers and decisions", "", "".join(parts)))

    # 4. Publishing plan and topics
    parts = ["<h3>Weekly plan</h3>"]
    if plans:
        parts.append('<ul class="paths">' + "".join(f"<li>{esc(C.rel(p))}</li>" for p in plans) + "</ul>")
        for p in plans[-2:]:
            parts.append(f'<details><summary>{esc(C.rel(p))}</summary><div class="prose">{md_block(C.read(p))}</div></details>')
    else:
        parts.append(empty("No weekly plans yet (the weeks/ folder is empty).", "the producer and orchestrator start the first weekly cycle and write weeks/<W>/01-plan.md"))
    parts.append("<h3>Publications per request</h3>")
    pub_rows = [(u["id"], x, u["pubs"]["path"]) for u in units if u["pubs"] for x in u["pubs"]["rows"]]
    if pub_rows:
        t = ['<div class="tablewrap"><table><thead><tr><th>request</th><th>platform</th><th>status</th><th>date</th><th>URL</th></tr></thead><tbody>']
        for uid, x, _ in pub_rows:
            url = x["url"]
            url_html = (f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(url)}</a>' if url.startswith("http") else (esc(url) or '<span class="muted">—</span>'))
            t.append(f'<tr><td class="mono">{esc(uid)}</td><td>{esc(x["platform"])}</td><td>{md_inline(x["status"])}</td><td>{esc(x["date"] or "—")}</td><td>{url_html}</td></tr>')
        t.append("</tbody></table></div>")
        parts.append("".join(t))
        parts.append('<p class="note">"kit_ready" means the manual publish kit is ready but the post is not out yet. '
                     'The publisher fills in the link after publishing.</p>')
    else:
        parts.append(empty("No publications yet.", "the publisher prepares a kit and writes requests/<id>/publications.md"))
    parts.append('<div class="cols">')
    if tmap and tmap["rows"]:
        parts.append(f'<div class="stack"><h3>Targeting map</h3><p class="src">{esc(tmap["path"])}</p>' + md_table(
            ["| " + " | ".join(tmap["head"]) + " |", "|" + "---|" * len(tmap["head"])] + ["| " + " | ".join(r) + " |" for r in tmap["rows"]]) + "</div>")
    else:
        dims = ", ".join(tmap["dims"]) if tmap else ""
        parts.append('<div class="stack"><h3>Targeting map</h3>' + (f'<p class="src">{esc(tmap["path"])}</p>' if tmap else "") +
                     empty(f"The map is empty{(' (' + dims.lower() + ')') if dims else ''}.", "metrics of the first publications arrive and the analyst runs the retro") + "</div>")
    if hk and any(t["stats"] or t["example"] for t in hk["types"]):
        rows = "".join(f'<tr><td>{esc(t["title"])}</td><td>{esc(t["example"] or "—")}</td><td class="mono small">{esc(json.dumps(t["stats"], ensure_ascii=False)) if t["stats"] else "—"}</td></tr>' for t in hk["types"])
        parts.append(f'<div class="stack"><h3>Hook library</h3><p class="src">{esc(hk["path"])}</p><div class="tablewrap"><table><thead><tr><th>type</th><th>example</th><th>stats</th></tr></thead><tbody>{rows}</tbody></table></div></div>')
    elif hk:
        chips = "".join(f'<span class="chip">{esc(t["title"])}</span>' for t in hk["types"])
        parts.append(f'<div class="stack"><h3>Hook library</h3><p class="src">{esc(hk["path"])}</p><div class="chips">{chips}</div>'
                     + empty(f"Types: {len(hk['types'])}, no examples or stats yet.", "posts go out and the analyst updates the stats at the retro") + "</div>")
    else:
        parts.append('<div class="stack"><h3>Hook library</h3>' + empty("hooks-library.yaml is missing.", "the analyst creates memory/hooks-library.yaml") + "</div>")
    parts.append("</div>")
    out.append(sec("plan", "Publishing plan and topics", "", "".join(parts)))

    # 5. Competitors and trends
    parts = ['<div class="cols">']
    ref_body = []
    for p in refs_files:
        txt = C.read(p)
        todo = "TODO" in txt
        ref_body.append(f'<details{" open" if len(refs_files) == 1 else ""}><summary>{esc(C.rel(p))}{" · has TODO" if todo else ""}</summary>'
                        f'<div class="prose">{md_block(txt)}</div></details>')
    links_html = ""
    if refs_links:
        groups = []
        for path, g, links in refs_links:
            label = {"own": "own examples", "other": "other accounts' examples"}.get(g, g or "links")
            groups.append(f'<p class="small"><b>{esc(path)}</b> · {esc(label)} ({len(links)})</p><ul class="paths">' +
                          "".join(f'<li><a href="{esc(l)}" target="_blank" rel="noopener">{esc(l)}</a></li>' for l in links) + "</ul>")
        links_html = f'<p class="src">{esc(ch_path)} -> references</p>' + "".join(groups)
    parts.append('<div class="stack"><h3>References</h3>' + (links_html or "") + "".join(ref_body) +
                 ("" if refs_links else empty("No list of reference accounts.", "the analyst fills in references/accounts.md")) + "</div>")
    if trends:
        parts.append('<div class="stack"><h3>Trends</h3>' + "".join(
            f'<details><summary>{esc(C.rel(p))}</summary><div class="prose">{md_block(C.read(p))}</div></details>' for p in trends) + "</div>")
    else:
        parts.append('<div class="stack"><h3>Trends</h3>' + empty("No trend reports yet (only a README in trends/).",
                                                                  "the analyst runs trend-scout and writes trends/<YYYY-Www>.md") + "</div>")
    parts.append("</div>")
    out.append(sec("refs", "Competitors and trends", [f"clients/{client}/references/", f"clients/{client}/trends/"], "".join(parts)))

    # 6. Metrics
    parts = []
    reg_rows, _ = registry
    sc_rows, _ = scores
    if reg_rows:
        keys = []
        for r in reg_rows:
            for k in r:
                if k not in keys:
                    keys.append(k)
        keys = keys[:7]
        t = ['<div class="tablewrap"><table><thead><tr>' + "".join(f"<th>{esc(k)}</th>" for k in keys) + "</tr></thead><tbody>"]
        for r in reg_rows[-30:]:
            t.append("<tr>" + "".join(f"<td>{esc(r.get(k, ''))}</td>" for k in keys) + "</tr>")
        t.append("</tbody></table></div>")
        parts.append(f"<h3>Publication registry · {len(reg_rows)}</h3>" + "".join(t))
    else:
        parts.append(empty("The publication registry is empty (analytics/registry.jsonl has no rows).",
                           "the first post goes out and the publisher writes a row to registry.jsonl"))
    if sc_rows:
        keys = [k for k in ("post_id", "channel", "format", "metric", "value", "multiplier", "label") if any(k in r for r in sc_rows)] or list(sc_rows[0].keys())[:7]
        t = ['<div class="tablewrap"><table><thead><tr>' + "".join(f"<th>{esc(k)}</th>" for k in keys) + "</tr></thead><tbody>"]
        for r in sc_rows[-30:]:
            t.append("<tr>" + "".join(f"<td>{esc(r.get(k, ''))}</td>" for k in keys) + "</tr>")
        t.append("</tbody></table></div>")
        parts.append(f"<h3>Post scores · {len(sc_rows)}</h3>" + "".join(t))
    else:
        parts.append(empty("No post scores (analytics/scores.jsonl has not been created yet).",
                           "the collectors take metrics and scripts/analytics/baseline.py computes the channel baselines"))
    out.append(sec("metrics", "Metrics", [f"clients/{client}/analytics/registry.jsonl", f"clients/{client}/analytics/scores.jsonl"], "".join(parts)))

    # 7. Spend
    t = ['<div class="tablewrap"><table><thead><tr><th>request</th><th>format</th><th class="num">credits</th><th class="num">$</th>'
         '<th>QC verdict</th><th>versions / hooks</th><th class="num">$ per video</th></tr></thead><tbody>']
    for r in cost["rows"]:
        t.append(f'<tr><td class="mono">{esc(r["id"])}</td><td class="mono small">{esc(r["flow"] or "no data")}</td>'
                 f'<td class="num">{esc(C.fmt_num(r["credits"]))}</td><td class="num">{esc(C.fmt_usd(r["usd"]))}</td>'
                 f'<td>{esc(C.verdict_text(r))}</td><td class="small">{esc(C.versions_text(r))}</td>'
                 f'<td class="num">{esc(C.fmt_usd(r["usd_per_video"])) if r["finals"] else "—"}</td></tr>')
    t.append(f'</tbody><tfoot><tr><td>Total</td><td></td><td class="num">{esc(C.fmt_num(cost["total_credits"]))}</td>'
             f'<td class="num">{esc(C.fmt_usd(cost["total_usd"]))}</td><td colspan="2">final videos with known spend: {cost["total_videos_with_cost"]}</td>'
             f'<td class="num">{esc(C.fmt_usd(cost["usd_per_video_avg"]))}</td></tr></tfoot></table></div>')
    rate = cost["rate"]
    notes = [f'Rate: 1 credit = {("$" + str(rate)) if rate is not None else "no data"} ({esc(cost["rate_src"])}).']
    if cost["unknown"]:
        notes.append(f'No spend data: {esc(", ".join(cost["unknown"]))}; not included in the total, nothing was estimated.')
    notes.append("\"$ per video\" = request $ / final videos in final/; light copies and old revisions are not counted.")
    notes.append(f"The same calculation is written to {esc(costs_md_path)}" + ("" if costs_md_exists else " (file not built yet: run scripts/analytics/costs.py)") + ".")
    srcs = "".join(f'<li><b class="mono">{esc(r["id"])}</b>: {esc(r["credits_src"])}</li>' for r in cost["rows"])
    inner = "".join(t) + '<div class="stack">' + "".join(f'<p class="note">{n}</p>' for n in notes) + \
        f'<details><summary>Where the numbers come from</summary><ul class="paths">{srcs}</ul></details></div>'
    out.append(sec("costs", "Spend", costs_md_path, inner))

    issues = "".join(f"<li>{esc(i)}</li>" for i in ISSUES) or "<li>everything parsed</li>"
    out.append(f'<footer><span>This page was built by scripts/dashboard/build.py from repository files. It publishes nothing. '
               f'To refresh it, run the script again.</span><details><summary>What could not be parsed ({len(ISSUES)})</summary>'
               f'<ul class="paths">{issues}</ul></details></footer>')
    out.append("</div></body></html>\n")
    return "\n".join(out)


def git_commit():
    try:
        return subprocess.run(["git", "-C", str(C.ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=10).stdout.strip() or "no git"
    except (OSError, subprocess.SubprocessError):
        return "no git"


def main():
    ap = argparse.ArgumentParser(description="Build a single HTML screen for a client")
    ap.add_argument("--client", required=True)
    ap.add_argument("--repo", help="repository root (default: two levels above the script)")
    ap.add_argument("--out", help="output file (default: dashboard/<client>.html)")
    args = ap.parse_args()
    if args.repo:
        C.set_root(args.repo)
    client_dir = C.ROOT / "clients" / args.client
    if not client_dir.is_dir():
        raise SystemExit(f"no such client: {client_dir}")
    passport = C.frontmatter("---\n" + C.read(client_dir / "passport.yaml") + "\n---\n") if yaml is None else \
        (yaml.safe_load(C.read(client_dir / "passport.yaml")) or {})
    cost = C.collect(args.client)
    units = collect_units(client_dir, cost)
    oq = open_questions(client_dir)
    uq = unit_questions(units, client_dir)
    dec_ans, dec_pend = decisions(units)
    conf = confirmed(client_dir)
    refs_files, refs_links, ch_path, trends = references(client_dir)
    costs_md = client_dir / "analytics" / "costs.md"
    page = render(args.client, passport, git_commit(), datetime.now().strftime("%Y-%m-%d %H:%M"), cost, units, oq, uq,
                  dec_ans, dec_pend, conf, weeks_plans(client_dir), targeting(client_dir), hooks(client_dir),
                  refs_files, refs_links, ch_path, trends,
                  jsonl(client_dir / "analytics" / "registry.jsonl"), jsonl(client_dir / "analytics" / "scores.jsonl"),
                  C.rel(costs_md), costs_md.is_file())
    out = Path(args.out) if args.out else C.ROOT / "dashboard" / f"{args.client}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    size = out.stat().st_size
    print(f"written: {out} ({size / 1024:.0f} KB)")
    if size > 5 * 1024 * 1024:
        print("WARNING: larger than 5 MB")
    for i in ISSUES:
        print("  not parsed:", i)


if __name__ == "__main__":
    main()
