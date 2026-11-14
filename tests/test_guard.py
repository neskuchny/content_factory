"""Tests for scripts/guard/guard.py, the PreToolUse hook that locks framework files per agent role.

The guard is run as a subprocess with the hook JSON on stdin (as Claude Code does). Because the
guard derives ROOT from its own location and appends every decision to ROOT/.cache/guard.log, the
tests copy guard.py and config/permissions-matrix.yaml into a throw-away root, so the repository
tree is never touched. The copied files are byte-identical to the shipped ones.

Protected globs and role globs are read from the shipped matrix at run time, so these tests follow
the matrix when it changes; a handful of hard-coded invariants guard against the matrix itself
being weakened.

Exit codes: 0 = allow, 2 = block.
"""
import concurrent.futures
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SHIPPED_GUARD = REPO / "scripts" / "guard" / "guard.py"
SHIPPED_MATRIX = REPO / "config" / "permissions-matrix.yaml"

ALLOW, DENY = 0, 2

with SHIPPED_MATRIX.open(encoding="utf-8") as _f:
    MATRIX = yaml.safe_load(_f)
PROTECTED = MATRIX["protected"]
READ_DENY = MATRIX["read_deny"]
ROLES = MATRIX["roles"]

# Files that must stay locked no matter how the matrix is edited.
INVARIANT_PROTECTED = [
    "CLAUDE.md",
    ".claude/settings.json",
    ".claude/agents/producer.md",
    ".claude/skills/dispatch/SKILL.md",
    "config/permissions-matrix.yaml",
    "scripts/guard/guard.py",
    "scripts/ticks/precheck.py",
    "flows/f00-text-only.md",
    "templates/client/passport.yaml",
    ".mcp.json",
    ".github/workflows/ci.yml",
    "clients/demo/passport.yaml",
    "clients/demo/permissions.yaml",
    "clients/demo/product-base/products.md",
    "clients/demo/brand/consents.md",
    "clients/demo/analytics/snapshots.jsonl",
    "clients/demo/analytics/baselines.json",
    "clients/demo/analytics/scores.jsonl",
]

ROOT = None  # throw-away root, set in setUpModule
_TMP = None


def setUpModule():
    global ROOT, _TMP
    _TMP = tempfile.mkdtemp(prefix="guard-test-")
    ROOT = Path(_TMP).resolve()
    (ROOT / "scripts" / "guard").mkdir(parents=True)
    (ROOT / "config").mkdir()
    shutil.copy2(SHIPPED_GUARD, ROOT / "scripts" / "guard" / "guard.py")
    shutil.copy2(SHIPPED_MATRIX, ROOT / "config" / "permissions-matrix.yaml")


def tearDownModule():
    shutil.rmtree(_TMP, ignore_errors=True)


# --------------------------------------------------------------------------- helpers

def concretize(glob):
    """Turn a matrix glob into one concrete path it must match."""
    p = glob
    if p.startswith("**/"):
        p = "zz/" + p[3:]
    if p.endswith("/**"):
        p = p[:-3] + "/zz/sample.md"
    return p.replace("*", "demo")


def glob_regex(glob):
    """Independent oracle: '*' stays inside one path segment, '**' crosses segments."""
    s = re.escape(glob)
    s = s.replace(r"\*\*/", "(?:.*/)?")
    s = s.replace(r"/\*\*", "(?:/.*)?")
    s = s.replace(r"\*", "[^/]*")
    return re.compile(s)


def matches_any(path, globs):
    return any(glob_regex(g).fullmatch(path) for g in globs or [])


def expected_role_decision(role, path):
    """What the matrix says should happen when `role` writes `path`."""
    if matches_any(path, PROTECTED):
        return DENY
    spec = ROLES[role]
    if matches_any(path, spec.get("except")):
        return DENY
    return ALLOW if matches_any(path, spec.get("write")) else DENY


