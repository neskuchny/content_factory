#!/usr/bin/env python3
"""build_timeline.py: shotlist.json -> data/texts.json + data/timeline.json (harness steps 4 and 5).

Reads the director's shotlist (source of truth), carries over the texts, the needle keys, the text windows and the
sound events, derives what the scene and sound.py both need (PCHIP needle, band transitions, detent clicks, tone
intervals) and runs the step-5 checks. Pure python, no randomness. Run:  python3 -I build_timeline.py
"""
import json
import math
import os
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SHOT = os.path.join(BASE, "..", "shotlist.json")
FPS = 30
EPS = 1e-6


# ---------------------------------------------------------------- PCHIP (same formulas as scene/anim.mjs and scipy)
def pchip_slopes(xs, ys):
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    dl = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    d = [0.0] * n
    for k in range(1, n - 1):
        if dl[k - 1] * dl[k] <= 0:
            d[k] = 0.0
        else:
            w1 = 2 * h[k] + h[k - 1]
            w2 = h[k] + 2 * h[k - 1]
            d[k] = (w1 + w2) / (w1 / dl[k - 1] + w2 / dl[k])

    def edge(h0, h1, d0, d1):
        v = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
        if (v > 0) != (d0 > 0) or v == 0:
            return 0.0
        if (d0 > 0) != (d1 > 0) and abs(v) > 3 * abs(d0):
            return 3 * d0
        return v

    d[0] = edge(h[0], h[1], dl[0], dl[1])
    d[-1] = edge(h[-1], h[-2], dl[-1], dl[-2])
    return d


class Needle:
    def __init__(self, keys):
        self.xs = [k["t"] for k in keys]
        self.ys = [float(k["day"]) for k in keys]
        self.d = pchip_slopes(self.xs, self.ys)

    def day(self, t):
        xs, ys, d = self.xs, self.ys, self.d
        if t <= xs[0]:
            return ys[0]
        if t >= xs[-1]:
            return ys[-1]
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if xs[m] <= t:
                lo = m
            else:
                hi = m
        h = xs[lo + 1] - xs[lo]
        s = (t - xs[lo]) / h
        h00 = 2 * s ** 3 - 3 * s ** 2 + 1
        h10 = s ** 3 - 2 * s ** 2 + s
        h01 = -2 * s ** 3 + 3 * s ** 2
        h11 = s ** 3 - s ** 2
        return h00 * ys[lo] + h10 * h * d[lo] + h01 * ys[lo + 1] + h11 * h * d[lo + 1]

    def slope_end(self, i):
        return self.d[i]


def lit(day):
    return (day > 5 + EPS) and (day <= 28 + EPS)


