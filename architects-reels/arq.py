#!/usr/bin/env python3
"""Reels do 7 Wonders Arquitetos – estilo "planta de arquitetura" (blueprint).

As peças reais do jogo (cartas, fichas, maravilha) entram sobre uma folha azul de
projeto; a maravilha começa como desenho técnico e vai sendo construída etapa por etapa.

    python3 arq.py --frame 12.3     # um quadro em out/frame.png
    python3 arq.py --only preview   # prévia com legendas
    python3 arq.py                  # com e sem legendas
"""
import argparse
import json
import math
import os
import subprocess
from functools import lru_cache
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
import trilha_arq as som  # noqa: E402

PECAS = os.path.join(ROOT, "assets", "pecas")
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
FPS = 30
DUR = 66.0

BP = (22, 70, 136)
BP_DARK = (10, 38, 84)
LINE = (214, 232, 255)
WHITE = (255, 255, 255)
GOLD = (246, 196, 70)
RED = (222, 56, 52)
INK = (12, 28, 60)


# ---------------------------------------------------------------- utilidades
def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.7):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


@lru_cache(None)
def font(name, size, var=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if var:
        f.set_variation_by_name(var)
    return f


HAND = "ArchitectsDaughter-Regular.ttf"
CINZEL = "Cinzel-VF.ttf"
POP = "Poppins-ExtraBold.ttf"


def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


@lru_cache(None)
def piece(name):
    return Image.open(os.path.join(PECAS, name)).convert("RGBA")


@lru_cache(None)
def sized(name, height):
    im = piece(name)
    return im.resize((max(2, int(im.width * height / im.height)), int(height)), Image.LANCZOS)


@lru_cache(None)
def sized_w(name, width):
    im = piece(name)
    return im.resize((int(width), max(2, int(im.height * width / im.width))), Image.LANCZOS)


def paste_c(img, im, x, y, rot=0.0, scale=1.0, alpha=1.0, sx=1.0):
    if scale <= 0.02 or alpha <= 0.01 or abs(sx) < 0.02:
        return
    if abs(scale - 1) > 0.002 or abs(sx - 1) > 0.002:
        im = im.resize((max(2, int(im.width * scale * abs(sx))), max(2, int(im.height * scale))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)


@lru_cache(None)
def shadowed(name, height, kind="h"):
    """Peça com sombra suave (fica "apoiada" na folha)."""
    im = sized(name, height) if kind == "h" else sized_w(name, height)
    pad = 40
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * 0.55)), (pad + 10, pad + 16))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(12)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


@lru_cache(None)
def card_img(name, height):
    """Carta com bordinha branca (esconde sobras do recorte) e sombra."""
    im = sized(name, height)
    b = max(4, int(height * 0.012))
    base = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), (0, 0, 0, 0))
    ImageDraw.Draw(base).rounded_rectangle((0, 0, base.width - 1, base.height - 1), radius=int(height * 0.05),
                                           fill=(250, 248, 242, 255))
    base.alpha_composite(im, (b, b))
    pad = 40
    out = Image.new("RGBA", (base.width + pad * 2, base.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(base.getchannel("A").point(lambda v: int(v * 0.5)), (pad + 10, pad + 16))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 255))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(12)))
    out.alpha_composite(sh)
    out.alpha_composite(base, (pad, pad))
    return out


