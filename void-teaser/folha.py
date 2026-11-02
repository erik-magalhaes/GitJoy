"""Folha de contato dos candidatos: folha.py prefixo -> out/folha_<prefixo>.jpg"""
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
fs = sorted(glob.glob(f"cand/{sys.argv[1]}_*.jpg"))
T = 300; C = 6
L = (len(fs) + C - 1) // C
im = Image.new("RGB", (C * T, max(1, L) * (T + 24)), "white")
d = ImageDraw.Draw(im)
fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
for i, f in enumerate(fs):
    try:
        a = Image.open(f).convert("RGB"); a.thumbnail((T, T))
    except Exception:
        continue
    x, y = (i % C) * T, (i // C) * (T + 24)
    im.paste(a, (x + (T - a.width) // 2, y))
    d.text((x + 4, y + T + 2), f"{os.path.basename(f)} {Image.open(f).size}", fill="black", font=fnt)
os.makedirs("out", exist_ok=True)
im.save(f"out/folha_{sys.argv[1]}.jpg", quality=80)
