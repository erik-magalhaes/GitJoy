#!/usr/bin/env python3
"""Fotos OFICIAIS das caixas (fotos de divulgação das editoras publicadas nas lojas Shopify):
cuckoo.jpg (HABA, Board Game Bliss), gravity.jpg (Sit Down!/Luma, Shop of Magic), draft3d.jpg (Ankama, Shop of Magic),
scooby.jpg (capa da CMON, Board Game Bliss). Recorte do fundo branco por flood fill a partir das bordas + casco convexo.

    python3 recortes_oficiais.py      # assets/oficial/*.png
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageFilter

OF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "oficial")


def recorta(nome, saida, tol=18):
    a = np.array(Image.open(os.path.join(OF, nome)).convert("RGB"))
    h, w = a.shape[:2]
    fundo = (a.min(2) > 255 - tol * 3).astype(np.uint8)
    m = np.zeros((h + 2, w + 2), np.uint8)
    cheio = fundo.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + [(x, 0) for x in range(0, w, 20)] + \
            [(x, h - 1) for x in range(0, w, 20)] + [(0, y) for y in range(0, h, 20)] + [(w - 1, y) for y in range(0, h, 20)]:
        if cheio[y, x] == 1:
            cv2.floodFill(cheio, m, (x, y), 2)
    obj = (cheio != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj)
    obj = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    pts = cv2.findNonZero(obj)
    alfa = np.zeros((h, w), np.uint8)
    cv2.fillPoly(alfa, [cv2.convexHull(pts)], 255)
    alfa = cv2.erode(alfa, np.ones((3, 3), np.uint8))
    im = Image.fromarray(np.dstack([a, alfa]), "RGBA")
    im = im.crop(im.getbbox())
    im.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(0.8)))
    im.save(os.path.join(OF, saida))
    print("ok", saida, im.size)


if __name__ == "__main__":
    recorta("cuckoo.jpg", "go_cuckoo.png")
    recorta("gravity.jpg", "gravity_superstar.png")
    recorta("draft3d.jpg", "draftosaurus.png")
    sc = Image.open(os.path.join(OF, "scooby.jpg")).convert("RGBA")  # capa reta (sem foto 3D oficial)
    sc.save(os.path.join(OF, "scooby_doo.png"))
    print("ok scooby_doo.png", sc.size)
