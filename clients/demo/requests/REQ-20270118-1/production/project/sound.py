#!/usr/bin/env python3
"""sound.py: all sound of "Freshness dial" made by code (numpy + scipy, seed 20270118). No voice, no music, no files, no licences.
Idea (card.md section 7): each object sounds like what it is, and the lit band has its own warm tone.
Every sound is placed from data/timeline.json (needle clicks, band intervals, event times) and data/bean_events.json (every bean's
landing times), so a sound sits on the frame of the event it belongs to. No whooshes.
Writes: audio/mix_raw.wav (48 kHz stereo 16-bit, exactly 18.000 s), audio/sfx_events.json, audio/sound_measure.json.
Run:  python3 -I sound.py      (then ffmpeg-skill: audio.py --replace, loudness.py -I -14 --tp -1)
"""
import json
import os
import wave

import numpy as np
from scipy import ndimage, signal

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SR = 48000
DUR = 18.0
N = int(round(DUR * SR))          # 864 000 samples = exactly 18.000 s
SEED = 20270118
FPS = 30
rng = np.random.default_rng(SEED)
TL = json.load(open(os.path.join(BASE, "data", "timeline.json")))
BE = json.load(open(os.path.join(BASE, "data", "bean_events.json")))
E = TL["events"]
db = lambda x: 10.0 ** (x / 20.0)
TAX = np.arange(N) / SR

# gains in dB at the point of placement (every source sound is normalised to peak 1 first)
G = {
    "stamp": -0.5, "settle": -3.0, "pour_accent": -6.0, "pour_grain": -12.0, "chute_rattle": -15.0, "tray_tick": -14.0,
    "door_open": -15.0, "door_close": -17.0, "click_sweep": -9.5, "click_hop": -9.0, "click_glide": -11.0, "click_back": -10.5,
    "rumble": -10.5, "stir": -16.0, "lid": -11.0, "slide_tick": -15.0, "bin_thud": -13.0, "dig": -13.0, "patter": -14.0,
    "crinkle": -13.0, "spring": -18.0, "paper_slide": -15.0, "tone": -9.5, "room_rms": -45.0,
}
PEAK_TARGET = -1.3   # sample peak of the raw mix, dBFS (loudness.py then needs only a small gain)


# -------------------------------------------------------------------------------------------------------------- tools
def sos(kind, f, order=2):
    return signal.butter(order, f, kind, fs=SR, output="sos")


def bp(x, lo, hi, order=2):
    return signal.sosfilt(sos("band", [lo, hi], order), x)


def lp(x, f, order=2):
    return signal.sosfilt(sos("low", f, order), x)


def hp(x, f, order=2):
    return signal.sosfilt(sos("high", f, order), x)


def noise(n):
    return rng.standard_normal(n)


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m > 0 else x


def pan_gains(p):
    a = (p + 1) * np.pi / 4
    return np.cos(a) * 1.4142, np.sin(a) * 1.4142


def put(layer, x, t, gdb=0.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N or i + len(x) <= 0:
        return
    j = min(N, i + len(x))
    l, r = pan_gains(pan)
    seg = x[: j - i] * db(gdb)
    layer[0, i:j] += seg * l
    layer[1, i:j] += seg * r


def layer():
    return np.zeros((2, N))


def pan_of_x(x):  # screen x (design px) -> pan, a little narrower than the picture
    return float(np.clip((x - 540.0) / 540.0 * 0.75, -0.8, 0.8))


# ------------------------------------------------------------------------------------------------------ source sounds
def click(f0=2300.0, dur=0.016):
    """a detent click: noise tick + short ring + low knock"""
    n = int(dur * SR); t = np.arange(n) / SR
    nz = bp(noise(n), 1600, 6500) * np.exp(-t / 0.0022)
    ring = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.0040)
    knock = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.0060)
    return norm(0.65 * nz + 0.5 * ring + 0.4 * knock)


def settle_tap():
    n = int(0.22 * SR); t = np.arange(n) / SR
    f = 95 + 70 * np.exp(-t / 0.025)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.055)
    tick = bp(noise(n), 1200, 5000) * np.exp(-t / 0.003)
    knock = np.sin(2 * np.pi * 380 * t) * np.exp(-t / 0.012)
    return norm(0.9 * body + 0.55 * tick + 0.35 * knock)


