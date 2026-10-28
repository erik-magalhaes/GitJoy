#!/usr/bin/env python3
"""Estilos "feitos à mão" para as cartas reais do Flip 7 (carta_real.camadas), como o lápis de cor do Taco Gato:
  papel(c)  PAPEL RECORTADO: cada camada vira um pedaço de papel colorido com fibra, borda um pouco irregular e sombrinha
            (colagem / stop motion de papel);
  giz(c)    GIZ NA LOUSA: a carta desenhada em giz colorido (traço granulado, falhado), a base só no contorno;
  neon(c)   NEON: a arte de linha da carta (moldura, número vazado, faixa, leque) vira tubo de neon aceso.
A semente muda o "tremido" (boil): trocar a cada 2 quadros dá a animação feita à mão.
"""
import cv2
import numpy as np
from PIL import Image, ImageFilter

from carta_real import CW, CH, camadas  # noqa: F401

LINHAS = {"fita", "arco", "num_fora", "num_dentro", "faixa", "dobra"}


def _borda_irregular(m, rng, amp=3):
    """Borda de papel recortado à tesoura: ruído suave empurrando a borda para dentro/fora."""
    ruido = cv2.GaussianBlur(rng.normal(0, 1, m.shape).astype(np.float32), (0, 0), 6)
    d = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 3) - cv2.distanceTransform((~m).astype(np.uint8),
                                                                                         cv2.DIST_L2, 3)
    return d + ruido / (np.abs(ruido).max() + 1e-6) * amp > 0


def papel(cs, esc=0.5, semente=0):
    rng = np.random.default_rng(semente)
    fibra = cv2.GaussianBlur(rng.normal(0, 1, (CH, CW)).astype(np.float32), (0, 0), 1.2)
    fibra = 1 + 0.06 * fibra / (np.abs(fibra).max() + 1e-6)
    fios = cv2.GaussianBlur((rng.random((CH, CW)) < 0.004).astype(np.float32), (0, 0), 0.8) * 0.5
    out = np.zeros((CH + 30, CW + 30, 4), np.float64)
    for nome, m, cor in cs:
        if nome in ("num_listra", "arco_txt", "nome") or m.sum() < 30:
            mm = m
        else:
            mm = _borda_irregular(m, rng, 2.5 if nome != "fundo" else 4)
        # sombra do pedaço de papel (deslocada e suave) por baixo
        sh = cv2.GaussianBlur(mm.astype(np.float32), (0, 0), 3 if nome != "fundo" else 8)
        dx, dy = (4, 5) if nome != "fundo" else (12, 16)
        alfa_sh = sh * (0.35 if nome != "fundo" else 0.45)
        reg = out[dy:dy + CH, dx:dx + CW]
        reg[..., :3] *= (1 - alfa_sh[..., None])
        reg[..., 3] = np.maximum(reg[..., 3], alfa_sh * 255)
        c = np.array(cor, float)[None, None, :] * fibra[..., None]
        c = np.clip(c + fios[..., None] * 60, 0, 255)
        alvo = out[:CH, :CW]
        alvo[mm, :3] = c[mm]
        alvo[mm, 3] = 255
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    return im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)


def _giz_textura(shape, rng, ang=25):
    r = rng.random(shape).astype(np.float32)
    k = np.zeros((9, 9), np.float32)
    k[4, :] = 1
    M = cv2.getRotationMatrix2D((4, 4), ang, 1)
    k = cv2.warpAffine(k, M, (9, 9))
    r = cv2.filter2D(r, -1, k / k.sum())
    return r


def giz(cs, esc=0.5, semente=0):
    rng = np.random.default_rng(semente)
    tex = _giz_textura((CH, CW), rng)
    out = np.zeros((CH, CW, 4), np.float64)
    for nome, m, cor in cs:
        if nome == "fundo":  # a base da carta: só o contorno em giz branco + um véu clarinho
            borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
            out[m, :3] = (70, 86, 80)
            out[m, 3] = 90
            m, cor = borda, (236, 236, 228)
        if nome == "faixa_fundo":
            continue
        cor = np.array(cor, float)
        cor = cor * 0.65 + 255 * 0.35  # giz é pastel
        falha = tex > (0.36 if nome in LINHAS or nome in ("nome", "arco_txt", "num_listra") else 0.46)
        mm = m & falha
        out[mm, :3] = cor
        out[mm, 3] = np.maximum(out[mm, 3], 235)
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(0.7))
    return im.resize((int(CW * esc), int(CH * esc)), Image.LANCZOS)


def neon(cs, esc=0.5, semente=0):
    rng = np.random.default_rng(semente)
    out = np.zeros((CH + 80, CW + 80, 4), np.float64)
    pisca = 0.92 + 0.08 * rng.random()
    for nome, m, cor in cs:
        if nome in ("faixa_fundo", "dobra"):
            continue
        if nome == "fundo":  # a carta: só o contorno em tubo branco frio
            m = m & ~cv2.erode(m.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool)
            cor = (200, 230, 255)
        elif nome in ("leque", "num_listra", "num_miolo"):  # áreas cheias viram só o contorno
            m = m & ~cv2.erode(m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        if nome == "num_miolo":
            continue
        mm = np.zeros((CH + 80, CW + 80), np.float32)
        mm[40:40 + CH, 40:40 + CW] = m
        cor = np.array(cor, float)
        cor = np.clip(cor * 1.15 + 30, 0, 255)
        for sig, a in ((18, 0.45), (6, 0.8)):
            g = cv2.GaussianBlur(mm, (0, 0), sig) * a * 2.2 * pisca
            out[..., :3] = out[..., :3] + g[..., None] * cor * (1 - out[..., 3:4] / 255 * 0.3)
            out[..., 3] = np.maximum(out[..., 3], np.clip(g * 255, 0, 255))
        nuc = mm > 0.5
        out[nuc, :3] = cor * 0.35 + 255 * 0.65
        out[nuc, 3] = 255
    out[..., :3] = np.minimum(out[..., :3], 255)
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    return im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
