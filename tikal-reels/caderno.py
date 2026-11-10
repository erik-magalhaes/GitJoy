#!/usr/bin/env python3
"""Tikal, visual C "CADERNO DO ARQUEÓLOGO" (10/nov/2026). MESMO roteiro e mesma linha do tempo do tikal.py (a narração
serve para os dois). 2ª rodada (pedido dele: "mais realista as escritas e a folha, nada de animação"): a folha é uma
'foto' de caderno (papel.py: fibras, luz, curvatura na espiral de arame, pauta impressa irregular) e a escrita é tinta de
esferográfica (Caveat com variação letra a letra, aplicada em multiplicar). Nada pula, cresce ou voa: cada coisa só
APARECE no lugar (como foto a foto), a caneta escreve/circula no ritmo de uma mão e a página troca com corte seco.
As peças OFICIAIS entram como fotos impressas presas com fita (hexágonos do manual, capa, caixa) e recortes colados
(exploradores, tesouros, logo).

    /usr/bin/python3 caderno.py --frame 2 8 15 ...   # out/frames_caderno.jpg
    /usr/bin/python3 caderno.py                      # out/caderno_previa_final.mp4 (sem voz, legenda do roteiro)
"""
import argparse
import math
import os
import random
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import papel as PP
import pecas as P
import tikal as T
from pecas import W, H, fonte, cola
from papel import TINTA_AZUL as AZUL_C, TINTA_VERM as VERM_C, GRAFITE, LINHA0, PASSO
from tikal import E, S, FPS, encode, final_loudness, seg

OUT = T.OUT
S_TXT = 62  # tamanho da letra que cabe na pauta


def linha(n):
    """y da n-ésima linha da pauta (onde a letra 'senta')."""
    return LINHA0 + n * PASSO


# ------------------------------------------------------------------------------------------------ escrita
def escreve(img, txt, x, n_linha, u, cor=AZUL_C, s=S_TXT, peso=520, centro=False, semente=None, base=None):
    """Tinta que vai aparecendo da esquerda para a direita (a mão escrevendo), sentada na linha n_linha da pauta."""
    if u <= 0:
        return
    sem = semente if semente is not None else (hash(txt) % 997)
    sp, larg, alt = PP.tinta(txt, s, cor, "Caveat.ttf", peso, sem)
    tot = sum(larg)
    q = u * tot
    m = np.zeros((sp.height, sp.width), np.uint8)
    acc = 0
    for i, w in enumerate(larg):
        vis = max(0, min(w, q - acc))
        if vis > 0:
            y0 = int(i * alt)
            m[y0:y0 + alt + 30, :int(vis)] = 255
        acc += w
    m = cv2.GaussianBlur(m, (0, 0), 3)
    a = np.asarray(sp.getchannel("A")).astype(np.float32) * m / 255
    sp = sp.copy()
    sp.putalpha(Image.fromarray(a.astype(np.uint8)))
    y = (base if base is not None else linha(n_linha)) - s * 0.86 - 18
    px = x - (larg[0] / 2 if centro else 0)
    PP.multiplica(img, sp, px, y)


def tempo_escrita(txt, cps=17):
    return max(0.4, len(txt.replace("\n", "")) / cps)


def caneta(img, pts, u, cor=VERM_C, w=6):
    """Traço de caneta até a fração u, com tinta irregular, em multiplicar."""
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
    xs, ys = [p[0] for p in out], [p[1] for p in out]
    x0, y0 = int(min(xs)) - 20, int(min(ys)) - 20
    lay = Image.new("L", (int(max(xs)) - x0 + 40, int(max(ys)) - y0 + 40), 0)
    ImageDraw.Draw(lay).line([(p[0] - x0, p[1] - y0) for p in out], fill=255, width=w, joint="curve")
    m = cv2.GaussianBlur(np.asarray(lay).astype(np.float32) / 255, (0, 0), 0.7)
    m *= np.clip(0.78 + 0.25 * np.random.default_rng(len(pts)).normal(0, 0.4, m.shape), 0.5, 1)
    rgb = np.zeros(m.shape + (3,), np.float32)
    rgb[...] = cor
    sp = Image.fromarray(np.dstack([rgb, np.clip(m * 235, 0, 255)]).astype(np.uint8))
    PP.multiplica(img, sp, x0, y0)