def clack(close=False):
    n = int(0.09 * SR); t = np.arange(n) / SR
    a = bp(noise(n), 700, 3200) * np.exp(-t / 0.006)
    b = np.roll(bp(noise(n), 900, 3800) * np.exp(-t / 0.005), int(0.011 * SR)) * 0.6
    b[: int(0.011 * SR)] = 0
    tone = np.sin(2 * np.pi * (330 if close else 430) * t) * np.exp(-t / 0.014)
    return norm(a + b + 0.7 * tone)


def tap(f=520.0):
    n = int(0.07 * SR); t = np.arange(n) / SR
    return norm(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.016) + 0.6 * bp(noise(n), 400, 1800) * np.exp(-t / 0.007))


def grain(kind="hard"):
    n = int(0.012 * SR); t = np.arange(n) / SR
    if kind == "hard":      # a bean on the metal chute or tray
        f0 = rng.uniform(2600, 5200)
        x = bp(noise(n), 2200, 7500) * np.exp(-t / 0.0012) + 0.7 * np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.0022)
    elif kind == "paper":   # a bean on the paper bag
        x = bp(noise(n), 1200, 4200) * np.exp(-t / 0.0025) + 0.4 * np.sin(2 * np.pi * rng.uniform(900, 1600) * t) * np.exp(-t / 0.004)
    else:                   # a bean dropping into the closed bin (dull)
        x = lp(noise(n), 900) * np.exp(-t / 0.004) + 0.8 * np.sin(2 * np.pi * rng.uniform(180, 320) * t) * np.exp(-t / 0.007)
    return norm(x)


def stamp():
    n = int(0.40 * SR); t = np.arange(n) / SR
    f = 78 + 75 * np.exp(-t / 0.028)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.085)
    sub = np.sin(2 * np.pi * 46 * t) * np.exp(-t / 0.13)
    slap = bp(noise(n), 900, 4800) * np.exp(-t / 0.011)
    thud = lp(noise(n), 420) * np.exp(-t / 0.04)
    x = 1.0 * body + 0.55 * sub + 0.85 * slap + 0.55 * thud
    x[:int(0.0006 * SR)] *= np.linspace(0.3, 1, int(0.0006 * SR))
    return norm(x)


def spring():
    n = int(0.16 * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for a, f, d in ((1.0, 780, 0.05), (0.6, 1190, 0.04), (0.35, 1730, 0.03)))
    return norm(x + 0.3 * bp(noise(n), 2500, 6000) * np.exp(-t / 0.004))


def crinkle(dur=0.16):
    n = int(dur * SR); out = np.zeros(n)
    u = np.arange(n) / n
    env = np.sin(np.pi * u) ** 1.5
    for _ in range(16):
        s = int(rng.uniform(0, 0.9) * n); L = int(rng.uniform(0.003, 0.010) * SR)
        out[s:s + L] += bp(noise(L + 40), 2400, 8500)[:L] * np.exp(-np.arange(L) / (L * 0.4)) * rng.uniform(0.3, 1.0)
    return norm(out * env)


def tone_signal(t_on, t_off, fade_from=None):
    """warm two-note tone D4 + A4 (sine partials, soft overtones, slight chorus); attack 80 ms, release 30 ms."""
    tt = TAX
    base = (np.sin(2 * np.pi * 293.66 * tt) + 0.85 * np.sin(2 * np.pi * 440.0 * tt) + 0.32 * np.sin(2 * np.pi * 587.33 * tt + 0.7)
            + 0.18 * np.sin(2 * np.pi * 880.0 * tt + 1.3) + 0.45 * np.sin(2 * np.pi * 293.66 * 1.0035 * tt + 2.0) + 0.38 * np.sin(2 * np.pi * 440.0 * 0.9965 * tt + 0.4))
    env = np.zeros(N)
    on = np.clip((tt - t_on) / 0.080, 0, 1); on = 0.5 - 0.5 * np.cos(np.pi * on)
    off = np.clip((t_off - tt) / 0.030, 0, 1); off = 0.5 - 0.5 * np.cos(np.pi * off)
    env = on * off * ((tt >= t_on) & (tt <= t_off))
    if fade_from is not None:  # linear in dB to -30 dB at the end (not to digital zero)
        k = np.clip((tt - fade_from) / (DUR - fade_from), 0, 1)
        env = env * 10 ** (-30 * k / 20)
    return norm(base) * env


