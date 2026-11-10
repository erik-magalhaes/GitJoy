#!/usr/bin/env python3
"""Tikal, visual C "CADERNO DO ARQUEÓLOGO" (10/nov/2026, pedido dele depois da prévia B). MESMO roteiro e mesma
linha do tempo do tikal.py (a narração serve para os dois), outra cara: o diário de campo de uma expedição. Página de
caderno pautada com margem vermelha e espiral, cada fala = uma página nova que vira; as peças OFICIAIS entram como fotos
presas com fita (hexágonos do manual, capa) e adesivos recortados (exploradores, tesouros); as anotações se escrevem à
mão em caneta azul (Patrick Hand / Kalam), a caneta vermelha circula e puxa setas, post-its com o custo em PA e carimbos.

    /usr/bin/python3 caderno.py --frame 2 8 15 ...   # out/frames_caderno.jpg
    /usr/bin/python3 caderno.py                      # out/caderno_previa_final.mp4 (sem voz, legenda do roteiro)
"""
import argparse
import math
import os
import random
import sys
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import pecas as P
import tikal as T
from pecas import W, H, fonte, cola
from tikal import E, S, FPS, encode, final_loudness, ease, out_back, seg, surge

OUT = T.OUT
AZUL_C, VERM_C, GRAFITE = (28, 48, 128), (196, 30, 40), (70, 70, 74)
LINHA0, PASSO = 250, 64