def lax_match(path, globs):
    """Mirror of the guard's own matcher: fnmatch, where '*' also crosses '/'."""
    for p in globs or []:
        if p.startswith("**/") and lax_match(path, [p[3:]]):
            return True
        if fnmatch.fnmatchcase(path, p) or (p.endswith("/**") and (path == p[:-3] or path.startswith(p[:-2]))):
            return True
    return False


def lax_role_decision(role, path):
    if lax_match(path, PROTECTED):
        return DENY
    spec = ROLES[role]
    if lax_match(path, spec.get("except")):
        return DENY
    return ALLOW if lax_match(path, spec.get("write")) else DENY


def run_guard(tool, tool_input, agent=None, env=None, cwd=None, root=None):
    """Run the guard once. Returns (exit_code, stderr)."""
    root = root or ROOT
    payload = {"tool_name": tool, "tool_input": tool_input, "cwd": str(cwd or root)}
    if agent:
        payload["agent_type"] = agent
    full_env = {k: v for k, v in os.environ.items() if k != "FACTORY_MODE"}
    full_env.update(env or {})
    proc = subprocess.run(
        [sys.executable, "-I", str(root / "scripts" / "guard" / "guard.py")],
        input=json.dumps(payload), text=True, capture_output=True,
        cwd=str(root), env=full_env, timeout=60,
    )
    return proc.returncode, proc.stderr


def write(path, agent=None, **kw):
    return run_guard("Write", {"file_path": path, "content": "x"}, agent=agent, **kw)[0]


def bash(cmd, agent=None, **kw):
    return run_guard("Bash", {"command": cmd}, agent=agent, **kw)[0]


def read(path, agent=None, **kw):
    return run_guard("Read", {"file_path": path}, agent=agent, **kw)[0]


def protected_paths():
    seen, out = set(), []
    for p in [concretize(g) for g in PROTECTED] + INVARIANT_PROTECTED:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# --------------------------------------------------------------------------- the matrix itself

class MatrixContract(unittest.TestCase):
    def test_invariants_are_covered_by_protected_globs(self):
        for p in INVARIANT_PROTECTED:
            with self.subTest(path=p):
                self.assertTrue(matches_any(p, PROTECTED), f"{p} is not covered by `protected` in the matrix")

    def test_secrets_are_read_denied(self):
        for p in (".env", ".env.local", "secrets/key.txt", "clients/demo/secrets/token.txt", "a/b/.env"):
            with self.subTest(path=p):
                self.assertTrue(matches_any(p, READ_DENY))

    def test_every_agent_file_has_a_role(self):
        names = set()
        for f in sorted((REPO / ".claude" / "agents").glob("*.md")):
            m = re.search(r"^name:\s*(\S+)", f.read_text(encoding="utf-8"), re.M)
            self.assertIsNotNone(m, f"{f.name} has no name: in its front matter")
            names.add(m.group(1))
        self.assertTrue(names, "no agents found")
        self.assertEqual(sorted(names - set(ROLES)), [], "agents without a role in the permissions matrix")

    def test_no_role_may_write_the_guard_itself(self):
        for role in ROLES:
            for target in ("scripts/guard/guard.py", "config/permissions-matrix.yaml", ".claude/settings.json"):
                with self.subTest(role=role, path=target):
                    self.assertEqual(expected_role_decision(role, target), DENY)

    def test_shipped_guard_is_what_we_run(self):
        self.assertEqual((ROOT / "scripts" / "guard" / "guard.py").read_bytes(), SHIPPED_GUARD.read_bytes())


# --------------------------------------------------------------------------- owner

