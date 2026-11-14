#!/usr/bin/env python3
"""strips.py: motion strips for the draft review (harness step 10): frames of a range at 12 fps in one image, with timecodes.
Reads numbered PNG frames (%05d.png, 30 fps) from a folder, writes a strip PNG (or JPG).
Usage: python3 -I strips.py <frames_dir> <t0> <t1> <out.jpg> [--crop y0:y1] [--cols N] [--cell W]
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

d, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
crop = None
cols, cell = 6, 200
if "--crop" in sys.argv:
    a, b = sys.argv[sys.argv.index("--crop") + 1].split(":"); crop = (int(a), int(b))
if "--cols" in sys.argv:
    cols = int(sys.argv[sys.argv.index("--cols") + 1])
if "--cell" in sys.argv:
    cell = int(sys.argv[sys.argv.index("--cell") + 1])
fps_out = 12
times = []
t = t0
while t <= t1 + 1e-9:
    times.append(t); t += 1 / fps_out
frames = sorted({round(t * 30) for t in times})
first = Image.open(os.path.join(d, "%05d.png" % frames[0]))
W, H = first.size
y0, y1 = crop if crop else (0, H)
ch = int(cell * (y1 - y0) / W)
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rows * (ch + 14)), "white")
dr = ImageDraw.Draw(sheet)
font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 11)
for i, f in enumerate(frames):
    im = Image.open(os.path.join(d, "%05d.png" % f)).convert("RGB").crop((0, y0, W, y1)).resize((cell - 2, ch), Image.LANCZOS)
    x, y = (i % cols) * cell, (i // cols) * (ch + 14)
    sheet.paste(im, (x + 1, y + 14))
    dr.text((x + 3, y + 1), "%.2f s  f%d" % (f / 30, f), font=font, fill="black")
sheet.save(out, quality=88)
print(out, sheet.size, len(frames), "frames")