# ------------------------------------------------------------------------------------------------ papel
@lru_cache(None)
def mesa():
    rnd = np.random.default_rng(5)
    n = cv2.resize(rnd.normal(0, 1, (H // 6, W // 40)), (W, H), interpolation=cv2.INTER_CUBIC)
    v = cv2.GaussianBlur(rnd.normal(0, 1, (H, W)), (0, 0), 2)
    base = np.array([92, 58, 34], float)[None, None] * (1 + 0.12 * n[..., None] + 0.04 * v[..., None])
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")


@lru_cache(None)
def pagina(k):
    """Folha de caderno: papel creme com fibras, pauta azul-clara, margem vermelha, furos da espiral, nº da página."""
    rnd = np.random.default_rng(10 + k)
    n = cv2.resize(rnd.normal(0, 1, (H // 10, W // 10)), (W, H), interpolation=cv2.INTER_CUBIC)
    f = cv2.GaussianBlur(rnd.normal(0, 1, (H, W)), (0, 0), 0.8)
    a = np.array([245, 239, 222], float)[None, None] * (1 + 0.025 * n[..., None] + 0.012 * f[..., None])
    yy, xx = np.mgrid[0:H, 0:W]
    a *= (1 - 0.10 * ((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2))[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for y in range(LINHA0, H - 40, PASSO):
        d.line((0, y, W, y), fill=(160, 186, 214, 255), width=2)
    d.line((132, 0, 132, H), fill=(222, 120, 120, 255), width=3)
    d.line((138, 0, 138, H), fill=(222, 120, 120, 180), width=1)
    for y in range(120, H, 150):
        d.ellipse((34, y - 17, 68, y + 17), fill=(92, 58, 34, 255))
        d.ellipse((38, y - 13, 64, y + 13), fill=(70, 44, 26, 255))
    d.text((W - 70, H - 70), str(k + 1), font=fonte("PatrickHand-Regular.ttf", 44), fill=(150, 150, 160), anchor="mm")
    return img


# ------------------------------------------------------------------------------------------------ escrita à mão
@lru_cache(None)
def _texto_img(txt, s, cor, fnome):
    f = fonte(fnome, s)
    linhas = txt.split("\n")
    larg = [int(math.ceil(f.getlength(li))) + 8 for li in linhas]
    alt = int(s * 1.22)
    im = Image.new("RGBA", (max(larg) + 10, alt * len(linhas) + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, li in enumerate(linhas):
        d.text((4, 6 + i * alt), li, font=f, fill=cor + (255,))
    return im, larg, alt


def escreve(img, txt, x, y, s, u, cor=AZUL_C, fnome="PatrickHand-Regular.ttf", centro=False, rot=0.0):
    """Texto que se escreve da esquerda para a direita, linha por linha (u de 0 a 1)."""
    if u <= 0:
        return
    im, larg, alt = _texto_img(txt, s, cor, fnome)
    tot = sum(larg)
    q = u * tot
    m = Image.new("L", im.size, 0)
    dm = ImageDraw.Draw(m)
    acc = 0
    for i, w in enumerate(larg):
        vis = max(0, min(w, q - acc))
        if vis > 0:
            dm.rectangle((0, i * alt, 4 + vis, (i + 1) * alt + 14), fill=255)
        acc += w
    sp = im.copy()
    sp.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m))))
    if rot:
        sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    px = x - (sp.width / 2 if centro else 0)
    img.alpha_composite(sp, (int(px), int(y - sp.height / 2)))


def tempo_escrita(txt, cps=26):
    return max(0.35, len(txt.replace("\n", "")) / cps)


def caneta(img, pts, u, cor=VERM_C, w=7):
    """Desenha uma polilinha até a fração u (traço de caneta)."""
    if u <= 0 or len(pts) < 2:
        return
    seglen = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(seglen)
    alvo = u * tot
    out = [pts[0]]
    acc = 0
    for i, L in enumerate(seglen):
        if acc + L >= alvo:
            r = (alvo - acc) / L if L else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r))
            break
        out.append(pts[i + 1])
        acc += L
    d = ImageDraw.Draw(img)
    d.line(out, fill=cor + (235,), width=w, joint="curve")


def circulo(cx, cy, rx, ry, semente=1, voltas=1.15):
    rnd = random.Random(semente)
    pts = []
    n = 70
    a0 = rnd.uniform(0, 6.28)
    for i in range(n + 1):
        a = a0 + voltas * 2 * math.pi * i / n
        k = 1 + 0.05 * math.sin(i * 0.4 + semente) + 0.03 * (i / n)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


def seta(img, p0, p1, u, cor=VERM_C, curva=0.25, w=7):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    nx, ny = -(p1[1] - p0[1]) * curva, (p1[0] - p0[0]) * curva
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * (mx + nx) + t * t * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * (my + ny) + t * t * p1[1]) for t in np.linspace(0, 1, 30)]
    caneta(img, pts, min(1, u / 0.85), cor, w)
    if u > 0.85:
        a = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
        k = min(1, (u - 0.85) / 0.15)
        for da in (2.6, -2.6):
            q = (p1[0] + 34 * k * math.cos(a + da), p1[1] + 34 * k * math.sin(a + da))
            ImageDraw.Draw(img).line((p1, q), fill=cor + (235,), width=w)


def sublinha(img, x0, x1, y, u, cor=VERM_C):
    pts = [(x0 + (x1 - x0) * t, y + 4 * math.sin(t * 9)) for t in np.linspace(0, 1, 20)]
    caneta(img, pts, u, cor, 6)


# ------------------------------------------------------------------------------------------------ fotos, adesivos, post-its
@lru_cache(None)
def foto(chave, w, h=None):
    """Foto de câmera instantânea: moldura branca com rodapé largo; a imagem entra inteira (nunca cortada)."""
    if chave == "capa":
        c = P.capa()
        y0, y1 = int(c.height * 0.24), int(c.height * 0.80)
        larg = int((y1 - y0) * w / (h or w))
        x0 = int(c.width * 0.62 - larg / 2)
        sp = c.crop((x0, y0, x0 + larg, y1)).convert("RGBA")
    elif chave == "caixa":
        sp = P.img("caixa.png")
    else:
        sp = P.img(f"hex_{chave}.png")
    h = h or w
    mold = Image.new("RGBA", (w + 40, h + 110), (252, 251, 246, 255))
    s = sp.copy()
    s.thumbnail((w, h), Image.LANCZOS)
    fundo = (236, 232, 220, 255) if chave not in ("capa",) else (0, 0, 0, 255)
    area = Image.new("RGBA", (w, h), fundo)
    area.alpha_composite(s, ((w - s.width) // 2, (h - s.height) // 2))
    mold.alpha_composite(area, (20, 20))
    d = ImageDraw.Draw(mold)
    d.rectangle((0, 0, mold.width - 1, mold.height - 1), outline=(214, 210, 200, 255), width=2)
    return mold


@lru_cache(None)
def fita(w=170, semente=0):
    rnd = random.Random(semente)
    im = Image.new("RGBA", (w, 56), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0, 4), (w, 0), (w - 6, 56), (4, 52)]
    d.polygon(pts, fill=(234, 220, 168, 190))
    for x in range(0, w, 7):  # serrilhado nas pontas
        d.polygon([(x, 0), (x + 3, 6), (x + 7, 0)], fill=(0, 0, 0, 0)) if rnd.random() < 0 else None
    return im


@lru_cache(None)
def adesivo(chave, h):
    """Peça recortada como adesivo (borda branca + sombra) — explorador tingido ou ficha de tesouro."""
    tipo, arg = chave.split(":")
    if tipo == "meeple":
        sp = P.meeple(arg, h)
    elif tipo == "tesouro":
        sp = P.tesouro(int(arg), h)
    elif tipo == "logo":
        sp = P.img("logo_tikal.png")
        sp = sp.resize((h * sp.width // sp.height, h), Image.LANCZOS)
    else:
        sp = P.img(arg)
    pad = 14
    a = np.asarray(sp.getchannel("A"))
    a = np.pad(a, pad)
    borda = cv2.dilate((a > 30).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)))
    borda = cv2.GaussianBlur(borda, (3, 3), 0)
    out = Image.new("RGBA", (sp.width + 2 * pad, sp.height + 2 * pad), (255, 255, 255, 0))
    branco = Image.new("RGBA", out.size, (255, 255, 255, 255))
    branco.putalpha(Image.fromarray(borda))
    out.alpha_composite(branco)
    out.alpha_composite(sp, (pad, pad))
    return out


@lru_cache(None)
def postit(txt, s=50, cor=(255, 226, 92), w=330):
    im = Image.new("RGBA", (w, w), cor + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, 34), fill=tuple(max(0, c - 22) for c in cor) + (255,))
    f = fonte("Kalam-Bold.ttf", s)
    linhas = txt.split("\n")
    for i, li in enumerate(linhas):
        d.text((w / 2, 40 + (w - 40) / 2 + (i - (len(linhas) - 1) / 2) * s * 1.15), li, font=f, fill=(40, 40, 60),
               anchor="mm")
    sh = Image.new("RGBA", (w + 30, w + 30), (0, 0, 0, 0))
    m = Image.new("L", (w, w), 90)
    sh.paste((0, 0, 0, 90), (14, 18), m)
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh.alpha_composite(im, (0, 0))
    return sh


@lru_cache(None)
def carimbo(txt, s=96, cor=VERM_C):
    f = fonte("Anton-Regular.ttf", s)
    larg = int(f.getlength(txt)) + 70
    alt = int(s * 1.35) + 30
    im = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, larg - 7, alt - 7), 20, outline=cor + (255,), width=10)
    d.text((larg / 2, alt / 2 + 3), txt, font=f, fill=cor + (255,), anchor="mm")
    a = np.asarray(im.getchannel("A")).astype(float)
    rnd = np.random.default_rng(len(txt))
    falha = cv2.GaussianBlur(rnd.random(a.shape), (0, 0), 2.5)
    a *= np.clip((falha - 0.25) * 3, 0.35, 1) * 0.88
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def poe(img, sp, x, y, rot, u, t0, d=0.3, queda=True, sombra=8):
    """Peça que cai na página (escala 1,25 → 1 com giro assentando)."""
    if u < t0:
        return
    q = min(1.0, (u - t0) / d)
    e = 1 + (0.25 * (1 - ease(q)) if queda else 0)
    cola(img, sp, x, y, rot + 6 * (1 - ease(q)), e, min(1, q * 2.5), sombra=sombra)


