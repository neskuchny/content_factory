"""Smoke tests: the factory's stdlib scripts run on the demo client and every .py file compiles.

Scripts are run as `python -I <script>` with --out pointing into a temporary directory, so the
repository tree is not modified (checked by test_runs_leave_the_repo_untouched).
"""
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
SKIP_DIRS = {".git", "__pycache__", ".cache", "node_modules"}


def run(script, *args, timeout=120):
    # -I ignores PYTHON* variables, so bytecode writing is switched off with -B (keeps __pycache__ out of the repo)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                          capture_output=True, text=True, timeout=timeout, env=env, cwd=str(REPO))


def tree_snapshot():
    out = set()
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in {".git"}]
        for f in filenames:
            out.add(str((Path(dirpath) / f).relative_to(REPO)))
    return out


class Smoke(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="smoke-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    # --- dashboard -----------------------------------------------------------------
    def test_dashboard_builds_html_for_demo(self):
        out = self.tmp / "demo.html"
        p = run(SCRIPTS / "dashboard" / "build.py", "--client", "demo", "--repo", REPO, "--out", out)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(out.is_file())
        html = out.read_text(encoding="utf-8")
        self.assertTrue(html.lstrip().lower().startswith("<!doctype html"))
        self.assertIn("</html>", html)
        self.assertIn("Brewline Demo Roasters", html)
        self.assertIn("client demo", html)
        self.assertNotRegex(html, r"(?i)<script[^>]+src=")           # self-contained
        self.assertNotRegex(html, r"(?i)<link[^>]+rel=.stylesheet")
        self.assertIsNone(re.search("[" + chr(0x400) + "-" + chr(0x4FF) + "]", html))
        self.assertIn("What could not be parsed (0)", html, "the demo must parse without issues")

    def test_dashboard_unknown_client_does_not_crash_silently(self):
        p = run(SCRIPTS / "dashboard" / "build.py", "--client", "no-such-client", "--repo", REPO,
                "--out", self.tmp / "x.html")
        # either a clean error or a page that says there is nothing; never a traceback
        self.assertNotIn("Traceback", p.stderr)

    # --- costs ---------------------------------------------------------------------
    def test_costs_runs_for_demo(self):
        out = self.tmp / "costs.md"
        p = run(SCRIPTS / "analytics" / "costs.py", "--client", "demo", "--repo", REPO, "--out", out)
        self.assertEqual(p.returncode, 0, p.stderr)
        text = out.read_text(encoding="utf-8")
        self.assertIn("REQ-20270111-1", text)
        self.assertIn("Spend per request - demo", text)
        self.assertIn("total", p.stdout.lower())

    def test_costs_requires_client(self):
        p = run(SCRIPTS / "analytics" / "costs.py")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--client", p.stderr)

    # --- precheck ------------------------------------------------------------------
    def test_precheck_returns_json_and_documented_exit_code(self):
        p = run(SCRIPTS / "ticks" / "precheck.py", "--client", "demo", "--no-network")
        wakes = json.loads(p.stdout)
        self.assertIsInstance(wakes, list)
        # documented: exit 0 = there is work, 3 = no work
        self.assertEqual(p.returncode, 0 if wakes else 3, p.stderr)
        for w in wakes:
            self.assertTrue({"client", "agent", "reason", "prompt"} <= set(w), w)
            self.assertEqual(w["client"], "demo")

    def test_precheck_all_clients_no_network(self):
        p = run(SCRIPTS / "ticks" / "precheck.py", "--no-network")
        wakes = json.loads(p.stdout)
        self.assertEqual(p.returncode, 0 if wakes else 3, p.stderr)
        self.assertTrue(all("client" in w for w in wakes))

    # --- dice ----------------------------------------------------------------------
    def test_dice_is_deterministic_with_a_seed(self):
        a = run(SCRIPTS / "qa" / "dice.py", "--seed", 1)
        b = run(SCRIPTS / "qa" / "dice.py", "--seed", 1)
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertEqual(a.stdout, b.stdout)
        lines = a.stdout.splitlines()
        self.assertEqual(lines[0], "seed: 1")
        self.assertEqual(len(lines), 4)  # seed line + the default 3 sparks
        for i, line in enumerate(lines[1:], 1):
            self.assertRegex(line, rf"^{i}\. \[[^\]]+\] .+")

    def test_dice_takes_a_count_and_draws_from_different_categories(self):
        p = run(SCRIPTS / "qa" / "dice.py", 4, "--seed", 7)
        lines = p.stdout.splitlines()[1:]
        self.assertEqual(len(lines), 4)
        cats = [re.match(r"^\d+\. \[([^\]]+)\]", l).group(1) for l in lines]
        self.assertGreaterEqual(len(set(cats)), min(4, 2))

    # --- words_check ---------------------------------------------------------------
    def test_words_check_runs_on_demo_scripts(self):
        files = sorted((REPO / "clients" / "demo" / "weeks" / "2027-W02" / "03-scripts").glob("*.md"))
        self.assertTrue(files)
        p = run(SCRIPTS / "qa" / "words_check.py", "--client", "demo", *files)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertRegex(p.stdout, r"total findings: \d+")

    # --- help ----------------------------------------------------------------------
    def test_argparse_scripts_answer_help(self):
        for rel in ("dashboard/build.py", "analytics/costs.py", "ticks/precheck.py", "qa/dice.py", "qa/words_check.py"):
            with self.subTest(script=rel):
                p = run(SCRIPTS / rel, "--help")
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn("usage:", p.stdout.lower())

    # --- hygiene of the run --------------------------------------------------------
    def test_runs_leave_the_repo_untouched(self):
        before = tree_snapshot()
        run(SCRIPTS / "dashboard" / "build.py", "--client", "demo", "--repo", REPO, "--out", self.tmp / "a.html")
        run(SCRIPTS / "analytics" / "costs.py", "--client", "demo", "--repo", REPO, "--out", self.tmp / "c.md")
        run(SCRIPTS / "ticks" / "precheck.py", "--client", "demo", "--no-network")
        run(SCRIPTS / "qa" / "dice.py", "--seed", 1)
        self.assertEqual(tree_snapshot() ^ before, set())


class Compile(unittest.TestCase):
    @staticmethod
    def python_files():
        out = []
        for dirpath, dirnames, filenames in os.walk(REPO):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            out += [Path(dirpath) / f for f in filenames if f.endswith(".py")]
        return sorted(out)

    def test_every_python_file_compiles(self):
        files = self.python_files()
        self.assertGreater(len(files), 5)
        with tempfile.TemporaryDirectory() as tmp:
            for i, f in enumerate(files):
                with self.subTest(file=str(f.relative_to(REPO))):
                    py_compile.compile(str(f), cfile=str(Path(tmp) / f"{i}.pyc"), doraise=True)

    def test_framework_scripts_are_present(self):
        for rel in ("guard/guard.py", "qa/words_check.py", "qa/dice.py", "analytics/costs.py",
                    "dashboard/build.py", "ticks/precheck.py"):
            self.assertTrue((SCRIPTS / rel).is_file(), rel)

    @unittest.skipUnless(shutil.which("bash"), "bash is not installed")
    def test_shell_scripts_have_valid_syntax(self):
        for f in sorted(SCRIPTS.rglob("*.sh")):
            with self.subTest(file=str(f.relative_to(REPO))):
                p = subprocess.run(["bash", "-n", str(f)], capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == "__main__":
    unittest.main()