class OwnerMode(unittest.TestCase):
    """Main session without agent_type and without FACTORY_MODE=run."""

    def test_owner_can_write_every_protected_file(self):
        for p in protected_paths():
            with self.subTest(path=p):
                self.assertEqual(write(p), ALLOW)

    def test_owner_can_write_ordinary_files(self):
        for p in ("README.md", "clients/demo/weeks/2027-W02/01-plan.md", "docs/new-doc.md"):
            with self.subTest(path=p):
                self.assertEqual(write(p), ALLOW)

    def test_owner_cannot_write_or_read_secrets(self):
        secrets = (".env", ".env.local", ".env.production", "secrets/key.txt",
                   "clients/demo/secrets/token.txt", "clients/demo/brand/secrets/x.json", "a/b/.env")
        for p in secrets:
            with self.subTest(path=p, tool="Write"):
                self.assertEqual(write(p), DENY)
            with self.subTest(path=p, tool="Read"):
                self.assertEqual(read(p), DENY)

    def test_owner_secrets_denied_for_all_write_tools(self):
        for tool, key in (("Edit", "file_path"), ("MultiEdit", "file_path"), ("NotebookEdit", "notebook_path")):
            with self.subTest(tool=tool):
                rc, _ = run_guard(tool, {key: ".env"})
                self.assertEqual(rc, DENY)

    def test_owner_bash_redirect_into_secrets_denied(self):
        self.assertEqual(bash("echo TOKEN=1 > .env"), DENY)
        self.assertEqual(bash("echo TOKEN=1 >> clients/demo/secrets/t.txt"), DENY)

    def test_owner_bash_into_protected_allowed(self):
        self.assertEqual(bash("echo hi > CLAUDE.md"), ALLOW)

    def test_owner_may_write_outside_repo(self):
        self.assertEqual(write("/etc/zz-guard-test"), ALLOW)

    def test_factory_mode_other_than_run_is_still_owner(self):
        self.assertEqual(write("CLAUDE.md", env={"FACTORY_MODE": "interactive"}), ALLOW)
        self.assertEqual(write("CLAUDE.md", env={"FACTORY_MODE": ""}), ALLOW)


# --------------------------------------------------------------------------- protected layer vs roles

class ProtectedLayer(unittest.TestCase):
    def test_every_protected_glob_denies_every_role(self):
        jobs = [(role, p) for role in ROLES for p in protected_paths()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda j: write(j[1], agent=j[0]), jobs))
        for (role, p), rc in zip(jobs, results):
            with self.subTest(role=role, path=p):
                self.assertEqual(rc, DENY, f"{role} was allowed to write the protected path {p}")

    def test_protected_denied_for_all_write_tools(self):
        for tool, key in (("Write", "file_path"), ("Edit", "file_path"), ("MultiEdit", "file_path"),
                          ("NotebookEdit", "notebook_path")):
            for role in ("orchestrator", "onboarding", "studio"):
                with self.subTest(tool=tool, role=role):
                    rc, err = run_guard(tool, {key: "CLAUDE.md"}, agent=role)
                    self.assertEqual(rc, DENY)
                    self.assertIn("guard:", err)

    def test_onboarding_cannot_touch_locked_client_files(self):
        # onboarding may write clients/** but never the locked layer or permissions/analytics
        for p in ("clients/demo/passport.yaml", "clients/demo/permissions.yaml",
                  "clients/demo/product-base/products.md", "clients/demo/brand/consents.md",
                  "clients/demo/analytics/registry.jsonl", "clients/demo/analytics/whatever.md"):
            with self.subTest(path=p):
                self.assertEqual(write(p, agent="onboarding"), DENY)
        self.assertEqual(write("clients/demo/brand/voice.md", agent="onboarding"), ALLOW)
        self.assertEqual(write("clients/newco/channels.yaml", agent="onboarding"), ALLOW)

    def test_traversal_into_protected_is_denied(self):
        self.assertEqual(write("clients/demo/weeks/../../../CLAUDE.md", agent="producer"), DENY)
        self.assertEqual(write("./clients/demo/../demo/passport.yaml", agent="orchestrator"), DENY)

    def test_relative_path_resolves_against_cwd(self):
        cwd = ROOT / "clients" / "demo"
        cwd.mkdir(parents=True, exist_ok=True)
        self.assertEqual(write("passport.yaml", agent="onboarding", cwd=cwd), DENY)
        self.assertEqual(write("../../CLAUDE.md", agent="orchestrator", cwd=cwd), DENY)
        self.assertEqual(write("quotas.yaml", agent="orchestrator", cwd=cwd), ALLOW)

    def test_absolute_path_inside_root_is_checked_like_relative(self):
        self.assertEqual(write(str(ROOT / "CLAUDE.md"), agent="orchestrator"), DENY)
        self.assertEqual(write(str(ROOT / "clients/demo/weeks/2027-W02/01-plan.md"), agent="producer"), ALLOW)

    def test_deny_message_points_to_proposals(self):
        rc, err = run_guard("Write", {"file_path": "CLAUDE.md"}, agent="producer")
        self.assertEqual(rc, DENY)
        self.assertIn("proposals.md", err)

    def test_reading_protected_files_is_allowed_for_roles(self):
        for role in ("producer", "reviewer", "studio"):
            with self.subTest(role=role):
                self.assertEqual(read("CLAUDE.md", agent=role), ALLOW)
                self.assertEqual(read("clients/demo/permissions.yaml", agent=role), ALLOW)

    def test_secrets_unreadable_for_every_role(self):
        for role in ROLES:
            for p in (".env", "clients/demo/secrets/t.txt"):
                with self.subTest(role=role, path=p):
                    self.assertEqual(read(p, agent=role), DENY)