def circulo(cx, cy, rx, ry, semente=1, voltas=1.12):
    rnd = random.Random(semente)
    pts = []
    n = 70
    a0 = rnd.uniform(0, 6.28)
    for i in range(n + 1):
        a = a0 + voltas * 2 * math.pi * i / n
        k = 1 + 0.05 * math.sin(i * 0.4 + semente) + 0.04 * (i / n)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


def seta(img, p0, p1, u, cor=VERM_C, curva=0.25, w=6):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    nx, ny = -(p1[1] - p0[1]) * curva, (p1[0] - p0[0]) * curva
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * (mx + nx) + t * t * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * (my + ny) + t * t * p1[1]) for t in np.linspace(0, 1, 30)]
    caneta(img, pts, min(1, u / 0.85), cor, w)
    if u > 0.85:
        a = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
        k = min(1, (u - 0.85) / 0.15)
        for da in (2.6, -2.6):
            caneta(img, [p1, (p1[0] + 32 * k * math.cos(a + da), p1[1] + 32 * k * math.sin(a + da))], 1, cor, w)


def sublinha(img, x0, x1, y, u, cor=VERM_C):
    caneta(img, [(x0 + (x1 - x0) * t, y + 4 * math.sin(t * 9)) for t in np.linspace(0, 1, 20)], u, cor, 6)