@lru_cache(None)
def photo_pin(name, height, tape_rot=0):
    """Foto de tabuleiro presa na planta com fita."""
    im = Image.open(os.path.join(PECAS, name)).convert("RGBA")
    im = im.resize((int(im.width * height / im.height), height), Image.LANCZOS)
    b = 12
    base = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), (255, 255, 255, 255))
    base.alpha_composite(im, (b, b))
    pad = 50
    out = Image.new("RGBA", (base.width + pad * 2, base.height + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(Image.new("L", base.size, 120), (pad + 8, pad + 14))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 255))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(10)))
    out.alpha_composite(sh)
    out.alpha_composite(base, (pad, pad))
    tape = Image.new("RGBA", (int(base.width * 0.42), 34), (250, 240, 200, 170))
    tape = tape.rotate(tape_rot, expand=True)
    out.alpha_composite(tape, (pad + base.width // 2 - tape.width // 2, pad - 18))
    return out


# ---------------------------------------------------------------- fundo (folha de projeto)
@lru_cache(None)
def background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((x - W / 2) / W, (y - H / 2) / H)
    base = np.array(BP, np.float32)[None, None] * (1.08 - 0.55 * r[..., None] ** 2)
    rng = np.random.default_rng(3)
    base += rng.normal(0, 3.2, (H, W, 1))
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for gx in range(0, W, 36):
        d.line((gx, 0, gx, H), fill=LINE + (34 if gx % 180 else 70,), width=1 if gx % 180 else 2)
    for gy in range(0, H, 36):
        d.line((0, gy, W, gy), fill=LINE + (34 if gy % 180 else 70,), width=1 if gy % 180 else 2)
    d.rectangle((24, 24, W - 25, H - 25), outline=LINE + (150,), width=3)
    d.rectangle((36, 36, W - 37, H - 37), outline=LINE + (90,), width=1)
    # carimbo de projeto no canto
    f = font(HAND, 26)
    d.rectangle((48, 48, 420, 150), outline=LINE + (150,), width=2)
    d.line((48, 98, 420, 98), fill=LINE + (120,), width=1)
    d.text((62, 56), "PROJETO: MARAVILHA Nº 7", font=f, fill=LINE + (200,))
    d.text((62, 106), "ARQUITETO: VOCÊ  ·  ESC. 1:25 MIN", font=f, fill=LINE + (170,))
    img = img.convert("RGBA")
    img.alpha_composite(ov)
    return img.convert("RGB")


# ---------------------------------------------------------------- tipografia
@lru_cache(None)
def title_img(text, size=84, fill=WHITE, maxw=980):
    f = font(CINZEL, size, "Black")
    lines = wrap(text, f, maxw)
    lh = int(size * 1.12)
    w = int(max(f.getlength(l) for l in lines)) + 40
    h = lh * len(lines) + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((w / 2 + 5, 20 + lh * i + lh / 2 + 7), l, font=f, fill=INK + (200,), anchor="mm")
        d.text((w / 2, 20 + lh * i + lh / 2), l, font=f, fill=fill, anchor="mm", stroke_width=3, stroke_fill=INK)
    return im


@lru_cache(None)
def note_img(text, size=54, maxw=820, color=WHITE, underline=False):
    f = font(HAND, size)
    lines = wrap(text, f, maxw)
    lh = int(size * 1.2)
    w = int(max(f.getlength(l) for l in lines)) + 30
    h = lh * len(lines) + 30
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((w / 2 + 3, 15 + lh * i + lh / 2 + 3), l, font=f, fill=INK + (170,), anchor="mm")
        d.text((w / 2, 15 + lh * i + lh / 2), l, font=f, fill=color, anchor="mm")
    if underline:
        lw = f.getlength(lines[-1])
        yy = 15 + lh * len(lines) - 6
        pts = [(w / 2 - lw / 2 + k * lw / 20, yy + 4 * math.sin(k * 1.3)) for k in range(21)]
        d.line(pts, fill=color, width=4)
    return im


@lru_cache(None)
def stamp_img(text, size=96, color=RED):
    f = font(CINZEL, size, "Black")
    tw = f.getlength(text)
    w, h = int(tw + size * 1.0), int(size * 1.75)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, h - 5), radius=18, outline=color + (255,), width=10)
    d.rounded_rectangle((20, 20, w - 21, h - 21), radius=10, outline=color + (255,), width=4)
    d.text((w / 2, h / 2 + 4), text, font=f, fill=color + (255,), anchor="mm")
    # textura de tinta falhada
    rng = np.random.default_rng(len(text))
    a = np.asarray(im.getchannel("A"), np.float32)
    holes = rng.random(a.shape) < 0.05
    a = a * np.where(holes, 0.25, 1.0)
    noise = cv2.GaussianBlur(rng.random(a.shape).astype(np.float32), (0, 0), 3)
    a = a * np.clip(0.55 + noise * 0.9, 0, 1)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


