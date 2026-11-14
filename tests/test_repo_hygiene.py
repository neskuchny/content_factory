"""Repository hygiene for the English open-source release.

* no Cyrillic outside the Russian locale and two vendored upstream files,
* no big files, no secrets,
* every local markdown link resolves,
* every skill and agent has valid front matter.
"""
import json
import os
import re
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".cache", "node_modules"}
MAX_BYTES = 1_000_000

CYRILLIC = re.compile("[" + chr(0x400) + "-" + chr(0x4FF) + "]")
# Allowed Cyrillic: the Russian stoplist (a translation, by design), the Russian quick start, the
# setup skill (its trigger phrases are listed in several languages) and two data files copied
# unchanged from the upstream ffmpeg-skill (see .claude/skills/ffmpeg-skill/VENDORED.md).
CYRILLIC_ALLOWED_PREFIXES = ("config/locales/",)
CYRILLIC_ALLOWED_FILES = {
    "README.ru.md",
    ".claude/skills/setup/SKILL.md",
    ".claude/skills/ffmpeg-skill/references/scripts.md",
    ".claude/skills/ffmpeg-skill/scripts/_common/decision.py",
}

SECRET_PATTERNS = {
    "OpenAI/Anthropic-style key": re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    "Slack token": re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}"),
    "AWS access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    "private key block": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    "hard-coded api key/token/secret": re.compile(
        r"""(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]secret)\b["']?\s*[=:]\s*["']?[A-Za-z0-9_\-+/]{16,}"""),
    "bearer token": re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+[A-Za-z0-9_\-.=]{20,}"),
}
FORBIDDEN_FILE_NAMES = {".env", "id_rsa", "id_ed25519", ".netrc", ".npmrc", ".pypirc"}
FORBIDDEN_SUFFIXES = (".pem", ".p12", ".pfx", ".key")


def all_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        out += [Path(dirpath) / f for f in sorted(filenames)]
    return out


def rel(p):
    return p.relative_to(REPO).as_posix()


def text_of(p):
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


class Languages(unittest.TestCase):
    def test_no_cyrillic_outside_locales_and_vendored_files(self):
        bad = []
        for p in all_files():
            r = rel(p)
            if r.startswith(CYRILLIC_ALLOWED_PREFIXES) or r in CYRILLIC_ALLOWED_FILES:
                continue
            t = text_of(p)
            if t is None:
                continue
            m = CYRILLIC.search(t)
            if m:
                line = t.count("\n", 0, m.start()) + 1
                bad.append(f"{r}:{line}")
        self.assertEqual(bad, [], "Cyrillic text found outside the allowed files")

    def test_cyrillic_allowlist_has_no_stale_entries(self):
        for r in CYRILLIC_ALLOWED_FILES:
            with self.subTest(file=r):
                p = REPO / r
                self.assertTrue(p.is_file(), "allow-listed file no longer exists; remove it from the allowlist")
                self.assertRegex(p.read_text(encoding="utf-8"), CYRILLIC, "no Cyrillic left; remove it from the allowlist")


MEDIA_LIMITS = {          # showcase media for the README; everything else stays under 1 MB
    "docs/showcase/": 4_000_000,   # 720p example videos and thumbnails
    "docs/assets/": 5_000_000,     # hero animation, diagrams, social preview
}


def size_limit(path):
    for prefix, limit in MEDIA_LIMITS.items():
        if path.startswith(prefix):
            return limit
    return MAX_BYTES


class Size(unittest.TestCase):
    def test_no_file_over_its_size_limit(self):
        big = [f"{rel(p)} ({p.stat().st_size} bytes > {size_limit(rel(p))})" for p in all_files()
               if p.stat().st_size > size_limit(rel(p))]
        self.assertEqual(big, [])

    def test_showcase_media_total_stays_small(self):
        total = sum(p.stat().st_size for p in all_files() if rel(p).startswith(tuple(MEDIA_LIMITS)))
        self.assertLess(total, 25_000_000, "keep README media under 25 MB in total")