def poe_foto(img, chave, x, y, rot, u, t0, w, h=None, semente=0):
    poe(img, foto(chave, w, h), x, y, rot, u, t0, sombra=12)
    if u >= t0 + 0.2:
        fh = (h or w) + 110
        dy = -fh / 2 + 8
        cx = x - dy * math.sin(math.radians(rot))
        cy = y + dy * math.cos(math.radians(rot))
        cola(img, fita(170, semente), cx, cy, rot + 4 - 8 * (semente % 2), 1, min(1, (u - t0 - 0.2) / 0.1))


def bate(img, sp, x, y, rot, u, t0):
    """Carimbo: entra grande e bate na página."""
    if u < t0:
        return
    q = min(1.0, (u - t0) / 0.18)
    cola(img, sp, x, y, rot, 1 + 0.7 * (1 - q), min(1, q * 1.5))


# ------------------------------------------------------------------------------------------------ páginas (cenas)
def titulo_pagina(img, txt, u, t0=0.05):
    escreve(img, txt, 170, 182, 64, seg(u, t0, t0 + tempo_escrita(txt, 30)), AZUL_C, "Kalam-Bold.ttf")


def pg_gancho(img, t, u, dur):
    escreve(img, "Diário da expedição", 170, 182, 62, seg(u, 0.0, 0.6), AZUL_C, "Kalam-Bold.ttf")
    poe_foto(img, "capa", 590, 560, 3, u, 0.15, 560, 440, 1)
    tx = "Você entraria na selva\natrás de templos perdidos?"
    escreve(img, tx, 175, 1000, 66, seg(u, 0.3, 0.3 + tempo_escrita(tx, 40)), AZUL_C, "Kalam-Bold.ttf")
    k = dur * 0.52
    poe(img, adesivo("logo:x", 190), 560, 1270, -4, u, k, 0.3)
    caneta(img, circulo(560, 1270, 320, 140, 3), seg(u, k + 0.4, k + 1.0))
    tx2 = "→ você comanda uma expedição!"
    escreve(img, tx2, 175, 1490, 58, seg(u, k + 0.7, k + 0.7 + tempo_escrita(tx2)), VERM_C)


