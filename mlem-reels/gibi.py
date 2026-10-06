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
    ((60, 320, 1060, 1580), "i8.jpg", (0.5, 0.40), 1.0, None),         # 1 foguete decolando
    ((1100, 320, 2100, 1150), "i1.jpg", (0.5, 0.40), 1.0, None),       # 2 caixa e gatos
    ((1100, 1190, 2100, 2600), "i3.jpg", (0.10, 0.62), 1.45, None),    # 3 foguete com as fichas
    ((60, 1620, 1060, 2600), "i11.jpg", (0.66, 0.02), 1.7, None),      # 4 dados no tabuleiro
    ((60, 2640, 2100, 3780), "i10.jpg", (0.38, 0.55), 1.0, None),      # 5 luas e planetas
]
PAGE2 = [
    ((60, 320, 2100, 1500), "i9.jpg", (0.5, 0.45), 1.05, (255, 90, 30)),   # 6 falha cósmica
    ((60, 1540, 1360, 2600), "i12.jpg", (0.5, 0.5), 1.0, None),           # 7 tabuleiros e poderes
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
    (2.4, "burst", ("GATOS NO ESPAÇO?!", 88, (255, 255, 255), RED, 24, 1.0), 600, 1200, 4),
    (3.6, "balloon", ("O QUE PODERIA DAR ERRADO?", 560, 58, (-0.3, 1.0)), 560, 1470, 0),
    (6.0, "caption", ("CADA JOGADOR COMANDA UMA AGÊNCIA DE GATOS", 800, 52), 1600, 440, -1),
    (7.6, "balloon", ("MIAU!", 360, 84, (-0.25, 1.0), RED), 1860, 700, 3),
    (9.0, "chip", ("DE REINER KNIZIA", 52), 1600, 1080, -2),
    (12.6, "caption", ("TODA RODADA, CADA UM EMBARCA UM GATO", 800, 56), 1600, 1310, 1),
    (14.0, "balloon", ("EU VOU!", 400, 78, (-0.3, 1.0), BLUE), 1840, 1600, -3),
    (15.4, "balloon", ("EU TAMBÉM!", 460, 68, (-0.3, 1.0), PINK), 1850, 1960, 2),
    (19.6, "caption", ("O CAPITÃO ROLA 6 DADOS E ESCOLHE UM GRUPO", 780, 54), 560, 1740, -1),
    (21.2, "burst", ("TEC TEC TEC!", 100, (255, 255, 255), RED, 18, 1.0), 560, 2060, -6),
    (23.6, "burst", ("+4!", 160, YELLOW, RED, 16, 1.25), 820, 2330, 8),
    (25.0, "chip", ("DADO USADO SAI DA RODADA", 48, RED, WHITE), 560, 2530, 1),
    (28.6, "caption", ("PULA NA LUA... OU CONTINUA?", 860, 62), 760, 2760, 1),
    (30.6, "balloon", ("PULO! PONTOS GARANTIDOS!", 520, 60, (0.3, 1.0), BLUE), 560, 3200, -2),
    (33.4, "balloon", ("EU CONTINUO! QUANTO MAIS LONGE, MAIS PONTOS!", 520, 54, (-0.3, 1.0), RED), 1460, 3330, 2),
]
EL2 = [
    (39.0, "caption", ("ATÉ QUE... NENHUM DADO SERVIU!", 900, 62), 640, 430, -1),
    (40.4, "burst", ("BOOM!", 300, ORANGE, YELLOW, 24, 1.0), 1150, 930, -5),
    (41.6, "caption", ("FALHA CÓSMICA! QUEM FICOU NO FOGUETE NÃO PONTUA", 860, 54), 1480, 1360, 1),
    (42.6, "balloon", ("MIAAAU!", 420, 84, (0.3, 1.0), RED), 420, 1150, -4),
    (45.6, "caption", ("CADA GATO TEM UM PODER ESPECIAL", 900, 60), 710, 1660, -1),
    (47.6, "chip", ("PLANETAS PREMIAM QUEM TEM MAIS GATOS", 46), 710, 2370, 1),
    (50.2, "chip", ("2 A 5 JOGADORES  ·  30 A 60 MIN", 50, YELLOW, INK), 710, 2500, -1),
    (53.4, "burst", ("E VOCÊ?", 130, (255, 255, 255), RED, 20, 1.05), 1750, 1700, 4),
    (54.6, "balloon", ("PULA NA 1ª LUA?", 420, 52, (0.2, 1.0), BLUE), 1750, 2070, -2),
    (55.6, "balloon", ("ARRISCA ATÉ O FIM?", 440, 52, (-0.2, 1.0), RED), 1750, 2380, 2),
    (56.8, "chip", ("COMENTA!", 56, RED, WHITE), 1750, 2540, 0),
    (59.0, "logo", (720,), 560, 2960, -3),
    (60.0, "burst", ("ALUGUE NA SUA VEZ!", 110, (255, 255, 255), RED, 22, 1.0), 1520, 3020, 3),
    (61.2, "chip", ("LINK NA BIO", 70, INK, YELLOW), 1520, 3500, -2),
]


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
    for t0, kind, args, x, y, rot in els:
        if t < t0:
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