@lru_cache(None)
def tag_img(text, size=48, bg=WHITE, fg=INK):
    f = font(POP, size)
    w, h = int(f.getlength(text)) + 70, int(size * 1.65)
    im = Image.new("RGBA", (w + 12, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 12, w + 8, h + 12), radius=h // 2, fill=(0, 0, 0, 110))
    d.rounded_rectangle((0, 0, w, h), radius=h // 2, fill=bg)
    d.text((w / 2, h / 2 + 2), text, font=f, fill=fg, anchor="mm")
    return im


@lru_cache(None)
def logo_card(width):
    lg = Image.open(os.path.join(ROOT, "assets", "logo_suavez.png")).convert("RGBA")
    pad = int(lg.width * 0.06)
    card = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2,
                                           fill=(255, 255, 255, 255), outline=INK, width=8)
    card.alpha_composite(lg, (pad, pad))
    return card.resize((int(width), int(card.height * width / card.width)), Image.LANCZOS)


@lru_cache(None)
def laurel(text, r=95, fill=GOLD):
    """Medalha de pontos (+3)."""
    S = r * 2 + 30
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    d.ellipse((c - r + 6, c - r + 10, c + r + 6, c + r + 10), fill=(0, 0, 0, 120))
    d.ellipse((c - r, c - r, c + r, c + r), fill=fill, outline=INK, width=7)
    d.ellipse((c - r + 16, c - r + 16, c + r - 16, c + r - 16), outline=(255, 245, 210), width=4)
    d.text((c, c + 4), text, font=font(CINZEL, int(r * 0.85), "Black"), fill=INK, anchor="mm")
    return im


def element_img(kind, args):
    return {"title": title_img, "note": note_img, "stamp": stamp_img, "tag": tag_img, "logo": logo_card,
            "laurel": laurel}[kind](*args)


# ---------------------------------------------------------------- desenho técnico da maravilha
@lru_cache(None)
def lineart(name, width):
    im = sized_w(name, width)
    a = np.asarray(im)
    g = cv2.cvtColor(a[..., :3], cv2.COLOR_RGB2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 90, 210)
    edge_a = cv2.dilate((a[..., 3] > 128).astype(np.uint8) * 255, np.ones((3, 3), np.uint8)) - \
        cv2.erode((a[..., 3] > 128).astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
    e = np.maximum(e, edge_a)
    e = cv2.GaussianBlur(e, (3, 3), 0)
    out = np.zeros(a.shape, np.uint8)
    out[..., :3] = LINE
    out[..., 3] = np.clip(e.astype(np.float32) * 1.3 + (a[..., 3] > 128) * 30, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


BANDS = [(0.75, 1.0), (0.5, 0.75), (0.0, 0.5)]  # etapas de baixo pra cima (fração da altura)


def wonder(img, cx, cy, width, t, draw0, builds, alpha=1.0):
    """Maravilha: desenho técnico surgindo em draw0 e etapas construídas nos tempos de `builds`."""
    if t < draw0 or alpha <= 0.01:
        return
    real = sized_w("maravilha_babilonia.png", width)
    la = lineart("maravilha_babilonia.png", width)
    w, h = real.size
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    p = seg(t, draw0, draw0 + 1.1)  # o desenho aparece varrendo da esquerda
    if p < 1:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rectangle((0, 0, int(w * p), h), fill=255)
        la2 = la.copy()
        la2.putalpha(Image.fromarray(np.minimum(np.asarray(la.getchannel("A")), np.asarray(m))))
        layer.alpha_composite(la2)
    else:
        layer.alpha_composite(la)
    flashes = []
    for (b0, b1), tb in zip(BANDS, builds):
        if tb is None or t < tb:
            continue
        u = ease(seg(t, tb, tb + 0.45))
        ya, yb = int(h * b0), int(h * b1)
        ytop = int(lerp(yb, ya, u))
        part = real.crop((0, ytop, w, yb))
        layer.alpha_composite(part, (0, ytop))
        flashes.append((tb, ya, yb))
    for tb, ya, yb in flashes:
        f = 1 - seg(t, tb + 0.35, tb + 0.9)
        if 0 < f < 1 or tb + 0.35 > t:
            band = real.crop((0, ya, w, yb))
            wa = np.asarray(band.getchannel("A"), np.float32) * 0.55 * (f if t > tb + 0.35 else seg(t, tb, tb + 0.35))
            white = Image.new("RGBA", band.size, (255, 255, 255, 0))
            white.putalpha(Image.fromarray(wa.astype(np.uint8)))
            layer.alpha_composite(white, (0, ya))
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(layer, (x0, y0), layer)
    for tb, ya, yb in flashes:  # poeira da obra
        dust(img, t, tb + 0.3, cx, y0 + yb - 10, w * 0.5)


def dust(img, t, t0, x, y, spread, n=16):
    u = (t - t0) / 1.1
    if not 0 <= u < 1:
        return
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(int(t0 * 100))
    for k in range(n):
        ang = rng.uniform(math.pi * 1.05, math.pi * 1.95)
        dist = spread * rng.uniform(0.3, 1.0) * ease(min(1, u * 1.4))
        px = x + math.cos(ang) * dist * (1 if k % 2 else -1) * 0.9
        py = y + math.sin(ang) * dist * 0.35 - u * 60
        r = rng.uniform(12, 30) * (0.6 + u)
        a = int(120 * (1 - u))
        d.ellipse((px - r, py - r, px + r, py + r), fill=(232, 228, 216, a))


def arrow(img, p0, p1, u, color=WHITE, width=7, bend=0.25):
    """Seta desenhada a mão, crescendo de p0 até p1 (u de 0 a 1)."""
    if u <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    pts = []
    n = 30
    for k in range(int(n * u) + 1):
        s = k / n
        pts.append(((1 - s) ** 2 * x0 + 2 * (1 - s) * s * mx + s * s * x1,
                    (1 - s) ** 2 * y0 + 2 * (1 - s) * s * my + s * s * y1))
    if len(pts) > 1:
        d.line(pts, fill=color, width=width, joint="curve")
    if u >= 1:
        ax, ay = pts[-1]
        bx, by = pts[-3]
        ang = math.atan2(ay - by, ax - bx)
        for da in (2.6, -2.6):
            d.line((ax, ay, ax + 34 * math.cos(ang + da), ay + 34 * math.sin(ang + da)), fill=color, width=width)


def dashed_rect(img, box, u=1.0, color=LINE, width=4, label=None):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    per = [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]
    total = 2 * (x1 - x0 + y1 - y0)
    left = total * u
    for ax, ay, bx, by in per:
        L = math.hypot(bx - ax, by - ay)
        s = 0
        while s < min(L, left):
            e = min(s + 22, L, left)
            d.line((ax + (bx - ax) * s / L, ay + (by - ay) * s / L, ax + (bx - ax) * e / L, ay + (by - ay) * e / L),
                   fill=color + (220,), width=width)
            s += 36
        left -= L
        if left <= 0:
            break


def fly(t, t0, dur, p0, p1, arc=0.0):
    u = ease(seg(t, t0, t0 + dur))
    x, y = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
    return x, y - math.sin(math.pi * u) * arc, u


def pop(t, t0, d=0.35):
    u = seg(t, t0, t0 + d)
    return max(0.0, out_back(u)) if u < 1 else 1.0


# ---------------------------------------------------------------- linha do tempo (original, antes da narração)
SCENES = [(0.0, 6.0), (6.0, 12.5), (12.5, 20.0), (20.0, 27.0), (27.0, 35.0), (35.0, 43.0),
          (43.0, 51.0), (51.0, 58.5), (58.5, 66.0)]
TR = 0.45  # troca de folha

# (t0, tipo, args, x, y, rot[, t1])
ELS = [
    (0.15, "title", ("CONSTRUIR UMA MARAVILHA DO MUNDO", 64, WHITE, 1000), 540, 320, 0),
    (0.9, "title", ("EM 25 MINUTOS?", 118, GOLD), 540, 500, -2),
    (4.4, "tag", ("2 A 7 JOGADORES", 46), 300, 1500, -3),
    (6.3, "note", ("CADA JOGADOR É O ARQUITETO DE UMA MARAVILHA", 50, 460), 790, 460, -2),
    (6.6, "tag", ("DE ANTOINE BAUZA", 40), 300, 1010, 2),
    (10.6, "stamp", ("+ PONTOS VENCE", 54, GOLD), 790, 800, -6),
    (12.6, "title", ("NA SUA VEZ: PEGUE 1 CARTA", 66, WHITE, 960), 540, 300, 0),
    (13.4, "note", ("ESQUERDA", 44), 200, 1010, 0),
    (13.6, "note", ("MEIO", 44), 540, 1010, 0),
    (13.8, "note", ("DIREITA", 44), 880, 1010, 0),
    (14.6, "note", ("SUA ÁREA", 46), 540, 1555, 0),
    (18.2, "stamp", ("ÀS CEGAS!", 64), 560, 600, -10),
    (20.1, "title", ("CARTAS CINZAS = MATERIAIS", 64, WHITE, 960), 540, 300, 0),
    (24.8, "stamp", ("CORINGA!", 70, GOLD), 770, 1410, -10),
    (25.4, "note", ("O OURO VALE QUALQUER MATERIAL", 40, 420), 770, 1530, 0),
    (27.1, "title", ("JUNTOU? CONSTRÓI!", 84, WHITE), 540, 300, 0),
    (28.3, "note", ("ETAPA 1: 2 IGUAIS", 48, 700, GOLD, True), 540, 1470, 0, 31.0),
    (31.1, "note", ("ETAPA 2: 3 DIFERENTES", 48, 700, GOLD, True), 540, 1470, 0, 33.4),
    (30.1, "laurel", ("+3", 80), 860, 1280, 0),
    (32.7, "tag", ("PODER ESPECIAL!", 44, GOLD, INK), 790, 1050, 4),
    (33.5, "tag", ("CADA ETAPA = PONTOS + PODER", 42), 540, 1500, 0),
    (35.1, "title", ("VERMELHAS = ESCUDOS", 70, WHITE, 960), 540, 300, 0),
    (37.2, "note", ("CORNETA? A FICHA VIRA!", 44, 440), 300, 1110, -2),
    (39.6, "stamp", ("GUERRA!", 120), 560, 1330, -8, 40.9),
    (40.9, "tag", ("VOCÊ: 3 ESCUDOS", 42, GOLD, INK), 300, 1480, -2),
    (41.2, "tag", ("VIZINHO: 1", 42), 790, 1480, 2),
    (41.7, "laurel", ("+3", 80), 760, 1180, 0),
    (43.1, "title", ("VERDES = CIÊNCIA", 76, WHITE, 960), 540, 300, 0, 47.0),
    (45.8, "tag", ("FICHA DE PROGRESSO", 50, GOLD, INK), 540, 1290, 0, 47.0),
    (47.1, "title", ("AZUIS = PONTOS", 80, WHITE, 960), 540, 300, 0),
    (48.3, "laurel", ("+2", 70), 170, 860, 0),
    (48.9, "note", ("O GATO ESPIA O MONTE DO MEIO", 44, 400), 810, 1390, 0),
    (51.1, "title", ("TERMINOU A MARAVILHA?", 72, WHITE, 960), 540, 300, 0, 54.3),
    (52.5, "stamp", ("FIM DE JOGO!", 84), 540, 1320, -6, 54.3),
    (53.2, "tag", ("MAIS PONTOS VENCE", 48, GOLD, INK), 540, 1490, 0, 54.3),
    (54.4, "title", ("QUAL MARAVILHA VOCÊ CONSTRUIRIA?", 70, WHITE, 940), 540, 350, 0),
    (56.6, "stamp", ("COMENTA AQUI!", 76, GOLD), 540, 1440, -4),
    (58.8, "logo", (500,), 540, 420, -2),
    (59.6, "title", ("ALUGUE O", 64, WHITE), 540, 720, 0),
    (59.9, "title", ("7 WONDERS ARQUITETOS", 66, GOLD, 980), 540, 810, 0),
    (60.6, "tag", ("2 A 7 JOGADORES", 42), 770, 1040, 2),
    (61.0, "tag", ("UNS 25 MIN", 42), 770, 1150, -2),
    (61.4, "tag", ("5 DIAS DE JOGO", 42, GOLD, INK), 770, 1260, 2),
    (62.0, "tag", ("RESERVE ONLINE · RETIRE EM MAUÁ E ABC", 36), 540, 1420, 0),
    (62.6, "tag", ("LINK NA BIO · @SUAVEZ_BG", 52, INK, GOLD), 540, 1530, 0),
]


def scene_of(t):
    for i, (a, b) in enumerate(SCENES):
        if a <= t < b:
            return i
    return len(SCENES) - 1


def draw_elements(img, t, scene):
    a, b = SCENES[scene]
    for e in ELS:
        t0, kind, args, x, y, rot = e[:6]
        t1 = e[6] if len(e) > 6 else b
        if not (a <= t0 < b) or t < t0 or t >= t1 + 0.25:
            continue
        im = element_img(kind, args)
        alpha = 1 - seg(t, t1, t1 + 0.25) if t1 < b else 1.0
        if kind == "stamp":  # carimbo bate na folha
            u = seg(t, t0, t0 + 0.22)
            sc = lerp(2.2, 1.0, ease(u)) if u < 1 else 1.0
            al = min(1.0, u * 1.6) * alpha
            paste_c(img, im, x, y, rot, sc, al)
        else:
            paste_c(img, im, x, y, rot, max(0.05, pop(t, t0)), alpha)


# ---------------------------------------------------------------- cenas
def stopwatch(img, t, x, y, r, t0, spin=(3.6, 5.6)):
    s = pop(t, t0)
    if s <= 0.05:
        return
    r = r * s
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((x - r + 8, y - r + 12, x + r + 8, y + r + 12), fill=(0, 0, 0, 90))
    d.rectangle((x - r * 0.18, y - r * 1.28, x + r * 0.18, y - r * 1.02), fill=WHITE, outline=INK, width=4)
    d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE, outline=INK, width=8)
    for k in range(12):
        a = k * math.pi / 6
        d.line((x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78, x + math.cos(a) * r * 0.9,
                y + math.sin(a) * r * 0.9), fill=INK, width=4)
    u = seg(t, *spin)
    ang = -math.pi / 2 + ease(u) * 2 * math.pi * 3
    d.line((x, y, x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72), fill=RED, width=8)
    d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=INK)
    if u >= 1:
        d.text((x, y + r * 0.42), "25'", font=font(CINZEL, int(r * 0.38), "Black"), fill=INK, anchor="mm")


PYR = [((540, 680), (160, 1340)), ((540, 680), (920, 1340)), ((160, 1340), (920, 1340)),
       ((330, 1020), (750, 1020)), ((245, 1180), (835, 1180)), ((420, 860), (660, 860)),
       ((540, 680), (540, 1340))]


def sc0(img, t):
    # pirâmide em desenho técnico que vira a caixa do jogo
    d = ImageDraw.Draw(img, "RGBA")
    fade = 1 - seg(t, 2.9, 3.6)
    if fade > 0:
        for k, (p, q) in enumerate(PYR):
            u = seg(t, 0.3 + k * 0.28, 0.3 + k * 0.28 + 0.5)
            if u > 0:
                d.line((p[0], p[1], lerp(p[0], q[0], u), lerp(p[1], q[1], u)), fill=LINE + (int(240 * fade),),
                       width=6 if k < 3 else 3)
        if t > 1.2:
            f = font(HAND, 34)
            d.text((960, 1010), "146 m", font=f, fill=LINE + (int(220 * fade),), anchor="mm")
            d.line((1000, 680, 1000, 1340), fill=LINE + (int(200 * fade),), width=2)
            d.text((540, 1395), "230 m", font=f, fill=LINE + (int(220 * fade),), anchor="mm")
    if t > 2.7:
        u = ease(seg(t, 2.7, 3.6))
        paste_c(img, shadowed("caixa.png", 860), 540, 1100, -2 * u, lerp(0.85, 1.0, u), u)
    stopwatch(img, t, 860, 1380, 105, 3.4)


BOARDS = ["tab_alexandria.jpg", "tab_halicarnasso.jpg", "tab_olimpia.jpg", "tab_rodes.jpg",
          "tab_efeso.jpg", "tab_babilonia.jpg", "tab_gize.jpg"]
BOARD_XY = [(150, 1180), (400, 1210), (655, 1180), (910, 1210), (280, 1470), (540, 1495), (800, 1470)]
BOARD_ROT = [-6, 4, -3, 6, 5, -4, 3]


def sc1(img, t):
    u = ease(seg(t, 6.0, 6.6))
    paste_c(img, shadowed("caixa.png", 640), lerp(540, 300, u), lerp(1060, 660, u), -4, lerp(1.4, 1.0, u))
    for k, (name, (x, y), r) in enumerate(zip(BOARDS, BOARD_XY, BOARD_ROT)):
        t0 = 7.6 + k * 0.28
        if t < t0:
            continue
        xx, yy, uu = fly(t, t0, 0.4, (x, y - 500), (x, y))
        paste_c(img, photo_pin(name, 270, r * 2), xx, yy, r * (1 - uu) * 3 + r, 1.0, min(1, uu * 3))


DECKS = {"esq": (200, 760), "meio": (540, 760), "dir": (880, 760)}
AREA = (150, 1220, 930, 1520)


def deck_stack(img, name, x, y, h, n=4, rot=0):
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(n, 0, -1):  # bordas das cartas de baixo do monte
        w = h * 540 / 800
        d.rounded_rectangle((x - w / 2 + k * 5, y - h / 2 + k * 7, x + w / 2 + k * 5, y + h / 2 + k * 7), radius=16,
                            fill=(244, 240, 230, 255), outline=(170, 170, 170, 255), width=2)
    paste_c(img, card_img(name, h), x, y, rot)


def sc2(img, t):
    for k, key in enumerate(("esq", "meio", "dir")):
        x, y = DECKS[key]
        dashed_rect(img, (x - 150, y - 200, x + 150, y + 200), seg(t, 12.8 + k * 0.2, 13.6 + k * 0.2))
    dashed_rect(img, AREA, seg(t, 13.8, 14.8), color=GOLD)
    s = pop(t, 14.0)
    if s > 0.05:
        if t < 15.9:
            deck_stack(img, "carta_vermelha.png", 200, 760, 330 * s)
        else:
            deck_stack(img, "carta_vidro.png", 200, 760, 330)  # carta de baixo aparece
    s2 = pop(t, 14.2)
    if s2 > 0.05:
        paste_c(img, shadowed("monte_central.png", 300), 540, 760, 90, s2)
    s3 = pop(t, 14.4)
    if s3 > 0.05:
        deck_stack(img, "carta_azul_gato.png", 880, 760, 330 * s3)
    # pega a carta da esquerda
    arrow(img, (200, 980), (420, 1260), seg(t, 15.3, 15.8), GOLD)
    if t >= 15.9:
        x, y, u = fly(t, 15.9, 0.6, (200, 760), (360, 1370), 120)
        paste_c(img, card_img("carta_vermelha.png", int(lerp(330, 250, u))), x, y, lerp(0, -8, u))
    # mostra a da direita
    if 16.8 <= t < 17.8:
        g = 0.5 + 0.5 * math.sin((t - 16.8) * 12)
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((880 - 140, 760 - 195, 880 + 140, 760 + 195), radius=20, outline=GOLD + (int(255 * g),),
                            width=8)
    # e a do meio, sem ver: vira no caminho
    if t >= 18.8:
        x, y, u = fly(t, 18.8, 0.8, (540, 760), (720, 1370), 140)
        sx = math.cos(math.pi * u)
        if sx > 0:
            paste_c(img, shadowed("monte_central.png", 210), x, y, 90 + 8 * u, 1.0, sx=sx)
        else:
            paste_c(img, card_img("carta_ouro.png", 250), x, y, 8 * u, 1.0, sx=-sx)


MATS = [("ic_pedra.png", "PEDRA"), ("ic_madeira.png", "MADEIRA"), ("ic_tijolo.png", "TIJOLO"),
        ("ic_papiro.png", "PAPIRO"), ("ic_vidro.png", "VIDRO")]
MAT_XY = [(150, 600), (345, 540), (540, 520), (735, 540), (930, 600)]


def sc3(img, t):
    u = ease(seg(t, 20.3, 20.9))
    if u > 0:
        paste_c(img, card_img("carta_vidro.png", 560), lerp(-300, 300, u), 1150, lerp(-20, -5, u))
    for k, ((name, lab), (x, y)) in enumerate(zip(MATS, MAT_XY)):
        t0 = 21.0 + k * 0.55
        s = pop(t, t0)
        if s > 0.05:
            paste_c(img, shadowed(name, 170), x, y, 0, s)
            paste_c(img, note_img(lab, 34), x, y + 120, 0, s)
    u2 = ease(seg(t, 24.2, 24.8))
    if u2 > 0:
        paste_c(img, card_img("carta_ouro.png", 560), lerp(1400, 770, u2), 1150, lerp(25, 6, u2))


B1, B2, B3 = 29.7, 32.3, 52.0  # etapas construídas


def sc4(img, t):
    wonder(img, 540, 900, 940, t, 27.3, (B1, B2, None))
    # 2 vidros iguais → etapa 1
    for k, x0 in enumerate((180, 900)):
        if 28.5 <= t < B1:
            x, y, u = fly(t, 29.0, 0.7, (x0, 1300), (540 + (k - 0.5) * 120, 1270), 80)
            paste_c(img, shadowed("ic_vidro.png", 150), x, y, 0, pop(t, 28.5) * (1 - 0.5 * u))
    # pedra, madeira e tijolo (diferentes) → etapa 2
    for k, (name, x0) in enumerate((("ic_pedra.png", 160), ("ic_madeira.png", 540), ("ic_tijolo.png", 920))):
        if 31.2 + k * 0.15 <= t < B2:
            x, y, u = fly(t, 31.7, 0.6, (x0, 1300), (440 + k * 100, 1030), 80)
            paste_c(img, shadowed(name, 140), x, y, 0, pop(t, 31.2 + k * 0.15) * (1 - 0.5 * u))


def sc5(img, t):
    u = ease(seg(t, 35.3, 35.9))
    if u > 0:
        paste_c(img, card_img("carta_vermelha.png", 560), lerp(-300, 300, u), 760, lerp(-18, -6, u))
    flips = (37.6, 38.3, 39.0)
    for k, tf in enumerate(flips):
        y = 600 + k * 230
        s = pop(t, 35.8 + k * 0.15)
        if s <= 0.05:
            continue
        if t < tf:
            paste_c(img, shadowed("conflito_paz.png", 190), 820, y, 0, s)
        else:
            v = seg(t, tf, tf + 0.3)
            sx = math.cos(math.pi * v)
            name = "conflito_paz.png" if sx > 0 else "conflito_guerra.png"
            paste_c(img, shadowed(name, 190), 820, y, 0, 1.0, sx=abs(sx))
    if 39.6 <= t < 41.0:  # tremidinha da guerra
        pass
    if t >= 41.4:  # fichas de vitória militar
        x, y, u = fly(t, 41.4, 0.5, (820, 600), (330, 1240), 150)
        paste_c(img, shadowed("fichas_vitoria.png", 220), x, y, 0, lerp(0.6, 1.0, u))


SCI = [("ic_sci_tabua.png", (210, 640)), ("ic_sci_roda.png", (540, 560)), ("ic_sci_compasso.png", (870, 640))]


def sc6(img, t):
    fade = 1 - seg(t, 46.8, 47.1)
    if fade > 0:
        for k, (name, (x, y)) in enumerate(SCI):
            s = pop(t, 43.5 + k * 0.3)
            if s <= 0.05:
                continue
            if t < 45.0:
                paste_c(img, shadowed(name, 250), x, y, 0, s, fade)
            elif t < 45.6:
                xx, yy, u = fly(t, 45.0, 0.6, (x, y), (540, 900))
                paste_c(img, shadowed(name, 250), xx, yy, 0, 1 - 0.6 * u, fade)
        if t >= 45.6:
            s = pop(t, 45.6, 0.4)
            d = ImageDraw.Draw(img, "RGBA")
            for k in range(14):  # brilho
                a = k * math.pi / 7 + t
                r0, r1 = 200 * s, 330 * s
                d.line((540 + math.cos(a) * r0, 900 + math.sin(a) * r0, 540 + math.cos(a) * r1,
                        900 + math.sin(a) * r1), fill=GOLD + (int(200 * fade),), width=9)
            paste_c(img, shadowed("progresso_a.png", 360), 540, 900, 0, s, fade)
    u = ease(seg(t, 47.3, 47.9))
    if u > 0:
        paste_c(img, card_img("carta_azul_gato.png", 600), lerp(-300, 330, u), 1060, lerp(-20, -4, u))
        if t >= 48.6:  # circula o gatinho na carta
            v = seg(t, 48.6, 49.1)
            d = ImageDraw.Draw(img, "RGBA")
            cx, cy = 425, 872  # ícone do gato na carta
            d.arc((cx - 58, cy - 58, cx + 58, cy + 58), -90, -90 + 360 * v, fill=GOLD, width=8)
    s = pop(t, 48.0)
    if s > 0.05:
        paste_c(img, shadowed("monte_central.png", 300), 820, 1000, 90, s)
        if t >= 49.6:  # espiada: a carta de cima levanta e mostra a frente
            v = seg(t, 49.6, 50.0) * (1 - seg(t, 50.8, 51.0))
            paste_c(img, card_img("carta_ouro.png", 300), 820 + 30 * v, 1000 - 120 * v, 10 * v, 1.0, v)


def sc7(img, t):
    fade = 1 - seg(t, 54.2, 54.5)
    if fade > 0:
        wonder(img, 540, 800, 880, t, 27.3, (B1, B2, B3), fade)
    for k, (name, r) in enumerate(zip(BOARDS, BOARD_ROT)):
        t0 = 54.7 + k * 0.14
        if t < t0:
            continue
        x = [180, 420, 660, 900, 300, 540, 780][k]
        y = [720, 750, 720, 750, 1080, 1110, 1080][k]
        paste_c(img, photo_pin(name, 300, r * 2), x, y, r, pop(t, t0))


def sc8(img, t):
    u = ease(seg(t, 59.2, 59.8))
    if u > 0:
        paste_c(img, shadowed("caixa.png", 560), lerp(-300, 300, u), 1150, -4)


SCENE_FN = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8]


