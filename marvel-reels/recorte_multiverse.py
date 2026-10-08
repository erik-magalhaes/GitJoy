#!/usr/bin/env python3
"""Recorta a caixa 3D do Marvel United: Multiverse (foto da loja em fundo branco) por flood fill a partir das bordas."""
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))


def recorta(src, dst, box=None):
    img = cv2.imread(src)
    if box:
        x0, y0, x1, y1 = box
        img = img[y0:y1, x0:x1]
    h, w = img.shape[:2]
    branco = (np.abs(img.astype(int) - 255).max(axis=2) < 18).astype(np.uint8)
    n, lab, _, _ = cv2.connectedComponentsWithStats(branco, connectivity=4)
    externos = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fundo = np.isin(lab, list(externos)) & (branco > 0)
    m = (~fundo).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8) * 255
    m = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (3, 3), 0)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB), m]), "RGBA")
    rgba.crop(rgba.getbbox()).save(dst)


if __name__ == "__main__":
    F = os.path.join(ROOT, "assets", "fotos")
    recorta(os.path.join(F, "mv_1736429485827.jpg"), os.path.join(ROOT, "assets", "multiverse_caixa.png"))
    recorta(os.path.join(F, "mv_1736429488890.jpg"), os.path.join(ROOT, "assets", "multiverse_verso.png"))
    print("ok")
