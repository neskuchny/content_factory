#!/usr/bin/env python3
"""PreToolUse hook: checks an agent's file permissions against config/permissions-matrix.yaml.

Wired up in .claude/settings.json for Read|Edit|Write|NotebookEdit|Bash.
Input is JSON on stdin (tool_name, tool_input, agent_type, cwd).
Block = exit 2 with the reason on stderr; allow = exit 0.
Every decision is written to .cache/guard.log (for incident review).

Main session without agent_type:
  FACTORY_MODE=run  -> acts as orchestrator (scheduled runs);
  otherwise         -> owner (interactive human work); only secrets are denied.
"""
import fnmatch
import json
import os
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "config" / "permissions-matrix.yaml"
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def load_matrix():
    try:
        import yaml  # PyYAML
        return yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    except Exception as e:  # no matrix: fail safe, deny writes
        print(f"guard: cannot read the permissions matrix ({e})", file=sys.stderr)
        return None


def match(path, patterns):
    for p in patterns or []:
        if p.startswith("**/") and match(path, [p[3:]]):
            return p
        if fnmatch.fnmatchcase(path, p) or (p.endswith("/**") and (path == p[:-3] or path.startswith(p[:-2]))):
            return p
    return None


def rel(path, cwd):
    p = Path(path)
    if not p.is_absolute():
        p = Path(cwd or ROOT) / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return None  # outside the repository


def bash_write_targets(cmd):
    """Rough heuristic: files a Bash command writes to (>, >>, tee, sed -i, cp/mv/rm, truncate)."""
    # ">" and ">>" as redirection; comparisons ">=", "=>", "->" and ">>>" inside code are not writes
    targets = re.findall(r"(?<![<>=!\-])>>?(?![=>])\s*([^\s;&|]+)", cmd)
    try:
        toks = shlex.split(cmd)
    except ValueError:
        toks = cmd.split()
    for i, t in enumerate(toks):
        if t in ("tee", "truncate", "rm", "touch") or (t == "sed" and "-i" in toks[i:i + 4]):
            targets += [x for x in toks[i + 1:i + 6] if not x.startswith("-")][:3]
        if t in ("cp", "mv", "install", "rsync"):
            args = [x for x in toks[i + 1:] if not x.startswith("-")]
            if args:
                targets.append(args[-1])
    # shell operators and trailing ";" are not files (otherwise false denials such as "write to |")
    clean = []
    for t in targets:
        t = t.strip().rstrip(";&)")
        if t and t not in ("/dev/null", "&1", "&2", "|", "||", "&&", "-") and not t.startswith(("&", "|")):
            clean.append(t)
    return clean


def log(entry):
    try:
        (ROOT / ".cache").mkdir(exist_ok=True)
        with (ROOT / ".cache" / "guard.log").open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def deny(reason, entry):
    entry["decision"] = "deny"
    entry["reason"] = reason
    log(entry)
    print(f"guard: {reason}", file=sys.stderr)
    sys.exit(2)


def main():
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd")
    agent = data.get("agent_type") or ""
    mode = os.environ.get("FACTORY_MODE", "")
    if not agent:
        agent = "orchestrator" if mode == "run" else "owner"
    entry = {"agent": agent, "tool": tool}

    m = load_matrix()
    if m is None and agent == "owner":
        sys.exit(0)
    if m is None:
        if tool in WRITE_TOOLS or tool == "Bash":
            deny("permissions matrix unavailable", entry)
        sys.exit(0)

    # paths touched by the call
    if tool == "Bash":
        cmd = ti.get("command", "")
        entry["cmd"] = cmd[:200]
        paths, writing = bash_write_targets(cmd), True
        # factory scripts (collectors, calculations) may be run by everyone: they write their own files
        if re.match(r"^\s*(python3|bash)\s+(-I\s+)?scripts/(collect|analytics|ticks)/", cmd):
            log({**entry, "decision": "allow", "reason": "factory script"})
            sys.exit(0)
    else:
        p = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
        paths, writing = ([p] if p else []), tool in WRITE_TOOLS

    for raw in paths:
        r = rel(raw, cwd)
        entry["path"] = r or raw
        if r is None:
            if writing and agent != "owner" and not str(raw).startswith(("/tmp/", "/dev/")):
                deny(f"{agent}: writing outside the repository is not allowed ({raw})", entry)
            continue
        if match(r, m.get("read_deny")):
            deny(f"{agent}: access to {r} is denied (secrets)", entry)
        if not writing:
            continue
        if agent == "owner":
            continue
        if match(r, m.get("protected")):
            deny(f"{agent}: {r} is in the locked layer; only a human may change it. "
                 f"Write a proposal to clients/<c>/memory/proposals.md", entry)
        role = (m.get("roles") or {}).get(agent)
        if role is None:
            deny(f"agent {agent} is not defined in the permissions matrix", entry)
        if match(r, role.get("except")):
            deny(f"{agent}: {r} is excluded from the role's permissions", entry)
        if not match(r, role.get("write")):
            deny(f"{agent}: no write permission for {r}. Allowed: {', '.join(role.get('write') or [])}", entry)

    log({**entry, "decision": "allow"})
    sys.exit(0)


if __name__ == "__main__":
    main()
