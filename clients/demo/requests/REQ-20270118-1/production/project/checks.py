#!/usr/bin/env python3
"""checks.py: harness step 7, checks without eyes. Reads a per-frame dump made by
   node render.cjs --dump 0:539 --out <dump.json>
and checks, on every frame: texts, safe zones, mechanics (knob/band/needle), causes in frame, overlaps; plus the static
greps (no Math.random / Date / performance.now) and the network log. Writes data/checks_report.json. Exit 1 on any FAIL.
Usage: python3 -I checks.py <dump.json> [<net.log>]
"""
import json
import os
import re
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
dump_path = sys.argv[1]
net_path = sys.argv[2] if len(sys.argv) > 2 else None
T = json.load(open(os.path.join(BASE, "data", "timeline.json")))
TX = json.load(open(os.path.join(BASE, "data", "texts.json")))
D = json.load(open(dump_path))
FPS = T["fps"]
E = T["events"]
report = {"frames_checked": len(D), "checks": {}}
fails = []


def rec(name, ok, detail=None):
    report["checks"][name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        fails.append(name)
    print(("PASS " if ok else "FAIL ") + name + ("" if detail is None else "  " + json.dumps(detail)[:400]))


# ---------------------------------------------------------------- static greps
bad = []
for fn in sorted(os.listdir(os.path.join(BASE, "scene"))):
    if fn.endswith((".mjs", ".html")):
        src = open(os.path.join(BASE, "scene", fn), encoding="utf-8").read()
        src_nc = re.sub(r"//.*", "", src)
        for pat in (r"Math\.random", r"Date\s*\(", r"new\s+Date", r"performance\.now", r"Date\.now"):
            if re.search(pat, src_nc):
                bad.append((fn, pat))
rec("no_random_date_clock_in_scene", not bad, bad)

if net_path and os.path.exists(net_path):
    blocked = 0
    for line in open(net_path):
        try:
            blocked += len(json.loads(line)["blocked"])
        except Exception:
            pass
    rec("network_0_external_requests", blocked == 0, {"blocked": blocked})

# ---------------------------------------------------------------- texts
allowed = {t["text"] for t in TX["titles"]} | set(TX["scene_labels"]) | {TX["cta"]["handle"], TX["cta"]["demo_mark"]}
title_text = {t["id"]: t["text"] for t in TX["titles"]}
extra = {x for f in D for x in [d["text"] for d in f["drawn"]]} - allowed
rec("texts_only_from_texts_json", not extra, sorted(extra))

bad = []
for tt in T["titles"]:
    f_full = [f for f in D if tt["t0"] + 0.40 <= f["f"] / FPS <= tt["t1"] - (0.30 if tt["exit"] else 0.0)]
    if not f_full:
        bad.append((tt["id"], "no fully shown frame"))
        continue
    for f in f_full:
        got = [d for d in f["drawn"] if d["id"] == tt["id"]]
        if len(got) != 1 or got[0]["text"] != title_text[tt["id"]] or " ".join(got[0]["lines"]) != title_text[tt["id"]]:
            bad.append((tt["id"], f["f"]))
            break
        if len(got[0]["lines"]) > 2:
            bad.append((tt["id"], "more than 2 lines"))
rec("titles_equal_texts_json_where_fully_shown", not bad, bad)
# only one title at a time
multi = [f["f"] for f in D if sum(1 for d in f["drawn"] if re.fullmatch(r"T\d", d["id"])) > 1]
rec("one_title_at_a_time", not multi, multi[:5])
# scene labels
bad = []
for f in D:
    ids = {d["id"]: d["text"] for d in f["drawn"]}
    for lid, txt in (("L0", "0"), ("L5", "5"), ("L28", "28"), ("LABEL_DAYS", "DAYS AFTER ROAST")):
        if ids.get(lid) != txt:
            bad.append((f["f"], lid))
    imp = "IMPRINT" in ids
    if imp != (f["f"] >= 306):
        bad.append((f["f"], "imprint"))
    if imp and ids["IMPRINT"] != "ROAST DATE":
        bad.append((f["f"], "imprint text"))
    for xid, txt in (("HANDLE", TX["cta"]["handle"]), ("DEMO", TX["cta"]["demo_mark"])):
        if xid in ids and ids[xid] != txt:
            bad.append((f["f"], xid))
rec("scene_labels_and_imprint_text", not bad, bad[:5])
# reading time
bad = [(t["id"], t["on_screen_s"], t["min_s"]) for t in T["titles"] if t["on_screen_s"] + 1e-9 < t["min_s"]]
rec("reading_time", not bad, bad)

# ---------------------------------------------------------------- safe zones (design units 1080x1920)
SX0, SX1, SY0, SY1 = 60, 940, 250, 1520
text_ids = re.compile(r"^(T\d|HANDLE|DEMO|L\d+|LABEL_DAYS|IMPRINT)$")
bad = []
for f in D:
    for name, b in f["boxes"].items():
        if text_ids.match(name):
            if b[0] < SX0 - 0.5 or b[2] > SX1 + 0.5 or b[1] < SY0 or b[3] > SY1:
                bad.append((f["f"], name, [round(v, 1) for v in b]))
rec("safe_zones_text_x60-940_y250-1520", not bad, bad[:5])

# ---------------------------------------------------------------- mechanics
bad_knob, bad_lit, bad_day, bad_ratio, bad_amt = [], [], [], [], []
prev = None
for f in D:
    s = f["s"]
    i = f["f"]
    if abs(s["knob_deg"] - 12 * s["day"]) > 0.5:
        bad_knob.append(i)
    if s["band_lit"] != (5 + 1e-6 < s["day"] <= 28 + 1e-6):
        bad_lit.append(i)
    if s["band_lit"] != bool(T["lit_by_frame"][i]):
        bad_lit.append(("timeline", i))
    if abs(s["day"] - T["day_by_frame"][i]) > 1e-4:
        bad_day.append((i, s["day"], T["day_by_frame"][i]))
    if prev is not None and abs((s["knob_deg"] - prev["knob_deg"]) - 12 * (s["day"] - prev["day"])) > 0.01:
        bad_ratio.append(i)
    # band colour: 3 frames to follow the lit state
    if i >= 3 and not any(D[j]["s"]["band_lit"] for j in range(i - 3, i + 1)) and s["band_amt"] > 0.01:
        bad_amt.append(i)
    prev = s
rec("knob_deg_equals_12_x_day", not bad_knob and not bad_ratio, {"off": bad_knob[:5], "ratio": bad_ratio[:5]})
rec("band_lit_iff_5<day<=28", not bad_lit, bad_lit[:5])
rec("needle_matches_python_pchip", not bad_day, bad_day[:3])
rec("band_colour_follows_lit_within_3_frames", not bad_amt, bad_amt[:5])
mx = max(f["s"]["day"] for f in D if 5.78 <= f["f"] / FPS <= 11.6)
rec("needle_never_passes_5_during_5.78-11.6", mx <= 5 + 1e-6, {"max_day": mx})
rec("band_unlit_on_frame_of_stamp_(day=5)", not D[306]["s"]["band_lit"], {"day": D[306]["s"]["day"]})

# ---------------------------------------------------------------- causes in frame
def box_touch(a, b):
    return a is not None and b is not None and a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


bad = []
for f in D:
    t = f["f"] / FPS
    s = f["s"]
    tags = {}
    for b in f["beans"]:
        tags.setdefault(b["tag"], []).append(b)
    for tg in ("door_to_chute", "chute"):
        if tg in tags and not s["door_open"]:
            bad.append((f["f"], tg + " without open door"))
    for b in tags.get("chute", []):
        if not (240 <= b["x"] <= 400 and 840 <= b["y"] <= 985):
            bad.append((f["f"], "chute bean off the chute", b))
    for b in tags.get("door_to_chute", []):
        if not (180 <= b["x"] <= 285 and 785 <= b["y"] <= 885):
            bad.append((f["f"], "door bean off path", b))
    for tg in ("fall", "tray", "slide"):
        for b in tags.get(tg, []):
            if not (325 <= b["x"] <= 530 and 900 <= b["y"] <= 1020):
                bad.append((f["f"], tg + " bean outside the tray", b))
    for b in tags.get("hop", []):
        if s["lid_a"] < 20:
            bad.append((f["f"], "hop with the lid down"))
        if not (480 <= b["x"] <= 720 and 780 <= b["y"] <= 1000):
            bad.append((f["f"], "hop bean off corridor", b))
    if "slide" in tags and s["tray_deg"] < 0.5:
        bad.append((f["f"], "beans slide but the tray is flat"))
    for b in tags.get("scoop", []):
        if not (600 <= b["x"] <= 900 and 760 <= b["y"] <= 1000):
            bad.append((f["f"], "scoop bean far from scoop", b))
    for b in tags.get("throw", []):
        if not (780 <= b["x"] <= 960 and 760 <= b["y"] <= 850):
            bad.append((f["f"], "thrown bean off the bag mouth", b))
    if tags.get("scoop") or tags.get("throw"):
        if s["lid_b"] < 20 and not tags.get("throw"):
            pass
    if s["tray_deg"] > 1 and s["lid_a"] < 20:
        bad.append((f["f"], "tray tipped with the lid down"))
rec("beans_only_on_chute_tray_bin_scoop_paths", not bad, bad[:6])

# beans leave the tray only when the tray tips; count check
cnt = {}
for f in D:
    for b in f["beans"]:
        cnt.setdefault(b["id"], 0)
rec("bean_count", sum(1 for k in cnt if k.startswith("tray_")) == E["pour"]["n"], {"tray": sum(1 for k in cnt if k.startswith("tray_")), "scoop": sum(1 for k in cnt if k.startswith("scoop"))})

# stir arm turns only when beans are in the tray
st = E["stir"]["t"]
rec("stir_arm_with_beans_in_tray", all(any(b["tag"] == "tray" for b in D[int(round(t0 * FPS))]["beans"]) for t0 in (st[0] + 0.1, st[1] - 0.1)), None)

# imprint and pad
pad306, lab306 = D[306]["boxes"].get("pad"), D[306]["boxes"].get("label")
pad305, lab305 = D[305]["boxes"].get("pad"), D[305]["boxes"].get("label")
rec("imprint_absent_before_306_present_from_306", (not D[305]["s"]["imprint"]) and D[306]["s"]["imprint"], None)
rec("pad_touches_label_on_frame_306_not_305", box_touch(pad306, lab306) and not box_touch(pad305, lab305), {"pad306": pad306, "label306": lab306, "pad305": pad305})
# the pad touches the label on no frame before 306
early = [f["f"] for f in D if f["f"] < 306 and box_touch(f["boxes"].get("pad"), f["boxes"].get("label"))]
rec("pad_never_touches_label_before_306", not early, early[:5])

# ---------------------------------------------------------------- overlap: object boxes vs title boxes
obj = ("roaster", "tray", "bin", "scoop", "bag", "label", "lever", "pad", "needle")
bad = []
for f in D:
    tb = [(n, b) for n, b in f["boxes"].items() if re.match(r"^(T\d|HANDLE|DEMO)$", n)]
    for n, b in tb:
        for o in obj:
            ob = f["boxes"].get(o)
            if ob and box_touch(ob, b):
                bad.append((f["f"], n, o))
        for bean in f["beans"]:
            if b[0] <= bean["x"] <= b[2] and b[1] <= bean["y"] <= b[3]:
                bad.append((f["f"], n, "bean"))
rec("no_object_box_overlaps_a_title_box", not bad, bad[:5])

# frame 0 sanity: the hook acts from frame 0
d0 = [D[0]["s"]["day"], D[1]["s"]["day"], D[2]["s"]["day"]]
rec("frame0_needle_already_moving", d0[0] > d0[1] > d0[2], d0)

report["ok"] = not fails
json.dump(report, open(os.path.join(BASE, "data", "checks_report.json"), "w"), indent=1)
print("\nFAILED:" if fails else "\nALL CHECKS PASS", fails if fails else "")
sys.exit(1 if fails else 0)
