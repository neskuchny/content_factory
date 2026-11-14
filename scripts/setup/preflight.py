#!/usr/bin/env python3
"""Machine check for the setup wizard (.claude/skills/setup): what is installed, what is missing,
and whether this checkout is the person's own copy or the public template.

Only reads: runs `--version` style commands and `git` queries, never installs or changes anything.
Prints a table (default) or JSON (--json). Exit code is 0 unless a REQUIRED item is missing (then 1),
so it can also gate a script.

    python3 scripts/setup/preflight.py
    python3 scripts/setup/preflight.py --json
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_REPO = "neskuchny/content_factory"   # the public template; client data must not go there
MIN_FREE_GB = 4


def run(*cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20, cwd=str(ROOT))
        return (p.stdout + p.stderr).strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def version_tuple(text):
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text or "")
    return tuple(int(x or 0) for x in m.groups()) if m else None


def item(name, level, ok, found, fix, unlocks=""):
    """level: required | recommended | optional."""
    return {"name": name, "level": level, "ok": bool(ok), "found": found or "not found",
            "fix": "" if ok else fix, "unlocks": unlocks}


def check_python():
    v = sys.version_info
    return item("python", "required", v >= (3, 10), f"{v.major}.{v.minor}.{v.micro}",
                "Install Python 3.10 or newer (3.12 recommended).")


def check_module(mod, pip_name, level, unlocks):
    ok = importlib.util.find_spec(mod) is not None
    return item(pip_name, level, ok, "installed" if ok else None,
                f"python3 -m pip install {pip_name}", unlocks)


def check_ffmpeg():
    out = run("ffmpeg", "-version")
    first = out.splitlines()[0] if out else ""
    v = version_tuple(first.split("Copyright")[0])
    # git builds ("ffmpeg version N-1234-g…") carry no release number: present counts as ok
    ok = bool(out) and (v is None or v >= (6, 1))
    return item("ffmpeg", "recommended", ok, first.split(" Copyright")[0] if out else None,
                "Install ffmpeg 6.1+ (macOS: brew install ffmpeg; Debian/Ubuntu: apt-get install -y ffmpeg).",
                "cutting, sound, export of every video")


def check_node():
    out = run("node", "--version")
    v = version_tuple(out)
    return item("node", "recommended", v and v >= (22, 0), out,
                "Install Node.js 22+ (nodejs.org or your package manager).",
                "videos rendered from HTML, three.js and HyperFrames")


def find_chromium():
    for exe in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if shutil.which(exe):
            return exe
    for base in (os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), "/opt/pw-browsers",
                 str(Path.home() / ".cache" / "ms-playwright"),
                 str(Path.home() / "Library" / "Caches" / "ms-playwright")):
        if base and Path(base).is_dir() and any(Path(base).glob("chromium*")):
            return f"Playwright browsers in {base}"
    mac = Path("/Applications/Google Chrome.app")
    return str(mac) if mac.exists() else None


def check_chromium():
    found = find_chromium()
    return item("chromium", "recommended", found, found,
                "npx playwright install chromium (or install Google Chrome).",
                "rendering code films frame by frame")


def check_disk():
    try:
        free = shutil.disk_usage(ROOT).free / 1024 ** 3
    except OSError:
        free = None
    return item("disk", "recommended", free is not None and free >= MIN_FREE_GB,
                f"{free:.1f} GB free" if free is not None else None,
                f"Free at least {MIN_FREE_GB} GB: rendering writes frames and video files.",
                "rendering")


def check_mcp():
    try:
        cfg = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        has = "higgsfield" in cfg.get("mcpServers", {})
    except (OSError, ValueError):
        has = False
    return item("higgsfield (MCP)", "optional", has, "listed in .mcp.json (account not checked)" if has else None,
                "Add the connector https://mcp.higgsfield.ai/mcp in Claude settings -> Connectors. "
                "Whether your account is connected can only be checked from inside Claude.",
                "AI images and video (paid credits on your own account)")


def git_state():
    inside = run("git", "rev-parse", "--is-inside-work-tree") == "true"
    origin = run("git", "remote", "get-url", "origin") if inside else None
    upstream = run("git", "remote", "get-url", "upstream") if inside else None
    name = run("git", "config", "user.name") if inside else None
    email = run("git", "config", "user.email") if inside else None
    branch = run("git", "branch", "--show-current") if inside else None
    if not inside:
        copy = "no-git"
    elif not origin:
        copy = "no-remote"
    elif UPSTREAM_REPO.lower() in origin.lower():
        copy = "template"
    else:
        copy = "own"
    return {"inside_git": inside, "origin": origin, "upstream": upstream, "branch": branch,
            "user_configured": bool(name and email), "copy": copy}


def git_items(g):
    advice = {
        "own": "",
        "template": "origin is the public template. Make your own private repository and point origin "
                    "to it (setup skill, stage 2) before you add client data.",
        "no-remote": "No remote yet. Create a private repository and add it as origin to keep your data.",
        "no-git": "This folder is not a git repository. Clone the factory with git.",
    }[g["copy"]]
    found = g["origin"] or g["copy"]
    if g["copy"] == "own":
        found += " (make sure it is private: a fork of a public repository is public)"
    out = [item("own copy", "recommended", g["copy"] == "own", found, advice,
                "saving your client data and history in your own private repository")]
    out.append(item("git identity", "recommended", g["user_configured"],
                    "configured" if g["user_configured"] else None,
                    'git config user.name "Your Name" && git config user.email you@example.com',
                    "commits"))
    return out


def check_mode():
    mode = os.environ.get("FACTORY_MODE", "")
    return item("interactive mode", "required", mode != "run", f"FACTORY_MODE={mode or '(unset)'}",
                "Setup is interactive: run it in a normal session, not with FACTORY_MODE=run "
                "(scheduled runs act as the orchestrator and may not write the locked layer).")


def cloud():
    return os.environ.get("CLAUDE_CODE_REMOTE", "").lower() == "true"


def active_client():
    try:
        return (ROOT / "config" / "active-client.txt").read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def clients():
    d = ROOT / "clients"
    return sorted(p.name for p in d.iterdir() if (p / "passport.yaml").is_file()) if d.is_dir() else []


def setups_in_progress():
    """Clients whose setup has started but not finished (drafts waiting, or a setup log with open items)."""
    d = ROOT / "clients"
    if not d.is_dir():
        return []
    def open_log(p):
        log = p / "memory" / "setup-log.md"
        return log.is_file() and "- [ ]" in log.read_text(encoding="utf-8", errors="replace")
    return sorted(p.name for p in d.iterdir()
                  if p.is_dir() and ((p / "setup" / "drafts").is_dir() or open_log(p)))


def collect():
    g = git_state()
    items = [check_python(), check_mode(),
             check_module("yaml", "pyyaml", "required", "every factory script"),
             check_module("PIL", "pillow", "optional", "cover thumbnails on the dashboard"),
             check_ffmpeg(), check_node(), check_chromium(), check_disk(), check_mcp(), *git_items(g)]
    ac = active_client()
    return {"items": items, "git": g, "cloud_session": cloud(), "active_client": ac, "clients": clients(),
            "setup_in_progress": setups_in_progress(),
            "needs_setup": ac in (None, "demo"),
            "required_missing": [i["name"] for i in items if i["level"] == "required" and not i["ok"]]}


def print_table(r):
    mark = {True: "ok ", False: "-- "}
    for i in r["items"]:
        line = f"{mark[i['ok']]} {i['name']:<17} {i['level']:<12} {i['found']}"
        print(line)
        if not i["ok"]:
            print(f"    fix: {i['fix']}")
            if i["unlocks"]:
                print(f"    needed for: {i['unlocks']}")
    print()
    print(f"clients: {', '.join(r['clients']) or 'none'}; active: {r['active_client'] or 'none'}")
    if r["setup_in_progress"]:
        print(f"setup in progress: {', '.join(r['setup_in_progress'])} (say \"continue setup\")")
    if r["cloud_session"]:
        print("cloud session: work in a session started on your own private repository; "
              "this container is temporary and pushes only to the session's repository.")
    if r["needs_setup"]:
        print("No own client is active yet: run the setup wizard (say \"set me up\" to Claude).")
    if r["required_missing"]:
        print(f"REQUIRED missing: {', '.join(r['required_missing'])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    a = ap.parse_args()
    r = collect()
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print_table(r)
    return 1 if r["required_missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