class Secrets(unittest.TestCase):
    def test_no_obvious_secrets_in_text_files(self):
        hits = []
        for p in all_files():
            t = text_of(p)
            if t is None:
                continue
            for name, rx in SECRET_PATTERNS.items():
                m = rx.search(t)
                if m:
                    line = t.count("\n", 0, m.start()) + 1
                    hits.append(f"{rel(p)}:{line}: {name}")
        self.assertEqual(hits, [])

    def test_no_build_machine_paths_in_text_files(self):
        # absolute paths from the machine that built a release (home dirs, temp/scratch folders) leak
        # local layout and session ids; repository files should use relative paths or placeholders
        rx = re.compile("/tmp/" + "claude-" + r"|/home/[a-z_][\w-]*/|/Users/[\w.-]+/|C:\\Users\\")
        hits = []
        for p in all_files():
            t = text_of(p)
            if t is None or rel(p).startswith("tests/"):  # tests use fake outside-repo paths on purpose
                continue
            m = rx.search(t)
            if m:
                hits.append(f"{rel(p)}:{t.count(chr(10), 0, m.start()) + 1}: {m.group(0)}")
        self.assertEqual(hits, [])

    def test_no_secret_files_are_shipped(self):
        bad = []
        for p in all_files():
            r = rel(p)
            if p.name in FORBIDDEN_FILE_NAMES or p.name.startswith(".env.") or p.suffix in FORBIDDEN_SUFFIXES \
                    or "/secrets/" in f"/{r}":
                bad.append(r)
        self.assertEqual(bad, [])

    def test_gitignore_covers_env_files(self):
        gi = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".env", gi)
        self.assertIn(".env.*", gi)
        self.assertIn(".cache/", gi)

    def test_secret_patterns_catch_known_shapes(self):
        """The detector itself must work: build fake tokens at run time so this file holds none."""
        fakes = {
            "OpenAI/Anthropic-style key": "sk-" + "a1B2" * 8,
            "GitHub token": "ghp_" + "A1b2C3d4E5" * 3,
            "Slack token": "xoxb-" + "1234567890-abcdef",
            "AWS access key id": "AKIA" + "ABCDEFGHIJKLMNOP",
            "hard-coded api key/token/secret": 'api_key = "' + "k" * 20 + '"',
            "private key block": "-----BEGIN RSA PRIVATE " + "KEY-----",
        }
        for name, sample in fakes.items():
            with self.subTest(pattern=name):
                self.assertRegex(sample, SECRET_PATTERNS[name])

    def test_secret_patterns_ignore_placeholders(self):
        for ok in ("api_key: <your key here>", "export API_KEY=...", "sk-ant-...", "token: ${TOKEN}",
                   "Authorization: Bearer <token>"):
            with self.subTest(text=ok):
                for rx in SECRET_PATTERNS.values():
                    self.assertIsNone(rx.search(ok))


# --------------------------------------------------------------------------- markdown links

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*(<[^>\n]+>|[^)\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s+(<[^>\n]+>|\S+)")
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|//|#)")


def md_links(path):
    """Yield (line_number, target) for markdown links outside fenced code and inline code."""
    in_fence, fence_mark = False, None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = FENCE.match(line)
        if m:
            if not in_fence:
                in_fence, fence_mark = True, m.group(1)
            elif m.group(1) == fence_mark:
                in_fence = False
            continue
        if in_fence:
            continue
        clean = INLINE_CODE.sub("", line)
        for lm in LINK.finditer(clean):
            yield n, lm.group(1)
        rm = REF_DEF.match(clean)
        if rm:
            yield n, rm.group(1)


def resolve_target(md_file, target):
    t = target.strip()
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1]
    if not t or EXTERNAL.match(t):
        return None
    t = re.split(r"[#?]", t, maxsplit=1)[0]
    if not t:
        return None
    base = REPO if t.startswith("/") else md_file.parent
    return (base / t.lstrip("/")).resolve()


