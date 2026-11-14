"""Summary "Client videos" for Google Drive (HTML -> Google Doc via the Drive connector).

Usage: python3 scripts/dashboard/drive_summary.py --client demo [--out path]
       [--repo-url https://github.com/<owner>/<repo>] [--branch <branch>]
Writes HTML (default dashboard/<client>_drive.html). The main session uploads it:
Google Drive create_file / update_file, contentMimeType text/html (converted to a Google Doc).
Videos are not uploaded to Drive: links point to files on GitHub (masters in Git LFS, light copies in git).
The repository URL defaults to `git config remote.origin.url` and the branch to the current branch.
"""
import argparse
import html
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analytics"))
import costs  # noqa: E402

REPO_URL = "{repo}/blob/{branch}/{path}"
TITLES = {
    "f04-object-insert-broll": "AI object appears in real footage",
    "f08-many-to-one": "Edit from real footage",
    "f10-infographic": "Infographic + carousel",
    "f11-comic-cartoon": "Cartoon / caricature character",
    "f13-avatar": "AI presenter talks to camera",
    "f17-product-commercial": "Product showcase video",
}


def git_out(*args):
    try:
        return subprocess.run(["git", "-C", str(costs.ROOT), *args], capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def default_repo_url():
    """Browsable https URL of the origin remote (git@host:owner/repo.git -> https://host/owner/repo)."""
    url = git_out("config", "remote.origin.url")
    if url.startswith("git@") and ":" in url:
        host, path = url[4:].split(":", 1)
        url = f"https://{host}/{path}"
    elif url.startswith("ssh://git@"):
        url = "https://" + url[len("ssh://git@"):]
    return url[:-4] if url.endswith(".git") else url


def default_branch():
    return git_out("rev-parse", "--abbrev-ref", "HEAD") or "main"


def esc(s):
    return html.escape(str(s)) if s is not None else "—"


def title_of(flow):
    if not flow:
        return "—"
    for k, v in TITLES.items():
        if k in flow:
            return v
    return flow


def brief_line(unit_dir):
    p = costs.ROOT / unit_dir / "brief.md"
    if not p.exists():
        return ""
    body = p.read_text(encoding="utf-8").split("---", 2)[-1]
    for line in body.splitlines():
        line = line.strip()
        line = line.replace("**", "")
        if line and not line.startswith("#"):
            return line[:220] + ("…" if len(line) > 220 else "")
    return ""


def link(path, branch, label=None):
    url = REPO_URL.format(repo=REPO_BASE, branch=branch, path=path)
    return f'<a href="{esc(url)}">{esc(label or Path(path).name)}</a>'


REPO_BASE = ""  # set in main(): --repo-url or origin remote


def build(client, branch):
    d = costs.collect(client)
    tracked = set(subprocess.run(["git", "-C", str(costs.ROOT), "ls-files", f"clients/{client}"],
                                 capture_output=True, text=True).stdout.splitlines())
    usd = lambda v: "no data" if v is None else f"${v:.2f}"
    num = lambda v: "no data" if v is None else f"{v:g}"
    out = [f"<h1>Videos: {esc(client)}</h1>",
           f"<p>Updated: {esc(d['generated'])}. Rate: 1 credit = ${d['rate']} "
           f"(config/pricing.yaml). Videos live on GitHub (branch {esc(branch)}): master files are in Git LFS, "
           f"light copies for viewing are in final/light/. The dashboard with all details is the \"Dashboard\" artifact.</p>",
           "<h2>Summary</h2>",
           "<table border='1' cellpadding='4'><tr><th>Request</th><th>Format</th><th>QC status</th>"
           "<th>Credits</th><th>$</th><th>Videos</th><th>$ per video</th></tr>"]
    for r in d["rows"]:
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in [
            esc(r["id"]), esc(title_of(r["flow"])), esc(r["verdict"] or "not checked yet"),
            num(r["credits"]), usd(r["usd"]), len(r["finals"]),
            usd(r["usd_per_video"]) if r["finals"] else "—"]) + "</tr>")
    out.append(f"<tr><td><b>Total</b></td><td></td><td></td><td><b>{num(d['total_credits'])}</b></td>"
               f"<td><b>{usd(d['total_usd'])}</b></td><td>{d['total_videos_with_cost']}</td>"
               f"<td>{usd(d['usd_per_video_avg'])}</td></tr></table>")
    if d["unknown"]:
        out.append(f"<p>Spend not calculated yet (in progress): {esc(', '.join(d['unknown']))}.</p>")
    out.append("<h2>By request</h2>")
    for r in d["rows"]:
        out.append(f"<h3>{esc(r['id'])} — {esc(title_of(r['flow']))}</h3>")
        b = brief_line(r["dir"])
        if b:
            out.append(f"<p>{esc(b)}</p>")
        out.append(f"<p>QC: {esc(r['verdict'] or 'not checked yet')}. Spend: {num(r['credits'])} cr. "
                   f"= {usd(r['usd'])}.</p>")
        if r["light"]:
            out.append("<p>Watch (light copies): " + ", ".join(link(p, branch) for p in r["light"]) + "</p>")
        stored = [p for p in r["finals"] if p in tracked]
        if stored:
            out.append("<p>Master files: " + ", ".join(link(p, branch) for p in stored) + "</p>")
        elif r["finals"]:
            out.append("<p>Master files will be stored after they pass QC.</p>")
        if not r["light"] and not r["finals"]:
            out.append("<p>No finished videos yet.</p>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Video summary for Google Drive")
    ap.add_argument("--client", required=True)
    ap.add_argument("--repo-url", help="https URL of the repository (default: git config remote.origin.url)")
    ap.add_argument("--branch", help="branch the links point to (default: the current branch)")
    ap.add_argument("--out")
    a = ap.parse_args()
    global REPO_BASE
    REPO_BASE = (a.repo_url or default_repo_url()).rstrip("/")
    a.branch = a.branch or default_branch()
    out = Path(a.out) if a.out else costs.ROOT / "dashboard" / f"{a.client}_drive.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(a.client, a.branch), encoding="utf-8")
    print(f"written: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