HEX4 = [("templo", "TEMPLO", -5), ("ruina", "RUÍNA (tesouro!)", 4), ("clareira", "CLAREIRA", -3), ("vulcao", "VULCÃO!!", 5)]


def pg_hexagono(img, t, u, dur):
    titulo_pagina(img, "Dia 1: a selva cresce", u)
    tx = "Na sua vez: tira um hexágono\ne encaixa no mapa."
    escreve(img, tx, 170, 330, 52, seg(u, 0.5, 0.5 + tempo_escrita(tx, 34)))
    pos = [(330, 760), (780, 760), (330, 1250), (780, 1250)]
    t0 = 1.6
    passo = (dur - t0 - 0.8) / 4
    for k, ((ch, nome, rot), (x, y)) in enumerate(zip(HEX4, pos)):
        tk = t0 + k * passo
        poe_foto(img, ch, x, y, rot, u, tk, 340, 300, k)
        escreve(img, nome, x, y + 245, 50, seg(u, tk + 0.25, tk + 0.25 + tempo_escrita(nome)), VERM_C if k == 3 else AZUL_C,
                centro=True)
    if u > t0 + 3 * passo + 0.4:
        caneta(img, circulo(780, 1250, 230, 220, 7), seg(u, t0 + 3 * passo + 0.4, t0 + 3 * passo + 0.9))


def caixinhas(img, gastos, x0=175, y=470):
    d = ImageDraw.Draw(img)
    for k in range(10):
        x = x0 + k * 76
        d.rounded_rectangle((x, y - 26, x + 52, y + 26), 6, outline=AZUL_C + (255,), width=4)
        q = min(1.0, max(0.0, gastos - k))
        if q > 0:
            pts = [(x + 6, y - 20), (x + 46, y + 20)]
            caneta(img, pts, min(1, q * 2), VERM_C, 6)
            if q > 0.5:
                caneta(img, [(x + 46, y - 20), (x + 6, y + 20)], (q - 0.5) * 2, VERM_C, 6)


def pg_pa(img, t, u, dur):
    titulo_pagina(img, "Regra nº 1: 10 pontos de ação", u)
    escreve(img, "por turno (PA):", 175, 370, 52, seg(u, 0.6, 1.1))
    a, b = (340, 930), (770, 930)
    poe_foto(img, "clareira", a[0], a[1], -4, u, 0.5, 320, 280, 1)
    poe_foto(img, "templo", b[0], b[1], 4, u, 0.7, 320, 280, 2)
    escreve(img, "acampamento", a[0], 1150, 46, seg(u, 0.9, 1.4), AZUL_C, centro=True)
    escreve(img, "templo", b[0], 1150, 46, seg(u, 1.0, 1.4), AZUL_C, centro=True)
    t_entra, t_anda = dur * 0.30, dur * 0.52
    gasto = 0.0
    d = ImageDraw.Draw(img)
    for k in range(2):  # as 2 pedras do caminho, a lápis
        x = 530 + k * 70
        d.rounded_rectangle((x - 24, 900, x + 24, 940), 8, outline=GRAFITE + (255,), width=4,
                            fill=(255, 226, 120, 255) if (u - t_anda) > 0.6 * (k + 1) else None)
    if u >= t_entra:
        gasto = seg(u, t_entra, t_entra + 0.3)
        q = seg(u, t_anda, dur - 0.6)
        gasto += 2 * q
        x = a[0] + (b[0] - a[0]) * ease(q)
        pulo = 60 * abs(math.sin(q * math.pi * 3))
        poe(img, adesivo("meeple:vermelho", 150), x, a[1] - 40 - pulo, -6, u, t_entra, 0.3)
        poe(img, postit("colocar\n= 1 PA", 50), 300, 1400, -6, u, t_entra + 0.2)
        if u > t_anda:
            poe(img, postit("andar = 1 PA\npor pedra", 46, (150, 230, 160)), 760, 1400, 5, u, t_anda + 0.2)
            pts = [(a[0] + 40, a[1] - 160)]
            pts += [(a[0] + (b[0] - a[0]) * s_ + 40, a[1] - 160 - 70 * math.sin(s_ * math.pi)) for s_ in np.linspace(0, 1, 20)]
            for j in range(0, int(len(pts) * q), 2):
                ImageDraw.Draw(img).ellipse((pts[j][0] - 5, pts[j][1] - 5, pts[j][0] + 5, pts[j][1] + 5), fill=GRAFITE)
    if u > 0.6:
        caixinhas(img, gasto)


