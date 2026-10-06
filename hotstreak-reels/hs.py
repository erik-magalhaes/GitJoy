#!/usr/bin/env python3
"""Reels do Hot Streak – visual "Arquibancada" com a arte oficial do jogo (vetor do manual).

    python3 hs.py --frame 1 3 6      # quadros de teste (out/frames.jpg)
    python3 hs.py --only preview     # só a versão com legenda
    python3 hs.py                    # com e sem legenda (out/hs_preview.mp4 e out/hs_limpo.mp4)
    python3 hs.py --teste            # teste curto do gancho (out/hs_teste.mp4)
"""
import argparse
import json
import math
import os
import subprocess
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

import som_hs as som

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "assets", "pecas")
FN = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
POSE = 12

RED = (230, 40, 40)
DRED = (150, 20, 20)
YEL = (255, 214, 60)
CREAM = (250, 236, 214)
GREEN = (60, 120, 60)
WHITE = (255, 255, 255)
INK = (30, 20, 30)
PEACH = (247, 178, 140)
ORANGE = (240, 106, 42)
NAVYC = (40, 58, 120)
MUSTARD = (248, 196, 30)
PURPLE = (110, 30, 100)
MAROON = (130, 20, 30)
LBLUE = (175, 208, 245)
MASC = ["p_hurley.png", "p_gobbler.png", "p_dangle.png", "p_mum.png"]
LUCKY = "LuckiestGuy-Regular.ttf"
SLAB = "AlfaSlabOne-Regular.ttf"
POP = "Poppins-ExtraBold.ttf"


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.7):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


def pose(t):
    return int(t * POSE) / POSE


def jit(t, a=3.0, seed=0):
    """Tremidinho de mão do stop motion (muda 12 vezes por segundo)."""
    k = int(t * POSE)
    r = np.random.default_rng(k * 31 + seed)
    return r.uniform(-a, a), r.uniform(-a, a), r.uniform(-a * 0.4, a * 0.4)


@lru_cache(None)
def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


@lru_cache(None)
def peca(n, h):
    im = Image.open(os.path.join(P, n)).convert("RGBA")
    return im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)


@lru_cache(None)
def peca_w(n, w):
    im = Image.open(os.path.join(P, n)).convert("RGBA")
    return im.resize((int(w), max(2, int(im.height * w / im.width))), Image.LANCZOS)


def sombra(im, blur=12, off=(12, 18), op=0.4, cor=(20, 30, 20)):
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
def com_sombra(n, h, espelho=False):
    im = peca(n, h)
    if espelho:
        im = ImageOps.mirror(im)
    return sombra(im, 12, (12, 18), 0.4)


