#!/usr/bin/env python3
"""Check a video text for "generated-sounding" phrasing and stock clichés (anti-jargon stoplist).

The idea comes from words_check.py in sarpstar/cinecode (MIT); the word lists are our own and live in
config/locales/<lang>.yaml (ru.yaml, en.yaml; add a language by adding a file).
Usage: python3 scripts/qa/words_check.py [--lang en] [--client demo] <file> [<file> ...]   (md, txt, json: read as text)
Language: --lang, otherwise `language:` of clients/<client>/passport.yaml (when --client is given), otherwise en.
Output: findings as "file:line: rule - fragment". The exit code is always 0: it is a hint, not a ban.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ROOT / "config" / "locales"


def passport_language(client):
    """`language` from clients/<client>/passport.yaml (BCP-47, e.g. "ru" or "pt-BR"), or None."""
    p = ROOT / "clients" / client / "passport.yaml"
    if not p.is_file():
        return None
    import yaml
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return str(data["language"]) if isinstance(data, dict) and data.get("language") else None


def load_rules(lang):
    """Rules [(regex, reason)] from config/locales/<lang>.yaml; falls back from "pt-BR" to "pt", then to en."""
    import yaml
    tried = []
    for code in (lang.lower(), lang.lower().split("-")[0], "en"):
        p = LOCALES / f"{code}.yaml"
        tried.append(p.name)
        if p.is_file():
            if code != lang.lower():
                print(f"words_check: no stoplist for '{lang}', using {p.name}", file=sys.stderr)
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            return [(r["pattern"], r["reason"]) for r in data.get("rules", [])]
    sys.exit(f"words_check: no locale file found (tried {', '.join(tried)} in {LOCALES})")


def check(path: Path, rules):
    hits = []
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        low = line.lower()
        for rx, why in rules:
            m = re.search(rx, low)
            if m:
                frag = line[max(0, m.start() - 15): m.end() + 15].strip()
                hits.append(f"{path}:{n}: {why} - \"{frag}\"")
    return hits


def main(argv):
    ap = argparse.ArgumentParser(description="Anti-jargon stoplist check for video texts")
    ap.add_argument("files", nargs="*", help="text files to check (md, txt, json)")
    ap.add_argument("--lang", help="locale code of config/locales/<lang>.yaml (default: the client's passport language, else en)")
    ap.add_argument("--client", help="read the language from clients/<client>/passport.yaml")
    a = ap.parse_args(argv[1:])
    if not a.files:
        ap.print_help()
        return 0
    lang = a.lang or (passport_language(a.client) if a.client else None) or "en"
    rules = load_rules(lang)
    total = 0
    for f in a.files:
        p = Path(f)
        if not p.is_file():
            print(f"{f}: no such file")
            continue
        for h in check(p, rules):
            print(h)
            total += 1
    print(f"total findings: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
