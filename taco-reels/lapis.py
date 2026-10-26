#!/usr/bin/env python3
"""Estilo "desenho de lápis de cor" (referência que ele mandou em 26/out/2026: elefante e gato rabiscados em papel creme,
contorno preto tremido em várias passadas, cor em hachura de lápis com o papel aparecendo, nomes escritos à mão com setinha).
lapis(img, w, semente): redesenha uma arte OFICIAL nesse estilo, na largura w de saída.
  - contorno: os traços escuros da arte (marrom) viram 2 passadas de linha preta tremida (contornos do cv2 com ruído suave);
  - cor: base clarinha (a cor da arte misturada com o papel) + milhares de riscos curtos na diagonal com a cor da arte variando;
  - a semente muda os riscos: trocar de semente a cada 3 quadros dá o "tremido de desenho animado" (boil).
"""
import math
import os
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
PAPEL = (250, 246, 236)
GRAFITE = (34, 28, 26)


@lru_cache(None)
def fonte(nome, s):
    return ImageFont.truetype(os.path.join(ASSETS, "fonts", nome), int(s))


def _ruido(n, amp, rng, suave=9):
    """Deslocamento suave ao longo do contorno (a mão tremendo, sem serrilhar)."""
    r = rng.normal(0, 1, n + suave * 2)
    k = np.hanning(suave * 2 + 1)
    r = np.convolve(r, k / k.sum(), "same")[suave:suave + n]
    return r / (np.abs(r).max() + 1e-9) * amp


def rabisco(d, pts, rng, cor=GRAFITE, larg=3, amp=2.2, passadas=2, fechado=True):
    """Desenha uma linha (lista de pontos) como traço de lápis: várias passadas tremidas, um pouco desencontradas."""
    pts = np.asarray(pts, np.float64)
    if len(pts) < 3:
        return
    for _ in range(passadas):
        n = len(pts)
        nx, ny = _ruido(n, amp, rng), _ruido(n, amp, rng)
        q = pts + np.stack([nx, ny], 1) + rng.normal(0, amp * 0.35, 2)
        q = [tuple(p) for p in q]
        if fechado:
            q.append(q[0])
        d.line(q, fill=cor, width=larg, joint="curve")


def contornos(mask, passo=4, minimo=18):
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        c = c[:, 0, :].astype(np.float64)
        if len(c) < minimo:
            continue
        out.append(c[::passo])
    return out


def hachura(base, mask, cor_img, rng, dens=1.0, ang=58.0, comp=(12, 30), larg=3, alfa=205, cruzada=0.25, sombra=0.0):
    """Riscos curtos de lápis dentro da máscara, cada um com a cor da arte naquele ponto (variando um pouco)."""
    h, w = mask.shape
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return
    n = int(len(xs) / 70 * dens)
    idx = rng.integers(0, len(xs), n)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in idx:
        x, y = xs[k], ys[k]
        c = cor_img[y, x].astype(np.float64)
        v = rng.normal(0, 14) - sombra * 30
        c = np.clip(c + v, 0, 255).astype(int)
        a = math.radians(ang + rng.normal(0, 7) + (90 if rng.random() < cruzada else 0))
        L = rng.uniform(*comp)
        dx, dy = math.cos(a) * L / 2, math.sin(a) * L / 2
        d.line((x - dx, y - dy, x + dx, y + dy), fill=tuple(c) + (alfa,), width=larg)
    m = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
    base.alpha_composite(lay)