def easeBrand(x):
    x1, y1, x2, y2 = 0.22, 1.0, 0.36, 1.0
    bx = lambda u: 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3
    by = lambda u: 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u * u * y2 + u ** 3
    x = np.clip(x, 0, 1); lo = np.zeros_like(x); hi = np.ones_like(x)
    for _ in range(40):
        m = (lo + hi) / 2; lt = bx(m) < x
        lo = np.where(lt, m, lo); hi = np.where(lt, hi, m)
    return by((lo + hi) / 2)



def lufs_blocks(x):
    """ITU-R BS.1770-4 K-weighted block loudness (400 ms, 75 % overlap) and gated integrated loudness, stereo array (2, n)."""
    b1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]; a1 = [1.0, -1.69065929318241, 0.73248077421585]
    b2 = [1.0, -2.0, 1.0]; a2 = [1.0, -1.99004745483398, 0.99007225036621]
    y = np.stack([signal.lfilter(b2, a2, signal.lfilter(b1, a1, c)) for c in x])
    n = int(0.4 * SR); h = int(0.1 * SR)
    z = np.array([np.sum(np.mean(y[:, i:i + n] ** 2, axis=1)) for i in range(0, y.shape[1] - n + 1, h)])
    lk = -0.691 + 10 * np.log10(z + 1e-20)
    g1 = lk > -70
    thr = -0.691 + 10 * np.log10(np.mean(z[g1])) - 10
    g2 = lk > thr
    return lk, -0.691 + 10 * np.log10(np.mean(z[g2]))


# ------------------------------------------------------------------------------------------------------------- layers
L_room, L_click, L_tone, L_mech, L_beans, L_hit = layer(), layer(), layer(), layer(), layer(), layer()
events = []


def ev(id_, t, sound, lay, gdb, pan=0.0, **kw):
    events.append({"id": id_, "t": round(float(t), 4), "frame": int(round(t * FPS)), "sound": sound, "layer": lay, "gain_db": gdb, **kw})


# room tone, -45 dBFS RMS, never digital silence
for c in range(2):
    x = lp(noise(N), 900, 1) + 0.6 * bp(noise(N), 60, 240)
    x = x / np.sqrt(np.mean(x ** 2)) * db(G["room_rms"])
    L_room[c] = x
ev("room", 0.0, "room tone (filtered noise, -45 dBFS RMS)", "room", G["room_rms"])

# ---- B1/B3/B5: detent clicks (73) and the settle tap
cl = TL["clicks"]
for k, c in enumerate(cl):
    t = c["t"]
    if abs(t - 1.40) < 0.02 and c["day"] == 0:
        continue  # the day-0 detent is the settle tap below
    grp = "sweep" if t < 1.5 else "hop" if t < 8.5 else "glide" if t < 14.0 else "back"
    g = G["click_" + grp] + rng.uniform(-1.2, 1.2)
    px = pan_of_x(150 + 26 * c["day"] * 1.0)
    put(L_click, click(rng.uniform(1900, 2800)), t, g, px)
    ev("click_%02d" % k, t, "detent click, day %d" % c["day"], "click", round(g, 1), group=grp, day=c["day"])
put(L_click, settle_tap(), 1.40, G["settle"], pan_of_x(150))
ev("settle", 1.40, "needle settle tap (knock 165->95 Hz + tick)", "click", G["settle"], day=0)

