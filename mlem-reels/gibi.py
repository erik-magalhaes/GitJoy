#!/usr/bin/env python3
"""Reels do MLEM: Space Agency em formato de GIBI — Sua Vez Locação de Jogos.

Duas páginas de história em quadrinhos montadas com as fotos oficiais do jogo.
A "câmera" passeia pela página: mostra o gibi inteiro, dá zoom em cada quadro
enquanto a narração explica e, de vez em quando, afasta para mostrar a página.
Movimento suave a 30 quadros/s (sem tremedeira).

Uso:
  python3 gibi.py               # out/gibi_preview.mp4 (legendas) e out/gibi_limpo.mp4
  python3 gibi.py --frame 20    # quadro de teste em out/frame.png
  python3 gibi.py --page 1      # página inteira em out/pagina1.png
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

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import som  # noqa: E402

FOTOS = os.path.join(ROOT, "assets", "fotos")
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
PW, PH = 2160, 3840          # página em resolução dobrada (zoom sem perder nitidez)
DUR = 66.0

INK = (18, 16, 24)
PAPER = (255, 249, 228)
YELLOW = (255, 214, 64)
DOT = (240, 186, 30)
RED = (232, 48, 56)
ORANGE = (255, 120, 40)
BLUE = (60, 120, 230)
CYAN = (90, 210, 240)
PINK = (245, 110, 180)
WHITE = (255, 255, 255)


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


BANG = "Bangers-Regular.ttf"
LUCKY = "LuckiestGuy-Regular.ttf"
POP = "Poppins-ExtraBold.ttf"


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def ease(u):
    return u * u * (3 - 2 * u)


def out_back(u, s=1.6):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def lerp(a, b, u):
    return a + (b - a) * u


# ---------------------------------------------------------------- página
def cover(im, w, h, cx=0.5, cy=0.5, zoom=1.0):
    s = max(w / im.width, h / im.height) * zoom
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x0 = int((im.width - w) * cx)
    y0 = int((im.height - h) * cy)
    return im.crop((x0, y0, x0 + w, y0 + h))


@lru_cache(None)
def halftone(w, h, step=14):
    """Retícula de pontinhos de gibi (máscara 0..1)."""
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for y in range(0, h, step):
        off = step // 2 if (y // step) % 2 else 0
        for x in range(-step, w + step, step):
            d.ellipse((x + off - 3, y - 3, x + off + 3, y + 3), fill=255)
    return np.asarray(m, np.float32) / 255


def comic_photo(name, w, h, focus=(0.5, 0.5), zoom=1.0, tint=None):
    im = Image.open(os.path.join(FOTOS, name)).convert("RGB")
    im = cover(im, w, h, *focus, zoom=zoom)
    a = np.asarray(im, np.float32)
    # cores mais "de gibi": saturação e contraste levemente maiores + retícula
    g = a.mean(2, keepdims=True)
    a = np.clip((a - g) * 1.25 + g, 0, 255)
    a = np.clip((a - 128) * 1.08 + 128, 0, 255)
    if tint is not None:
        a = a * 0.55 + np.array(tint, np.float32) * 0.45
    a = a * (1 - 0.10 * halftone(w, h)[..., None])
    return Image.fromarray(a.astype(np.uint8))


def page_background(d, title):
    d.rectangle((0, 0, PW, PH), fill=YELLOW)
    step = 46
    for y in range(0, PH, step):
        for x in range(0, PW, step):
            r = 7 + 5 * math.sin((x + y) / 260)
            d.ellipse((x - r, y - r, x + r, y + r), fill=DOT)
    # faixa de título do gibi
    d.rectangle((60, 60, PW - 60, 270), fill=INK)
    d.text((PW / 2, 158), title, font=font(BANG, 150), fill=YELLOW, anchor="mm")


# quadros: (x0, y0, x1, y1), foto, foco, zoom, tinta
PAGE1 = [
    ((60, 320, 1060, 1580), "i8.jpg", (0.02, 0.95), 2.4, None),          # 1 nuvens e fogo da decolagem (o foguete é animado)
    ((1100, 320, 2100, 1150), "i1.jpg", (0.5, 0.40), 1.0, None),       # 2 caixa e gatos
    ((1100, 1190, 2100, 2600), "i12.jpg", (0.5, 0.5), 1.3, (20, 24, 60)),  # 3 fundo para o embarque
    ((60, 1620, 1060, 2600), "i11.jpg", (0.45, 0.6), 1.2, None),       # 4 tabuleiro (dados animados por cima)
    ((60, 2640, 2100, 3780), "i10.jpg", (0.38, 0.55), 1.0, None),      # 5 luas e planetas
]
PAGE2 = [
    ((60, 320, 2100, 1500), "i10.jpg", (0.7, 0.3), 1.3, (255, 90, 30)),   # 6 falha cósmica (foguete animado)
    ((60, 1540, 1360, 2600), "i29.jpg", (0.5, 0.35), 1.0, None),          # 7 tabuleiros dos jogadores
    ((1400, 1540, 2100, 2600), "i14.png", (0.5, 0.5), 1.0, None),         # 8 e você? (fichas de gato)
    ((60, 2640, 2100, 3780), "i5.jpg", (0.5, 0.55), 1.0, None),           # 9 sua vez
]


@lru_cache(None)
def page_base(n):
    panels = PAGE1 if n == 1 else PAGE2
    im = Image.new("RGB", (PW, PH), YELLOW)
    d = ImageDraw.Draw(im)
    page_background(d, "AS AVENTURAS DA AGÊNCIA MLEM" if n == 1 else "MLEM  ·  CAPÍTULO 2: O RISCO")
    for (x0, y0, x1, y1), name, focus, zoom, tint in panels:
        ph = comic_photo(name, x1 - x0, y1 - y0, focus, zoom, tint)
        d.rectangle((x0 - 14 + 12, y0 - 14 + 14, x1 + 14 + 12, y1 + 14 + 14), fill=(0, 0, 0))  # sombra
        d.rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), fill=INK)
        im.paste(ph, (x0, y0))
    return im


def panels_of(n):
    return [p[0] for p in (PAGE1 if n == 1 else PAGE2)]


# ---------------------------------------------------------------- balões, legendas, onomatopeias
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


@lru_cache(None)
def caption(text, maxw=820, size=64):
    """Quadro de narração (retângulo creme com borda)."""
    f = font(LUCKY, size)
    lines = wrap(text, f, maxw)
    lh = int(size * 1.15)
    w = int(max(f.getlength(l) for l in lines)) + 70
    h = lh * len(lines) + 50
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((14, 14, w + 14, h + 14), fill=(0, 0, 0, 160))
    d.rectangle((0, 0, w, h), fill=PAPER, outline=INK, width=9)
    for i, l in enumerate(lines):
        d.text((w / 2, 25 + lh * i + lh / 2), l, font=f, fill=INK, anchor="mm")
    return im


@lru_cache(None)
def balloon(text, maxw=700, size=74, tail=(-0.25, 1.0), color=RED, fill=WHITE):
    """Balão de fala com rabinho. tail = direção do rabinho (x relativo, y relativo)."""
    f = font(LUCKY, size)
    lines = wrap(text, f, maxw)
    lh = int(size * 1.12)
    tw = max(f.getlength(l) for l in lines)
    bw, bh = int(tw * 1.32 + 90), int(lh * len(lines) * 1.45 + 70)
    pad = 160
    im = Image.new("RGBA", (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = pad + bw / 2, pad + bh / 2
    tx, ty = cx + tail[0] * bw * 0.9, cy + tail[1] * bh * 0.95
    b1 = (cx + tail[0] * bw * 0.2 - 40, cy + bh * 0.25)
    b2 = (cx + tail[0] * bw * 0.2 + 40, cy + bh * 0.25)
    d.polygon([b1, (tx, ty), b2], fill=INK)
    d.ellipse((pad - 9, pad - 9, pad + bw + 9, pad + bh + 9), fill=INK)
    d.polygon([(b1[0] + 10, b1[1]), (tx + (6 if tail[0] < 0 else -6), ty - 18), (b2[0] - 10, b2[1])], fill=fill)
    d.ellipse((pad, pad, pad + bw, pad + bh), fill=fill)
    y0 = cy - lh * len(lines) / 2
    for i, l in enumerate(lines):
        d.text((cx, y0 + lh * i + lh / 2), l, font=f, fill=color, anchor="mm")
    return im


@lru_cache(None)
def burst(text, size=200, fill=ORANGE, ink=YELLOW, spikes=22, r=1.0):
    """Explosão de onomatopeia (BOOM!, TEC TEC!)."""
    f = font(BANG, size)
    tw = f.getlength(text)
    R = max(tw * 0.62, size * 1.0) * r
    S = int(R * 2.4)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    rng = np.random.default_rng(len(text) * 7 + size)
    pts = []
    for i in range(spikes * 2):
        rr = R * (1.0 if i % 2 == 0 else 0.68) * rng.uniform(0.92, 1.08)
        a = i * math.pi / spikes
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a) * 0.82))
    d.polygon([(x + 14, y + 16) for x, y in pts], fill=(0, 0, 0, 150))
    d.polygon(pts, fill=fill, outline=INK, width=10)
    d.text((c, c), text, font=f, fill=ink, anchor="mm", stroke_width=10, stroke_fill=INK)
    return im


@lru_cache(None)
def chip(text, size=60, bg=INK, ink=YELLOW):
    f = font(LUCKY, size)
    w, h = int(f.getlength(text)) + 80, int(size * 1.6)
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, w + 12, h + 12), radius=h // 2, fill=(0, 0, 0, 150))
    d.rounded_rectangle((0, 0, w, h), radius=h // 2, fill=bg, outline=INK, width=6)
    d.text((w / 2, h / 2 + 4), text, font=f, fill=ink, anchor="mm")
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


# elementos de cada página: (t0 na linha do tempo original, tipo, args, x, y, rot)
EL1 = [
    (0.9, "caption", ("ENQUANTO ISSO, NO ESPAÇO...", 620, 60), 440, 450, -1),
    (2.1, "burst", ("VRUUUM!", 120, YELLOW, RED, 20, 1.0), 330, 1020, -8, 3.3),
    (3.4, "burst", ("GATOS NO ESPAÇO?!", 88, (255, 255, 255), RED, 24, 1.0), 600, 860, 4),
    (4.2, "balloon", ("O QUE PODERIA DAR ERRADO?", 560, 58, (-0.3, 1.0)), 560, 1300, 0),
    (6.0, "caption", ("CADA JOGADOR COMANDA UMA EQUIPE DE GATOS ASTRONAUTAS", 800, 50), 1600, 450, -1),
    (7.6, "balloon", ("MIAU!", 360, 84, (-0.25, 1.0), RED), 1860, 720, 3),
    (9.0, "chip", ("DE REINER KNIZIA", 52), 1600, 1080, -2),
    (12.4, "caption", ("TODA RODADA, CADA UM EMBARCA UM GATO", 800, 56), 1600, 1300, 1),
    (16.0, "balloon", ("EU VOU!", 330, 66, (0.3, 1.0), BLUE), 1300, 1560, -3),
    (16.8, "balloon", ("EU TAMBÉM!", 380, 58, (-0.3, 1.0), PINK), 1900, 1640, 2),
    (19.4, "caption", ("O CAPITÃO ROLA OS DADOS...", 780, 58), 520, 1730, -1),
    (20.0, "burst", ("TEC TEC TEC!", 84, (255, 255, 255), RED, 18, 1.0), 330, 1960, -6),
    (22.8, "balloon", ("ESCOLHO OS 2!", 380, 56, (0.2, 1.0), BLUE), 330, 2000, 2),
    (24.6, "burst", ("+4!", 130, YELLOW, RED, 16, 1.2), 640, 1880, 8),
    (25.2, "chip", ("DADO USADO FICA DE FORA", 46, RED, WHITE), 560, 2530, 1),
    (28.6, "caption", ("DESCE AGORA... OU CONTINUA?", 860, 62), 1400, 2700, 1),
    (31.0, "balloon", ("DESÇO! PONTOS GARANTIDOS!", 420, 56, (0.35, -1.0), BLUE), 920, 3080, -2),
    (33.4, "balloon", ("EU CONTINUO! LONGE VALE MAIS!", 470, 54, (0.3, -1.0), RED), 1460, 3380, 2),
]
EL2 = [
    (38.9, "caption", ("A CADA ROLAGEM, MENOS DADOS...", 900, 60), 640, 430, -1),
    (39.9, "caption", ("NENHUM SERVIU!", 600, 60), 560, 1380, 2),
    (40.4, "burst", ("BOOM!", 300, ORANGE, YELLOW, 24, 1.0), 1250, 880, -5),
    (41.6, "caption", ("QUEM FICOU NO FOGUETE SAI SEM NADA", 860, 54), 1500, 1380, 1),
    (42.4, "balloon", ("MIAAAU!", 420, 84, (0.3, 1.0), RED), 420, 1060, -4),
    (45.6, "caption", ("GANHA QUEM SOUBER A HORA CERTA DE PULAR", 1000, 56), 710, 1660, -1),
    (48.0, "chip", ("CADA GATO TEM UM PODER ESPECIAL", 46), 710, 2350, 1),
    (49.6, "chip", ("2 A 5 JOGADORES  ·  UNS 40 MIN", 50, YELLOW, INK), 710, 2490, -1),
    (53.4, "burst", ("E VOCÊ?", 130, (255, 255, 255), RED, 20, 1.05), 1750, 1700, 4),
    (54.6, "balloon", ("PULA NA 1ª LUA?", 420, 52, (0.2, 1.0), BLUE), 1750, 2070, -2),
    (55.6, "balloon", ("ARRISCA ATÉ O INFINITO?", 440, 50, (-0.2, 1.0), RED), 1750, 2380, 2),
    (56.8, "chip", ("COMENTA AÍ!", 56, RED, WHITE), 1750, 2540, 0),
    (58.9, "logo", (680,), 500, 2950, -3),
    (59.8, "burst", ("ALUGUE O MLEM!", 104, (255, 255, 255), RED, 22, 1.0), 1520, 2900, 3),
    (60.8, "chip", ("5 DIAS DE JOGO COM A SUA GALERA", 52, YELLOW, INK), 1080, 3330, -1),
    (61.8, "chip", ("RESERVE ONLINE  ·  RETIRE EM MAUÁ E ABC", 48, PAPER, INK), 1080, 3480, 1),
    (62.6, "chip", ("LINK NA BIO  ·  @SUAVEZ_BG", 64, INK, YELLOW), 1080, 3650, -1),
]


# ---------------------------------------------------------------- animações desenhadas por cima dos quadros
PIECES = os.path.join(ROOT, "assets", "pieces")


@lru_cache(None)
def piece(name):
    return Image.open(os.path.join(PIECES, name)).convert("RGBA")


@lru_cache(None)
def sized(name_or_key, height):
    im = rocket_partial(name_or_key) if isinstance(name_or_key, int) else piece(name_or_key)
    return im.resize((max(2, int(im.width * height / im.height)), int(height)), Image.LANCZOS)


SLOT_XY = [(291, 224), (273, 324), (251, 402), (233, 486)]  # janelas no rocket_full.png


@lru_cache(None)
def slot_patch(i):
    """Ficha de miaustronauta tirada da foto do foguete cheio (encaixa perfeito no foguete vazio)."""
    x, y = SLOT_XY[i]
    box = (x - 66, y - 64, x + 66, y + 60)
    p = piece("rocket_full.png").crop(box)
    m = Image.new("L", p.size, 0)
    ImageDraw.Draw(m).ellipse((4, 4, p.width - 4, p.height - 4), fill=255)
    p.putalpha(m.filter(ImageFilter.GaussianBlur(5)))
    return p, box


@lru_cache(None)
def rocket_partial(n):
    im = piece("rocket_empty.png").copy()
    for i in range(n):
        p, box = slot_patch(i)
        im.alpha_composite(p, (box[0], box[1]))
    return im


def paste_c(page, im, x, y, rot=0.0, scale=1.0, alpha=1.0):
    if scale <= 0.02 or alpha <= 0.01:
        return
    if abs(scale - 1) > 0.002:
        im = im.resize((max(2, int(im.width * scale)), max(2, int(im.height * scale))), Image.BICUBIC)
    if abs(rot) > 0.1:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    page.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)


@lru_cache(None)
def puff(size, shade=245):
    """Nuvenzinha de fumaça de gibi (bolinhas com contorno)."""
    S = int(size * 1.6)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    blobs = [(0, 0, 0.42), (-0.28, 0.08, 0.30), (0.28, 0.06, 0.32), (-0.1, -0.22, 0.30), (0.16, -0.2, 0.26)]
    for dx, dy, r in blobs:
        R = r * size
        d.ellipse((c + dx * size - R - 7, c + dy * size - R - 7, c + dx * size + R + 7, c + dy * size + R + 7), fill=INK)
    for dx, dy, r in blobs:
        R = r * size
        d.ellipse((c + dx * size - R, c + dy * size - R, c + dx * size + R, c + dy * size + R), fill=(shade, shade, shade + 5))
    return im


def smoke_trail(page, t, t0, t1, path, every=0.07, size=150, life=1.5, shade=245):
    """Puffs deixados ao longo do caminho: crescem e somem."""
    k = 0
    while True:
        ts = t0 + k * every
        if ts > min(t, t1):
            break
        age = t - ts
        if age < life:
            x, y = path(ts)
            g = (k * 37 % 11) / 11 - 0.5
            sc = 0.45 + 0.9 * min(1, age / 0.9)
            paste_c(page, puff(size, shade), x + g * 60, y + abs(g) * 40, rot=k * 23, scale=sc,
                    alpha=max(0, 1 - age / life))
        k += 1


PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)]}


@lru_cache(None)
def die_sprite(face, s=150, dim=False):
    """Dado desenhado no estilo do gibi (faces do MLEM: 1, 2, 2, 3, 4 e a pata/propulsor)."""
    S = s + 40
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = 14
    d.rounded_rectangle((o + 10, o + 12, o + s + 10, o + s + 12), radius=30, fill=(0, 0, 0, 150))
    d.rounded_rectangle((o, o, o + s, o + s), radius=30, fill=(150, 150, 160) if dim else WHITE, outline=INK, width=9)
    c = o + s / 2
    if face == "paw":
        r = s * 0.13
        d.ellipse((c - s * 0.2, c - s * 0.02, c + s * 0.2, c + s * 0.3), fill=INK)
        for ang, dd in ((-60, 0.27), (-22, 0.32), (22, 0.32), (60, 0.27)):
            a = math.radians(ang - 90)
            x, y = c + dd * s * math.cos(a), c + 0.06 * s + dd * s * math.sin(a)
            d.ellipse((x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8), fill=INK)
    else:
        for px, py in PIPS[face]:
            x, y = c + px * s * 0.25, c + py * s * 0.25
            d.ellipse((x - s * 0.085, y - s * 0.085, x + s * 0.085, y + s * 0.085), fill=INK)
    return im


FACES = [1, 2, 2, 3, 4, "paw"]


def motion_lines(page, x, y, vx, vy, n=3, length=90):
    d = ImageDraw.Draw(page)
    ln = math.hypot(vx, vy) or 1
    ux, uy = -vx / ln, -vy / ln
    px, py = -uy, ux
    for i in range(n):
        o = (i - (n - 1) / 2) * 34
        sx, sy = x + ux * 90 + px * o, y + uy * 90 + py * o
        d.line((sx, sy, sx + ux * length, sy + uy * length), fill=INK, width=8)


def roll(page, t, t0, dur, start, slots, faces, rots, dim=(), gone=None, s=150):
    """Dados rolando: saem de 'start', quicam e param nas faces dadas."""
    for k, ((x, y), face, r) in enumerate(zip(slots, faces, rots)):
        if gone and k in gone and t >= gone[k]:
            continue
        a = t0 + k * 0.06
        if t < a:
            continue
        u = seg(t, a, a + dur)
        e = 1 - (1 - u) ** 2
        px = lerp(start[0], x, e)
        py = lerp(start[1], y, e) - abs(math.sin(e * math.pi * 2.5)) * 160 * (1 - e)
        if u < 1:
            f = FACES[(int(t * FPS / 3) + k * 2) % 6]
            rot = r + (1 - e) * 720
            motion_lines(page, px, py, x - start[0], y - start[1])
            paste_c(page, die_sprite(f, s), px, py, rot=rot)
        else:
            paste_c(page, die_sprite(face, s, k in dim), x, y, rot=r)


def bezier(p0, p1, p2, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
            (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1])


# --- quadro 1: decolagem que rompe a borda do quadro
R1 = (560, 1240)


def r1_path(t):
    u = seg(t, 1.8, 3.6) ** 2
    return lerp(R1[0], 640, u), lerp(R1[1], -800, u)


# --- quadro 4 → 5: o foguete atravessa a página
R4, R5 = (860, 1880), (1560, 2940)  # pousa no começo da trilha
FLY = (26.6, 27.9)


def fly_path(t):
    u = ease(seg(t, *FLY))
    return bezier(R4, (1900, 2250), R5, u)


DICE_SLOTS = [(200, 2160), (380, 2250), (560, 2150), (740, 2260), (290, 2400), (620, 2410)]
DICE_FACES = [2, 4, 2, 1, "paw", 3]
DICE_ROTS = [-8, 12, 18, -14, 6, -20]
PICKED = (0, 2)


def anim_page1(page, t):
    # 1. foguete em cima das nuvens: treme, decola e sai do quadro
    if t < 4.0:
        smoke_trail(page, t, 1.75, 3.6, r1_path, every=0.06, size=170, life=1.6)
        x, y = r1_path(t)
        if t < 1.8:
            x += 4 * math.sin(t * 60) * seg(t, 1.0, 1.8)
        paste_c(page, sized("rocket_full.png", 700), x, y)
    # 3. embarque: fichas caem uma a uma no foguete
    n = sum(1 for k in range(4) if t >= 13.2 + k * 0.7 + 0.35)
    rk_h, rk_x, rk_y = 1180, 1600, 1930
    paste_c(page, sized(n, rk_h), rk_x, rk_y)
    full = piece("rocket_full.png")
    sc = rk_h / full.height
    for k in range(4):
        a = 13.2 + k * 0.7
        tx = rk_x + (SLOT_XY[k][0] - full.width / 2) * sc
        ty = rk_y + (SLOT_XY[k][1] - full.height / 2) * sc
        u = seg(t, a, a + 0.35)
        if 0 < u < 1:
            p, _ = slot_patch(k)
            paste_c(page, p, tx, lerp(ty - 500, ty, u * u), rot=(1 - u) * 30, scale=sc * lerp(1.7, 1.0, u))
        if a + 0.35 <= t < a + 0.8:
            paste_c(page, burst("PLIM!", 70, YELLOW, RED, 14, 1.0), tx + 190, ty - 60,
                    scale=out_back(seg(t, a + 0.35, a + 0.55)))
    # 4. dados rolando e o foguete pequeno que recebe os dados escolhidos
    if 19.0 <= t < FLY[1]:
        gone = {k: 24.0 for k in PICKED}
        dim = tuple(k for k in range(6) if k not in PICKED) if t >= 24.0 else ()
        roll(page, t, 19.8, 1.1, (120, 2650), DICE_SLOTS, DICE_FACES, DICE_ROTS, dim=dim, gone=gone)
        if 22.6 <= t < 24.0:
            d = ImageDraw.Draw(page)
            pul = 1 + 0.06 * math.sin(t * 10)
            for k in PICKED:
                x, y = DICE_SLOTS[k]
                r = 115 * pul
                d.ellipse((x - r, y - r, x + r, y + r), outline=YELLOW, width=16)
                d.ellipse((x - r - 8, y - r - 8, x + r + 8, y + r + 8), outline=INK, width=6)
        for k in PICKED:
            u = seg(t, 24.0, 24.6)
            if 0 < u < 1:
                x0, y0 = DICE_SLOTS[k]
                paste_c(page, die_sprite(2, 150), lerp(x0, R4[0], ease(u)), lerp(y0, R4[1], ease(u)) - math.sin(u * math.pi) * 180,
                        rot=u * 360, scale=lerp(1, 0.3, u))
    if 19.0 <= t < 37.6:
        if t < FLY[0]:
            paste_c(page, sized("rocket_full.png", 330), *R4)
        elif t < FLY[1]:  # atravessa a página deixando rastro de fumaça
            smoke_trail(page, t, FLY[0], FLY[1], fly_path, every=0.05, size=110, life=1.3)
            x, y = fly_path(t)
            x2, y2 = fly_path(min(FLY[1], t + 0.05))
            ang = -math.degrees(math.atan2(x2 - x, -(y2 - y))) if (x2, y2) != (x, y) else 0
            paste_c(page, sized("rocket_full.png", 360), x, y, rot=ang)
        else:  # pousa no quadro 5
            smoke_trail(page, t, FLY[0], FLY[1], fly_path, every=0.05, size=110, life=1.3)
            bob = 6 * math.sin(t * 2)
            paste_c(page, sized("rocket_full.png", 380), R5[0], R5[1] + bob)
            # uma ficha pula do foguete para a lua
            u = seg(t, 30.4, 31.0)
            if u > 0:
                p, _ = slot_patch(3)
                x = lerp(R5[0], HOP[0], ease(u))
                y = lerp(R5[1], HOP[1], ease(u)) - math.sin(u * math.pi) * 260
                paste_c(page, p, x, y, rot=(1 - u) * 60, scale=0.9)


HOP = (1110, 2810)  # 1ª lua da trilha (planeta da patinha)
R6 = (1450, 900)


def anim_page2(page, t):
    if t < 38.6:
        return
    boom = 40.4
    if t < boom:  # o foguete treme cada vez mais enquanto os últimos dados rolam
        sh = 14 * seg(t, 39.0, boom)
        paste_c(page, sized("rocket_full.png", 760), R6[0] + sh * math.sin(t * 70), R6[1] + sh * math.cos(t * 53),
                rot=sh * 0.4 * math.sin(t * 40))
    roll(page, t, 38.9, 0.9, (100, 1500), [(420, 1150), (640, 1220)], [1, 1], [10, -15],
         dim=(0, 1) if t >= 39.8 else ())
    if 39.8 <= t:
        d = ImageDraw.Draw(page)
        for x, y in [(420, 1150), (640, 1220)]:
            d.line((x - 70, y - 70, x + 70, y + 70), fill=RED, width=22)
            d.line((x + 70, y - 70, x - 70, y + 70), fill=RED, width=22)
    if t >= boom:  # explosão: nuvens para todo lado e as fichas voando
        u = seg(t, boom, boom + 1.6)
        for i in range(14):
            a = i * 2 * math.pi / 14 + 0.3
            r = 120 + 520 * (1 - (1 - u) ** 2)
            paste_c(page, puff(220, 200 if i % 2 else 240), R6[0] + math.cos(a) * r, R6[1] + math.sin(a) * r * 0.7,
                    rot=i * 40, scale=0.7 + 0.8 * u, alpha=1 - u * 0.85)
        for k in range(4):
            uu = seg(t, boom, boom + 2.0)
            a = math.radians(-150 + k * 40)
            x = R6[0] + math.cos(a) * 900 * uu
            y = R6[1] + math.sin(a) * 600 * uu + 1300 * uu * uu
            p, _ = slot_patch(k)
            paste_c(page, p, x, y, rot=uu * 720 * (1 if k % 2 else -1), scale=1.4)


def element_img(kind, args):
    if kind == "caption":
        return caption(*args)
    if kind == "balloon":
        return balloon(*args)
    if kind == "burst":
        return burst(*args)
    if kind == "chip":
        return chip(*args)
    if kind == "logo":
        return logo_card(*args)
    raise ValueError(kind)


def draw_elements(page, els, t):
    for e in els:
        t0, kind, args, x, y, rot = e[:6]
        if t < t0 or (len(e) > 6 and t >= e[6]):
            continue
        u = seg(t, t0, t0 + 0.32)
        sc = max(0.05, out_back(u)) if u < 1 else 1.0
        im = element_img(kind, args)
        if kind == "burst" and u >= 1:  # onomatopeia "pulsa" de leve
            sc = 1 + 0.03 * math.sin((t - t0) * 9)
        if abs(sc - 1) > 0.002:
            im = im.resize((max(2, int(im.width * sc)), max(2, int(im.height * sc))), Image.BICUBIC)
        if rot:
            im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        page.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)


def camera(keys, t):
    for (ta, ra), (tb, rb) in zip(keys, keys[1:]):
        if ta <= t <= tb:
            u = ease(seg(t, ta, tb))
            cx, cy = lerp(ra[0], rb[0], u), lerp(ra[1], rb[1], u)
            w = lerp(ra[2], rb[2], u)
            if ra != rb and ra[2] < PW and rb[2] < PW:  # ao trocar de quadro, afasta um pouco no meio
                w = min(PW, w * (1 + 0.35 * math.sin(math.pi * u)))
            return cx, cy, w
    return keys[-1][1]


def view(page, cam):
    """Recorta o enquadramento da câmera. Pode passar da borda da página: o fundo amarelo continua."""
    cx, cy, w = cam
    h = w * H / W
    if w >= PW - 1:  # página inteira: centraliza
        cx, cy = PW / 2, PH / 2
    box = (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))
    if box[0] >= 0 and box[1] >= 0 and box[2] <= PW and box[3] <= PH:
        crop = page.crop(box)
    else:
        crop = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), YELLOW)
        crop.paste(page, (-box[0], -box[1]))
    return crop.resize((W, H), Image.BICUBIC)


SCENES = [(0.0, 5.5), (5.5, 12.0), (12.0, 19.0), (19.0, 28.0), (28.0, 38.0), (38.0, 45.0), (45.0, 53.0),
          (53.0, 58.5), (58.5, 66.0)]


# ---------------------------------------------------------------- câmera
def fit(rect, margin=1.10, cx=None, w=None):
    """Enquadra um quadro. Nos quadros largos, cx/w miram no ponto de interesse."""
    x0, y0, x1, y1 = rect
    ww = w or max(x1 - x0, (y1 - y0) * W / H) * margin
    return (cx or (x0 + x1) / 2, (y0 + y1) / 2, min(ww, PW))


FULL = (PW / 2, PH / 2, PW)
P1, P2 = panels_of(1), panels_of(2)
# quadros-chave (tempo na linha original, enquadramento)
def scene_of(t0):
    for i, (a, b) in enumerate(SCENES):
        if a <= t0 < b:
            return i
    return len(SCENES) - 1


def element_box(e):
    t0, kind, args, x, y, rot = e[:6]
    im = element_img(kind, args)
    w, h = im.width, im.height
    if kind == "balloon":  # o sprite do balão tem margem para o rabinho
        w, h = w * 0.8, h * 0.8
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


# objetos animados que também precisam aparecer em cada cena (página, cena) → retângulos
EXTRA = {
    3: [(R4[0] - 110, R4[1] - 180, R4[0] + 110, R4[1] + 180)],
    4: [(R5[0] - 120, R5[1] - 210, R5[0] + 120, R5[1] + 210), (HOP[0] - 110, HOP[1] - 110, HOP[0] + 110, HOP[1] + 110)],
    5: [(R6[0] - 260, R6[1] - 420, R6[0] + 260, R6[1] + 420), (320, 1050, 740, 1320)],
}
SAFE_TOP, SAFE_BOT = 240, 1590   # área livre do vídeo (acima: logo; abaixo: legendas)


def auto_cam(i, panel):
    """Enquadra o quadro + todos os balões/legendas da cena, centralizados na área livre do vídeo."""
    els = [e for e in (EL1 + EL2) if scene_of(e[0]) == i]
    boxes = [element_box(e) for e in els] + EXTRA.get(i, [])
    if panel[2] - panel[0] < 1300:   # quadro estreito: mostra o quadro inteiro
        boxes.append(panel)
    else:                            # quadro largo: mira na área dos balões, com a altura do quadro
        bx0, bx1 = min(b[0] for b in boxes), max(b[2] for b in boxes)
        boxes.append((bx0, panel[1], bx1, panel[3]))
    x0 = min(b[0] for b in boxes) - 30
    y0 = min(b[1] for b in boxes) - 30
    x1 = max(b[2] for b in boxes) + 30
    y1 = max(b[3] for b in boxes) + 30
    frac = (SAFE_BOT - SAFE_TOP) / H
    vh = max((y1 - y0) / frac, (x1 - x0) * H / W)
    vw = min(PW, vh * W / H)
    vh = vw * H / W
    cx = (x0 + x1) / 2
    if (y1 - y0) / frac >= (x1 - x0) * H / W:   # limitado pela altura: centraliza na área livre
        mid = (SAFE_TOP + SAFE_BOT) / 2 / H
        cy = (y0 + y1) / 2 + (0.5 - mid) * vh
    else:                                        # limitado pela largura: encosta logo acima das legendas
        cy = y1 - (SAFE_BOT / H - 0.5) * vh
    # evita mostrar além da página quando der, sem tirar o conteúdo da área livre
    lo = y1 - (SAFE_BOT / H - 0.5) * vh          # menor cy que mantém o conteúdo acima das legendas
    hi = y0 - (SAFE_TOP / H - 0.5) * vh          # maior cy que mantém o conteúdo abaixo do logo
    if cy - vh / 2 < 0:
        cy = min(hi, max(lo, vh / 2))
    if cy + vh / 2 > PH:
        cy = max(lo, min(hi, PH - vh / 2))
    return (cx, cy, vw)


A = [auto_cam(i, (P1 + P2)[i]) for i in range(9)]
CAM1 = [(0.0, FULL), (0.6, FULL), (1.4, A[0]), (5.5, A[0]), (6.2, A[1]), (12.0, A[1]),
        (12.7, A[2]), (19.0, A[2]), (19.7, A[3]), (26.0, A[3]),
        (26.6, FULL), (28.0, FULL), (28.7, A[4]), (37.0, A[4]), (37.6, FULL), (40.0, FULL)]
CAM2 = [(0.0, FULL), (38.6, FULL), (39.3, A[5]), (45.0, A[5]), (45.7, A[6]), (53.0, A[6]), (53.7, A[7]), (58.5, A[7]),
        (59.2, A[8]), (62.8, A[8]), (63.8, FULL), (99.0, FULL)]
TURN = (37.6, 38.6)  # virada de página



def page_at(n, t):
    pg = page_base(n).copy()
    (anim_page1 if n == 1 else anim_page2)(pg, t)
    draw_elements(pg, EL1 if n == 1 else EL2, t)
    return pg


# ---------------------------------------------------------------- narração (opcional)
ROTEIRO = [
    "Imagina mandar seus gatos pro espaço... e torcer pro foguete não explodir.",
    "Esse é o MLEM: Agência Espacial. Cada jogador comanda uma equipe de gatos astronautas.",
    "Toda rodada, cada um coloca um gato no foguete.",
    "Aí o capitão rola os dados, escolhe um número, e o foguete avança. Os dados usados ficam de fora.",
    "A cada parada, você decide: desce agora e garante os pontos... ou continua, porque quanto mais longe, mais vale.",
    "Mas a cada rolagem sobram menos dados. Se nenhum servir... BOOM! Quem ficou no foguete sai sem nada.",
    "Ganha quem souber a hora certa de pular. De 2 a 5 jogadores, em uns 40 minutos.",
    "E você: pula na primeira lua ou arrisca até explodir? Comenta aí!",
    "Quer testar com a sua galera antes de comprar? Aluga o MLEM na Sua Vez por 5 dias: "
    "reserva no link da bio e retira aqui em Mauá.",
]


def default_subs():
    """Legendas provisórias (antes da narração): cada fala dividida em pedaços dentro da sua cena."""
    out = []
    for (a, b), txt in zip(SCENES, ROTEIRO):
        words = txt.split()
        chunks, cur = [], []
        for w in words:
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
    """Tempo do vídeo final → tempo da linha original (estica as cenas para caber a voz)."""
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
    P = lambda t, g=0.45: c.append((t, "pop", g))
    for els in (EL1, EL2):
        for e in els:
            P(e[0], 0.4)
    c += [(1.0, "launch", 0.5), (1.8, "launch", 0.9), (1.8, "whoosh", 0.6)]
    for k in range(4):  # fichas encaixando
        c += [(13.2 + k * 0.7 + 0.35, "beephi", 0.35), (13.2 + k * 0.7 + 0.35, "clack", 0.5)]
    c += [(19.8, "rattle", 0.8)] + [(19.8 + k * 0.06 + 1.1, "clack", 0.55) for k in range(6)]
    c += [(22.6, "ding", 0.35), (24.0, "whoosh", 0.35), (24.6, "ding", 0.5)]
    c += [(FLY[0], "launch", 0.5), (FLY[0], "whoosh", 0.7), (FLY[1], "clack", 0.6), (30.4, "boing", 0.5)]
    c += [(37.7, "whoosh", 0.5)]
    c += [(38.9, "rattle", 0.6), (39.9, "clack", 0.6), (39.6, "alarm", 0.45), (40.4, "boom", 1.0)]
    c += [(58.9, "ding", 0.4), (64.8, "chime", 0.5)]
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
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=22, fill=(18, 16, 24, 215))
    for i, l in enumerate(lines):
        d.text((w / 2, 13 + lh * i + lh / 2), l, font=f, fill=WHITE, anchor="mm")
    return im


@lru_cache(None)
def watermark():
    lg = logo_card(190)
    lg = lg.copy()
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.92)))
    return lg


def render_frame(args):
    fi, subs = args
    t = fi / FPS
    to = to_orig(t)
    if to < TURN[0]:
        img = view(page_at(1, to), camera(CAM1, to))
    elif to < TURN[1]:  # virada de página: a página 1 sai, a 2 entra
        u = ease(seg(to, *TURN))
        a = view(page_at(1, to), FULL)
        b = view(page_at(2, to), FULL)
        img = Image.new("RGB", (W, H), INK)
        img.paste(b, (int(W * (1 - u)), 0))
        sh = Image.new("RGB", (40, H), (0, 0, 0))
        img.paste(a, (int(-W * u), 0))
        img.paste(sh, (int(W * (1 - u)) - 20, 0))
    else:
        img = view(page_at(2, to), camera(CAM2, to))
    if to < 58.5:
        wm = watermark()
        img.paste(wm, (W - wm.width - 30, 90), wm)
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
    ap.add_argument("--frame", type=float)
    ap.add_argument("--page", type=int)
    ap.add_argument("--only", choices=["preview", "limpo"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.page:
        pg = page_at(a.page, 999)
        pg.resize((PW // 2, PH // 2), Image.LANCZOS).save(os.path.join(OUT, f"pagina{a.page}.png"))
        return
    if a.frame is not None:
        Image.frombytes("RGB", (W, H), render_frame((int(a.frame * FPS), True))).save(os.path.join(OUT, "frame.png"))
        return
    wav = os.path.join(OUT, "trilha_gibi.wav")
    voz = [(os.path.join(ROOT, v["arquivo"]), v["inicio"]) for v in TIMELINE["voz"]] if TIMELINE else None
    som.build(wav, DUR, warp=warp, voz=voz, cues=CUES)
    with open(os.path.join(ROOT, "legendas_gibi.srt"), "w", encoding="utf-8") as f:
        for i, (a_, b_, s) in enumerate(SUBS, 1):
            ts = lambda x: f"{int(x // 3600):02}:{int(x // 60 % 60):02}:{int(x % 60):02},{int(round(x * 1000)) % 1000:03}"
            f.write(f"{i}\n{ts(a_)} --> {ts(b_)}\n{s}\n\n")
    if a.only != "limpo":
        render(os.path.join(OUT, "gibi_preview.mp4"), wav, subs=True)
    if a.only != "preview":
        render(os.path.join(OUT, "gibi_limpo.mp4"), wav, subs=False)


if __name__ == "__main__":
    main()
