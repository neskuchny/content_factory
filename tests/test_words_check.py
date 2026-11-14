"""Tests for scripts/qa/words_check.py and the stoplists in config/locales/.

Russian samples are built from code points so that this file stays Cyrillic-free.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "qa" / "words_check.py"
LOCALES = REPO / "config" / "locales"

# The Russian sentence for "it is not just coffee" (a stock cliche): it hits a rule in ru.yaml and
# none in en.yaml. Built from code points so that this file stays free of Cyrillic characters.
RU_TEXT = "".join(chr(c) for c in (
    0x42D, 0x442, 0x43E, 0x20, 0x43D, 0x435, 0x20,
    0x43F, 0x440, 0x43E, 0x441, 0x442, 0x43E, 0x20,
    0x43A, 0x43E, 0x444, 0x435, 0x2E))
CYRILLIC = re.compile("[" + chr(0x400) + "-" + chr(0x4FF) + "]")
EN_DIRTY = "Let's delve into this game-changer of a roast."
EN_CLEAN = "Store the beans in an airtight jar. Grind them just before brewing."


def run(args, script=SCRIPT, cwd=None):
    p = subprocess.run([sys.executable, "-I", str(script), *map(str, args)],
                       capture_output=True, text=True, cwd=cwd, timeout=60)
    return p.returncode, p.stdout, p.stderr


def total(stdout):
    m = re.search(r"total findings: (\d+)", stdout)
    assert m, f"no total line in: {stdout!r}"
    return int(m.group(1))


class WordsCheckBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="words-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def text(self, content, name="script.md"):
        p = self.tmp / name
        p.write_text(content, encoding="utf-8")
        return p


class EnglishStoplist(WordsCheckBase):
    def test_classic_llm_words_are_flagged(self):
        p = self.text(EN_DIRTY)
        rc, out, _ = run(["--lang", "en", p])
        self.assertEqual(rc, 0)
        self.assertIn('"delve" is a classic LLM word', out)
        self.assertIn("advertising cliché", out)
        self.assertGreaterEqual(total(out), 2)

    def test_each_sample_phrase_is_flagged(self):
        samples = [
            "We will delve into the details.",
            "A true game-changer for your mornings.",
            "A game-changing roast.",
            "A gamechanger roast.",
            "Unlock the flavour of the bean.",
            "Seamless brewing at home.",
            "Our cutting-edge roaster.",
            "In today's fast-paced world nobody has time.",
            "It's not just coffee, it's a ritual.",
            "This is a testament to craft.",
            "We leverage small batches.",
            "What if your coffee could taste better?",
            "An incredibly smooth cup.",
        ]
        for s in samples:
            with self.subTest(sample=s):
                rc, out, _ = run(["--lang", "en", self.text(s)])
                self.assertEqual(rc, 0)
                self.assertGreaterEqual(total(out), 1, out)

    def test_matching_is_case_insensitive(self):
        rc, out, _ = run(["--lang", "en", self.text("DELVE INTO IT")])
        self.assertGreaterEqual(total(out), 1)

    def test_report_format_has_file_line_and_fragment(self):
        p = self.text("Fine line one.\nNow we delve deeper.\n")
        _, out, _ = run(["--lang", "en", p])
        self.assertRegex(out, re.escape(f"{p}:2: ") + r".+ - \".*delve.*\"")
        self.assertNotIn(f"{p}:1:", out)

    def test_clean_text_passes(self):
        rc, out, err = run(["--lang", "en", self.text(EN_CLEAN)])
        self.assertEqual(rc, 0)
        self.assertEqual(total(out), 0, out)
        self.assertEqual(err, "")

    def test_exit_code_is_zero_even_with_findings(self):
        rc, out, _ = run(["--lang", "en", self.text(EN_DIRTY)])
        self.assertEqual(rc, 0)
        self.assertGreater(total(out), 0)

    def test_multiple_files_and_missing_file(self):
        a, b = self.text(EN_DIRTY, "a.md"), self.text(EN_CLEAN, "b.md")
        _, out, _ = run(["--lang", "en", a, b, self.tmp / "nope.md"])
        self.assertIn(f"{a}:1:", out)
        self.assertNotIn(f"{b}:1:", out)
        self.assertIn("nope.md: no such file", out)

    def test_default_language_is_english(self):
        _, out, err = run([self.text(EN_DIRTY)])
        self.assertGreater(total(out), 0)
        self.assertEqual(err, "")

    def test_no_files_prints_help(self):
        rc, out, _ = run([])
        self.assertEqual(rc, 0)
        self.assertIn("usage:", out.lower())


class OtherLanguages(WordsCheckBase):
    def test_ru_flag_loads_russian_stoplist(self):
        p = self.text(RU_TEXT)
        _, out_ru, err_ru = run(["--lang", "ru", p])
        _, out_en, _ = run(["--lang", "en", p])
        self.assertGreaterEqual(total(out_ru), 1, out_ru)
        self.assertEqual(err_ru, "", "ru.yaml exists, so there must be no fallback notice")
        self.assertEqual(total(out_en), 0, "the Russian sample must not be flagged by the English list")

    def test_ru_list_does_not_flag_english_cliches(self):
        _, out, _ = run(["--lang", "ru", self.text(EN_DIRTY)])
        self.assertEqual(total(out), 0)

    def test_unknown_language_falls_back_to_english(self):
        p = self.text(EN_DIRTY)
        _, out_xx, err = run(["--lang", "zz-ZZ", p])
        _, out_en, _ = run(["--lang", "en", p])
        self.assertIn("no stoplist for 'zz-ZZ'", err)
        self.assertIn("en.yaml", err)
        self.assertEqual(total(out_xx), total(out_en))
        self.assertGreater(total(out_xx), 0)

    def test_region_code_falls_back_to_base_language(self):
        _, out, err = run(["--lang", "ru-RU", self.text(RU_TEXT)])
        self.assertIn("ru.yaml", err)
        self.assertGreaterEqual(total(out), 1)


class PassportLanguage(WordsCheckBase):
    """--client reads `language:` from clients/<client>/passport.yaml of the script's own repository,
    so these tests copy the script and the locales into a temporary repository."""

    def setUp(self):
        super().setUp()
        self.repo = self.tmp / "repo"
        (self.repo / "scripts" / "qa").mkdir(parents=True)
        shutil.copy2(SCRIPT, self.repo / "scripts" / "qa" / "words_check.py")
        shutil.copytree(LOCALES, self.repo / "config" / "locales")
        self.script = self.repo / "scripts" / "qa" / "words_check.py"

    def client(self, name, passport_text):
        d = self.repo / "clients" / name
        d.mkdir(parents=True, exist_ok=True)
        if passport_text is not None:
            (d / "passport.yaml").write_text(passport_text, encoding="utf-8")

    def test_language_comes_from_passport(self):
        self.client("ruco", "client: ruco\nlanguage: ru\n")
        p = self.text(RU_TEXT)
        _, out, err = run(["--client", "ruco", p], script=self.script)
        self.assertGreaterEqual(total(out), 1, out)
        self.assertEqual(err, "")

    def test_passport_english_uses_english_list(self):
        self.client("enco", "client: enco\nlanguage: en\n")
        _, out, _ = run(["--client", "enco", self.text(EN_DIRTY)], script=self.script)
        self.assertGreater(total(out), 0)
        _, out, _ = run(["--client", "enco", self.text(RU_TEXT, "ru.md")], script=self.script)
        self.assertEqual(total(out), 0)

    def test_explicit_lang_beats_passport(self):
        self.client("ruco", "client: ruco\nlanguage: ru\n")
        _, out, _ = run(["--client", "ruco", "--lang", "en", self.text(EN_DIRTY)], script=self.script)
        self.assertGreater(total(out), 0)

    def test_passport_with_unknown_language_falls_back(self):
        self.client("xxco", "client: xxco\nlanguage: zz\n")
        _, out, err = run(["--client", "xxco", self.text(EN_DIRTY)], script=self.script)
        self.assertIn("no stoplist for 'zz'", err)
        self.assertGreater(total(out), 0)

    def test_missing_passport_or_language_defaults_to_english(self):
        self.client("nopass", None)
        self.client("nolang", "client: nolang\n")
        for c in ("nopass", "nolang", "doesnotexist"):
            with self.subTest(client=c):
                _, out, err = run(["--client", c, self.text(EN_DIRTY)], script=self.script)
                self.assertGreater(total(out), 0)
                self.assertEqual(err, "")

    def test_shipped_demo_client_is_english(self):
        _, out, err = run(["--client", "demo", self.text(EN_DIRTY)])
        self.assertGreater(total(out), 0)
        self.assertEqual(err, "")


class LocaleFiles(unittest.TestCase):
    def test_locale_files_are_well_formed(self):
        files = sorted(LOCALES.glob("*.yaml"))
        self.assertTrue({"en", "ru"} <= {f.stem for f in files})
        for f in files:
            with self.subTest(locale=f.name):
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
                self.assertEqual(str(data["language"]).lower(), f.stem)
                self.assertTrue(data["rules"], "empty rule list")
                for i, r in enumerate(data["rules"]):
                    self.assertTrue(r.get("pattern"), f"rule {i} has no pattern")
                    self.assertTrue(r.get("reason"), f"rule {i} has no reason")
                    try:
                        re.compile(r["pattern"])
                    except re.error as e:
                        self.fail(f"rule {i} pattern does not compile: {e}")

    def test_english_list_has_no_cyrillic(self):
        self.assertIsNone(CYRILLIC.search((LOCALES / "en.yaml").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
