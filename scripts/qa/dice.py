#!/usr/bin/env python3
"""Idea dice: N sparks from different categories of config/sparks.yaml (idea-dice skill).
Usage: python3 scripts/qa/dice.py [N] [--seed S]
"""
import argparse
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path):
    cats, cur = {}, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            cur = line[:-1].strip()
            cats[cur] = []
        elif line.strip().startswith("- ") and cur:
            cats[cur].append(line.strip()[2:].strip())
    return {k: v for k, v in cats.items() if v}


def main():
    ap = argparse.ArgumentParser(description="Idea dice")
    ap.add_argument("n", nargs="?", type=int, default=3)
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    seed = a.seed if a.seed is not None else int(time.time()) % 1000000
    rnd = random.Random(seed)
    cats = load(ROOT / "config" / "sparks.yaml")
    names = list(cats)
    rnd.shuffle(names)
    print(f"seed: {seed}")
    for i in range(a.n):
        c = names[i % len(names)]
        print(f"{i + 1}. [{c}] {rnd.choice(cats[c])}")


if __name__ == "__main__":
    main()