def pg_templo(img, t, u, dur):
    titulo_pagina(img, "Templo: cavar pra cima!", u)
    poe_foto(img, "templo", 420, 820, -3, u, 0.3, 480, 420, 2)
    k1, k2 = dur * 0.3, dur * 0.6
    for j, kk in enumerate((k1, k2)):
        poe(img, T.andar_templo(5 + j, 150), 420, 790, 0, u, kk, 0.3)
    valor = 4 + (u >= k1 + 0.3) + (u >= k2 + 0.3)
    x0 = 790
    escreve(img, "valor:", x0 - 40, 560, 54, seg(u, 0.6, 1.0))
    for j, v in enumerate(range(4, valor + 1)):
        escreve(img, str(v), x0 + j * 90, 670, 96, 1, VERM_C if v == valor else GRAFITE, "Kalam-Bold.ttf", centro=True)
        if v < valor:
            ImageDraw.Draw(img).line((x0 + j * 90 - 30, 670, x0 + j * 90 + 30, 670), fill=VERM_C, width=6)
    poe(img, postit("2 PA\npor andar", 54), 780, 1100, 6, u, k1 + 0.1)
    tx = "e o templo passa\na valer mais!"
    escreve(img, tx, 175, 1380, 60, seg(u, k2 + 0.4, k2 + 0.4 + tempo_escrita(tx)))


def pg_tesouro(img, t, u, dur):
    titulo_pagina(img, "Ruína: cavar tesouros", u)
    poe_foto(img, "ruina", 380, 660, -4, u, 0.3, 400, 350, 3)
    tc = dur * 0.18
    q = seg(u, tc, tc + 0.6)
    if q > 0:
        cola(img, adesivo("tesouro:4", 150), 380 + 380 * ease(q), 640 - 140 * math.sin(q * math.pi), 0, 1, 1, sombra=6)
    poe(img, postit("cavar\n= 3 PA", 54), 820, 900, 7, u, tc + 0.3)
    grupos = [([4], "1 = 1 ponto"), ([4, 4], "par = 3"), ([4, 4, 4], "trinca = 6!")]
    t0 = dur * 0.42
    for j, (fichas, rot) in enumerate(grupos):
        tj = t0 + j * (dur - t0 - 0.6) / 3
        y = 1110 + j * 165
        for i, f in enumerate(fichas):
            poe(img, adesivo(f"tesouro:{f}", 120), 250 + i * 95, y, (i - 1) * 7, u, tj + i * 0.08, 0.25)
        escreve(img, rot, 560, y, 64, seg(u, tj + 0.2, tj + 0.2 + tempo_escrita(rot)), VERM_C if j == 2 else AZUL_C)
    tl = t0 + 2 * (dur - t0 - 0.6) / 3
    caneta(img, circulo(700, 1440, 210, 70, 11), seg(u, tl + 0.6, tl + 1.1))


