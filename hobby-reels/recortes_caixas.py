#!/usr/bin/env python3
"""Recorta as caixas das fotos do acervo da Sua Vez (render 3D sobre fundo laranja liso) com GrabCut."""
import glob
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "assets", "caixas_foto")
P = os.path.join(ROOT, "assets", "caixas")


def recorta(path):
    img = cv2.imread(path)
    h, w = img.shape[:2]
    lab = cv2.cvtColor(cv2.GaussianBlur(img, (5, 5), 0), cv2.COLOR_BGR2LAB).astype(np.float32)
    # o fundo é um degradê: modela a cor esperada em cada ponto por um plano ajustado na borda
    borda = np.zeros((h, w), bool)
    borda[:12], borda[-12:], borda[:, :12], borda[:, -12:] = True, True, True, True
    yy, xx = np.mgrid[0:h, 0:w]
    A = np.c_[xx[borda], yy[borda], np.ones(borda.sum())]
    fundo = np.zeros_like(lab)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, lab[..., c][borda], rcond=None)
        fundo[..., c] = coef[0] * xx + coef[1] * yy + coef[2]
    dist = np.linalg.norm(lab - fundo, axis=2)
    # a sombra da caixa tem o mesmo tom do fundo (mesmo ângulo a/b), só que mais escura
    a, b = lab[..., 1] - 128, lab[..., 2] - 128
    fa, fb = fundo[..., 1] - 128, fundo[..., 2] - 128
    dang = np.abs(np.angle(np.exp(1j * (np.arctan2(b, a) - np.arctan2(fb, fa)))))
    cr = np.hypot(a, b) / (np.hypot(fa, fb) + 1e-6)
    sombra = (dang < np.radians(7)) & (cr > 0.55) & (cr < 1.35) & (lab[..., 0] < fundo[..., 0] + 4)
    bg = (dist < 9) | sombra
    dist = np.where(sombra, 0, dist)
    mask = np.where(bg, cv2.GC_PR_BGD, cv2.GC_PR_FGD).astype(np.uint8)
    mask[cv2.erode(bg.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0] = cv2.GC_BGD
    mask[cv2.erode((dist > 30).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0] = cv2.GC_FGD
    bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, None, bgm, fgm, 5, cv2.GC_INIT_WITH_MASK)
    m = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8) & ~sombra
    # descasca de fora para dentro tudo que tem cor de fundo/sombra e está ligado ao fundo
    # (é o que deixava pedaços laranja grudados na caixa, como no Flamecraft)
    descasca = (sombra | (dist < 14)).astype(np.uint8)
    n_, lab2, _, _ = cv2.connectedComponentsWithStats(descasca, connectivity=4)
    externos = set(np.unique(np.r_[lab2[0], lab2[-1], lab2[:, 0], lab2[:, -1]])) - {0}
    m = m & ~np.isin(lab2, list(externos))
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m)
    m = (lab_ == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    # a caixa é um bloco (silhueta convexa): o casco convexo devolve as partes laranja que pareciam sombra
    pts = cv2.findNonZero(m)
    full = np.zeros_like(m)
    cv2.fillConvexPoly(full, cv2.convexHull(pts), 255)
    full = cv2.GaussianBlur(cv2.erode(full, np.ones((3, 3), np.uint8)), (3, 3), 0)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB), full]), "RGBA")
    rgba.crop(rgba.getbbox()).save(os.path.join(P, os.path.basename(path)[:-4] + ".png"))


if __name__ == "__main__":
    os.makedirs(P, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(F, "*.jpg"))):  # (as caixas laranja já foram descartadas)
        recorta(f)
    print("ok")
