"""Folha de miniaturas do Mixkit por busca: folha_mix.py q1 q2 ... -> out/mix_<q>.jpg"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
idx = json.load(open("mix/idx.json"))
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
for q in sys.argv[1:]:
    ids = [i for i, v in idx.items() if v["q"] == q]
    C = 6; T = 320
    L = (len(ids) + C - 1) // C
    im = Image.new("RGB", (C * T, L * 190), "white")
    d = ImageDraw.Draw(im)
    for k, i in enumerate(ids):
        try:
            a = Image.open(f"mix/t_{i}.jpg").convert("RGB")
        except Exception:
            continue
        a.thumbnail((T, 180))
        x, y = (k % C) * T, (k // C) * 190
        im.paste(a, (x, y))
        d.text((x + 4, y + 4), i, fill="yellow", font=f, stroke_width=2, stroke_fill="black")
    im.save(f"out/mix_{q}.jpg", quality=80)