class MarkdownLinks(unittest.TestCase):
    def test_all_local_links_resolve(self):
        broken = []
        for p in all_files():
            if p.suffix.lower() != ".md" or text_of(p) is None:
                continue
            for n, target in md_links(p):
                dest = resolve_target(p, target)
                if dest is not None and not dest.exists():
                    broken.append(f"{rel(p)}:{n}: ({target})")
        self.assertEqual(broken, [], "broken local markdown links")

    def test_link_extractor_behaves(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x.md"
            f.write_text(
                "[a](one.md) and [b](https://x.example/y) and [c](#anchor) and `[d](inline.md)`\n"
                "```\n[e](fenced.md)\n```\n"
                "~~~\n[f](tilde.md)\n~~~\n"
                "![img](pics/p.png \"title\") [g](two.md#sec) [h](<three four.md>)\n"
                "[ref]: four.md\n",
                encoding="utf-8")
            targets = [t for _, t in md_links(f)]
            self.assertEqual(targets, ["one.md", "https://x.example/y", "#anchor", "pics/p.png", "two.md#sec",
                                       "<three four.md>", "four.md"])
            self.assertIsNone(resolve_target(f, "https://x.example/y"))
            self.assertIsNone(resolve_target(f, "#anchor"))
            self.assertIsNone(resolve_target(f, "mailto:a@b.example"))
            self.assertEqual(resolve_target(f, "two.md#sec"), (Path(d) / "two.md").resolve())
            self.assertEqual(resolve_target(f, "<three four.md>"), (Path(d) / "three four.md").resolve())


# --------------------------------------------------------------------------- front matter

def front_matter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


class FrontMatter(unittest.TestCase):
    def test_skills_have_name_and_description(self):
        skills = sorted((REPO / ".claude" / "skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skills), 10)
        for f in skills:
            with self.subTest(skill=f.parent.name):
                fm = front_matter(f)
                self.assertIsInstance(fm, dict, "missing or invalid front matter")
                self.assertTrue(str(fm.get("name", "")).strip(), "front matter has no name")
                self.assertTrue(str(fm.get("description", "")).strip(), "front matter has no description")
                self.assertEqual(fm["name"], f.parent.name, "name must equal the folder name")

    def test_agents_have_name_and_description(self):
        agents = sorted((REPO / ".claude" / "agents").glob("*.md"))
        self.assertGreaterEqual(len(agents), 10)
        for f in agents:
            with self.subTest(agent=f.stem):
                fm = front_matter(f)
                self.assertIsInstance(fm, dict, "missing or invalid front matter")
                self.assertTrue(str(fm.get("name", "")).strip(), "front matter has no name")
                self.assertTrue(str(fm.get("description", "")).strip(), "front matter has no description")
                self.assertEqual(fm["name"], f.stem, "name must equal the file name")

    def test_agents_declare_a_model(self):
        for f in sorted((REPO / ".claude" / "agents").glob("*.md")):
            with self.subTest(agent=f.stem):
                self.assertTrue(front_matter(f).get("model"), "CLAUDE.md section 7: models are set in the agent header")


class ConfigFiles(unittest.TestCase):
    def test_json_files_parse(self):
        for p in all_files():
            if p.suffix == ".json":
                with self.subTest(file=rel(p)):
                    json.loads(p.read_text(encoding="utf-8"))

    def test_yaml_files_parse(self):
        for p in all_files():
            if p.suffix in (".yaml", ".yml"):
                with self.subTest(file=rel(p)):
                    yaml.safe_load(p.read_text(encoding="utf-8"))

    def test_settings_wire_the_guard_hook(self):
        s = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        cmds = [h["command"] for g in s["hooks"]["PreToolUse"] for h in g["hooks"]]
        self.assertTrue(any("scripts/guard/guard.py" in c for c in cmds))
        matcher = " ".join(g["matcher"] for g in s["hooks"]["PreToolUse"])
        for tool in ("Edit", "Write", "Bash"):
            self.assertIn(tool, matcher)
        deny = " ".join(s["permissions"]["deny"])
        self.assertIn(".env", deny)
        self.assertIn("secrets", deny)

    def test_release_files_exist(self):
        for name in ("README.md", "CLAUDE.md", "LICENSE", "requirements.txt"):
            with self.subTest(file=name):
                self.assertTrue((REPO / name).is_file(), f"{name} is missing from the repository root")

    def test_license_is_mit(self):
        lic = REPO / "LICENSE"
        if lic.is_file():
            self.assertIn("MIT License", lic.read_text(encoding="utf-8"))

    def test_requirements_pin_only_pyyaml(self):
        req = REPO / "requirements.txt"
        if req.is_file():
            names = [re.split(r"[<>=!~\[; ]", l.strip(), maxsplit=1)[0].lower()
                     for l in req.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.strip().startswith("#")]
            self.assertEqual(names, ["pyyaml"], "scripts and tests rely on the stdlib plus PyYAML only")


if __name__ == "__main__":
    unittest.main()
