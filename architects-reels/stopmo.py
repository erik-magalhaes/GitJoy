#!/usr/bin/env python3
"""Reels do 7 Wonders Arquitetos em stop motion de recortes — Sua Vez Locação de Jogos.

Peças oficiais do jogo (kit de imprensa da Repos/Galápagos) animadas quadro a quadro a 12 poses
por segundo, com o "tremidinho" de quem reposiciona cada peça com a mão. A maravilha de Éfeso é
montada em obras e cada etapa vira a peça para o lado construído, como no jogo.

    python3 stopmo.py --frame 12.3 20 31   # quadros de teste (out/frames.jpg)
    python3 stopmo.py --only preview       # prévia com legendas
    python3 stopmo.py                      # com e sem legendas
"""
import argparse
import json
import math
import os
import subprocess
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
import trilha_arq as som  # noqa: E402

OF = os.path.join(ROOT, "assets", "oficial")
PE = os.path.join(ROOT, "assets", "pecas")
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
FPS = 12
DUR = 66.0

CREAM = (255, 244, 220)
GOLD = (255, 200, 60)
RED = (232, 56, 50)
BLUE = (70, 160, 240)
GREEN = (110, 200, 70)
INK = (22, 24, 40)
WHITE = (255, 255, 255)


# ---------------------------------------------------------------- utilidades
def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def ease_out(u):
    return 1 - (1 - u) ** 2


def lerp(a, b, u):
    return a + (b - a) * u


POP = [0.25, 0.75, 1.22, 1.08, 0.95, 1.0]


def pop(t, t0):
    """Escala de entrada em poucas poses, como um recorte colocado na mesa."""
    if t < t0:
        return None
    k = int((t - t0) * FPS)
    return POP[k] if k < len(POP) else 1.0


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


LUCKY = "LuckiestGuy-Regular.ttf"
POPPINS = "Poppins-ExtraBold.ttf"


@lru_cache(None)
def piece(name):
    d = OF if os.path.exists(os.path.join(OF, name)) else PE
    return Image.open(os.path.join(d, name)).convert("RGBA")


@lru_cache(None)
def by_h(name, h):
    im = piece(name)
    return im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)


@lru_cache(None)
def by_w(name, w):
    im = piece(name)
    return im.resize((int(w), max(2, int(im.height * w / im.width))), Image.LANCZOS)


class Ctx:
    def __init__(self, fi):
        self.fi = fi
        self.t = fi / FPS
        self.rng = np.random.default_rng(fi * 7919 + 17)

    def j(self, a):
        return float(self.rng.uniform(-a, a))


def place(canvas, ctx, im, x, y, rot=0.0, sc=1.0, sx=1.0, lift=0.0, shadow=0.55, alpha=1.0, jitter=1.0):
    """Cola um recorte com sombra e o erro de posicionamento da mão."""
    if im is None or sc is None or sc <= 0.02 or abs(sx) < 0.03:
        return
    x += ctx.j(2.0 * jitter)
    y += ctx.j(2.0 * jitter)
    rot += ctx.j(0.8 * jitter)
    w = max(2, int(im.width * sc * abs(sx)))
    h = max(2, int(im.height * sc))
    if (w, h) != im.size:
        im = im.resize((w, h), Image.BICUBIC)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    a = im.getchannel("A")
    if alpha < 1.0:
        a = a.point(lambda v: int(v * alpha))
        im.putalpha(a)
    px, py = int(x - im.width / 2), int(y - im.height / 2)
    if shadow > 0:
        blur = 7 + lift * 0.05
        op = shadow * alpha * max(0.25, 1 - lift / 500)
        pad = int(blur * 2 + 4)
        sm = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
        sm.paste(a.point(lambda v: int(v * op)), (pad, pad))
        sm = sm.filter(ImageFilter.GaussianBlur(blur))
        ox, oy = int(10 + lift * 0.3), int(16 + lift * 0.7)
        canvas.paste((6, 6, 12), (px - pad + ox, py - pad + oy), sm)
    canvas.paste(im, (px, py), im)


def hop(u, p0, p1, height):
    """Caminho de uma peça levantada pela mão e assentada de novo (sobe, viaja, desce)."""
    e = ease(u)
    x, y = lerp(p0[0], p1[0], e), lerp(p0[1], p1[1], e)
    lift = math.sin(math.pi * e) * height
    return x, y - lift, lift