def forma_cheia(a):
    """Máscara da forma inteira (preenche buracos: o texto impresso das cartas é recortado/transparente)."""
    cs, _ = cv2.findContours(a.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    m = np.zeros(a.shape, np.uint8)
    cv2.drawContours(m, cs, -1, 1, -1)
    return m.astype(bool)


def satura(rgb, k=1.35, escurece=0.92):
    g = rgb.mean(2, keepdims=True)
    return np.clip((g + (rgb - g) * k) * escurece, 0, 255)


def texto_impresso(escuro, h):
    """O nome impresso das cartas (alto à esquerda e embaixo de cabeça para baixo): pedaços escuros PEQUENOS nas faixas
    de 9–21% e 79–91% da altura. Pedaço grande (pé do gato, por exemplo) fica."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(escuro.astype(np.uint8))
    out = np.zeros_like(escuro)
    for i in range(1, n):
        x, y, ww, hh, area = st[i]
        y0, y1 = y / h, (y + hh) / h
        if hh < 0.075 * h and ((y0 > 0.08 and y1 < 0.22) or (y0 > 0.78 and y1 < 0.92)):
            out |= lab == i
    return out


def lapis(img, w, semente=0, linha_lim=100, dens=1.0, cheia=True, tira_texto=False):
    """img: RGBA/RGB da arte oficial. Linha = os traços pretos da arte (lum < 100; o marrom do gorila é cor)."""
    rng = np.random.default_rng(semente)
    im = img.convert("RGBA")
    h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float64)
    rgb, a = arr[..., :3], arr[..., 3] > 128
    forma = forma_cheia(a) if cheia else a
    buraco = forma & ~a
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    escuro = (lum < linha_lim) & a
    txt = texto_impresso(escuro, h) if tira_texto else np.zeros_like(escuro)
    txt = cv2.dilate(txt.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    linha = escuro & ~txt
    m8 = ((linha | buraco | txt) * 255).astype(np.uint8)
    cor = cv2.inpaint(rgb.astype(np.uint8), m8, 9, cv2.INPAINT_TELEA).astype(np.float64)
    cor = satura(cor)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    clara = cor * 0.30 + np.array(PAPEL) * 0.70  # o lápis não cobre tudo: o papel aparece
    out.alpha_composite(Image.fromarray(np.dstack([clara, forma * 255.0]).astype(np.uint8), "RGBA"))
    esc = max(1.0, w / 460)
    hachura(out, forma, cor, rng, dens=dens * 0.55, comp=(18 * esc, 44 * esc), larg=max(2, int(3 * esc)), alfa=215,
            cruzada=0.12)
    hachura(out, forma, cor, rng, dens=dens * 0.25, ang=-28, comp=(10 * esc, 26 * esc), larg=max(2, int(2 * esc)),
            alfa=160, cruzada=0)
    # linhas: a linha da arte bem suave + 3 passadas de grafite tremido por cima (cara de traço à mão)
    lm = cv2.GaussianBlur(linha.astype(np.float32), (0, 0), 1.0) > 0.45
    lay = np.zeros((h, w, 4), np.uint8)
    lay[lm] = GRAFITE + (215,)
    out.alpha_composite(Image.fromarray(lay, "RGBA"))
    d = ImageDraw.Draw(out)
    larg = max(2, int(round(w / 300)))
    for c in contornos(lm):
        rabisco(d, c, rng, larg=larg, amp=2.0 * esc, passadas=3)
    return out


def desenho(img, w, semente=0, linha_lim=100):
    """Qualquer arte (emoji, ilustração) em lápis, com o contorno de fora rabiscado (emoji não tem linha preta)."""
    out = lapis(img, w, semente, linha_lim=linha_lim, cheia=False)
    a = np.asarray(out.getchannel("A")) > 128
    d = ImageDraw.Draw(out)
    rng = np.random.default_rng(semente + 7)
    for c in contornos(a, passo=4, minimo=30):
        rabisco(d, c, rng, larg=max(2, w // 160), amp=1.8 * w / 400, passadas=3)
    return out


def carta(nome_png, w, titulo, semente=0, cor_tit=GRAFITE):
    """Uma carta oficial do jogo em lápis: arte sem o texto impresso, borda rabiscada e o nome escrito à mão."""
    img = Image.open(os.path.join(ASSETS, "cartas", nome_png)).convert("RGBA")
    out = lapis(img, w, semente, tira_texto=True)
    rng = np.random.default_rng(semente + 99)
    d = ImageDraw.Draw(out)
    a = np.asarray(out.getchannel("A")) > 128
    for c in contornos(a, passo=5, minimo=50)[:1]:
        rabisco(d, c, rng, larg=max(3, w // 130), amp=2.2 * w / 500, passadas=3)
    f = fonte("Kalam-Bold.ttf", w * 0.115)
    d.text((w * 0.08, w * 0.055), titulo, font=f, fill=cor_tit)
    tx = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(tx).text((w * 0.08, w * 0.055), titulo, font=f, fill=cor_tit)
    out.alpha_composite(tx.rotate(180))
    return out


if __name__ == "__main__":
    import sys
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    carta(sys.argv[1], w, os.path.splitext(sys.argv[1])[0].upper()).save("/tmp/lapis_teste.png")
