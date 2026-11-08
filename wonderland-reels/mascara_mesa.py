#!/usr/bin/env python3
"""Máscara do vídeo deles na mesa (brutos/mesa.mp4): separa o TABULEIRO + peças do fundo da sala (parede, cadeiras,
sacola). Borda do tabuleiro = reta (RANSAC) nos pontos onde, de cima pra baixo, a "sala" (claro e pouco saturado)
acaba; tudo acima da reta é fundo, menos as peças em pé (standees, meeples, castelos) que o isnet (rembg) acha e que
são coloridas e encostam na borda. A reta é suavizada no tempo.

    /usr/bin/python3 mascara_mesa.py [--teste 30 180 ...]   → out/mask_mesa/NNNN.png (360x640)
"""
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "out", "frames_mesa")
DST = os.path.join(ROOT, "out", "mask_mesa")
OBJ = os.path.join(ROOT, "out", "obj_mesa")  # só as peças em pé (isnet), para o HUD mirar nelas
_S = None


def isnet(f):
    global _S
    from rembg import new_session, remove
    from PIL import Image
    if _S is None:
        _S = new_session("isnet-general-use")
    m = remove(Image.fromarray(f[..., ::-1]), session=_S, only_mask=True)
    return np.asarray(m) > 110


def pontos(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(float)
    Hh, S, V = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    sala = ((V > 0.5) & (S < 0.35)) | ((V > 0.3) & (S < 0.2)) | ((Hh > 70) & (Hh < 100) & (V > 0.35))  # parede/cadeira | sacola verde-água
    nao = ~sala
    run = ndimage.uniform_filter1d(nao.astype(float), 14, axis=0, origin=-6) > 0.95
    h, w = S.shape
    b = np.where(run.any(0), run.argmax(0), h).astype(float)
    return b, S, Hh


def reta(b, h, ant=None, baixa=False):
    w = len(b)
    xs = np.arange(w)
    ok = b < h - 5
    if ok.sum() < w * 0.25:
        return (0.0, 0.0) if ant is None else ant
    if (b[ok] < 4).mean() > 0.7:          # vista de cima: sem sala
        return (0.0, 0.0)
    rng = np.random.default_rng(0)
    best, bi = None, -1
    X, Y = xs[ok], b[ok]
    for _ in range(300):
        i, j = rng.choice(len(X), 2, replace=False)
        if X[i] == X[j]:
            continue
        a = (Y[j] - Y[i]) / (X[j] - X[i])
        if abs(a) > 1.2:
            continue
        c = Y[i] - a * X[i]
        r = np.abs(Y - (a * X + c))
        acima = ((a * X + c) - Y) > 6
        inl = (r < 6).sum() + 0.15 * (acima.sum() if baixa else (~acima & (r >= 6)).sum())
        if inl > bi:
            bi, best = inl, (a, c)
    a, c = best
    inl = np.abs(Y - (a * X + c)) < 6
    a, c = np.polyfit(X[inl], Y[inl], 1)
    return (a, c)


def mascara(f, ab, objs):
    h, w = f.shape[:2]
    a, c = ab
    yy, xx = np.mgrid[:h, :w]
    linha = a * xx + c
    m = yy >= linha - 2
    if objs is not None:
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(float)
        S, Hh = hsv[..., 1] / 255, hsv[..., 0]
        lab, n = ndimage.label(objs & ~m)
        for k in range(1, n + 1):
            p = lab == k
            if p.sum() < 25:
                continue
            ys = np.where(p)[0]
            xs = np.where(p)[1]
            enc = ((a * xs + c) - ys).min() < 8
            caixa = (xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)
            col = p.sum() / caixa > 0.4 and ((Hh[p] > 70) & (Hh[p] < 100)).mean() < 0.5  # cadeira = vazada; sacola = verde-água
            if enc and col:
                m |= ndimage.binary_dilation(p, iterations=1)
    m = ndimage.binary_closing(m, iterations=2)
    return m


def main():
    os.makedirs(DST, exist_ok=True)
    os.makedirs(OBJ, exist_ok=True)
    nomes = sorted(os.listdir(SRC))
    teste = [int(x) for x in sys.argv[sys.argv.index("--teste") + 1:]] if "--teste" in sys.argv else None
    ant = None
    lista = teste or range(1, len(nomes) + 1)
    vis = []
    for n in lista:
        f = cv2.imread(os.path.join(SRC, "%04d.jpg" % n))
        h = f.shape[0]
        b, _, _ = pontos(f)
        objs = isnet(f)
        bi = np.clip(b.astype(int), 0, h - 1)
        sobre = ndimage.binary_dilation(objs, iterations=4)[bi, np.arange(len(b))]
        b = np.where(sobre, h, b)              # ponto da borda em cima de peça em pé não conta
        ab = reta(b, h, ant, baixa=540 <= n <= 700)  # trilha de pontos: cadeira atrás, a borda é a reta de BAIXO
        if ant is not None and not teste and ab != (0.0, 0.0) and ant != (0.0, 0.0):
            ab = (0.6 * ab[0] + 0.4 * ant[0], 0.6 * ab[1] + 0.4 * ant[1])
        ant = ab
        m = mascara(f, ab, objs if ab != (0.0, 0.0) else None)
        cv2.imwrite(os.path.join(DST, "%04d.png" % n), (m * 255).astype(np.uint8))
        cv2.imwrite(os.path.join(OBJ, "%04d.png" % n), (objs * 255).astype(np.uint8))
        if teste:
            g = f.copy()
            g[~m] = (0, 255, 0)
            vis.append(np.hstack([f, g]))
        elif n % 50 == 0:
            print(n, flush=True)
    if teste:
        cv2.imwrite(os.path.join(ROOT, "out", "teste_mask.jpg"), np.vstack([np.hstack(vis[i:i + 4]) for i in range(0, len(vis), 4)]))


if __name__ == "__main__":
    main()