# ---- warm tone tied to band_lit
for a, b in TL["lit"]["intervals"]:
    fade = 17.40 if b >= DUR - 1e-6 else None
    put_tone = tone_signal(a, b, fade_from=fade)
    L_tone[0] += put_tone * db(G["tone"]) * 0.95
    L_tone[1] += put_tone * db(G["tone"]) * 1.0
    ev("tone_%.2f" % a, a, "warm tone D4+A4 (sine partials), attack 80 ms; on while band_lit", "tone", G["tone"], t_on=round(a, 4), t_off=round(b, 4),
       frame_on=int(round(a * FPS)), frame_off=int(round(b * FPS)))

# ---- B2: drum, door, pour, stir
dr = E["drum"]
tt = np.arange(int(round(dr["spin_up"][0] * SR)), int(round(dr["slow"][1] * SR)))
tx = tt / SR
smooth = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
w = dr["rev_per_s"] * smooth(dr["spin_up"][0], dr["spin_up"][1], tx) * (1 - smooth(dr["slow"][0], dr["slow"][1], tx))
rev = np.cumsum(w) / SR
mod = 1 + 0.38 * np.cos(2 * np.pi * 6 * rev)            # six spokes pass the door per turn
br = bp(noise(len(tx)), 55, 130) * 3.0 + bp(noise(len(tx)), 170, 420) * 0.55
rum = br * (w / dr["rev_per_s"]) ** 1.2 * mod
rum = norm(rum)
fi = np.minimum(1, (tx - tx[0]) / 0.25)
rum = rum * fi
put(L_mech, rum, tx[0], G["rumble"], pan_of_x(200))
ev("drum_rumble", tx[0], "drum rumble 55-130 Hz noise, modulated by the spokes", "mech", G["rumble"], t_end=round(tx[-1], 3))
put(L_mech, clack(), E["door"]["open_t"], G["door_open"], pan_of_x(205))
ev("door_open", E["door"]["open_t"], "door clack", "mech", G["door_open"])
put(L_mech, clack(True), E["door"]["close_t"], G["door_close"], pan_of_x(205))
ev("door_close", E["door"]["close_t"], "door clack (softer)", "mech", G["door_close"])

tray_be = [b for b in BE if b["kind"] == "tray"]
# pour: onset accent on the first grains, then one tick per bean that leaves the door, rattle on the chute, tick on landing
put(L_beans, norm(bp(noise(int(0.11 * SR)), 350, 1500) * np.hanning(int(0.11 * SR)) ** 0.5), 3.00, G["pour_accent"], pan_of_x(230))
ev("pour_accent", 3.00, "first rush through the open door (band noise 350-1500 Hz)", "beans", G["pour_accent"])
for b in tray_be:
    d = b["door"]
    g = G["pour_grain"] + (3.0 if d < 3.05 else 0) + rng.uniform(-1.5, 1.5)
    put(L_beans, grain("hard"), d, g, pan_of_x(230))
    put(L_beans, grain("hard"), b["land"], G["tray_tick"] + rng.uniform(-2, 2), pan_of_x(420))
# chute rattle: noise band whose level follows how many beans are on the chute
cnt = np.zeros(N)
for b in tray_be:
    i0, i1 = int(b["door"] * SR), int(b["fall"] * SR)
    cnt[i0:i1] += 1
cnt = lp(cnt, 18, 1)
rat = bp(noise(N), 1500, 4200) * np.clip(cnt / 20.0, 0, 1.4)
pg = pan_gains(pan_of_x(300))
L_beans[0] += rat * db(G["chute_rattle"]) * pg[0]
L_beans[1] += rat * db(G["chute_rattle"]) * pg[1]
ev("pour_stream", 3.00, "one grain tick per bean at the door and at the tray, rattle on the chute", "beans", G["pour_grain"], t_end=round(max(b["land"] for b in tray_be), 3))
# stir arm scrape follows its angular speed (easeInOutSine over 1 turn)
s0, s1 = E["stir"]["t"]
n_s = int(round((s1 - s0) * SR)); ts = np.arange(n_s) / SR
u = ts / (s1 - s0)
speed = np.sin(np.pi * u)
scr = bp(noise(n_s), 850, 3000) * (0.35 + 0.65 * np.clip(lp(noise(n_s), 40, 1) * 6 + 0.6, 0, 1.4))
scr = norm(scr * speed ** 1.2)
put(L_mech, scr, s0, G["stir"], pan_of_x(425))
ev("stir_scrape", s0, "soft scrape of the stir arm, level follows its speed", "mech", G["stir"], t_end=s1)

