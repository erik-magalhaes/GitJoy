#!/usr/bin/env python3
"""Prepara as peças do stop motion a partir do kit de imprensa oficial (Repos Production, BR).

Kit: https://www.rprod.com/en/press/7-wonders-architects  (7warc-press-pack-br-*.zip)

    python3 pecas_oficiais.py /caminho/para/press   # pasta onde o zip foi extraído (contém BR/)

Gera assets/oficial/*.png: cartas retas, as 5 peças da maravilha de Éfeso nos dois lados
(em obras e construída), caixa 3D, logo e fichas recortadas do manual.
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets", "oficial")

CARTAS = {"carta_verso": "ARC_Cards_2_Back_Common", "carta_verde": "ARC_Cards_15_Green_Tablette",
          "carta_azul": "ARC_Cards_8_Blue_2VP", "carta_pedra": "ARC_Cards_3_Grey_Stone",
          "carta_vermelha": "ARC_Cards_12_Red_2H", "carta_verso_efeso": "ARC_Cards_20_Back_Ephesos"}

# cortes das peças de Éfeso no tabuleiro de peças (3946 x 3983): escada, 3 colunas e frontão
Y_TOPO, Y_BASE = 1385, 3254
X_COL = (1392, 2545)
ESCALA_MARAVILHA = 0.30


def carta(src):
    im = Image.open(src).convert("RGB")  # CMYK → RGB
    w, h = 540, 800
    im = im.resize((w, h), Image.LANCZOS)
    im = im.convert("RGBA")
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((6, 6, w * 4 - 7, h * 4 - 7), radius=150, fill=255)
    im.putalpha(m.resize((w, h), Image.LANCZOS))
    return im


def pecas_maravilha(src, lado):
    im = Image.open(src).convert("RGBA")
    W, H = im.size
    caixas = {1: (0, Y_BASE, W, H), 2: (0, Y_TOPO, X_COL[0], Y_BASE), 3: (X_COL[0], Y_TOPO, X_COL[1], Y_BASE),
              4: (X_COL[1], Y_TOPO, W, Y_BASE), 5: (0, 0, W, Y_TOPO)}
    pos = {}
    for k, b in caixas.items():
        p = im.crop(b)
        bb = p.getbbox()
        p = p.crop(bb)
        x0, y0 = b[0] + bb[0], b[1] + bb[1]
        s = ESCALA_MARAVILHA
        p = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
        p.save(os.path.join(OUT, f"efeso_{lado}_{k}.png"))
        pos[k] = [round(x0 * s), round(y0 * s), p.width, p.height]
    return pos, (round(W * ESCALA_MARAVILHA), round(H * ESCALA_MARAVILHA))


def recorte_pagina(img, box, thr=28, cortar_baixo=None, out=None, size=None):
    """Peça impressa no manual sobre fundo claro: máscara pela diferença do fundo + casco convexo."""
    c = np.asarray(img.crop(box).convert("RGB")).astype(np.int16)
    bg = np.median(np.concatenate([c[:4].reshape(-1, 3), c[-4:].reshape(-1, 3)]), 0)
    diff = np.abs(c - bg).max(2)
    m = (diff > thr).astype(np.uint8)
    if cortar_baixo:
        m[cortar_baixo:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, 4]))
    cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = cv2.convexHull(cs[0])
    full = np.zeros(m.shape, np.uint8)
    cv2.fillPoly(full, [hull], 255)
    full = cv2.erode(full, np.ones((3, 3), np.uint8))
    a = cv2.GaussianBlur(full, (3, 3), 0)
    rgba = Image.fromarray(np.dstack([c.astype(np.uint8), a]), "RGBA")
    rgba = rgba.crop(rgba.getbbox())
    if size:
        rgba = rgba.resize((int(rgba.width * size / rgba.height), size), Image.LANCZOS)
    rgba.save(os.path.join(OUT, out))


def icone(img, c, r, out, size=260):
    x, y = c
    im = img.crop((x - r, y - r, x + r, y + r)).convert("RGB").resize((size, size), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse((6, 6, size * 4 - 7, size * 4 - 7), fill=255)
    im.putalpha(m.resize((size, size), Image.LANCZOS))
    im.save(os.path.join(OUT, out))


def main(press):
    import pymupdf
    os.makedirs(OUT, exist_ok=True)
    br = os.path.join(press, "BR")
    for k, f in CARTAS.items():
        carta(os.path.join(br, "03_CONTENT", "_CARDS", f + ".jpg")).save(os.path.join(OUT, k + ".png"))
    pos, tam = pecas_maravilha(os.path.join(br, "03_CONTENT", "_BOARD", "ARC_COMMON_Punchboards_14_DET.png"), "obra")
    pecas_maravilha(os.path.join(br, "03_CONTENT", "_BOARD", "ARC_COMMON_Punchboards_13_DET.png"), "pronto")
    json.dump({"pecas": pos, "tamanho": tam}, open(os.path.join(OUT, "efeso.json"), "w"), indent=1)
    box = Image.open(os.path.join(br, "02_PRODUCT", "_3D", "7ARC_3DBOX_left_BR.png")).convert("RGBA")
    box.resize((box.width // 2, box.height // 2), Image.LANCZOS).save(os.path.join(OUT, "caixa3d.png"))
    lg = Image.open(os.path.join(br, "01_LOGOS", "ARC_BR_Logo.png")).convert("RGBA")
    lg.resize((1000, int(lg.height * 1000 / lg.width)), Image.LANCZOS).save(os.path.join(OUT, "logo_jogo.png"))
    # fichas e marcador do gato, renderizados do manual (vetor) em alta resolução
    doc = pymupdf.open(os.path.join(br, "03_CONTENT", "_RULES", "ARC_BR01_Rules.pdf"))
    k = 72 / 60

    def page(n, x0, y0, x1, y1, dpi=400):
        pix = doc[n].get_pixmap(dpi=dpi, clip=pymupdf.Rect(x0 * k, y0 * k, x1 * k, y1 * k), alpha=False)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    conf = page(1, 270, 555, 450, 610)
    recorte_pagina(conf, (0, 0, 260, conf.height), out="conflito_paz.png", size=300)
    recorte_pagina(conf, (570, 0, 840, conf.height), out="conflito_guerra.png", size=300)
    recorte_pagina(page(0, 185, 295, 240, 375), (0, 0, 367, 534), cortar_baixo=490, out="gato.png", size=420)
    cinzas = page(1, 505, 250, 725, 305, dpi=500)
    for nome, cx in (("madeira", 183), ("pedra", 535), ("tijolo", 885), ("papiro", 1235), ("vidro", 1585)):
        icone(cinzas, (cx, 148), 60, f"ic_{nome}.png")
    amarela = page(1, 785, 250, 830, 305, dpi=500)
    icone(amarela, (165, 146), 60, "ic_ouro.png")
    print("ok:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main(sys.argv[1])