def pg_maioria(img, t, u, dur):
    titulo_pagina(img, "Quem manda no templo?", u)
    poe_foto(img, "templo", 540, 720, 2, u, 0.2, 520, 450, 4)
    t_chefe = dur * 0.45
    for k, (x, y) in enumerate([(700, 760), (780, 690), (760, 840)]):
        poe(img, adesivo("meeple:azul", 120), x, y, 4, u, 0.4 + 0.15 * k, 0.25)
    for k, (x, y) in enumerate([(360, 760), (430, 840)]):
        poe(img, adesivo("meeple:vermelho", 120), x, y, -4, u, 0.9 + 0.15 * k, 0.25)
    poe(img, adesivo("meeple:vermelho", 175), 330, 610, -6, u, t_chefe, 0.3)
    if u > t_chefe + 0.3:
        caneta(img, circulo(330, 610, 110, 120, 5), seg(u, t_chefe + 0.3, t_chefe + 0.7))
        seta(img, (220, 470), (280, 530), seg(u, t_chefe + 0.5, t_chefe + 0.9))
        escreve(img, "chefe = 3!", 175, 430, 56, seg(u, t_chefe + 0.6, t_chefe + 1.1), VERM_C, "Kalam-Bold.ttf")
    verm = 2 + (3 if u >= t_chefe + 0.3 else 0)
    escreve(img, "vermelho:", 175, 1180, 60, seg(u, 1.0, 1.5))
    escreve(img, "azul:", 175, 1310, 60, seg(u, 1.2, 1.6))
    d = ImageDraw.Draw(img)
    for i in range(verm if u > 1.2 else 0):  # risquinhos de contagem
        x = 480 + i * 34 + (14 if i >= 4 else 0)
        if i == 4:
            caneta(img, [(470, 1205), (620, 1165)], 1, VERM_C, 6)
        else:
            d.line((x, 1160, x, 1210), fill=VERM_C, width=6)
    for i in range(3 if u > 1.4 else 0):
        x = 480 + i * 34
        d.line((x, 1290, x, 1340), fill=AZUL_C, width=6)
    if u > t_chefe + 0.6:
        bate(img, carimbo("TEMPLO DO VERMELHO!", 72), W / 2 + 40, 1480, -5, u, t_chefe + 0.6)


def pg_guardiao(img, t, u, dur):
    meio = dur * 0.5
    if u < meio:
        titulo_pagina(img, "Quer garantir?", u)
        poe_foto(img, "templo", 540, 760, -2, u, 0.2, 520, 450, 5)
        q = seg(u, 0.5, 1.1)
        poe(img, adesivo("meeple:vermelho", 175), 540, 720 - 40 * math.sin(q * math.pi), 0, u, 0.5, 0.3)
        poe(img, postit("guardião\n= 5 PA", 54), 820, 420, 6, u, 1.0)
        bate(img, carimbo("GUARDADO", 96), 540, 1180, -8, u, 1.5)
        tx = "o templo é seu até o fim!"
        escreve(img, tx, 175, 1420, 58, seg(u, 1.9, 1.9 + tempo_escrita(tx)), VERM_C)
        return
    v = u - meio
    titulo_pagina(img, "Troca de tesouro", v)
    poe(img, adesivo("meeple:vermelho", 220), 300, 640, -5, v, 0.15)
    poe(img, adesivo("meeple:azul", 220), 780, 640, 5, v, 0.25)
    escreve(img, "você", 300, 800, 54, seg(v, 0.3, 0.6), AZUL_C, centro=True)
    escreve(img, "adversário", 780, 800, 54, seg(v, 0.35, 0.8), AZUL_C, centro=True)
    q = ease(seg(v, 0.6, 1.4))
    for k, (f, x0, x1) in enumerate(((1, 300, 780), (5, 780, 300))):
        x = x0 + (x1 - x0) * q
        y = 1000 + 120 * math.sin(q * math.pi) * (1 if k == 0 else -1)
        cola(img, adesivo(f"tesouro:{f}", 150), x, y, 0, 1, min(1, seg(v, 0.5, 0.7)), sombra=6)
    seta(img, (360, 1120), (720, 1120), seg(v, 0.6, 1.3), VERM_C, -0.25)
    seta(img, (720, 880), (360, 880), seg(v, 0.7, 1.4), VERM_C, -0.25)
    poe(img, postit("trocar\n= 3 PA", 54), 540, 1330, -4, v, 0.9)
    tx = "e ele não pode recusar!"
    escreve(img, tx, 175, 1560, 56, seg(v, 1.3, 1.3 + tempo_escrita(tx)), VERM_C)


def pg_vulcao(img, t, u, dur):
    tremor = max(0, 1 - abs(u - 0.9) * 2.5)
    titulo_pagina(img, "VULCÃO! hora de contar", u)
    poe_foto(img, "vulcao", 400 + 10 * tremor * math.sin(u * 70), 640, -5, u, 0.4, 420, 360, 6)
    if u > 0.9:
        for j in range(3):  # rabiscos de "fumaça" em lápis vermelho
            pts = [(560 + 30 * j + 20 * math.sin(s_ * 12 + j), 520 - 160 * s_) for s_ in np.linspace(0, 1, 18)]
            caneta(img, pts, seg(u, 0.9 + j * 0.1, 1.3 + j * 0.1), VERM_C, 5)
    bate(img, carimbo("CONTAGEM!", 90), 790, 900, 9, u, 1.0)
    t1 = dur * 0.38
    escreve(img, "+ templos que você domina", 175, 1110, 56, seg(u, t1, t1 + 0.9))
    escreve(img, "+ seus tesouros", 175, 1210, 56, seg(u, t1 + 0.5, t1 + 1.1))
    t2 = dur * 0.66
    escreve(img, "3 vulcões + contagem final", 175, 1330, 56, seg(u, t2, t2 + 1.0), GRAFITE)
    t3 = dur * 0.80
    tx = "mais pontos vence!"
    escreve(img, tx, 175, 1470, 76, seg(u, t3, t3 + 0.6), VERM_C, "Kalam-Bold.ttf")
    sublinha(img, 175, 820, 1525, seg(u, t3 + 0.6, t3 + 0.9))


