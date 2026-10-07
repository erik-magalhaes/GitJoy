#!/usr/bin/env python3
"""Reels "o que são os jogos modernos" – visual ESTANTE DA LUDOTECA (caixas do acervo da Sua Vez em prateleiras
de madeira, caixas saindo da estante em stop motion e etiquetas de preço).

    python3 ludoteca.py --frame 1 3 6    # quadros de teste (out/frames.jpg)
    python3 ludoteca.py --only preview   # só a versão com legenda
    python3 ludoteca.py                  # com e sem legenda (out/hobby_preview.mp4 e out/hobby_limpo.mp4)
"""
import argparse
import json
import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import som_hobby as som

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "..", "promo"))
C = os.path.join(ROOT, "assets", "caixas")
FN = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
POSE = 12

ORANGE, ORANGE_D = (249, 115, 22), (214, 84, 6)
NAVY, WHITE, CREAM = (15, 23, 42), (255, 255, 255), (255, 247, 237)
GREEN, BLUE, GRAY = (22, 163, 74), (44, 120, 200), (110, 112, 122)
KRAFT, KRAFT_D, INK = (214, 178, 128), (120, 82, 44), (52, 32, 18)
LUCKY, POP, POPB, SEMI = "LuckiestGuy-Regular.ttf", "Poppins-ExtraBold.ttf", "Poppins-Black.ttf", \
    "Poppins-SemiBold.ttf"
TODAS = ["7_wonders_duel", "azul_duel", "camel_up_second_edition", "cartographers", "clank_catacombs", "dixit",
         "everdell_duo", "flamecraft", "harmonies", "hive", "hot_streak", "king_of_tokyo", "marvel_united",
         "mlem_space_agency", "nekojima", "root", "santorini", "ticket_to_ride", "wingspan"]


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.6):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


def pose(t):
    return int(t * POSE) / POSE


def pop(t, t0, d=0.35):
    u = seg(t, t0, t0 + d)
    return max(0.0, out_back(u)) if u < 1 else 1.0


def jit(t, a=2.0, seed=0):
    """Tremidinho de mão do stop motion (muda 12 vezes por segundo)."""
    r = np.random.default_rng(int(t * POSE) * 31 + seed)
    return r.uniform(-a, a), r.uniform(-a, a), r.uniform(-a * 0.4, a * 0.4)


def balanco(t, t0, amp=14, f=1.6, tau=0.9):
    """Etiqueta pendurada balançando e parando (pêndulo amortecido)."""
    u = max(0.0, t - t0)
    return amp * math.cos(2 * math.pi * f * u) * math.exp(-u / tau)


@lru_cache(None)
def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


@lru_cache(None)
def caixa(n, h):
    im = Image.open(os.path.join(C, n + ".png")).convert("RGBA")
    return im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)


def sombra(im, blur=14, off=(10, 18), op=0.45, cor=(0, 0, 0)):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * op)), (pad + off[0], pad + off[1]))
    sh = Image.new("RGBA", out.size, cor + (255,))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


@lru_cache(None)
def caixa_s(n, h):
    return sombra(caixa(n, h), max(8, h // 30), (h // 40, h // 22), 0.55)


def cola(img, im, x, y, rot=0.0, sc=1.0, alpha=1.0, sx=1.0):
    if sc <= 0.02 or alpha <= 0.01 or abs(sx) < 0.02:
        return
    if abs(sc - 1) > 0.003 or abs(sx - 1) > 0.003:
        im = im.resize((max(2, int(im.width * sc * abs(sx))), max(2, int(im.height * sc))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def cola_topo(img, im, x, y, rot=0.0, sc=1.0):
    """Cola pendurado pelo topo (x, y = ponto do barbante): gira em volta desse ponto."""
    if sc <= 0.02:
        return
    if abs(sc - 1) > 0.003:
        im = im.resize((max(2, int(im.width * sc)), max(2, int(im.height * sc))), Image.BICUBIC)
    h = im.height
    r = math.radians(rot)
    cx, cy = x + math.sin(r) * h / 2, y + math.cos(r) * h / 2
    cola(img, im, cx, cy, rot)


@lru_cache(None)
def logo_card(width):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2, fill=WHITE)
    card.alpha_composite(lg, (pad, pad))
    return card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)


# ---------------------------------------------------------------- estante
@lru_cache(None)
def parede():
    """Fundo de madeira escura com veios."""
    img = Image.new("RGBA", (W, H), (58, 36, 24, 255))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(1)
    for k in range(0, W, 5):
        c = 60 + int(rng.integers(0, 12))
        d.line((k, 0, k + 30 * math.sin(k * 0.03), H), fill=(c, 38 + c // 12, 25), width=4)
    for k in range(0, W, 180):  # tábuas
        d.line((k, 0, k, H), fill=(40, 24, 15), width=3)
    return img


def prateleira(d, y, x0=0, x1=W):
    d.rectangle((x0, y, x1, y + 38), fill=(156, 104, 62))
    d.rectangle((x0, y, x1, y + 6), fill=(186, 132, 86))
    d.rectangle((x0, y + 38, x1, y + 54), fill=(92, 58, 34))


ESTANTE = [  # (y da prateleira, caixas da fileira)
    (560, ["7_wonders_duel", "azul_duel", "camel_up_second_edition", "cartographers"]),
    (960, ["king_of_tokyo", "harmonies", "dixit", "nekojima"]),
    (1360, ["root", "santorini", "flamecraft", "mlem_space_agency"]),
]


def posicoes_fileira(nomes, h=300, x0=50):
    out, x = [], x0
    for n in nomes:
        b = caixa(n, h)
        out.append((n, x + b.width / 2, b.width))
        x += b.width - 18
    return out


@lru_cache(None)
def estante_base(faltando=()):
    """Estante cheia (com sombras e luz quente). faltando = caixas que saíram (lugar vazio)."""
    img = parede().copy()
    d = ImageDraw.Draw(img)
    for y, nomes in ESTANTE:
        for n, cx, bw in posicoes_fileira(nomes):
            if n in faltando:
                continue
            b = caixa_s(n, 300)
            img.alpha_composite(b, (int(cx - b.width / 2 + 4), int(y - 300 - 10 - 2)))
        prateleira(d, y)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((-300, -500, W + 300, 1000), fill=(255, 200, 120, 46))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(90)))
    return img


def caixa_na_estante(n):
    for y, nomes in ESTANTE:
        for m, cx, bw in posicoes_fileira(nomes):
            if m == n:
                return cx, y - 150
    raise KeyError(n)


def escurece(img, a):
    if a > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (20, 10, 5, int(170 * a))))


