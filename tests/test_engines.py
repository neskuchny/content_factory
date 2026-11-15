"""Tests for the paid engines (Higgsfield, treg): who may call them, where they are configured, and
how their spend is counted. treg bills in dollars (`usd_direct` in a video's manifest), Higgsfield in
credits; scripts/analytics/costs.py adds both into one dollar total.
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
AGENTS = REPO / ".claude" / "agents"
TREG_SERVERS = ("treg", "claude_ai_treg", "claude_ai_Treg")   # local .mcp.json name and claude.ai connector names
PAID_TREG = ("call", "call_media")
OUTBOUND_TREG = ("feedback", "review", "catalog_request")      # send data to treg


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"\A---\n(.*?)\n---\n", text, re.S).group(1))


def split(v):
    if not v:
        return []
    return [x.strip() for x in (v if isinstance(v, list) else str(v).split(",")) if x.strip()]


def blocked(fm, server, tool):
    """True if the agent cannot call mcp__<server>__<tool>: a whitelist without it, or a deny entry."""
    name = f"mcp__{server}__{tool}"
    allow = split(fm.get("tools"))
    if allow and not any(a == name or (a.endswith("*") and name.startswith(a[:-1])) for a in allow):
        return True
    return any(d == name or (d.endswith("*") and name.startswith(d[:-1])) for d in split(fm.get("disallowedTools")))


class TregAccess(unittest.TestCase):
    def test_only_studio_may_make_paid_or_outbound_treg_calls(self):
        for f in sorted(AGENTS.glob("*.md")):
            fm = front_matter(f)
            for server in TREG_SERVERS:
                for tool in PAID_TREG + OUTBOUND_TREG:
                    with self.subTest(agent=fm["name"], tool=f"{server}/{tool}"):
                        if fm["name"] == "studio":
                            self.assertFalse(blocked(fm, server, tool), "studio is the one role that generates")
                        else:
                            self.assertTrue(blocked(fm, server, tool),
                                            f"{fm['name']} must not call mcp__{server}__{tool}")

    def test_roles_without_any_higgsfield_also_have_no_treg(self):
        for f in sorted(AGENTS.glob("*.md")):
            fm = front_matter(f)
            if "mcp__higgsfield__*" in split(fm.get("disallowedTools")):
                with self.subTest(agent=fm["name"]):
                    for server in TREG_SERVERS:
                        self.assertTrue(blocked(fm, server, "catalog_search"))

    def test_studio_loads_the_gateway_skill(self):
        self.assertIn("treg-gateway", front_matter(AGENTS / "studio.md")["skills"])


class TregConfig(unittest.TestCase):
    def test_mcp_json_lists_the_hosted_endpoint_without_secrets(self):
        cfg = json.loads((REPO / ".mcp.json").read_text(encoding="utf-8"))
        treg = cfg["mcpServers"]["treg"]
        self.assertEqual(treg, {"type": "http", "url": "https://treg.to/mcp/v2/"})
        self.assertNotIn("headers", json.dumps(cfg).lower())

    def test_engine_and_limits_are_declared(self):
        self.assertIn("treg", (REPO / "config" / "engines.yaml").read_text(encoding="utf-8"))
        for p in (REPO / "templates" / "client" / "permissions.yaml", REPO / "clients" / "demo" / "permissions.yaml"):
            with self.subTest(file=str(p.relative_to(REPO))):
                spending = yaml.safe_load(p.read_text(encoding="utf-8"))["spending"]
                self.assertEqual(spending.get("treg_usd_week"), 0, "the default is: ask before every paid call")

    def test_gateway_skill_keeps_the_factory_rules(self):
        text = (REPO / ".claude" / "skills" / "treg-gateway" / "SKILL.md").read_text(encoding="utf-8")
        for must in ("treg_usd_week", "usd_direct", "Estimate before spending", "factory rules win",
                     "curl", "treg scan", "labelled", "by code only", "consents.md"):
            self.assertIn(must, text)


class DollarSpend(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="costs-usd-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.root, True)
        (self.root / "config").mkdir()
        shutil.copy2(REPO / "config" / "pricing.yaml", self.root / "config" / "pricing.yaml")
        self.rate = yaml.safe_load((REPO / "config" / "pricing.yaml").read_text(encoding="utf-8"))["higgsfield"]["credit_usd"]
        for rid, manifest in (("REQ-20270201-1", {"credits": 10, "usd_direct": {"treg": 0.5, "other": 0.25}}),
                              ("REQ-20270201-2", {"usd_direct": 1.2}),
                              ("REQ-20270201-3", {"credits": 4})):
            final = self.root / "clients" / "acme" / "requests" / rid / "production" / "final"
            final.mkdir(parents=True)
            (final / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (final / f"{rid}.mp4").write_bytes(b"")

    def run_costs(self):
        out = self.root / "costs.md"
        p = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts" / "analytics" / "costs.py"),
                            "--client", "acme", "--repo", str(self.root), "--out", str(out)],
                           capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(p.returncode, 0, p.stderr)
        return out.read_text(encoding="utf-8")

    def test_direct_dollars_are_added_to_the_total(self):
        text = self.run_costs()
        expected = 14 * self.rate + 0.5 + 0.25 + 1.2
        self.assertIn(f"**${expected:.2f}**", text)
        self.assertIn("paid directly in dollars", text)
        self.assertIn("$1.95", text)   # 0.75 + 1.2 direct
        self.assertNotIn("No spend data", text, "a dollars-only request is not 'unknown'")

    def test_no_direct_line_without_direct_spend(self):
        for rid in ("REQ-20270201-1", "REQ-20270201-2"):
            shutil.rmtree(self.root / "clients" / "acme" / "requests" / rid)
        self.assertNotIn("paid directly in dollars", self.run_costs())


if __name__ == "__main__":
    unittest.main()
