#!/usr/bin/env python3
"""Create a new client folder from templates/client/ (run by the setup wizard in the owner's session).

Copies the template and refuses to touch an existing client. The locked files of the template
(passport, permissions, consents, product base) are NOT put in place: they go to
clients/<slug>/setup/drafts/ with the same relative paths, so nothing enters the locked layer before
the person confirms the summary. The draft passport gets `client`, `language` and `name`.
`scripts/setup/apply_drafts.py` moves the drafts into place after the "yes".

    python3 scripts/setup/new_client.py --slug acme-bakery --language en --name "Acme Bakery"
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLUG = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?$")
LANG = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
RESERVED = {"demo", "template", "templates", "all"}
# the locked layer of a client (config/permissions-matrix.yaml → protected); analytics stays in place
LOCKED = ("passport.yaml", "permissions.yaml", "brand/consents.md", "product-base")


def set_field(text, key, value):
    """Replace the value of a top-level `key:` line, keeping any trailing comment."""
    pat = re.compile(rf"^({re.escape(key)}:[ \t]*)([^#\n]*?)([ \t]*#.*)?$", re.M)
    if not pat.search(text):
        return f"{key}: {value}\n" + text
    return pat.sub(lambda m: f"{m.group(1)}{value}{m.group(3) or ''}", text, count=1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--slug", required=True, help="folder name: lowercase latin letters, digits, dashes")
    ap.add_argument("--language", required=True, help="BCP-47 code of the audience language (en, de, ru, pt-BR …)")
    ap.add_argument("--name", default="", help="business name as the person writes it")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)  # tests use a throw-away copy
    a = ap.parse_args(argv)

    root = Path(a.root).resolve()
    if not SLUG.match(a.slug) or a.slug in RESERVED:
        ap.error(f"bad slug {a.slug!r}: use 1-40 lowercase latin letters, digits and dashes "
                 f"(not {', '.join(sorted(RESERVED))})")
    if not LANG.match(a.language):
        ap.error(f"bad language code {a.language!r}: use a BCP-47 code such as en, de, ru, pt-BR")
    template, dest = root / "templates" / "client", root / "clients" / a.slug
    if not template.is_dir():
        ap.error(f"template not found: {template}")
    if dest.exists():
        print(f"client {a.slug!r} already exists: {dest.relative_to(root)} (nothing changed)", file=sys.stderr)
        return 2

    shutil.copytree(template, dest)
    drafts = dest / "setup" / "drafts"
    for rel in LOCKED:
        src = dest / rel
        if src.exists():
            (drafts / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(drafts / rel))
    passport = drafts / "passport.yaml"
    text = passport.read_text(encoding="utf-8")
    text = set_field(text, "client", a.slug)
    text = set_field(text, "language", a.language)
    text = set_field(text, "name", json.dumps(a.name, ensure_ascii=False))
    passport.write_text(text, encoding="utf-8")
    print(f"created clients/{a.slug}/ from templates/client/ (language {a.language}); "
          f"locked files are drafts in clients/{a.slug}/setup/drafts/ until the person confirms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
