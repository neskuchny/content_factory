"""Structure contract for the fictional demo client in clients/demo/.

The demo is the first thing a new user reads and the fixture for the script smoke tests, so it must
stay complete, parseable, English-only, clearly fictional and safe by default (manual publishing,
no direct messages).
"""
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
DEMO = REPO / "clients" / "demo"
TEMPLATE = REPO / "templates" / "client"
WEEK = DEMO / "weeks" / "2027-W02"
APPROVAL = WEEK / "06-approval.md"

# Parts of templates/client/ that are created on first use (collectors, indexer, retro...), so a demo
# need not ship them. Everything else in the template is required in the demo.
OPTIONAL_TEMPLATE_PARTS = (
    "media-index/", "references/", "trends/", "analytics/", "brand/references/", "brand/sounds/",
    "memory/targeting-map.md", "memory/platform-learnings.md", "memory/published-log.md",
    "memory/feedback-log.md", "memory/hooks-library.yaml", "memory/channel-state.md",
)
CYRILLIC = re.compile("[" + chr(0x400) + "-" + chr(0x4FF) + "]")
UNIT_ID = re.compile(r"^W\d{2}-[RCSLPVX]\d{2}$")


def demo_files():
    return sorted(p for p in DEMO.rglob("*") if p.is_file())


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_precheck():
    spec = importlib.util.spec_from_file_location("precheck_under_test", REPO / "scripts" / "ticks" / "precheck.py")
    mod = importlib.util.module_from_spec(spec)
    old, sys.dont_write_bytecode = sys.dont_write_bytecode, True  # keep __pycache__ out of the repo
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = old
    return mod


class Structure(unittest.TestCase):
    def test_demo_exists(self):
        self.assertTrue(DEMO.is_dir())

    def test_required_template_files_exist(self):
        required = []
        for f in sorted(TEMPLATE.rglob("*")):
            if not f.is_file() or f.name == ".gitkeep":
                continue
            rel = f.relative_to(TEMPLATE).as_posix()
            if any(rel == o or rel.startswith(o) for o in OPTIONAL_TEMPLATE_PARTS if o.endswith("/")) or rel in OPTIONAL_TEMPLATE_PARTS:
                continue
            required.append(rel)
        self.assertIn("passport.yaml", required)
        self.assertIn("permissions.yaml", required)
        self.assertIn("memory/MEMORY.md", required)
        for rel in required:
            with self.subTest(file=rel):
                self.assertTrue((DEMO / rel).is_file(), f"clients/demo/{rel} is missing (required by templates/client/{rel})")

    def test_week_and_request_folder_names(self):
        weeks = [p.name for p in (DEMO / "weeks").iterdir() if p.is_dir()]
        self.assertTrue(weeks)
        for w in weeks:
            self.assertRegex(w, r"^\d{4}-W\d{2}$")
        for r in (DEMO / "requests").iterdir():
            if r.is_dir():
                self.assertRegex(r.name, r"^REQ-\d{8}-\d+$")

    def test_demo_week_has_the_stage_files(self):
        for name in ("00-inputs.md", "01-plan.md", "02-shoot-brief.md", "06-approval.md"):
            with self.subTest(file=name):
                self.assertTrue((WEEK / name).is_file())
        self.assertTrue(list((WEEK / "03-scripts").glob("*.md")))

    def test_script_files_are_named_after_unit_ids_in_the_approval_pack(self):
        pack = APPROVAL.read_text(encoding="utf-8")
        for f in (WEEK / "03-scripts").glob("*.md"):
            with self.subTest(script=f.name):
                self.assertRegex(f.stem, UNIT_ID)
                self.assertIn(f.stem, pack)

    def test_no_stray_files(self):
        for f in demo_files():
            with self.subTest(file=f.relative_to(DEMO).as_posix()):
                self.assertNotIn(f.suffix.lower(), {".pyc", ".log", ".env", ".mp4", ".mov"})
                self.assertFalse(f.name.startswith(".env"))
                self.assertLess(f.stat().st_size, 200_000)