# --------------------------------------------------------------------------- role write permissions

class RoleWrites(unittest.TestCase):
    NEUTRAL = [
        "README.md",
        "docs/notes.md",
        "clients/demo/weeks/2027-W02/06-approval.md",
        "clients/demo/weeks/2027-W02/07-publications.md",
        "clients/demo/weeks/2027-W02/04-production/W02-R01/review.md",
        "clients/demo/weeks/2027-W02/04-production/W02-R01/harness.md",
        "clients/demo/requests/REQ-1/production/x.txt",
        "clients/demo/analytics/registry.jsonl",
        "clients/demo/memory/MEMORY.md",
        "clients/demo/quotas.yaml",
        "clients/demo/brand/voice.md",
        ".cache/x.json",
    ]

    @classmethod
    def probe_paths(cls):
        paths = []
        for spec in ROLES.values():
            paths += [concretize(g) for g in spec.get("write", [])]
        return sorted(set(paths + cls.NEUTRAL))

    @classmethod
    def lax_discrepancies(cls):
        """(role, path) pairs where the guard's '*'-crosses-'/' matching differs from the strict reading."""
        return [(r, p) for r in ROLES for p in cls.probe_paths()
                if lax_role_decision(r, p) != expected_role_decision(r, p)]

    def test_role_matrix_matches_oracle(self):
        skip = set(self.lax_discrepancies())  # covered by test_star_does_not_cross_directories
        jobs = [(role, p) for role in ROLES for p in self.probe_paths() if (role, p) not in skip]
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            results = list(ex.map(lambda j: write(j[1], agent=j[0]), jobs))
        for (role, p), rc in zip(jobs, results):
            want = expected_role_decision(role, p)
            with self.subTest(role=role, path=p, want=want):
                self.assertEqual(rc, want)

    # KNOWN GAP in scripts/guard/guard.py (reported, not fixed here): matching uses fnmatch, where
    # '*' also matches '/'. So `clients/*/references/**` (analyst) also matches
    # `clients/demo/brand/references/x.md` (feedback's), `clients/*/weeks/*/01-plan.md` matches
    # deeper paths, etc.: roles can write slightly more than the matrix says. The protected layer
    # is unaffected (it only gets broader). expectedFailure until the matcher is made segment-aware.
    @unittest.expectedFailure
    def test_star_does_not_cross_directories(self):
        self.assertEqual(self.lax_discrepancies(), [])

    def test_every_role_can_write_each_of_its_own_unprotected_globs(self):
        for role, spec in ROLES.items():
            for g in spec.get("write", []):
                p = concretize(g)
                if matches_any(p, PROTECTED) or matches_any(p, spec.get("except")):
                    continue
                with self.subTest(role=role, glob=g):
                    self.assertEqual(write(p, agent=role), ALLOW)

    def test_producer_examples(self):
        w = "clients/demo/weeks/2027-W02/"
        self.assertEqual(write(w + "01-plan.md", agent="producer"), ALLOW)
        self.assertEqual(write(w + "02-shoot-brief.md", agent="producer"), ALLOW)
        self.assertEqual(write(w + "03-scripts/W02-R01.md", agent="producer"), ALLOW)
        self.assertEqual(write("clients/demo/requests/REQ-1/brief.md", agent="producer"), ALLOW)
        self.assertEqual(write("CLAUDE.md", agent="producer"), DENY)
        self.assertEqual(write(w + "06-approval.md", agent="producer"), DENY)
        self.assertEqual(write(w + "04-production/W02-R01/harness.md", agent="producer"), DENY)

    def test_reviewer_may_only_write_review_md(self):
        base = "clients/demo/weeks/2027-W02/04-production/W02-R01/"
        self.assertEqual(write(base + "review.md", agent="reviewer"), ALLOW)
        self.assertEqual(write("clients/demo/requests/REQ-1/production/review.md", agent="reviewer"), ALLOW)
        for p in (base + "harness.md", base + "review.md.bak", base + "notes.md",
                  "clients/demo/weeks/2027-W02/01-plan.md", "README.md", "CLAUDE.md"):
            with self.subTest(path=p):
                self.assertEqual(write(p, agent="reviewer"), DENY)

    def test_publisher_cannot_edit_plans_or_scripts(self):
        w = "clients/demo/weeks/2027-W02/"
        self.assertEqual(write(w + "07-publications.md", agent="publisher"), ALLOW)
        self.assertEqual(write("clients/demo/analytics/registry.jsonl", agent="publisher"), ALLOW)
        self.assertEqual(write(w + "01-plan.md", agent="publisher"), DENY)
        self.assertEqual(write(w + "03-scripts/W02-R01.md", agent="publisher"), DENY)

    def test_only_publisher_writes_registry_and_nobody_writes_raw_metrics(self):
        for role in ROLES:
            if role != "publisher":
                with self.subTest(role=role):
                    self.assertEqual(write("clients/demo/analytics/registry.jsonl", agent=role), DENY)
            for raw in ("snapshots.jsonl", "baselines.json", "scores.jsonl"):
                with self.subTest(role=role, file=raw):
                    self.assertEqual(write(f"clients/demo/analytics/{raw}", agent=role), DENY)

    def test_quotas_only_orchestrator(self):
        for role in ROLES:
            want = ALLOW if role in ("orchestrator", "onboarding") else DENY
            with self.subTest(role=role):
                self.assertEqual(write("clients/demo/quotas.yaml", agent=role), want)

    def test_unknown_agent_type_is_denied(self):
        for agent in ("hacker", "general-purpose", "Producer", "producer ", "orchestrator2"):
            for p in ("clients/demo/weeks/2027-W02/01-plan.md", "README.md", "CLAUDE.md", ".cache/x"):
                with self.subTest(agent=agent, path=p):
                    self.assertEqual(write(p, agent=agent), DENY)

    def test_unknown_agent_message_names_the_agent(self):
        rc, err = run_guard("Write", {"file_path": "clients/demo/weeks/2027-W02/01-plan.md"}, agent="hacker")
        self.assertEqual(rc, DENY)
        self.assertIn("hacker", err)

    def test_unknown_agent_can_still_read_ordinary_files(self):
        self.assertEqual(read("README.md", agent="hacker"), ALLOW)