def main():
    S = json.load(open(SHOT, encoding="utf-8"))
    problems = []

    # ------------------------------------------------------------------ step 4: texts.json
    texts = {
        "_note": "Copied character for character from shotlist.json (texts_exact, scene_labels_exact, cta). Do not edit by hand.",
        "titles": [{"id": t["id"], "text": t["text"]} for t in S["texts_exact"]],
        "scene_labels": S["scene_labels_exact"],
        "cta": {"title": S["cta"]["title"], "handle": S["cta"]["handle"]["text"], "demo_mark": S["cta"]["demo_mark"]["text"]},
    }
    for t in S["texts_exact"]:
        if t["keyword"] not in t["text"]:
            problems.append("keyword not in text " + t["id"])
        if len(t["text"].split()) != t["words"]:
            problems.append("word count " + t["id"])

    # ------------------------------------------------------------------ windows
    win = {}
    for b in S["beats"]:
        for tx in b["texts"]:
            win[tx["id"]] = tx["t"]
    titles = []
    for t in S["texts_exact"]:
        w = win[t["id"]]
        need = max(1.5, 0.6 + 0.25 * t["words"])
        dur = w[1] - w[0]
        if dur + 1e-9 < need:
            problems.append("title %s on screen %.2f s < %.2f s" % (t["id"], dur, need))
        if abs(t["min_s"] - need) > 1e-9:
            problems.append("min_s mismatch " + t["id"])
        titles.append({"id": t["id"], "text": t["text"], "keyword": t["keyword"], "t0": w[0], "t1": w[1], "in": 0.35, "out": 0.25,
                       "exit": (w[1] < S["canvas"]["duration"] - 1e-9), "words": t["words"], "on_screen_s": round(dur, 3), "min_s": need})
    extras = [
        {"id": "HANDLE", "text": S["cta"]["handle"]["text"], "t0": win["HANDLE"][0], "t1": win["HANDLE"][1], "y": S["cta"]["handle"]["y"], "size": 44, "alpha": 1.0},
        {"id": "DEMO", "text": S["cta"]["demo_mark"]["text"], "t0": win["DEMO"][0], "t1": win["DEMO"][1], "y": S["cta"]["demo_mark"]["y"] + 6, "size": 32, "alpha": S["cta"]["demo_mark"]["opacity"]},  # size 32 (was 26) and y + 6 (was 512): review fix, the disclosure line is about 30 px tall and keeps a gap to the handle
    ]

    # ------------------------------------------------------------------ beats
    beats = [{"id": b["id"], "n": b["n"], "t": b["t"], "frames": b["frames"]} for b in S["beats"]]
    for i, b in enumerate(beats):
        if i and abs(b["t"][0] - beats[i - 1]["t"][1]) > 1e-9:
            problems.append("gap before " + b["id"])
        if b["frames"][0] != round(b["t"][0] * FPS) or b["frames"][1] != round(b["t"][1] * FPS) - 1:
            problems.append("frames of " + b["id"])
    if abs(beats[-1]["t"][1] - S["canvas"]["duration"]) > 1e-9 or beats[-1]["frames"][1] != S["canvas"]["frames"] - 1:
        problems.append("beats do not sum to 18.0 s / 540 frames")

    # ------------------------------------------------------------------ needle, band, clicks
    keys = S["needle_keys"]
    nd = Needle(keys)
    frames = S["canvas"]["frames"]
    day_by_frame = [round(nd.day(f / FPS), 6) for f in range(frames)]
    lit_by_frame = [lit(nd.day(f / FPS)) for f in range(frames)]

    # band transitions found on a fine grid (1/6000 s), refined by bisection
    def refine(t0, t1, want):
        for _ in range(60):
            m = (t0 + t1) / 2
            if lit(nd.day(m)) == want:
                t1 = m
            else:
                t0 = m
        return t1

    transitions = []
    prev = lit(nd.day(0.0))
    n_grid = int(S["canvas"]["duration"] * 6000)
    for i in range(1, n_grid + 1):
        t = i / 6000
        cur = lit(nd.day(t))
        if cur != prev:
            transitions.append({"t": round(refine((i - 1) / 6000, t, cur), 5), "lit": cur})
            prev = cur
    initial_lit = lit(nd.day(0.0))
    intervals = []
    start = 0.0 if initial_lit else None
    for tr in transitions:
        if tr["lit"]:
            start = tr["t"]
        else:
            intervals.append([start, tr["t"]])
            start = None
    if start is not None:
        intervals.append([start, S["canvas"]["duration"]])

    # detent clicks: every integer day reached or crossed, per key segment (start excluded, end included).
    # A segment that starts below 0 is the reseat after the overshoot: it belongs to the settle tap, no click.
    clicks = []
    xs, ys = nd.xs, nd.ys
    for i in range(len(xs) - 1):
        a, b = ys[i], ys[i + 1]
        if a == b or a < 0:
            continue
        step = 1 if b > a else -1
        d = int(math.floor(a)) + 1 if step > 0 else int(math.ceil(a)) - 1
        while (d <= b + 1e-12) if step > 0 else (d >= b - 1e-12):
            target = float(d)
            end_hold = (abs(d - b) < 1e-12) and abs(nd.d[i + 1]) < 1e-12
            if end_hold:  # the detent seats within 0.02 day of the final value
                target = d - step * 0.02
            t0, t1 = xs[i], xs[i + 1]
            for _ in range(60):
                m = (t0 + t1) / 2
                v = nd.day(m)
                reached = (v >= target) if step > 0 else (v <= target)
                if reached:
                    t1 = m
                else:
                    t0 = m
            clicks.append({"t": round(t1, 5), "day": d, "dir": step, "seg": i})
            d += step
    clicks.sort(key=lambda c: c["t"])
    groups = {"sweep_hook": 0, "hops": 0, "glide": 0, "back": 0}
    for c in clicks:
        if c["t"] < 1.5:
            groups["sweep_hook"] += 1
        elif c["t"] < 8.5:
            groups["hops"] += 1
        elif c["t"] < 14.0:
            groups["glide"] += 1
        else:
            groups["back"] += 1
    if [groups[k] for k in ("sweep_hook", "hops", "glide", "back")] != [31, 5, 23, 14]:
        problems.append("clicks per group %s, expected 31/5/23/14" % groups)

    # day counter (review fix, jury 1): "Day n" pops on each of the five hops, at the click time of the hop (arrival of the needle).
    # Derived from the clicks, not from the shotlist: the words come from the "5 days" fact (no new fact). Text window ends with T3.
    hop_clicks = [c for c in clicks if 5.5 < c["t"] < 8.5 and c["dir"] == 1]
    t3 = next(t for t in titles if t["id"] == "T3")
    counter = {"font": "700 48px Inter", "x": 60, "y": 440, "pop_s": 0.12, "rise_px": 14, "t1": t3["t1"], "out": t3["out"],
               "items": [{"n": c["day"], "text": "Day %d" % c["day"], "t": c["t"]} for c in hop_clicks]}
    texts["counter"] = [i["text"] for i in counter["items"]]
    if [i["n"] for i in counter["items"]] != [1, 2, 3, 4, 5]:
        problems.append("counter items %s, expected days 1..5" % [i["n"] for i in counter["items"]])
    if counter["items"] and counter["items"][-1]["t"] + 0.2 > counter["t1"] - counter["out"]:
        problems.append("last counter item has under 0.2 s before the fade-out")

    # the needle never passes 5 during 5.78..11.6
    worst = max(nd.day(5.78 + i * (11.6 - 5.78) / 5000) for i in range(5001))
    if worst > 5 + 1e-9:
        problems.append("needle passes 5 during the hops: %.9f" % worst)

    # ------------------------------------------------------------------ events (single source for scene and sound)
    scoop_keys = [
        {"t": 8.60, "x": 748, "y": 1013, "rot": 60, "loaded": False},
        {"t": 8.74, "x": 655, "y": 870, "rot": -4, "ctrl": [780, 860], "loaded": True, "note": "dip: beans come up with the bowl"},
        {"t": 8.86, "x": 822, "y": 800, "rot": 10, "ctrl": [735, 780], "loaded": True},
        {"t": 8.92, "x": 830, "y": 795, "rot": 80, "loaded": True, "note": "tilt over the bag mouth"},
        {"t": 9.04, "x": 830, "y": 795, "rot": 80, "loaded": False},
        {"t": 9.10, "x": 822, "y": 800, "rot": 10, "loaded": False},
        {"t": 9.22, "x": 655, "y": 870, "rot": -4, "ctrl": [735, 780], "loaded": True},
        {"t": 9.34, "x": 822, "y": 800, "rot": 10, "ctrl": [735, 780], "loaded": True},
        {"t": 9.40, "x": 830, "y": 795, "rot": 80, "loaded": True},
        {"t": 9.56, "x": 830, "y": 795, "rot": 80, "loaded": False},
        {"t": 9.66, "x": 748, "y": 1013, "rot": 60, "ctrl": [752, 860], "loaded": False, "note": "back to the parking place"},
    ]
    events = {
        "drum": {"spin_up": [2.6, 2.9], "rev_per_s": 0.8, "slow": [3.8, 4.4]},
        "door": {"open_t": 2.9, "open_dur": 0.08, "close_t": 4.4, "close_dur": 0.08},
        "pour": {"t": [3.0, 3.8], "n": 40, "door_to_chute_s": 0.12, "chute_s": 0.3, "fall_s": 0.14},
        "stir": {"t": [3.8, 5.1], "revs": 1},
        "lid_a": {"up": [5.15, 5.85], "lift": 40, "dur": 0.10},
        "tip": {"t": [5.3, 5.8], "deg": 16, "pivot": [515, 985], "up": [5.30, 5.45], "down": [5.62, 5.80], "depart": [5.34, 5.46], "slide_s": 0.10, "hop_s": 0.22},
        "lid_b": {"up": [8.6, 9.7], "lift": 40, "dur": 0.10},
        "scoop_keys": scoop_keys,
        "scoop_pours": [{"t": [8.92, 9.04], "n": 12, "fall_s": 0.20}, {"t": [9.40, 9.52], "n": 12, "fall_s": 0.20}],
        "scoop_dips": [8.74, 9.22],
        "scoop_scale": 1.2,
        "bag_fold": [9.85, 10.0],
        "lever": {"pivot": [1010, 760], "L": 180, "th_rest": -35, "th_hit": 38.9, "down": [10.0, 10.2], "hit": 10.2, "squash": 0.04,
                  "squash_s": 2 / FPS, "up": [10.25, 10.7], "bag_dip": 3},
        "cta": {"t": [15.0, 15.8], "bag_x": 540, "scale": 1.35, "slide_dur": 0.44, "slide_dx": {"roaster": -520, "tray": -640, "bin": -800, "lever": 340},
                "stagger": [["roaster", 15.0], ["tray", 15.08], ["bin", 15.16], ["lever", 15.0]]},
    }

    timeline = {
        "id": S["id"], "seed": S["canvas"]["seed"], "fps": FPS, "frames": frames, "duration": S["canvas"]["duration"],
        "canvas": {"w": 1080, "h": 1920}, "beats": beats, "titles": titles, "extras": extras, "counter": counter,
        "scene_labels": S["scene_labels_exact"],
        "needle_keys": keys,
        "lit": {"initial": initial_lit, "transitions": transitions, "intervals": intervals, "fade_frames": 3, "eps": EPS},
        "clicks": clicks, "click_groups": groups,
        "settle": {"t": 1.40, "day": 0},
        "events": events,
        "day_by_frame": day_by_frame, "lit_by_frame": [1 if v else 0 for v in lit_by_frame],
        "stills_t": S["stills_t"], "cover": S["cover"],
        "pchip_slopes": [round(v, 6) for v in nd.d],
    }
    json.dump(texts, open(os.path.join(BASE, "data", "texts.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(timeline, open(os.path.join(BASE, "data", "timeline.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)

    print("frames", frames, "| beats", len(beats), "| clicks", len(clicks), groups, "| lit intervals", [[round(a, 3), round(b, 3)] for a, b in intervals])
    print("transitions", transitions)
    print("max day in hops", round(worst, 9))
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("build_timeline: OK")


if __name__ == "__main__":
    main()
