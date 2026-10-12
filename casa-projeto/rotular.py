"""Escreve o nome dos cômodos sobre a imagem da planta 3D: python3 rotular.py out/imagem.png"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def rotular(png):
    im = Image.open(png).convert("RGB")
    W, H = im.size
    pts = json.load(open(os.path.splitext(png)[0] + ".json"))
    d = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(FONTE, max(14, W // 85))
    for nome, x, y in pts:
        if not (0.03 < x < 0.97 and 0.03 < y < 0.97):
            continue
        cx, cy = x * W, y * H
        l, t, r, b = d.textbbox((0, 0), nome.upper(), font=f)
        w, h = r - l, b - t
        pad = h * 0.45
        d.rounded_rectangle((cx - w / 2 - pad, cy - h / 2 - pad, cx + w / 2 + pad, cy + h / 2 + pad),
                            radius=h * 0.6, fill=(255, 255, 255, 215), outline=(60, 60, 60, 160), width=1)
        d.text((cx - w / 2 - l, cy - h / 2 - t), nome.upper(), font=f, fill=(35, 35, 35))
    saida = png.replace(".png", "_rotulos.png")
    im.save(saida)
    return saida


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(rotular(p))