class Parsing(unittest.TestCase):
    def test_yaml_files_parse(self):
        files = [f for f in demo_files() if f.suffix in (".yaml", ".yml")]
        self.assertGreaterEqual(len(files), 6)
        for f in files:
            with self.subTest(file=f.name):
                self.assertIsInstance(load_yaml(f), dict)

    def test_json_files_parse(self):
        for f in demo_files():
            if f.suffix == ".json":
                with self.subTest(file=f.name):
                    self.assertIsInstance(json.loads(f.read_text(encoding="utf-8")), dict)
            elif f.suffix == ".jsonl":
                with self.subTest(file=f.name):
                    for line in f.read_text(encoding="utf-8").splitlines():
                        if line.strip():
                            json.loads(line)

    def test_passport(self):
        p = load_yaml(DEMO / "passport.yaml")
        self.assertEqual(p["client"], "demo")
        self.assertEqual(p["language"], "en")
        for key in ("name", "niche", "audience", "target_action"):
            self.assertTrue(p.get(key), f"passport.yaml: {key} is empty")
        self.assertEqual(p.get("people"), [], "the demo has no people on camera")

    def test_channels(self):
        ch = load_yaml(DEMO / "channels.yaml")["channels"]
        roles = {c["role"] for c in ch.values()}
        self.assertTrue(roles <= {"hub", "spoke"})
        self.assertIn("hub", roles)
        self.assertIn("spoke", roles)
        for name, c in ch.items():
            with self.subTest(channel=name):
                self.assertTrue(str(c.get("access", "")).startswith("none"), "demo channels must not have API access")

    def test_brand_tokens_have_ai_label(self):
        tokens = json.loads((DEMO / "brand" / "tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(tokens["ai_label"]["text"], "AI visualization")
        self.assertTrue(tokens["ai_label"]["always_on"])

    def test_utm_uses_reserved_example_domain(self):
        utm = load_yaml(DEMO / "utm.yaml")
        self.assertTrue(utm["base_url"].rstrip("/").endswith(".example"), utm["base_url"])
        for url in utm["landing_pages"].values():
            self.assertIn(".example", url)


class Permissions(unittest.TestCase):
    def setUp(self):
        self.perm = load_yaml(DEMO / "permissions.yaml")

    def test_publish_default_is_manual(self):
        self.assertEqual(self.perm["publish"]["default"], "manual")

    def test_no_platform_is_set_to_auto(self):
        for platform, mode in self.perm["publish"].items():
            with self.subTest(platform=platform):
                self.assertNotEqual(mode, "auto")

    def test_direct_messages_forbidden(self):
        self.assertEqual(self.perm["messages"]["direct_messages"], "forbidden")

    def test_replies_are_drafts_only(self):
        self.assertEqual(self.perm["messages"]["comments_reply"], "draft_only")
        self.assertEqual(self.perm["messages"]["reviews_reply"], "draft_only")

    def test_paid_placements_need_approval(self):
        self.assertEqual(self.perm["spending"]["paid_placements"], "approval_each")

    def test_spending_limits_are_small_non_negative_numbers(self):
        s = self.perm["spending"]
        self.assertIsInstance(s["generation_credits_week"], (int, float))
        self.assertGreaterEqual(s["generation_credits_week"], 0)
        for req, limit in (s.get("request_credits") or {}).items():
            self.assertRegex(req, r"^REQ-\d{8}-\d+$")
            self.assertGreaterEqual(limit, 0)

    def test_same_sections_as_the_template(self):
        self.assertEqual(set(self.perm), set(load_yaml(TEMPLATE / "permissions.yaml")))

    def test_people_on_camera_escalation_is_kept(self):
        self.assertTrue(any("consents.md" in item for item in self.perm["escalate_to_human"]))


class ApprovalPack(unittest.TestCase):
    """06-approval.md must follow the format scripts/ticks/precheck.py parses: `## <ID> ...` then `decision:`."""

    @staticmethod
    def sections(text):
        out, cur = [], None
        for line in text.splitlines():
            m = re.match(r"^## (\S+)", line)
            if m:
                cur = {"id": m.group(1), "lines": []}
                out.append(cur)
            elif cur is not None:
                cur["lines"].append(line)
        return out

    def setUp(self):
        self.text = APPROVAL.read_text(encoding="utf-8")
        self.units = [s for s in self.sections(self.text) if UNIT_ID.match(s["id"])]

    def test_has_units(self):
        self.assertGreaterEqual(len(self.units), 3)

    def test_unit_ids_are_unique(self):
        ids = [u["id"] for u in self.units]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_unit_has_exactly_one_decision_line(self):
        for u in self.units:
            with self.subTest(unit=u["id"]):
                decisions = [l for l in u["lines"] if l.startswith("decision:")]
                self.assertEqual(len(decisions), 1)
                self.assertTrue(decisions[0][len("decision:"):].strip(), "decision: must not be empty (use `pending`)")

    def test_decision_lines_only_inside_units(self):
        for s in self.sections(self.text):
            if not UNIT_ID.match(s["id"]):
                with self.subTest(section=s["id"]):
                    self.assertFalse([l for l in s["lines"] if l.startswith("decision:")])

    def test_demo_shows_both_pending_and_decided_units(self):
        values = []
        for u in self.units:
            for l in u["lines"]:
                if l.startswith("decision:"):
                    values.append(l[len("decision:"):].strip())
        self.assertTrue(any(v.split("#")[0].strip() == "pending" for v in values))
        self.assertTrue(any(not v.startswith("pending") for v in values))

    def test_precheck_wakes_publisher_and_feedback_for_the_demo_week(self):
        pre = load_precheck()
        pre.iso_week = lambda d=None: "2027-W02"
        wakes = pre.check_client("demo", network=False)
        agents = {w["agent"] for w in wakes}
        self.assertIn("publisher", agents)
        self.assertIn("feedback", agents)
        for w in wakes:
            self.assertEqual(w["client"], "demo")

    # Regression: precheck used one regex with re.S over the whole pack, so a section whose decision
    # was `pending` got stitched to the NEXT section's decision (it reported the non-unit heading
    # "Questions" instead of W02-R01 and W02-C01). Sections are now parsed one by one.
    def test_precheck_reports_exactly_the_decided_units(self):
        pre = load_precheck()
        pre.iso_week = lambda d=None: "2027-W02"
        pub = next(w for w in pre.check_client("demo", network=False) if w["agent"] == "publisher")
        listed = pub["prompt"].split("units:")[1].strip().rstrip(".").replace(" ", "").split(",")
        self.assertEqual(sorted(listed), ["W02-C01", "W02-R01"])


class Fictional(unittest.TestCase):
    def test_every_fact_file_is_labelled_fictional(self):
        facts = sorted((DEMO / "product-base").glob("*.md"))
        self.assertGreaterEqual(len(facts), 3)
        for f in facts:
            with self.subTest(file=f.name):
                self.assertIn("FICTIONAL", f.read_text(encoding="utf-8"), f"{f.name} lacks the FICTIONAL label")

    def test_top_level_config_files_are_labelled_fictional(self):
        for name in ("passport.yaml", "channels.yaml", "permissions.yaml", "quotas.yaml", "sources.yaml", "utm.yaml"):
            with self.subTest(file=name):
                self.assertIn("FICTIONAL", (DEMO / name).read_text(encoding="utf-8"))

    def test_no_cyrillic_anywhere_in_the_demo(self):
        for f in demo_files():
            with self.subTest(file=f.relative_to(DEMO).as_posix()):
                self.assertIsNone(CYRILLIC.search(f.read_text(encoding="utf-8")))

    def test_demo_has_no_real_contact_data(self):
        email = re.compile(r"[\w.+-]+@(?!example\.)[\w-]+\.[a-z]{2,}", re.I)
        for f in demo_files():
            with self.subTest(file=f.relative_to(DEMO).as_posix()):
                self.assertIsNone(email.search(f.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