def scene_frame(i, t):
    img = background().copy().convert("RGBA")
    SCENE_FN[i](img, t)
    draw_elements(img, t, i)
    a, b = SCENES[i]
    z = 1 + 0.035 * seg(t, a, b)  # leve zoom ao longo da cena
    if i == 5 and 39.6 <= t < 40.4:  # tremor da guerra
        k = 1 - seg(t, 39.6, 40.4)
        dx, dy = 14 * k * math.sin(t * 90), 10 * k * math.cos(t * 77)
    else:
        dx = dy = 0
    img = img.convert("RGB")
    if z > 1.001 or dx or dy:
        cw, ch = W / z, H / z
        box = (W / 2 - cw / 2 + dx, H / 2 - ch / 2 + dy, W / 2 + cw / 2 + dx, H / 2 + ch / 2 + dy)
        img = img.resize((W, H), Image.BICUBIC, box=box)
    return img


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
    c = []
    for e in ELS:
        c.append((e[0], "stamp" if e[1] == "stamp" else "pop", 0.55 if e[1] == "stamp" else 0.32))
    for a, _ in SCENES[1:]:
        c.append((a, "paper", 0.6))
    c += [(0.3, "draw", 0.4), (1.2, "draw", 0.35), (2.7, "whoosh", 0.5), (3.4, "pop", 0.4), (3.6, "tick", 0.5),
          (5.6, "ding", 0.4)]
    c += [(7.6 + k * 0.28, "card", 0.45) for k in range(7)]
    c += [(14.0, "card", 0.5), (14.2, "card", 0.5), (14.4, "card", 0.5), (15.9, "whoosh", 0.4), (16.5, "card", 0.5),
          (18.8, "whoosh", 0.4), (19.2, "card", 0.4), (19.6, "card", 0.5)]
    c += [(20.3, "whoosh", 0.4)] + [(21.0 + k * 0.55, "pop", 0.4) for k in range(5)] + [(24.2, "whoosh", 0.45),
                                                                                         (24.9, "coin", 0.6)]
    c += [(27.3, "draw", 0.5), (29.0, "whoosh", 0.35), (B1, "build", 0.9), (30.1, "ding", 0.4),
          (31.7, "whoosh", 0.35), (B2, "build", 0.9), (32.7, "chime", 0.4)]
    c += [(35.3, "whoosh", 0.4), (37.6, "horn", 0.55), (38.3, "horn", 0.6), (39.0, "horn", 0.7),
          (39.6, "clash", 0.9), (41.4, "whoosh", 0.4), (41.8, "coin", 0.6)]
    c += [(45.0, "whoosh", 0.4), (45.6, "chime", 0.6), (47.3, "whoosh", 0.4), (48.6, "meow", 0.5),
          (49.6, "card", 0.5)]
    c += [(B3, "build", 1.0), (52.5, "fanfare", 0.7)] + [(54.7 + k * 0.14, "card", 0.35) for k in range(7)]
    c += [(59.2, "whoosh", 0.4), (65.0, "chime", 0.5)]
    return c


