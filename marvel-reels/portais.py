#!/usr/bin/env python3
"""Reels dos Marvel United do acervo + Multiverse – visual PORTAIS DO MULTIVERSO com pegada de filme de herói
(caixas 3D e miniaturas recortadas saindo de portais de faíscas, holofote, brilho de lente, granulado de cinema).

    python3 portais.py --frame 1 3 6     # quadros de teste (out/frames.jpg)
    python3 portais.py --only preview    # só a versão com legenda
    python3 portais.py                   # com e sem legenda (out/marvel_preview.mp4 e out/marvel_limpo.mp4)
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

import som_marvel as som

ROOT = os.path.dirname(os.path.abspath(__file__))
CX = os.path.join(ROOT, "assets", "caixas")
MI = os.path.join(ROOT, "assets", "minis")
FN = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
POSE = 12

WHITE, GOLD, RED = (255, 255, 255), (255, 200, 70), (220, 30, 50)
AZUL, LARANJA, ROXO = (90, 170, 255), (255, 150, 40), (150, 80, 255)
DRED = (120, 10, 20)
BANG, BUNGEE, POP = "Bangers-Regular.ttf", "Bungee-Regular.ttf", "Poppins-ExtraBold.ttf"
BASES = [("base", "MARVEL UNITED"), ("xmen", "X-MEN"), ("spider_geddon", "SPIDER-GEDDON")]
EXPANSOES = [("civil_war", "CIVIL WAR"), ("blue_team", "BLUE TEAM"), ("x_men_gold_team", "GOLD TEAM"),
             ("deadpool", "DEADPOOL"), ("rise_of_the_black_panther", "PANTERA NEGRA"),
             ("enter_the_spider_verse", "SPIDER-VERSE")]


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
    r = np.random.default_rng(int(t * POSE) * 31 + seed)
    return r.uniform(-a, a), r.uniform(-a, a), r.uniform(-a * 0.4, a * 0.4)


@lru_cache(None)
def font(n, s):
    return ImageFont.truetype(os.path.join(FN, n), s)


@lru_cache(None)
def peca(nome, h, pasta="cx"):
    p = os.path.join(CX if pasta == "cx" else MI, nome + ".png")
    im = Image.open(p).convert("RGBA")
    return im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)


@lru_cache(None)
def peca_w(nome, w, pasta="cx"):
    p = os.path.join(CX if pasta == "cx" else MI, nome + ".png")
    im = Image.open(p).convert("RGBA")
    return im.resize((int(w), max(2, int(im.height * w / im.width))), Image.LANCZOS)


@lru_cache(None)
def rim(nome, h, pasta="cx", cor=AZUL, w=12):
    """Peça com luz de recorte (rim light) colorida atrás, como em pôster de filme."""
    im = peca(nome, h, pasta)
    pad = w * 3
    big = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.alpha_composite(im, (pad, pad))
    a = big.getchannel("A").filter(ImageFilter.MaxFilter((w // 2) * 2 + 1)).filter(ImageFilter.GaussianBlur(w))
    g = Image.new("RGBA", big.size, cor + (255,))
    g.putalpha(a.point(lambda v: int(v * 0.85)))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(big)
    return out


def cola(img, im, x, y, rot=0.0, sc=1.0, alpha=1.0):
    if sc <= 0.02 or alpha <= 0.01:
        return
    if abs(sc - 1) > 0.003:
        im = im.resize((max(2, int(im.width * sc)), max(2, int(im.height * sc))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def cola_pe(img, im, x, chao, sc=1.0, rot=0.0, alpha=1.0, reflexo=True):
    """Cola com o pé em (x, chao) e reflexo no piso espelhado."""
    if sc <= 0.02:
        return
    if abs(sc - 1) > 0.003:
        im = im.resize((max(2, int(im.width * sc)), max(2, int(im.height * sc))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(x - im.width / 2), int(chao - im.height)))
    if reflexo:
        r = im.transpose(Image.FLIP_TOP_BOTTOM)
        a = np.asarray(r.getchannel("A")).astype(float)
        a *= np.linspace(0.32, 0, r.height)[:, None]
        r.putalpha(Image.fromarray(a.astype(np.uint8)))
        y = int(chao)
        if y < H:
            img.alpha_composite(r.crop((0, 0, r.width, min(r.height, H - y))) if y + r.height > H else r,
                                (int(x - im.width / 2), y))


@lru_cache(None)
def logo_card(width):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2, fill=WHITE)
    card.alpha_composite(lg, (pad, pad))
    return card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)


# ---------------------------------------------------------------- cosmos, portais, luz e cinema
@lru_cache(None)
def cosmos(seed=1):
    """Espaço do multiverso: degradê roxo-azul, nebulosas e estrelas (desenhado maior para dar parallax)."""
    w, h = W + 200, H + 200
    yy = np.linspace(0, 1, h)[:, None, None]
    a = (np.array((26, 6, 54)) * (1 - yy) + np.array((3, 8, 34)) * yy) * np.ones((1, w, 1))
    img = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rng = np.random.default_rng(seed)
    for _ in range(16):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(160, 460)
        c = [(120, 40, 220), (40, 110, 255), (255, 50, 140), (40, 200, 220)][rng.integers(4)]
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (38,))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(100)))
    d = ImageDraw.Draw(img)
    for _ in range(320):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(0.8, 2.8)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rng.uniform(110, 255))))
    return img


def fundo(img, t, cor_luz=None):
    c = cosmos()
    dx, dy = 100 + 60 * math.sin(t * 0.13), 100 + 80 * math.cos(t * 0.1)
    img.alpha_composite(c.crop((int(dx), int(dy), int(dx) + W, int(dy) + H)))
    if cor_luz:
        luz(img, 540, 1050, 560, cor_luz, 70)


@lru_cache(None)
def _glow(r, cor, a):
    s = int(r * 2 + 160)
    ov = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), fill=cor + (a,))
    return ov.filter(ImageFilter.GaussianBlur(r * 0.45))


def luz(img, cx, cy, r, cor, a=120):
    g = _glow(int(r) // 10 * 10 + 10, cor, a)
    img.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))


@lru_cache(None)
def anel_glow(r, cor):
    s = int(r * 2 + 140)
    ov = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((70, 70, s - 70, s - 70), outline=cor + (255,), width=max(8, r // 8))
    return ov.filter(ImageFilter.GaussianBlur(max(6, r // 10)))


CAPAS = {"base": "capas/marvel_united.jpg", "xmen": "capas/marvel_united_x_men.jpg",
         "civil_war": "capas/marvel_united_civil_war.jpg", "blue_team": "capas/marvel_united_x_men_blue_team.jpg",
         "x_men_gold_team": "fotos/capa_x-men-gold-team.jpg", "deadpool": "fotos/capa_deadpool.jpg",
         "rise_of_the_black_panther": "fotos/capa_rise-of-the-black-panther.jpg",
         "enter_the_spider_verse": "fotos/capa_enter-the-spider-verse.jpg",
         "spider_geddon": "fotos/capa_spider-geddon.jpg"}


@lru_cache(None)
def miolo_capa(nome, r):
    """Arte da capa recortada em disco (o que se vê do outro lado do portal), com borda escurecida."""
    im = Image.open(os.path.join(ROOT, "assets", CAPAS[nome])).convert("RGB")
    sq = min(im.width, im.height)
    k = int(sq * 0.08)  # tira a moldura da foto
    c = im.crop(((im.width - sq) // 2 + k, (im.height - sq) // 2 + k, (im.width + sq) // 2 - k,
                 (im.height + sq) // 2 - k)).resize((r * 2, r * 2), Image.LANCZOS).convert("RGBA")
    yy, xx = np.mgrid[0:r * 2, 0:r * 2] - r
    rad = np.hypot(xx, yy) / r
    a = np.clip((1 - rad) * 40, 0, 1) * 255
    vin = np.clip(1.15 - rad * 0.5, 0, 1)[..., None]
    rgb = (np.asarray(c)[..., :3] * vin).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, a.astype(np.uint8)]), "RGBA")


@lru_cache(None)
def miolo_vortice(r, cor):
    """O outro lado do portal: um pedaço de espaço com núcleo brilhante e redemoinho bem sutil."""
    s = r * 2
    yy, xx = np.mgrid[0:s, 0:s] - r
    ang = np.arctan2(yy, xx)
    rad = np.hypot(xx, yy) / r
    sw = 0.5 + 0.5 * np.sin(ang * 3 + rad * 9)
    nucleo = np.exp(-rad * 2.6)
    base = (np.array((10, 6, 30))[None, None, :] * (1 - nucleo[..., None]) + np.array(cor)[None, None, :] * nucleo[..., None]
            * 1.4 + np.array(cor)[None, None, :] * 0.18 * sw[..., None] * (1 - rad[..., None]))
    rng = np.random.default_rng(r)
    est = np.zeros((s, s))
    ys, xs = rng.integers(0, s, (2, int(s * s / 900)))
    est[ys, xs] = 255
    base = base + est[..., None]
    a = np.clip((1 - rad) * 40, 0, 1) * 255
    return Image.fromarray(np.dstack([np.clip(base, 0, 255), a]).astype(np.uint8), "RGBA")


def portal(img, cx, cy, r, t, seed=0, cor=LARANJA, capa=None, vortice=ROXO, abre=1.0):
    """Portal de faíscas girando. abre de 0 a 1 (abre com pulinho)."""
    if abre <= 0.01:
        return
    r = max(4, int(r * abre))
    g = anel_glow(r // 6 * 6 + 6, cor)
    img.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
    if capa:
        m = miolo_capa(capa, r)
    else:
        m = miolo_vortice(max(8, r // 8 * 8), vortice).rotate(-t * 25 % 360, resample=Image.BICUBIC)
        m = m.resize((r * 2, r * 2), Image.BILINEAR)
    img.alpha_composite(m, (int(cx - r), int(cy - r)))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    giro = pose(t) * 3.2
    n = int(70 + r * 0.5)
    for _ in range(n):  # faíscas tangentes à borda, girando
        a0 = rng.uniform(0, 2 * math.pi)
        a = a0 + giro * (1 + rng.uniform(-0.2, 0.2))
        rr = r + rng.uniform(-4, 18)
        L = rng.uniform(10, 38) * (r / 200) ** 0.5
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        c = (255, int(rng.uniform(150, 240)), int(rng.uniform(40, 120)))
        d.line((x, y, x - L * math.sin(a), y + L * math.cos(a)), fill=c, width=3)
    for _ in range(int(r * 0.12)):  # faíscas soltas voando
        a = rng.uniform(0, 2 * math.pi) + giro
        rr = r + 20 + ((pose(t) * 140 + rng.uniform(0, 160)) % 160)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=(255, 220, 140))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 230, 150), width=4)


def holofote(img, x, cor=(180, 210, 255), a=46):
    g = _holofote(cor, a)
    img.alpha_composite(g, (int(x - g.width / 2), 0))


@lru_cache(None)
def _holofote(cor, a):
    ov = Image.new("RGBA", (900, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(390, 0), (510, 0), (850, H), (50, H)], fill=cor + (a,))
    return ov.filter(ImageFilter.GaussianBlur(40))


def piso(img, y):
    """Piso preto espelhado com brilho na linha do horizonte."""
    ov = Image.new("RGBA", (W, H - int(y)), (2, 2, 8, 225))
    img.alpha_composite(ov, (0, int(y)))
    d = ImageDraw.Draw(img)
    d.line((0, y, W, y), fill=(120, 170, 255, 120), width=3)


def flare(img, x, y, s=1.0, a=1.0):
    if a <= 0:
        return
    ov = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    yy = 150
    for w_, al in ((26, 40), (10, 90), (3, 220)):
        d.line((0, yy, W, yy), fill=(120, 180, 255, int(al * a)), width=int(w_ * s))
    d.line((x, yy - 140 * s, x, yy + 140 * s), fill=(200, 230, 255, int(140 * a)), width=3)
    d.ellipse((x - 14 * s, yy - 14 * s, x + 14 * s, yy + 14 * s), fill=(255, 255, 255, int(255 * a)))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)), (0, int(y - 150)))


@lru_cache(None)
def grao_frames():
    out = []
    for k in range(6):
        rng = np.random.default_rng(k)
        n = np.clip(rng.normal(128, 10, (H // 3, W // 3)), 0, 255).astype(np.uint8)
        g = Image.fromarray(n).resize((W, H), Image.BILINEAR)
        out.append(np.asarray(g).astype(np.int16) - 128)
    return out


def cinema(img, t):
    """Granulado de filme (12 poses/s) e faixas pretas."""
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    a += grao_frames()[int(t * POSE) % 6][..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 70), fill=(0, 0, 0))
    d.rectangle((0, H - 70, W, H), fill=(0, 0, 0))
    return img


@lru_cache(None)
def letreiro(txt, size=96, cor=WHITE, glow=(90, 160, 255), f=BUNGEE, maxw=960):
    """Título de trailer com brilho."""
    lines = txt.split("\n")
    while max(font(f, size).getlength(l) for l in lines) > maxw and size > 30:
        size -= 4
    ft = font(f, size)
    lh = int(size * 1.15)
    w = int(max(ft.getlength(l) for l in lines)) + 80
    h = lh * len(lines) + 80
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        d.text((w / 2, 40 + lh * k + lh / 2), l, font=ft, fill=glow + (255,), anchor="mm")
    im = im.filter(ImageFilter.GaussianBlur(14))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        d.text((w / 2, 40 + lh * k + lh / 2), l, font=ft, fill=cor, anchor="mm")
    return im


@lru_cache(None)
def hq(txt, size=96, cor=WHITE, contorno=DRED, maxw=960):
    """Título no estilo HQ (Bangers com contorno grosso)."""
    lines = txt.split("\n")
    while max(font(BANG, size).getlength(l) for l in lines) > maxw - 40 and size > 30:
        size -= 4
    ft = font(BANG, size)
    lh = int(size * 1.02)
    sw = max(4, size // 10)
    w = int(max(ft.getlength(l) for l in lines)) + sw * 4 + 20
    h = lh * len(lines) + sw * 4 + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        y = sw * 2 + 10 + lh * k + lh / 2
        d.text((w / 2 + 6, y + 8), l, font=ft, fill=(0, 0, 0, 160), anchor="mm", stroke_width=sw, stroke_fill=(0, 0, 0, 160))
        d.text((w / 2, y), l, font=ft, fill=cor, anchor="mm", stroke_width=sw, stroke_fill=contorno)
    return im


@lru_cache(None)
def selo(txt, size=44, fundo=RED, letra=WHITE):
    f = font(BUNGEE, size)
    w = int(f.getlength(txt)) + size * 2
    h = int(size * 1.8)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 14, w + 10, h + 14), radius=h // 3, fill=(0, 0, 0, 120))
    d.rounded_rectangle((0, 0, w, h), radius=h // 3, fill=fundo)
    d.text((w / 2, h / 2 + 2), txt, font=f, fill=letra, anchor="mm")
    return im


def estouro(img, cx, cy, r, t, t0, cor=(255, 220, 60)):
    """Clarão de impacto (raios + círculo) que some rápido."""
    u = seg(t, t0, t0 + 0.4)
    if u <= 0 or u >= 1:
        return
    d = ImageDraw.Draw(img)
    rr = r * (0.4 + u)
    for k in range(14):
        a = k * math.pi / 7 + 0.2
        d.line((cx + rr * 0.3 * math.cos(a), cy + rr * 0.3 * math.sin(a), cx + rr * math.cos(a),
                cy + rr * math.sin(a)), fill=cor + (int(255 * (1 - u)),), width=8)


# ---------------------------------------------------------------- cenas
SCENES = [(0.0, 6.0), (6.0, 13.0), (13.0, 20.0), (20.0, 27.0), (27.0, 33.5), (33.5, 41.0), (41.0, 48.5),
          (48.5, 56.5), (56.5, 65.5)]
CTA = len(SCENES) - 1
DUR = SCENES[-1][1]
TR = 0.35
CHAO = 1420
HEROIS = ["heroi_1", "heroi_2", "heroi_3", "heroi_4", "heroi_5", "heroi_6", "heroi_7"]
VILOES = ["vilao_1", "vilao_2", "vilao_3"]


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if a <= t < b:
            return i
    return len(SCENES) - 1


def sai_do_portal(img, nome, px, py, x, chao, h, t, t0, d=0.5, pasta="mi", cor=AZUL, rot=0.0):
    """Peça saindo do portal: começa pequena no centro e salta para o lugar dela."""
    if t < t0:
        return
    u = seg(t, t0, t0 + d)
    v = ease(u)
    im = rim(nome, h, pasta, cor, 10)
    if u < 1:
        sc = lerp(0.25, 1.0, v)
        xx = lerp(px, x, v)
        yy = lerp(py + im.height * 0.5 * 0.25, chao, v) - math.sin(u * math.pi) * 160
        cola_pe(img, im, xx, yy, sc, rot * (1 - v) + 20 * (1 - v), reflexo=False)
    else:
        jx, jy, jr = jit(t, 1.2, hash(nome) % 50)
        cola_pe(img, im, x + jx, chao, 1.0, rot + jr)


def cena_gancho(img, t):
    a = SCENES[0][0]
    u = t - a
    fundo(img, t)
    holofote(img, 540)
    piso(img, CHAO)
    abre = out_back(seg(t, a + 0.15, a + 0.8)) if u < 0.8 else 1.0
    portal(img, 540, 900, 300, t, 1, LARANJA, "base", ROXO, abre)
    luz(img, 540, 900, 380, (255, 140, 40), int(60 * abre))
    for k, (n, x, h) in enumerate((("heroi_1", 300, 360), ("heroi_3", 780, 380), ("heroi_2", 540, 470))):
        sai_do_portal(img, n, 540, 900, x, CHAO, h, t, a + 1.2 + k * 0.5)
    flare(img, 760, 640, 1.0, 0.8 * seg(t, a + 1.0, a + 1.5))
    cola(img, hq("JÁ IMAGINOU OS HERÓIS\nDA MARVEL NA SUA MESA?", 96), 540, 330, -2, pop(t, a + 0.0, 0.25))


def cena_coop(img, t):
    a = SCENES[1][0]
    u = t - a
    fundo(img, t)
    piso(img, CHAO)
    portal(img, 260, 760, 170, t, 2, AZUL, "xmen", (40, 120, 255), out_back(seg(t, a, a + 0.5)))
    portal(img, 820, 760, 170, t, 3, (255, 60, 60), None, (200, 30, 40), out_back(seg(t, a + 2.2, a + 2.7)))
    cola(img, hq("MARVEL UNITED", 120, WHITE, (20, 60, 160)), 540, 250, -2, pop(t, a + 0.2))
    if u >= 0.8:
        cola(img, selo("JOGO COOPERATIVO", 46, (30, 110, 220)), 540, 420, 2, pop(t, a + 0.8))
    for k, (n, x, h) in enumerate((("heroi_4", 110, 300), ("heroi_6", 250, 340), ("heroi_5", 400, 320))):
        sai_do_portal(img, n, 260, 760, x, CHAO, h, t, a + 1.1 + k * 0.3)
    for k, (n, x, h) in enumerate((("vilao_2", 690, 360), ("vilao_1", 860, 400), ("vilao_3", 1000, 340))):
        sai_do_portal(img, n, 820, 760, x, CHAO, h, t, a + 2.8 + k * 0.3, cor=(255, 70, 50))
    if u >= 3.8:
        cola(img, letreiro("VOCÊS", 72, WHITE, AZUL), 250, 1540, 0, pop(t, a + 3.8))
        cola(img, letreiro("×", 90, WHITE, (255, 200, 80)), 540, 1540, 0, pop(t, a + 4.0))
        cola(img, letreiro("O VILÃO", 72, WHITE, (255, 60, 60)), 840, 1540, 0, pop(t, a + 4.2))


def cena_combo(img, t):
    a = SCENES[2][0]
    u = t - a
    fundo(img, t, (60, 40, 200))
    cola(img, hq("O SEGREDO: COMBO!", 110, (255, 220, 60), DRED), 540, 250, -2, pop(t, a + 0.1))
    # mão de cartas entra de baixo
    v = ease(seg(t, a + 0.3, a + 0.9))
    jx, jy, jr = jit(t, 1.5, 7)
    cola(img, peca_w("mao_cartas", 1000, "mi"), 540 + jx, lerp(2200, 1400, v) + jy, -3 + jr)
    # duas fichas de símbolo se juntam: a sua + a do amigo
    sx = ease(seg(t, a + 2.0, a + 2.6))
    cola(img, peca_w("simbolo_2", 340, "mi"), lerp(-300, 330, sx), 760, -6, 1.0)
    cola(img, peca_w("simbolo_1", 340, "mi"), lerp(1400, 760, sx), 760, 6, 1.0)
    if u >= 2.0:
        cola(img, selo("SUA CARTA", 34, (30, 110, 220)), 330, 600, -4, pop(t, a + 2.2))
        cola(img, selo("CARTA DO AMIGO", 34, (120, 60, 200)), 760, 600, 4, pop(t, a + 2.5))
    if u >= 2.7:
        estouro(img, 545, 760, 260, t, a + 2.7)
        cola(img, letreiro("+", 140, WHITE, (255, 200, 80)), 545, 760, 0, pop(t, a + 2.7))
    if u >= 3.6:
        b = 1 + 0.05 * abs(math.sin(pose(t) * 6))
        cola(img, hq("UM HERÓI AJUDA O OUTRO!", 80), 540, 1000, 2, pop(t, a + 3.6) * b)


def cena_vilao(img, t):
    a = SCENES[3][0]
    u = t - a
    fundo(img, t)
    vermelho = seg(t, a + 2.4, a + 2.8)
    if vermelho > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (180, 0, 20, int(70 * vermelho))))
    piso(img, CHAO)
    for k in range(3):  # contador de cartas dos heróis
        t0 = a + 0.3 + k * 0.6
        if t >= t0:
            cola(img, selo(f"CARTA {k + 1}", 40, (30, 110, 220)), 250 + k * 290, 420, 0, pop(t, t0))
    cola(img, hq("A CADA 3 CARTAS...", 96), 540, 260, -2, pop(t, a + 0.1))
    if u >= 2.4:
        portal(img, 540, 900, 260, t, 4, (255, 50, 50), None, (160, 20, 30), out_back(seg(t, a + 2.4, a + 2.9)))
        sai_do_portal(img, "vilao_2", 540, 900, 540, CHAO, 560, t, a + 2.7, cor=(255, 60, 40))
        if u < 4.6:
            cola(img, hq("O VILÃO AGE!", 130, (255, 80, 60), (40, 0, 0)), 540, 1530, 3, pop(t, a + 2.6))
    if u >= 4.6:
        cola(img, selo("MISSÕES CUMPRIDAS = VILÃO VULNERÁVEL", 30, (20, 140, 70)), 540, 1530, -1, pop(t, a + 4.6))
    if u >= 5.6:  # os heróis partem pra cima
        sai_do_portal(img, "heroi_6", 120, 700, 230, CHAO, 380, t, a + 5.6)
        estouro(img, 500, 1050, 300, t, a + 6.0, (255, 230, 120))
        cola(img, hq("POW!", 150, (255, 230, 60), DRED), 760, 1080, 12, pop(t, a + 6.0))


def cena_bases(img, t):
    a = SCENES[4][0]
    fundo(img, t, (40, 80, 220))
    cola(img, hq("3 JOGOS BASE", 120, WHITE, (20, 60, 160)), 540, 250, -2, pop(t, a + 0.1))
    for k, (n, nome) in enumerate(BASES):
        t0 = a + 0.6 + k * 1.3
        cx, cy = 540, 610 + k * 380
        cxp = 270 if k % 2 == 0 else 810
        portal(img, cxp, cy, 150, t, 10 + k, LARANJA, n, ROXO, out_back(seg(t, t0, t0 + 0.4)))
        if t >= t0 + 0.2:
            v = ease(seg(t, t0 + 0.2, t0 + 0.7))
            jx, jy, jr = jit(t, 1.5, 11 + k)
            xx = lerp(cxp, 810 if k % 2 == 0 else 270, v)
            cola(img, rim(n, 360, "cx", AZUL, 10), xx + jx, cy + jy, (-6 if k % 2 == 0 else 6) * v + jr, lerp(0.3, 1, v))
            if v >= 1:
                cola(img, selo(f"FASE {k + 1}: {nome}", 32, (30, 110, 220)), cxp, cy + 150, 0, pop(t, t0 + 0.7))


def cena_expansoes(img, t):
    a = SCENES[5][0]
    u = t - a
    fundo(img, t, (150, 40, 200))
    cola(img, hq("+ 6 EXPANSÕES", 120, (255, 220, 60), DRED), 540, 250, -2, pop(t, a + 0.1))
    for k, (n, nome) in enumerate(EXPANSOES):
        t0 = a + 0.5 + k * 0.55
        x, y = 290 + (k % 2) * 500, 620 + (k // 2) * 360
        portal(img, x, y, 120, t, 20 + k, LARANJA, n, ROXO, out_back(seg(t, t0, t0 + 0.35)) * (1 - seg(t, t0 + 0.5,
                                                                                                         t0 + 0.8)))
        if t >= t0 + 0.2:
            v = ease(seg(t, t0 + 0.2, t0 + 0.6))
            jx, jy, jr = jit(t, 1.5, 21 + k)
            if u < 5.4:
                cola(img, rim(n, 270, "cx", (200, 120, 255), 8), x + jx, y + jy, [-5, 5][k % 2] + jr, lerp(0.3, 1, v))
                if v >= 1:
                    cola(img, selo(nome, 28, (120, 50, 200)), x, y + 140, 0, pop(t, t0 + 0.6))
            else:  # todas giram para o centro: dá pra misturar
                w_ = ease(seg(t, a + 5.4, a + 6.3))
                ang = k * math.pi / 3 + w_ * 4
                rr = lerp(math.hypot(x - 540, y - 1000), 160, w_)
                cola(img, rim(n, 270, "cx", (200, 120, 255), 8), 540 + rr * math.cos(ang), 1000 + rr * math.sin(ang),
                     w_ * 200 + k * 20, lerp(1, 0.55, w_))
    if u >= 5.8:
        estouro(img, 540, 1000, 340, t, a + 6.3)
        cola(img, hq("DÁ PRA MISTURAR TUDO!", 90), 540, 1530, 2, pop(t, a + 5.8))


def cena_promo(img, t):
    a = SCENES[6][0]
    u = t - a
    fundo(img, t, (220, 60, 40))
    cola(img, hq("A DICA DE OURO:", 100, (255, 220, 60), DRED), 540, 240, -2, pop(t, a + 0.1))
    itens = [("base", 270, 760, 380, -8, "1 BASE"), ("deadpool", 810, 760, 320, 8, "+ EXPANSÃO"),
             ("enter_the_spider_verse", 540, 1040, 340, 0, "+ EXPANSÃO")]
    for k, (n, x, y, h, r, tag) in enumerate(itens):
        t0 = a + 0.7 + k * 0.7
        if t < t0:
            continue
        v = ease(seg(t, t0, t0 + 0.45))
        jx, jy, jr = jit(t, 1.5, 31 + k)
        cola(img, rim(n, h, "cx", (255, 170, 80), 10), lerp(540, x, v) + jx, lerp(-300, y, v) + jy, r + jr)
        cola(img, selo(tag, 34, RED), x, y - h / 2 - 20, 0, pop(t, t0 + 0.4))
    if u >= 3.4:
        b = 1 + 0.05 * abs(math.sin(pose(t) * 6))
        cola(img, selo("3 CAIXAS = 7 DIAS DE JOGO!", 50, RED), 540, 1340, -2, pop(t, a + 3.4) * b)
    if u >= 4.6:
        cola(img, selo("PELO MESMO PREÇO", 40, (20, 140, 70)), 540, 1460, 2, pop(t, a + 4.6))
    if u >= 5.6:
        cola(img, letreiro("5 CAIXAS = 10 DIAS   ·   7 CAIXAS = 15 DIAS", 34, GOLD, (255, 120, 40)), 540, 1560, 0,
             pop(t, a + 5.6))


def cena_multiverse(img, t):
    a = SCENES[7][0]
    u = t - a
    fundo(img, t)
    abre = out_back(seg(t, a + 0.3, a + 1.2)) if u < 1.2 else 1.0
    tremor = 6 * (1 - seg(t, a + 1.2, a + 2.4)) if u > 0.3 else 0
    jx, jy, _ = jit(t, tremor, 77)
    luz(img, 540, 880, 520, (90, 140, 255), int(90 * abre))
    portal(img, 540 + jx, 880 + jy, 420, t, 40, (120, 200, 255), None, (60, 40, 200), abre)
    if u >= 0.9:
        v = ease(seg(t, a + 0.9, a + 1.8))
        cola(img, rim("multiverse", 760, "cx", (130, 200, 255), 16), 540 + jx, 900 + jy, lerp(-20, -3, v), lerp(0.2, 1, v))
        flare(img, 700, 620, 1.2, seg(t, a + 1.6, a + 2.0))
    cola(img, letreiro("VEM AÍ...", 90, WHITE, (120, 180, 255)), 540, 230, 0, pop(t, a + 0.1))
    if 2.0 <= u < 4.2:
        cola(img, selo("EM BREVE NA SUA VEZ", 44, RED), 540, 1380, -2, pop(t, a + 2.0))
    if u >= 4.2:  # chamada para comentar: dois heróis, um de cada lado
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(120 * seg(t, a + 4.2, a + 4.6)))))
        sai_do_portal(img, "heroi_1", 540, 880, 220, 1640, 420, t, a + 4.3)
        sai_do_portal(img, "heroi_3", 540, 880, 860, 1640, 420, t, a + 4.5)
        cola(img, hq("QUAL DUPLA DE HERÓIS\nVOCÊ MONTARIA?", 92), 540, 560, 2, pop(t, a + 4.4))
        b = 1 + 0.06 * abs(math.sin(pose(t) * 6))
        cola(img, selo("COMENTA AQUI!", 64, RED), 540, 1180, -3, pop(t, a + 5.4) * b)


def cena_cta(img, t):
    a = SCENES[CTA][0]
    fundo(img, t, (60, 60, 220))
    portal(img, 540, 760, 330, t, 50, LARANJA, None, ROXO, out_back(seg(t, a, a + 0.5)))
    cola(img, logo_card(430), 540, 200, 0, pop(t, a + 0.1))
    caixas = [("xmen", 260, 800, 300, -10), ("spider_geddon", 820, 800, 300, 10), ("base", 540, 760, 400, 0)]
    for k, (n, x, y, h, r) in enumerate(caixas):
        t0 = a + 0.4 + k * 0.25
        if t >= t0:
            v = ease(seg(t, t0, t0 + 0.4))
            jx, jy, jr = jit(t, 1.2, 60 + k)
            cola(img, rim(n, h, "cx", AZUL, 10), lerp(540, x, v) + jx, lerp(760, y, v) + jy, r * v + jr, lerp(0.3, 1, v))
    if t >= a + 1.3:
        cola(img, hq("ALUGUE MARVEL UNITED!", 100, WHITE, (20, 60, 160)), 540, 1060, -2, pop(t, a + 1.3))
    if t >= a + 1.8:
        cola(img, selo("COOPERATIVO · 40 MIN", 34, (30, 110, 220)), 300, 1200, -2, pop(t, a + 1.8))
    if t >= a + 2.1:
        cola(img, selo("R$ 30 · 5 DIAS", 34, RED), 800, 1200, 2, pop(t, a + 2.1))
    if t >= a + 2.5:
        cola(img, selo("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 30, (40, 40, 70)), 540, 1310, -1, pop(t, a + 2.5))
    if t >= a + 2.9:
        cola(img, selo("OU RECEBA EM CASA!", 32, (20, 140, 70)), 540, 1410, 1, pop(t, a + 2.9))
    if t >= a + 3.4:
        b = 1 + 0.04 * abs(math.sin(pose(t) * 5))
        cola(img, selo("LINK NA BIO · @SUAVEZ_BG", 50, (255, 200, 60), (40, 10, 10)), 540, 1530, -2, pop(t, a + 3.4) * b)


CENAS = [cena_gancho, cena_coop, cena_combo, cena_vilao, cena_bases, cena_expansoes, cena_promo, cena_multiverse,
         cena_cta]


def frame_at(t):
    i = scene_of(t)
    img = Image.new("RGBA", (W, H), (4, 4, 14, 255))
    CENAS[i](img, t)
    a, b = SCENES[i]
    f = 0.0  # transição: clarão de portal entre as cenas
    if i > 0 and t < a + TR / 2:
        f = 1 - (t - a) / (TR / 2)
    if i < len(SCENES) - 1 and t > b - TR / 2:
        f = (t - (b - TR / 2)) / (TR / 2)
    if f > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (230, 220, 255, int(220 * f))))
    return cinema(img, t)


# ---------------------------------------------------------------- narração, legendas e render
ROTEIRO = [
    "Já imaginou reunir os maiores heróis da Marvel… na mesa da sua casa?",
    "Esse é o Marvel United: um jogo cooperativo em que vocês são os heróis contra um vilão que o próprio jogo controla.",
    "Na sua vez, você joga uma carta e soma os símbolos com a do amigo anterior. É o combo: um herói ajuda o outro!",
    "A cada três cartas dos heróis, o vilão age. Cumpram as missões pra deixar ele vulnerável… e partam pra cima!",
    "Aqui na Sua Vez tem três jogos base: o Marvel United, o X-Men e o Spider-Geddon.",
    "E seis expansões: Civil War, Blue Team, Gold Team, Deadpool, Pantera Negra e Spider-Verse. E dá pra misturar tudo!",
    "A dica: pega um jogo base e duas expansões, que são três caixas… e você fica sete dias jogando, pelo mesmo preço!",
    "E vem aí o Multiverse, com heróis de outras dimensões! Qual dupla de heróis você montaria? Comenta aqui!",
    "Cada caixa sai por 30 reais. Aluga na Sua Vez, o link tá na bio!",
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
        span = (b - a - 0.6) / len(chunks)
        for k, ch in enumerate(chunks):
            out.append((a + 0.3 + k * span, a + 0.3 + (k + 1) * span, ch))
    return out


SUBS = default_subs()
TIMELINE_PATH = os.path.join(ROOT, "narracao", "timeline.json")
TIMELINE = json.load(open(TIMELINE_PATH, encoding="utf-8")) if os.path.exists(TIMELINE_PATH) else None
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
    c = [(S[0] + 0.15, "portal", 0.9), (S[0] + 0.0, "pop", 0.4)] + [(S[0] + 1.2 + k * 0.5, "swoosh", 0.5) for k in range(3)]
    c += [(S[0] + 2.6, "impacto", 0.6), (S[0] + 5.6, "braam", 0.8)]
    c += [(S[1], "portal", 0.6), (S[1] + 0.2, "pop", 0.4), (S[1] + 0.8, "pop", 0.35)]
    c += [(S[1] + 1.1 + k * 0.3, "swoosh", 0.4) for k in range(3)] + [(S[1] + 2.2, "portal", 0.6)]
    c += [(S[1] + 2.8 + k * 0.3, "swoosh", 0.4) for k in range(3)] + [(S[1] + 4.0, "impacto", 0.6)]
    c += [(S[2] + 0.1, "pop", 0.4), (S[2] + 0.3, "swoosh", 0.5), (S[2] + 2.0, "swoosh", 0.5), (S[2] + 2.7, "impacto", 0.8),
          (S[2] + 3.6, "pop", 0.5)]
    c += [(S[3] + 0.1, "pop", 0.4)] + [(S[3] + 0.3 + k * 0.6, "flip", 0.7) for k in range(3)]
    c += [(S[3] + 2.4, "braam", 0.9), (S[3] + 2.4, "portal", 0.6), (S[3] + 4.6, "ding", 0.5), (S[3] + 5.6, "swoosh", 0.5),
          (S[3] + 6.0, "impacto", 0.9)]
    c += [(S[4] + 0.1, "pop", 0.4)] + [(S[4] + 0.6 + k * 1.3, "portal", 0.5) for k in range(3)]
    c += [(S[4] + 1.3 + k * 1.3, "pop", 0.4) for k in range(3)]
    c += [(S[5] + 0.1, "pop", 0.4)] + [(S[5] + 0.5 + k * 0.55, "portal", 0.35) for k in range(6)]
    c += [(S[5] + 5.4, "riser", 0.5), (S[5] + 6.3, "impacto", 0.8)]
    c += [(S[6] + 0.1, "pop", 0.4)] + [(S[6] + 0.7 + k * 0.7, "swoosh", 0.5) for k in range(3)]
    c += [(S[6] + 3.4, "cash", 0.8), (S[6] + 4.6, "ding", 0.4), (S[6] + 5.6, "pop", 0.3)]
    c += [(S[7] - 1.6, "riser", 0.7), (S[7] + 0.3, "portal", 1.0), (S[7] + 1.2, "braam", 1.0), (S[7] + 2.0, "pop", 0.4),
          (S[7] + 4.3, "swoosh", 0.5), (S[7] + 5.4, "pop", 0.6), (S[7] + 5.5, "crowd", 0.4)]
    c += [(S[8], "portal", 0.6), (S[8] + 0.1, "pop", 0.5)] + [(S[8] + 0.4 + k * 0.25, "swoosh", 0.4) for k in range(3)]
    c += [(S[8] + x, "pop", 0.35) for x in (1.3, 1.8, 2.1, 2.5, 2.9)] + [(S[8] + 3.4, "cash", 0.6)]
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
        wm = logo_card(170)
        img.alpha_composite(wm, (W - wm.width - 30, 90))
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
        encode(os.path.join(OUT, "marvel_preview.mp4"), wav, n, [(j, True) for j in range(n)])
    if a.only != "preview":
        encode(os.path.join(OUT, "marvel_limpo.mp4"), wav, n, [(j, False) for j in range(n)])


if __name__ == "__main__":
    main()