# ---------------------------------------------------------------- etiquetas e títulos
@lru_cache(None)
def titulo(txt, size=88, cor=WHITE, contorno=NAVY, maxw=980):
    lines = txt.split("\n")
    while max(font(LUCKY, size).getlength(l) for l in lines) > maxw - 40 and size > 30:
        size -= 4
    f = font(LUCKY, size)
    lh = int(size * 1.12)
    w = int(max(f.getlength(l) for l in lines)) + 40
    im = Image.new("RGBA", (w, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        d.text((w / 2, 20 + lh * k + lh / 2), l, font=f, fill=cor, anchor="mm", stroke_width=max(4, size // 11),
               stroke_fill=contorno)
    return sombra(im, 8, (4, 8), 0.5)


@lru_cache(None)
def kraft(txt, size=50, fundo=KRAFT, letra=INK, maxw=900):
    """Etiqueta de papel kraft com furinho (presa por barbante)."""
    lines = txt.split("\n")
    while max(font(POP, size).getlength(l) for l in lines) > maxw - size * 2 and size > 24:
        size -= 2
    f = font(POP, size)
    lh = int(size * 1.2)
    tw = int(max(f.getlength(l) for l in lines))
    w, h = tw + int(size * 1.6), lh * len(lines) + int(size * 0.9)
    im = Image.new("RGBA", (w, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((w / 2, 0, w / 2, 62), fill=(235, 225, 205), width=4)  # barbante
    d.rounded_rectangle((0, 50, w - 1, h + 49), radius=int(size * 0.3), fill=fundo)
    d.ellipse((w / 2 - 9, 58, w / 2 + 9, 76), fill=(70, 50, 35))
    for k, l in enumerate(lines):
        d.text((w / 2, 50 + size * 0.45 + lh * k + lh / 2), l, font=f, fill=letra, anchor="mm")
    return sombra(im, 8, (6, 10), 0.45)


@lru_cache(None)
def preco(txt1, txt2, cor, w=380, riscado=False):
    """Etiqueta de preço (formato de tag, com furinho)."""
    h = int(w * 0.6)
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(20, 20 + h * 0.5), (20 + h * 0.35, 20), (w + 20, 20), (w + 20, h + 20), (20 + h * 0.35, h + 20)]
    d.polygon(pts, fill=cor)
    d.ellipse((20 + h * 0.2 - 12, 20 + h * 0.5 - 12, 20 + h * 0.2 + 12, 20 + h * 0.5 + 12), fill=(0, 0, 0, 0))
    cx = 20 + h * 0.35 + (w - h * 0.35) / 2
    d.text((cx, 20 + h * 0.28), txt1, font=font(POP, int(h * 0.16)), fill=WHITE, anchor="mm")
    f2 = int(h * 0.34)
    while font(POPB, f2).getlength(txt2) > (w - h * 0.35) * 0.9:
        f2 -= 2
    d.text((cx, 20 + h * 0.64), txt2, font=font(POPB, f2), fill=WHITE, anchor="mm")
    if riscado:
        d.line((cx - w * 0.3, 20 + h * 0.82, cx + w * 0.3, 20 + h * 0.46), fill=(255, 220, 0), width=12)
    return sombra(im, 8, (6, 10), 0.45)


@lru_cache(None)
def icone(tipo, r=46, cor=ORANGE):
    """Ícones simples desenhados: relógio, livro (regras), mãos (todos jogam), coração, pessoa, risada..."""
    S = 4
    im = Image.new("RGBA", (r * 2 * S, r * 2 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    R = r * S
    d.ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=cor)
    c = R
    lw = int(R * 0.12)
    if tipo == "relogio":
        d.ellipse((c - R * 0.55, c - R * 0.55, c + R * 0.55, c + R * 0.55), outline=WHITE, width=lw)
        d.line((c, c, c, c - R * 0.38), fill=WHITE, width=lw)
        d.line((c, c, c + R * 0.28, c + R * 0.1), fill=WHITE, width=lw)
    elif tipo == "regras":
        d.rounded_rectangle((c - R * 0.45, c - R * 0.55, c + R * 0.45, c + R * 0.55), radius=R * 0.08, outline=WHITE,
                            width=lw)
        for k in range(3):
            y = c - R * 0.25 + k * R * 0.25
            d.line((c - R * 0.25, y, c + R * 0.25, y), fill=WHITE, width=lw // 2 + 2)
    elif tipo == "todos":
        for dx in (-0.32, 0.32):
            d.ellipse((c + R * dx - R * 0.17, c - R * 0.5, c + R * dx + R * 0.17, c - R * 0.16), fill=WHITE)
            d.pieslice((c + R * dx - R * 0.3, c - R * 0.1, c + R * dx + R * 0.3, c + R * 0.6), 180, 360, fill=WHITE)
    elif tipo == "coracao":
        d.ellipse((c - R * 0.5, c - R * 0.42, c + R * 0.02, c + R * 0.1), fill=WHITE)
        d.ellipse((c - R * 0.02, c - R * 0.42, c + R * 0.5, c + R * 0.1), fill=WHITE)
        d.polygon([(c - R * 0.48, c - R * 0.06), (c + R * 0.48, c - R * 0.06), (c, c + R * 0.5)], fill=WHITE)
    elif tipo == "pessoa":
        d.ellipse((c - R * 0.2, c - R * 0.55, c + R * 0.2, c - R * 0.15), fill=WHITE)
        d.pieslice((c - R * 0.4, c - R * 0.05, c + R * 0.4, c + R * 0.75), 180, 360, fill=WHITE)
    elif tipo == "risada":
        d.ellipse((c - R * 0.3, c - R * 0.3, c - R * 0.1, c - R * 0.1), fill=WHITE)
        d.ellipse((c + R * 0.1, c - R * 0.3, c + R * 0.3, c - R * 0.1), fill=WHITE)
        d.chord((c - R * 0.42, c - R * 0.15, c + R * 0.42, c + R * 0.5), 0, 180, fill=WHITE)
    elif tipo == "maos":
        d.polygon([(c - R * 0.5, c + R * 0.2), (c - R * 0.1, c - R * 0.4), (c + R * 0.1, c - R * 0.4),
                   (c + R * 0.5, c + R * 0.2), (c, c + R * 0.5)], fill=WHITE)
    elif tipo == "cerebro":
        for dx, dy in ((-0.2, -0.15), (0.2, -0.15), (-0.25, 0.15), (0.25, 0.15), (0, 0)):
            d.ellipse((c + R * (dx - 0.25), c + R * (dy - 0.22), c + R * (dx + 0.25), c + R * (dy + 0.22)),
                      fill=WHITE)
    elif tipo == "ok":
        d.line((c - R * 0.4, c, c - R * 0.1, c + R * 0.3, c + R * 0.45, c - R * 0.35), fill=WHITE, width=lw * 2,
               joint="curve")
    return sombra(im.resize((r * 2, r * 2), Image.LANCZOS), 6, (3, 6), 0.4)


def selo_tag(img, tipo, txt, x, y, t, t0, cor=ORANGE, size=46, rot=0):
    """Ícone redondo + etiqueta kraft ao lado (entra com pulinho)."""
    p = pop(t, t0)
    if p <= 0:
        return
    k = kraft(txt, size)
    cola(img, k, x + 40, y + 20, rot, p)
    cola(img, icone(tipo, 52, cor), x - k.width / 2 + 30, y + 30, 0, p)


# ---------------------------------------------------------------- cenas
SCENES = [(0.0, 7.0), (7.0, 14.0), (14.0, 20.5), (20.5, 26.0), (26.0, 32.2), (32.2, 40.0), (40.0, 49.5),
          (49.5, 56.4), (56.4, 65.4)]
CTA = len(SCENES) - 1
DUR = SCENES[-1][1]
TR = 0.35


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if a <= t < b:
            return i
    return len(SCENES) - 1


@lru_cache(None)
def caixa_velha():
    """Caixa genérica de "jogo de antigamente" (sem marca): papelão gasto com dado e tabuleiro de casinhas."""
    w, h = 520, 380
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=12, fill=(176, 160, 134))
    d.rounded_rectangle((20, 20, w - 21, h - 21), radius=8, outline=(140, 122, 96), width=6)
    rng = np.random.default_rng(4)  # manchas e desgaste
    for _ in range(60):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(4, 22)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(186, 170, 144))
    for i in range(8):  # trilha de casinhas
        x = 60 + i * 52
        d.rectangle((x, 250, x + 46, 296), fill=[(190, 70, 60), (70, 110, 160), (200, 170, 70), (90, 140, 90)][i % 4])
    d.rounded_rectangle((360, 70, 450, 160), radius=14, fill=(235, 230, 220))
    for dx, dy in ((385, 95), (425, 135), (405, 115)):
        d.ellipse((dx - 9, dy - 9, dx + 9, dy + 9), fill=(40, 40, 40))
    d.text((60, 90), "JOGO DE", font=font(POPB, 44), fill=(110, 92, 70))
    d.text((60, 140), "TABULEIRO", font=font(POPB, 44), fill=(110, 92, 70))
    im = im.resize((int(w * 1.35), int(h * 1.35)), Image.LANCZOS)
    return sombra(im, 12, (8, 14), 0.5)


def cena_gancho(img, t):
    """Estante vazia com a caixa velha → em "senta aí" a estante se enche de jogos modernos."""
    a = SCENES[0][0]
    u = t - a
    t_enche = a + 3.2
    if u < 3.2:
        img.alpha_composite(parede())
        d = ImageDraw.Draw(img)
        for y, _ in ESTANTE:
            prateleira(d, y)
        jx, jy, jr = jit(t, 1.5, 1)
        cola(img, caixa_velha(), 540 + jx, 960 - 256 - 10 + jy, -2 + jr)
        # poeirinha
        rng = np.random.default_rng(int(t * POSE))
        dd = ImageDraw.Draw(img, "RGBA")
        for _ in range(30):
            x, y = rng.uniform(200, 880), rng.uniform(500, 900)
            dd.ellipse((x, y, x + 4, y + 4), fill=(255, 240, 220, 90))
        escurece(img, 0.25)
    else:
        img.alpha_composite(parede())
        d = ImageDraw.Draw(img)
        for y, _ in ESTANTE:
            prateleira(d, y)
        # as caixas caem na estante uma a uma (12 poses/s)
        k = 0
        for r, (y, nomes) in enumerate(ESTANTE):
            for n, cx, bw in posicoes_fileira(nomes):
                t0 = t_enche + 0.12 * k
                k += 1
                if t < t0:
                    continue
                v = seg(pose(t), t0, t0 + 0.25)
                yy = lerp(y - 150 - 700, y - 150 - 12, ease(v)) - (math.sin(min(1, (t - t0 - 0.25) / 0.2) * math.pi)
                                                                   * 18 if t > t0 + 0.25 else 0)
                cola(img, caixa_s(n, 300), cx + 4, yy, (1 - v) * 8 * (1 if k % 2 else -1))
        if t >= t_enche:
            vv = ease(seg(t, t_enche, t_enche + 0.3))
            cola(img, caixa_velha(), lerp(540, -400, vv), 960 - 200 + 300 * vv, -2 - 40 * vv)
    if u < 3.2:
        cola(img, titulo("JOGO DE TABULEIRO É SÓ\nBANCO IMOBILIÁRIO?", 82), 540, 250, -2, pop(t, a + 0.0, 0.25))
    else:
        cola(img, titulo("TÁ PERDENDO\nMUITA COISA!", 104, WHITE, ORANGE_D), 540, 260, 2, pop(t, t_enche + 0.4))


def cena_modernos(img, t):
    a = SCENES[1][0]
    u = t - a
    img.alpha_composite(estante_base(("camel_up_second_edition",)))
    escurece(img, 0.6 * ease(seg(t, a, a + 0.5)))
    # o Camel Up sai da estante e vem para a frente
    x0, y0 = caixa_na_estante("camel_up_second_edition")
    v = ease(seg(t, a, a + 0.7))
    jx, jy, jr = jit(t, 2, 2)
    cola(img, caixa_s("camel_up_second_edition", 300), lerp(x0, 540, v) + jx, lerp(y0, 760, v) + jy,
         lerp(0, -5, v) + jr, lerp(1, 2.0, v))
    cola(img, titulo("JOGOS MODERNOS", 96, WHITE, ORANGE_D), 540, 210, -2, pop(t, a + 0.3))
    selo_tag(img, "regras", "REGRAS SIMPLES", 540, 1180, t, a + 1.6, BLUE, 50, balanco(t, a + 1.6, 6))
    selo_tag(img, "relogio", "PARTIDAS RÁPIDAS", 540, 1340, t, a + 2.6, ORANGE, 50, balanco(t, a + 2.6, 6))
    selo_tag(img, "todos", "NINGUÉM É ELIMINADO", 540, 1500, t, a + 3.8, GREEN, 50, balanco(t, a + 3.8, 6))


TIPOS = [("dixit", "FESTA", "risada", ORANGE), ("marvel_united", "COOPERATIVO", "maos", BLUE),
         ("root", "ESTRATÉGIA", "cerebro", GREEN)]


def tres_caixas(img, t, a, itens, ts, alturas=(380, 380, 380)):
    xs = (220, 540, 860)
    for k, ((n, txt, ic, cor), t0, hh) in enumerate(zip(itens, ts, alturas)):
        if t < t0:
            continue
        v = ease(seg(pose(t), t0, t0 + 0.4))
        jx, jy, jr = jit(t, 2, 10 + k)
        y = lerp(-400, 900, v) - (abs(math.sin((t - t0 - 0.4) * 9)) * 30 * math.exp(-(t - t0 - 0.4) * 3)
                                  if t > t0 + 0.4 else 0)
        cola(img, caixa_s(n, hh), xs[k] + jx, y + jy, [-6, 3, 7][k] + jr)
        if t >= t0 + 0.3:
            p = pop(t, t0 + 0.3)
            cola(img, icone(ic, 60, cor), xs[k], 1170, 0, p)
            cola_topo(img, kraft(txt, 34, cor, WHITE), xs[k], 1220, balanco(t, t0 + 0.3, 10), p)


def cena_tipos(img, t):
    a = SCENES[2][0]
    img.alpha_composite(estante_base(("dixit", "root")))
    escurece(img, 0.65)
    cola(img, titulo("TEM PRA TODO GOSTO", 88), 540, 220, 2, pop(t, a + 0.1))
    tres_caixas(img, t, a, TIPOS, (a + 0.4, a + 1.7, a + 3.2), (380, 340, 360))


def cena_dois(img, t):
    a = SCENES[3][0]
    img.alpha_composite(estante_base(("7_wonders_duel", "azul_duel", "flamecraft")))
    escurece(img, 0.65)
    cola(img, titulo("PRA DOIS...", 96, WHITE, (200, 40, 80)), 540, 220, -2, pop(t, a + 0.1))
    for k, (n, x, r) in enumerate((("7_wonders_duel", 330, -7), ("azul_duel", 750, 6))):
        t0 = a + 0.3 + k * 0.35
        if t >= t0:
            v = ease(seg(pose(t), t0, t0 + 0.4))
            jx, jy, jr = jit(t, 2, 20 + k)
            cola(img, caixa_s(n, 330), lerp(-300 if k == 0 else 1400, x, v) + jx, 640 + jy, r + jr)
    if t >= a + 1.0:
        cola(img, icone("coracao", 70, (220, 50, 90)), 540, 560, 0, pop(t, a + 1.0) * (1 + 0.08 * abs(math.sin(
            pose(t) * 6))))
    if t >= a + 2.4:
        cola(img, titulo("...E PRA JOGAR SOZINHO!", 72, WHITE, NAVY), 540, 1000, 2, pop(t, a + 2.4))
        v = ease(seg(pose(t), a + 2.6, a + 3.0))
        jx, jy, jr = jit(t, 2, 23)
        cola(img, caixa_s("flamecraft", 380), lerp(1400, 540, v) + jx, 1330 + jy, -4 + jr)
        if t >= a + 3.1:
            cola(img, icone("pessoa", 56, GREEN), 800, 1200, 0, pop(t, a + 3.1))


def cena_caro(img, t):
    a = SCENES[4][0]
    u = t - a
    img.alpha_composite(estante_base(("wingspan",)))
    escurece(img, 0.7)
    jx, jy, jr = jit(t, 2, 30)
    v = ease(seg(t, a, a + 0.6))
    cola(img, caixa_s("wingspan", 760), 540 + jx, lerp(1500, 860, v) + jy, -4 + jr)
    cola(img, titulo("SÓ QUE TEM UM DETALHE...", 80), 540, 220, -2, pop(t, a + 0.1))
    if u >= 2.0:
        cola(img, titulo("NA LOJA, COSTUMA\nSAIR CARO!", 84, (255, 215, 60), (120, 20, 20)), 540, 395, 2, pop(t, a + 2.0))
    if u >= 3.4:
        cola_topo(img, preco("NA LOJA", "R$ 400", GRAY, 420), 770, 1180, balanco(t, a + 3.4, 16), pop(t, a + 3.4))
        cola(img, kraft("a partir de R$ 377 nas lojas online", 30, CREAM, INK), 400, 1500, -2, pop(t, a + 3.8))


def cena_aluga(img, t):
    a = SCENES[5][0]
    u = t - a
    img.alpha_composite(estante_base(("wingspan",)))
    escurece(img, 0.7)
    jx, jy, jr = jit(t, 2, 30)
    cola(img, caixa_s("wingspan", 760), 540 + jx, 860 + jy, -4 + jr)
    cola_topo(img, preco("NA LOJA", "R$ 400", GRAY, 420, riscado=u >= 1.6), 770, 1180, balanco(t, a + 1.6, 10))
    cola(img, titulo("POR ISSO, ALUGA!", 100, WHITE, ORANGE_D), 540, 230, -2, pop(t, a + 0.1))
    if u >= 1.0:
        cola_topo(img, preco("5 DIAS", "R$ 45", ORANGE, 440), 330, 1260, balanco(t, a + 1.0, 18), pop(t, a + 1.0))
    if u >= 4.2:
        cola(img, kraft("GOSTOU? AÍ VOCÊ COMPRA\nSEM MEDO DE ERRAR!", 46, (40, 140, 70), WHITE), 540, 400, 2,
             pop(t, a + 4.2))
        cola(img, icone("ok", 60, GREEN), 880, 330, 0, pop(t, a + 4.5))


DEGRAUS = [(3, 7, BLUE), (5, 10, ORANGE), (7, 15, GREEN)]
PILHA = ["wingspan", "hot_streak", "ticket_to_ride", "dixit", "root", "nekojima", "camel_up_second_edition"]


@lru_cache(None)
def degrau(k):
    """Coluna da promoção: barra colorida com "N JOGOS / D DIAS" (as caixas vão por cima, empilhadas)."""
    jogos, dias, cor = DEGRAUS[k]
    w, h = 290, int(400 + 130 * k)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h + 40), radius=36, fill=cor)
    d.text((w / 2, 60), f"{jogos} JOGOS", font=font(POP, 46), fill=WHITE, anchor="mm")
    d.line((w * 0.2, 105, w * 0.8, 105), fill=WHITE + (150,), width=4)
    d.text((w / 2, h * 0.5 + 40), str(dias), font=font(POPB, 150), fill=WHITE, anchor="mm")
    d.text((w / 2, h - 60), "DIAS", font=font(POPB, 54), fill=WHITE, anchor="mm")
    return sombra(im, 12, (8, 14), 0.5)


def pilha_caixas(img, n, x, base, t, t0):
    """Leque de caixas caindo uma a uma em cima do degrau (stop motion)."""
    passo = 200 / max(1, n - 1)
    for i in range(n):
        ti = t0 + 0.09 * i
        if t < ti:
            break
        v = ease(seg(pose(t), ti, ti + 0.2))
        nome = PILHA[i % len(PILHA)]
        b = caixa_s(nome, 150) if nome != "hot_streak" else caixa_s(nome, 90)
        xi = x - 100 + i * passo if n > 1 else x
        y = base - 70 - abs(i - (n - 1) / 2) * -6
        cola(img, b, xi, lerp(y - 500, y, v), (i - (n - 1) / 2) * -5)


def cena_progressivo(img, t):
    a = SCENES[6][0]
    u = t - a
    img.alpha_composite(estante_base())
    escurece(img, 0.78)
    cola(img, titulo("QUANTO MAIS JOGOS,\nMAIS DIAS!", 92, WHITE, ORANGE_D), 540, 270, -2, pop(t, a + 0.1))
    chao = 1390
    for k, t0 in enumerate((a + 1.4, a + 3.2, a + 4.6)):
        if t < t0:
            continue
        x = 220 + k * 320
        g = degrau(k)
        v = out_back(seg(pose(t), t0, t0 + 0.4)) if t < t0 + 0.4 else 1.0
        topo = chao - (g.height - 70) * v
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lay.alpha_composite(g, (int(x - g.width / 2), int(topo - 35)))
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rectangle((0, 0, W, chao), fill=255)
        lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(m))))
        img.alpha_composite(lay)
        if t >= t0 + 0.4:
            pilha_caixas(img, DEGRAUS[k][0], x, chao - (g.height - 70), t, t0 + 0.4)
    d = ImageDraw.Draw(img)
    d.rectangle((40, chao, W - 40, chao + 14), fill=(156, 104, 62))
    if u >= 6.4:
        cola(img, kraft("PELO MESMO PREÇO!", 54, ORANGE, WHITE), 540, 1470, -2, pop(t, a + 6.4))
    if u >= 7.6:
        cola(img, kraft("ex.: 3 jogos por R$ 120 = 7 dias", 34, CREAM, INK), 540, 1560, 2, pop(t, a + 7.6))


