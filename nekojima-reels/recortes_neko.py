#!/usr/bin/env python3
"""Recorta as peças do Nekojima das fotos oficiais em fundo branco (para animar soltas, em vez de foto parada).

    python3 recortes_neko.py      # gera assets/pecas/*.png
"""
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ROOT, "assets", "fotos")
P = os.path.join(ROOT, "assets", "pecas")


def grabcut_white(img, box, thr=28, iters=6, keep=1, extra_fg=None):
    """Peça sobre fundo branco: semente pela diferença do branco + GrabCut para refinar a borda."""
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].copy()
    bg = np.median(np.concatenate([c[:6].reshape(-1, 3), c[:, :6].reshape(-1, 3), c[:, -6:].reshape(-1, 3)]), 0)
    diff = np.abs(c.astype(np.int16) - bg).max(2)
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    fg = (diff > thr) | (hsv[..., 1] > 60)
    mask = np.where(fg, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
    mask[cv2.erode(fg.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = cv2.GC_FGD
    mask[diff < thr * 0.35] = cv2.GC_BGD
    if extra_fg is not None:
        mask[extra_fg[y0:y1, x0:x1] > 0] = cv2.GC_FGD
    bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(c, mask, None, bgm, fgm, iters, cv2.GC_INIT_WITH_MASK)
    m = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    order = np.argsort(-st[1:, 4])[:keep] + 1
    m = np.isin(lab, order).astype(np.uint8) * 255
    m = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (3, 3), 0)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(c, cv2.COLOR_BGR2RGB), m]), "RGBA")
    return rgba.crop(rgba.getbbox())


def dark_cut(img, box, thr=95):
    """Gatinho preto: tudo que é escuro e conectado vira a peça."""
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].copy()
    g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
    m = (g < thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, 4]))
    m = (lab == k).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    full = np.zeros_like(m)
    cv2.drawContours(full, cs, -1, 255, -1)
    full = cv2.GaussianBlur(cv2.dilate(full, np.ones((3, 3), np.uint8)), (3, 3), 0)
    rgba = Image.fromarray(np.dstack([cv2.cvtColor(c, cv2.COLOR_BGR2RGB), full]), "RGBA")
    return rgba.crop(rgba.getbbox())


def sem_fio(rgba):
    """Apaga o pedacinho de fio azul que ficou grudado embaixo, à esquerda do gato."""
    a = np.asarray(rgba).copy()
    h, w = a.shape[:2]
    reg = a[int(h * 0.78):, :int(w * 0.6)]
    hsv = cv2.cvtColor(np.ascontiguousarray(reg[..., :3]), cv2.COLOR_RGB2HSV)
    # no canto: só fica o que é bem escuro e sem o azul-esverdeado do fio
    fio = ((hsv[..., 0] > 60) & (hsv[..., 0] < 105) & (hsv[..., 1] > 50)) | (hsv[..., 2] > 85)
    fio = cv2.dilate(fio.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    reg[fio, 3] = 0
    m = (a[..., 3] > 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    a[lab != 1 + int(np.argmax(st[1:, 4])), 3] = 0
    al = cv2.morphologyEx(a[..., 3], cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    a[..., 3] = cv2.GaussianBlur(cv2.medianBlur(al, 5), (3, 3), 0)
    im = Image.fromarray(a, "RGBA")
    return im.crop(im.getbbox())


def face(img, c, r, out, size=200, squash=1.0):
    """Face redonda do dado (corrige a elipse da perspectiva esticando para círculo)."""
    x, y = c
    ry = int(r * squash)
    crop = img[y - ry:y + ry, x - r:x + r]
    crop = cv2.resize(crop, (size, size), interpolation=cv2.INTER_CUBIC)
    m = np.zeros((size, size), np.uint8)
    cv2.circle(m, (size // 2, size // 2), size // 2 - 4, 255, -1, lineType=cv2.LINE_AA)
    Image.fromarray(np.dstack([cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), m]), "RGBA").save(os.path.join(P, out))


def main():
    os.makedirs(P, exist_ok=True)
    cai = cv2.imread(os.path.join(F, "caindo.jpg"))
    sem_fio(dark_cut(cai, (2400, 2300, 2760, 2800))).save(os.path.join(P, "gato.png"))
    grabcut_white(cai, (3040, 1220, 3440, 1660)).save(os.path.join(P, "poste_rosa.png"))
    # textura de madeira para o corpo dos dados (um trecho liso de poste)
    wood = cai[1700:1900, 1500:1560]
    cv2.imwrite(os.path.join(P, "madeira.png"), cv2.resize(wood, (240, 240), interpolation=cv2.INTER_CUBIC))
    t2 = cv2.imread(os.path.join(F, "torre2.jpg"))
    grabcut_white(t2, (300, 20, 840, 905), thr=22).save(os.path.join(P, "torre.png"))
    dd = cv2.imread(os.path.join(F, "dados.jpg"))
    grabcut_white(dd, (540, 200, 1000, 580), thr=25).save(os.path.join(P, "nivel.png"))
    face(dd, (190, 565), 32, "face_arcoiris.png")
    face(dd, (361, 551), 32, "face_torii.png")
    face(dd, (388, 607), 30, "face_adaga.png", squash=0.75)
    print("ok", sorted(os.listdir(P)))


if __name__ == "__main__":
    main()