def cola(img, im, x, y, rot=0.0, sc=1.0, sx=1.0, sy=1.0, alpha=1.0):
    if sc <= 0.02 or alpha <= 0.01 or abs(sx) < 0.01:
        return
    if sx < 0:
        im = ImageOps.mirror(im)
        sx = -sx
    if abs(sc * sx - 1) > 0.003 or abs(sc * sy - 1) > 0.003:
        im = im.resize((max(2, int(im.width * sc * sx)), max(2, int(im.height * sc * sy))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)


def pop(t, t0, d=0.35):
    u = seg(t, t0, t0 + d)
    return max(0.0, out_back(u)) if u < 1 else 1.0


# ---------------------------------------------------------------- cenário: arquibancada + pista
CROWD_H = 1300


@lru_cache(None)
def torcida():
    im = Image.open(os.path.join(P, "v_torcida_limpa.png")).convert("RGBA")
    s = CROWD_H / im.height
    return im.resize((int(im.width * s), CROWD_H), Image.LANCZOS)


@lru_cache(None)
def torcida_fundo(escuro=0.55, blur=10):
    """Torcida desfocada e escurecida, para as cenas de mesa (bilhetes e placar)."""
    tc = torcida()
    s = H / tc.height
    im = tc.resize((int(tc.width * s), H), Image.LANCZOS).convert("RGB")
    x0 = (im.width - W) // 2
    im = im.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(im, Image.new("RGB", im.size, (40, 10, 20)), escuro).convert("RGBA")


@lru_cache(None)
def pista(w=1400, h=880):
    """Pista no estilo do tapete do jogo: faixas verdes alternadas."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lanes = 4
    lh = h / lanes
    for k in range(lanes):
        d.rectangle((0, k * lh, w, (k + 1) * lh), fill=(52, 160, 76) if k % 2 else (62, 178, 86))
        d.rectangle((0, k * lh, w, k * lh + 10), fill=(44, 140, 66))
    return im


def estrela(d, cx, cy, r, cor):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + i * math.pi / 5),
            cy + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=cor)


def desenha_pista(img, y0, scroll):
    """Pista com marcas andando (scroll em px) para dar a sensação de velocidade."""
    base = pista().copy()
    d = ImageDraw.Draw(base)
    lh = base.height / 4
    for k in range(4):
        off = (scroll * (1 + 0.1 * k)) % 160
        for x in np.arange(-160, base.width + 160, 160) - off:
            d.rounded_rectangle((x, (k + 1) * lh - 26, x + 70, (k + 1) * lh - 12), radius=6, fill=WHITE)
        off2 = (scroll * 0.9) % 330
        for x in np.arange(-330, base.width + 330, 330) - off2:
            estrela(d, x + (k % 2) * 160, k * lh + lh * 0.42, 26, (176, 232, 176))
    img.paste(base, (int((W - base.width) / 2), int(y0)), base)
    d2 = ImageDraw.Draw(img)  # gramado e linha lateral embaixo da pista
    yb = int(y0 + base.height)
    if yb < H:
        d2.rectangle((0, yb, W, H), fill=(36, 110, 54))
        d2.rectangle((0, yb, W, min(H, yb + 14)), fill=WHITE)


def confete(img, t, n=120, seed=3, top=0, bottom=H):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    cols = [(255, 210, 60), (240, 60, 70), (60, 160, 240), (255, 255, 255), (250, 120, 40), (120, 200, 90)]
    for _ in range(n):
        x0, sp, ph = rng.uniform(0, W), rng.uniform(140, 320), rng.uniform(0, 6.28)
        y = top + (rng.uniform(0, bottom - top) + t * sp) % (bottom - top)
        x = x0 + 30 * math.sin(t * 2 + ph)
        a = t * 4 + ph
        col = cols[rng.integers(len(cols))]
        L = 20 * abs(math.cos(a)) + 6
        d.line((x - L * math.cos(a), y - L * math.sin(a) * 0.4, x + L * math.cos(a), y + L * math.sin(a) * 0.4),
               fill=col, width=9)


@lru_cache(None)
def placa(txt, size=96, fundo=RED, letra=YEL, maxw=980):
    """Placa de torcida no estilo do jogo (retângulo de papel com letras grossas)."""
    lines = txt.split("\n")
    while True:
        f = font(LUCKY, size)
        tw = max(f.getlength(l) for l in lines)
        if tw + size * 0.9 <= maxw or size < 30:
            break
        size -= 4
    bw = int(tw + size * 0.9)
    bh = int(size * 1.25 * len(lines) + size * 0.6)
    im = Image.new("RGBA", (bw + 30, bh + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((16, 18, bw + 16, bh + 18), fill=(0, 0, 0, 90))
    d.rectangle((0, 0, bw, bh), fill=fundo)
    for k, l in enumerate(lines):
        d.text((bw / 2, size * 0.35 + size * 1.25 * k + size * 0.62), l, font=f, fill=letra, anchor="mm",
               stroke_width=max(4, size // 16) if sum(letra) > 380 else 0,
               stroke_fill=DRED if fundo == RED else INK)
    return im


@lru_cache(None)
def estouro(txt, w=360, cor=(250, 235, 30), letra=INK):
    """Estouro amarelo oficial do manual (o do "DQ!") com o nosso texto por cima."""
    im = peca_w("v_dq.png", w).copy()
    if cor != (250, 235, 30):
        a = im.getchannel("A")
        im = Image.new("RGBA", im.size, cor + (255,))
        im.putalpha(a)
    d = ImageDraw.Draw(im)
    lines = txt.split("\n")
    size = int(w * (0.26 if len(lines) == 1 else 0.2))
    while max(font(SLAB, size).getlength(l) for l in lines) > w * 0.66:
        size -= 2
    f = font(SLAB, size)
    for k, l in enumerate(lines):
        y = im.height * 0.5 + (k - (len(lines) - 1) / 2) * size * 1.15
        d.text((im.width * 0.5, y), l, font=f, fill=letra, anchor="mm")
    return sombra(im, 8, (6, 10), 0.35, (0, 0, 0))


def corredor(img, nome, x, y, h, t, fase=0.0, vel=1.0, rot0=0.0, espelho=False):
    """Mascote correndo: pulinho, balanço e esticadinha a cada passo (12 poses/s)."""
    tp = pose(t) * vel * 2 * math.pi * 1.6 + fase
    hop = abs(math.sin(tp)) * h * 0.06
    rot = rot0 + 7 * math.sin(tp) * (-1 if espelho else 1)
    sq = 1 + 0.05 * math.cos(2 * tp)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((x - h * 0.28, y - 14, x + h * 0.28, y + 14), fill=(20, 60, 25, 110))
    cola(img, com_sombra(nome, h, espelho), x, y - h * 0.5 - hop, rot, 1.0, 1 / sq, sq)
    if vel > 0.2:  # poeirinha atrás
        rng = np.random.default_rng(int(t * POSE) + int(fase * 10))
        s = -1 if espelho else 1
        for k in range(3):
            r = rng.uniform(12, 26) * h / 300 + 6
            px = x - s * (h * 0.35 + k * 30 * h / 300 + rng.uniform(0, 20))
            d.ellipse((px - r, y - 20 - r, px + r, y - 20 + r), fill=(230, 245, 220, 150 - k * 40))


@lru_cache(None)
def logo_card(width):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2,
                                           fill=(255, 255, 255, 255))
    card.alpha_composite(lg, (pad, pad))
    return card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)


# ---------------------------------------------------------------- cartas de corrida, notas e bilhetes
CARTA = {  # mascote, cor do fundo, cor do texto, número/ação, linha de baixo
    "g3": ("p_gobbler.png", ORANGE, PURPLE, "3", None),
    "h_cai": ("p_hurley.png", PEACH, (205, 35, 45), "CAI!", None),
    "d_volta": ("p_dangle.png", NAVYC, LBLUE, "MEIA\nVOLTA", None),
    "m_desvia": ("p_mum.png", MUSTARD, MAROON, "1", "DESVIA!"),
    "d_cai": ("p_dangle.png", NAVYC, LBLUE, "CAI!", None),
    "h_desvia": ("p_hurley.png", PEACH, (205, 35, 45), "1", "DESVIA!"),
}


@lru_cache(None)
def carta(chave, h):
    """Carta de corrida redesenhada no estilo do jogo (cor do mascote, borda pontilhada, texto em cima e
    de ponta-cabeça embaixo)."""
    nome, cor, tc, txt, sub = CARTA[chave]
    w = int(h * 0.72)
    S = 2  # desenha em dobro e reduz (bordas lisas)
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=int(h * 0.06 * S), fill=cor)
    m = h * 0.05 * S
    step = h * 0.035 * S
    x0, y0, x1, y1 = m, m, w * S - m, h * S - m
    r = h * 0.008 * S
    for x in np.arange(x0, x1, step):  # borda pontilhada
        d.ellipse((x - r, y0 - r, x + r, y0 + r), fill=tc)
        d.ellipse((x - r, y1 - r, x + r, y1 + r), fill=tc)
    for y in np.arange(y0, y1, step):
        d.ellipse((x0 - r, y - r, x0 + r, y + r), fill=tc)
        d.ellipse((x1 - r, y - r, x1 + r, y + r), fill=tc)
    lines = txt.split("\n")
    size = h * (0.2 if len(txt) <= 2 else 0.11 if len(lines) == 1 else 0.085)

    def texto(dd, lines_, cy, sz):
        f = font(SLAB, int(sz * S))
        for k, l in enumerate(lines_):
            dd.text((w * S / 2, cy + (k - (len(lines_) - 1) / 2) * sz * S * 1.05), l, font=f, fill=tc, anchor="mm")

    texto(d, lines, h * S * 0.16, size)
    if sub:
        texto(d, [sub], h * S * 0.31, h * 0.07)
    # medalhão com o mascote
    cy = h * S * (0.58 if sub else 0.5)
    rr = h * 0.17 * S
    d.ellipse((w * S / 2 - rr, cy - rr, w * S / 2 + rr, cy + rr), fill=CREAM, outline=tc, width=int(h * 0.012 * S))
    mi = peca(nome, int(rr * 1.6))
    if mi.width > rr * 1.7:
        mi = peca_w(nome, int(rr * 1.7))
    im.alpha_composite(mi, (int(w * S / 2 - mi.width / 2), int(cy - mi.height / 2)))
    # o número de ponta-cabeça embaixo (como nas cartas do jogo)
    bot = Image.new("RGBA", im.size, (0, 0, 0, 0))
    texto(ImageDraw.Draw(bot), lines, h * S * 0.13, size * 0.8)
    im.alpha_composite(bot.rotate(180))
    im = im.resize((w, h), Image.LANCZOS)
    return sombra(im, 8, (6, 10), 0.45, (0, 0, 0))


@lru_cache(None)
def verso(h):
    """Verso amarelo das cartas de corrida: fitas quadriculadas e confete."""
    w = int(h * 0.72)
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=int(h * 0.06 * S), fill=(250, 200, 30))
    mask = np.asarray(im.getchannel("A"))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    rng = np.random.default_rng(5)
    for _ in range(40):
        x, y = rng.uniform(0, w * S), rng.uniform(0, h * S)
        a = rng.uniform(0, 6.28)
        L = h * 0.05 * S
        dl.line((x, y, x + L * math.cos(a), y + L * math.sin(a)), fill=[(230, 50, 60), (40, 120, 220),
                (255, 255, 255)][rng.integers(3)], width=int(h * 0.018 * S))
    q = h * 0.035 * S
    for k, yy in enumerate((0.22, 0.52, 0.82)):  # três fitas quadriculadas onduladas
        for i in range(int(w * S / q) + 2):
            x = i * q
            yb = h * S * yy + math.sin(i * 0.6 + k) * h * 0.04 * S
            for j in range(2):
                dl.rectangle((x, yb + j * q, x + q, yb + (j + 1) * q), fill=INK if (i + j) % 2 else WHITE)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), mask)))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=int(h * 0.06 * S), outline=(200, 140, 10),
                        width=int(h * 0.012 * S))
    im = im.resize((w, h), Image.LANCZOS)
    return sombra(im, 8, (6, 10), 0.45, (0, 0, 0))


@lru_cache(None)
def nota(valor, cor, w=300):
    """Nota de dinheiro do jogo (estilizada)."""
    h = int(w * 0.46)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(h * 0.1), fill=cor)
    d.rounded_rectangle((h * 0.08, h * 0.08, w - h * 0.08, h - h * 0.08), radius=int(h * 0.07),
                        outline=WHITE + (200,), width=max(2, int(h * 0.04)))
    d.ellipse((w / 2 - h * 0.3, h * 0.2, w / 2 + h * 0.3, h * 0.8), fill=CREAM)
    d.text((w / 2, h * 0.5), "$", font=font(SLAB, int(h * 0.42)), fill=cor, anchor="mm")
    for x in (h * 0.42, w - h * 0.42):
        d.text((x, h * 0.5), str(valor), font=font(SLAB, int(h * 0.36)), fill=WHITE, anchor="mm")
    return sombra(im, 6, (4, 8), 0.35, (0, 0, 0))


NOTAS = [(10, (92, 160, 92)), (5, (230, 110, 150)), (20, (70, 120, 210)), (1, (240, 190, 40))]


def chuva_de_notas(img, t, t0, n=14, seed=4, x=540, y=1500, alcance=1.0):
    """Notas voando a partir de (x, y) em leque, girando."""
    u = t - t0
    if u <= 0 or u > 2.4:
        return
    rng = np.random.default_rng(seed)
    for k in range(n):
        v, cor = NOTAS[k % 4]
        ang = rng.uniform(-2.4, -0.7)
        sp = rng.uniform(900, 1500) * alcance
        px = x + math.cos(ang) * sp * u
        py = y + math.sin(ang) * sp * u + 900 * u * u
        rot = rng.uniform(-40, 40) + u * rng.uniform(-300, 300)
        cola(img, nota(v, cor, 220), px, py, rot, sy=abs(math.cos(u * rng.uniform(4, 9))) * 0.8 + 0.2)


# ---------------------------------------------------------------- cenas
SCENES = [(0.0, 5.6), (5.6, 12.6), (12.6, 19.6), (19.6, 26.6), (26.6, 34.0), (34.0, 42.0), (42.0, 49.0),
          (49.0, 57.4), (57.4, 66.0)]
DUR = SCENES[-1][1]
TR = 0.4  # bandeirada entre as cenas


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if a <= t < b:
            return i
    return len(SCENES) - 1


def cena_gancho(img, t):
    tc = torcida()
    bob = 10 * abs(math.sin(pose(t) * 9))  # a torcida pula
    z = 1 + 0.04 * seg(t, 0, 5.6)
    im = tc.resize((int(tc.width * z), int(tc.height * z)), Image.BICUBIC)
    img.paste(im, (int((W - im.width) / 2), int(-80 - bob)), im)
    confete(img, t, 90, 1, 0, 1300)
    desenha_pista(img, 1180, t * 40)
    chuva_de_notas(img, t, 2.5, 16, 7, 540, 1650)
    u = seg(t, 0.25, 0.75)
    x = lerp(-400, 540, ease(u))
    cola(img, com_sombra("p_hurley.png", 900), x, 1180 + 30 * (1 - ease(u)), lerp(-25, -4, ease(u)) +
         3 * math.sin(pose(t) * 5))
    cola(img, placa("APOSTOU NUM\nCACHORRO-QUENTE?!", 84), 540, 430, -4 + 1.5 * math.sin(pose(t) * 6), pop(t, 0.05))
    if t >= 2.4:
        cola(img, placa("PREPARA A CARTEIRA...", 58, YEL, RED), 540, 650, 3, pop(t, 2.4))
    if t >= 3.9:  # "...e a garganta!": a torcida grita
        k = 1 + 0.06 * math.sin(pose(t) * 20)
        cola(img, estouro("AAAAH!", 360), 860, 900, 10, pop(t, 3.9) * k)
        cola(img, estouro("UHUU!", 280, (255, 255, 255)), 190, 1000, -12, pop(t, 4.1) * k)


NOMES = ["HURLEY", "GOBBLER", "DANGLE", "RAINHA MUM"]


def cena_largada(img, t):
    t0 = SCENES[1][0]
    u = ease(seg(t, t0, t0 + 1.4))  # câmera desce da torcida até a pista
    cam = lerp(0, 450, u)
    tc = torcida()
    bob = 8 * abs(math.sin(pose(t) * 9))
    img.paste(tc, (int((W - tc.width) / 2), int(-60 - cam - bob)), tc)
    py = 1180 - cam
    largada = t0 + 4.6
    desenha_pista(img, py, max(0.0, t - (largada - 0.1)) * 900)
    confete(img, t, 60, 2, 0, int(1300 - cam))
    lanes_y = [py + 220 * (k + 1) - 26 for k in range(4)]
    for k, nome in enumerate(MASC):
        te = t0 + 1.2 + k * 0.55  # cada mascote entra na sua raia
        if t < te:
            continue
        v = seg(t, te, te + 0.5)
        if t < largada:
            x = lerp(-200, 260, ease(v))
            corredor(img, nome, x, lanes_y[k], 300, t, fase=k * 1.3, vel=1.0 if v < 1 else 0.0)
            cola(img, placa(NOMES[k], 46, WHITE, INK), 640, lanes_y[k] - 120, -3 + k * 2, pop(t, te + 0.3))
        else:
            w = seg(t, largada + k * 0.05, largada + 0.9)
            x = lerp(260, 360 + [180, 40, 120, -20][k], ease(w)) + (35 * math.sin(t * 1.3 + k) if w >= 1 else 0)
            corredor(img, nome, x, lanes_y[k], 300, t, fase=k * 1.3, vel=1.0)
    if t < largada - 0.7:
        cola(img, placa("HOT STREAK", 120, RED, YEL), 540, 300 - cam * 0.2, -3, pop(t, t0 + 0.4))
    if largada - 0.7 <= t < largada + 0.3:
        cola(img, placa("JÁ!" if t >= largada else "3, 2, 1...", 120, YEL, RED), 540, 300, 0,
             pop(t, largada - 0.7, 0.2))
    if t >= largada + 0.9:
        cola(img, placa("VOCÊS APOSTAM\nEM QUEM GANHA!", 80), 540, 300, -3, pop(t, largada + 0.9))


# --- guichê de apostas (cenas 3 e 4)
@lru_cache(None)
def guiche():
    """Painel creme com borda vermelha (cores do manual)."""
    im = Image.new("RGBA", (980, 1240), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 979, 1239), radius=40, fill=RED)
    d.rounded_rectangle((34, 34, 945, 1205), radius=26, fill=CREAM)
    return sombra(im, 16, (10, 18), 0.5, (0, 0, 0))


def lampadas(img, x0, y0, x1, y1, t, n_lado=(13, 17)):
    """Lâmpadas de letreiro que piscam em sequência."""
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(n_lado[0]):
        pts.append((lerp(x0, x1, i / (n_lado[0] - 1)), y0))
    for i in range(1, n_lado[1]):
        pts.append((x1, lerp(y0, y1, i / (n_lado[1] - 1))))
    for i in range(1, n_lado[0]):
        pts.append((lerp(x1, x0, i / (n_lado[0] - 1)), y1))
    for i in range(1, n_lado[1] - 1):
        pts.append((x0, lerp(y1, y0, i / (n_lado[1] - 1))))
    fase = int(t * POSE / 2) % 3
    for k, (x, y) in enumerate(pts):
        on = k % 3 == fase
        r = 11
        d.ellipse((x - r - 4, y - r - 4, x + r + 4, y + r + 4), fill=(120, 20, 20))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 190) if on else (230, 170, 60))


def fundo_guiche(img, t, titulo):
    img.paste(torcida_fundo(), (0, 0))
    g = guiche()
    img.paste(g, (540 - g.width // 2, 920 - g.height // 2), g)
    lampadas(img, 70, 320, 1010, 1520, t)
    cola(img, placa(titulo, 74, RED, YEL), 540, 300, -2)


def ticket(img, nome, x, y, w, t, t_in, de=1, rot=-4):
    """Bilhete chegando voando (de=1 da direita, -1 da esquerda) com tremidinho."""
    if t < t_in:
        return
    u = ease(seg(t, t_in, t_in + 0.45))
    jx, jy, jr = jit(t, 2.5, len(nome))
    cola(img, sombra(peca_w(nome, w), 10, (8, 14), 0.45, (0, 0, 0)), lerp(x + de * 1100, x, u) + jx,
         lerp(y - 200, y, u) + jy, lerp(rot + de * 30, rot, u) + jr)


@lru_cache(None)
def balao(txt, size=48, w=600):
    """Carta preta de pergunta (aposta paralela)."""
    f = font(SLAB, size)
    lines = txt.split("\n")
    h = int(size * 1.3 * len(lines) + size * 1.2)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=28, fill=(25, 22, 28))
    d.rounded_rectangle((12, 12, w - 13, h - 13), radius=20, outline=YEL, width=4)
    for k, l in enumerate(lines):
        d.text((w / 2, size * 0.6 + size * 1.3 * k + size * 0.65), l, font=f, fill=WHITE, anchor="mm")
    return sombra(im, 10, (8, 14), 0.45, (0, 0, 0))


def circulo(img, cx, cy, rx, ry, u, cor=RED, width=10):
    """Círculo de caneta sendo desenhado (u de 0 a 1)."""
    if u <= 0:
        return
    d = ImageDraw.Draw(img)
    a1 = -100 + 380 * min(1, u)
    pts = [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
           for a in np.linspace(-100, a1, 60)]
    d.line(pts, fill=cor, width=width, joint="curve")


def cena_bilhetes(img, t):
    a = SCENES[2][0]
    u = t - a
    fundo_guiche(img, t, "BILHETES DE APOSTA")
    cola(img, placa("2 POR CORRIDA!", 56, YEL, RED), 540, 420, 3, pop(t, a + 0.5))
    ticket(img, "ticket_gobbler_safe.png", 540, 680, 820, t, a + 0.8, 1, -4)
    if 1.4 <= u < 3.6:
        cola(img, placa("NO MASCOTE...", 56, WHITE, INK), 540, 960, -3, pop(t, a + 1.4))
    ticket(img, "ticket_yes_safe.png", 560, 1160, 640, t, a + 3.0, -1, 4)
    if u >= 3.6:
        cola(img, placa("...OU EM COISA BIZARRA!", 56, WHITE, INK), 540, 920, 3, pop(t, a + 3.6))
    if u >= 4.6:
        cola(img, balao("ALGUÉM VAI SAIR\nDA PISTA?", 46, 640), 480, 1440, -2 + math.sin(pose(t) * 4),
             pop(t, a + 4.6))
    if u >= 5.6:
        cola(img, estouro("SIM\nOU NÃO?", 300), 860, 1250, 12, pop(t, a + 5.6))


def flip_ticket(img, frente, verso_, x, y, w, t, t_flip, rot=-3):
    """Bilhete virando do lado seguro para o arriscado (como no jogo: o bilhete tem dois lados)."""
    u = seg(t, t_flip, t_flip + 0.4)
    sx = math.cos(u * math.pi)
    nome = frente if sx >= 0 else verso_
    jx, jy, jr = jit(t, 2.0, 11)
    lift = math.sin(u * math.pi) * 60
    cola(img, sombra(peca_w(nome, w), 10, (8, 14), 0.45, (0, 0, 0)), x + jx, y - lift + jy, rot + jr,
         sx=max(0.02, abs(sx)), sc=1 + 0.08 * math.sin(u * math.pi))


def cena_risco(img, t):
    a = SCENES[3][0]
    u = t - a
    fundo_guiche(img, t, "SEGURA OU ARRISCADA?")
    tf = a + 2.2
    flip_ticket(img, "ticket_gobbler_safe.png", "ticket_gobbler_risky.png", 540, 680, 860, t, tf)
    if u < 2.2:
        cola(img, placa("SEGURA", 64, (40, 140, 70), WHITE), 290, 470, -6, pop(t, a + 0.3))
    else:
        cola(img, placa("ARRISCADA!", 64, RED, YEL), 290, 470, -6, pop(t, tf + 0.3))
        # o 1º lugar pula de $10 para $15
        circulo(img, 540 - 430 + 860 * 0.365, 680, 80, 120, seg(t, tf + 0.6, tf + 1.0), (255, 190, 0), 12)
        if u >= 3.0:
            cola(img, estouro("PAGA\nMAIS!", 250), 880, 480, 10, pop(t, tf + 0.8))
    if u >= 0.0:
        flip_ticket(img, "ticket_yes_safe.png", "ticket_yes_risky.png", 540, 1170, 700, t, a + 3.8, 3)
        if u < 3.8:
            cola(img, placa("SEGURA", 50, (40, 140, 70), WHITE), 300, 1440, -4, pop(t, a + 0.6))
        circulo(img, 540 - 350 + 700 * 0.78, 1170, 80, 120, seg(t, a + 4.4, a + 4.8), RED, 12)
        if u >= 4.8:
            cola(img, placa("PODE PERDER $!", 58, RED, YEL), 540, 1440, -3, pop(t, a + 4.8))
        for k in range(5):  # dinheiro escapando
            v = seg(t, a + 5.0 + k * 0.15, a + 6.4 + k * 0.15)
            if 0 < v < 1:
                cola(img, nota(*NOTAS[k % 4], 200), 540 + (k - 2) * 150 + 80 * math.sin(v * 6 + k),
                     1380 - 900 * v, 20 * math.sin(v * 8 + k), alpha=1 - v)


# --- carta secreta (cena 5)
@lru_cache(None)
def telao(w=960, h=640):
    """Telão do estádio mostrando a ilustração oficial das cartas secretas."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=26, fill=(35, 35, 45))
    d.rounded_rectangle((10, 10, w - 11, h - 11), radius=20, outline=(90, 90, 110), width=6)
    return sombra(im, 14, (8, 16), 0.5, (0, 0, 0))


@lru_cache(None)
def secreta(w, h):
    im = Image.open(os.path.join(P, "v_secreta1.png")).convert("RGBA")
    im = im.crop((0, 0, im.width, int(im.height * 0.72)))
    bg = Image.new("RGBA", im.size, CREAM + (255,))
    bg.alpha_composite(im)
    s = max(w / bg.width, h / bg.height)
    return bg.resize((int(bg.width * s) + 2, int(bg.height * s) + 2), Image.LANCZOS)


def cena_secreta(img, t):
    a = SCENES[4][0]
    u = t - a
    tc = torcida()
    bob = 8 * abs(math.sin(pose(t) * 7))
    img.paste(tc, (int((W - tc.width) / 2), int(-140 - bob)), tc)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1060, W, H), fill=(36, 110, 54))  # mesa verde (gramado)
    d.rectangle((0, 1060, W, 1074), fill=WHITE)
    v = ease(seg(t, a, a + 0.5))  # telão desce
    ty = lerp(-700, 330, v)
    tl = telao()
    img.paste(tl, (60 - 42, int(ty) - 42), tl)
    sw, sh = 920, 600
    z = 1 + 0.12 * seg(t, a, a + 7.4)
    sc = secreta(sw, sh)
    sc = sc.resize((int(sc.width * z), int(sc.height * z)), Image.BICUBIC)
    cx = (sc.width - sw) // 2
    cy = int((sc.height - sh) * 0.3)
    img.paste(sc.crop((cx, cy, cx + sw, cy + sh)), (80, int(ty) + 20))
    if u >= 0.4:
        cola(img, placa("MALANDRAGEM!", 92, RED, YEL), 540, int(ty) + 10, -4, pop(t, a + 0.4))
    for k in range(6):  # o baralho de 18 cartas na mesa
        cola(img, verso(300), 300 - k * 3, 1330 - k * 4, -2 + k * 0.6)
    if u >= 1.2:
        cola(img, placa("18 CARTAS", 44, WHITE, INK), 300, 1545, -3, pop(t, a + 1.2))
    # a carta secreta: aparece de frente, vira e entra no baralho
    t_ap, t_vira, t_entra = a + 1.8, a + 3.2, a + 3.8
    if t >= t_ap:
        uv = seg(t, t_vira, t_vira + 0.35)
        sx = math.cos(uv * math.pi)
        im = carta("h_cai", 300) if sx >= 0 else verso(300)
        ue = ease(seg(t, t_entra, t_entra + 0.6))
        x = lerp(lerp(1300, 760, ease(seg(t, t_ap, t_ap + 0.4))), 300, ue)
        y = 1320 - 80 * math.sin(ue * math.pi) - 12 * (1 - ue)
        if ue < 1:
            cola(img, im, x, y, lerp(8, -1, ue), sx=max(0.02, abs(sx)))
        if t < t_vira:
            cola(img, placa("SÓ VOCÊ SABE!", 46, YEL, RED), 760, 1120, 4, pop(t, t_ap + 0.3))
            cola(img, estouro("SHHH!", 230, (255, 255, 255)), 950, 1460, 12, pop(t, t_ap + 0.5))
    if u >= 4.6:
        cola(img, placa("PUXA A SARDINHA\nPRO SEU LADO!", 62, YEL, RED), 720, 1330, 4, pop(t, a + 4.6))