def pg_cta(img, t, u, dur):
    if u < T.T_COMENTA:
        titulo_pagina(img, "Pergunta pra você:", u)
        tx = "Você escava templos\nou rouba tesouro?"
        escreve(img, tx, 175, 520, 78, seg(u, 0.3, 0.3 + tempo_escrita(tx, 34)), AZUL_C, "Kalam-Bold.ttf")
        poe(img, adesivo("meeple:vermelho", 230), 330, 980, -6, u, 1.2)
        poe(img, adesivo("tesouro:0", 230), 770, 980, 8, u, 1.4)
        escreve(img, "ou", 540, 980, 70, seg(u, 1.5, 1.7), VERM_C, "Kalam-Bold.ttf", centro=True)
        bate(img, carimbo("COMENTA AQUI!", 96), W / 2, 1360, -4, u, 1.9)
        return
    v = u - T.T_COMENTA
    titulo_pagina(img, "Pra levar pra casa:", v)
    img.alpha_composite(E.logo(200), (W - 250, 60))
    poe_foto(img, "caixa", 330, 720, -4, v, 0.15, 400, 440, 8)
    linhas = ["Alugue o Tikal", "2 a 4 jogadores", "90 min", "5 dias de jogo"]
    for k, li in enumerate(linhas):
        escreve(img, li, 600, 470 + k * 110, 62 if k == 0 else 52, seg(v, 0.4 + k * 0.25, 0.75 + k * 0.25),
                VERM_C if k == 0 else AZUL_C, "Kalam-Bold.ttf" if k == 0 else "PatrickHand-Regular.ttf")
    tx = "Reserve online · retire em Mauá\nou receba em casa"
    escreve(img, tx, 175, 1150, 56, seg(v, 1.3, 2.1))
    bate(img, carimbo("LINK NA BIO · @SUAVEZ_BG", 64, AZUL_C), W / 2, 1430, -3, v, 2.2)


PG = {"gancho": pg_gancho, "hexagono": pg_hexagono, "pa": pg_pa, "templo": pg_templo, "tesouro": pg_tesouro,
      "maioria": pg_maioria, "guardiao": pg_guardiao, "vulcao": pg_vulcao, "cta": pg_cta}
ORDEM = [c["cena"] for c in T.TL]
VIRA = 0.45  # duração da página virando


def folha(k, t, u, dur):
    img = pagina(k).copy()
    PG[ORDEM[k]](img, t, u, dur)
    return img


@lru_cache(None)
def folha_final(k):
    c = T.TL[k]
    return folha(k, c["ini"] + c["dur"] - 0.02, c["dur"] - 0.02, c["dur"])


def quadro(t):
    cena, u, dur = T.cena_em(t)
    k = ORDEM.index(cena)
    nova = folha(k, t, u, dur)
    # leve balanço de câmera na mão (bem sutil)
    dx, dy = 6 * math.sin(t * 0.7), 5 * math.sin(t * 0.53 + 1)
    if k > 0 and u < VIRA:
        q = ease(u / VIRA)
        img = mesa().copy()
        img.alpha_composite(nova)
        velha = folha_final(k - 1)
        # a folha anterior sobe e sai pela esquerda girando (vira a página do caderno)
        ang = 18 * q
        sp = velha.rotate(ang, resample=Image.BICUBIC, expand=True, center=None)
        x = int(-q * W * 1.15 - (sp.width - W) / 2)
        y = int(-q * 260 - (sp.height - H) / 2)
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.alpha_composite(Image.new("RGBA", sp.size, (0, 0, 0, int(110 * (1 - q)))), (x + 30, y + 30))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
        img.alpha_composite(sp, (x, y))
    else:
        img = mesa().copy()
        img.alpha_composite(nova, (int(dx), int(dy)))
    if not (cena == "cta" and u >= T.T_COMENTA):
        img.alpha_composite(E.logo(170), (W - 205, 40))
    T.legenda(img, t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


# ------------------------------------------------------------------------------------------------ som
SR = S.SR


def rabisco(d=0.6, semente=1):
    """Caneta riscando o papel: ruído em banda com a mão indo e voltando."""
    n = int(d * SR)
    rnd = np.random.default_rng(semente)
    x = S.bp_fft(rnd.normal(0, 1, n), 1800, 6500)
    t = np.arange(n) / SR
    env = (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 7 * t + rnd.uniform(0, 3)))) * np.minimum(1, t * 30) * np.minimum(1, (d - t) * 20)
    return x * env * 0.5


