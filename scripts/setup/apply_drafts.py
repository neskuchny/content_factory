#!/usr/bin/env python3
"""Move confirmed drafts of a client's locked files into place (the last step of setup, stage 5).

The setup wizard and the onboarding agent write the locked files of a client (passport.yaml,
permissions.yaml, brand/consents.md, product-base/**) as drafts under clients/<slug>/setup/drafts/.
After the person has said "yes" to the summary, the owner's session runs this script: every draft
replaces the file at the same relative path, the drafts folder is removed, and with --activate the
client becomes the active one. The permissions hook lets only the owner's session run scripts/setup/.

    python3 scripts/setup/apply_drafts.py --slug acme-bakery            # show what would move
    python3 scripts/setup/apply_drafts.py --slug acme-bakery --yes --activate
"""
import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# only these may be moved out of the drafts: the locked layer of a client
ALLOWED = ("passport.yaml", "permissions.yaml", "brand/consents.md", "product-base/")


def allowed(rel):
    return any(rel == a or (a.endswith("/") and rel.startswith(a)) for a in ALLOWED)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--slug", required=True)
    ap.add_argument("--yes", action="store_true", help="the person confirmed the summary: move the files")
    ap.add_argument("--activate", action="store_true", help="also write the slug to config/active-client.txt")
    ap.add_argument("--keep-proposed", action="store_true",
                    help="move drafts that still contain `proposed: true` (the person kept them as proposals)")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)  # tests use a throw-away copy
    a = ap.parse_args(argv)

    root = Path(a.root).resolve()
    client = (root / "clients" / a.slug).resolve()
    if client.parent != (root / "clients").resolve() or not client.is_dir():
        ap.error(f"no such client: clients/{a.slug}")
    drafts = client / "setup" / "drafts"
    files = sorted(p for p in drafts.rglob("*") if p.is_file()) if drafts.is_dir() else []
    if not files:
        print(f"nothing to apply: clients/{a.slug}/setup/drafts/ is empty or missing")
        return 0

    plan, refused = [], []
    for f in files:
        rel = f.relative_to(drafts).as_posix()
        (plan if allowed(rel) else refused).append(rel)
    for rel in plan:
        state = "replace" if (client / rel).exists() else "new"
        print(f"{state:>7}  clients/{a.slug}/{rel}")
    for rel in refused:
        print(f"   skip  setup/drafts/{rel} (not a locked file: write it in place instead)")
    proposed = [rel for rel in plan if "proposed: true" in (drafts / rel).read_text(encoding="utf-8", errors="replace")]
    for rel in proposed:
        print(f"   note  {rel} still has `proposed: true`")
    if not a.yes:
        print("dry run: nothing moved. Run again with --yes after the person confirmed the summary.")
        return 0
    if proposed and not a.keep_proposed:
        print("refused: remove `proposed: true` from what the person confirmed, or pass --keep-proposed "
              "if they want these values kept as proposals. Nothing moved.", file=sys.stderr)
        return 3

    for rel in plan:
        dst = client / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(drafts / rel), str(dst))
    if refused:
        # non-locked leftovers go next to the drafts, so the drafts folder (= "setup in progress") disappears
        left = client / "setup" / "not-applied"
        for rel in refused:
            (left / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(drafts / rel), str(left / rel))
        print(f"   moved {len(refused)} non-locked file(s) to clients/{a.slug}/setup/not-applied/: put them in place by hand")
    shutil.rmtree(drafts)
    try:
        (client / "setup").rmdir()
    except OSError:
        pass
    if a.activate:
        (root / "config").mkdir(exist_ok=True)
        (root / "config" / "active-client.txt").write_text(a.slug + "\n", encoding="utf-8")
        print(f"active client: {a.slug}")
    print(f"applied {len(plan)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