# --------------------------------------------------------------------------- Bash heuristics

class BashWrites(unittest.TestCase):
    DENIED_FOR_PRODUCER = [
        "echo hi > CLAUDE.md",
        "echo hi >> clients/demo/passport.yaml",
        "echo hi>clients/demo/permissions.yaml",
        "cat x | tee scripts/guard/guard.py",
        "echo hi | tee -a config/permissions-matrix.yaml",
        "sed -i 's/a/b/' CLAUDE.md",
        "sed -n p x && sed -i s/a/b/ clients/demo/brand/consents.md",
        "cp /tmp/x clients/demo/permissions.yaml",
        "cp -r /tmp/x templates/client",
        "mv /tmp/x .claude/settings.json",
        "rm CLAUDE.md",
        "rm -f flows/f00-text-only.md",
        "touch .github/workflows/x.yml",
        "install -m 644 /tmp/x flows/f99.md",
        "rsync -a /tmp/x/ templates/",
        "truncate -s 0 .mcp.json",
        "echo x > ./clients/../CLAUDE.md",
        "echo x > clients/demo/product-base/products.md",
        "echo x > clients/demo/weeks/2027-W02/06-approval.md",   # not the producer's file
        "echo x > /home/other/file",                             # outside the repo
        "cp clients/demo/passport.yaml /etc/zz-copy",            # outside the repo
    ]
    ALLOWED_FOR_PRODUCER = [
        "echo hi > clients/demo/weeks/2027-W02/01-plan.md",
        "echo hi >> clients/demo/memory/proposals.md",
        "cp /tmp/x clients/demo/weeks/2027-W02/03-scripts/W02-R01.md",
        "cat CLAUDE.md",
        "ls -la",
        "grep -n foo clients/demo/passport.yaml | head",
        "echo hi > /tmp/scratch.txt",
        "echo hi > /dev/null",
        "ls missing 2>/dev/null",
        "ls missing 2>&1 | head -3",
        "python3 -c 'print(1 >= 0)'",
        "cat a.txt | sort | uniq",
    ]

    def test_producer_denied(self):
        for cmd in self.DENIED_FOR_PRODUCER:
            with self.subTest(cmd=cmd):
                self.assertEqual(bash(cmd, agent="producer"), DENY)

    def test_producer_allowed(self):
        for cmd in self.ALLOWED_FOR_PRODUCER:
            with self.subTest(cmd=cmd):
                self.assertEqual(bash(cmd, agent="producer"), ALLOW)

    def test_bash_into_every_protected_path_denied_for_every_role(self):
        paths = protected_paths()
        jobs = [(role, p) for role in ROLES for p in paths[:: max(1, len(paths) // 6)]]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda j: bash(f"echo x > {j[1]}", agent=j[0]), jobs))
        for (role, p), rc in zip(jobs, results):
            with self.subTest(role=role, path=p):
                self.assertEqual(rc, DENY)

    def test_reviewer_bash_only_review_md(self):
        base = "clients/demo/weeks/2027-W02/04-production/W02-R01/"
        self.assertEqual(bash(f"echo PASS > {base}review.md", agent="reviewer"), ALLOW)
        self.assertEqual(bash(f"echo PASS > {base}harness.md", agent="reviewer"), DENY)
        self.assertEqual(bash("echo x > clients/demo/weeks/2027-W02/01-plan.md", agent="reviewer"), DENY)

    def test_studio_may_write_cache(self):
        self.assertEqual(bash("echo x > .cache/tmp.json", agent="studio"), ALLOW)
        self.assertEqual(bash("echo x > .cache/tmp.json", agent="reviewer"), DENY)

    def test_unknown_agent_bash_write_denied(self):
        self.assertEqual(bash("echo x > clients/demo/weeks/2027-W02/01-plan.md", agent="hacker"), DENY)

    def test_factory_scripts_may_be_run_by_everyone(self):
        for cmd in ("python3 scripts/ticks/precheck.py --client demo --no-network",
                    "python3 -I scripts/analytics/costs.py --client demo",
                    "bash scripts/ticks/run.sh"):
            for role in ("producer", "reviewer", "hacker"):
                with self.subTest(cmd=cmd, role=role):
                    self.assertEqual(bash(cmd, agent=role), ALLOW)

    # KNOWN GAP in scripts/guard/guard.py (reported, not fixed here): a command that merely STARTS
    # with `python3 scripts/(collect|analytics|ticks)/...` is whitelisted before any redirect or
    # chained command is inspected, so any role can append `> CLAUDE.md` or `; rm ...` to it.
    # These tests state the intended behaviour. They are marked expectedFailure so CI stays green
    # until the owner fixes the guard; once fixed they will report "unexpected success" and the
    # decorator must then be removed.
    @unittest.expectedFailure
    def test_factory_script_prefix_does_not_bypass_redirect_check(self):
        self.assertEqual(bash("python3 scripts/ticks/precheck.py > CLAUDE.md", agent="producer"), DENY)
        self.assertEqual(bash("python3 -I scripts/analytics/costs.py --client demo >> clients/demo/passport.yaml",
                              agent="reviewer"), DENY)

    @unittest.expectedFailure
    def test_factory_script_prefix_does_not_bypass_chained_commands(self):
        self.assertEqual(bash("python3 scripts/ticks/precheck.py; rm CLAUDE.md", agent="producer"), DENY)
        self.assertEqual(bash("python3 scripts/ticks/precheck.py && tee config/x.yaml", agent="producer"), DENY)


# --------------------------------------------------------------------------- outside the repository

class OutsideRepo(unittest.TestCase):
    def test_role_cannot_write_outside_repo(self):
        for p in ("/etc/zz-guard-test", "/home/other/file.txt", "/root/.bashrc", "/var/tmp/x", "/usr/local/bin/x"):
            for role in ("producer", "studio", "onboarding"):
                with self.subTest(role=role, path=p):
                    self.assertEqual(write(p, agent=role), DENY)

    def test_role_can_write_tmp(self):
        for role in ("producer", "reviewer", "studio"):
            with self.subTest(role=role):
                self.assertEqual(write("/tmp/zz-guard-test.txt", agent=role), ALLOW)

    # KNOWN GAP in scripts/guard/guard.py (reported, not fixed here): the /tmp exemption is a string
    # prefix check on the raw path, so `/tmp/../etc/x` passes. Same expectedFailure convention as above.
    @unittest.expectedFailure
    def test_tmp_prefix_does_not_allow_traversal_out_of_tmp(self):
        self.assertEqual(write("/tmp/../etc/zz-guard-test", agent="producer"), DENY)

    def test_role_can_write_dev_null(self):
        self.assertEqual(write("/dev/null", agent="reviewer"), ALLOW)

    def test_reading_outside_repo_is_allowed(self):
        self.assertEqual(read("/etc/hostname", agent="producer"), ALLOW)


# --------------------------------------------------------------------------- FACTORY_MODE=run

class FactoryModeRun(unittest.TestCase):
    RUN = {"FACTORY_MODE": "run"}

    def test_main_session_acts_as_orchestrator(self):
        w = "clients/demo/weeks/2027-W02/"
        for p in (w + "01-plan.md", w + "06-approval.md", "clients/demo/requests/REQ-1/brief.md",
                  "clients/demo/quotas.yaml", "clients/demo/channels.yaml", "clients/demo/memory/proposals.md"):
            with self.subTest(path=p):
                self.assertEqual(write(p, env=self.RUN), ALLOW)

    def test_run_mode_locks_protected_files_for_the_main_session(self):
        for p in protected_paths():
            with self.subTest(path=p):
                self.assertEqual(write(p, env=self.RUN), DENY)

    def test_run_mode_cannot_write_other_roles_files(self):
        for p in ("clients/demo/analytics/registry.jsonl", "clients/demo/brand/voice.md",
                  "clients/demo/memory/MEMORY.md", "README.md"):
            with self.subTest(path=p):
                self.assertEqual(write(p, env=self.RUN), DENY)
                self.assertEqual(write(p, env={}), ALLOW)  # the same write is fine for the owner

    def test_run_mode_bash(self):
        self.assertEqual(bash("echo x > CLAUDE.md", env=self.RUN), DENY)
        self.assertEqual(bash("echo x > clients/demo/weeks/2027-W02/01-plan.md", env=self.RUN), ALLOW)
        self.assertEqual(bash("echo x > /home/other/file", env=self.RUN), DENY)

    def test_run_mode_still_denies_secrets(self):
        self.assertEqual(write(".env", env=self.RUN), DENY)
        self.assertEqual(read("clients/demo/secrets/t.txt", env=self.RUN), DENY)

    def test_explicit_agent_type_wins_over_run_mode(self):
        self.assertEqual(write("clients/demo/weeks/2027-W02/01-plan.md", agent="reviewer", env=self.RUN), DENY)
        self.assertEqual(write("clients/demo/weeks/2027-W02/01-plan.md", agent="producer", env=self.RUN), ALLOW)


# --------------------------------------------------------------------------- failure modes and logging

class FailSafeAndLog(unittest.TestCase):
    def _bare_root(self, with_matrix):
        tmp = Path(tempfile.mkdtemp(prefix="guard-test-bare-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "scripts" / "guard").mkdir(parents=True)
        shutil.copy2(SHIPPED_GUARD, tmp / "scripts" / "guard" / "guard.py")
        if with_matrix:
            (tmp / "config").mkdir()
            (tmp / "config" / "permissions-matrix.yaml").write_text(
                SHIPPED_MATRIX.read_text(encoding="utf-8"), encoding="utf-8")
        return tmp

    def test_missing_matrix_denies_roles_but_not_reads_or_owner(self):
        root = self._bare_root(with_matrix=False)
        rc, err = run_guard("Write", {"file_path": "clients/demo/weeks/2027-W02/01-plan.md"}, agent="producer", root=root)
        self.assertEqual(rc, DENY)
        self.assertIn("matrix", err)
        self.assertEqual(run_guard("Bash", {"command": "echo x > README.md"}, agent="producer", root=root)[0], DENY)
        self.assertEqual(run_guard("Read", {"file_path": "README.md"}, agent="producer", root=root)[0], ALLOW)
        self.assertEqual(run_guard("Write", {"file_path": "README.md"}, root=root)[0], ALLOW)

    def test_broken_matrix_denies_roles(self):
        root = self._bare_root(with_matrix=True)
        (root / "config" / "permissions-matrix.yaml").write_text("protected: [unclosed\n", encoding="utf-8")
        rc, _ = run_guard("Write", {"file_path": "clients/demo/weeks/2027-W02/01-plan.md"}, agent="producer", root=root)
        self.assertEqual(rc, DENY)

    def test_decisions_are_logged_under_the_root_cache(self):
        root = self._bare_root(with_matrix=True)
        run_guard("Write", {"file_path": "CLAUDE.md"}, agent="producer", root=root)
        run_guard("Write", {"file_path": "clients/demo/weeks/2027-W02/01-plan.md"}, agent="producer", root=root)
        log = root / ".cache" / "guard.log"
        self.assertTrue(log.is_file())
        entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([e["decision"] for e in entries], ["deny", "allow"])
        self.assertTrue(all(e["agent"] == "producer" for e in entries))
        self.assertIn("reason", entries[0])

    def test_unrelated_tools_are_allowed(self):
        for tool in ("Glob", "Grep", "WebFetch", "Task"):
            with self.subTest(tool=tool):
                rc, _ = run_guard(tool, {}, agent="producer")
                self.assertEqual(rc, ALLOW)


if __name__ == "__main__":
    unittest.main()
