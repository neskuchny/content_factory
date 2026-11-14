#!/usr/bin/env python3
"""make_sheet.py: contact sheet of the stills for the owner (harness step 8), and the 390 px thumbs.
Reads the full-size stills S_<t>.png from <cache>/stills (not kept in the repo), writes
  stills/sheet.jpg (time + "cause -> event" under each still, <= 600 KB)  and  stills/thumbs/S_<t>_390.jpg
Usage: python3 -I make_sheet.py <stills_dir_with_pngs>
"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC = sys.argv[1]
T = json.load(open(os.path.join(BASE, "data", "timeline.json")))
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"   # only for the sheet captions, not part of the film
FONT_R = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
day = lambda t: T["day_by_frame"][round(t * 30)]
CAP = {
    0.0: "knob turns -> needle sweeps in (day %.0f)" % day(0.0),
    0.5: "needle inside the band (day %.0f) -> band copper" % day(0.5),
    1.6: "needle settled at day 0 -> band unlit",
    3.3: "door open -> beans slide down the chute",
    4.5: "beans in the tray -> stir arm turns",
    6.9: "knob click per hop -> needle on day %d" % round(day(6.9)),
    9.1: "scoop lifts beans from the bin -> bag",
    10.2: "pad touches the label -> imprint appears",
    12.7: "knob turns (day %.0f) -> band copper" % day(12.7),
    14.8: "needle back at day %d -> band still lit" % round(day(14.8)),
    17.0: "one object left: the bag with its date",
}
ts = T["stills_t"]
CW, CH = 330, 383
cols, rows = 4, 3
cap_h = 64
sheet = Image.new("RGB", (CW * cols, (CH + cap_h) * rows), "#F6EFE6")
dr = ImageDraw.Draw(sheet)
fb, fr = ImageFont.truetype(FONT, 17), ImageFont.truetype(FONT_R, 13)
os.makedirs(os.path.join(BASE, "stills", "thumbs"), exist_ok=True)
for i, t in enumerate(ts):
    im = Image.open(os.path.join(SRC, "S_%.2f.png" % t)).convert("RGB")
    crop = im.crop((0, 220, 1080, 1540)).resize((CW - 8, CH - 8), Image.LANCZOS)  # active area: titles, shelf, radio
    x, y = (i % cols) * CW, (i // cols) * (CH + cap_h)
    sheet.paste(crop, (x + 4, y + 4))
    dr.text((x + 8, y + CH), "%.2f s" % t, font=fb, fill="#2B1D14")
    dr.text((x + 8, y + CH + 22), CAP[t], font=fr, fill="#54473E")
    if t in (0.5, 10.2, 17.0):
        w = 390
        im.resize((w, round(w * im.height / im.width)), Image.LANCZOS).save(os.path.join(BASE, "stills", "thumbs", "S_%.2f_390.jpg" % t), quality=82)
# the 12th cell: legend
x, y = 3 * CW, 2 * (CH + cap_h)
dr.text((x + 10, y + 10), "REQ-20270118-1  Freshness dial", font=fb, fill="#2B1D14")
dr.text((x + 10, y + 36), "11 stills, full frame cropped to y 220-1540", font=fr, fill="#54473E")
dr.text((x + 10, y + 56), "(titles, set, radio). FICTIONAL demo.", font=fr, fill="#54473E")
out = os.path.join(BASE, "stills", "sheet.jpg")
q = 82
while True:
    sheet.save(out, quality=q, optimize=True)
    if os.path.getsize(out) <= 600 * 1024 or q <= 40:
        break
    q -= 6
print("sheet.jpg", sheet.size, os.path.getsize(out) // 1024, "KB q", q)