def folha_vira(d=0.45):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = S.bp_fft(np.random.default_rng(4).normal(0, 1, n), 600, 5000)
    return x * np.sin(np.pi * t / d) ** 2 * 0.8


def trilha(dur):
    """Diário de viagem: violão dedilhado (pluck), marimba suave e chocalho leve, 92 bpm."""
    out = np.zeros(int((dur + 1) * SR))
    b = 60 / 92
    acordes = [["D3", "A3", "D4", "F4"], ["A#2", "F3", "A#3", "D4"], ["C3", "G3", "C4", "E4"], ["A2", "E3", "A3", "C#4"]]
    n = int(dur / b) + 1
    for k in range(n):
        t0 = k * b
        ac = acordes[(k // 4) % 4]
        for j in range(2):
            nota = ac[(k * 2 + j) % 4]
            f = S.hz(nota)
            tt = np.arange(int(0.9 * SR)) / SR
            pl = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 5)
            S.add(out, pl, t0 + j * b / 2, 0.22)
        S.add(out, T.shaker(), t0 + b / 2, 0.08)
        if k % 8 == 0:
            S.add(out, T.tom(80, 0.5), t0, 0.35)
        if k >= 8 and k % 4 == 2:
            S.add(out, S.marimba(S.hz(ac[3]) * 2, b * 1.5), t0, 0.18)
    return out[:int(dur * SR)]


def cues():
    ev = []
    for i, c in enumerate(T.TL):
        ini, d = c["ini"], c["dur"]
        if i > 0:
            ev.append((ini, folha_vira(), 0.6))
        # caneta escrevendo no começo de cada página e em alguns momentos
        for k, tt in enumerate((0.1, 0.7, d * 0.45)):
            ev.append((ini + tt, rabisco(0.55, i * 7 + k), 0.35))
        n = c["cena"]
        if n == "pa":
            ev += [(ini + d * 0.30, T.baque(0.3), 0.35)]
        if n == "templo":
            ev += [(ini + d * x, T.baque(0.4), 0.5) for x in (0.3, 0.6)]
        if n == "tesouro":
            ev += [(ini + d * 0.18, S.plim(), 0.35)] + [(ini + d * 0.42 + j * (d * 0.58 - 0.6) / 3, S.plim(), 0.3)
                                                         for j in range(3)]
        if n == "maioria":
            ev += [(ini + d * 0.45 + 0.6, T.baque(0.4), 0.6)]
        if n == "guardiao":
            ev += [(ini + 1.5, T.baque(0.4), 0.6), (ini + d * 0.5 + 0.6, S.sopro(0.6), 0.35)]
        if n == "vulcao":
            ev += [(ini + 0.9, T.ronco(1.2), 0.8), (ini + 1.0, T.baque(0.4), 0.6)]
        if n == "cta":
            ev += [(ini + 1.9, T.baque(0.4), 0.6), (ini + T.T_COMENTA + 2.2, T.baque(0.4), 0.6)]
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--sem-legenda", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [quadro(x) for x in a.frame]
        cols = min(6, len(ims))
        rows = math.ceil(len(ims) / cols)
        sh = Image.new("RGB", (360 * cols, 640 * rows))
        for k, im in enumerate(ims):
            sh.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
        sh.save(os.path.join(OUT, "frames_caderno.jpg"), quality=88)
        print("ok")
        return
    nome = "caderno_previa"
    com = os.path.join(OUT, f"{nome}_com.wav")
    S.grava(com, T.DUR, cues(), trilha(T.DUR + 0.5), musica_ganho=0.36, fx_ganho=0.8)
    n = int(round(T.DUR * FPS))
    base = os.path.join(OUT, f"{nome}.mp4")
    encode(base, render, list(range(n)), com)
    final_loudness(base, base.replace(".mp4", "_final.mp4"))
    print("ok", T.DUR)


if __name__ == "__main__":
    main()