# ---- B3: lid, tray tips, beans into the bin
la = E["lid_a"]["up"]
put(L_mech, tap(560), la[0], G["lid"], pan_of_x(645)); ev("lid_up_1", la[0], "wooden lid tap", "mech", G["lid"])
put(L_mech, tap(480), la[1], G["lid"] - 2, pan_of_x(645)); ev("lid_down_1", la[1], "wooden lid tap (closing)", "mech", G["lid"] - 2)
for b in tray_be:
    put(L_beans, grain("hard"), b["depart"] + rng.uniform(0, 0.02), G["slide_tick"] + rng.uniform(-2, 2), pan_of_x(470))
    put(L_beans, grain("dull"), b["arrive"], G["bin_thud"] + rng.uniform(-2.5, 2.5), pan_of_x(620))
ev("tray_tip_pour", E["tip"]["depart"][0], "ticks as beans slide off the tray, dull thuds into the bin", "beans", G["bin_thud"],
   t_end=round(max(b["arrive"] for b in tray_be), 3))

# ---- B4: scoop, fold, stamp
lb = E["lid_b"]["up"]
put(L_mech, tap(560), lb[0], G["lid"], pan_of_x(645)); ev("lid_up_2", lb[0], "wooden lid tap", "mech", G["lid"])
put(L_mech, tap(480), lb[1], G["lid"] - 2, pan_of_x(645)); ev("lid_down_2", lb[1], "wooden lid tap (closing)", "mech", G["lid"] - 2)
for k, dip in enumerate(E["scoop_dips"]):
    n_d = int(0.13 * SR); dg = np.zeros(n_d)
    for _ in range(14):
        s = int(rng.uniform(0, 0.85) * n_d); Ls = int(0.004 * SR)
        dg[s:s + Ls] += bp(noise(Ls + 30), 500, 2400)[:Ls] * np.exp(-np.arange(Ls) / (Ls * 0.5)) * rng.uniform(0.3, 1)
    put(L_beans, norm(dg), dip - 0.03, G["dig"], pan_of_x(655))
    ev("scoop_dig_%d" % (k + 1), dip - 0.03, "scoop digs in the beans (grainy scrape)", "beans", G["dig"])
for b in BE:
    if b["kind"] == "scoop":
        put(L_beans, grain("paper"), b["land"] - 0.02, G["patter"] + rng.uniform(-3, 2), pan_of_x(870))
for k, sp in enumerate(E["scoop_pours"]):
    ev("patter_%d" % (k + 1), sp["t"][0], "beans patter on the paper bag (12 grains)", "beans", G["patter"], t_end=round(sp["t"][1] + sp["fall_s"], 3))
fo = E["bag_fold"]
put(L_mech, crinkle(), fo[0], G["crinkle"], pan_of_x(870)); ev("paper_crinkle", fo[0], "paper crinkle as the bag top folds", "mech", G["crinkle"], t_end=fo[1])
lv = E["lever"]
put(L_hit, stamp(), lv["hit"], G["stamp"], pan_of_x(870)); ev("stamp", lv["hit"], "STAMP THUNK: body 150->78 Hz + sub 46 Hz + paper slap", "hit", G["stamp"])
put(L_mech, spring(), lv["up"][0] + 0.05, G["spring"], pan_of_x(1000)); ev("lever_spring", lv["up"][0] + 0.05, "lever spring", "mech", G["spring"])