def flip_sx(t, t0, poses=4):
    """Virar uma peça: some na lateral em `poses` poses e volta mostrando o outro lado."""
    k = (t - t0) * FPS
    if k < 0:
        return 1.0, False
    if k >= poses * 2:
        return 1.0, True
    seq = [0.75, 0.4, 0.12, 0.05][:poses]
    i = int(k)
    return (seq[i] if i < poses else seq[poses * 2 - 1 - i]), i >= poses


# ---------------------------------------------------------------- adesivos de texto (recorte de papel)
def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return "\n".join(lines)


@lru_cache(None)
def sticker(text, size=92, color=CREAM, maxw=930, ink=INK, paper=(255, 255, 255)):
    fnt = font(LUCKY, size)
    txt = wrap(text, fnt, maxw)
    s1 = max(4, size // 11)
    s2 = s1 + max(6, size // 7)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    bb = d.multiline_textbbox((0, 0), txt, font=fnt, align="center", spacing=8, stroke_width=s2)
    bb = [int(math.floor(bb[0])), int(math.floor(bb[1])), int(math.ceil(bb[2])), int(math.ceil(bb[3]))]
    pad = 10
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    org = (pad - bb[0], pad - bb[1])

    def mask(stroke):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).multiline_text(org, txt, font=fnt, fill=255, align="center", spacing=8,
                                         stroke_width=stroke, stroke_fill=255)
        return m

    m2 = mask(s2).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", (w, h), paper + (0,))
    out.putalpha(m2)
    out.paste(Image.new("RGBA", (w, h), ink + (255,)), (0, 0), mask(s1))
    out.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), mask(0))
    return out


@lru_cache(None)
def logo_suavez(width):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2,
                                           fill=(255, 255, 255, 255))
    card.alpha_composite(lg, (pad, pad))
    return card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)


@lru_cache(None)
def watermark():
    im = logo_suavez(200).copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * 0.7)))
    return im


