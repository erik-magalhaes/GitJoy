#!/usr/bin/env python3
"""Recortes das fotos oficiais do Coffee Rush (Galápagos, loja.galapagosjogos.com.br/ccstore/v1/products/CFR001):
ingredientes da foto em fundo verde-limão (chave de cor + tirar o verde que vaza nas peças transparentes),
a caixa 3D e a foto dos componentes (PNG com transparência).

    python3 recortes.py
"""
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(ROOT, "assets", "orig")
ING = os.path.join(ROOT, "assets", "ing")
FUNDO = np.array([201, 207, 86], float)
# caixas (x0, y0, x1, y1) na foto de 2000 px
CAIXAS = {"caramelo": (700, 580, 960, 890), "cha": (840, 720, 1240, 1190), "chocolate": (1420, 510, 1800, 820),
          "agua": (1350, 860, 1660, 1120), "gelo": (430, 1290, 730, 1620), "cafe": (840, 1340, 1150, 1680),
          "leite": (1300, 1280, 1560, 1570), "espuma": (1730, 1140, 2000, 1510), "xicara": (0, 540, 640, 1200)}


VIDRO = {"agua", "gelo", "espuma", "xicara"}


def chave(a, vidro=False, lum_sombra=45):
    """Fundo = pixels com a cor do fundo (ou a sombra dele: k·FUNDO, k > 0,6) LIGADOS À BORDA; o resto é a peça."""
    rgb = a[..., :3].astype(float)
    k = (rgb @ FUNDO) / (FUNDO @ FUNDO)
    res = np.sqrt(((rgb - k[..., None] * FUNDO) ** 2).sum(-1))
    # fundo e sombra: R ≈ G − 6, claro, e o azul bem abaixo (a sombra só escurece R/G e "afunda" o azul)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = (r + g) / 2
    pare = ((np.abs(g - r - 6) < 13) & (lum > 120) & (b < lum * 0.56)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(pare, connectivity=4)
    borda = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fundo = np.isin(lab, list(borda)).astype(np.uint8)
    # descasca a sombra escura colada na peça: cresce o fundo por pixels "amarelados" (mesmo escuros)
    sombra = ((np.abs(g - r - 6) < 18) & (b < lum * 0.62) & (lum > lum_sombra)).astype(np.uint8)
    for _ in range(40):
        novo = cv2.dilate(fundo, np.ones((3, 3), np.uint8)) & (sombra | fundo)
        if (novo == fundo).all():
            break
        fundo = novo
    fundo = fundo.astype(bool)
    obj = cv2.morphologyEx((~fundo).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj)
    grandes = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= (0.08 if vidro else 1) * st[1:, cv2.CC_STAT_AREA].max()]
    obj = np.isin(lab, grandes).astype(np.uint8)
    cs, _ = cv2.findContours(obj, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cheio = np.zeros_like(obj)
    if vidro:  # o contorno do vidro não fecha: usa o casco convexo
        cv2.drawContours(cheio, [cv2.convexHull(np.vstack(cs))], -1, 1, -1)
    else:
        cv2.drawContours(cheio, cs, -1, 1, -1)
    alfa = cv2.GaussianBlur(cheio.astype(np.float32), (0, 0), 1.2)
    if vidro:  # o miolo transparente mostra o fundo verde: fica meio transparente e sem o verde
        dentro = np.clip((res - 10) / 40, 0, 1)
        alfa = alfa * np.maximum(dentro, 0.6)
        lum = rgb.mean(-1, keepdims=True)
        vid = lum * np.array([0.97, 1.0, 1.06]) * 1.1 + 12
        w = (1 - dentro)[..., None]
        rgb = rgb * (1 - w) + vid * w
    else:  # a franja da borda puxa o verde do fundo: refaz a cor da borda com a cor de dentro da peça
        faixa = cv2.dilate(cheio, np.ones((7, 7), np.uint8)).astype(bool) & ~cv2.erode(cheio, np.ones((7, 7), np.uint8)).astype(bool)
        rgb = cv2.inpaint(rgb.clip(0, 255).astype(np.uint8), faixa.astype(np.uint8), 4, cv2.INPAINT_TELEA).astype(float)
    return np.dstack([rgb, alfa * 255]).clip(0, 255).astype(np.uint8)


def main():
    os.makedirs(ING, exist_ok=True)
    foto = np.asarray(Image.open(os.path.join(ORIG, "g3.jpg")).convert("RGB"))
    for nome, (x0, y0, x1, y1) in CAIXAS.items():
        a = chave(foto[y0:y1, x0:x1], nome in VIDRO, 100 if nome == "cafe" else 45)
        im = Image.fromarray(a)
        im = im.crop(im.getbbox())
        im.save(os.path.join(ING, nome + ".png"))
    for f, nome in (("g1.jpg", "caixa.png"), ("g2.jpg", "componentes.png"), ("g4.jpg", "baristas.jpg")):
        im = Image.open(os.path.join(ORIG, f))
        if im.mode == "RGBA":
            im = im.crop(im.getbbox())
        im.save(os.path.join(ROOT, "assets", nome))
    print("ok")


if __name__ == "__main__":
    main()