# ---- B6: paper slides while the props leave (level follows each object's speed; no whoosh)
cta = E["cta"]
for name, pan_x in (("roaster", 200), ("tray", 420), ("bin", 650), ("lever", 1000)):
    t0 = [s for s in cta["stagger"] if s[0] == name][0][1]
    n_p = int(round(cta["slide_dur"] * SR)); ts = np.arange(n_p) / SR
    u = ts / cta["slide_dur"]
    sp = np.gradient(easeBrand(u))
    sp = np.abs(sp) / np.max(np.abs(sp))
    lowb, highb = bp(noise(n_p), 450, 1300), bp(noise(n_p), 1400, 4200)
    x = (lowb * (1 - 0.6 * sp) + highb * 0.6 * sp) * sp
    put(L_mech, norm(x), t0, G["paper_slide"], pan_of_x(pan_x))
    ev("paper_slide_" + name, t0, "paper slides out (scuff, level follows speed)", "mech", G["paper_slide"], t_end=round(t0 + cta["slide_dur"], 3))
n_p = int(round((cta["t"][1] - cta["t"][0]) * SR)); u = np.arange(n_p) / n_p
sp = np.abs(np.gradient(easeBrand(u))); sp /= sp.max()
x = bp(noise(n_p), 500, 2600) * sp
put(L_mech, norm(x), cta["t"][0], G["paper_slide"] + 1, pan_of_x(700))
ev("paper_slide_bag", cta["t"][0], "the bag comes forward (scuff)", "mech", G["paper_slide"] + 1, t_end=cta["t"][1])

# ----------------------------------------------------------------------------------------------------------------- mix
LAYERS = {"room": L_room, "click": L_click, "tone": L_tone, "mech": L_mech, "beans": L_beans, "hit": L_hit}
mix_dry = sum(LAYERS.values())


