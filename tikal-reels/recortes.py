#!/usr/bin/env python3
"""Recortes OFICIAIS do Tikal (edição Super Meeple, a mesma da Conclave no Brasil) para a animação.
Fontes em assets/orig/ (fora do git): manual oficial francês (supermeeple.com/wp-content/uploads/2015/02/ReglesTikalBD.pdf),
renders oficiais TIKALmeeple.jpg / TIKALtresors.jpg / TIKALtemples.jpg e a caixa FR 3497 px.
  - hexágonos (templo, clareira, ruína, vulcão): página 2 do manual a 400 dpi + máscara de HEXÁGONO geométrica (lado
    plano em cima) + Real-ESRGAN x2 (via x4 e reduz) → assets/pecas/hex_*.png
  - exploradores: TIKALmeeple.jpg (fundo verde) → cada meeple por cor/saturação → assets/pecas/meeple_<cor>.png
  - tesouros: TIKALtresors.jpg (8 fichas redondas) → círculos → assets/pecas/tesouro_N.png

    /usr/bin/python3 recortes.py
"""
import os
import subprocess

import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(ROOT, "assets", "orig")
PEC = os.path.join(ROOT, "assets", "pecas")
MODELO = "/tmp/claude-0/-home-user-GitJoy/153e5d98-d8cd-5f33-8f51-eae5254c4f72/scratchpad/RealESRGAN_x4.onnx"
AMPLIA = os.path.join(os.path.dirname(ROOT), "wonderland-reels", "ampliar_tab.py")

# (página, caixa aproximada a 400 dpi) — conferidas na página 2 ("Les différents types d'hexagone")
HEX = {"templo": (1, 2804, 332, 3251, 724), "clareira": (1, 2811, 847, 3259, 1239),
       "ruina": (1, 2804, 1494, 3251, 1886), "vulcao": (1, 2811, 2490, 3259, 2882)}


def pagina(i, dpi=400):
    p = os.path.join(ORIG, f"_p{i}_{dpi}.png")
    if not os.path.exists(p):
        pymupdf.open(os.path.join(ORIG, "ReglesTikalBD.pdf"))[i].get_pixmap(dpi=dpi).save(p)
    return Image.open(p).convert("RGB")


def amplia(im, fator=2):
    t = os.path.join(ORIG, "_tmp_in.png")
    o = os.path.join(ORIG, "_tmp_out.png")
    im.save(t)
    subprocess.run(["/usr/bin/python3", AMPLIA, MODELO, t, o], check=True, stdout=subprocess.DEVNULL)
    r = Image.open(o).convert("RGB")
    return r.resize((im.width * fator, im.height * fator), Image.LANCZOS)


def mascara_hex(w, h, enc=0.985):
    """Hexágono com lado plano em cima e embaixo (vértices à esquerda e à direita), suavizado."""
    k = 4
    m = Image.new("L", (w * k, h * k), 0)
    cx, cy, r = w * k / 2, h * k / 2, w * k / 2 * enc
    ry = h * k / 2 * enc
    pts = [(cx + r, cy), (cx + r / 2, cy - ry), (cx - r / 2, cy - ry), (cx - r, cy), (cx - r / 2, cy + ry),
           (cx + r / 2, cy + ry)]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def hexagonos():
    for nome, (pg, x0, y0, x1, y1) in HEX.items():
        im = pagina(pg).crop((x0, y0, x1 + 1, y1 + 1))
        if nome == "vulcao":  # a caixa achada começou cortada no alto: recalcula pela largura (razão 2/√3)
            h = round(im.width * 3 ** 0.5 / 2)
            im = pagina(pg).crop((x0, y1 + 1 - h, x1 + 1, y1 + 1))
        im = amplia(im)
        if nome == "ruina":  # tira a seta branca do manual (canto de baixo à direita) com inpaint
            a = np.asarray(im).copy()
            m = (a.min(2) > 200).astype(np.uint8)
            m[:int(im.height * 0.55)] = 0
            m[:, :int(im.width * 0.55)] = 0
            m = cv2.dilate(m, np.ones((9, 9), np.uint8)) * 255
            im = Image.fromarray(cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA))
        im.putalpha(mascara_hex(im.width, im.height))
        im.save(os.path.join(PEC, f"hex_{nome}.png"))
        print("hex", nome, im.size)


def meeples():
    im = amplia(Image.open(os.path.join(ORIG, "TIKALmeeple.jpg")).convert("RGB"), 4)
    a = np.asarray(im).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    fundo = (g >= r - 4) & (g >= b - 6) & (np.abs(r - b) < 45)  # verde-acinzentado do fundo
    obj = ndimage.binary_opening(~fundo, iterations=3)
    obj = ndimage.binary_fill_holes(obj)
    lab, n = ndimage.label(obj)
    pecas = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        area = (lab[sl] == i).sum()
        if area < 4000:
            continue
        pecas.append((sl[1].start, sl, i, area))
    pecas.sort()
    for k, (_, sl, i, area) in enumerate(pecas):
        m = (lab[sl] == i).astype(np.uint8) * 255
        sp = im.crop((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)).convert("RGBA")
        sp.putalpha(Image.fromarray(m).filter(ImageFilter.GaussianBlur(1.2)))
        sp.save(os.path.join(PEC, f"meeple_{k:02d}.png"))
        print("meeple", k, sp.size, area)


def tesouros():
    """As 8 fichas ficam numa grade 4x2 (centros medidos com HoughCircles no original de 800x450)."""
    im = Image.open(os.path.join(ORIG, "TIKALtresors.jpg")).convert("RGB")
    k = 0
    for cy in (133, 328):
        for cx in (144, 315, 485, 657):
            r = 80
            sp = amplia(im.crop((cx - r, cy - r, cx + r, cy + r)), 3).convert("RGBA")
            m = Image.new("L", (sp.width * 4, sp.height * 4), 0)
            ImageDraw.Draw(m).ellipse((8, 8, sp.width * 4 - 9, sp.height * 4 - 9), fill=255)
            sp.putalpha(m.resize(sp.size, Image.LANCZOS))
            sp.save(os.path.join(PEC, f"tesouro_{k}.png"))
            print("tesouro", k, sp.size)
            k += 1


if __name__ == "__main__":
    os.makedirs(PEC, exist_ok=True)
    import sys
    for f in (sys.argv[1:] or ["hexagonos", "meeples", "tesouros"]):
        globals()[f]()
