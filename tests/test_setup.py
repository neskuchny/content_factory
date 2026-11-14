"""Tests for the first-run path: scripts/setup/preflight.py, scripts/setup/new_client.py and the
`setup` skill wiring (CLAUDE.md first-run rule, README entry points).

new_client.py is run against a throw-away copy of templates/ (its hidden --root option), so the
repository tree is never touched.
"""
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
PREFLIGHT = REPO / "scripts" / "setup" / "preflight.py"
NEW_CLIENT = REPO / "scripts" / "setup" / "new_client.py"
APPLY = REPO / "scripts" / "setup" / "apply_drafts.py"
LOCKED = ("passport.yaml", "permissions.yaml", "brand/consents.md", "product-base/")


def run(script, *args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                          capture_output=True, text=True, timeout=60, env=env, cwd=str(REPO))


class Preflight(unittest.TestCase):
    def test_json_report_has_the_documented_shape(self):
        p = run(PREFLIGHT, "--json")
        self.assertIn(p.returncode, (0, 1), p.stderr)
        r = json.loads(p.stdout)
        self.assertTrue({"items", "git", "active_client", "clients", "needs_setup", "required_missing"} <= set(r))
        names = {i["name"] for i in r["items"]}
        for n in ("python", "pyyaml", "ffmpeg", "node", "own copy"):
            self.assertIn(n, names)
        for i in r["items"]:
            self.assertIn(i["level"], ("required", "recommended", "optional"))
            if not i["ok"]:
                self.assertTrue(i["fix"], f"{i['name']} is missing but has no fix hint")
        self.assertIn(r["git"]["copy"], ("own", "template", "no-remote", "no-git"))
        self.assertIn("demo", r["clients"])
        # exit code follows the required items only
        self.assertEqual(p.returncode, 1 if r["required_missing"] else 0)

    def test_table_mode_and_help(self):
        p = run(PREFLIGHT)
        self.assertIn("python", p.stdout)
        self.assertIn("clients:", p.stdout)
        h = run(PREFLIGHT, "--help")
        self.assertEqual(h.returncode, 0)
        self.assertIn("usage:", h.stdout.lower())

    def test_preflight_only_reads(self):
        before = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO).stdout
        run(PREFLIGHT, "--json")
        after = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO).stdout
        self.assertEqual(before, after)