# ------------------------------------------------------------------------------------------------ fotos, recortes, post-its
@lru_cache(None)
def foto(chave, w, h=None):
    """Foto impressa em papel fotográfico (borda branca), com leve brilho e textura; a imagem entra inteira."""
    h = h or w
    if chave == "capa":
        c = P.capa()
        y0, y1 = int(c.height * 0.24), int(c.height * 0.80)
        larg = int((y1 - y0) * w / h)
        x0 = int(c.width * 0.62 - larg / 2)
        sp = c.crop((x0, y0, x0 + larg, y1)).convert("RGBA")
    elif chave == "caixa":
        sp = P.img("caixa.png")
    else:
        sp = P.img(f"hex_{chave}.png")
    mold = Image.new("RGBA", (w + 36, h + 100), (250, 249, 244, 255))
    s = sp.copy()
    s.thumbnail((w, h), Image.LANCZOS)
    area = Image.new("RGBA", (w, h), (226, 222, 210, 255) if chave != "capa" else (0, 0, 0, 255))
    area.alpha_composite(s, ((w - s.width) // 2, (h - s.height) // 2))
    mold.alpha_composite(area, (18, 18))
    a = np.asarray(mold).astype(np.float32)
    hh, ww = a.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww]
    brilho = 0.06 * np.exp(-((xx / ww - 0.3) ** 2 + (yy / hh - 0.2) ** 2) / 0.08)  # reflexo suave do papel foto
    grao = np.random.default_rng(w).normal(0, 2.0, (hh, ww))
    a[..., :3] = a[..., :3] * (1 - brilho[..., None]) + 255 * brilho[..., None] + grao[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


@lru_cache(None)
def fita(w=170, semente=0):
    """Fita adesiva fosca: meio transparente, com textura e pontas serrilhadas."""
    rnd = np.random.default_rng(semente)
    h = 54
    a = np.full((h, w), 150, np.float32) + rnd.normal(0, 10, (h, w))
    for x in range(w):
        for borda in (0, 1):
            pass
    m = np.ones((h, w), np.float32)
    for y in range(h):
        c = int(4 + 3 * math.sin(y * 1.7 + semente) + rnd.uniform(0, 3))
        m[y, :c] = 0
        m[y, w - c - int(rnd.uniform(0, 3)):] = 0
    rgb = np.zeros((h, w, 3), np.float32)
    rgb[...] = (238, 232, 205)
    return Image.fromarray(np.dstack([rgb, a * m]).astype(np.uint8))


@lru_cache(None)
def recorte(chave, h):
    """Peça recortada com tesoura e colada: borda branca irregular + sombra curta (papel colado)."""
    tipo, arg = chave.split(":")
    if tipo == "meeple":
        sp = P.meeple(arg, h)
    elif tipo == "tesouro":
        sp = P.tesouro(int(arg), h)
    else:
        sp = P.img("logo_tikal.png")
        sp = sp.resize((h * sp.width // sp.height, h), Image.LANCZOS)
    pad = 14
    a = np.pad(np.asarray(sp.getchannel("A")), pad)
    borda = cv2.dilate((a > 30).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    out = Image.new("RGBA", (sp.width + 2 * pad, sp.height + 2 * pad), (0, 0, 0, 0))
    branco = Image.new("RGBA", out.size, (248, 246, 240, 255))
    branco.putalpha(Image.fromarray(borda))
    out.alpha_composite(branco)
    out.alpha_composite(sp, (pad, pad))
    return out


@lru_cache(None)
def postit(txt, s=58, cor=(250, 222, 104), w=320, semente=1):
    """Post-it: papel com textura, ponta de baixo levemente levantada (sombra), texto à mão em multiplicar."""
    rnd = np.random.default_rng(semente)
    a = np.array(cor, np.float32)[None, None] * (1 + 0.025 * rnd.normal(0, 1, (w, w))[..., None])
    yy = np.linspace(0, 1, w)[:, None, None]
    a *= 1 - 0.08 * yy
    a[:30] *= 0.94  # faixa de cola
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    linhas = txt.split("\n")
    tsp, larg, alt = PP.tinta(txt, s, (30, 30, 50), "Caveat.ttf", 700, semente)
    PP.multiplica(im, tsp, (w - max(larg)) / 2, (w - alt * len(linhas)) / 2 - 6)
    sh = Image.new("RGBA", (w + 40, w + 40), (0, 0, 0, 0))
    m = Image.new("L", (w, w), 0)
    ImageDraw.Draw(m).polygon([(6, 30), (w - 6, 30), (w + 6, w + 6), (0, w)], fill=110)
    sh.paste((0, 0, 0, 255), (8, 10), m)
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    sh.alpha_composite(im, (0, 0))
    return sh


@lru_cache(None)
def carimbo(txt, s=92, cor=VERM_C):
    f = fonte("Anton-Regular.ttf", s)
    larg = int(f.getlength(txt)) + 70
    alt = int(s * 1.35) + 30
    im = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, larg - 7, alt - 7), 18, outline=cor + (255,), width=9)
    d.text((larg / 2, alt / 2 + 3), txt, font=f, fill=cor + (255,), anchor="mm")
    a = np.asarray(im.getchannel("A")).astype(float)
    rnd = np.random.default_rng(len(txt))
    falha = cv2.GaussianBlur(rnd.random(a.shape), (0, 0), 2.2)
    a *= np.clip((falha - 0.25) * 3, 0.25, 1) * 0.8
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def poe(img, sp, x, y, rot, u, t0, sombra=7):
    """A peça simplesmente está ali a partir de t0 (sem pular nem crescer)."""
    if u >= t0:
        cola(img, sp, x, y, rot, 1.0, 1.0, sombra=sombra)


def poe_foto(img, chave, x, y, rot, u, t0, w, h=None, semente=0):
    if u < t0:
        return
    cola(img, foto(chave, w, h), x, y, rot, 1.0, 1.0, sombra=10)
    fh = (h or w) + 100
    dy = -fh / 2 + 8
    cola(img, fita(170, semente), x - dy * math.sin(math.radians(rot)), y + dy * math.cos(math.radians(rot)),
         rot + 4 - 8 * (semente % 2))


def carimba(img, sp, x, y, rot, u, t0):
    if u >= t0:
        s = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
        PP.multiplica(img, s, x - s.width / 2, y - s.height / 2)


# ------------------------------------------------------------------------------------------------ páginas (cenas)
def titulo_pagina(img, txt, u, t0=0.05):
    escreve(img, txt, 185, 0, seg(u, t0, t0 + tempo_escrita(txt, 22)), AZUL_C, 76, 640)


def pg_gancho(img, t, u, dur):
    escreve(img, "Diário da expedição", 185, 0, seg(u, 0.0, 0.7), AZUL_C, 76, 640)
    poe_foto(img, "capa", 600, 600, 3, u, 0.15, 560, 440, 1)
    tx = "Você entraria na selva\natrás de templos perdidos?"
    escreve(img, tx, 185, 13, seg(u, 0.3, 0.3 + tempo_escrita(tx, 26)), AZUL_C, 70, 600)
    k = dur * 0.52
    poe(img, recorte("logo:x", 180), 560, 1340, -4, u, k)
    caneta(img, circulo(560, 1340, 320, 135, 3), seg(u, k + 0.3, k + 0.9))
    tx2 = "... e você comanda uma expedição!"
    escreve(img, tx2, 185, 21, seg(u, k + 0.6, k + 0.6 + tempo_escrita(tx2, 22)), VERM_C)


HEX4 = [("templo", "templo", -5), ("ruina", "ruína (tesouro!)", 4), ("clareira", "clareira", -3), ("vulcao", "VULCÃO!!", 5)]


def pg_hexagono(img, t, u, dur):
    titulo_pagina(img, "Dia 1: a selva cresce", u)
    tx = "Na sua vez: tira um hexágono\ne encaixa no mapa."
    escreve(img, tx, 185, 2, seg(u, 0.5, 0.5 + tempo_escrita(tx, 24)))
    pos = [(330, 760), (780, 760), (330, 1250), (780, 1250)]
    t0 = 1.6
    passo = (dur - t0 - 0.8) / 4
    linhas = [10, 10, 18, 18]
    for k, ((ch, nome, rot), (x, y)) in enumerate(zip(HEX4, pos)):
        tk = t0 + k * passo
        poe_foto(img, ch, x, y, rot, u, tk, 340, 300, k)
        escreve(img, nome, x, 0, seg(u, tk + 0.25, tk + 0.25 + tempo_escrita(nome)), VERM_C if k == 3 else AZUL_C,
                46, centro=True, base=y + 186)  # escrito na borda branca da foto
    tl = t0 + 3 * passo + 0.5
    caneta(img, circulo(780, 1250, 230, 220, 7), seg(u, tl, tl + 0.6))


def caixinhas(img, gastos, x0=190, y=linha(5) - 26):
    for k in range(10):
        x = x0 + k * 76
        caneta(img, [(x, y - 24), (x + 50, y - 26), (x + 52, y + 24), (x + 2, y + 26), (x, y - 24)], 1, AZUL_C, 4)
        q = min(1.0, max(0.0, gastos - k))
        if q > 0:
            caneta(img, [(x + 6, y - 18), (x + 46, y + 20)], min(1, q * 2), VERM_C, 6)
            if q > 0.5:
                caneta(img, [(x + 46, y - 18), (x + 6, y + 20)], (q - 0.5) * 2, VERM_C, 6)


def pg_pa(img, t, u, dur):
    titulo_pagina(img, "Regra nº 1: 10 pontos de ação", u)
    escreve(img, "por turno (PA):", 190, 2, seg(u, 0.6, 1.3))
    a, b = (340, 930), (770, 930)
    poe_foto(img, "clareira", a[0], a[1], -4, u, 0.5, 320, 280, 1)
    poe_foto(img, "templo", b[0], b[1], 4, u, 0.7, 320, 280, 2)
    escreve(img, "acampamento", a[0], 15, seg(u, 0.9, 1.6), AZUL_C, centro=True)
    escreve(img, "templo", b[0], 15, seg(u, 1.0, 1.5), AZUL_C, centro=True)
    t_entra, t_anda = dur * 0.30, dur * 0.52
    gasto = 0.0
    q = seg(u, t_anda, dur - 0.6)
    for k in range(2):  # as 2 pedras do caminho, desenhadas a lápis
        x = 520 + k * 76
        caneta(img, [(x - 24, 905), (x + 24, 903), (x + 25, 945), (x - 23, 947), (x - 24, 905)], 1, GRAFITE, 4)
    if u >= t_entra:
        gasto = 1.0 + 2 * q
        chegou = q >= 1
        x = b[0] if chegou else a[0]
        poe(img, recorte("meeple:vermelho", 150), x, a[1] - 40, -6, u, t_entra)
        poe(img, postit("colocar\n= 1 PA", 58, semente=2), 310, 1460, -6, u, t_entra + 0.2)
        if u > t_anda:
            poe(img, postit("andar = 1 PA\npor pedra", 52, (168, 226, 170), semente=3), 770, 1460, 5, u, t_anda + 0.2)
            pts = [(a[0] + 60 + (b[0] - a[0] - 120) * s_, a[1] - 170 - 70 * math.sin(s_ * math.pi)) for s_ in np.linspace(0, 1, 40)]
            caneta(img, pts, q, GRAFITE, 4)
            if q >= 1:
                seta(img, pts[-6], pts[-1], 1, GRAFITE, 0, 4)
    if u > 0.6:
        caixinhas(img, gasto)


def pg_templo(img, t, u, dur):
    titulo_pagina(img, "Templo: cavar pra cima!", u)
    poe_foto(img, "templo", 420, 820, -3, u, 0.3, 480, 420, 2)
    k1, k2 = dur * 0.3, dur * 0.6
    for j, kk in enumerate((k1, k2)):
        poe(img, T.andar_templo(5 + j, 150), 420, 790, 0, u, kk)
    valor = 4 + (u >= k1 + 0.2) + (u >= k2 + 0.2)
    escreve(img, "valor:", 740, 5, seg(u, 0.6, 1.1))
    for j, v in enumerate(range(4, valor + 1)):
        escreve(img, str(v), 770 + j * 90, 7, 1, VERM_C if v == valor else GRAFITE, 110, 700, semente=v)
        if v < valor:
            caneta(img, [(760 + j * 90, linha(7) - 40), (820 + j * 90, linha(7) - 50)], 1, VERM_C, 6)
    poe(img, postit("2 PA\npor andar", 60, semente=4), 790, 1110, 6, u, k1 + 0.1)
    tx = "e o templo passa\na valer mais!"
    escreve(img, tx, 185, 19, seg(u, k2 + 0.4, k2 + 0.4 + tempo_escrita(tx)))


def pg_tesouro(img, t, u, dur):
    titulo_pagina(img, "Ruína: cavar tesouros", u)
    poe_foto(img, "ruina", 380, 640, -4, u, 0.3, 400, 350, 3)
    tc = dur * 0.18
    poe(img, recorte("tesouro:4", 150), 760, 560, 6, u, tc)
    seta(img, (560, 650), (690, 590), seg(u, tc, tc + 0.4), VERM_C, -0.3)
    poe(img, postit("cavar\n= 3 PA", 60, semente=5), 830, 880, 7, u, tc + 0.3)
    grupos = [([4], "um = 1 ponto"), ([4, 4], "par = 3"), ([4, 4, 4], "trinca = 6!")]
    t0 = dur * 0.42
    for j, (fichas, rot) in enumerate(grupos):
        tj = t0 + j * (dur - t0 - 0.6) / 3
        n = 15 + j * 3
        y = linha(n) - 30
        for i, f in enumerate(fichas):
            poe(img, recorte(f"tesouro:{f}", 110), 250 + i * 90, y, (i - 1) * 7, u, tj + i * 0.15)
        escreve(img, rot, 560, n, seg(u, tj + 0.3, tj + 0.3 + tempo_escrita(rot)), VERM_C if j == 2 else AZUL_C, 70)
    tl = t0 + 2 * (dur - t0 - 0.6) / 3
    caneta(img, circulo(720, linha(21) - 25, 210, 62, 11), seg(u, tl + 0.9, tl + 1.4))


def pg_maioria(img, t, u, dur):
    titulo_pagina(img, "Quem manda no templo?", u)
    poe_foto(img, "templo", 560, 740, 2, u, 0.2, 520, 450, 4)
    t_chefe = dur * 0.45
    for k, (x, y) in enumerate([(720, 780), (800, 710), (780, 860)]):
        poe(img, recorte("meeple:azul", 115), x, y, 4, u, 0.4 + 0.2 * k)
    for k, (x, y) in enumerate([(400, 780), (470, 860)]):
        poe(img, recorte("meeple:vermelho", 115), x, y, -4, u, 1.0 + 0.2 * k)
    poe(img, recorte("meeple:vermelho", 170), 350, 640, -6, u, t_chefe)
    if u > t_chefe:
        caneta(img, circulo(350, 640, 105, 115, 5), seg(u, t_chefe + 0.2, t_chefe + 0.6))
        seta(img, (250, 480), (300, 545), seg(u, t_chefe + 0.5, t_chefe + 0.8))
        escreve(img, "chefe = 3!", 190, 3, seg(u, t_chefe + 0.6, t_chefe + 1.2), VERM_C, 74, 700)
    verm = 2 + (3 if u >= t_chefe + 0.3 else 0)
    escreve(img, "vermelho:", 190, 15, seg(u, 1.0, 1.6))
    escreve(img, "azul:", 190, 17, seg(u, 1.3, 1.7))
    for i in range(verm if u > 1.6 else 0):  # risquinhos de contagem
        x = 500 + i * 30
        if i == 4:
            caneta(img, [(485, linha(15) - 10), (625, linha(15) - 52)], 1, VERM_C, 6)
        else:
            caneta(img, [(x, linha(15) - 55), (x + 3, linha(15) - 5)], 1, VERM_C, 6)
    for i in range(3 if u > 1.7 else 0):
        x = 500 + i * 30
        caneta(img, [(x, linha(17) - 55), (x + 3, linha(17) - 5)], 1, AZUL_C, 6)
    carimba(img, carimbo("TEMPLO DO VERMELHO!", 68), W / 2 + 40, 1500, -5, u, t_chefe + 0.9)


def pg_guardiao(img, t, u, dur):
    meio = dur * 0.5
    if u < meio:
        titulo_pagina(img, "Quer garantir?", u)
        poe_foto(img, "templo", 540, 760, -2, u, 0.2, 520, 450, 5)
        poe(img, recorte("meeple:vermelho", 170), 540, 700, 0, u, 0.6)
        poe(img, postit("guardião\n= 5 PA", 60, semente=6), 850, 420, 6, u, 1.0)
        carimba(img, carimbo("GUARDADO", 92), 540, 1180, -8, u, 1.5)
        tx = "o templo é seu até o fim!"
        escreve(img, tx, 185, 19, seg(u, 1.9, 1.9 + tempo_escrita(tx)), VERM_C)
        return
    v = u - meio
    titulo_pagina(img, "Troca de tesouro", v)
    poe(img, recorte("meeple:vermelho", 210), 300, 620, -5, v, 0.15)
    poe(img, recorte("meeple:azul", 210), 780, 620, 5, v, 0.25)
    escreve(img, "você", 300, 9, seg(v, 0.3, 0.6), AZUL_C, centro=True)
    escreve(img, "adversário", 780, 9, seg(v, 0.35, 0.9), AZUL_C, centro=True)
    trocou = v >= 1.5
    for k, (f, x0, x1) in enumerate(((1, 300, 780), (5, 780, 300))):
        poe(img, recorte(f"tesouro:{f}", 140), x1 if trocou else x0, 1000, 0, v, 0.45)
    seta(img, (380, 1110), (700, 1110), seg(v, 0.7, 1.3), VERM_C, -0.25)
    seta(img, (700, 890), (380, 890), seg(v, 0.8, 1.4), VERM_C, -0.25)
    poe(img, postit("trocar\n= 3 PA", 60, semente=7), 540, 1340, -4, v, 1.0)
    tx = "e ele não pode recusar!"
    escreve(img, tx, 185, 21, seg(v, 1.4, 1.4 + tempo_escrita(tx)), VERM_C)


def pg_vulcao(img, t, u, dur):
    titulo_pagina(img, "VULCÃO! hora de contar", u)
    poe_foto(img, "vulcao", 400, 640, -5, u, 0.4, 420, 360, 6)
    carimba(img, carimbo("CONTAGEM!", 88), 800, 880, 9, u, 1.0)
    t1 = dur * 0.38
    escreve(img, "+ templos que você domina", 190, 14, seg(u, t1, t1 + 1.2))
    escreve(img, "+ seus tesouros", 190, 16, seg(u, t1 + 0.6, t1 + 1.3))
    t2 = dur * 0.66
    escreve(img, "3 vulcões + contagem final", 190, 18, seg(u, t2, t2 + 1.2), GRAFITE)
    t3 = dur * 0.80
    escreve(img, "mais pontos vence!", 190, 20, seg(u, t3, t3 + 0.8), VERM_C, 88, 700)
    sublinha(img, 190, 760, linha(20) + 14, seg(u, t3 + 0.8, t3 + 1.1))


def pg_cta(img, t, u, dur):
    if u < T.T_COMENTA:
        titulo_pagina(img, "Pergunta pra você:", u)
        tx = "Você escava templos\nou rouba tesouro?"
        escreve(img, tx, 190, 5, seg(u, 0.3, 0.3 + tempo_escrita(tx, 22)), AZUL_C, 90, 650)
        poe(img, recorte("meeple:vermelho", 230), 330, 1000, -6, u, 1.2)
        poe(img, recorte("tesouro:0", 230), 770, 1000, 8, u, 1.4)
        escreve(img, "ou", 520, 12, seg(u, 1.5, 1.8), VERM_C, 80, 700)
        carimba(img, carimbo("COMENTA AQUI!", 96), W / 2, 1370, -4, u, 1.9)
        return
    v = u - T.T_COMENTA
    titulo_pagina(img, "Pra levar pra casa:", v)
    img.alpha_composite(E.logo(200), (W - 250, 70))
    poe_foto(img, "caixa", 340, 720, -4, v, 0.15, 400, 440, 8)
    linhas_ = [("Alugue o Tikal", VERM_C, 82), ("2 a 4 jogadores", AZUL_C, S_TXT), ("90 min", AZUL_C, S_TXT),
               ("5 dias de jogo", AZUL_C, S_TXT)]
    for k, (li, cor, s) in enumerate(linhas_):
        escreve(img, li, 610, 5 + 2 * k, seg(v, 0.4 + k * 0.35, 0.9 + k * 0.35), cor, s, 650 if k == 0 else 520)
    tx = "Reserve online · retire em Mauá\nou receba em casa"
    escreve(img, tx, 190, 15, seg(v, 1.8, 2.8))
    carimba(img, carimbo("LINK NA BIO · @SUAVEZ_BG", 62, AZUL_C), W / 2, 1470, -3, v, 2.9)


PG = {"gancho": pg_gancho, "hexagono": pg_hexagono, "pa": pg_pa, "templo": pg_templo, "tesouro": pg_tesouro,
      "maioria": pg_maioria, "guardiao": pg_guardiao, "vulcao": pg_vulcao, "cta": pg_cta}
ORDEM = [c["cena"] for c in T.TL]


def quadro(t):
    cena, u, dur = T.cena_em(t)
    k = ORDEM.index(cena)
    img = PP.folha(k).copy()
    PG[cena](img, t, u, dur)
    if not (cena == "cta" and u >= T.T_COMENTA):
        img.alpha_composite(E.logo(170), (W - 205, 40))
    T.legenda(img, t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


# ------------------------------------------------------------------------------------------------ som
SR = S.SR


def rabisco(d=0.6, semente=1):
    """Caneta riscando o papel."""
    n = int(d * SR)
    rnd = np.random.default_rng(semente)
    x = S.bp_fft(rnd.normal(0, 1, n), 1800, 6500)
    t = np.arange(n) / SR
    env = (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 7 * t + rnd.uniform(0, 3)))) * np.minimum(1, t * 30) * \
        np.minimum(1, (d - t) * 20)
    return x * env * 0.5


def folha_vira(d=0.35):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = S.bp_fft(np.random.default_rng(4).normal(0, 1, n), 600, 5000)
    return x * np.sin(np.pi * t / d) ** 2 * 0.7


def papel_pousa(d=0.12):
    n = int(d * SR)
    t = np.arange(n) / SR
    return S.bp_fft(np.random.default_rng(6).normal(0, 1, n), 300, 3000) * np.exp(-t * 40) * 0.6


def trilha(dur):
    """Diário de viagem: violão dedilhado, marimba suave e chocalho leve, 92 bpm."""
    out = np.zeros(int((dur + 1) * SR))
    b = 60 / 92
    acordes = [["D3", "A3", "D4", "F4"], ["A#2", "F3", "A#3", "D4"], ["C3", "G3", "C4", "E4"], ["A2", "E3", "A3", "C#4"]]
    n = int(dur / b) + 1
    for k in range(n):
        t0 = k * b
        ac = acordes[(k // 4) % 4]
        for j in range(2):
            f = S.hz(ac[(k * 2 + j) % 4])
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
            ev.append((ini, folha_vira(), 0.5))
        for k, tt in enumerate((0.1, 0.7, d * 0.45)):
            ev.append((ini + tt, rabisco(0.55, i * 7 + k), 0.35))
        for tt in (0.2, 0.5):
            ev.append((ini + tt, papel_pousa(), 0.4))
        n = c["cena"]
        if n in ("maioria", "guardiao", "vulcao", "cta"):
            ev.append((ini + {"maioria": d * 0.45 + 0.9, "guardiao": 1.5, "vulcao": 1.0, "cta": 1.9}[n], T.baque(0.3), 0.5))
        if n == "vulcao":
            ev.append((ini + 0.4, T.ronco(1.0), 0.5))
        if n == "cta":
            ev.append((ini + T.T_COMENTA + 2.9, T.baque(0.3), 0.5))
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