CUES = _cues()


@lru_cache(None)
def sub_img(text):
    f = font(POP, 50)
    lines = wrap(text, f, 900)
    lh = 62
    w = int(max(f.getlength(l) for l in lines)) + 50
    h = lh * len(lines) + 26
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=22, fill=(8, 20, 44, 225))
    for i, l in enumerate(lines):
        d.text((w / 2, 13 + lh * i + lh / 2), l, font=f, fill=WHITE, anchor="mm")
    return im


@lru_cache(None)
def watermark():
    lg = logo_card(190).copy()
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.92)))
    return lg


def frame_at(to):
    i = scene_of(to)
    a, _ = SCENES[i]
    if i > 0 and to < a + TR:  # folha nova entra pela direita por cima da antiga
        u = ease(seg(to, a, a + TR))
        old = scene_frame(i - 1, a - 0.001)
        new = scene_frame(i, to)
        img = Image.new("RGB", (W, H), BP_DARK)
        img.paste(old, (int(-W * 0.3 * u), 0))
        sh = Image.new("RGBA", (60, H), (0, 0, 0, 0))
        sh.putalpha(Image.linear_gradient("L").rotate(90).resize((60, H)).point(lambda v: int(v * 0.5)))
        x = int(W * (1 - u))
        img.paste(sh.convert("RGB"), (x - 60, 0), sh)
        img.paste(new, (x, 0))
        return img
    return scene_frame(i, to)


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    to = to_orig(t)
    img = frame_at(to)
    if to < SCENES[-1][0]:
        wm = watermark()
        img.paste(wm, (W - wm.width - 40, 60), wm)
    if subs:
        for a_, b_, s in SUBS:
            if a_ <= t < b_:
                si = sub_img(s)
                img.paste(si, ((W - si.width) // 2, 1700 - si.height // 2), si)
    return img.tobytes()


def render(out_path, wav, subs, workers=4):
    n = int(DUR * FPS)
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers) as pool:
        for i, fr in enumerate(pool.imap(render_frame, [(k, subs) for k in range(n)], chunksize=6)):
            p.stdin.write(fr)
            if i % 300 == 0:
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
        else:
            sheet = Image.new("RGB", (360 * len(ims), 640))
            for k, im in enumerate(ims):
                sheet.paste(im.resize((360, 640), Image.LANCZOS), (360 * k, 0))
            sheet.save(os.path.join(OUT, "frames.jpg"), quality=90)
        return
    wav = os.path.join(OUT, "trilha.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz, cues=CUES)
    with open(os.path.join(ROOT, "legendas.srt"), "w", encoding="utf-8") as f:
        for i, (a_, b_, s) in enumerate(SUBS, 1):
            ts = lambda x: f"{int(x // 3600):02}:{int(x // 60 % 60):02}:{int(x % 60):02},{int(round(x * 1000)) % 1000:03}"
            f.write(f"{i}\n{ts(a_)} --> {ts(b_)}\n{s}\n\n")
    if a.only != "limpo":
        render(os.path.join(OUT, "arq_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "arq_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