def limiter(x, ceiling_db, look=0.002, release=0.090):
    """look-ahead peak limiter (sample peak): gain reduction starts `look` s before the peak, recovers with a one-pole release."""
    c = db(ceiling_db); nl = int(look * SR)
    pk = np.max(np.abs(x), axis=0)
    need = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    g = ndimage.minimum_filter1d(need, size=2 * nl + 1, origin=0)
    g = ndimage.uniform_filter1d(g, size=nl + 1, origin=-(nl // 2))   # smooth the attack ramp before the peak
    g = np.minimum(g, need)
    k = np.exp(-1.0 / (release * SR))
    out = np.empty_like(g); cur = 1.0
    for i in range(len(g)):
        gi = g[i]
        cur = gi if gi < cur else gi + (cur - gi) * k   # instant attack (already ramped), exponential release
        out[i] = cur
    return x * out, out


CEIL = -1.4          # dBFS sample-peak ceiling of the limiter (loudness.py then checks true peak <= -1 dBTP)
TARGET_LUFS = -14.0
lo, hi = -10.0, 30.0  # pre-gain search (dB)
for _ in range(14):
    mid = (lo + hi) / 2
    y, _g = limiter(mix_dry * db(mid), CEIL)
    li = lufs_blocks(y)[1]
    if li < TARGET_LUFS:
        lo = mid
    else:
        hi = mid
PRE_GAIN = (lo + hi) / 2
mix, GR = limiter(mix_dry * db(PRE_GAIN), CEIL)
SCALE = db(PRE_GAIN)
# a few samples of fade at the very start and end of the file avoid edge clicks; the tail is room tone + tone at -30 dB, not zero
ramp = np.linspace(0, 1, 48)
mix[:, :48] *= ramp
mix[:, -48:] *= ramp[::-1]

os.makedirs(os.path.join(BASE, "audio"), exist_ok=True)
pcm = np.clip(np.round(mix.T * 32767), -32768, 32767).astype("<i2")
WAV = os.path.join(os.environ.get("FILM_CACHE", os.path.join(BASE, "audio")), "mix_raw.wav")   # the 3.4 MB wav stays out of the repo (FILM_CACHE)
with wave.open(WAV, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())


# ------------------------------------------------------------------------------------------------------------ measure
def peak_db(x):
    m = np.max(np.abs(x))
    return round(20 * np.log10(m + 1e-12), 2)


def win(t0, t1, arr=None):
    a = mix if arr is None else arr
    return a[:, int(t0 * SR):int(t1 * SR)]


lk_blocks, lufs_int = lufs_blocks(mix)
measure = {"bs1770_integrated_lufs": round(float(lufs_int), 2), "momentary_max_lufs": round(float(lk_blocks.max()), 1), "pre_gain_db": round(PRE_GAIN, 2), "max_gain_reduction_db": round(float(-20 * np.log10(GR.min())), 2), "limiter_ceiling_dbfs": CEIL, "samples": mix.shape[1], "duration_s": mix.shape[1] / SR,
           "peak_dbfs": peak_db(mix), "tail_rms_dbfs_17.8-18.0": round(20 * np.log10(np.sqrt(np.mean(win(17.8, 18.0) ** 2)) + 1e-12), 1),
           "event_peaks_dbfs": {
               "stamp_10.20": peak_db(win(10.18, 10.40)), "settle_1.40": peak_db(win(1.38, 1.55)), "pour_3.00": peak_db(win(2.99, 3.12)),
               "door_clack_2.90": peak_db(win(2.89, 2.96)), "hop_clicks_5.9-7.9": peak_db(win(5.88, 7.95)), "sweep_clicks_0-1.35": peak_db(win(0.0, 1.35)),
               "stream_3.2-3.8": peak_db(win(3.2, 3.8)), "scoop_8.6-9.7": peak_db(win(8.6, 9.7)), "glide_11.6-13.8": peak_db(win(11.6, 13.8)),
               "paper_slides_15-15.8": peak_db(win(15.0, 15.8)), "back_14.2-14.8": peak_db(win(14.2, 14.8)), "drum_rumble_3.9-4.4": peak_db(win(3.9, 4.4))}}
tone_env = np.abs(L_tone[1])
th = 0.01 * np.max(tone_env)   # on = more than -40 dB below the tone's own peak (the end fade stays at -30 dB)
frames_on = [int(f) for f in range(int(DUR * FPS)) if np.max(tone_env[int(f / FPS * SR):int((f + 1) / FPS * SR)]) > th]
lit = TL["lit_by_frame"]
mism = [f for f in range(int(DUR * FPS)) if (f in set(frames_on)) != bool(lit[f])]
measure["tone_vs_band_lit"] = {"tone_frames_on": len(frames_on), "band_lit_frames": int(sum(lit)), "mismatched_frames": mism,
                               "max_offset_frames": 0 if not mism else 1}
rms_db = lambda x: round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12), 1)
# intended level of an event = its placement gain + the master pre-gain (every source sound is normalised to peak 1). The limiter then
# flattens the sample peaks of the three loudest events to the ceiling, so the order is read from the intended levels and from the effects' RMS.
body = [e for e in events if e["layer"] not in ("room", "tone")]
intended = sorted(((round(e["gain_db"] + PRE_GAIN, 1), e["id"]) for e in body), reverse=True)
measure["loudest_events_intended_dbfs"] = [list(v) for v in intended[:8]]
measure["loudest_order"] = [v[1] for v in intended[:3]]
fx = (L_click + L_mech + L_beans + L_hit) * db(PRE_GAIN) * GR          # effects only, as they sit in the final mix
EVW = {"stamp_10.20": (10.20, 10.45), "settle_1.40": (1.40, 1.65), "pour_3.00": (3.00, 3.25), "sweep_0.50": (0.50, 0.75), "scoop_patter_9.40": (9.40, 9.65),
       "glide_12.0": (12.0, 12.25), "slide_15.1": (15.1, 15.35), "lid_5.15": (5.15, 5.25)}
measure["event_rms_dbfs_250ms_effects_only"] = {k: rms_db(win(a, b, fx)) for k, (a, b) in EVW.items()}
tl = (L_tone * db(PRE_GAIN) * GR)[:, int(13 * SR):int(14 * SR)]
measure["tone_peak_dbfs_13-14s"] = peak_db(tl); measure["tone_rms_dbfs_13-14s"] = rms_db(tl)
json.dump(measure, open(os.path.join(BASE, "audio", "sound_measure.json"), "w"), indent=1)
events.sort(key=lambda e: e["t"])
json.dump({"seed": SEED, "sr": SR, "duration_s": DUR, "clicks": len(cl), "events": events}, open(os.path.join(BASE, "audio", "sfx_events.json"), "w"), indent=0)
print(json.dumps(measure, indent=1))