# ---------------------------------------------------------------- câmera
def fit(rect, margin=1.10, cx=None, w=None):
    """Enquadra um quadro. Nos quadros largos, cx/w miram no ponto de interesse."""
    x0, y0, x1, y1 = rect
    ww = w or max(x1 - x0, (y1 - y0) * W / H) * margin
    return (cx or (x0 + x1) / 2, (y0 + y1) / 2, min(ww, PW))


FULL = (PW / 2, PH / 2, PW)
P1, P2 = panels_of(1), panels_of(2)
# quadros-chave (tempo na linha original, enquadramento)
CAM1 = [(0.0, FULL), (0.6, FULL), (1.4, fit(P1[0])), (5.5, fit(P1[0])), (6.2, fit(P1[1])), (12.0, fit(P1[1])),
        (12.7, fit(P1[2])), (19.0, fit(P1[2])), (19.7, fit(P1[3])), (26.0, fit(P1[3])),
        (26.8, FULL), (27.6, FULL), (28.4, fit(P1[4], cx=1000, w=1500)), (37.0, fit(P1[4], cx=1000, w=1500)),
        (37.6, FULL), (40.0, FULL)]
CAM2 = [(0.0, FULL), (38.6, FULL), (39.3, fit(P2[0], cx=1100, w=1400)), (45.0, fit(P2[0], cx=1100, w=1400)),
        (45.7, fit(P2[1])), (53.0, fit(P2[1])), (53.7, fit(P2[2])), (58.5, fit(P2[2])),
        (59.2, fit(P2[3], cx=1080, w=1500)), (62.8, fit(P2[3], cx=1080, w=1500)), (63.8, FULL), (99.0, FULL)]
TURN = (37.6, 38.6)  # virada de página


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
    cx, cy, w = cam
    h = w * H / W
    cx = min(max(cx, w / 2), PW - w / 2)
    cy = min(max(cy, h / 2), PH - h / 2)
    box = (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))
    return page.crop(box).resize((W, H), Image.BICUBIC)


def page_at(n, t):
    pg = page_base(n).copy()
    draw_elements(pg, EL1 if n == 1 else EL2, t)
    return pg


# ---------------------------------------------------------------- narração (opcional)
SCENES = [(0.0, 5.5), (5.5, 12.0), (12.0, 19.0), (19.0, 28.0), (28.0, 38.0), (38.0, 45.0), (45.0, 53.0),
          (53.0, 58.5), (58.5, 66.0)]
from mlem import SUBS as _SUBS  # noqa: E402  (mesmo roteiro dos outros formatos)
SUBS = [s for s in _SUBS if not s[2].startswith("3...")]

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
    som.build(wav, DUR, warp=warp, voz=voz)
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