@lru_cache(None)
def parede_cheia():
    """Parede inteira de estantes (acervo), com as caixas pequenas repetidas."""
    img = parede().copy()
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for r in range(8):
        y = 300 + r * 230
        x = 20 + rng.uniform(-40, 0)
        while x < W:
            n = TODAS[int(rng.integers(len(TODAS)))]
            b = caixa_s(n, 180)
            img.alpha_composite(b, (int(x), int(y - 180 - 18)))
            x += caixa(n, 180).width - 8
        prateleira(d, y)
    return img


def cena_acervo(img, t):
    a = SCENES[7][0]
    u = t - a
    z = lerp(1.25, 1.0, ease(seg(t, a, a + 1.2)))
    pc = parede_cheia()
    if z > 1.001:
        pc = pc.resize((int(W * z), int(H * z)), Image.BICUBIC)
        pc = pc.crop(((pc.width - W) // 2, (pc.height - H) // 2, (pc.width - W) // 2 + W, (pc.height - H) // 2 + H))
    img.alpha_composite(pc)
    escurece(img, 0.35 + 0.3 * seg(t, a + 2.4, a + 2.8))
    n = int(lerp(0, 160, ease(seg(t, a + 0.2, a + 1.6))))
    cola(img, titulo(f"+ DE {n} JOGOS", 120, WHITE, ORANGE_D), 540, 330, -2, pop(t, a + 0.2))
    cola(img, kraft("NO ACERVO DA SUA VEZ", 50), 540, 480, 2, pop(t, a + 0.8))
    if u >= 2.6:
        cola(img, titulo("QUAL DESSES VOCÊ\nJOGARIA PRIMEIRO?", 84), 540, 1050, 2, pop(t, a + 2.6))
    if u >= 4.6:
        b = 1 + 0.05 * abs(math.sin(pose(t) * 6))
        cola(img, kraft("COMENTA AQUI!", 80, ORANGE, WHITE), 540, 1380, -3, pop(t, a + 4.6) * b)


def cena_cta(img, t):
    a = SCENES[CTA][0]
    img.alpha_composite(estante_base())
    escurece(img, 0.8)
    cola(img, logo_card(470), 540, 230, 0, pop(t, a + 0.1))
    for k, (n, x, y, r) in enumerate((("wingspan", 300, 700, -8), ("hot_streak", 760, 760, 6),
                                      ("ticket_to_ride", 540, 690, 0))):
        t0 = a + 0.4 + k * 0.2
        if t >= t0:
            v = ease(seg(pose(t), t0, t0 + 0.35))
            jx, jy, jr = jit(t, 1.5, 40 + k)
            cola(img, caixa_s(n, 360 if n != "hot_streak" else 200), x + jx, lerp(-300, y, v) + jy, r + jr)
    if t >= a + 1.2:
        cola(img, titulo("ALUGUE JOGOS NA SUA VEZ!", 80, WHITE, ORANGE_D), 540, 980, -2, pop(t, a + 1.2))
    if t >= a + 1.7:
        cola(img, kraft("+160 JOGOS", 44), 300, 1110, -3, pop(t, a + 1.7))
    if t >= a + 2.0:
        cola(img, kraft("5 DIAS DE JOGO", 44, ORANGE, WHITE), 770, 1110, 3, pop(t, a + 2.0))
    if t >= a + 2.4:
        cola(img, kraft("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 38, CREAM, INK), 540, 1240, -1, pop(t, a + 2.4))
    if t >= a + 2.8:
        cola(img, kraft("OU RECEBA EM CASA!", 40, (40, 140, 70), WHITE), 540, 1350, 2, pop(t, a + 2.8))
    if t >= a + 3.3:
        b = 1 + 0.04 * abs(math.sin(pose(t) * 5))
        cola(img, kraft("LINK NA BIO · @SUAVEZ_BG", 58, ORANGE, WHITE), 540, 1480, -2, pop(t, a + 3.3) * b)


CENAS = [cena_gancho, cena_modernos, cena_tipos, cena_dois, cena_caro, cena_aluga, cena_progressivo, cena_acervo,
         cena_cta]


def frame_at(t):
    i = scene_of(t)
    img = Image.new("RGBA", (W, H), (40, 25, 16, 255))
    CENAS[i](img, t)
    a, b = SCENES[i]
    # transição: "piscada" de luz quente entre as cenas
    f = 0.0
    if i > 0 and t < a + TR / 2:
        f = 1 - (t - a) / (TR / 2)
    if i < len(SCENES) - 1 and t > b - TR / 2:
        f = (t - (b - TR / 2)) / (TR / 2)
    if f > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 236, 205, int(200 * f))))
    return img


# ---------------------------------------------------------------- narração, legendas e render
TIMELINE_PATH = os.path.join(ROOT, "narracao", "timeline.json")
TIMELINE = json.load(open(TIMELINE_PATH, encoding="utf-8")) if os.path.exists(TIMELINE_PATH) else None
ROTEIRO = [
    "Jogo de tabuleiro é só Banco Imobiliário e Detetive? Então senta aí, que você tá perdendo muita coisa!",
    "Os jogos modernos são outra coisa: regras simples, partidas rápidas, e ninguém fica eliminado esperando a vez.",
    "Tem jogo de festa pra dar risada, cooperativo pra jogar junto, e estratégia pra quem gosta de pensar.",
    "Tem até jogo pra dois, perfeito pro casal... e jogo pra jogar sozinho.",
    "Só que os jogos modernos costumam ser caros: um Wingspan, por exemplo, sai por uns 400 reais na loja.",
    "Por isso alugar faz tanto sentido: na Sua Vez, ele sai por 45 reais, com 5 dias pra jogar. Gostou? Aí você compra sem medo de errar.",
    "E quanto mais jogos, mais dias: 3 jogos, 7 dias. 5, 10. E 7 jogos, 15 dias, pelo mesmo preço!",
    "São mais de 160 jogos no acervo. E aí, qual desses você jogaria primeiro? Comenta aqui!",
    "Reserva online, retira em Mauá ou recebe em casa: aluga na Sua Vez, o link tá na bio!",
]


def default_subs():
    """Legendas do roteiro distribuídas pela cena (prévia sem voz)."""
    out = []
    for (a, b), txt in zip(SCENES, ROTEIRO):
        chunks, cur = [], []
        for w in txt.split():
            cur.append(w)
            if len(" ".join(cur)) > 34 or w[-1] in ".?!:":
                chunks.append(" ".join(cur))
                cur = []
        if cur:
            chunks.append(" ".join(cur))
        span = (b - a - 0.6) / len(chunks)
        for k, ch in enumerate(chunks):
            out.append((a + 0.3 + k * span, a + 0.3 + (k + 1) * span, ch))
    return out


SUBS = default_subs()
if TIMELINE:
    DUR = TIMELINE["duracao"]
    SUBS = [tuple(x) for x in TIMELINE["legendas"]]


def to_orig(t):
    if TIMELINE is None:
        return t
    for o0, o1, n0, n1 in TIMELINE["cenas"]:
        if n0 <= t < n1:
            return o0 + (t - n0) * (o1 - o0) / (n1 - n0)
    o0, o1, n0, n1 = TIMELINE["cenas"][-1]
    return o0 + (t - n0) * (o1 - o0) / (n1 - n0)


def warp(t_orig):
    if TIMELINE is None:
        return t_orig
    for o0, o1, n0, n1 in TIMELINE["cenas"]:
        if o0 <= t_orig < o1:
            return n0 + (t_orig - o0) * (n1 - n0) / (o1 - o0)
    return t_orig


def _cues():
    S = [s[0] for s in SCENES]
    c = [(0.0, "pop", 0.4), (3.2, "swoosh", 0.6)] + [(3.2 + 0.12 * k + 0.25, "caixa", 0.45) for k in range(12)]
    c += [(3.6, "pop", 0.5)]
    c += [(S[1], "swoosh", 0.5), (S[1] + 0.3, "pop", 0.4)] + [(S[1] + x, "papel", 0.6) for x in (1.6, 2.6, 3.8)]
    c += [(S[2] + 0.1, "pop", 0.4)] + [(S[2] + x + 0.4, "caixa", 0.7) for x in (0.4, 1.7, 3.2)]
    c += [(S[2] + x + 0.3, "papel", 0.5) for x in (0.4, 1.7, 3.2)]
    c += [(S[3] + 0.1, "pop", 0.4), (S[3] + 0.7, "caixa", 0.6), (S[3] + 1.05, "caixa", 0.6), (S[3] + 1.0, "ding", 0.4),
          (S[3] + 2.4, "pop", 0.4), (S[3] + 3.0, "caixa", 0.6)]
    c += [(S[4], "swoosh", 0.6), (S[4] + 0.1, "pop", 0.3), (S[4] + 2.0, "pop", 0.5), (S[4] + 3.4, "papel", 0.7)]
    c += [(S[5] + 0.1, "pop", 0.5), (S[5] + 1.0, "papel", 0.7), (S[5] + 1.6, "flip", 0.6), (S[5] + 2.0, "cash", 0.8),
          (S[5] + 4.2, "pop", 0.5), (S[5] + 4.5, "ding", 0.5)]
    c += [(S[6] + 0.1, "pop", 0.5)] + [(S[6] + x + 0.3, "caixa", 0.7) for x in (1.4, 3.2, 4.6)]
    c += [(S[6] + x + 0.35, "ding", 0.35 + 0.1 * k) for k, x in enumerate((1.4, 3.2, 4.6))]
    c += [(S[6] + 6.4, "cash", 0.7), (S[6] + 7.6, "pop", 0.4)]
    c += [(S[7], "swoosh", 0.5)] + [(S[7] + 0.2 + k * 0.1, "tick", 0.3) for k in range(14)]
    c += [(S[7] + 2.6, "pop", 0.5), (S[7] + 4.6, "pop", 0.6), (S[7] + 4.7, "crowd", 0.35)]
    c += [(S[8] + 0.1, "pop", 0.5)] + [(S[8] + 0.75 + k * 0.2, "caixa", 0.6) for k in range(3)]
    c += [(S[8] + x, "papel", 0.5) for x in (1.2, 1.7, 2.0, 2.4, 2.8)] + [(S[8] + 3.3, "cash", 0.6)]
    return c


CUES = _cues()


@lru_cache(None)
def sub_img(text):
    f = font(POP, 48)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        tst = (cur + " " + w_).strip()
        if f.getlength(tst) > 920 and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = tst
    lines.append(cur)
    lh = 60
    w = int(max(f.getlength(l) for l in lines)) + 50
    h = lh * len(lines) + 24
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=(0, 0, 0, 200))
    for k, l in enumerate(lines):
        d.text((w / 2, 12 + lh * k + lh / 2), l, font=f, fill=WHITE, anchor="mm")
    return im


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    to = to_orig(t)
    img = frame_at(to)
    if scene_of(to) < CTA:
        wm = logo_card(180)
        img.alpha_composite(wm, (W - wm.width - 30, 40))
    if subs:
        for a_, b_, s in SUBS:
            if a_ <= t < b_:
                si = sub_img(s)
                img.alpha_composite(si, ((W - si.width) // 2, 1740 - si.height // 2))
    return img.convert("RGB").tobytes()


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def encode(out_path, wav, n, args):
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, fr in enumerate(pool.imap(render_frame, args, chunksize=6)):
            p.stdin.write(fr)
            if k % 300 == 0:
                print(f"  quadro {k}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("ok:", out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--only", choices=["preview", "limpo"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [Image.frombytes("RGB", (W, H), render_frame((int(round(x * FPS)), True))) for x in a.frame]
        cols = min(6, len(ims))
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (360 * cols, 640 * rows))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
        sheet.save(os.path.join(OUT, "frames.jpg"), quality=88)
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz, cues=CUES)
    n = int(DUR * FPS)
    if a.only != "limpo":
        encode(os.path.join(OUT, "hobby_preview.mp4"), wav, n, [(j, True) for j in range(n)])
    if a.only != "preview":
        encode(os.path.join(OUT, "hobby_limpo.mp4"), wav, n, [(j, False) for j in range(n)])


if __name__ == "__main__":
    main()