# ---------------------------------------------------------------- fundos
@lru_cache(None)
def bg_mesa():
    """Pano escuro de mesa de jogo, com textura e luz de abajur no centro."""
    rng = np.random.default_rng(5)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((x - W * 0.5) / W, (y - H * 0.45) / H)
    base = np.array((62, 64, 80), np.float32) * (1.25 - 0.9 * r[..., None] ** 1.6)
    fib = rng.normal(0, 1, (H // 3, W // 3)).astype(np.float32)
    fib = np.asarray(Image.fromarray(((fib + 4) * 30).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                     np.float32) / 30 - 4
    base += fib[..., None] * 2.2 + rng.normal(0, 2.0, (H, W, 1))
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


@lru_cache(None)
def bg_capa():
    im = Image.open(os.path.join(ROOT, "assets", "fotos", "capa.jpg")).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x0 = (im.width - W) // 2
    im = im.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(9))
    a = np.asarray(im, np.float32) * np.array([0.40, 0.42, 0.52])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- maravilha de Éfeso
EF = json.load(open(os.path.join(OF, "efeso.json")))
EF_W, EF_H = EF["tamanho"]
# o lado construído é o verso da peça: a coluna da esquerda em obras vira a da direita construída
VERSO = {"1": "1", "2": "4", "3": "3", "4": "2", "5": "5"}


def efeso(canvas, ctx, cx, cy, width, t, chegada=None, builds=None, alpha=1.0):
    """Desenha a maravilha. chegada[k] = instante em que a peça k entra; builds[k] = instante em que vira."""
    s = width / EF_W
    x0, y0 = cx - width / 2, cy - EF_H * s / 2
    for k in ("1", "2", "3", "4", "5"):
        px, py, pw, ph = EF["pecas"][k]
        tx, ty = x0 + (px + pw / 2) * s, y0 + (py + ph / 2) * s
        if chegada and k in chegada:
            t0 = chegada[k]
            if t < t0:
                continue
            u = seg(t, t0, t0 + 0.5)
            start = (tx + (-700 if k in "12" else 700 if k in "4" else 0), ty + (900 if k in "13" else -900))
            x, y, lift = hop(u, start, (tx, ty), 160)
        else:
            x, y, lift = tx, ty, 0
        tb = builds.get(k) if builds else None
        sx, built = (1.0, False) if tb is None else flip_sx(t, tb)
        if built:
            qx, qy, qw, qh = EF["pecas"][VERSO[k]]
            im = by_w(f"efeso_pronto_{VERSO[k]}.png", max(2, int(qw * s)))
        else:
            im = by_w(f"efeso_obra_{k}.png", max(2, int(pw * s)))
        place(canvas, ctx, im, x, y, sx=sx, lift=lift + (40 if sx < 1 else 0), alpha=alpha, jitter=0.6)


def dust(canvas, ctx, t, t0, x, y, spread):
    u = (t - t0) / 1.0
    if not 0 <= u < 1:
        return
    d = ImageDraw.Draw(canvas, "RGBA")
    rng = np.random.default_rng(int(t0 * 100))
    for k in range(14):
        ang = rng.uniform(math.pi * 1.05, math.pi * 1.95)
        dist = spread * rng.uniform(0.3, 1.0) * ease_out(min(1, u * 1.5))
        px = x + math.cos(ang) * dist * (1 if k % 2 else -1)
        py = y + math.sin(ang) * dist * 0.3 - u * 50
        r = rng.uniform(14, 30) * (0.6 + u) + ctx.j(2)
        d.ellipse((px - r, py - r, px + r, py + r), fill=(236, 226, 206, int(150 * (1 - u))))


# ---------------------------------------------------------------- linha do tempo original (antes da narração)
SCENES = [(0.0, 6.0), (6.0, 12.5), (12.5, 20.0), (20.0, 27.0), (27.0, 35.0), (35.0, 43.0),
          (43.0, 51.0), (51.0, 58.5), (58.5, 66.0)]

# adesivos: (t0, texto, tamanho, cor, x, y, rot[, t1])
STK = [
    (0.4, "CONSTRUIR UMA MARAVILHA DO MUNDO...", 74, CREAM, 540, 330, -2),
    (1.6, "EM 25 MINUTOS?!", 120, GOLD, 540, 520, 2),
    (4.4, "2 A 7 JOGADORES", 62, CREAM, 540, 1560, -2),
    (7.0, "CADA JOGADOR CONSTRÓI UMA MARAVILHA", 60, CREAM, 540, 1480, -1, 10.5),
    (10.6, "MAIS PONTOS NO FINAL VENCE!", 64, GOLD, 540, 1480, 2),
    (12.7, "NA SUA VEZ: PEGUE 1 CARTA!", 64, CREAM, 540, 320, -2),
    (13.6, "ESQUERDA", 46, CREAM, 200, 1050, -3),
    (13.8, "MEIO", 46, CREAM, 540, 1050, 2),
    (14.0, "DIREITA", 46, CREAM, 880, 1050, -2),
    (18.2, "SEM VER!", 70, GOLD, 560, 600, -10),
    (20.2, "CINZAS = MATERIAIS", 88, CREAM, 540, 320, -2),
    (24.9, "CORINGA!", 84, GOLD, 790, 1380, -10),
    (25.5, "O OURO VALE QUALQUER UM", 46, CREAM, 790, 1505, 2),
    (27.2, "JUNTOU? CONSTRÓI!", 96, CREAM, 540, 320, -2),
    (28.4, "2 DIFERENTES", 64, GOLD, 540, 1500, 2, 31.0),
    (30.2, "+3!", 110, GOLD, 860, 1240, 8, 31.4),
    (31.2, "2 IGUAIS", 64, GOLD, 540, 1500, -2, 33.4),
    (32.8, "PODER ESPECIAL!", 62, GOLD, 830, 900, 6),
    (33.6, "CADA ETAPA = PONTOS + PODER", 52, CREAM, 540, 1500, 0),
    (35.1, "VERMELHAS = ESCUDOS", 84, CREAM, 540, 320, -2),
    (37.3, "CORNETA? A FICHA VIRA!", 46, CREAM, 300, 1140, -2),
    (39.6, "GUERRA!", 170, RED, 540, 1240, -6, 40.9),
    (40.9, "VOCÊ: 3 ESCUDOS", 50, GOLD, 300, 1500, -3),
    (41.2, "VIZINHO: 1", 50, CREAM, 800, 1500, 3),
    (41.8, "+3!", 110, GOLD, 560, 1330, 8),
    (43.1, "VERDES = CIÊNCIA", 90, CREAM, 540, 320, -2, 47.0),
    (45.8, "FICHA DE PROGRESSO!", 56, GOLD, 760, 1420, 3, 47.0),
    (47.1, "AZUIS = PONTOS", 96, CREAM, 540, 320, 2),
    (48.8, "MIAU!", 70, GOLD, 900, 560, 10),
    (49.2, "O GATO ESPIA O MONTE DO MEIO", 52, CREAM, 540, 1500, -2),
    (51.1, "TERMINOU A MARAVILHA?", 80, CREAM, 540, 320, -2, 54.3),
    (52.6, "FIM DE JOGO!", 120, GOLD, 540, 1290, -4, 54.3),
    (53.3, "MAIS PONTOS VENCE!", 64, CREAM, 540, 1460, 2, 54.3),
    (54.4, "QUAL MARAVILHA VOCÊ CONSTRUIRIA?", 84, CREAM, 540, 400, -2),
    (56.6, "COMENTA AQUI!", 110, GOLD, 540, 1440, -3),
    (59.6, "ALUGUE O 7 WONDERS ARQUITETOS!", 76, GOLD, 540, 760, -2),
    (60.6, "2 A 7 JOGADORES", 48, CREAM, 790, 1010, 3),
    (61.0, "UNS 25 MIN", 48, CREAM, 790, 1120, -2),
    (61.4, "5 DIAS DE JOGO", 48, GOLD, 790, 1230, 2),
    (62.0, "RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 44, CREAM, 540, 1400, -1),
    (62.6, "LINK NA BIO · @SUAVEZ_BG", 66, GOLD, 540, 1520, 1),
]
NOMES = [("GIZÉ", 230, 700, -6), ("BABILÔNIA", 720, 680, 5), ("ÉFESO", 330, 860, 4), ("RODES", 780, 860, -5),
         ("OLÍMPIA", 250, 1030, 3), ("ALEXANDRIA", 700, 1040, -3), ("HALICARNASSO", 540, 1210, 2)]
NOME_COR = [GOLD, GREEN, RED, BLUE, CREAM, BLUE, GOLD]


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if a <= t < b:
            return i
    return len(SCENES) - 1


def draw_stickers(canvas, ctx, t, i):
    a, b = SCENES[i]
    for e in STK:
        t0, txt, size, col, x, y, rot = e[:7]
        t1 = e[7] if len(e) > 7 else b
        if a <= t0 < b and t0 <= t < t1:
            place(canvas, ctx, sticker(txt, size, col), x, y, rot, pop(t, t0), shadow=0.6)


# ---------------------------------------------------------------- cenas
def deck(canvas, ctx, x, y, h, top, under="carta_verso_efeso.png", n=3, rot=0.0):
    for k in range(n, 0, -1):
        place(canvas, ctx, by_h(under, h), x + k * 4, y + k * 6, rot, shadow=0.35 if k == n else 0, jitter=0.3)
    if top:
        place(canvas, ctx, by_h(top, h), x, y, rot, shadow=0.2, jitter=0.6)


def s0(c, ctx, t):
    place(c, ctx, by_h("caixa3d.png", 880), 540, 1080, -2, pop(t, 0.2), shadow=0.7)
    for k, (name, x, y, r) in enumerate((("carta_vermelha.png", 170, 1380, -14), ("carta_azul.png", 910, 1370, 12),
                                         ("carta_verde.png", 150, 820, -10))):
        place(c, ctx, by_h(name, 330), x, y, r, pop(t, 3.2 + k * 0.3))


def s1(c, ctx, t):
    place(c, ctx, by_w("logo_jogo.png", 860), 540, 330, 0, pop(t, 6.1), shadow=0.5)
    efeso(c, ctx, 540, 940, 840, t, chegada={"1": 6.9, "2": 7.3, "3": 7.7, "4": 8.1, "5": 8.6})


DK = {"esq": (200, 790), "meio": (540, 790), "dir": (880, 790)}


def s2(c, ctx, t):
    if t >= 14.0:
        deck(c, ctx, *DK["esq"], 360, "carta_vermelha.png" if t < 15.9 else "carta_pedra.png", rot=-3)
    if t >= 14.2:
        deck(c, ctx, *DK["meio"], 360, None, under="carta_verso.png", n=4)
        if t < 18.8:
            place(c, ctx, by_h("carta_verso.png", 360), *DK["meio"], 0, shadow=0.2, jitter=0.6)
    if t >= 14.4:
        deck(c, ctx, *DK["dir"], 360, "carta_azul.png", rot=3)
    if t >= 15.9:  # pega a de cima da esquerda
        u = seg(t, 15.9, 16.6)
        x, y, lift = hop(u, DK["esq"], (360, 1330), 200)
        place(c, ctx, by_h("carta_vermelha.png", int(lerp(360, 300, u))), x, y, lerp(-3, -9, u), lift=lift)
    if 16.8 <= t < 17.8 and int((t - 16.8) * FPS) % 4 < 2:  # mostra a da direita
        place(c, ctx, by_h("carta_azul.png", 380), DK["dir"][0], DK["dir"][1] - 20, 3, lift=60)
    if t >= 18.8:  # a do meio, sem ver: vira no caminho
        u = seg(t, 18.8, 19.6)
        x, y, lift = hop(u, DK["meio"], (720, 1330), 220)
        sx, flipped = flip_sx(t, 19.0)
        name = "carta_pedra.png" if flipped else "carta_verso.png"
        place(c, ctx, by_h(name, int(lerp(360, 300, u))), x, y, lerp(0, 8, u), sx=sx, lift=lift)


MATS = [("ic_pedra.png", "PEDRA"), ("ic_madeira.png", "MADEIRA"), ("ic_tijolo.png", "TIJOLO"),
        ("ic_papiro.png", "PAPIRO"), ("ic_vidro.png", "VIDRO")]
MAT_XY = [(140, 600), (340, 545), (540, 525), (740, 545), (940, 600)]


def s3(c, ctx, t):
    if t >= 20.4:
        u = seg(t, 20.4, 21.0)
        x, y, lift = hop(u, (-250, 1100), (320, 1040), 120)
        place(c, ctx, by_h("carta_pedra.png", 640), x, y, -4, lift=lift)
    for k, ((name, lab), (x, y)) in enumerate(zip(MATS, MAT_XY)):
        s = pop(t, 21.0 + k * 0.55)
        place(c, ctx, by_h(name, 160), x, y, 0, s)
        place(c, ctx, sticker(lab, 34), x, y + 112, 0, s, shadow=0.4)
    if t >= 24.2:
        u = seg(t, 24.2, 24.8)
        x, y, lift = hop(u, (1350, 1100), (790, 1040), 120)
        place(c, ctx, by_h("carta_ouro.png", 640), x, y, 6, lift=lift)


B1, B2 = 29.8, 32.4  # etapas construídas na explicação
FIM = {"2": 51.5, "3": 51.95, "5": 52.4}


def s4(c, ctx, t):
    builds = {"1": B1, "4": B2}
    efeso(c, ctx, 540, 900, 900, t, builds=builds)
    s = 900 / EF_W
    y0 = 900 - EF_H * s / 2
    for tb, key in ((B1, "1"), (B2, "4")):
        px, py, pw, ph = EF["pecas"][key]
        dust(c, ctx, t, tb + 0.4, 540 - 450 + (px + pw / 2) * s, y0 + (py + ph) * s, pw * s * 0.6)
    # 2 diferentes (pedra + madeira) → escada; 2 iguais (tijolo + tijolo) → coluna "2="
    px, py, pw, ph = EF["pecas"]["1"]
    alvo1 = (540, y0 + (py + ph / 2) * s)
    px, py, pw, ph = EF["pecas"]["4"]
    alvo2 = (540 - 450 + (px + pw / 2) * s, y0 + (py + ph / 2) * s)
    for k, (name, x0) in enumerate((("ic_pedra.png", 200), ("ic_madeira.png", 880))):
        if 28.6 <= t < B1:
            u = seg(t, 29.0, 29.7)
            x, y, lift = hop(u, (x0, 1330), (alvo1[0] + (k - 0.5) * 120, alvo1[1]), 140)
            place(c, ctx, by_h(name, 150), x, y, 0, pop(t, 28.6), lift=lift)
    for k, x0 in enumerate((200, 880)):
        if 31.3 <= t < B2:
            u = seg(t, 31.6, 32.3)
            x, y, lift = hop(u, (x0, 1330), (alvo2[0], alvo2[1] + (k - 0.5) * 110), 140)
            place(c, ctx, by_h("ic_tijolo.png", 150), x, y, 0, pop(t, 31.3), lift=lift)


def s5(c, ctx, t):
    if t >= 35.3:
        u = seg(t, 35.3, 35.9)
        x, y, lift = hop(u, (-250, 820), (300, 800), 120)
        place(c, ctx, by_h("carta_vermelha.png", 600), x, y, -5, lift=lift)
    for k, tf in enumerate((37.6, 38.3, 39.0)):
        y = 600 + k * 250
        s = pop(t, 35.9 + k * 0.2)
        if s is None:
            continue
        sx, flipped = flip_sx(t, tf)
        name = "conflito_guerra.png" if flipped else "conflito_paz.png"
        place(c, ctx, by_h(name, 220), 820, y, 0, s, sx=sx, lift=50 if sx < 1 else 0)
    if t >= 41.4:  # fichas de vitória militar vêm pra você
        u = seg(t, 41.4, 42.0)
        x, y, lift = hop(u, (1250, 700), (330, 1320), 200)
        place(c, ctx, by_h("fichas_vitoria.png", 230), x, y, 0, lift=lift)


PROG = [("progresso_a.png", (820, 650)), ("progresso_b.png", (820, 900)), ("progresso_c.png", (820, 1150))]


def s6(c, ctx, t):
    if t < 47.0:
        if t >= 43.3:
            u = seg(t, 43.3, 43.9)
            x, y, lift = hop(u, (-250, 900), (320, 900), 120)
            place(c, ctx, by_h("carta_verde.png", 620), x, y, -4, lift=lift)
        place(c, ctx, by_h("progresso_verso.png", 200), 820, 900, 0, pop(t, 44.4))
        for k, (name, (x, y)) in enumerate(PROG):
            if t >= 45.4 + k * 0.15:
                u = seg(t, 45.4 + k * 0.15, 45.9 + k * 0.15)
                xx, yy, lift = hop(u, (820, 900), (x, y), 160)
                place(c, ctx, by_h(name, 200), xx, yy, 0, lift=lift)
        return
    if t >= 47.3:
        u = seg(t, 47.3, 47.9)
        x, y, lift = hop(u, (-250, 1000), (320, 980), 120)
        place(c, ctx, by_h("carta_azul.png", 640), x, y, -4, lift=lift)
    place(c, ctx, by_h("gato.png", 420), 800, 760, 4, pop(t, 48.5))
    if t >= 49.3:
        deck(c, ctx, 800, 1170, 300, None, under="carta_verso.png", n=3)
        v = seg(t, 49.8, 50.2) * (1 - seg(t, 50.9, 51.0))
        if v <= 0:
            place(c, ctx, by_h("carta_verso.png", 300), 800, 1170, 0, shadow=0.2)
        else:  # espiadinha: a de cima levanta e mostra a frente
            sx, flipped = flip_sx(t, 49.8, 3)
            name = "carta_vermelha.png" if flipped else "carta_verso.png"
            place(c, ctx, by_h(name, 300), 800 + 30 * v, 1170 - 110 * v, 8 * v, sx=sx, lift=80 * v)


def s7(c, ctx, t):
    if t < 54.3:
        builds = {"1": 0.0, "4": 0.0, **FIM}
        efeso(c, ctx, 540, 860, 860, t, builds=builds)
        s = 860 / EF_W
        y0 = 860 - EF_H * s / 2
        for k, tb in FIM.items():
            px, py, pw, ph = EF["pecas"][k]
            dust(c, ctx, t, tb + 0.4, 540 - 430 + (px + pw / 2) * s, y0 + (py + ph) * s, pw * s * 0.5)
        return
    for k, ((nome, x, y, r), col) in enumerate(zip(NOMES, NOME_COR)):
        place(c, ctx, sticker(nome, 62, col), x, y, r, pop(t, 54.8 + k * 0.18))


def s8(c, ctx, t):
    place(c, ctx, logo_suavez(460), 540, 420, -2, pop(t, 58.7), shadow=0.6)
    if t >= 59.2:
        u = seg(t, 59.2, 59.8)
        x, y, lift = hop(u, (-300, 1150), (300, 1140), 120)
        place(c, ctx, by_h("caixa3d.png", 560), x, y, -4, lift=lift, shadow=0.7)


SCENE_FN = [s0, s1, s2, s3, s4, s5, s6, s7, s8]
SCENE_BG = ["capa", "mesa", "mesa", "mesa", "mesa", "mesa", "mesa", "mesa", "capa"]


@lru_cache(None)
def vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 1.414
    return (1 - 0.5 * np.clip(r, 0, 1) ** 2.2)[..., None]


def post(img, ctx, shake=0.0):
    a = np.asarray(img, np.float32)
    a = a * vignette() * (1.0 + ctx.j(0.03))  # oscilação da luz entre as poses
    g = ctx.rng.normal(0, 3.2, (H // 2, W // 2)).astype(np.float32)
    a = np.clip(a + np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None], 0, 255).astype(np.uint8)
    m = 2 + int(shake)
    dx, dy = int(ctx.rng.integers(-m, m + 1)), int(ctx.rng.integers(-m, m + 1))  # câmera levemente mexida
    return np.roll(a, (dy, dx), (0, 1))


def frame_at(to, ctx):
    i = scene_of(to)
    img = (bg_capa() if SCENE_BG[i] == "capa" else bg_mesa()).copy()
    SCENE_FN[i](img, ctx, to)
    draw_stickers(img, ctx, to, i)
    return img, i


# ---------------------------------------------------------------- roteiro, narração e legendas
ROTEIRO = [
    "Já pensou construir uma das sete maravilhas do mundo... em só vinte e cinco minutos?",
    "Esse é o 7 Wonders Arquitetos! Cada jogador é o arquiteto de uma maravilha, e no final vence quem tiver mais pontos.",
    "Na sua vez, você pega só uma carta: do monte da esquerda, do monte da direita... ou arrisca no monte do meio, sem ver.",
    "As cartas cinzas são materiais: pedra, madeira, tijolo, papiro e vidro. E o ouro vale como qualquer um deles.",
    "Juntou os materiais que a maravilha pede? Constrói uma etapa! Cada etapa dá pontos, e algumas ainda dão um poder especial.",
    "As vermelhas são escudos. Quando aparece a corneta, uma ficha vira... e quando todas viram, é guerra! "
    "Quem tem mais escudos que o vizinho ganha pontos.",
    "As verdes são ciência e dão fichas de progresso. As azuis dão pontos direto, e algumas trazem o gato, que espia o monte do meio.",
    "Quando alguém termina a maravilha, o jogo acaba e vence quem tiver mais pontos. E aí, qual maravilha você construiria? Comenta aqui!",
    "Junta a galera, de 2 a 7 jogadores, e aluga o 7 Wonders Arquitetos na Sua Vez. O link tá na bio!",
]


def default_subs():
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
        span = (b - a - 0.5) / len(chunks)
        for i, ch in enumerate(chunks):
            out.append((a + 0.3 + i * span, a + 0.3 + (i + 1) * span, ch))
    return out


SUBS = default_subs()
TIMELINE_PATH = os.path.join(ROOT, "narracao", "timeline.json")
TIMELINE = None
if os.path.exists(TIMELINE_PATH):
    TIMELINE = json.load(open(TIMELINE_PATH, encoding="utf-8"))
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
    c = [(e[0], "pop", 0.32) for e in STK]
    c += [(a, "paper", 0.5) for a, _ in SCENES[1:]]
    c += [(0.2, "card", 0.5), (3.2, "card", 0.4), (3.5, "card", 0.4), (3.8, "card", 0.4), (1.6, "ding", 0.3)]
    c += [(6.1, "pop", 0.4)] + [(t0 + 0.5, "build", 0.45) for t0 in (6.9, 7.3, 7.7, 8.1, 8.6)]
    c += [(14.0, "card", 0.5), (14.2, "card", 0.5), (14.4, "card", 0.5), (15.9, "card", 0.5), (16.6, "card", 0.4),
          (18.8, "card", 0.4), (19.1, "whoosh", 0.3), (19.6, "card", 0.5)]
    c += [(20.4, "card", 0.5)] + [(21.0 + k * 0.55, "pop", 0.4) for k in range(5)] + [(24.2, "card", 0.5),
                                                                                       (24.9, "coin", 0.6)]
    c += [(29.0, "whoosh", 0.3), (B1, "card", 0.5), (B1 + 0.4, "build", 0.9), (30.2, "ding", 0.4),
          (31.6, "whoosh", 0.3), (B2, "card", 0.5), (B2 + 0.4, "build", 0.9), (32.8, "chime", 0.4)]
    c += [(35.3, "card", 0.5), (37.6, "horn", 0.55), (38.3, "horn", 0.6), (39.0, "horn", 0.7),
          (39.6, "clash", 0.9), (41.4, "whoosh", 0.4), (42.0, "coin", 0.6)]
    c += [(43.3, "card", 0.5), (44.4, "pop", 0.4), (45.4, "whoosh", 0.4), (45.8, "chime", 0.5),
          (47.3, "card", 0.5), (48.5, "meow", 0.5), (49.3, "card", 0.4), (49.8, "card", 0.4)]
    c += [(tb + 0.4, "build", 0.8) for tb in FIM.values()] + [(52.6, "fanfare", 0.7)]
    c += [(59.2, "card", 0.5), (65.0, "chime", 0.5)]
    return c


CUES = _cues()


@lru_cache(None)
def sub_img(text):
    f = font(POPPINS, 50)
    lines = wrap(text, f, 900).split("\n")
    lh = 62
    w = int(max(f.getlength(l) for l in lines)) + 50
    h = lh * len(lines) + 26
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=22, fill=(16, 16, 28, 220))
    for i, l in enumerate(lines):
        d.text((w / 2, 13 + lh * i + lh / 2), l, font=f, fill=WHITE, anchor="mm")
    return im


def render_frame(args):
    fi, subs = args
    ctx = Ctx(fi)
    t = fi / FPS
    to = to_orig(t)
    img, i = frame_at(to, ctx)
    if i < len(SCENES) - 1:
        wm = watermark()
        img.paste(wm, (W - wm.width - 34, 70), wm)
    if subs:
        for a_, b_, s in SUBS:
            if a_ <= t < b_:
                si = sub_img(s)
                img.paste(si, ((W - si.width) // 2, 1700 - si.height // 2), si)
    shake = 10 * (1 - seg(to, 39.6, 40.4)) if 39.6 <= to < 40.4 else 0
    return post(img, ctx, shake).tobytes()


def render(out_path, wav, subs, workers=4):
    n = int(DUR * FPS)
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-maxrate", "8M", "-bufsize", "16M",
           "-r", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
           out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for i, fr in enumerate(pool.imap(render_frame, [(k, subs) for k in range(n)], chunksize=4)):
            p.stdin.write(fr)
            if i % 120 == 0:
                print(f"  quadro {i}/{n}", flush=True)
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
        ims = [Image.frombytes("RGB", (W, H), render_frame((int(x * FPS), True))) for x in a.frame]
        if len(ims) == 1:
            ims[0].save(os.path.join(OUT, "frame.png"))
        sheet = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * k, 0))
        sheet.save(os.path.join(OUT, "frames.jpg"), quality=90)
        return
    wav = os.path.join(OUT, "trilha_stopmo.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz, cues=CUES)
    with open(os.path.join(ROOT, "legendas.srt"), "w", encoding="utf-8") as f:
        for i, (a_, b_, s) in enumerate(SUBS, 1):
            ts = lambda x: f"{int(x // 3600):02}:{int(x // 60 % 60):02}:{int(x % 60):02},{int(round(x * 1000)) % 1000:03}"
            f.write(f"{i}\n{ts(a_)} --> {ts(b_)}\n{s}\n\n")
    if a.only != "limpo":
        render(os.path.join(OUT, "stopmo_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "stopmo_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