class NewClient(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="new-client-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.root, True)
        shutil.copytree(REPO / "templates", self.root / "templates")

    def make(self, *args):
        return run(NEW_CLIENT, "--root", self.root, "--language", "en", *args) if "--language" not in args else run(NEW_CLIENT, "--root", self.root, *args)

    def test_creates_client_with_locked_files_only_as_drafts(self):
        p = self.make("--slug", "acme-bakery", "--language", "de", "--name", 'Acme "Bakery" & Co')
        self.assertEqual(p.returncode, 0, p.stderr)
        dest = self.root / "clients" / "acme-bakery"
        tmpl = sorted(f.relative_to(self.root / "templates" / "client").as_posix()
                      for f in (self.root / "templates" / "client").rglob("*") if f.is_file())
        placed = sorted(f.relative_to(dest).as_posix() for f in dest.rglob("*")
                        if f.is_file() and not f.relative_to(dest).as_posix().startswith("setup/"))
        drafts = sorted(f.relative_to(dest / "setup" / "drafts").as_posix()
                        for f in (dest / "setup" / "drafts").rglob("*") if f.is_file())
        is_locked = lambda r: any(r == x or (x.endswith("/") and r.startswith(x)) for x in LOCKED)
        self.assertEqual(placed, [r for r in tmpl if not is_locked(r)], "locked files must not be in place yet")
        self.assertEqual(drafts, [r for r in tmpl if is_locked(r)])
        passport = yaml.safe_load((dest / "setup" / "drafts" / "passport.yaml").read_text(encoding="utf-8"))
        self.assertEqual(passport["client"], "acme-bakery")
        self.assertEqual(passport["language"], "de")
        self.assertEqual(passport["name"], 'Acme "Bakery" & Co')
        self.assertFalse((self.root / "config" / "active-client.txt").exists(),
                         "the active client is switched only after the person confirms")

    def test_never_overwrites_an_existing_client(self):
        self.assertEqual(self.make("--slug", "acme").returncode, 0)
        marker = self.root / "clients" / "acme" / "brand" / "voice.md"
        marker.write_text("edited by the owner", encoding="utf-8")
        p = self.make("--slug", "acme")
        self.assertEqual(p.returncode, 2)
        self.assertIn("already exists", p.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "edited by the owner")

    def test_rejects_bad_slugs_and_language_codes(self):
        for slug in ("Acme", "acme bakery", "../evil", "-acme", "demo", "a" * 41, "p\u0435karnya"):  # the second letter is Cyrillic
            with self.subTest(slug=slug):
                p = self.make("--slug", slug)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse((self.root / "clients").exists() and any((self.root / "clients").iterdir()))
        p = self.make("--slug", "acme", "--language", "english please")
        self.assertNotEqual(p.returncode, 0)


class ApplyDrafts(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="apply-drafts-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.root, True)
        shutil.copytree(REPO / "templates", self.root / "templates")
        self.assertEqual(run(NEW_CLIENT, "--root", self.root, "--slug", "acme", "--language", "en").returncode, 0)
        self.client = self.root / "clients" / "acme"

    def apply(self, *args):
        return run(APPLY, "--root", self.root, "--slug", "acme", *args)

    def test_dry_run_moves_nothing(self):
        p = self.apply()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("dry run", p.stdout)
        self.assertFalse((self.client / "passport.yaml").exists())
        self.assertTrue((self.client / "setup" / "drafts" / "passport.yaml").exists())

    def test_yes_moves_drafts_and_activates(self):
        p = self.apply("--yes", "--activate")
        self.assertEqual(p.returncode, 0, p.stderr)
        for rel in ("passport.yaml", "permissions.yaml", "brand/consents.md", "product-base/README.md"):
            self.assertTrue((self.client / rel).is_file(), rel)
        self.assertFalse((self.client / "setup").exists())
        self.assertEqual((self.root / "config" / "active-client.txt").read_text(encoding="utf-8").strip(), "acme")
        self.assertEqual(yaml.safe_load((self.client / "passport.yaml").read_text(encoding="utf-8"))["client"], "acme")

    def test_only_locked_files_leave_the_drafts(self):
        stray = self.client / "setup" / "drafts" / "weeks" / "x.md"
        stray.parent.mkdir(parents=True)
        stray.write_text("not a locked file", encoding="utf-8")
        p = self.apply("--yes")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("skip", p.stdout)
        self.assertFalse((self.client / "weeks" / "x.md").exists(), "a non-locked draft is never put in place")
        self.assertTrue((self.client / "setup" / "not-applied" / "weeks" / "x.md").exists())
        self.assertFalse((self.client / "setup" / "drafts").exists(), "no drafts left = setup not 'in progress'")
        self.assertTrue((self.client / "passport.yaml").exists())

    def test_refuses_unconfirmed_proposals(self):
        perm = self.client / "setup" / "drafts" / "permissions.yaml"
        perm.write_text("weekly_credit_limit: 0\nproposed: true\n", encoding="utf-8")
        p = self.apply("--yes")
        self.assertEqual(p.returncode, 3)
        self.assertFalse((self.client / "permissions.yaml").exists())
        self.assertEqual(self.apply("--yes", "--keep-proposed").returncode, 0)
        self.assertTrue((self.client / "permissions.yaml").exists())

    def test_refuses_paths_outside_clients(self):
        for slug in ("../templates", "nope"):
            with self.subTest(slug=slug):
                self.assertNotEqual(run(APPLY, "--root", self.root, "--slug", slug, "--yes").returncode, 0)


class Wiring(unittest.TestCase):
    def test_setup_skill_has_front_matter_and_all_stages(self):
        text = (REPO / ".claude" / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
        fm = yaml.safe_load(re.match(r"\A---\n(.*?)\n---\n", text, re.S).group(1))
        self.assertEqual(fm["name"], "setup")
        for stage in range(10):
            self.assertIn(f"## Stage {stage}", text)
        for must in ("scripts/setup/preflight.py", "scripts/setup/new_client.py",
                     "scripts/setup/apply_drafts.py", "setup/drafts/", "cloud_session",
                     "language of the person's latest message", "Never ask for passwords"):
            self.assertIn(must, text)

    def test_claude_md_routes_first_run_to_setup(self):
        text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("`setup` skill", text)
        self.assertIn("Your copy is yours", text)
        self.assertIn("language of the person's latest message", text)

    def test_readmes_point_to_the_wizard(self):
        en = (REPO / "README.md").read_text(encoding="utf-8")
        ru = (REPO / "README.ru.md").read_text(encoding="utf-8")
        self.assertIn("Set me up", en)
        self.assertIn("README.ru.md", en)
        self.assertIn("scripts/setup/preflight.py", ru)

    def test_onboarding_agent_writes_drafts_of_locked_files(self):
        text = (REPO / ".claude" / "agents" / "onboarding.md").read_text(encoding="utf-8")
        self.assertIn("setup/drafts/", text)
        self.assertNotIn("write `config/active-client.txt`", text)

    def test_ticks_workflow_has_no_hard_coded_branch(self):
        wf = yaml.safe_load((REPO / ".github" / "workflows" / "factory-ticks.yml").read_text(encoding="utf-8"))
        ref = wf["jobs"]["tick"]["steps"][0]["with"]["ref"]
        self.assertIn("vars.FACTORY_BRANCH", ref)
        self.assertNotIn("schedule", wf[True], "the schedule stays off in the template")


if __name__ == "__main__":
    unittest.main()
