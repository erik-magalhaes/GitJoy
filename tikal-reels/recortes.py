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


# Peças DIGITAIS oficiais do Tikal no Board Game Arena (x.boardgamearena.net/.../games/tikal/260729-0805/img/
# TikalTerrains.png, 6 colunas de 277 px × 8 linhas): arte limpa, sem compressão → Real-ESRGAN x4 = HD de verdade.
BGA_HEX = {"vulcao": (1, 4), "clareira": (1, 1), "templo": (2, 3), "ruina": (0, 3)}


def amplia4(im):
    t = os.path.join(ORIG, "_tmp_in.png")
    o = os.path.join(ORIG, "_tmp_out.png")
    im.save(t)
    subprocess.run(["/usr/bin/python3", AMPLIA, MODELO, t, o], check=True, stdout=subprocess.DEVNULL)
    return Image.open(o).convert("RGB")


def hexagonos_bga():
    folha = Image.open(os.path.join(ORIG, "TikalTerrains.png")).convert("RGBA")
    for nome, (r, c) in BGA_HEX.items():
        y = round(r * folha.height / 8)
        cel = folha.crop((c * 277, y, c * 277 + 277, y + 241))
        a = np.asarray(cel).astype(np.float32)
        al = a[..., 3] / 255
        # fundo fora do hexágono = a própria arte borrada (o ESRGAN não inventa borda magenta/preta)
        rgb = a[..., :3]
        bl = cv2.GaussianBlur(rgb * al[..., None], (0, 0), 6) / np.maximum(cv2.GaussianBlur(al, (0, 0), 6), 1e-3)[..., None]
        rgb = rgb * al[..., None] + bl * (1 - al[..., None])
        pad = 12
        rgb = cv2.copyMakeBorder(np.clip(rgb, 0, 255).astype(np.uint8), pad, pad, pad, pad, cv2.BORDER_REFLECT)
        big = amplia4(Image.fromarray(rgb))
        big = big.crop((pad * 4, pad * 4, big.width - pad * 4, big.height - pad * 4))
        m = Image.fromarray((al * 255).astype(np.uint8)).resize(big.size, Image.LANCZOS)
        m = Image.fromarray(np.clip((np.asarray(m).astype(np.float32) - 128) * 3 + 128, 0, 255).astype(np.uint8))
        m = m.filter(ImageFilter.GaussianBlur(1.2))
        bb = m.getbbox()
        big.putalpha(m)
        big = big.crop(bb)
        big.save(os.path.join(PEC, f"hex_{nome}.png"))
        print("hex bga", nome, big.size)


def tesouros_bga():
    """Fichas de tesouro do BGA (TikalTokens.png, PNG com alfa), na MESMA ordem dos tesouro_N antigos."""
    folha = Image.open(os.path.join(ORIG, "TikalTokens.png")).convert("RGBA")
    a = np.asarray(folha)[..., 3] > 128
    lab, n = ndimage.label(a)
    circ = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        w, h = sl[1].stop - sl[1].start, sl[0].stop - sl[0].start
        if 120 < w < 170 and abs(w - h) < 8 and sl[1].start < 690:
            circ.append((sl[0].start // 100, sl[1].start, sl))
    circ.sort()
    grade = {(r, k): sl for k, (r, _, sl) in enumerate([c for c in circ if c[0] == 0])} | \
            {(r, k): sl for k, (r, _, sl) in enumerate([c for c in circ if c[0] != 0])}
    ordem = [(0, 2), (0, 3), (1, 3), (1, 1), (1, 2), (1, 0), (0, 0), (0, 1)]
    for k, (r, c) in enumerate(ordem):
        sl = grade[(r if r == 0 else max(x[0] for x in grade), c)]
        cel = folha.crop((sl[1].start - 6, sl[0].start - 6, sl[1].stop + 6, sl[0].stop + 6))
        al = np.asarray(cel)[..., 3]
        fundo = Image.new("RGB", cel.size, (60, 90, 110))
        fundo.paste(cel, (0, 0), cel)
        big = amplia4(fundo)
        d = big.width
        m = Image.new("L", (d * 4, d * 4), 0)
        bb = Image.fromarray(al).getbbox()
        ImageDraw.Draw(m).ellipse([v * 16 + 6 for v in bb[:2]] + [v * 16 - 6 for v in bb[2:]], fill=255)
        big.putalpha(m.resize(big.size, Image.LANCZOS))
        big = big.crop(big.getbbox())
        big.save(os.path.join(PEC, f"tesouro_{k}.png"))
        print("tesouro bga", k, big.size)


if __name__ == "__main__":
    os.makedirs(PEC, exist_ok=True)
    import sys
    for f in (sys.argv[1:] or ["hexagonos", "meeples", "tesouros"]):
        globals()[f]()