# --- corrida (cenas 6 e 7): pista com casas, cartas virando embaixo
RY0, LH, NCASAS = 400, 190, 7
CX0, CW = 90, 130
CARD_X, CARD_Y, CARD_H = 450, 1385, 330


def casa_x(k):
    return CX0 + CW * (k + 0.5)


def lane_y(k):
    return RY0 + LH * (k + 1) - 26


@lru_cache(None)
def pista_corrida():
    im = Image.new("RGBA", (W, LH * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(4):
        d.rectangle((0, k * LH, W, (k + 1) * LH), fill=(52, 160, 76) if k % 2 else (62, 178, 86))
        d.rectangle((0, k * LH, W, k * LH + 8), fill=(44, 140, 66))
        for c in range(NCASAS + 1):  # risquinhos das casas
            x = CX0 + CW * c
            d.rounded_rectangle((x - 5, k * LH + LH * 0.3, x + 5, k * LH + LH * 0.62), radius=4, fill=WHITE)
        for c in (1, 4):
            estrela(d, casa_x(c) + 30, k * LH + LH * 0.25, 20, (176, 232, 176))
    fx = CX0 + CW * NCASAS + 14  # linha de chegada quadriculada
    q = 19
    for j in range(int(LH * 4 / q) + 1):
        for i in range(2):
            d.rectangle((fx + i * q, j * q, fx + (i + 1) * q, (j + 1) * q), fill=INK if (i + j) % 2 else WHITE)
    d.rectangle((0, 0, W, 10), fill=WHITE)
    d.rectangle((0, LH * 4 - 10, W, LH * 4), fill=WHITE)
    return im


# trajetória de cada mascote: (t, casa, raia); estados: meia-volta, caído e DQ (tempos)
CORRIDA = {
    "p_hurley.png": {"pos": [(0, 2, 0), (44.9, 2, 0), (45.5, 2.3, -1.4)], "cai": 36.8, "dq": 45.5, "sai": True},
    "p_gobbler.png": {"pos": [(0, 1, 1), (35.3, 1, 1), (36.1, 4, 1), (46.8, 4, 1), (47.7, 6.7, 1)]},
    "p_dangle.png": {"pos": [(0, 3, 2)], "vira": 38.3, "cai": 40.6, "dq": 42.7},
    "p_mum.png": {"pos": [(0, 2, 3), (39.8, 2, 3), (40.2, 3, 3), (40.6, 3, 2)]},
}
# cartas viradas pelo Dealer: (tempo, carta, legenda)
FLIPS = [(35.0, "g3", "GOBBLER\nANDA 3!"), (36.5, "h_cai", "HURLEY\nCAIU!"), (38.0, "d_volta", "DANGLE DEU\nMEIA-VOLTA!"),
         (39.5, "m_desvia", "A RAINHA\nDESVIOU!"), (42.3, "d_cai", "DANGLE CAIU\nDE NOVO!"),
         (44.5, "h_desvia", "HURLEY\nDESVIOU!")]


def posicao(nome, t):
    ks = CORRIDA[nome]["pos"]
    if t <= ks[0][0]:
        return ks[0][1], ks[0][2], False
    for (t0, c0, l0), (t1, c1, l1) in zip(ks, ks[1:]):
        if t0 <= t < t1:
            andando = (c0 != c1 or l0 != l1)
            u = ease((t - t0) / (t1 - t0)) if andando else 0.0
            return lerp(c0, c1, u), lerp(l0, l1, u), andando
    return ks[-1][1], ks[-1][2], False


def mascote_pista(img, nome, t, h=170, fase=0.0):
    est = CORRIDA[nome]
    casa, raia, andando = posicao(nome, t)
    x, ground = casa_x(casa), RY0 + LH * (raia + 1) - 26
    dq = est.get("dq")
    if dq and t >= dq + 0.3:  # desclassificado: sai voando girando
        v = seg(t, dq + 0.3, dq + 1.1)
        if v >= 1:
            return
        cola(img, com_sombra(nome, h), x + 260 * v, ground - h * 0.5 - 1000 * v + 400 * v * v, 720 * v,
             1 - 0.3 * v, alpha=1 - v * 0.5)
        return
    vira = est.get("vira")
    flip = math.cos(seg(t, vira, vira + 0.3) * math.pi) if vira and t >= vira else 1.0
    cai = est.get("cai")
    fall = ease(seg(t, cai, cai + 0.3)) if cai and t >= cai else 0.0
    d = ImageDraw.Draw(img, "RGBA")
    if raia >= -0.2:
        d.ellipse((x - h * 0.3, ground - 12, x + h * 0.3, ground + 12), fill=(20, 60, 25, 110))
    if fall >= 1 and nome == "p_hurley.png":  # o desenho oficial do Hurley caído
        im = sombra(peca("v_hurley_caido.png", int(h * 0.62)), 10, (10, 14), 0.4)
        jx = (jit(t, 4, 9)[0] if andando else 0)
        cola(img, im, x + jx, ground - h * 0.3)
        return
    if fall > 0:
        ang = (-88 if flip >= 0 else 88) * fall
        cx = x - h / 2 * math.sin(math.radians(ang)) * 0.85
        cy = ground - h / 2 * math.cos(math.radians(ang)) - fall * peca(nome, h).width * 0.38
        cola(img, com_sombra(nome, h, flip < 0), cx, cy, ang)
        return
    if andando:
        corredor(img, nome, x, ground, h, t, fase, 1.0, 0.0, espelho=flip < 0)
        return
    bob = abs(math.sin(pose(t) * 3 + fase)) * 6
    cola(img, com_sombra(nome, h), x, ground - h * 0.5 - bob, 2 * math.sin(pose(t) * 2 + fase), sx=flip)


def cartas_mesa(img, t):
    """Baralho à esquerda; o Dealer vira uma carta por vez para o centro, com a legenda ao lado."""
    d = ImageDraw.Draw(img)
    d.rectangle((0, RY0 + LH * 4, W, H), fill=(36, 110, 54))
    for k in range(5):
        cola(img, verso(260), 150 - k * 3, CARD_Y - k * 4, -3 + k)
    vis = [f for f in FLIPS if f[0] <= t]
    for k, (tf, ch, leg) in enumerate(vis):
        old = len(vis) - 1 - k
        if old > 2:
            continue
        u = seg(t, tf, tf + 0.35)
        sx = math.cos((1 - u) * math.pi)  # sai do baralho de costas e vira de frente
        im = carta(ch, CARD_H) if sx >= 0 else verso(260)
        x = lerp(150, CARD_X, ease(u))
        y = CARD_Y - math.sin(u * math.pi) * 90
        rot = [-2, 5, -6, 4, -3, 6][k % 6] if old else lerp(-10, -2, u)
        cola(img, im, x + old * 8, y + old * 5, rot, sx=max(0.02, abs(sx)))
    if vis:
        tf, ch, leg = vis[-1]
        if t >= tf + 0.35:
            cola(img, placa(leg, 50, WHITE, INK, maxw=440), 820, CARD_Y, 4, pop(t, tf + 0.35))


def cena_corrida(img, t):
    sh = 0.0
    for tc_ in (40.6, 42.7, 45.5):  # tremor nas batidas
        if tc_ <= t < tc_ + 0.35:
            sh = 14 * (1 - (t - tc_) / 0.35)
    jx, jy, _ = jit(t, sh, 3) if sh else (0, 0, 0)
    tc = torcida()
    bob = 8 * abs(math.sin(pose(t) * 9))
    img.paste(tc, (int((W - tc.width) / 2), int(-330 - bob)), tc)
    pc = pista_corrida()
    img.paste(pc, (int(jx), int(RY0 + jy)), pc)
    cartas_mesa(img, t)
    for k, nome in enumerate(MASC):  # a raia de cima por último (o Hurley sai por cima da pista)
        mascote_pista(img, nome, t, 235, k * 1.3)


def cena_corre(img, t):
    a = SCENES[5][0]
    cena_corrida(img, t)
    if t < a + 0.9:
        cola(img, placa("COMEÇOU!", 120, YEL, RED), 540, 260, -3, pop(t, a + 0.1))
    if t >= 40.6:
        cola(img, estouro("POW!", 280), casa_x(3) + 60, lane_y(2) - 150, -8, pop(t, 40.6))
    if t >= 41.0:
        cola(img, placa("DERRUBOU!", 80, RED, YEL), 540, 260, 3, pop(t, 41.0))


def cena_dq(img, t):
    a = SCENES[6][0]
    cena_corrida(img, t)
    if 42.7 <= t < 46.8:
        cola(img, estouro("DQ!", 280), casa_x(3), lane_y(2) - 110, 8, pop(t, 42.7))
    if 42.9 <= t < 44.5:
        cola(img, placa("CAIU JÁ CAÍDO?\nDESCLASSIFICADO!", 60, RED, YEL), 540, 250, -3, pop(t, 42.9))
    if 45.5 <= t < 46.8:
        cola(img, estouro("DQ!", 280), casa_x(2) + 60, RY0 + 40, -10, pop(t, 45.5))
    if 45.7 <= t < 47.0:
        cola(img, placa("SAIU DA PISTA?\nDESCLASSIFICADO!", 60, RED, YEL), 540, 250, 3, pop(t, 45.7))
    if t >= 47.0:  # gritaria na mesa
        k = 1 + 0.05 * math.sin(pose(t) * 22)
        cola(img, placa("GRITARIA\nGARANTIDA!", 80, YEL, RED), 540, 250, -3, pop(t, 47.0) * k)
        cola(img, estouro("AAAAH!", 260), 300, 1000, 10, pop(t, 47.2) * k)
        confete(img, t, 70, 9, 0, 1160)
    if t >= 47.7:
        cola(img, estouro("CHEGOU!", 240, (255, 255, 255)), 760, lane_y(1) - 230, -6, pop(t, 47.7))


# --- vencedor e comentário (cena 8)
def pilha_notas(img, x, base, n, cor_i, t, t0):
    k = int(n * ease(seg(t, t0, t0 + 1.4)))
    for i in range(k):
        v, cor = NOTAS[(cor_i + i) % 4]
        cola(img, nota(v, cor, 240), x + [0, 6, -5, 3][i % 4], base - i * 26, [-3, 2, -1, 4][i % 4])
    return base - k * 26


@lru_cache(None)
def coroa():
    """Coroa da Rainha Mum (do desenho oficial) para o jogador que ganhou."""
    im = Image.open(os.path.join(P, "p_mum.png")).convert("RGBA")
    c = im.crop((0, 0, im.width, int(im.height * 0.2)))
    c = c.crop(c.getbbox())
    return sombra(c.resize((240, int(c.height * 240 / c.width)), Image.LANCZOS), 6, (4, 8), 0.4, (0, 0, 0))


def cena_final_corrida(img, t):
    a = SCENES[7][0]
    u = t - a
    if u < 3.9:
        img.paste(torcida_fundo(0.35, 4), (0, 0))
        confete(img, t, 80, 5)
        cola(img, placa("DEPOIS DE 3 CORRIDAS...", 70, YEL, RED), 540, 300, -2, pop(t, a + 0.2))
        topos = []
        for k, (x, n) in enumerate(((240, 9), (540, 16), (840, 6))):
            topos.append(pilha_notas(img, x, 1450, n, k, t, a + 0.6 + k * 0.15))
            cola(img, placa(["JOGADOR 1", "VOCÊ!", "JOGADOR 3"][k], 40, WHITE, INK), x, 1545, 0)
        if u >= 2.0:
            cola(img, coroa(), 540, topos[1] - 100, -6, pop(t, a + 2.0))
            cola(img, placa("MAIS DINHEIRO\nVENCE!", 80, RED, YEL), 540, 560, 3, pop(t, a + 2.2))
            chuva_de_notas(img, t, a + 2.2, 14, 9, 540, topos[1] - 60, 0.8)
        return
    # tela VS: cachorro-quente ou rainha?
    v = ease(seg(t, a + 3.9, a + 4.3))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(30, 20, 30))
    off = (1 - v) * 1200
    d.polygon([(-off, 0), (W * 0.62 - off, 0), (W * 0.38 - off, H), (-off, H)], fill=(225, 55, 50))
    d.polygon([(W * 0.62 + off, 0), (W + off, 0), (W + off, H), (W * 0.38 + off, H)], fill=(120, 30, 90))
    for k in range(14):  # riscos de velocidade
        y = (k * 157 + pose(t) * 900) % H
        d.line((0 - off, y, W * 0.4 - off, y - 40), fill=(255, 120, 100), width=5)
        d.line((W * 0.6 + off, H - y, W + off, H - y - 40), fill=(170, 70, 140), width=5)
    jx, jy, jr = jit(t, 3, 21)
    cola(img, com_sombra("p_hurley.png", 760), 290 - off + jx, 1090 + jy, -6 + jr)
    cola(img, com_sombra("p_mum.png", 760, True), 800 + off - jx, 1070 - jy, 6 - jr)
    if u >= 4.1:
        cola(img, placa("VOCÊ APOSTARIA NO...", 66, WHITE, INK), 540, 300, -2, pop(t, a + 4.1))
    if u >= 4.6:
        cola(img, placa("CACHORRO-QUENTE", 52, YEL, RED), 280, 520, -6, pop(t, a + 4.6))
    if u >= 5.0:
        cola(img, estouro("OU", 220), 540, 900, 0, pop(t, a + 5.0) * (1 + 0.05 * math.sin(pose(t) * 12)))
    if u >= 5.4:
        cola(img, placa("OU NA RAINHA?", 52, YEL, PURPLE), 800, 640, 6, pop(t, a + 5.4))
    if u >= 6.4:
        b = 1 + 0.06 * abs(math.sin(pose(t) * 6))
        cola(img, placa("COMENTA AQUI!", 100, RED, YEL), 540, 1470, -3, pop(t, a + 6.4) * b)


# --- CTA (cena 9)
@lru_cache(None)
def caixa_img(w):
    return sombra(peca_w("caixa.png", w), 18, (12, 24), 0.55, (0, 0, 0))


def cena_cta(img, t):
    a = SCENES[8][0]
    img.paste(torcida_fundo(0.45, 3), (0, 0))
    confete(img, t, 60, 8)
    cola(img, logo_card(420), 540, 220, 0, pop(t, a + 0.1))
    jx, jy, jr = jit(t, 1.5, 5)
    cola(img, caixa_img(920), 540 + jx, 620 + jy, -3 + jr, pop(t, a + 0.4))
    if t >= a + 0.9:
        cola(img, placa("ALUGUE O HOT STREAK!", 76, RED, YEL), 540, 950, -2, pop(t, a + 0.9))
    if t >= a + 1.5:
        cola(img, placa("2 A 8 JOGADORES", 44, WHITE, INK), 300, 1100, -3, pop(t, a + 1.5))
    if t >= a + 1.8:
        cola(img, placa("5 DIAS DE JOGO", 44, YEL, RED), 780, 1100, 3, pop(t, a + 1.8))
    if t >= a + 2.3:
        cola(img, placa("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 40, WHITE, INK), 540, 1230, -1, pop(t, a + 2.3))
    if t >= a + 2.7:
        cola(img, placa("OU RECEBA EM CASA!", 40, (40, 140, 70), WHITE), 540, 1340, 2, pop(t, a + 2.7))
    if t >= a + 3.2:
        b = 1 + 0.04 * abs(math.sin(pose(t) * 5))
        cola(img, placa("LINK NA BIO · @SUAVEZ_BG", 66, YEL, RED), 540, 1480, -2, pop(t, a + 3.2) * b)


# ---------------------------------------------------------------- montagem
CENAS = [cena_gancho, cena_largada, cena_bilhetes, cena_risco, cena_secreta, cena_corre, cena_dq,
         cena_final_corrida, cena_cta]


@lru_cache(None)
def bandeira():
    """Faixa quadriculada inclinada (bandeira de chegada) usada na transição."""
    q = 90
    bw = q * 9
    im = Image.new("RGBA", (bw + H, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for j in range(H // q + 1):
        y = j * q
        sk = (H - y) * 0.45
        for i in range(9):
            x = sk + i * q
            d.polygon([(x, y), (x + q, y), (x + q - q * 0.45, y + q), (x - q * 0.45, y + q)],
                      fill=INK if (i + j) % 2 else WHITE)
    return im


def bandeirada(img, u):
    """Transição: bandeira quadriculada passando da esquerda para a direita."""
    if u <= 0 or u >= 1:
        return img
    b = bandeira()
    x = int(lerp(-b.width, W, u))
    img.paste(b, (x, 0), b)
    return img


def frame_at(t):
    i = scene_of(t)
    img = Image.new("RGBA", (W, H), (40, 110, 60, 255))
    CENAS[i](img, t)
    a, b = SCENES[i]
    if i == 0 and t > b - 0.1:
        img = Image.blend(img, Image.new("RGBA", img.size, WHITE + (255,)), 0.7 * seg(t, b - 0.1, b))
    if i == 1 and t < a + 0.1:
        img = Image.blend(img, Image.new("RGBA", img.size, WHITE + (255,)), 0.7 * (1 - seg(t, a, a + 0.1)))
    if i >= 2 and t < a + TR / 2:
        img = bandeirada(img, 0.5 + (t - a) / TR)
    if 1 <= i < len(SCENES) - 1 and t > b - TR / 2:
        img = bandeirada(img, (t - (b - TR / 2)) / TR)
    return img


# ---------------------------------------------------------------- roteiro, narração e legendas
ROTEIRO = [
    "Já apostou dinheiro num cachorro-quente? Prepara a carteira... e a garganta!",
    "Esse é o Hot Streak: quatro mascotes trapalhões correm, e vocês apostam em quem vai ganhar.",
    "Antes de cada corrida, cada um pega dois bilhetes de aposta: no mascote... ou em coisas bizarras, "
    "tipo 'alguém vai sair da pista?'",
    "E você escolhe: aposta segura... ou arriscada, que paga muito mais, mas pode até te fazer perder dinheiro!",
    "Aí vem a malandragem: cada jogador coloca uma carta secreta no baralho da corrida pra puxar a sardinha "
    "pro seu lado.",
    "Começou! As cartas viram uma a uma: o mascote corre, tropeça, dá meia-volta, invade a raia do outro "
    "e derruba geral!",
    "Caiu de novo quando já tava no chão, ou saiu da pista? Desclassificado! E a gritaria na mesa é garantida.",
    "Depois de três corridas, quem tiver mais dinheiro ganha. E aí, você apostaria no cachorro-quente "
    "ou na rainha? Comenta aqui!",
    "Aluga o Hot Streak na Sua Vez e chama a galera pra apostar! O link tá na bio.",
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
        for k, ch in enumerate(chunks):
            out.append((a + 0.3 + k * span, a + 0.3 + (k + 1) * span, ch))
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
    c = [(0.0, "crowd", 0.7), (0.25, "swoosh", 0.6), (0.4, "pop", 0.5), (2.4, "pop", 0.4), (2.5, "cash", 0.8),
         (3.9, "aah", 0.9), (5.5, "stinger", 0.6)]
    a = SCENES[1][0]
    c += [(a + 0.4, "pop", 0.5)] + [(a + 1.5 + k * 0.55, "pop", 0.35) for k in range(4)]
    c += [(a + 3.6, "bugle", 0.8), (a + 4.6, "whistle", 0.8), (a + 4.6, "crowd", 0.8), (a + 5.5, "pop", 0.5)]
    a = SCENES[2][0]
    c += [(a + 0.5, "pop", 0.4), (a + 0.8, "swoosh", 0.6), (a + 1.4, "pop", 0.35), (a + 3.0, "swoosh", 0.6),
          (a + 3.6, "pop", 0.35), (a + 4.6, "pop", 0.5), (a + 5.6, "boing", 0.5)]
    a = SCENES[3][0]
    c += [(a + 0.3, "pop", 0.4), (a + 2.2, "flip", 0.8), (a + 2.5, "pop", 0.4), (a + 2.8, "cash", 0.8),
          (a + 3.8, "swoosh", 0.6), (a + 4.4, "zap", 0.5), (a + 4.8, "buzzer", 0.5)]
    a = SCENES[4][0]
    c += [(a + 0.1, "swoosh", 0.6), (a + 0.4, "pop", 0.5), (a + 1.2, "pop", 0.3), (a + 1.8, "swoosh", 0.5),
          (a + 2.3, "shh", 0.8), (a + 3.2, "flip", 0.8), (a + 3.8, "swoosh", 0.5), (a + 4.4, "flip", 0.6),
          (a + 4.6, "pop", 0.5)]
    a = SCENES[5][0]
    c += [(a + 0.1, "whistle", 0.7), (a + 0.1, "crowd", 0.7)]
    c += [(tf, "flip", 0.8) for tf, _, _ in FLIPS]
    c += [(35.3, "swoosh", 0.4), (36.8, "tombo", 0.8), (38.3, "swoosh", 0.4), (39.8, "swoosh", 0.4),
          (40.6, "hit", 0.9), (40.7, "tombo", 0.6), (41.0, "crowd", 0.7), (42.7, "buzzer", 0.8), (43.0, "aah", 0.6),
          (45.5, "buzzer", 0.8), (47.0, "aah", 1.0), (47.7, "whistle", 0.7)]
    a = SCENES[7][0]
    c += [(a + 0.2, "pop", 0.5), (a + 0.6, "cash", 0.6), (a + 2.0, "ding", 0.5), (a + 2.2, "cash", 0.9),
          (a + 3.9, "stinger", 0.7), (a + 4.6, "pop", 0.4), (a + 5.0, "hit", 0.6), (a + 5.4, "pop", 0.4),
          (a + 6.4, "pop", 0.6)]
    a = SCENES[8][0]
    c += [(a + 0.1, "pop", 0.5), (a + 0.4, "swoosh", 0.6), (a + 0.9, "pop", 0.5), (a + 1.5, "pop", 0.35),
          (a + 1.8, "pop", 0.35), (a + 2.3, "pop", 0.35), (a + 2.7, "pop", 0.35), (a + 3.2, "cash", 0.7),
          (a + 7.5, "crowd", 0.6)]
    c += [(s[0] - TR / 2, "swoosh", 0.45) for s in SCENES[2:]]
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
    if scene_of(to) < len(SCENES) - 1:
        wm = logo_card(180)
        img.paste(wm, (W - wm.width - 30, 40), wm)
    if subs:
        for a_, b_, s in SUBS:
            if a_ <= t < b_:
                si = sub_img(s)
                img.paste(si, ((W - si.width) // 2, 1740 - si.height // 2), si)
    return img.convert("RGB").tobytes()


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def encode(out_path, wav, n, fn, args):
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, fr in enumerate(pool.imap(fn, args, chunksize=6)):
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
    ap.add_argument("--teste", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [Image.frombytes("RGB", (W, H), render_frame((int(round(x * FPS)), True))) for x in a.frame]
        ims[0].save(os.path.join(OUT, "frame.png"))
        cols = min(6, len(ims))
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (360 * cols, 640 * rows))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
        sheet.save(os.path.join(OUT, "frames.jpg"), quality=88)
        return
    wav = os.path.join(OUT, "trilha.wav")
    if a.teste:
        dur = 10.0
        som.build(wav, dur, cues=[c for c in CUES if c[0] < dur])
        n = int(dur * FPS)
        encode(os.path.join(OUT, "hs_teste.mp4"), wav, n, render_frame, [(j, True) for j in range(n)])
        return
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz, cues=CUES)
    with open(os.path.join(ROOT, "legendas.srt"), "w", encoding="utf-8") as f:
        for k, (a_, b_, s) in enumerate(SUBS, 1):
            ts = lambda x: f"{int(x // 3600):02}:{int(x // 60 % 60):02}:{int(x % 60):02},{int(round(x * 1000)) % 1000:03}"
            f.write(f"{k}\n{ts(a_)} --> {ts(b_)}\n{s}\n\n")
    n = int(DUR * FPS)
    if a.only != "limpo":
        encode(os.path.join(OUT, "hs_preview.mp4"), wav, n, render_frame, [(j, True) for j in range(n)])
    if a.only != "preview":
        encode(os.path.join(OUT, "hs_limpo.mp4"), wav, n, render_frame, [(j, False) for j in range(n)])


if __name__ == "__main__":
    main()
