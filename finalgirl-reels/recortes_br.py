#!/usr/bin/env python3
"""Recortes OFICIAIS do Final Girl:
- caixas da edição BRASILEIRA (Ludofun, loja oficial store.ludofun.com.br, fotos 1200 px em fundo branco):
  assets/br/base.png (Caixa Base), fg01 Happy Trails (Hans), fg02 Mansão Creech (Poltergeist),
  fg03 Massacre nos Bosques (Inkanyamba), fg04 Carnificina no Circo (Geppetto), fg05 Terror em Maple Lane (Dr. Medo);
- arte de cada assassino tirada do tabuleiro oficial da Van Ryder (assets/oficial/FFn-compview.png), sem o título em inglês.

    python3 recortes_br.py      # assets/recortes/*.png
"""
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
BR = os.path.join(ROOT, "assets", "br")
OF = os.path.join(ROOT, "assets", "oficial")
OUT = os.path.join(ROOT, "assets", "recortes")
CAIXAS = {"base": "base.png", "hans": "fg01.png", "poltergeist": "fg02.png", "inkanyamba": "fg03.png",
          "geppetto": "fg04.png", "drmedo": "fg05.png"}
ASSASSINOS = {"hans": "FF1", "poltergeist": "FF2", "inkanyamba": "FF3", "geppetto": "FF4", "drmedo": "FF5"}


def recorta_branco(path, tol=14):
    a = np.array(Image.open(path).convert("RGB"))
    h, w = a.shape[:2]
    fundo = (a.min(2) > 255 - tol).astype(np.uint8)
    cheio = fundo.copy()
    m = np.zeros((h + 2, w + 2), np.uint8)
    for x, y in [(x, 0) for x in range(0, w, 15)] + [(x, h - 1) for x in range(0, w, 15)] + \
            [(0, y) for y in range(0, h, 15)] + [(w - 1, y) for y in range(0, h, 15)]:
        if cheio[y, x] == 1:
            cv2.floodFill(cheio, m, (x, y), 2)
    obj = (cheio != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj)
    obj = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    alfa = np.zeros((h, w), np.uint8)
    cv2.fillPoly(alfa, [cv2.convexHull(cv2.findNonZero(obj))], 255)
    alfa = cv2.GaussianBlur(cv2.erode(alfa, np.ones((3, 3), np.uint8)), (3, 3), 0)
    im = Image.fromarray(np.dstack([a, alfa]), "RGBA")
    return im.crop(im.getbbox())


def main():
    os.makedirs(OUT, exist_ok=True)
    for k, f in CAIXAS.items():
        im = recorta_branco(os.path.join(BR, f))
        im.save(os.path.join(OUT, f"caixa_{k}.png"))
        print("caixa", k, im.size)
    for k, f in ASSASSINOS.items():
        im = Image.open(os.path.join(OF, f"{f}-compview.png")).convert("RGB")
        w, h = im.size
        art = im.crop((int(0.592 * w), int(0.30 * h), int(0.737 * w), int(0.675 * h)))  # só a arte (sem trilhas nem textos)
        art.save(os.path.join(OUT, f"assassino_{k}.png"))
        print("assassino", k, art.size)


if __name__ == "__main__":
    main()
