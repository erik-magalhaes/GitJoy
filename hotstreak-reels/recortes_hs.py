#!/usr/bin/env python3
"""Recortes do Hot Streak: bonecos de vinil da foto oficial (fundo verde da pista + branco) com GrabCut."""
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "assets", "fotos")
P = os.path.join(ROOT, "assets", "pecas")


def fundo_pista(c):
    """Máscara do fundo: verde da pista, linhas/estrelas brancas e o branco da mesa."""
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    verde = (h > 40) & (h < 90) & (s > 70) & (v > 60)
    branco = (s < 35) & (v > 170)
    return verde | branco


def recorta(img, box, keep=1, out=None, scale=0.5):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].copy()
    bg = fundo_pista(c)
    mask = np.where(bg, cv2.GC_PR_BGD, cv2.GC_PR_FGD).astype(np.uint8)
    mask[cv2.erode(bg.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0] = cv2.GC_BGD
    mask[cv2.erode((~bg).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0] = cv2.GC_FGD
    small = cv2.resize(c, None, fx=0.5, fy=0.5)
    ms = cv2.resize(mask, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(small, ms, None, bgm, fgm, 5, cv2.GC_INIT_WITH_MASK)
    m = np.isin(ms, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8) * 255
    m = cv2.resize(m, (c.shape[1], c.shape[0]), interpolation=cv2.INTER_LINEAR)
    m = (m > 127).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    order = np.argsort(-st[1:, 4])[:keep] + 1
    m = np.isin(lab, order).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    full = np.zeros_like(m)
    cv2.drawContours(full, cs, -1, 255, -1)
    full = cv2.GaussianBlur(cv2.erode(full, np.ones((3, 3), np.uint8)), (5, 5), 0)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(c, cv2.COLOR_BGR2RGB), full]), "RGBA")
    rgba = rgba.crop(rgba.getbbox())
    rgba = rgba.resize((int(rgba.width * scale), int(rgba.height * scale)), Image.LANCZOS)
    rgba.save(os.path.join(P, out))
    return rgba


def main():
    os.makedirs(P, exist_ok=True)
    img = cv2.imread(os.path.join(F, "HS4751.jpg"))
    recorta(img, (1300, 1750, 2150, 2950), out="hurley.png")
    recorta(img, (3650, 1180, 4480, 2300), out="dangle.png")
    recorta(img, (2950, 2580, 4150, 3720), out="gobbler_caido.png")
    print("ok", sorted(os.listdir(P)))


if __name__ == "__main__":
    main()
